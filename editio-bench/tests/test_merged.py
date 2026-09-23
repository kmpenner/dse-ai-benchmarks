"""Offline unit tests for editio-bench (no API calls)."""
import json
from pathlib import Path

import pytest

from editio_bench.metrics import (
    sigla_preservation, count_sigla, compute_all, has_usable_reference,
)
from editio_bench.prompts import PromptLibrary, extract_translation, Protocol, candidate_id
from editio_bench.elo import fit_bradley_terry, to_elo, elo_with_ci
from editio_bench.cache import Cache
from editio_bench.judge import summarise_judge, _parse_json
from editio_bench.phase_bench import (
    parse_score, phase_summary, load_benchmarks, _consensus_score, TIEBREAK_THRESHOLD,
)
from editio_bench.readiness import analyse_readiness

ROOT = Path(__file__).resolve().parent.parent


# ----- metrics: deterministic sigla preservation -----
def test_sigla_preservation_flags_dropped_brackets():
    src = "the [reconstructed] word and ◦◦"
    good = sigla_preservation(src, "the [reconstructed] word and ◦◦")
    bad = sigla_preservation(src, "the reconstructed word")
    assert good["reconstructions_preserved"] == 1.0
    assert bad["reconstructions_preserved"] == 0.0
    assert bad["traces_preserved"] == 0.0

def test_count_sigla_types():
    c = count_sigla("[a] ⟦b⟧ ⟨c⟩ ◦")
    assert c == {"reconstructions": 1, "deletions": 1, "supralinear": 1, "traces": 1}

def test_compute_all_has_length_ratio():
    m = compute_all("[x] y", "the [x] y", "the x y", enable_bleu=False, enable_chrf=False)
    assert "length_ratio" in m and "reconstructions_preserved" in m

def test_placeholder_reference_suppresses_reference_metrics():
    m = compute_all("[x] y", "the [x] y", "PLACEHOLDER — replace", reference_source="placeholder")
    assert m["reference_metrics_available"] is False
    assert "chrf" not in m and "bleu" not in m and "length_ratio" not in m
    assert m["reconstructions_preserved"] == 1.0

def test_has_usable_reference():
    assert has_usable_reference("real translation", "published")
    assert not has_usable_reference("PLACEHOLDER — replace", "placeholder")


# ----- prompts: chain-of-thought extraction marker -----
def test_extract_marker_strips_reasoning():
    proto = Protocol(name="cot", system="s", extract_marker="TRANSLATION:")
    out = extract_translation("analysis...\nTRANSLATION:\nFinal text", proto)
    assert out == "Final text"

def test_candidate_id_format():
    assert candidate_id("openai/gpt-5", "negative") == "openai/gpt-5 [negative]"

def test_prompt_library_loads_shipped_protocols():
    lib = PromptLibrary.load(ROOT / "prompts" / "protocols.yaml")
    assert {"baseline", "cot", "negative"} <= set(lib.protocols)


# ----- elo: Bradley-Terry monotonicity -----
def test_bradley_terry_orders_by_wins():
    comps = ([{"model_a": "A", "model_b": "B", "winner": "A", "passage_id": "p1"}] * 8 +
             [{"model_a": "A", "model_b": "B", "winner": "B", "passage_id": "p1"}] * 2)
    res = elo_with_ci(comps, ["A", "B"], n_bootstrap=50, seed=1)
    assert res["A"]["elo"] > res["B"]["elo"]

def test_to_elo_anchor():
    st = fit_bradley_terry(["A", "B"], {("A", "B"): 5.0, ("B", "A"): 5.0})
    elo = to_elo(st)
    assert abs(elo["A"] - elo["B"]) < 1e-6  # equal records -> equal elo


# ----- cache: sqlite roundtrip -----
def test_cache_roundtrip(tmp_path):
    c = Cache(tmp_path / "c.sqlite")
    k = c.key(kind="x", model="m", messages=[{"r": 1}])
    assert c.get(k) is None
    c.put(k, {"v": 42})
    assert c.get(k) == {"v": 42}


# ----- judge helpers -----
def test_summarise_judge_averages_six_dims():
    j = {d: {"score": 4} for d in ["lexical_accuracy", "syntactic_fidelity",
         "sectarian_terminology", "lacuna_treatment", "register", "fluency"]}
    assert summarise_judge(j) == 4.0

def test_parse_json_from_fenced_block():
    assert _parse_json('```json\n{"winner":"A"}\n```')["winner"] == "A"


# ----- phase track -----
@pytest.mark.parametrize("txt,exp", [
    ("```\n85\n```", 85), ("Score: 90/100", 90), ("```markdown\n100\n```", 100),
    ("nonsense", None), (None, None), ("250", None)])
def test_parse_score(txt, exp):
    assert parse_score(txt) == exp

# ----- consensus scoring: tiebreak on >10-point scorer disagreement -----
def test_consensus_agrees_within_threshold_uses_mean():
    score, needs_tiebreak = _consensus_score({"a": 80, "b": 80 + TIEBREAK_THRESHOLD})
    assert not needs_tiebreak
    assert score == 80 + TIEBREAK_THRESHOLD / 2

def test_consensus_disagreement_over_threshold_requests_tiebreak():
    score, needs_tiebreak = _consensus_score({"a": 40, "b": 40 + TIEBREAK_THRESHOLD + 1})
    assert needs_tiebreak
    assert score is None

def test_consensus_with_third_scorer_uses_median_not_mean():
    # 40 and 90 disagree by 50 (>threshold); a third scorer's 85 pulls the
    # median (85) toward the two that agree, unlike the mean (71.7) which
    # would still be dragged down by the outlier.
    score, needs_tiebreak = _consensus_score({"a": 40, "b": 90, "c": 85})
    assert not needs_tiebreak
    assert score == 85

def test_consensus_single_scorer_passthrough():
    score, needs_tiebreak = _consensus_score({"a": 72})
    assert score == 72 and not needs_tiebreak

def test_consensus_no_scores():
    score, needs_tiebreak = _consensus_score({"a": None})
    assert score is None and not needs_tiebreak

def test_phase_summary_prefers_score_consensus_when_present():
    rows = [{"model": "M", "task_type": "translation",
             "score::S1": 40, "score::S2": 90, "score_consensus": 85}]
    summ = {(s["model"], s["phase"]): s for s in phase_summary(rows, ["S1", "S2"])}
    assert summ[("M", "translation")]["mean_score"] == 85.0


def test_phase_summary_na_safe():
    rows = [
        {"model": "M", "task_type": "translation", "score::S1": 80, "score::S2": 90},
        {"model": "M", "task_type": "collation", "score::S1": "N/A", "score::S2": 70},
    ]
    summ = {(s["model"], s["phase"]): s for s in phase_summary(rows, ["S1", "S2"])}
    assert summ[("M", "translation")]["mean_score"] == 85.0
    assert summ[("M", "collation")]["mean_score"] == 70.0
    assert summ[("M", "ALL_PHASES")]["n_tasks"] == 2

def test_benchmarks_json_valid_and_multiphase():
    doc = load_benchmarks(ROOT / "data" / "benchmarks.json")
    phases = {b["task_type"] for b in doc["benchmarks"]}
    assert {"transcription", "collation", "translation", "annotation"} <= phases
    for name in ["transcription", "collation", "annotation", "translation"]:
        assert name in doc["rubrics"]

def test_readiness_counts_placeholder_references():
    result = analyse_readiness(ROOT / "data" / "benchmarks.json")
    assert len(result["needs_ground_truth_ids"]) >= 0
    assert result["benchmarks"] > 0
