"""
Benchmark scorer for the Aramaic (4Q530) and Latin (Vat.lat.629) corpora.
SSHRC IDG: Generative AI in Digital Humanities Research Methodology.

The Greek page has its own scorer (score_greek_q.py) because the metrics that
matter there — lunate sigma, nomina sacra, scriptio continua — are Greek
problems. This module carries the two script profiles that came after it and
the measures those corpora need:

  hebrew  4Q530, Herodian square script. Word-divided, so WER is computed on
          the diplomatic layer directly rather than on the model's own
          normalized edition. Final letter forms are folded for the headline
          CER and kept for the strict one. Crucially, the ground truth
          contains editorial restorations inside [ ]: CER is therefore
          reported twice, once against everything and once against the
          letters actually on the leather, and the restored material is
          searched for in the model's output as evidence that it reproduced
          a printed edition instead of reading the fragment.

  latin   Vat.lat.629, Caroline-Gothic transitional minuscule. The headline
          CER folds the palaeographic variation a modern reader ignores
          (long s, u/v, i/j, case, the titulus) so that it measures letter
          identification; the strict CER keeps the abbreviation marks, so the
          gap between the two is the model's abbreviation fidelity.

Usage:
    python score_transcription.py benchmark_results/<file>.json --profile hebrew
"""

import argparse
import json
import re
import unicodedata
from collections import defaultdict

# ------------------------------------------------------------------ profiles

HEBREW_LETTERS = "אבגדהוזחטיכךלמםנןסעפףצץקרשת"
FINALS = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
# Uncertainty is marked two ways in this corpus: with combining marks in
# 4Q530.txt (U+05AF circle above = lecture tres vraisemblable, U+0307 dot
# above = lecture incertaine) and with the spacing characters the prompt asks
# models to use, since most models will not emit Hebrew combining points.
UNCERTAIN_MARKS = "°•·˚\u05af\u0307"
# Allographs and ligatures folded for the loose (letter-identification) layer,
# on the same principle as the Greek scorer's collapse of all four sigma
# forms: a model that writes the scribe's dotless i or r rotunda has read the
# letter correctly and should not be charged for rendering it faithfully.
# Abbreviation *marks* are deliberately not folded away here — they are
# stripped as combining characters in the loose layer and kept in the strict
# one, so the gap between the two CERs measures abbreviation fidelity.
LATIN_FOLD = {
    "ſ": "s", "v": "u", "j": "i", "æ": "ae", "œ": "oe",
    "&": "et", "⁊": "et", "ﬂ": "fl", "ﬁ": "fi", "ﬀ": "ff",
    "ı": "i", "ȷ": "i",                       # dotless i / j
    "ꝛ": "r", "ꞃ": "r",                       # r rotunda
    "ł": "l", "ꝉ": "l",                       # l with stroke
    "ꝑ": "p", "ꝓ": "p", "ꝗ": "q", "ꝙ": "q",   # per/pro/qui/quod brevigraphs
    "ꝺ": "d", "ẟ": "d", "ꞇ": "t", "ᵹ": "g", "ꝥ": "th",
    "đ": "d", "ħ": "h", "ŧ": "t", "ꝯ": "con",
}


def strip_combining(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if not unicodedata.combining(c))


def hebrew_stream(text, fold_finals=True):
    t = strip_combining(text)
    out = []
    for c in t:
        if c not in HEBREW_LETTERS:
            continue
        out.append(FINALS.get(c, c) if fold_finals else c)
    return "".join(out)


def latin_stream(text, fold=True):
    t = text.lower()
    if fold:
        t = strip_combining(t)          # drops the titulus / macron
    out = []
    for c in t:
        if fold and c in LATIN_FOLD:
            out.append(LATIN_FOLD[c])
            continue
        if c.isalpha() or (not fold and unicodedata.combining(c)):
            out.append(c)
    return "".join(out)


PROFILES = {
    "hebrew": {
        "stream": hebrew_stream,
        "loose_kw": {"fold_finals": True},
        "strict_kw": {"fold_finals": False},
        "strict_label": "CER_finals_strict",
        "script_re": re.compile(r"[֐-׿]"),
        "rtl": True,
    },
    "latin": {
        "stream": latin_stream,
        "loose_kw": {"fold": True},
        "strict_kw": {"fold": False},
        "strict_label": "CER_abbrev_strict",
        "script_re": re.compile(r"[A-Za-zÀ-ÿſ]"),
        "rtl": False,
    },
}

# ---------------------------------------------------------------- edit distance


def levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# ------------------------------------------------------------- layer extraction

NORM_HEAD = re.compile(
    r"^\s*(#{1,6}\s*)?\**\s*([0-9IVXLCDM]+\.?\s*)?(normali[sz]ed|normali[sz]ed edition|edition)\b",
    re.I | re.M)
NOTES_HEAD = re.compile(
    r"^\s*(#{1,6}\s*)?\**\s*(scholarly notes|notes\b|commentary|apparatus)",
    re.I | re.M)
DIP_HEAD = re.compile(
    r"^\s*(#{1,6}\s*)?\**\s*([0-9IVXLCDM]+\.?\s*)?diplomatic\b.*$", re.I | re.M)


def normalized_layer(output):
    if not output:
        return ""
    m = NORM_HEAD.search(output)
    if not m:
        return ""
    tail = output[m.end():]
    n = NOTES_HEAD.search(tail)
    return tail[:n.start()] if n else tail


def diplomatic_layer(output, script_re, min_chars=3):
    """Everything from the diplomatic heading up to the normalized edition.

    Models label their sections; where they do not, the fallback is the text
    before the first normalized/notes heading, filtered to runs in the target
    script so English prose and headings drop out.

    min_chars is the number of script characters a line must carry to survive
    that filter. Three is right for a full page and wrong for 4Q530's small
    fragments, where a whole manuscript line can be two surviving letters:
    the caller lowers it for short ground truths so that a correct sparse
    transcription is not discarded as prose.
    """
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
    keep = [ln for ln in head.splitlines()
            if len(script_re.findall(ln)) >= min_chars]
    return "\n".join(keep)


# Phrases by which a model reports that it cannot read the image. Constraint 9
# of the Aramaic prompt explicitly invites this answer, and on a fragment whose
# colour exposure shows no ink it is the right one.
DECLINED_RE = re.compile(
    r"no (ancient |legible |identifiable )?(text|script|ink|letters?)"
    r"|cannot (be )?(read|identif|transcrib|discern)"
    r"|not legible|illegible|no legible|unable to (read|identify|transcribe)"
    r"|no identifiable letter", re.I)


# A transcription made entirely of lacuna brackets and trace marks.
TRACE_RE = re.compile(r"(\[\s*\.{2,}\s*\]|·|◌|°)\s*(\[|·|◌|°|$)", re.M)


# Models were asked to mark rubricated initials as [rubric: X]. The letter
# inside is real text on the page; the label is not, and left alone it both
# injects the word "rubric" into the character stream and inflates the lacuna
# count. Unwrap it before anything else looks at the output.
RUBRIC_RE = re.compile(r"\[\s*rubric[^\]:]*[:\-]?\s*([^\]]*?)\s*\]", re.I)


def unwrap_rubrics(text):
    return RUBRIC_RE.sub(lambda m: m.group(1), text or "")


# ------------------------------------------------------- restoration handling

# [ ... ] and ( ... ) both mark material that is NOT on the parchment:
# square brackets a lacuna with the editor's restoration inside it, round
# brackets an estimated count of missing letters (DJD 31 p. xviii).
BRACKET = re.compile(r"\[[^\[\]]*\]|\([^()]*\)")


def extant_only(text):
    """Ground truth minus every editorially supplied letter."""
    prev = None
    while prev != text:
        prev, text = text, BRACKET.sub(" ", text)
    return text


def certain_only(text):
    """Ground truth minus both editorially supplied letters and uncertain/dotted traces."""
    nfd = unicodedata.normalize("NFD", text)
    # Remove letter followed/preceded by uncertain marks (combining dot/circle or spacing sigla)
    pat = r"[֐-׿]\s*[\u05af\u0307°•·˚]|[\u05af\u0307°•·˚]\s*[֐-׿]"
    cleaned = re.sub(pat, " ", nfd)
    prev = None
    while prev != cleaned:
        prev, cleaned = cleaned, BRACKET.sub(" ", cleaned)
    return cleaned


def restored_segments(text, stream_fn, kw, min_len=5):
    """Distinctive restored letter-runs, as comparable streams.

    Only runs that do not already occur in the extant text count: a short
    restoration that happens to repeat a sequence the scribe also wrote
    somewhere legible is not evidence that a model imported an edition.
    """
    extant = stream_fn(extant_only(text), **kw)
    segs = []
    for m in BRACKET.finditer(text):
        body = m.group(0)[1:-1]
        body = re.sub(r"--+|\?", " ", body)
        for part in body.split():
            s = stream_fn(part, **kw)
            if len(s) >= min_len and s not in extant:
                segs.append(s)
    return segs


# ------------------------------------------------------------------ measures

LACUNA_RE = re.compile(r"\[[^\]]{0,40}\]")
VACAT_RE = re.compile(r"vacat|〚|〛", re.I)


def repetition_score(stream, n=30):
    if len(stream) < n * 2:
        return 0.0
    grams = [stream[i:i + n] for i in range(len(stream) - n + 1)]
    return round(1 - len(set(grams)) / len(grams), 4)


def words(text, stream_fn, kw):
    toks = []
    for w in re.split(r"\s+", text):
        s = stream_fn(w, **kw)
        if s:
            toks.append(s)
    return toks


def count_uncertainty(text):
    d = unicodedata.normalize("NFD", text)
    return sum(d.count(c) for c in UNCERTAIN_MARKS)


def final_form_profile(text):
    t = strip_combining(text)
    finals = sum(t.count(c) for c in FINALS)
    medials = sum(t.count(v) for v in FINALS.values())
    return {"final_forms": finals, "medial_of_same": medials}


ABBREV_MARKS = re.compile(r"[̄̅̃]|ſ|q[:;]|⁊|&|̄")


def abbrev_profile(text):
    d = unicodedata.normalize("NFD", text)
    return {
        "titulus_macron": len(re.findall(r"[̄̅̃]", d)),
        "long_s": text.count("ſ"),
        "que_enclitic": len(re.findall(r"q[:;]", text)),
        "tironian_or_amp": text.count("⁊") + text.count("&"),
    }


# ------------------------------------------------------------------- scoring

def score(entry, prof):
    stream, loose, strict = prof["stream"], prof["loose_kw"], prof["strict_kw"]
    res = entry["result"]
    gt_raw = entry.get("ground_truth") or ""
    out_raw = res.get("output") or ""
    raw = res.get("raw_response") or {}
    usage = raw.get("usage") or {}
    choice = (raw.get("choices") or [{}])[0]
    cost = res.get("cost")
    if cost is None:
        cost = usage.get("cost")
    prompt_tokens = res.get("prompt_tokens") or usage.get("prompt_tokens") or 0
    completion_tokens = res.get("completion_tokens") or usage.get("completion_tokens") or 0
    total_tokens = res.get("total_tokens") or usage.get("total_tokens") or (prompt_tokens + completion_tokens)
    elapsed = res.get("elapsed_seconds")

    row = {
        "page_id": entry.get("page_id"),
        "model": res["model"],
        "reported_status": res.get("status"),
        "finish_reason": choice.get("finish_reason") or res.get("finish_reason"),
        "error": res.get("error"),
        "elapsed_seconds": elapsed,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost": cost,
        "output_chars": len(out_raw),
    }

    # The vendor's safety filter stopped the response. Whatever text reached
    # the client under a content_filter cut is not a transcription the model
    # stands behind, so it must not be scored as one. Motivating case:
    # Claude Opus 5 on the Aramaic corpus returned finish_reason
    # content_filter on all 12 units while well-formed abstention prose still
    # arrived, and three of those responses were being scored as
    # transcriptions. Blocked is reported as blocked, with the bill.
    if row["finish_reason"] == "content_filter" or res.get("status") == "BLOCKED":
        row.update({"scored": False,
                    "failure_mode": "content filter blocked the response",
                    "content_blocked": True})
        return row

    # A fragment whose whole ground truth is a few letters cannot be held to
    # the full-page line filter.
    min_chars = 1 if len(prof["script_re"].findall(gt_raw)) < 60 else 3
    dip = unwrap_rubrics(diplomatic_layer(out_raw, prof["script_re"], min_chars))
    if not dip.strip():
        # Distinguish three things the old code called one thing: an
        # infrastructure failure, a model that answered but wrote no script,
        # and a model that examined the image and reported it illegible. The
        # third is a correct scholarly outcome on a blank or effaced
        # fragment, and counting it as a failure inverts the finding.
        script_in_output = len(prof["script_re"].findall(out_raw))
        # The unfiltered diplomatic section, to tell a model that abstained
        # inside a transcription from one that never produced a section.
        section = diplomatic_layer(out_raw, prof["script_re"], min_chars=0)
        traces_only = bool(TRACE_RE.search(section))
        if row["reported_status"] not in ("SUCCESS", "TRUNCATED", None):
            mode = f"no output ({row['reported_status']})"
        elif traces_only:
            # A transcription consisting entirely of [...] and trace dots:
            # the model looked, found ink it could not resolve, and said so
            # in the transcription itself rather than inventing letters.
            mode = ("abstained: transcribed as lacunae and unidentified "
                    "traces, no letter claimed")
            row["abstained"] = True
        elif DECLINED_RE.search(out_raw or ""):
            mode = "declined: model reported the image illegible"
            row["declined_as_illegible"] = True
        elif script_in_output == 0:
            mode = "answered, but wrote no text in the target script"
        else:
            mode = ("script present but outside the diplomatic section "
                    "(check layer extraction)")
        row.update({"scored": False, "failure_mode": mode})
        return row

    gt_full = stream(gt_raw, **loose)
    hy = stream(dip, **loose)
    gt_ext = stream(extant_only(gt_raw), **loose)
    gt_cert = stream(certain_only(gt_raw), **loose)
    gt_strict = stream(gt_raw, **strict)
    hy_strict = stream(dip, **strict)

    gt_w = words(gt_raw, stream, loose)
    hy_w = words(dip, stream, loose)

    segs = restored_segments(gt_raw, stream, loose)
    imported = [s for s in segs if s in hy]

    row.update({
        "scored": True,
        "gt_chars": len(gt_full),
        "gt_chars_extant": len(gt_ext),
        "gt_chars_certain": len(gt_cert),
        "hyp_chars": len(hy),
        "length_ratio": round(len(hy) / len(gt_full), 3) if gt_full else None,
        "CER": round(levenshtein(gt_full, hy) / len(gt_full), 4) if gt_full else None,
        "CER_extant": (round(levenshtein(gt_ext, hy) / len(gt_ext), 4)
                       if gt_ext else None),
        "CER_certain": (round(levenshtein(gt_cert, hy) / len(gt_cert), 4)
                        if gt_cert else None),
        prof["strict_label"]: (round(levenshtein(gt_strict, hy_strict) /
                                     len(gt_strict), 4) if gt_strict else None),
        "WER": (round(levenshtein(gt_w, hy_w) / len(gt_w), 4)
                if gt_w and hy_w else None),
        "gt_words": len(gt_w),
        "hyp_words": len(hy_w),
        "supplied_normalized_edition": bool(normalized_layer(out_raw).strip()),
        "repetition_30gram": repetition_score(hy),
        "restored_segments": len(segs),
        "restored_segments_reproduced": len(imported),
        "restoration_import_rate": (round(len(imported) / len(segs), 4)
                                    if segs else None),
        "gt_lacuna_markers": len(LACUNA_RE.findall(gt_raw)),
        "hyp_lacuna_markers": len(LACUNA_RE.findall(unwrap_rubrics(out_raw))),
        "gt_vacat": len(VACAT_RE.findall(gt_raw)),
        "hyp_vacat": len(VACAT_RE.findall(out_raw)),
    })
    if prof["rtl"]:
        row["gt_uncertainty_marks"] = count_uncertainty(gt_raw)
        row["hyp_uncertainty_marks"] = count_uncertainty(dip)
        row["gt_finals"] = final_form_profile(gt_raw)
        row["hyp_finals"] = final_form_profile(dip)
    else:
        row["gt_abbrev"] = abbrev_profile(gt_raw)
        row["hyp_abbrev"] = abbrev_profile(dip)

    # Incomplete-capture rule (HANDOFF item 7 / findings_latin_isidore §6):
    # a response carrying under ~80% of a LACUNA-FREE ground truth is a
    # truncated or partial capture, not a transcription, and must not be
    # scored as one — five Latin models swung by >0.6 CER on this alone
    # between two runs of the same page. Deliberately scoped to lacuna-free
    # ground truths: on 4Q530 the ground truth is mostly editorial brackets
    # and a short honest transcription of the extant letters is precisely
    # what a disciplined model should emit, so the rule would misfire there.
    # Measurements stay on the row for the record; only `scored` flips.
    lr = row.get("length_ratio")
    if (gt_full and not LACUNA_RE.search(gt_raw) and lr is not None
            and lr < 0.8):
        row.update({
            "scored": False,
            "failure_mode": (f"incomplete capture: length_ratio {lr} < 0.80 "
                             f"on a lacuna-free page (rule: incomplete "
                             f"captures are not transcriptions)"),
            "incomplete_capture": True,
        })
    return row


def aggregate(rows):
    """Per-model totals, weighted by ground-truth characters."""
    by = defaultdict(list)
    for r in rows:
        by[r["model"]].append(r)
    out = []
    for model, rs in by.items():
        ok = [r for r in rs if r.get("scored")]
        tot = sum(r["gt_chars"] for r in ok) or 0
        ext = sum(r["gt_chars_extant"] for r in ok) or 0
        cert = sum(r["gt_chars_certain"] for r in ok) or 0
        wtot = sum(r["gt_words"] for r in ok) or 0
        segs = sum(r["restored_segments"] for r in ok)
        imp = sum(r["restored_segments_reproduced"] for r in ok)

        def wavg(key, weight):
            num = sum((r[key] or 0) * r[weight] for r in ok if r.get(key) is not None)
            den = sum(r[weight] for r in ok if r.get(key) is not None)
            return round(num / den, 4) if den else None

        costs = [r["cost"] for r in rs if r.get("cost") is not None]
        tot_cost = sum(costs) if costs else None
        times = [r["elapsed_seconds"] for r in rs if r.get("elapsed_seconds") is not None]
        tot_time = sum(times) if times else None
        avg_time = (tot_time / len(times)) if times else None
        tot_prompt_toks = sum(r.get("prompt_tokens") or 0 for r in rs)
        tot_comp_toks = sum(r.get("completion_tokens") or 0 for r in rs)

        out.append({
            "model": model,
            "units_scored": len(ok),
            "units_failed": len(rs) - len(ok),
            "units_content_blocked": sum(1 for r in rs if r.get("content_blocked")),
            "units_incomplete_capture": sum(1 for r in rs if r.get("incomplete_capture")),
            "gt_chars": tot,
            "gt_chars_extant": ext,
            "gt_chars_certain": cert,
            "CER": wavg("CER", "gt_chars"),
            "CER_extant": wavg("CER_extant", "gt_chars_extant") if ext else None,
            "CER_certain": wavg("CER_certain", "gt_chars_certain") if cert else None,
            "WER": wavg("WER", "gt_words") if wtot else None,
            "length_ratio": wavg("length_ratio", "gt_chars"),
            "repetition_30gram": max((r["repetition_30gram"] for r in ok),
                                     default=None),
            "restoration_import_rate": round(imp / segs, 4) if segs else None,
            "lacuna_markers": sum(r["hyp_lacuna_markers"] for r in ok),
            "gt_lacuna_markers": sum(r["gt_lacuna_markers"] for r in ok),
            "total_cost": round(tot_cost, 4) if tot_cost is not None else None,
            "total_time_sec": round(tot_time, 2) if tot_time is not None else None,
            "avg_time_sec": round(avg_time, 2) if avg_time is not None else None,
            "total_prompt_tokens": tot_prompt_toks,
            "total_completion_tokens": tot_comp_toks,
        })
    out.sort(key=lambda r: (r["CER"] is None, r["CER"] if r["CER"] is not None else 9))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--profile", choices=sorted(PROFILES), required=True)
    args = ap.parse_args()

    prof = PROFILES[args.profile]
    data = json.load(open(args.results, encoding="utf-8"))
    rows = [score(e, prof) for e in data]
    agg = aggregate(rows)

    print(f"\n{args.profile} benchmark — {args.results}\n" + "=" * 118)
    print(f"{'model':36s} {'CER':>7s} {'CERext':>7s} {'CERcert':>7s} {'WER':>7s} "
          f"{'len':>6s} {'cost ($)':>9s} {'time (s)':>9s} {'n':>3s}")
    print("-" * 118)
    for r in agg:
        def f(v, w=7):
            return f"{v:{w}.3f}" if isinstance(v, float) else f"{'—':>{w}s}"
        def f_cost(v):
            return f"${v:7.4f}" if isinstance(v, float) else f"{'—':>8s}"
        def f_time(v):
            return f"{v:7.1f}s" if isinstance(v, (float, int)) else f"{'—':>8s}"

        print(f"{r['model']:36s} {f(r['CER'])} {f(r['CER_extant'])} {f(r['CER_certain'])} "
              f"{f(r['WER'])} {f(r['length_ratio'], 6)} "
              f"{f_cost(r['total_cost']):>9s} "
              f"{f_time(r['total_time_sec']):>9s} {r['units_scored']:3d}")
    fails = [r for r in rows if not r.get("scored")]
    if fails:
        print("\nunscored units:")
        for r in fails:
            print(f"  {r['page_id']:18s} {r['model']:40s} "
                  f"[{r['finish_reason']}] {r.get('error') or r.get('failure_mode')}")

    out = args.results.replace(".json", "_scored.json")
    json.dump({"per_unit": rows, "per_model": agg},
              open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nDetail written to {out}")


if __name__ == "__main__":
    main()
