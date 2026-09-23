"""
Greek Q Benchmark Scorer (Codex Marchalianus / Vat. gr. 2125, p. 11)
SSHRC IDG: Generative AI in Digital Humanities Research Methodology

Computes CER/WER plus philological fidelity metrics (lunate sigma, nomina
sacra, lacuna handling, degenerate repetition) for the diplomatic layer of
each model's transcription against the TEI-derived ground truth.

Usage:
    python score_greek_q.py benchmark_results/greek_q_results_<ts>.json
"""

import json
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------- normalizing

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
PUNCT = "·.,;:'\"()[]{}<>|/\\-–—*_#`~!?" + "·;"

SIGMA_FORMS = "σςϲΣϹ"  # σ ς ϲ Σ Ϲ


def strip_diacritics(s: str) -> str:
    d = unicodedata.normalize("NFD", s)
    return "".join(c for c in d if not unicodedata.combining(c))


def greek_stream(text: str, fold_sigma: bool = True) -> str:
    """Reduce to a bare comparable majuscule character stream."""
    t = strip_diacritics(text)
    t = t.upper()
    out = []
    for c in t:
        if c in PUNCT or c.isspace():
            continue
        if not GREEK_RE.match(c):
            continue
        if fold_sigma and c in SIGMA_FORMS.upper():
            c = "Σ"
        out.append(c)
    return "".join(out)


def words(text: str) -> list:
    t = strip_diacritics(text).upper()
    t = re.sub(f"[{re.escape(PUNCT)}]", " ", t)
    t = t.replace("Ϲ", "Σ").replace("Σ", "Σ")
    toks = [w for w in t.split() if GREEK_RE.match(w[0])] if t.split() else []
    return toks


# Editorial lacuna brackets in a ground truth. Their presence marks the page
# as lacunose, which switches off the incomplete-capture rule: on a damaged
# page a short response can be an honest transcription of what survives.
LACUNA_RE = re.compile(r"\[\s*\.{2,}\s*\]|\[[^\]]*\]")


# ------------------------------------------------------------------ edit dist

def levenshtein(a, b) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# ------------------------------------------------------- diplomatic extraction

DIP_HEAD = re.compile(
    r"^\s*(#{1,6}\s*)?(\*{1,2}\s*)?(\b[IVX0-9]+[\.\)]\s*)?(\*{1,2}\s*)?"
    r"(diplomatic|diplomatique|διπλωματική|διπλωματικη)\b",
    re.I | re.M
)
NORM_HEAD = re.compile(
    r"^\s*(#{1,6}\s*)?(\*{1,2}\s*)?(\b[IVX0-9]+[\.\)]\s*)?(\*{1,2}\s*)?"
    r"(normalized|normalised|κανονικοποιημένη|κανονικοποιημενη)\b",
    re.I | re.M
)
NOTES_HEAD = re.compile(
    r"^\s*(#{1,6}\s*)?(\*{1,2}\s*)?(\b[IVX0-9]+[\.\)]\s*)?(\*{1,2}\s*)?"
    r"(scholarly notes|critical notes|notes\b|commentary|παρατηρήσεις|σχόλια)",
    re.I | re.M
)


def normalized_layer(output: str) -> str:
    """The model's own normalized edition, if it supplied one."""
    if not output:
        return ""
    m = NORM_HEAD.search(output)
    if not m:
        return ""
    tail = output[m.end():]
    n = NOTES_HEAD.search(tail)
    if n:
        tail = tail[:n.start()]
    return tail


def diplomatic_layer(output: str) -> str:
    """Everything before the model's normalized edition / notes section."""
    if not output:
        return ""
    start = 0
    d = DIP_HEAD.search(output)
    if d:
        start = d.end()
    cut = len(output)
    for pat in (NORM_HEAD, NOTES_HEAD):
        m = pat.search(output, start)
        if m:
            cut = min(cut, m.start())
    head = output[start:cut]
    # keep lines with substantial Greek text (drops English prose/headers without discarding lines containing lacuna brackets)
    keep = [ln for ln in head.splitlines() if len(GREEK_RE.findall(ln)) >= 3]
    return "\n".join(keep)


# ---------------------------------------------------------- fidelity measures

# Contracted sacred names, and the plene spellings that signal a silent
# (unmarked) expansion by the model. Both are searched in the sigma-folded
# majuscule stream, so ϲ/σ/ς/Σ all collapse to Σ.
# Contracted sacred names, paired with the plene spelling that signals a
# silent (unmarked) expansion. Two-letter contractions such as ΙΣ, ΚΣ and ΧΣ
# are deliberately excluded: in scriptio continua they collide constantly with
# ordinary letter sequences, so substring counts for them are not evidence.
# ΘΣ is retained because it is the one nomen sacrum tagged in the TEI ground
# truth for this page and its plene form is checked alongside it.
NOMINA_SACRA = {
    "ΘΣ": "ΘΕΟΣ",
    "ΠΡΩΝ": "ΠΑΤΕΡΩΝ",
    "ΙΛΗΜ": "ΙΕΡΟΥΣΑΛΗΜ",
    "ΠΝΑ": "ΠΝΕΥΜΑ",
}


def nomina_sacra_profile(gt_raw: str, hyp: str) -> dict:
    """Compare contracted vs. plene sacred names in ground truth and output.

    A model that writes ΘΕΟΣ where the manuscript has the contracted ΘΣ has
    silently expanded an abbreviation — a diplomatic-transcription failure
    even when the resulting text is lexically 'correct'.
    """
    g, h = greek_stream(gt_raw), greek_stream(hyp)
    out = {}
    for short, plene in NOMINA_SACRA.items():
        out[short] = {
            "gt_contracted": g.count(short),
            "hyp_contracted": h.count(short),
            "hyp_plene": h.count(plene),
        }
    return {k: v for k, v in out.items()
            if v["gt_contracted"] or v["hyp_contracted"] or v["hyp_plene"]}


def sigma_profile(text: str) -> dict:
    t = strip_diacritics(text)
    lunate = sum(t.count(c) for c in "ϲϹ")
    normal = sum(t.count(c) for c in "σςΣ")
    tot = lunate + normal
    return {"lunate": lunate, "non_lunate": normal,
            "lunate_rate": round(lunate / tot, 4) if tot else None}


def repetition_score(stream: str, n: int = 30) -> float:
    """Degenerate-loop measure: 1 - (distinct n-grams / total n-grams).

    0.0 = every window unique; values near 1.0 mean the output is a loop.
    """
    if len(stream) < n * 2:
        return 0.0
    grams = [stream[i:i + n] for i in range(len(stream) - n + 1)]
    return round(1 - len(set(grams)) / len(grams), 4)


def word_space_rate(text: str) -> float:
    """Spaces per Greek character in the diplomatic layer: scriptio continua check."""
    greek = sum(1 for c in text if GREEK_RE.match(c))
    sp = text.count(" ")
    return round(sp / greek, 4) if greek else 0.0


# ------------------------------------------------------------------- scoring

# Sidecar path of the staged benchmark package, set by main(); the normalized
# ground truth used for WER lives there (see load_gt_normalized).
_RESULTS_PATH = None


def load_gt_normalized(page_id):
    """The corpus's normalized ground truth for this page.

    The diplomatic stream is scriptio continua, so no word tokens can come
    from it: WER is computed against the corpus's normalized edition, keyed
    by page_id. The staged package (greek_q_transcriptions.json) sits two
    levels up from benchmark_results/. Returns "" when no sidecar is found;
    WER is then reported as n/a rather than fabricated from line blobs.
    """
    if not page_id or not _RESULTS_PATH:
        return ""
    here = os.path.dirname(os.path.abspath(_RESULTS_PATH))
    for _ in range(4):
        cand = os.path.join(here, "greek_q_transcriptions.json")
        if os.path.exists(cand):
            try:
                with open(cand, encoding="utf-8") as fh:
                    for e in json.load(fh):
                        if e.get("page_id") == page_id:
                            return e.get("normalized_ground_truth") or ""
            except Exception:
                return ""
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    return ""


def score(entry: dict) -> dict:
    res = entry["result"]
    gt_raw = entry["ground_truth"] or ""
    out_raw = res.get("output") or ""
    raw = res.get("raw_response") or {}
    choice = (raw.get("choices") or [{}])[0]
    finish = choice.get("finish_reason") or res.get("finish_reason")
    err = (choice.get("error") or {}).get("message") or res.get("error")
    usage = raw.get("usage") or {}
    cost = res.get("cost")
    if cost is None:
        cost = usage.get("cost")
    prompt_tokens = res.get("prompt_tokens") or usage.get("prompt_tokens") or 0
    completion_tokens = res.get("completion_tokens") or usage.get("completion_tokens") or 0
    total_tokens = res.get("total_tokens") or usage.get("total_tokens") or (prompt_tokens + completion_tokens)
    elapsed = res.get("elapsed_seconds")

    row = {
        "model": res["model"],
        "reported_status": res.get("status"),
        "finish_reason": finish,
        "error": err,
        "elapsed_seconds": elapsed,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost": cost,
        "output_chars": len(out_raw),
    }

    # The vendor's safety filter stopped the response. The visible text under
    # such a block is at best a fragment the vendor chose to withhold and at
    # worst refusal boilerplate; it is not a transcription the model stands
    # behind, so it must not be scored as one. Claude Opus 5 on the Aramaic
    # corpus is the motivating case: finish_reason was content_filter on all
    # 12 units while well-formed abstention prose still reached the client.
    if finish == "content_filter" or res.get("status") == "BLOCKED":
        row.update({"scored": False,
                    "failure_mode": "content filter blocked the response"})
        return row

    dip = diplomatic_layer(out_raw)
    if not dip.strip():
        row.update({"scored": False, "failure_mode":
                    "no usable transcription returned"})
        return row

    gt_s = greek_stream(gt_raw)
    hy_s = greek_stream(dip)
    gt_strict = greek_stream(gt_raw, fold_sigma=False)
    hy_strict = greek_stream(dip, fold_sigma=False)

    # WER is only meaningful where both sides carry word division. The
    # diplomatic ground truth is scriptio continua, so the comparison is each
    # model's own normalized edition against the corpus's normalized ground
    # truth (not against the diplomatic stream's line-blob "tokens").
    norm = normalized_layer(out_raw)
    gt_norm = load_gt_normalized(entry.get("page_id"))
    gt_w, hy_w = words(gt_norm) if gt_norm else [], words(norm)

    row.update({
        "scored": True,
        "gt_chars": len(gt_s),
        "hyp_chars": len(hy_s),
        "length_ratio": round(len(hy_s) / len(gt_s), 3) if gt_s else None,
        "CER": round(levenshtein(gt_s, hy_s) / len(gt_s), 4),
        "CER_sigma_strict": round(levenshtein(gt_strict, hy_strict) / len(gt_strict), 4),
        "supplied_normalized_edition": bool(norm.strip()),
        "WER_normalized": (round(levenshtein(gt_w, hy_w) / len(gt_w), 4)
                           if gt_w and hy_w else None),
        "wer_basis": "gt-normalized" if (gt_w and hy_w) else None,
        "repetition_30gram": repetition_score(hy_s),
        "space_per_greek_char": word_space_rate(dip),
        "sigma": sigma_profile(dip),
        "gt_sigma": sigma_profile(gt_raw),
        "nomina_sacra": nomina_sacra_profile(gt_raw, dip),
        "lacuna_markers": len(re.findall(r"\[\s*\.\.\.\s*\]|\[[^\]]{0,12}\]", out_raw)),
    })

    # Incomplete-capture rule (HANDOFF item 7 / findings_latin_isidore §6):
    # a response carrying under ~80% of a LACUNA-FREE ground truth is a
    # truncated or partial capture, not a transcription, and must not be
    # scored as one (five Latin models moved >0.6 CER on this alone). The
    # rule does not apply where the page itself is lacunose — on 4Q530 the
    # ground truth is mostly brackets, and a short honest transcription of
    # the extant letters is exactly what a disciplined model should emit.
    # The measurements are kept on the row for the record; only `scored`
    # flips, so nothing is silently discarded.
    if (gt_s and not LACUNA_RE.search(gt_raw)
            and row["length_ratio"] is not None and row["length_ratio"] < 0.8):
        row.update({
            "scored": False,
            "failure_mode": (f"incomplete capture: length_ratio "
                             f"{row['length_ratio']} < 0.80 on a lacuna-free "
                             f"page (rule: incomplete captures are not "
                             f"transcriptions)"),
        })
    return row


def main():
    global _RESULTS_PATH
    path = sys.argv[1] if len(sys.argv) > 1 else \
        "benchmark_results/greek_q_results_1787071894.json"
    _RESULTS_PATH = path
    data = json.load(open(path, encoding="utf-8"))
    rows = [score(e) for e in data]
    rows.sort(key=lambda r: (not r["scored"], r.get("CER", 9)))

    print(f"\nGreek Q benchmark — {path}\n" + "=" * 98)
    hdr = f"{'model':38s} {'CER':>7s} {'WER':>7s} {'len':>6s} {'rep':>6s} {'cost ($)':>9s} {'time (s)':>9s}"
    print(hdr)
    print("-" * 98)
    for r in rows:
        def f_cost(v):
            return f"${v:7.4f}" if isinstance(v, float) else f"{'—':>8s}"
        def f_time(v):
            return f"{v:7.1f}s" if isinstance(v, (float, int)) else f"{'—':>8s}"

        if r["scored"]:
            wer = r["WER_normalized"]
            wer_s = f"{wer:7.3f}" if wer is not None else f"{'n/a':>7s}"
            print(f"{r['model']:38s} {r['CER']:7.3f} {wer_s} "
                  f"{r['length_ratio']:6.2f} {r['repetition_30gram']:6.3f} "
                  f"{f_cost(r['cost']):>9s} {f_time(r['elapsed_seconds']):>9s}")
        else:
            print(f"{r['model']:38s} {'—':>7s} {'—':>7s}  [{r['finish_reason']}] "
                  f"{r.get('error') or r.get('failure_mode')} "
                  f"{f_cost(r['cost']):>9s} {f_time(r['elapsed_seconds']):>9s}")
    out = path.replace(".json", "_scored.json")
    json.dump(rows, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nDetail written to {out}")


if __name__ == "__main__":
    main()
