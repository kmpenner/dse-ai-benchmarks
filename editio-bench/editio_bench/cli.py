"""CLI: phase | run | pairwise | report | review | agreement | tokentax | readiness

One corpus (data/benchmarks.json), one CLI. `phase` grades any target model
0-100 against ground truth across all five workflow phases (transcription,
collation, translation, annotation, encoding); `run`/`pairwise`/`report`/
`review` add chrF/BLEU, pairwise ELO, and human-review specifically for the
translation-type tasks within that same file.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .runner import run, load_config
from .pairwise import run_pairwise
from .report import make_report
from .human_review import make_review_html, agreement
from .cache import Cache
from .phase_bench import run_phase_bench, print_phase_summary, load_benchmarks, TIEBREAK_THRESHOLD
from .readiness import analyse_readiness, to_markdown as readiness_markdown


def main() -> None:
    p = argparse.ArgumentParser(prog="editio-bench")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser(
        "run",
        help="Translate + rubric-score all (model × protocol) candidates "
             "and external baselines",
    )
    pr.add_argument("--config", type=Path, default=Path("config.yaml"))
    pr.add_argument("--benchmarks", type=Path, default=Path("data/benchmarks.json"))
    pr.add_argument("--out", type=Path, required=True)

    pw = sub.add_parser(
        "pairwise",
        help="Anonymized A/B tournament over the candidates from a `run` output",
    )
    pw.add_argument("--results", type=Path, required=True)
    pw.add_argument("--config", type=Path, default=Path("config.yaml"))
    pw.add_argument("--benchmarks", type=Path, default=Path("data/benchmarks.json"))
    pw.add_argument("--out", type=Path, required=True)
    pw.add_argument("--judge", type=str, default=None)
    pw.add_argument("--seed", type=int, default=42)
    pw.add_argument("--max-pairs-per-passage", type=int, default=None)

    pp = sub.add_parser("report", help="Aggregate into a Markdown report")
    pp.add_argument("inputs", type=Path, nargs="+")
    pp.add_argument("--comparisons", type=Path, default=None)
    pp.add_argument("--out", type=Path, default=Path("report.md"))

    rv = sub.add_parser("review", help="Blind A/B HTML for human raters")
    rv.add_argument("--comparisons", type=Path, required=True)
    rv.add_argument("--results", type=Path, required=True)
    rv.add_argument("--benchmarks", type=Path, default=Path("data/benchmarks.json"))
    rv.add_argument("--out", type=Path, default=Path("review.html"))
    rv.add_argument("--n", type=int, default=40)
    rv.add_argument("--seed", type=int, default=42)

    ag = sub.add_parser(
        "agreement",
        help="Judge–human + inter-rater agreement from one or more votes files",
    )
    ag.add_argument("votes", type=Path, nargs="+")

    tt = sub.add_parser(
        "tokentax",
        help="Tokenization-tax analysis of the corpus (offline, no API cost)",
    )
    tt.add_argument("--benchmarks", type=Path, default=Path("data/benchmarks.json"))
    tt.add_argument("--out", type=Path, default=Path("tokentax.md"))
    tt.add_argument(
        "--hf", type=str, nargs="*", default=[],
        help="Optional HuggingFace tokenizer names (requires transformers)",
    )

    rd = sub.add_parser(
        "readiness",
        help="Summarize which benchmark data are runnable vs. awaiting RA/GT work",
    )
    rd.add_argument("--benchmarks", type=Path, default=Path("data/benchmarks.json"))
    rd.add_argument("--out", type=Path, default=None)
    rd.add_argument("--json", action="store_true")

    ph = sub.add_parser(
        "phase",
        help="Full workflow suite (transcription/collation/translation/"
             "annotation/encoding). Grades any target(s) 0-100 vs ground truth. "
             "Use --model to benchmark a single new OpenRouter slug.",
    )
    ph.add_argument("--config", type=Path, default=Path("config.yaml"))
    ph.add_argument("--benchmarks", type=Path, default=Path("data/benchmarks.json"))
    ph.add_argument("--model", type=str, default=None,
                    help="Single OpenRouter slug to benchmark as the sole target "
                         "(overrides candidate_models from config).")
    ph.add_argument("--phase", action="append", dest="phases", metavar="TASK_TYPE",
                    help="Restrict to one or more phases (repeatable).")
    ph.add_argument("--reasoning", type=str, default="none",
                    choices=["none", "low", "high"],
                    help="Reasoning effort for the target model(s) being "
                         "benchmarked -- NOT the scorer panel, which always "
                         "runs at low. Default: none.")
    ph.add_argument("--out", type=Path, default=None)
    ph.add_argument("--dry-run", action="store_true",
                    help="Offline: validate + list what would run, no API calls.")

    args = p.parse_args()

    if args.cmd == "run":
        asyncio.run(run(args.config, args.benchmarks, args.out))
    elif args.cmd == "pairwise":
        cfg = load_config(args.config)
        judge = args.judge or cfg.get("judge_model", "anthropic/claude-opus-4.7")
        if judge in cfg.get("candidate_models", []) and not cfg.get("allow_self_judge", False):
            print(
                "warning: judge model is also in candidate_models; avoid this for "
                "production HITL evidence or set allow_self_judge: true"
            )
        cache = Cache(Path(cfg.get("cache_path", ".editio_cache.sqlite")))
        asyncio.run(run_pairwise(
            results_path=args.results,
            passages_path=args.benchmarks,
            out_path=args.out,
            judge_model=judge,
            concurrency=cfg.get("concurrency", 4),
            seed=args.seed,
            max_pairs_per_passage=args.max_pairs_per_passage,
            cache=cache,
        ))
    elif args.cmd == "report":
        make_report(args.inputs, args.out, comparisons_path=args.comparisons)
        print(f"wrote {args.out}")
    elif args.cmd == "review":
        make_review_html(
            args.comparisons, args.results, args.benchmarks, args.out,
            n_samples=args.n, seed=args.seed,
        )
        print(f"wrote {args.out} — open in a browser; each rater downloads "
              f"their own votes_<name>.json")
    elif args.cmd == "agreement":
        print(json.dumps(agreement(args.votes), indent=2))
    elif args.cmd == "phase":
        import asyncio
        from datetime import datetime, timezone
        cfg = load_config(args.config)
        doc = load_benchmarks(args.benchmarks)
        targets = [args.model] if args.model else list(cfg["candidate_models"])
        scorers = cfg.get("phase_scorers") or [cfg.get("judge_model", "anthropic/claude-opus-4.7")]
        tiebreaker_scorer = cfg.get("phase_tiebreaker_scorer") or cfg.get("judge_model")
        all_phases = sorted({b["task_type"] for b in doc["benchmarks"]})
        if args.phases:
            unknown = set(args.phases) - set(all_phases)
            if unknown:
                p.error(f"unknown phase(s) {sorted(unknown)}; available: {all_phases}")
        runnable = [b for b in doc["benchmarks"] if b.get("ground_truth")
                    and (not args.phases or b["task_type"] in set(args.phases))]
        print(f"targets: {targets}")
        print(f"scorers: {scorers}")
        print(f"tiebreaker (used when the two scorers disagree by >{TIEBREAK_THRESHOLD} pts): {tiebreaker_scorer}")
        print(f"reasoning effort (target model(s)): {args.reasoning}")
        print(f"phases: {args.phases or all_phases}")
        print(f"runnable tasks (with ground truth): {len(runnable)}")
        if args.dry_run:
            for b in runnable:
                print(f"  [{b['task_type']:14}] {b['id']}")
            print("dry-run: no API calls made.")
            return
        stamp = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
        tag = (args.model.replace('/', '__') if args.model else "panel")
        out = args.out or Path("results") / f"phase_{tag}_{args.reasoning}_{stamp}.csv"
        rows = asyncio.run(run_phase_bench(
            benchmarks_path=args.benchmarks, out_csv=out,
            targets=targets, scorers=scorers, phases=args.phases,
            concurrency=cfg.get("concurrency", 4),
            temperature=cfg.get("temperature", 0.0),
            max_tokens=cfg.get("max_tokens", 2048),
            cache_path=Path(cfg.get("cache_path", ".editio_cache.sqlite")),
            tiebreaker_scorer=tiebreaker_scorer,
            reasoning_effort=args.reasoning,
        ))
        if rows:
            print_phase_summary(rows, scorers)
    elif args.cmd == "tokentax":
        from .tokentax import analyse, to_markdown
        result = analyse(args.benchmarks, hf_tokenizers=args.hf)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(to_markdown(result), encoding="utf-8")
        print(f"wrote {args.out}")
        for s in result["summary"]:
            print(s)
    elif args.cmd == "readiness":
        result = analyse_readiness(args.benchmarks)
        text = json.dumps(result, indent=2, ensure_ascii=False) if args.json else readiness_markdown(result)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text, encoding="utf-8")
            print(f"wrote {args.out}")
        else:
            print(text)


if __name__ == "__main__":
    main()
