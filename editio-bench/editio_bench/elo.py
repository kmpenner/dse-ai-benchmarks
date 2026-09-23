"""Bradley–Terry model over pairwise comparisons, reported on an ELO-like
scale, with bootstrap confidence intervals resampled over passages.

Ties are handled by awarding half a win to each side (standard practice).
Resampling over *passages* (not individual comparisons) respects the fact
that comparisons on the same passage are correlated.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

ELO_SCALE = 400.0 / math.log(10.0)
ELO_ANCHOR = 1000.0


def fit_bradley_terry(
    models: list[str],
    wins: dict[tuple[str, str], float],
    iters: int = 2000,
    tol: float = 1e-9,
) -> dict[str, float]:
    """Minorize–maximize (Hunter 2004) fit. wins[(i, j)] = #wins of i over j
    (ties counted as 0.5 to each). Returns strength params normalised to
    mean-zero log scale."""
    idx = {m: k for k, m in enumerate(models)}
    n = len(models)
    W = np.zeros((n, n))
    for (a, b), w in wins.items():
        W[idx[a], idx[b]] += w

    p = np.ones(n)
    # Regularize with a tiny pseudo-count so undefeated/never-winning models
    # don't diverge to +/- infinity.
    eps = 0.01
    W = W + eps

    total_wins = W.sum(axis=1)
    for _ in range(iters):
        p_new = np.empty(n)
        for i in range(n):
            denom = 0.0
            for j in range(n):
                if i == j:
                    continue
                nij = W[i, j] + W[j, i]
                denom += nij / (p[i] + p[j])
            p_new[i] = total_wins[i] / denom if denom > 0 else p[i]
        p_new /= np.exp(np.mean(np.log(p_new)))  # geometric-mean normalise
        if np.max(np.abs(np.log(p_new) - np.log(p))) < tol:
            p = p_new
            break
        p = p_new

    log_p = np.log(p)
    log_p -= log_p.mean()
    return {m: float(log_p[idx[m]]) for m in models}


def to_elo(strengths: dict[str, float]) -> dict[str, float]:
    return {m: round(ELO_ANCHOR + ELO_SCALE * s, 1) for m, s in strengths.items()}


def _wins_from_comparisons(comparisons: list[dict]) -> dict[tuple[str, str], float]:
    wins: dict[tuple[str, str], float] = defaultdict(float)
    for c in comparisons:
        a, b, w = c["model_a"], c["model_b"], c["winner"]
        if w == "A":
            wins[(a, b)] += 1.0
        elif w == "B":
            wins[(b, a)] += 1.0
        elif w == "tie":
            wins[(a, b)] += 0.5
            wins[(b, a)] += 0.5
    return wins


def elo_with_ci(
    comparisons: list[dict],
    models: list[str],
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict[str, dict]:
    """comparisons: [{model_a, model_b, winner: 'A'|'B'|'tie', passage_id}, ...]

    Returns {model: {elo, ci_low, ci_high, n_comparisons}}.
    Bootstrap resamples passages with replacement.
    """
    valid = [c for c in comparisons if c.get("winner") in ("A", "B", "tie")]
    point = to_elo(fit_bradley_terry(models, _wins_from_comparisons(valid)))

    by_passage: dict[str, list[dict]] = defaultdict(list)
    for c in valid:
        by_passage[c["passage_id"]].append(c)
    passage_ids = sorted(by_passage)

    rng = np.random.default_rng(seed)
    samples: dict[str, list[float]] = {m: [] for m in models}
    for _ in range(n_bootstrap):
        chosen = rng.choice(len(passage_ids), size=len(passage_ids), replace=True)
        boot = []
        for k in chosen:
            boot.extend(by_passage[passage_ids[k]])
        elos = to_elo(fit_bradley_terry(models, _wins_from_comparisons(boot)))
        for m in models:
            samples[m].append(elos[m])

    n_by_model: dict[str, int] = defaultdict(int)
    for c in valid:
        n_by_model[c["model_a"]] += 1
        n_by_model[c["model_b"]] += 1

    out = {}
    for m in models:
        arr = np.array(samples[m])
        out[m] = {
            "elo": point[m],
            "ci_low": round(float(np.percentile(arr, 2.5)), 1),
            "ci_high": round(float(np.percentile(arr, 97.5)), 1),
            "n_comparisons": n_by_model[m],
        }
    return out
