"""Pairwise tournament over candidates (= model × protocol, and external
baselines). Both presentation orders per pair; emits comparisons JSONL."""
from __future__ import annotations

import asyncio
import itertools
import json
import random
from pathlib import Path

import httpx
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

from .translate import OpenRouterClient
from .judge import judge_pair
from .corpus import load_translation_tasks

console = Console()


def _load_translations(results_path: Path):
    idx = {}
    meta = {}
    with results_path.open("r", encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            r = json.loads(ln)
            if r.get("error") or not (r.get("translation") or "").strip():
                continue
            idx[(r["candidate"], r["passage_id"])] = r["translation"]
            meta.setdefault(r["passage_id"], {
                "target_language": r.get("target_language"),
            })
    return idx, meta


async def run_pairwise(
    results_path: Path,
    passages_path: Path,
    out_path: Path,
    judge_model: str,
    concurrency: int = 4,
    seed: int = 42,
    max_pairs_per_passage: int | None = None,
    cache=None,
) -> None:
    tr_idx, meta = _load_translations(results_path)

    full = {p["id"]: p for p in load_translation_tasks(passages_path, runnable_only=False)}

    candidates = sorted({c for (c, _) in tr_idx})
    passage_ids = sorted({pid for (_, pid) in tr_idx})
    if len(candidates) < 2:
        console.print("[red]Need at least 2 candidates with translations.[/red]")
        return

    rng = random.Random(seed)
    jobs = []
    for pid in passage_ids:
        if pid not in full:
            continue
        avail = [c for c in candidates if (c, pid) in tr_idx]
        pairs = list(itertools.combinations(avail, 2))
        rng.shuffle(pairs)
        if max_pairs_per_passage is not None:
            pairs = pairs[:max_pairs_per_passage]
        for a, b in pairs:
            jobs.append((pid, a, b, "ab"))
            jobs.append((pid, a, b, "ba"))

    console.print(
        f"[bold]Pairwise:[/bold] {len(candidates)} candidates, "
        f"{len(passage_ids)} passages, {len(jobs)} judge calls (both orders). "
        f"Judge: {judge_model}"
    )

    client = OpenRouterClient()
    sem = asyncio.Semaphore(concurrency)
    timeout = httpx.Timeout(180.0, connect=30.0)
    limits = httpx.Limits(max_connections=concurrency * 2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_f = out_path.open("w", encoding="utf-8")
    total_cost = 0.0

    async def one(pid, a, b, order):
        passage = full[pid]
        tl = meta[pid].get("target_language") or "English"
        first, second = (a, b) if order == "ab" else (b, a)
        async with sem:
            j, cost = await judge_pair(
                client, http, judge_model, passage,
                tr_idx[(first, pid)], tr_idx[(second, pid)],
                target_language=tl, cache=cache,
            )
        winner = j.get("winner")
        if winner == "A":
            mapped = "A" if order == "ab" else "B"
        elif winner == "B":
            mapped = "B" if order == "ab" else "A"
        elif winner == "tie":
            mapped = "tie"
        else:
            mapped = None
        return {
            "passage_id": pid,
            "model_a": a,
            "model_b": b,
            "presentation": order,
            "winner": mapped,
            "confidence": j.get("confidence"),
            "rationale": j.get("rationale"),
            "error": j.get("error"),
        }, cost

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as http:
        with Progress(
            TextColumn("[bold]{task.description}"), BarColumn(),
            TextColumn("{task.completed}/{task.total}"), TimeElapsedColumn(),
            console=console,
        ) as progress:
            t = progress.add_task("pairwise judging", total=len(jobs))
            tasks = [one(*job) for job in jobs]
            for fut in asyncio.as_completed(tasks):
                row, cost = await fut
                total_cost += cost
                out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                out_f.flush()
                progress.update(t, advance=1)

    out_f.close()
    console.print(
        f"[green]Wrote comparisons to {out_path}[/green] "
        f"(judge cost: ${total_cost:.4f})"
    )
