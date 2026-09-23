"""Character error rate for the three image-bearing transcription tasks.

The clean suite scores every task with an LLM judge panel. On the visual
transcription tasks that panel proved unreliable: on Vat. lat. 629 f. 3v,
answers whose letters are identical to the ground truth were scored anywhere
from 70 to 96, the spread tracking presentation rather than reading. This
script adds a deterministic measure beside the judges, reusing the script
profiles already built for the transcription corpora:

  Greek   greek_stream (score_greek_q.py): majuscule, diacritics stripped,
          all sigma forms folded. Lunate omega (Coptic Ⲱ) is folded to Ω first,
          since the ground truth accepts either.
  Latin   latin_stream (score_transcription.py): loose CER folds long s, u/v,
          i/j, case and abbreviation marks (letter identification); strict CER
          keeps the marks (abbreviation fidelity).
  Aramaic hebrew_stream: loose folds final forms, strict keeps them. The
          ground truth is reduced to the letters physically extant (editorial
          [ ] restorations and ( ) alternatives removed), and so is the model's
          diplomatic layer, so a model is neither charged for honest gaps nor
          credited for reproducing a printed restoration.

The ground truths cover the four lines inside each crop, but many models go on
to transcribe the rest of the visible page. CER is therefore computed against
the best-matching span of the model's diplomatic layer (free leading and
trailing text), and hyp_ratio (model chars / GT chars) is reported so that
over-generation stays visible instead of being silently forgiven.

Reads editio-bench/resac2026_clean_sweep.json and each config's results CSV;
writes resac2026/clean_suite_visual_cer.csv (one row per config x task).

Usage: python3 scripts/score_visual_cer.py
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import score_greek_q as gq  # noqa: E402
import score_transcription as st  # noqa: E402

sys.path.insert(0, str(ROOT / "editio-bench"))
from editio_bench.phase_bench import NO_IMAGE_STATUS, claims_no_image  # noqa: E402

EB = ROOT / "editio-bench"
SWEEP_JSON = EB / "resac2026_clean_sweep.json"
BENCH_JSON = EB / "data" / "benchmarks.json"
OUT_CSV = ROOT / "resac2026" / "clean_suite_visual_cer.csv"
csv.field_size_limit(10**9)

LINE_RE = re.compile(r"^\s*Line\s+\d+\s*:\s*(.*)$", re.M)
# "Saias (Eſaiaſ)" -> the parenthesised scribal form; an optional one-letter
# token before it absorbs the detached rubricated initial ("E Saias (Eſaiaſ)").
LATIN_ALT = re.compile(r"(?:(?<!\S)\S )?\S+ \(([^()]+)\)")
PAREN = re.compile(r"\s*\([^()]*\)")
# Refusal phrasings DECLINED_RE (score_transcription.py) misses.
DECLINED_EXTRA = re.compile(
    r"(can.?t|cannot|can not|unable to) (make|provide|produce|give|supply|responsibly)"
    r"|does not (support|allow) a reliable|too (blurred|indistinct|dark)"
    r"|(can.?t|cannot|can not|unable to) perform (this|the) transcription", re.I)


# Coptic letters U+2C80..U+2CB1 in capital/small pairs, in Greek alphabet
# order (sou, U+2C8A, has no Greek letter). Some models write the whole
# majuscule in these look-alikes; they are a faithful rendering, not noise.
COPTIC_GREEK = "ΑΒΓΔΕ\0ΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
COPTIC_FOLD = {}
for i, g in enumerate(COPTIC_GREEK):
    if g != "\0":
        COPTIC_FOLD[0x2C80 + 2 * i] = g
        COPTIC_FOLD[0x2C81 + 2 * i] = g.lower()


def fold_greek(t):
    return t.translate(COPTIC_FOLD)


def greek_majuscule(t):
    """Drop lowercase Greek. The diplomatic layer is majuscule; many models
    append an unlabelled normalized edition in minuscule, whose letters fold
    to the same majuscule stream and would otherwise match the ground truth."""
    return "".join(c for c in t if not (c.isalpha() and c.islower()))


TASKS = {
    "trans-greek-marchalianus-p11": {
        "label": "Greek",
        "gt": lambda lines: fold_greek(" ".join(lines)),
        "gt_strict": None,
        "hyp": lambda a: greek_majuscule(PAREN.sub("", gq.diplomatic_layer(fold_greek(a)))),
        "loose": lambda t: gq.greek_stream(t, fold_sigma=True),
        "strict": None,
    },
    "trans-latin-vatlat629-f3v": {
        "label": "Latin",
        "gt": lambda lines: PAREN.sub("", " ".join(lines)),
        "gt_strict": lambda lines: LATIN_ALT.sub(r"\1", " ".join(lines)),
        "hyp": lambda a: st.diplomatic_layer(st.unwrap_rubrics(a), st.PROFILES["latin"]["script_re"]),
        "loose": lambda t: st.latin_stream(t, fold=True),
        "strict": lambda t: st.latin_stream(t, fold=False),
    },
    "trans-aramaic-4q530-f2ii": {
        "label": "Aramaic",
        "gt": lambda lines: st.extant_only(" ".join(lines)),
        "gt_strict": None,
        "hyp": lambda a: st.extant_only(
            st.diplomatic_layer(a, st.PROFILES["hebrew"]["script_re"], min_chars=2)),
        "loose": lambda t: st.hebrew_stream(t, fold_finals=True),
        "strict": lambda t: st.hebrew_stream(t, fold_finals=False),
    },
}


def span_distance(gt, hyp):
    """Edit distance from gt to the best-matching substring of hyp."""
    if not gt:
        return 0
    prev = [0] * (len(hyp) + 1)            # free start anywhere in hyp
    for i, cg in enumerate(gt, 1):
        cur = [i]
        for j, ch in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (cg != ch)))
        prev = cur
    return min(prev)                        # free end anywhere in hyp


def cer(gt, hyp):
    return round(span_distance(gt, hyp) / len(gt), 4) if gt else None


def load_ground_truth():
    data = json.loads(BENCH_JSON.read_text())
    data = data if isinstance(data, list) else data.get("benchmarks", data)
    gts = {}
    for b in data:
        if b["id"] in TASKS:
            lines = LINE_RE.findall(b["ground_truth"])
            if not lines:
                raise SystemExit(f"{b['id']}: no 'Line N:' rows in ground truth")
            gts[b["id"]] = lines
    return gts


def resolve(path):
    p = Path(path)
    if not p.is_absolute():                 # public release stores repo-relative paths
        p = ROOT / p
    if p.exists():
        return p
    # older sweep entries were recorded before the project moved under SSHRC/
    alt = Path(str(p).replace("/Research/IDG/", "/Research/SSHRC/IDG/"))
    return alt if alt.exists() else None


def main():
    gts = load_ground_truth()
    sweep = json.loads(SWEEP_JSON.read_text())
    rows = []
    for key, v in sweep.items():
        path = resolve(v.get("csv", ""))
        if path is None:
            continue
        with path.open(encoding="utf-8", newline="") as f:
            answers = {r["benchmark"]: r for r in csv.DictReader(f) if r["benchmark"] in TASKS}
        for tid, spec in TASKS.items():
            r = answers.get(tid)
            if r is None:
                continue
            ok = r.get("answer_status") == "ok"
            hyp_text = spec["hyp"](r.get("answer", "")) if ok else ""
            g = spec["loose"](spec["gt"](gts[tid]))
            h = spec["loose"](hyp_text)
            row = {
                "config": key, "Model": v["model"], "Effort": v["effort"],
                "task": tid, "script": spec["label"], "answer_status": r.get("answer_status"),
                "cer": cer(g, h) if ok else None,
                "cer_strict": None,
                "gt_chars": len(g), "hyp_chars": len(h),
                "hyp_ratio": round(len(h) / len(g), 2) if g else None,
                "declined": bool(r.get("answer_status") == NO_IMAGE_STATUS
                                 or (ok and not h and (st.DECLINED_RE.search(r.get("answer", ""))
                                                       or DECLINED_EXTRA.search(r.get("answer", ""))))),
                # distinct from an abstention about the manuscript ("no ink visible")
                "claims_no_image": claims_no_image(r.get("answer", "")),
                "judge_score": r.get("score_consensus"),
            }
            if ok and spec["strict"]:
                gs = spec["strict"]((spec["gt_strict"] or spec["gt"])(gts[tid]))
                row["cer_strict"] = cer(gs, spec["strict"](hyp_text))
            rows.append(row)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT_CSV} ({len(rows)} rows)")

    by_cfg = {}
    for r in rows:
        by_cfg.setdefault(r["config"], {})[r["script"]] = r["cer"]
    print(f"\n{'config':48} {'Greek':>7} {'Latin':>7} {'Aramaic':>7} {'mean':>7}")
    ranked = sorted(by_cfg.items(), key=lambda kv: (
        sum(x for x in kv[1].values() if x is not None) / max(1, sum(x is not None for x in kv[1].values()))
        if any(x is not None for x in kv[1].values()) else 9))
    for k, c in ranked:
        vals = [c.get(s) for s in ("Greek", "Latin", "Aramaic")]
        got = [x for x in vals if x is not None]
        fmt = lambda x: f"{x:7.3f}" if x is not None else f"{'—':>7}"
        print(f"{k:48} {fmt(vals[0])} {fmt(vals[1])} {fmt(vals[2])} "
              f"{fmt(sum(got) / len(got) if got else None)}")


if __name__ == "__main__":
    main()
