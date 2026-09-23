"""Per-task Pareto charts: quality vs cost and quality vs latency, one panel
per task, for the clean re-run (editio-bench/resac2026_clean_sweep.json +
editio-bench/results/phase_*_sweep.csv).

The master-level Pareto charts (clean_chart_pareto_cost.png /
_latency.png) look at *total* cost/latency across all 13 tasks. This script
answers a different question: for a single task (e.g. "V: Aramaic"), which
model+effort configs are Pareto-optimal on that task alone? A model can be
on the frontier overall while being dominated on a specific task, or vice
versa.

Cost per task = that task's answer_cost_usd + its judge scoring costs
(score_cost_usd::*, including the tiebreak scorer when triggered).
Latency per task = that task's answer_latency_s (judge latency isn't
captured upstream).

Config eligibility (2026-09-10 audit): configs excluded by
scripts/build_clean_suite_report.py's gates (<90% task coverage, or a
mostly-cache-replayed run) are also excluded here — read from the
`included` column of resac2026/clean_suite_master.csv, so run
build_clean_suite_report.py first if that file is missing or stale.

Usage: python3 scripts/build_per_task_pareto.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
EB = ROOT / "editio-bench"
SWEEP_JSON = EB / "resac2026_clean_sweep.json"
OUT_DIR = ROOT / "resac2026"

# Column-major layout: left column = Aramaic, middle = Greek, right = Latin.
LANGUAGE_COLUMNS = [
    ["trans-aramaic-4q530-f2ii", "coll-aramaic-4q530-giants-parallels",
     "translat-aramaic-4q530-tree-vision", "annot-aramaic-4q530-morphology"],
    ["trans-greek-marchalianus-p11", "coll-greek-marchalianus-vitae",
     "translat-greek-marchalianus-siloam", "annot-greek-marchalianus-tei-msd",
     "encode-greek-marchalianus-teiheader"],
    ["trans-latin-vatlat629-f3v", "coll-latin-vatlat629-isidore",
     "translat-latin-vatlat629-seraphim", "annot-latin-vatlat629-abbreviations"],
]
TASK_ORDER = [tid for col in LANGUAGE_COLUMNS for tid in col]
TASK_LABEL = {
    "trans-greek-marchalianus-p11": "V: Greek", "trans-latin-vatlat629-f3v": "V: Latin",
    "trans-aramaic-4q530-f2ii": "V: Aramaic", "coll-greek-marchalianus-vitae": "C: Greek",
    "coll-latin-vatlat629-isidore": "C: Latin", "coll-aramaic-4q530-giants-parallels": "C: Aramaic",
    "translat-greek-marchalianus-siloam": "Tr: Greek", "translat-latin-vatlat629-seraphim": "Tr: Latin",
    "translat-aramaic-4q530-tree-vision": "Lac: Aramaic", "annot-greek-marchalianus-tei-msd": "A: Greek",
    "annot-latin-vatlat629-abbreviations": "A: Latin", "annot-aramaic-4q530-morphology": "A: Aramaic",
    "encode-greek-marchalianus-teiheader": "Enc: Greek",
}

PROVIDER_COLORS = {
    'Anthropic': '#7c3aed', 'Google': '#2563eb', 'OpenAI': '#059669', 'xAI': '#dc2626',
    'DeepSeek': '#0891b2', 'Meta': '#ea580c', 'Qwen': '#d97706', 'Mistral': '#4f46e5',
    'Z.ai / GLM': '#0ea5e9', 'MiniMax': '#9333ea', 'Other': '#64748b',
}


def provider_of(model: str) -> str:
    m = model.lower()
    for needle, prov in [('anthropic', 'Anthropic'), ('claude', 'Anthropic'), ('google', 'Google'),
                          ('gemini', 'Google'), ('gemma', 'Google'), ('openai', 'OpenAI'), ('gpt', 'OpenAI'),
                          ('x-ai', 'xAI'), ('grok', 'xAI'), ('deepseek', 'DeepSeek'), ('meta', 'Meta'),
                          ('llama', 'Meta'), ('qwen', 'Qwen'), ('mistral', 'Mistral'), ('z-ai', 'Z.ai / GLM'),
                          ('glm', 'Z.ai / GLM'), ('minimax', 'MiniMax')]:
        if needle in m:
            return prov
    return 'Other'


def pareto_mask(q: np.ndarray, r: np.ndarray) -> np.ndarray:
    n = len(q)
    dominated = np.zeros(n, dtype=bool)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if q[j] >= q[i] and r[j] <= r[i] and (q[j] > q[i] or r[j] < r[i]):
                dominated[i] = True
                break
    return ~dominated


def eligible_configs() -> set[tuple[str, str]]:
    """(model, effort) pairs that passed the master report's gates.

    Reads the `included` column of the master CSV (written by
    build_clean_suite_report.py). If that file doesn't exist yet, compute it
    inline from the sweep JSON rather than silently plotting everything.
    """
    master = ROOT / "resac2026" / "clean_suite_master.csv"
    if master.exists():
        df = pd.read_csv(master)
        return set(zip(df.loc[df["included"], "Model"], df.loc[df["included"], "Effort"]))
    import subprocess
    subprocess.run(["python3", str(ROOT / "scripts" / "build_clean_suite_report.py")],
                   check=True, capture_output=True)
    df = pd.read_csv(master)
    return set(zip(df.loc[df["included"], "Model"], df.loc[df["included"], "Effort"]))


def load_per_task_rows() -> pd.DataFrame:
    """One row per (model, effort, task): score_consensus, task cost, task latency."""
    keep = eligible_configs()
    sweep = json.loads(SWEEP_JSON.read_text())
    records = []
    for key, v in sweep.items():
        if "quality" not in v or v["quality"] is None:
            continue
        if (v["model"], v["effort"]) not in keep:
            continue  # failed the coverage / cache-replay gates
        try:
            tdf = pd.read_csv(ROOT / v["csv"]).set_index("benchmark")
        except FileNotFoundError:
            continue
        for tid in TASK_ORDER:
            if tid not in tdf.index:
                continue
            row = tdf.loc[tid]
            score = row.get("score_consensus")
            if pd.isna(score):
                continue
            cost = row.get("answer_cost_usd", 0.0) or 0.0
            for col in tdf.columns:
                if col.startswith("score_cost_usd::") and pd.notna(row.get(col)):
                    cost += row[col]
            latency = row.get("answer_latency_s", 0.0) or 0.0
            records.append({
                "Model": v["model"], "Effort": v["effort"], "Provider": provider_of(v["model"]),
                "task": tid, "task_label": TASK_LABEL[tid],
                "quality": score, "cost_usd": cost, "latency_s": latency,
            })
    return pd.DataFrame(records)


def plot_grid(df: pd.DataFrame, resource_col: str, xlabel: str, title: str, out_png: Path):
    """One subplot per task, arranged column-major by language:
    Aramaic (left), Greek (middle, incl. the Greek-only encoding task), Latin (right)."""
    n_rows = max(len(col) for col in LANGUAGE_COLUMNS)
    grid = [[None] * len(LANGUAGE_COLUMNS) for _ in range(n_rows)]
    for c, col in enumerate(LANGUAGE_COLUMNS):
        for r, tid in enumerate(col):
            grid[r][c] = tid
    fig, axes = plt.subplots(n_rows, len(LANGUAGE_COLUMNS), figsize=(16, 18), dpi=170)
    for r in range(n_rows):
        for c in range(len(LANGUAGE_COLUMNS)):
            ax = axes[r][c]
            tid = grid[r][c]
            if tid is None:
                ax.set_visible(False)
                continue
            label = TASK_LABEL[tid]
            sub = df[df["task"] == tid].copy()
            if sub.empty:
                ax.set_visible(False)
                continue
            sub = sub[sub[resource_col] > 0]  # log scale can't plot zero-cost rows
            if sub.empty:
                ax.set_visible(False)
                continue
            mask = pareto_mask(sub["quality"].to_numpy(), sub[resource_col].to_numpy())
            sub["on_front"] = mask
            for prov, psub in sub.groupby("Provider"):
                ax.scatter(psub[resource_col], psub["quality"], label=prov,
                           color=PROVIDER_COLORS.get(prov, '#64748b'), s=22, alpha=0.8, linewidths=0)
            front = sub[sub["on_front"]].sort_values(resource_col)
            ax.plot(front[resource_col], front["quality"], color='black', linewidth=1.0, linestyle='--', zorder=1)
            for front_row in front.itertuples():
                short = f"{front_row.Model.split('/')[-1]} ({front_row.Effort})"
                ax.annotate(short, (getattr(front_row, resource_col), front_row.quality), fontsize=5.5,
                            xytext=(3, 3), textcoords='offset points')
            ax.set_xscale('log')
            ax.set_title(label, fontsize=10, fontweight='bold')
            ax.set_ylim(-5, 105)
            ax.tick_params(labelsize=7)
    # language column headers: Aramaic left, Greek middle, Latin right
    for c, lang in enumerate(["Aramaic", "Greek", "Latin"]):
        axes[0][c].annotate(lang, xy=(0.5, 1.22), xycoords='axes fraction',
                            ha='center', fontsize=12, fontweight='bold', color='#374151')
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower right', bbox_to_anchor=(0.98, 0.06), fontsize=9)
    fig.supxlabel(xlabel, fontsize=11)
    fig.supylabel("Quality (score_consensus, 0-100)", fontsize=11)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout(rect=(0, 0, 1, 0.97))
    plt.savefig(out_png)
    plt.close()


def main():
    df = load_per_task_rows()
    print(f"Loaded {len(df)} (model, effort, task) scored rows across {df['Model'].nunique()} models.")
    plot_grid(df, "cost_usd", "Task cost ($, log scale)",
              "Per-task Pareto frontiers: quality vs cost", OUT_DIR / "clean_chart_pareto_cost_by_task.png")
    plot_grid(df, "latency_s", "Task latency (s, log scale)",
              "Per-task Pareto frontiers: quality vs latency", OUT_DIR / "clean_chart_pareto_latency_by_task.png")
    print("Wrote resac2026/clean_chart_pareto_cost_by_task.png")
    print("Wrote resac2026/clean_chart_pareto_latency_by_task.png")


if __name__ == "__main__":
    main()
