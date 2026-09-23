"""Async OpenRouter client + protocol-aware translation.

A candidate is (model × protocol). External baselines (deterministic tools,
published translations) are injected as pseudo-candidates without API calls.
"""
from __future__ import annotations

import os
import time
import asyncio
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import httpx

from .prompts import Protocol, PromptLibrary, extract_translation, candidate_id

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


@dataclass
class TranslationResult:
    model: str
    protocol: str
    candidate: str
    passage_id: str
    translation: str
    raw_output: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_s: float
    cached: bool = False
    external: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class OpenRouterClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        url: str = OPENROUTER_URL,
        timeout: float = 600.0,
        max_retries: int = 4,
        app_url: str = "https://github.com/local/editio-bench",
        app_name: str = "editio-bench",
    ):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY not set. export OPENROUTER_API_KEY=sk-or-v1-..."
            )
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": app_url,
            "X-Title": app_name,
        }

    async def chat(
        self,
        client: httpx.AsyncClient,
        model: str,
        messages: list[dict],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        extra: Optional[dict] = None,
    ) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "usage": {"include": True},
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if extra:
            payload.update(extra)
        last_err: Optional[Exception] = None
        import random
        for attempt in range(self.max_retries):
            try:
                r = await client.post(
                    self.url, headers=self._headers, json=payload, timeout=self.timeout
                )
                # Read the body before deciding how to react to the status --
                # OpenRouter puts the real reason in a JSON "error" object on
                # 4xx responses (and occasionally alongside a 200), and that
                # text is what callers need to tell "this request is invalid
                # for this model" apart from "the model's answer was bad".
                try:
                    data = r.json()
                except ValueError:
                    data = None
                if r.status_code == 429 or 500 <= r.status_code < 600:
                    retry_after = r.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after and retry_after.isdigit() else min(4 * (2**attempt) + random.uniform(0.5, 2.0), 60.0)
                    body_msg = (data or {}).get("error", {}).get("message") if isinstance(data, dict) else None
                    last_err = RuntimeError(f"retryable {r.status_code}: {body_msg or r.text[:200]}")
                    await asyncio.sleep(sleep_time)
                    continue
                if isinstance(data, dict) and data.get("error"):
                    err = data["error"]
                    err_code = err.get("code") if isinstance(err, dict) else None
                    err_msg = err.get("message", "") if isinstance(err, dict) else str(err)
                    err_msg_lower = err_msg.lower()
                    is_retryable = (
                        err_code in (408, 429, 500, 502, 503, 504)
                        or any(k in err_msg_lower for k in [
                            "rate-limit", "rate limit", "quota", "too many requests",
                            "timed out", "timeout", "temporarily unavailable", "overloaded",
                            "upstream error", "bad gateway", "service unavailable",
                            "internal server error", "provider error"
                        ])
                    )
                    if is_retryable:
                        sleep_time = min(4 * (2**attempt) + random.uniform(0.5, 2.0), 60.0)
                        last_err = RuntimeError(f"retryable provider error ({err_code}): {err_msg}")
                        await asyncio.sleep(sleep_time)
                        continue
                    # A deterministic non-transient rejection of this request (e.g. invalid auth or model)
                    raise RuntimeError(f"provider error ({err_code}): {err_msg}")
                r.raise_for_status()
                return data
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                last_err = e
                # Exponential backoff with jitter
                sleep_sec = min(3.0 * (1.8**attempt) + random.uniform(0.5, 2.0), 45.0)
                await asyncio.sleep(sleep_sec)
        raise RuntimeError(f"OpenRouter call failed after {self.max_retries} retries: {last_err}")


def extract_usage(resp: dict) -> tuple[int, int, int, float]:
    u = resp.get("usage", {}) or {}
    return (
        u.get("prompt_tokens", 0),
        u.get("completion_tokens", 0),
        u.get("total_tokens", 0),
        float(u.get("cost", 0.0) or 0.0),
    )


def build_translation_messages(
    passage: dict,
    target_language: str,
    protocol: Protocol,
    lib: PromptLibrary,
) -> list[dict]:
    lang_code = passage.get("language", "QH")
    user = (
        f"Source siglum: {passage.get('siglum', passage['id'])}\n"
        f"Source language: {lib.language_profile(lang_code)}\n"
        f"Genre: {passage.get('genre', 'unknown')}\n"
        f"Target language: {target_language}\n\n"
        f"{lib.sigla_note}\n\n"
        f"Source text:\n\n{passage['source']}\n\n"
        f"Translate into {target_language}. Do not include the source text or "
        f"transliteration. Mark reconstructed text with [brackets] in the "
        f"translation."
    )
    if protocol.user_suffix:
        user += "\n\n" + protocol.user_suffix
    return [
        {"role": "system", "content": protocol.system},
        {"role": "user", "content": user},
    ]


async def translate_one(
    client: OpenRouterClient,
    http: httpx.AsyncClient,
    model: str,
    protocol: Protocol,
    passage: dict,
    target_language: str,
    lib: PromptLibrary,
    temperature: float,
    max_tokens: int,
    cache=None,
) -> TranslationResult:
    cand = candidate_id(model, protocol.name)
    msgs = build_translation_messages(passage, target_language, protocol, lib)

    cache_key = None
    if cache is not None:
        cache_key = cache.key(
            kind="translation", model=model, messages=msgs,
            temperature=temperature, max_tokens=max_tokens,
        )
        hit = cache.get(cache_key)
        if hit is not None:
            return TranslationResult(
                model=model, protocol=protocol.name, candidate=cand,
                passage_id=passage["id"],
                translation=hit["translation"],
                raw_output=hit.get("raw_output", hit["translation"]),
                prompt_tokens=hit.get("prompt_tokens", 0),
                completion_tokens=hit.get("completion_tokens", 0),
                total_tokens=hit.get("total_tokens", 0),
                cost_usd=hit.get("cost_usd", 0.0),
                latency_s=0.0, cached=True,
            )

    t0 = time.time()
    try:
        resp = await client.chat(
            http, model, msgs, temperature=temperature, max_tokens=max_tokens
        )
        elapsed = time.time() - t0
        raw = (resp["choices"][0]["message"]["content"] or "").strip()
        text = extract_translation(raw, protocol)
        pt, ct, tt, cost = extract_usage(resp)
        if cache is not None and text:
            cache.put(cache_key, {
                "translation": text, "raw_output": raw,
                "prompt_tokens": pt, "completion_tokens": ct,
                "total_tokens": tt, "cost_usd": cost,
            })
        return TranslationResult(
            model=model, protocol=protocol.name, candidate=cand,
            passage_id=passage["id"], translation=text, raw_output=raw,
            prompt_tokens=pt, completion_tokens=ct, total_tokens=tt,
            cost_usd=cost, latency_s=round(elapsed, 3),
        )
    except Exception as e:
        return TranslationResult(
            model=model, protocol=protocol.name, candidate=cand,
            passage_id=passage["id"], translation="", raw_output="",
            prompt_tokens=0, completion_tokens=0, total_tokens=0,
            cost_usd=0.0, latency_s=round(time.time() - t0, 3), error=str(e),
        )


def load_external_baselines(specs: list[dict]) -> list[TranslationResult]:
    """specs: [{name: 'deterministic-v1', path: 'baselines/det.jsonl'}, ...]
    Each JSONL line: {"passage_id": ..., "translation": ...}
    Injected as candidates named 'baseline:NAME' — they enter scoring and the
    pairwise tournament but cost nothing and are never re-generated.
    """
    out = []
    for spec in specs or []:
        name = spec["name"]
        cand = f"baseline:{name}"
        p = Path(spec["path"])
        if not p.exists():
            raise FileNotFoundError(f"external baseline file not found: {p}")
        with p.open("r", encoding="utf-8") as f:
            for ln in f:
                if not ln.strip():
                    continue
                row = json.loads(ln)
                out.append(TranslationResult(
                    model=cand, protocol="external", candidate=cand,
                    passage_id=row["passage_id"],
                    translation=row["translation"],
                    raw_output=row["translation"],
                    prompt_tokens=0, completion_tokens=0, total_tokens=0,
                    cost_usd=0.0, latency_s=0.0, external=True,
                ))
    return out
