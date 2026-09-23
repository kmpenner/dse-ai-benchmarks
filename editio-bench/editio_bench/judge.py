"""LLM-as-judge: (a) absolute six-dimension rubric, (b) anonymized pairwise A/B.

Pairwise judging avoids rubric calibration drift; each pair is judged in BOTH
orders to control position bias. Ties are allowed.
"""
from __future__ import annotations

import json
import re
from typing import Optional

import httpx

from .translate import OpenRouterClient, extract_usage


# --------------------------- absolute rubric --------------------------------

JUDGE_SYSTEM = """You are a senior philologist of the Dead Sea Scrolls, fluent in Qumran Hebrew, Qumran Aramaic, the relevant ancient Near Eastern context, and the target language. You are evaluating a candidate translation of a Qumran passage against a scholarly reference translation.

You must be rigorous and concise. Score each dimension on an integer 1–5 scale (1 = unacceptable, 3 = adequate, 5 = excellent and publishable). Cite specific words/phrases when justifying scores.

Return ONLY a single JSON object — no prose before or after — with this exact schema:

{
  "lexical_accuracy": {"score": 1-5, "rationale": "..."},
  "syntactic_fidelity": {"score": 1-5, "rationale": "..."},
  "sectarian_terminology": {"score": 1-5, "rationale": "..."},
  "lacuna_treatment": {"score": 1-5, "rationale": "..."},
  "register": {"score": 1-5, "rationale": "..."},
  "fluency": {"score": 1-5, "rationale": "..."},
  "hallucinations": {"present": true|false, "examples": ["..."], "severity": "none|minor|major"},
  "overall": {"score": 1-5, "summary": "..."}
}

Scoring guidance:
- lexical_accuracy: correctness of word-level choices, including rare/sectarian vocabulary (e.g. יחד, פשר, מבקר, רזי נהיה, בני אור).
- syntactic_fidelity: clause structure, waw-consecutive handling, construct chains, verbal aspect.
- sectarian_terminology: correct and consistent rendering of sect-specific technical terms.
- lacuna_treatment: did the candidate (a) preserve editorial brackets [ ], ⟦ ⟧, ⟨ ⟩, ◦, and (b) refrain from inventing content for damaged text? Silent smoothing scores 1–2 regardless of fluency.
- register: appropriateness to genre (legal, hymnic, pesher, apocalyptic, narrative).
- fluency: target-language naturalness.
- hallucinations: content NOT derivable from the source, including filled lacunae. Give concrete examples.
"""

JUDGE_USER_TMPL = """Source ({source_language}, {genre}, {siglum}):
{source}

Reference translation ({target_language}):
{reference}

Candidate translation ({target_language}):
{candidate}

Evaluate the candidate. Return only the JSON object."""


# --------------------------- pairwise ----------------------------------------

PAIRWISE_SYSTEM = """You are a senior philologist of the Dead Sea Scrolls, expert in Qumran Hebrew and Qumran Aramaic. You will compare two anonymous candidate translations (A and B) of the same Qumran passage.

Judge on: lexical accuracy (especially sectarian/technical vocabulary), syntactic fidelity, treatment of lacunae and editorial sigla (a translation that silently fills gaps or drops brackets is inferior even if more fluent), genre-appropriate register, and target-language quality. A scholarly reference translation may be provided as an aid; the candidates need not match it verbatim to be good.

Return ONLY a single JSON object:
{"winner": "A"|"B"|"tie", "confidence": "low"|"medium"|"high", "rationale": "one or two sentences citing specific evidence"}"""

PAIRWISE_USER_TMPL = """Source ({source_language}, {genre}, {siglum}):
{source}

Reference translation ({target_language}):
{reference}

Candidate A:
{cand_a}

Candidate B:
{cand_b}

Which translation is better? Return only the JSON object."""


JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = JSON_BLOCK.search(text)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError as e:
                return {"error": f"could not parse judge JSON: {e}", "raw": text[:500]}
        return {"error": "no JSON object in judge output", "raw": text[:500]}


async def _judge_call(
    client: OpenRouterClient,
    http: httpx.AsyncClient,
    judge_model: str,
    system: str,
    user: str,
    max_tokens: int,
    cache=None,
) -> tuple[dict, float]:
    """Returns (parsed_json, cost_usd)."""
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]

    cache_key = None
    if cache is not None:
        cache_key = cache.key(kind="judge", model=judge_model, messages=msgs)
        hit = cache.get(cache_key)
        if hit is not None:
            return hit["parsed"], 0.0

    async def call(extra):
        resp = await client.chat(
            http, judge_model, msgs, temperature=0.0,
            max_tokens=max_tokens, extra=extra,
        )
        text = resp["choices"][0]["message"]["content"] or ""
        _, _, _, cost = extract_usage(resp)
        return _parse_json(text), cost

    try:
        parsed, cost = await call({"response_format": {"type": "json_object"}})
    except Exception:
        try:
            parsed, cost = await call(None)
        except Exception as e:
            return {"error": f"judge failed: {e}"}, 0.0

    if cache is not None and "error" not in parsed:
        cache.put(cache_key, {"parsed": parsed})
    return parsed, cost


async def judge_one(
    client: OpenRouterClient,
    http: httpx.AsyncClient,
    judge_model: str,
    passage: dict,
    candidate: str,
    target_language: str,
    max_tokens: int = 1500,
    cache=None,
) -> tuple[dict, float]:
    user = JUDGE_USER_TMPL.format(
        source_language=passage.get("language", "QH"),
        genre=passage.get("genre", "unknown"),
        siglum=passage.get("siglum", passage["id"]),
        source=passage["source"],
        reference=passage.get("reference", "(no reference provided)"),
        candidate=candidate,
        target_language=target_language,
    )
    return await _judge_call(
        client, http, judge_model, JUDGE_SYSTEM, user, max_tokens, cache
    )


async def judge_pair(
    client: OpenRouterClient,
    http: httpx.AsyncClient,
    judge_model: str,
    passage: dict,
    cand_a: str,
    cand_b: str,
    target_language: str,
    max_tokens: int = 600,
    cache=None,
) -> tuple[dict, float]:
    """One directed comparison: A shown first, B second."""
    user = PAIRWISE_USER_TMPL.format(
        source_language=passage.get("language", "QH"),
        genre=passage.get("genre", "unknown"),
        siglum=passage.get("siglum", passage["id"]),
        source=passage["source"],
        reference=passage.get("reference", "(no reference provided)"),
        cand_a=cand_a,
        cand_b=cand_b,
        target_language=target_language,
    )
    return await _judge_call(
        client, http, judge_model, PAIRWISE_SYSTEM, user, max_tokens, cache
    )


def summarise_judge(j: dict) -> Optional[float]:
    if "error" in j:
        return None
    keys = [
        "lexical_accuracy", "syntactic_fidelity", "sectarian_terminology",
        "lacuna_treatment", "register", "fluency",
    ]
    try:
        scores = [float(j[k]["score"]) for k in keys if k in j]
        return round(sum(scores) / len(scores), 2) if scores else None
    except (KeyError, TypeError, ValueError):
        return None
