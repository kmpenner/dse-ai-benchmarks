"""Dataset readiness summaries for grant/HITL reporting.

One corpus (data/benchmarks.json), one status model: every task — whichever
workflow phase it belongs to, translation included — is either runnable
(has real ground truth) or backlog (verification_status NEEDS_GT, usually a
placeholder reference awaiting an RA).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .phase_bench import load_benchmarks


def analyse_readiness(benchmarks_path: Path) -> dict:
    bench_doc = load_benchmarks(benchmarks_path)
    benchmarks = bench_doc["benchmarks"]

    by_phase = defaultdict(lambda: {"runnable": 0, "needs_work": 0, "statuses": Counter()})
    for b in benchmarks:
        phase = b.get("task_type", "?")
        status = b.get("verification_status") or (
            "RUNNABLE" if b.get("ground_truth") else "NEEDS_GT"
        )
        by_phase[phase]["statuses"][status] += 1
        if b.get("ground_truth"):
            by_phase[phase]["runnable"] += 1
        else:
            by_phase[phase]["needs_work"] += 1

    phase_rows = []
    for phase, data in sorted(by_phase.items()):
        phase_rows.append({
            "phase": phase,
            "runnable": data["runnable"],
            "needs_work": data["needs_work"],
            "statuses": dict(sorted(data["statuses"].items())),
        })

    return {
        "benchmarks": len(benchmarks),
        "by_phase": phase_rows,
        "needs_ground_truth_ids": [
            b["id"] for b in benchmarks if not b.get("ground_truth")
        ],
    }


def to_markdown(result: dict) -> str:
    lines = ["# editio-bench Readiness\n"]
    lines.append(f"- Benchmark tasks: {result['benchmarks']}")
    lines.append("\n| Phase | Runnable | Needs work | Verification statuses |")
    lines.append("|---|---:|---:|---|")
    for row in result["by_phase"]:
        statuses = ", ".join(f"{k}: {v}" for k, v in row["statuses"].items())
        lines.append(
            f"| {row['phase']} | {row['runnable']} | "
            f"{row['needs_work']} | {statuses} |"
        )
    if result["needs_ground_truth_ids"]:
        lines.append(
            "\nGround-truth work remaining: "
            + ", ".join(f"`{bid}`" for bid in result["needs_ground_truth_ids"])
        )
    return "\n".join(lines) + "\n"
