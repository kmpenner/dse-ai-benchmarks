"""Automated metrics: chrF++, BLEU, optional BERTScore, length ratio,
and deterministic editorial-sigla preservation."""
from __future__ import annotations

import re
from typing import Optional

import sacrebleu

RECON_BRACKETS = re.compile(r"\[([^\[\]]*)\]")
DELETED = re.compile(r"⟦([^⟦⟧]*)⟧")
SUPRALINEAR = re.compile(r"⟨([^⟨⟩]*)⟩")
TRACE_DOTS = re.compile(r"◦+")


def chrf_score(hypothesis: str, reference: str) -> float:
    if not hypothesis.strip():
        return 0.0
    return float(sacrebleu.sentence_chrf(hypothesis, [reference], word_order=2).score)


def bleu_score(hypothesis: str, reference: str) -> float:
    if not hypothesis.strip():
        return 0.0
    return float(sacrebleu.sentence_bleu(hypothesis, [reference]).score)


def length_ratio(hypothesis: str, reference: str) -> float:
    if not reference.strip():
        return 0.0
    return round(len(hypothesis) / max(len(reference), 1), 3)


def has_usable_reference(reference: str, reference_source: Optional[str] = None) -> bool:
    """Return False for placeholder references that would make BLEU/chrF noise."""
    ref = (reference or "").strip()
    src = (reference_source or "").strip().lower()
    return bool(ref) and src != "placeholder" and not ref.upper().startswith("PLACEHOLDER")


def bertscore_f1(
    hypotheses: list[str], references: list[str], target_lang_code: str = "en"
) -> Optional[list[float]]:
    try:
        from bert_score import score as _score
    except ImportError:
        return None
    _, _, F = _score(
        hypotheses, references, lang=target_lang_code,
        rescale_with_baseline=False, verbose=False,
    )
    return [round(float(f), 4) for f in F]


def count_sigla(text: str) -> dict:
    return {
        "reconstructions": len(RECON_BRACKETS.findall(text)),
        "deletions": len(DELETED.findall(text)),
        "supralinear": len(SUPRALINEAR.findall(text)),
        "traces": len(TRACE_DOTS.findall(text)),
    }


def sigla_preservation(source: str, hypothesis: str) -> dict:
    src = count_sigla(source)
    hyp = count_sigla(hypothesis)
    out = {}
    for k, v_src in src.items():
        v_hyp = hyp.get(k, 0)
        out[f"src_{k}"] = v_src
        out[f"hyp_{k}"] = v_hyp
        if v_src == 0:
            out[f"{k}_preserved"] = 1.0 if v_hyp == 0 else 0.0
        else:
            out[f"{k}_preserved"] = round(min(v_hyp / v_src, 1.0), 3)
    return out


def compute_all(
    source: str,
    hypothesis: str,
    reference: str,
    reference_source: Optional[str] = None,
    enable_bleu: bool = True,
    enable_chrf: bool = True,
) -> dict:
    out: dict = {}
    usable_reference = has_usable_reference(reference, reference_source)
    out["reference_metrics_available"] = usable_reference
    if enable_chrf and usable_reference:
        out["chrf"] = round(chrf_score(hypothesis, reference), 2)
    if enable_bleu and usable_reference:
        out["bleu"] = round(bleu_score(hypothesis, reference), 2)
    if usable_reference:
        out["length_ratio"] = length_ratio(hypothesis, reference)
    out.update(sigla_preservation(source, hypothesis))
    return out
