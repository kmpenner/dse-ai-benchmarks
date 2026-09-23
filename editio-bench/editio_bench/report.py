"""Markdown report: ELO over candidates, rubric leaderboard, protocol effects
(model × protocol matrix + protocol marginals), per-genre, hallucinations,
per-passage detail."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Optional

from .elo import elo_with_ci


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                rows.append(json.loads(ln))
    return rows


def _avg(xs) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    return round(mean(xs), 2) if xs else None


def _fmt(x) -> str:
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.2f}"
    return str(x)


def make_report(
    result_paths: list[Path],
    out_path: Path,
    comparisons_path: Optional[Path] = None,
) -> None:
    rows = []
    for p in result_paths:
        rows.extend(_load_jsonl(p))
    if not rows:
        out_path.write_text("# editio-bench: empty results\n", encoding="utf-8")
        return

    for r in rows:
        r.setdefault("candidate", r.get("model"))
        r.setdefault("protocol", "baseline")

    by_cand: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_cand[r["candidate"]].append(r)

    target = rows[0].get("target_language", "?")
    lines: list[str] = []
    lines.append(f"# editio-bench report — target: **{target}**\n")
    lines.append(
        f"_{len(rows)} (candidate, passage) evaluations across "
        f"{len(by_cand)} candidates (candidate = model × prompt protocol, "
        f"plus any external baselines)._\n"
    )

    # ---- ELO ------------------------------------------------------------
    if comparisons_path is not None and comparisons_path.exists():
        comps = [
            c for c in _load_jsonl(comparisons_path)
            if c.get("winner") in ("A", "B", "tie")
        ]
        cands = sorted({c["model_a"] for c in comps} | {c["model_b"] for c in comps})
        if len(cands) >= 2 and comps:
            elo = elo_with_ci(comps, cands)
            lines.append("## Pairwise ELO (Bradley–Terry, 95% bootstrap CI)\n")
            lines.append("| Candidate | ELO | 95% CI | Comparisons |")
            lines.append("|---|---:|---:|---:|")
            for m in sorted(cands, key=lambda m: -elo[m]["elo"]):
                e = elo[m]
                lines.append(
                    f"| `{m}` | {e['elo']:.0f} | "
                    f"[{e['ci_low']:.0f}, {e['ci_high']:.0f}] | "
                    f"{e['n_comparisons']} |"
                )
            lines.append(
                "\n_Overlapping CIs mean the ranking between those candidates "
                "is not resolved by this corpus._\n"
            )
            bias = _position_bias(_load_jsonl(comparisons_path))
            if bias is not None:
                lines.append(
                    f"_Position-bias check: judge picked the first-shown "
                    f"candidate in {bias:.0%} of decisive comparisons "
                    f"(unbiased ≈ 50%)._\n"
                )

    # ---- Rubric leaderboard -----------------------------------------------
    placeholder_refs = sum(
        1 for r in rows
        if not r.get("metrics", {}).get("reference_metrics_available", True)
    )
    if placeholder_refs:
        lines.append(
            "## Reference metric coverage\n\n"
            f"{placeholder_refs} evaluation rows had placeholder or missing "
            "reference translations, so chrF++/BLEU/length-ratio metrics were "
            "suppressed for those rows. Judge scores and sigla-preservation "
            "checks remain available.\n"
        )

    lines.append("## Rubric leaderboard\n")
    lines.append(
        "| Candidate | Judge avg | chrF++ | BLEU | Length ratio | "
        "Recon. preserved | Cost (USD) | Latency (s) | Errors |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    board = []
    for cand, mr in by_cand.items():
        board.append({
            "cand": cand,
            "judge_avg": _avg([r.get("judge_avg") for r in mr]),
            "chrf": _avg([r.get("metrics", {}).get("chrf") for r in mr]),
            "bleu": _avg([r.get("metrics", {}).get("bleu") for r in mr]),
            "lr": _avg([r.get("metrics", {}).get("length_ratio") for r in mr]),
            "rp": _avg([
                r.get("metrics", {}).get("reconstructions_preserved") for r in mr
            ]),
            "cost": round(sum(r.get("cost_usd", 0.0) or 0.0 for r in mr), 4),
            "lat": _avg([
                r.get("latency_s") for r in mr
                if not r.get("cached") and not r.get("external")
            ]),
            "errs": sum(1 for r in mr if r.get("error")),
        })
    board.sort(
        key=lambda r: (
            r["judge_avg"] if r["judge_avg"] is not None else -1,
            r["chrf"] if r["chrf"] is not None else -1,
        ),
        reverse=True,
    )
    for r in board:
        lines.append(
            f"| `{r['cand']}` | {_fmt(r['judge_avg'])} | {_fmt(r['chrf'])} | "
            f"{_fmt(r['bleu'])} | {_fmt(r['lr'])} | {_fmt(r['rp'])} | "
            f"{r['cost']:.4f} | {_fmt(r['lat'])} | {r['errs']} |"
        )

    # ---- Protocol effects ---------------------------------------------------
    models = sorted({r["model"] for r in rows if r.get("protocol") != "external"})
    protocols = sorted({
        r["protocol"] for r in rows if r.get("protocol") != "external"
    })
    if len(protocols) > 1:
        lines.append("\n## Protocol effects (judge average)\n")
        lines.append("| Model | " + " | ".join(protocols) + " | best protocol |")
        lines.append("|---|" + "|".join("---:" for _ in protocols) + "|---|")
        for m in models:
            cells = [f"`{m}`"]
            vals = {}
            for pr in protocols:
                v = _avg([
                    r.get("judge_avg") for r in rows
                    if r["model"] == m and r["protocol"] == pr
                ])
                vals[pr] = v
                cells.append(_fmt(v))
            best = max(
                (pr for pr in protocols if vals[pr] is not None),
                key=lambda pr: vals[pr], default=None,
            )
            cells.append(best or "—")
            lines.append("| " + " | ".join(cells) + " |")

        lines.append("\n**Protocol marginals** (averaged over all models):\n")
        lines.append("| Protocol | Judge avg | chrF++ | Recon. preserved |")
        lines.append("|---|---:|---:|---:|")
        for pr in protocols:
            sub = [r for r in rows if r.get("protocol") == pr]
            lines.append(
                f"| `{pr}` | {_fmt(_avg([r.get('judge_avg') for r in sub]))} | "
                f"{_fmt(_avg([r.get('metrics', {}).get('chrf') for r in sub]))} | "
                f"{_fmt(_avg([r.get('metrics', {}).get('reconstructions_preserved') for r in sub]))} |"
            )

    # ---- Per-genre ------------------------------------------------------------
    lines.append("\n## By genre (judge average)\n")
    genres = sorted({r.get("genre") or "?" for r in rows})
    lines.append("| Candidate | " + " | ".join(genres) + " |")
    lines.append("|---|" + "|".join("---:" for _ in genres) + "|")
    for cand in by_cand:
        cells = [f"`{cand}`"]
        for g in genres:
            vals = [
                r.get("judge_avg") for r in by_cand[cand]
                if (r.get("genre") or "?") == g
            ]
            cells.append(_fmt(_avg(vals)))
        lines.append("| " + " | ".join(cells) + " |")

    # ---- Hallucinations ----------------------------------------------------------
    lines.append("\n## Hallucinations flagged by judge\n")
    halluc = defaultdict(list)
    for r in rows:
        h = (r.get("judge") or {}).get("hallucinations") or {}
        if h.get("present"):
            halluc[r["candidate"]].append((
                r.get("siglum") or r["passage_id"],
                h.get("severity", "?"),
                "; ".join(h.get("examples", [])[:2]),
            ))
    if halluc:
        for m, items in sorted(halluc.items(), key=lambda kv: -len(kv[1])):
            lines.append(f"- `{m}` ({len(items)}):")
            for sig, sev, ex in items:
                lines.append(f"  - {sig} [{sev}] {ex}")
    else:
        lines.append("_None flagged._")

    # ---- Per-passage detail --------------------------------------------------------
    lines.append("\n## Per-passage detail\n")
    by_passage = defaultdict(list)
    for r in rows:
        by_passage[r["passage_id"]].append(r)
    for pid, prows in by_passage.items():
        first = prows[0]
        lines.append(
            f"\n### {first.get('siglum') or pid} _(genre: {first.get('genre')})_\n"
        )
        for r in sorted(prows, key=lambda r: -(r.get("judge_avg") or 0)):
            j = r.get("judge") or {}
            lines.append(
                f"**`{r['candidate']}`** — judge avg: {_fmt(r.get('judge_avg'))}, "
                f"chrF: {_fmt(r.get('metrics', {}).get('chrf'))}"
            )
            if r.get("error"):
                lines.append(f"\n> error: {r['error']}\n")
                continue
            lines.append("")
            lines.append("```")
            lines.append((r.get("translation") or "")[:1200])
            lines.append("```")
            if "overall" in j:
                lines.append(f"_Judge:_ {j['overall'].get('summary', '')}")
            lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def _position_bias(all_comps: list[dict]) -> Optional[float]:
    firsts = 0
    decisive = 0
    for c in all_comps:
        w = c.get("winner")
        pres = c.get("presentation")
        if w not in ("A", "B") or pres not in ("ab", "ba"):
            continue
        decisive += 1
        first_model = c["model_a"] if pres == "ab" else c["model_b"]
        won_model = c["model_a"] if w == "A" else c["model_b"]
        if first_model == won_model:
            firsts += 1
    return firsts / decisive if decisive else None
