"""Human validation, multi-rater.

`make_review_html` — self-contained blind A/B voting page. Asks the rater's
name first; every vote records it, so several URAs can use copies of the same
page (same seed → same items) and each downloads their own votes_<name>.json.

`agreement` — accepts one or more votes files:
  * per-rater Cohen's κ vs the LLM judge
  * inter-rater Fleiss' κ across all human raters (items voted by ≥2 raters)
  * majority-vote (of humans) agreement with the judge
"""
from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from .corpus import load_translation_tasks


def make_review_html(
    comparisons_path: Path,
    results_path: Path,
    passages_path: Path,
    out_path: Path,
    n_samples: int = 40,
    seed: int = 42,
) -> None:
    comps = [
        json.loads(ln)
        for ln in comparisons_path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    seen = set()
    pool = []
    for c in comps:
        if c.get("winner") not in ("A", "B", "tie"):
            continue
        k = (c["passage_id"], c["model_a"], c["model_b"])
        if k in seen:
            continue
        seen.add(k)
        pool.append(c)

    rng = random.Random(seed)
    rng.shuffle(pool)
    pool = pool[:n_samples]

    tr = {}
    for ln in results_path.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            if (r.get("translation") or "").strip():
                tr[(r["candidate"], r["passage_id"])] = r["translation"]

    passages = {p["id"]: p for p in load_translation_tasks(passages_path, runnable_only=False)}

    items = []
    for i, c in enumerate(pool):
        pid = c["passage_id"]
        p = passages.get(pid, {})
        a_c, b_c = c["model_a"], c["model_b"]
        flip = rng.random() < 0.5
        left, right = (b_c, a_c) if flip else (a_c, b_c)
        items.append({
            "id": i,
            "item_key": f"{pid}|{a_c}|{b_c}",
            "passage_id": pid,
            "siglum": p.get("siglum", pid),
            "genre": p.get("genre", ""),
            "source": p.get("source", ""),
            "reference": p.get("reference", ""),
            "left": tr.get((left, pid), ""),
            "right": tr.get((right, pid), ""),
            "left_model": left,
            "right_model": right,
            "judge_winner_model": (
                a_c if c["winner"] == "A"
                else b_c if c["winner"] == "B" else "tie"
            ),
        })

    page = _HTML_TEMPLATE.replace("__DATA__", json.dumps(items, ensure_ascii=False))
    out_path.write_text(page, encoding="utf-8")


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>editio-bench human review</title>
<style>
  body { font-family: Georgia, serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #222; }
  .src { direction: rtl; font-size: 1.4rem; background: #f6f2e8; padding: 1rem; border-radius: 8px; }
  .src.ltr { direction: ltr; }
  .ref { font-style: italic; color: #555; margin: .75rem 0; }
  .pair { display: flex; gap: 1rem; margin: 1rem 0; }
  .cand { flex: 1; border: 2px solid #ccc; border-radius: 8px; padding: 1rem; cursor: pointer; }
  .cand:hover { border-color: #8a6d3b; }
  .meta { color: #777; font-size: .9rem; }
  button { font-size: 1rem; padding: .5rem 1.2rem; margin-right: .5rem; cursor: pointer; }
  input { font-size: 1rem; padding: .4rem; }
</style>
</head>
<body>
<h1>editio-bench — blind A/B review</h1>
<div id="app"></div>
<script>
const DATA = __DATA__;
let i = 0;
let rater = null;
const votes = [];
const app = document.getElementById("app");

function esc(s) {
  return (s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function renderName() {
  app.innerHTML = `
    <p>Enter your name or initials (recorded with each vote for inter-rater statistics):</p>
    <input id="rname" placeholder="e.g. KP"> <button onclick="setName()">Start</button>
    <p class="meta">Model identities are hidden. Judge on lexical accuracy, syntax,
    treatment of lacunae/sigla (silent gap-filling is a defect), register, and fluency.
    Votes stay in this page until you download them at the end.</p>
  `;
}
function setName() {
  const v = document.getElementById("rname").value.trim();
  if (!v) return;
  rater = v;
  render();
}

function render() {
  if (i >= DATA.length) { return renderDone(); }
  const it = DATA[i];
  const ltr = /^[\\u0000-\\u036f]/.test(it.source);
  app.innerHTML = `
    <p><b>Item ${i+1} / ${DATA.length}</b> — <span class="meta">${esc(it.siglum)} (${esc(it.genre)}) — rater: ${esc(rater)}</span></p>
    <div class="src${ltr ? ' ltr' : ''}">${esc(it.source)}</div>
    <div class="ref">Reference: ${esc(it.reference)}</div>
    <div class="pair">
      <div class="cand" onclick="choose('left')"><b>Candidate 1</b><p>${esc(it.left)}</p></div>
      <div class="cand" onclick="choose('right')"><b>Candidate 2</b><p>${esc(it.right)}</p></div>
    </div>
    <button onclick="choose('tie')">Tie / can't decide</button>
    <button onclick="choose('skip')">Skip</button>
  `;
}

function choose(which) {
  const it = DATA[i];
  if (which !== "skip") {
    let w = "tie";
    if (which === "left") w = it.left_model;
    else if (which === "right") w = it.right_model;
    votes.push({
      rater,
      item_key: it.item_key,
      passage_id: it.passage_id,
      model_a: it.item_key.split("|")[1],
      model_b: it.item_key.split("|")[2],
      human_winner_model: w,
      judge_winner_model: it.judge_winner_model
    });
  }
  i += 1;
  render();
}

function renderDone() {
  const blob = new Blob([JSON.stringify(votes, null, 2)], {type: "application/json"});
  const url = URL.createObjectURL(blob);
  const fname = "votes_" + rater.replace(/\\W+/g, "_") + ".json";
  app.innerHTML = `
    <h2>Done — ${votes.length} votes by ${esc(rater)}</h2>
    <p><a href="${url}" download="${fname}"><button>Download ${fname}</button></a></p>
    <p class="meta">Then: <code>python -m editio_bench.cli agreement votes_*.json</code></p>
  `;
}
renderName();
</script>
</body>
</html>
"""


def _cohen_kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return float("nan")
    agree = sum(1 for a, b in pairs if a == b)
    p_o = agree / n
    labels = sorted({x for pr in pairs for x in pr})
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    p_e = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    return (p_o - p_e) / (1 - p_e) if p_e < 1 else 1.0


def _fleiss_kappa(item_votes: dict[str, list[str]]) -> float | None:
    """item_votes: item_key -> list of category labels (one per rater).
    Uses only items with >= 2 votes; standard Fleiss' kappa with variable
    handling by requiring a common n (uses the minimum >= 2 and subsamples
    deterministically)."""
    usable = {k: v for k, v in item_votes.items() if len(v) >= 2}
    if len(usable) < 2:
        return None
    n = min(len(v) for v in usable.values())
    cats = sorted({c for v in usable.values() for c in v})
    N = len(usable)
    p_j = defaultdict(float)
    P_i = []
    for _, v in sorted(usable.items()):
        v = v[:n]
        counts = Counter(v)
        for c in cats:
            p_j[c] += counts.get(c, 0)
        s = sum(c * (c - 1) for c in counts.values())
        P_i.append(s / (n * (n - 1)))
    total = N * n
    p_j = {c: p_j[c] / total for c in cats}
    P_bar = sum(P_i) / N
    P_e = sum(p**2 for p in p_j.values())
    if P_e >= 1:
        return 1.0
    return (P_bar - P_e) / (1 - P_e)


def agreement(votes_paths: list[Path]) -> dict:
    all_votes = []
    for vp in votes_paths:
        all_votes.extend(json.loads(vp.read_text(encoding="utf-8")))
    if not all_votes:
        return {"n": 0}

    by_rater: dict[str, list[dict]] = defaultdict(list)
    for v in all_votes:
        by_rater[v.get("rater", "anonymous")].append(v)

    per_rater = {}
    for rater, votes in by_rater.items():
        pairs = [(v["human_winner_model"], v["judge_winner_model"]) for v in votes]
        agree = sum(1 for a, b in pairs if a == b)
        per_rater[rater] = {
            "n": len(votes),
            "raw_agreement_vs_judge": round(agree / len(votes), 3),
            "cohens_kappa_vs_judge": round(_cohen_kappa(pairs), 3),
        }

    # Inter-rater Fleiss' kappa on items with >= 2 human votes.
    item_votes: dict[str, list[str]] = defaultdict(list)
    for v in all_votes:
        item_votes[v["item_key"]].append(v["human_winner_model"])
    fleiss = _fleiss_kappa(item_votes)

    # Majority human vote vs judge on multi-voted items; single votes pass through.
    maj_pairs = []
    judge_by_item = {}
    for v in all_votes:
        judge_by_item[v["item_key"]] = v["judge_winner_model"]
    for k, hv in item_votes.items():
        top, cnt = Counter(hv).most_common(1)[0]
        if cnt * 2 <= len(hv):  # no strict majority
            continue
        maj_pairs.append((top, judge_by_item[k]))
    maj_kappa = round(_cohen_kappa(maj_pairs), 3) if maj_pairs else None

    return {
        "n_votes": len(all_votes),
        "n_raters": len(by_rater),
        "per_rater": per_rater,
        "fleiss_kappa_inter_rater": (
            round(fleiss, 3) if fleiss is not None else None
        ),
        "majority_vote_vs_judge": {
            "n_items": len(maj_pairs),
            "cohens_kappa": maj_kappa,
        },
        "interpretation": (
            "kappa > 0.6: substantial; 0.4-0.6: moderate (use with caution); "
            "< 0.4: do not trust the automated leaderboard on this corpus. "
            "If inter-rater kappa is itself low, refine the grading criteria "
            "before blaming the judge."
        ),
    }
