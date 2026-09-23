"""Rubric run over (model × protocol) candidates plus external baselines."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import httpx
import yaml
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

from .translate import (
    OpenRouterClient, translate_one, load_external_baselines,
)
from .prompts import PromptLibrary
from .metrics import compute_all, bertscore_f1, has_usable_reference
from .judge import judge_one, summarise_judge
from .cache import Cache
from .corpus import load_translation_tasks

console = Console()


def load_passages(path: Path) -> list[dict]:
    """Load runnable translation tasks from the merged benchmarks.json."""
    return load_translation_tasks(path, runnable_only=True)


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg.setdefault("target_language", "English")
    cfg.setdefault("temperature", 0.0)
    cfg.setdefault("max_tokens", 2048)
    cfg.setdefault("concurrency", 4)
    cfg.setdefault("cache_path", ".editio_cache.sqlite")
    cfg.setdefault("prompt_library", "prompts/protocols.yaml")
    cfg.setdefault("prompt_protocols", ["baseline"])
    cfg.setdefault("external_baselines", [])
    cfg.setdefault("metrics", {})
    cfg["metrics"].setdefault("chrf", True)
    cfg["metrics"].setdefault("bleu", True)
    cfg["metrics"].setdefault("bertscore", False)
    cfg["metrics"].setdefault("judge", True)
    cfg.setdefault("bertscore_lang", "en")
    return cfg


async def run(config_path: Path, passages_path: Path, out_path: Path) -> None:
    cfg = load_config(config_path)
    passages = load_passages(passages_path)
    if not passages:
        console.print("[red]No passages loaded.[/red]")
        sys.exit(1)

    lib = PromptLibrary.load(Path(cfg["prompt_library"]))
    protocol_names = cfg["prompt_protocols"]
    missing = [p for p in protocol_names if p not in lib.protocols]
    if missing:
        console.print(f"[red]Protocols not in library: {missing}[/red]")
        sys.exit(1)
    protocols = [lib.protocols[p] for p in protocol_names]

    models: list[str] = cfg["candidate_models"]
    judge_model: str = cfg.get("judge_model", "anthropic/claude-opus-4.7")
    if judge_model in models and not cfg.get("allow_self_judge", False):
        console.print(
            "[yellow]Judge model is also in candidate_models; this is useful for "
            "smoke tests but should be avoided for production HITL evidence. "
            "Set allow_self_judge: true to silence this warning.[/yellow]"
        )
    target = cfg["target_language"]
    sem = asyncio.Semaphore(cfg["concurrency"])
    cache = Cache(Path(cfg["cache_path"]))

    externals = load_external_baselines(cfg["external_baselines"])
    pids = {p["id"] for p in passages}
    externals = [e for e in externals if e.passage_id in pids]

    client = OpenRouterClient()
    timeout = httpx.Timeout(180.0, connect=30.0)
    limits = httpx.Limits(max_connections=cfg["concurrency"] * 2)

    n_api = len(models) * len(protocols) * len(passages)
    total = n_api + len(externals)
    console.print(
        f"[bold]Models:[/bold] {len(models)}  "
        f"[bold]Protocols:[/bold] {protocol_names}  "
        f"[bold]Passages:[/bold] {len(passages)}  "
        f"[bold]External baselines:[/bold] {len(cfg['external_baselines'])}  "
        f"[bold]Target:[/bold] {target}"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_f = out_path.open("w", encoding="utf-8")
    run_cost = {"translation": 0.0, "judge": 0.0}

    async def bounded(coro):
        async with sem:
            return await coro

    passage_by_id = {p["id"]: p for p in passages}

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as http:
        with Progress(
            TextColumn("[bold]{task.description}"), BarColumn(),
            TextColumn("{task.completed}/{task.total}"), TimeElapsedColumn(),
            console=console,
        ) as progress:
            t1 = progress.add_task("translating", total=n_api)
            tasks = [
                bounded(
                    translate_one(
                        client, http, model, proto, p,
                        target_language=target, lib=lib,
                        temperature=cfg["temperature"],
                        max_tokens=cfg["max_tokens"], cache=cache,
                    )
                )
                for model in models
                for proto in protocols
                for p in passages
            ]
            translations = list(externals)
            for fut in asyncio.as_completed(tasks):
                tr = await fut
                if not tr.cached:
                    run_cost["translation"] += tr.cost_usd
                translations.append(tr)
                progress.update(t1, advance=1)

            t2 = progress.add_task("scoring", total=len(translations))
            score_tasks = [
                bounded(
                    _score_one(
                        client, http, cfg, judge_model, target,
                        passage_by_id[tr.passage_id], tr, cache,
                    )
                )
                for tr in translations
            ]
            for fut in asyncio.as_completed(score_tasks):
                row, judge_cost = await fut
                run_cost["judge"] += judge_cost
                out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                out_f.flush()
                progress.update(t2, advance=1)

    out_f.close()
    n_cached = sum(1 for t in translations if t.cached)
    console.print(
        f"[green]Wrote results to {out_path}[/green]  "
        f"cached: {n_cached}  "
        f"API cost this run: "
        f"${run_cost['translation'] + run_cost['judge']:.4f} "
        f"(translate ${run_cost['translation']:.4f} / judge ${run_cost['judge']:.4f})"
    )


async def _score_one(
    client, http, cfg, judge_model, target_language, passage, tr, cache
) -> tuple[dict, float]:
    row = {
        "candidate": tr.candidate,
        "model": tr.model,
        "protocol": tr.protocol,
        "passage_id": passage["id"],
        "siglum": passage.get("siglum"),
        "genre": passage.get("genre"),
        "source_language": passage.get("language"),
        "target_language": target_language,
        "translation": tr.translation,
        "cached": tr.cached,
        "external": tr.external,
        "error": tr.error,
        "latency_s": tr.latency_s,
        "cost_usd": tr.cost_usd,
        "tokens": {
            "prompt": tr.prompt_tokens,
            "completion": tr.completion_tokens,
            "total": tr.total_tokens,
        },
    }
    if tr.error or not tr.translation.strip():
        return row, 0.0

    metrics = compute_all(
        source=passage["source"],
        hypothesis=tr.translation,
        reference=passage.get("reference", ""),
        reference_source=passage.get("reference_source"),
        enable_bleu=cfg["metrics"]["bleu"],
        enable_chrf=cfg["metrics"]["chrf"],
    )
    if cfg["metrics"]["bertscore"] and has_usable_reference(
        passage.get("reference", ""), passage.get("reference_source")
    ):
        bs = bertscore_f1(
            [tr.translation], [passage.get("reference", "")],
            target_lang_code=cfg.get("bertscore_lang", "en"),
        )
        if bs is not None:
            metrics["bertscore_f1"] = bs[0]
    row["metrics"] = metrics

    judge_cost = 0.0
    if cfg["metrics"]["judge"]:
        j, judge_cost = await judge_one(
            client, http, judge_model, passage, tr.translation,
            target_language, cache=cache,
        )
        row["judge"] = j
        row["judge_avg"] = summarise_judge(j)
    return row, judge_cost
