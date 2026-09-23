"""Build the master CSV and charts for the clean, uniform re-run.

Replaces the entire old dss_benchmark_35models_16tasks* patchwork: every
number here comes from one pipeline (current phase_bench.py, real images,
minimax+gemini panel with a deepseek-v4-flash tiebreak on >10pt disagreement,
real cost/latency capture), read from
editio-bench/resac2026_clean_sweep.json (per (model,effort) summary) and the
individual editio-bench/results/phase_*_sweep.csv files (per-task detail).

No "T:" column anywhere -- see git log on this branch for why that column
never measured anything real.

Usage: python3 scripts/build_clean_suite_report.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
EB = ROOT / "editio-bench"
SWEEP_JSON = EB / "resac2026_clean_sweep.json"
OUT_CSV = ROOT / "resac2026" / "clean_suite_master.csv"
OUT_DIR = ROOT / "resac2026"
VISUAL_CER_CSV = OUT_DIR / "clean_suite_visual_cer.csv"   # scripts/score_visual_cer.py

TASK_ORDER = [
    "trans-greek-marchalianus-p11", "trans-latin-vatlat629-f3v", "trans-aramaic-4q530-f2ii",
    "coll-greek-marchalianus-vitae", "coll-latin-vatlat629-isidore", "coll-aramaic-4q530-giants-parallels",
    "translat-greek-marchalianus-siloam", "translat-latin-vatlat629-seraphim", "translat-aramaic-4q530-tree-vision",
    "annot-greek-marchalianus-tei-msd", "annot-latin-vatlat629-abbreviations", "annot-aramaic-4q530-morphology",
    "encode-greek-marchalianus-teiheader",
]
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
    'Z.ai / GLM': '#0ea5e9', 'MiniMax': '#9333ea', 'Unbiased': '#14b8a6', 'Other': '#64748b',
}


def provider_of(model: str) -> str:
    m = model.lower()
    for needle, prov in [('anthropic', 'Anthropic'), ('claude', 'Anthropic'), ('google', 'Google'),
                          ('gemini', 'Google'), ('gemma', 'Google'), ('openai', 'OpenAI'), ('gpt', 'OpenAI'),
                          ('x-ai', 'xAI'), ('grok', 'xAI'), ('deepseek', 'DeepSeek'), ('meta', 'Meta'),
                          ('llama', 'Meta'), ('qwen', 'Qwen'), ('mistral', 'Mistral'), ('z-ai', 'Z.ai / GLM'),
                          ('glm', 'Z.ai / GLM'), ('minimax', 'MiniMax'), ('unbiased', 'Unbiased'), ('stealth', 'Unbiased')]:
        if needle in m:
            return prov
    return 'Other'


def pareto_front(df: pd.DataFrame, resource_col: str) -> pd.Series:
    q, r = df["quality"].to_numpy(), df[resource_col].to_numpy()
    n = len(df)
    dominated = np.zeros(n, dtype=bool)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if q[j] >= q[i] and r[j] <= r[i] and (q[j] > q[i] or r[j] < r[i]):
                dominated[i] = True
                break
    return pd.Series(~dominated, index=df.index)


def _run_is_replayed(row: pd.Series) -> tuple[str, int] | None:
    """Detect a config whose CSV is (mostly) cache replays of an earlier run.

    The reasoning-escalation retry in phase_bench stores answers under the
    escalated effort's cache key, so a sweep at a different requested effort
    can silently replay an earlier config's answers. A run where most rows
    carry answer_cached=True is a copy, not a measurement.
    Returns (earlier-config-key, n_cached) or None.
    """
    try:
        tdf = pd.read_csv(row["csv"])
    except FileNotFoundError:
        return None
    if "answer_cached" not in tdf.columns or len(tdf) == 0:
        return None
    n_cached = int(tdf["answer_cached"].astype(bool).sum())
    if n_cached <= len(tdf) / 2:
        return None
    # Which earlier config was the source? Match by (model, per-task latency).
    sweep = json.loads(SWEEP_JSON.read_text())
    for key, v in sweep.items():
        if key == row["config"] or v.get("model") != row["Model"]:
            continue
        try:
            odf = pd.read_csv(ROOT / v["csv"]).set_index("benchmark")
        except FileNotFoundError:
            continue
        if "answer_latency_s" not in odf.columns:
            continue
        common = tdf.set_index("benchmark").index.intersection(odf.index)
        if len(common) == 0:
            continue
        a = tdf.set_index("benchmark").loc[common, "answer_latency_s"].round(2)
        b = odf.loc[common, "answer_latency_s"].round(2)
        if (a == b).mean() > 0.8:
            return key, n_cached
    return "unknown source", n_cached


def load_master() -> pd.DataFrame:
    sweep = json.loads(SWEEP_JSON.read_text())
    rows = []
    for key, v in sweep.items():
        if "quality" not in v or v["quality"] is None:
            continue  # error or fully-unscored config
        rows.append({
            "config": key, "Model": v["model"], "Effort": v["effort"],
            "Provider": provider_of(v["model"]),
            "quality": v["quality"], "tasks_attempted": v["n_tasks"], "tasks_scored": v["n_scored"],
            "total_cost_usd": v["total_cost_usd"], "avg_cost_usd": v["avg_cost_usd"],
            "total_latency_s": v["total_latency_s"], "avg_latency_s": v["avg_latency_s"],
            "csv": v["csv"],
        })
    df = pd.DataFrame(rows)
    # Chart-eligibility gates (2026-09-10 audit):
    # 1. Coverage — a quality mean over a mostly-unscored suite is survivorship
    #    bias (gemma-4-31b-it:free "70.5" = 2 surviving tasks). Configs must
    #    cover >=90% of tasks to be plotted or ranked.
    # 2. Cache replay — escalation-replayed runs are copies of an earlier
    #    config, not independent measurements; plotting both corrupts the
    #    Pareto frontier (duplicate points can never be dominated).
    COVERAGE_MIN = 0.9
    df["coverage"] = df["tasks_scored"] / df["tasks_attempted"]
    df["fully_scored"] = df["coverage"] >= COVERAGE_MIN
    df["fully_scored_note"] = df.apply(
        lambda r: "" if r["fully_scored"]
        else f"only {r['tasks_scored']}/{r['tasks_attempted']} tasks scored "
             f"(<{COVERAGE_MIN:.0%} coverage)", axis=1)
    df["replayed"] = df.apply(_run_is_replayed, axis=1)
    df["replayed_note"] = df.apply(
        lambda r: "cache replay of {} ({}/{} answers cached)".format(
            r["replayed"][0], r["replayed"][1], r["tasks_attempted"])
        if r["replayed"] else "", axis=1)
    df["excluded_note"] = (df["fully_scored_note"] + " " + df["replayed_note"]).str.strip()
    df["included"] = df["fully_scored"] & (df["excluded_note"] == "")
    df["on_cost_frontier"] = pareto_front(df, "total_cost_usd")
    df["on_latency_frontier"] = pareto_front(df, "total_latency_s")
    df["on_any_frontier"] = df["on_cost_frontier"] | df["on_latency_frontier"]

    # per-task score_consensus, pivoted in from each config's own results CSV
    for tid in TASK_ORDER:
        df[TASK_LABEL[tid]] = np.nan
    for i, row in df.iterrows():
        try:
            tdf = pd.read_csv(row["csv"]).set_index("benchmark")
        except FileNotFoundError:
            continue
        for tid in TASK_ORDER:
            if tid in tdf.index and pd.notna(tdf.loc[tid, "score_consensus"]):
                df.at[i, TASK_LABEL[tid]] = tdf.loc[tid, "score_consensus"]

    # deterministic CER beside the judge scores on the three image tasks
    if VISUAL_CER_CSV.exists():
        cer = pd.read_csv(VISUAL_CER_CSV).pivot(index="config", columns="script", values="cer")
        cer.columns = [f"CER: {c}" for c in cer.columns]
        df = df.merge(cer, left_on="config", right_index=True, how="left")

    df = df.sort_values("quality", ascending=False).reset_index(drop=True)
    return df


def plot_leaderboard(df: pd.DataFrame, out_png: Path):
    fig, ax = plt.subplots(figsize=(11, max(6, 0.32 * len(df))), dpi=200)
    labels = [f"{r.Model.split('/')[-1]} ({r.Effort})" for r in df.itertuples()]
    colors = [PROVIDER_COLORS.get(p, '#64748b') for p in df["Provider"]]
    y = np.arange(len(df))
    ax.barh(y, df["quality"], color=colors)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Quality (mean score_consensus, 13 tasks)")
    ax.set_xlim(0, 100)
    ax.set_title("Clean re-run leaderboard — one pipeline, real images, real cost/latency", fontsize=11, fontweight='bold')
    for yi, q in zip(y, df["quality"]):
        ax.text(q + 1, yi, f"{q:.1f}", va='center', fontsize=7)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def plot_pareto(df: pd.DataFrame, resource_col: str, frontier_col: str, xlabel: str, out_png: Path, logx=True):
    fig, ax = plt.subplots(figsize=(10, 7), dpi=200)
    for prov, sub in df.groupby("Provider"):
        ax.scatter(sub[resource_col], sub["quality"], label=prov,
                   color=PROVIDER_COLORS.get(prov, '#64748b'), s=45, alpha=0.85,
                   edgecolors='black' if frontier_col else 'none', linewidths=0.4)
    front = df[df[frontier_col]].sort_values(resource_col)
    ax.plot(front[resource_col], front["quality"], color='black', linewidth=1.2, linestyle='--', zorder=1)
    seen_points = {}  # (resource, quality) -> [efforts] -- collapse identical
    for r in front.itertuples():           # points (a reasoning-mandatory model whose
        seen_points.setdefault((getattr(r, resource_col), r.quality), []).append(r)  # requested effort fell back to the same real one)
    for (x, q), rs in seen_points.items():
        label = f"{rs[0].Model.split('/')[-1]} ({'/'.join(sorted({r.Effort for r in rs}))})"
        ax.annotate(label, (x, q), fontsize=7, xytext=(4, 4), textcoords='offset points')
    if logx:
        ax.set_xscale('log')
    ax.set_xlabel(xlabel); ax.set_ylabel("Quality")
    ax.set_title(f"Pareto frontier: quality vs {xlabel}", fontsize=11, fontweight='bold')
    ax.legend(fontsize=7, loc='lower right')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def plot_heatmap(df: pd.DataFrame, out_png: Path):
    cols = [TASK_LABEL[t] for t in TASK_ORDER]
    labels = [f"{r.Model.split('/')[-1]} ({r.Effort})" for r in df.itertuples()]
    data = df[cols].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(13, max(6, 0.3 * len(df))), dpi=200)
    im = ax.imshow(data, cmap='YlGnBu', vmin=0, vmax=100, aspect='auto')
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=7)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not np.isnan(data[i, j]):
                ax.text(j, i, f"{data[i,j]:.0f}", ha='center', va='center', fontsize=6,
                        color='white' if data[i, j] > 55 else 'black')
    fig.colorbar(im, ax=ax, shrink=0.6, label='score_consensus (0-100)')
    ax.set_title("Per-task scores — clean re-run (blank = not scored / no vision support)", fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def plot_heatmap_with_cost_latency(df: pd.DataFrame, out_png: Path):
    """Score grid with two appended resource columns: total cost (answer +
    judging) and total answer latency, on a shared log-10 colour scale.

    The resource columns use log10 because cost spans ~$0.01–$2.7 and latency
    ~8s–12,400s across configs; their colours are NOT comparable to the score
    colours (separate normalisation, separated by a spacer column), and the
    cell text shows the real value, not the log. Cheaper/faster = darker;
    a *lower* value is better there, unlike the score columns.
    """
    cols = [TASK_LABEL[t] for t in TASK_ORDER]
    labels = [f"{r.Model.split('/')[-1]} ({r.Effort})" for r in df.itertuples()]
    scores = df[cols].to_numpy(dtype=float)
    cost = df["total_cost_usd"].to_numpy(dtype=float)
    lat = df["total_latency_s"].to_numpy(dtype=float)

    def log_norm(v):
        v = np.asarray(v, dtype=float)
        lo, hi = np.log10(v.min()), np.log10(v.max())
        if hi == lo:
            return np.zeros_like(v)
        return (np.log10(v) - lo) / (hi - lo)

    cost_n, lat_n = log_norm(cost), log_norm(lat)
    n_res = 2
    spacer = 1
    total_cols = scores.shape[1] + spacer + n_res
    data = np.full((len(df), total_cols), np.nan)
    data[:, :scores.shape[1]] = scores
    data[:, -n_res:] = np.column_stack([cost_n, lat_n]) * 100.0  # reuse 0-100 scale

    fig, ax = plt.subplots(figsize=(15, max(6, 0.3 * len(df))), dpi=200)
    im = ax.imshow(np.where(np.isnan(data), np.nan, data), cmap='YlGnBu',
                   vmin=0, vmax=100, aspect='auto')
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=7)
    col_labels = cols + ["", "Cost $", "Latency s"]
    ax.set_xticks(range(total_cols)); ax.set_xticklabels(col_labels, rotation=45,
                                                         ha='right', fontsize=8)
    # vertical separator between the score grid and the resource columns
    ax.axvline(scores.shape[1] - 0.5 + spacer, color='black', linewidth=1.2)
    for i in range(len(df)):
        for j in range(total_cols):
            if np.isnan(data[i, j]):
                continue
            if j < scores.shape[1]:
                txt, fs = f"{scores[i, j]:.0f}", 6
            elif j == total_cols - 2:
                txt, fs = f"${cost[i]:.3g}", 5.5
            else:
                txt, fs = f"{lat[i]:.3g}s", 5.5
            dark = data[i, j] > 55
            ax.text(j, i, txt, ha='center', va='center', fontsize=fs,
                    color='white' if dark else 'black')
    fig.colorbar(im, ax=ax, shrink=0.6,
                 label='score (0-100) | cost & latency: log-normalised, darker = cheaper/faster')
    ax.set_title("Per-task scores + run cost/latency — clean re-run "
                 "(resource columns on their own log colour scale)", fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def main():
    df = load_master()
    df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {OUT_CSV} ({len(df)} configs)")
    inc = df[df["included"]]
    exc = df[~df["included"]]
    if len(exc):
        print(f"\nExcluded from charts ({len(exc)} configs — partial scoring or cache replay):")
        for r in exc.itertuples():
            print(f"  {r.config:45s} {r.excluded_note}")
    plot_leaderboard(inc, OUT_DIR / "clean_chart_leaderboard.png")
    plot_pareto(inc, "total_cost_usd", "on_cost_frontier", "Total cost ($, log scale)",
                OUT_DIR / "clean_chart_pareto_cost.png")
    plot_pareto(inc, "total_latency_s", "on_latency_frontier", "Total latency (s, log scale)",
                OUT_DIR / "clean_chart_pareto_latency.png")
    plot_heatmap(inc, OUT_DIR / "clean_chart_heatmap.png")
    plot_heatmap_with_cost_latency(inc, OUT_DIR / "clean_chart_heatmap_cost_latency.png")
    print("\nCharts written to resac2026/clean_chart_*.png")
    print("\nFinal frontier (cost or latency):")
    print(inc[inc["on_any_frontier"]][["Model", "Effort", "quality", "total_cost_usd", "total_latency_s"]]
          .to_string(index=False))


if __name__ == "__main__":
    main()
