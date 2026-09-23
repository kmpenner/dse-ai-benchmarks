"""Four-phase task-typed benchmark track (Penner SSHRC IDG).

The `run`/`pairwise` track scores *translation* candidates. This track covers the
other named workflow phases — transcription, collation, translation, annotation,
encoding — where each task carries its own ground truth and rubric
(`data/benchmarks.json`). A target model answers each task; a scorer panel grades
0-100 against the ground truth using the task's rubric.

It reuses dss-bench's OpenRouterClient (retries/backoff/USD cost) and SQLite Cache
rather than a second HTTP layer, so this track and the translation track share one
OpenRouter path and one cache.

Public entry point: `run_phase_bench(...)`. The CLI exposes it as `dss-bench phase`,
including a single-slug shortcut (`--model <openrouter-slug>`) for dropping any
newly released model straight onto the whole suite.
"""
from __future__ import annotations

import asyncio
import csv
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Optional

import httpx
from rich.console import Console

from .translate import OpenRouterClient, extract_usage
from .cache import Cache

console = Console()

NA = "N/A"

SYSTEM_PHILOLOGIST = (
    "You are a strict philologist working on ancient manuscript texts (Dead Sea "
    "Scrolls, Septuagint, Latin parabiblica). Do NOT normalize spelling variations. "
    "Preserve all scribal anomalies exactly as transcribed. When text is broken "
    "(lacuna), say so explicitly and never present a conjectural restoration as certain."
)

# An answer to an image task that says no image reached the model. The
# rubric's full credit for "epigraphic restraint" is meant for located
# judgments about the manuscript ("no ink visible", "line 3 is cropped"),
# and the text-only judges cannot tell those apart from "you attached
# nothing" -- two of three gave the latter 100 (mimo-v2.6-flash, 2026-09-22),
# although the call's 572 prompt tokens show the image was delivered.
NO_IMAGE_CLAIM_RE = re.compile(
    r"\bno (actual )?(image|photograph|photo|picture|attachment|image file|file)s? "
    r"(has|have|was|were|is|are)? ?(actually )?(been )?(actually )?"
    r"(attached|provided|included|uploaded|shared|received|supplied)"
    r"|\b(image|photograph|photo|picture|attachment|file)s? (has|have|was|were|is|are) not "
    r"(actually )?(been )?(actually )?(attached|provided|included|uploaded|shared|received|supplied)"
    r"|\b(did|do) not (actually )?(attach|provide|include|upload|share|supply) "
    r"(an|the|any) (image|photograph|photo|file)"
    r"|\b(don't|do not|cannot|can't) see (any|an) (image|attachment|photograph|photo|picture)"
    r"|\bno visual (data|input) (to|was|is|has)"
    r"|\bI (cannot|can't|am unable to) (see|view|examine|access|process)"
    r"( or (see|view|examine|access|process))? "
    r"(images|attachments|photographs|visual (content|input))",
    re.I)
NO_IMAGE_STATUS = "declined: claims no image attached"


def claims_no_image(answer: str) -> bool:
    return bool(NO_IMAGE_CLAIM_RE.search(answer or ""))


_FENCE = re.compile(r"```[a-zA-Z]*\s*\n?(.*?)\n?```", re.DOTALL)
_INT = re.compile(r"\b(100|\d{1,2})\b")

# openrouter/fusion is a meta-model: it fans a prompt out to a panel of
# `analysis_models` (run in parallel, each paid at its own rate) and has
# `model` (the judge) synthesize their answers into one response -- the
# fusion wrapper itself is free, so the whole point of hand-picking a panel
# is to combine several cheap models into a candidate that might out-quality
# any one of them for less than a frontier model's cost (Ken, 2026-09-07).
# Panel = the three vision-capable models (transcription tasks need to see
# the manuscript image); judge = deepseek-v4-flash, the only text-only one
# of the four requested, since the judge only ever sees the panel's text.
FUSION_MODEL = "openrouter/fusion"
FUSION_PLUGIN_CONFIG = {
    "plugins": [{
        "id": "fusion",
        "analysis_models": [
            "google/gemini-2.5-flash",
            "google/gemini-3.8-flash",
            "minimax/minimax-m3",
        ],
        "model": "deepseek/deepseek-v4-flash",
    }]
}


def parse_score(text: str) -> Optional[int]:
    """Extract an integer 0-100; prefer a fenced markdown block (checking from
    last to first), strip thinking tags, and fallback to trailing bounded integer.
    Returns None if nothing valid is found."""
    if not text:
        return None

    # Clean escaped newlines/returns that models occasionally mimic from prompt templates
    clean_text = text.replace("\\n", "\n").replace("\\r", "\n")
    # Strip thinking blocks from reasoning models so internal CoT integers aren't parsed as scores
    clean_text = re.sub(r"<think>.*?</think>", "", clean_text, flags=re.DOTALL).strip()
    target_text = clean_text if clean_text else text

    # Check fenced code blocks in reverse order (score is placed at the end)
    fences = re.findall(r"```[a-zA-Z]*\s*(.*?)\s*```", target_text, re.DOTALL)
    for chunk in reversed(fences):
        chunk_str = chunk.strip()
        m_exact = re.fullmatch(r"(100|\d{1,2})", chunk_str)
        if m_exact:
            return int(m_exact.group(1))
        m = re.search(r"\b(100|\d{1,2})\b", chunk_str)
        if m:
            val = int(m.group(1))
            if 0 <= val <= 100:
                return val

    # Fallback: search trailing lines from bottom up
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        for line in reversed(lines[-5:]):
            m = re.fullmatch(r"(100|\d{1,2})", line)
            if m:
                return int(m.group(1))
            m = re.search(r"\b(100|\d{1,2})\b", line)
            if m:
                val = int(m.group(1))
                if 0 <= val <= 100:
                    return val
    return None


def _resolve_image_path(raw: str, benchmarks_path: Path) -> Path:
    """Resolve a benchmark's image_path independently of the launch directory.

    image_path values are stored repo-root-relative (e.g. "resac2026/foo.jpg"),
    but the sanctioned wrapper scripts run with cwd=editio-bench/, so a plain
    CWD-relative lookup silently fails there. Search the plausible anchors and
    hard-fail if a declared image is nowhere to be found: a missing manuscript
    image must abort the task, never quietly degrade it to a text-only prompt
    (which scores 0 and is indistinguishable from genuine model failure).
    """
    candidate = Path(raw)
    if candidate.is_absolute():
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"benchmark image_path not found: {candidate}")

    data_dir = benchmarks_path.resolve().parent      # .../editio-bench/data
    anchors = [
        Path.cwd(),
        data_dir,
        data_dir.parent,                             # .../editio-bench
        data_dir.parent.parent,                      # repo root
    ]
    for anchor in anchors:
        hit = anchor / candidate
        if hit.exists():
            return hit
    searched = "\n  ".join(str(a / candidate) for a in anchors)
    raise FileNotFoundError(
        f"benchmark image_path {raw!r} not found. Searched:\n  {searched}"
    )


def load_benchmarks(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if "benchmarks" not in doc or not doc["benchmarks"]:
        raise ValueError(f"{path}: no benchmarks")
    doc.setdefault("rubrics", {})
    for b in doc["benchmarks"]:
        if b.get("image_path"):
            try:
                b["image_path"] = str(_resolve_image_path(b["image_path"], path))
            except FileNotFoundError:
                if not b.get("image_source"):
                    raise
                b["image_path"] = str(_fetch_image(b, path))
    return doc


def _fetch_image(bench: dict, benchmarks_path: Path) -> Path:
    """Download and crop an image the release may not redistribute (4Q530 is
    IAA copyright), saving it at image_path under the repo root."""
    from io import BytesIO
    from PIL import Image

    src = bench["image_source"]
    dest = benchmarks_path.resolve().parent.parent.parent / bench["image_path"]
    print(f"fetching {bench['id']} image from {src['url']}", file=sys.stderr)
    r = httpx.get(src["url"], follow_redirects=True, timeout=60.0)
    r.raise_for_status()
    im = Image.open(BytesIO(r.content)).convert("RGB")
    if src.get("crop"):
        im = im.crop(tuple(src["crop"]))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, quality=95)
    return dest


def _scorer_messages(bench: dict, candidate: str, rubric: dict) -> list[dict]:
    rubric_txt = json.dumps(rubric, ensure_ascii=False, indent=2)
    system = (
        "You are an expert evaluator of ancient-language scholarship. Score the "
        "candidate answer against the ground truth using this rubric:\n" + rubric_txt
    )
    user = (
        f"TASK TYPE: {bench['task_type']}\n\nPROMPT GIVEN TO THE MODEL:\n{bench['prompt']}\n\n"
        f"GROUND TRUTH:\n{bench['ground_truth']}\n\nCANDIDATE ANSWER:\n{candidate}\n\n"
        "Return ONLY your integer score 0-100 inside a fenced markdown code block."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


async def _vision_capable(http, models: list[str]) -> dict[str, Optional[bool]]:
    """Map each model slug -> True/False/None for image input support.

    None means "unknown" (model list unreachable or slug absent); callers treat
    only an explicit False as grounds for skipping, so a lookup failure degrades
    to the previous behaviour rather than silently dropping every task.
    """
    try:
        resp = await http.get("https://openrouter.ai/api/v1/models", timeout=30.0)
        resp.raise_for_status()
        catalog = {m["id"]: m for m in resp.json()["data"]}
    except Exception as e:
        console.print(f"[yellow]Could not check model modalities ({e}); "
                      f"proceeding without the vision pre-check.[/yellow]")
        return {m: None for m in models}
    out: dict[str, Optional[bool]] = {}
    for m in models:
        if m == FUSION_MODEL:
            # Tried treating this as vision-capable since FUSION_PLUGIN_CONFIG's
            # panel members can all see images -- turns out OpenRouter's fusion
            # *routing layer* rejects image input outright regardless of the
            # panel ("provider error (404): No endpoints found that support
            # image input"), so the panel's own vision support never gets
            # exercised. Left as True (not skipped) so that rejection shows up
            # explicitly as an error in the per-task CSV instead of a silent
            # "no vision support" skip -- same end result, more honest paper
            # trail. See resac2026/clean_suite_master.csv: 10/13 tasks scored.
            out[m] = True
            continue
        entry = catalog.get(m)
        if entry is None:
            console.print(f"[yellow]{m} is not on OpenRouter's model list.[/yellow]")
            out[m] = None
        else:
            out[m] = "image" in entry.get("architecture", {}).get("input_modalities", [])
    return out


async def _answer(client, http, model, prompt, cache, temperature, max_tokens=None, image_path=None, reasoning_effort="none"):
    """Returns (text, cost_usd, cached, error, latency_s, effective_effort).

    latency_s is wall-clock time for the API call, 0.0 on a cache hit -- the
    prior version of this pipeline never recorded latency at all, unlike the
    ad-hoc experiment scripts that timed each call manually, so no run
    through this function before this change has a comparable figure.
    effective_effort is the reasoning effort the answer was actually produced
    at, which differs from the requested one when a "reasoning is mandatory"
    rejection triggered the escalation retry below; callers persist it in the
    results CSV so a replayed run never masquerades as an independent
    measurement at the requested effort.
    """
    import time
    t0 = time.monotonic()
    effective_effort = reasoning_effort
    if image_path:
        # Paths are resolved and existence-checked in load_benchmarks; a missing
        # image raises there rather than silently degrading to a text-only prompt.
        import base64
        with open(image_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
        ]
    else:
        user_content = prompt

    msgs = [
        {"role": "system", "content": SYSTEM_PHILOLOGIST},
        {"role": "user", "content": user_content},
    ]

    # Some models reject reasoning_effort="none" outright ("Reasoning is
    # mandatory for this endpoint and cannot be disabled") rather than
    # silently ignoring it. That is a real, informative rejection of THIS
    # request, not evidence about vision support -- so on that specific
    # error we retry once at the next rung up, instead of either (a) burning
    # the client's full retry budget on a request that will never succeed,
    # or (b) mislabeling it and scoring a fabricated "answer" (both of which
    # this function used to do; see git log for the incident that surfaced
    # this on 2026-09-07 during the reasoning-effort Pareto sweep).
    _RUNGS = ["none", "low", "high"]
    effort = reasoning_effort
    last_err_str = None
    for attempt in range(2):
        if model == FUSION_MODEL:
            # The reasoning-effort knob controls the *target* model, not the
            # fusion panel/judge -- there's nothing to escalate, so run it
            # once under a fixed plugin config rather than pass an
            # undocumented param to a meta-endpoint.
            extra = dict(FUSION_PLUGIN_CONFIG)
        else:
            extra = {"reasoning": {"effort": effort}} if effort else None
        key = cache.key(kind=f"phase_answer_{effort}", model=model, messages=msgs,
                        temperature=temperature, max_tokens=max_tokens) if cache else None
        if cache:
            hit = cache.get(key)
            # A cache hit means we didn't pay for or wait on this call THIS
            # run, but the run that originally produced it did -- for a
            # suite whose whole point is honest cost/latency, replaying that
            # as 0.0 would be exactly the kind of undercounting this rewrite
            # exists to eliminate. An entry from before "latency" was
            # tracked can't tell us that number, so it isn't usable data
            # for this purpose: treat it as a miss and pay for one real call
            # to get a trustworthy figure, which then overwrites the old
            # entry -- the cache heals itself with no manual purging, and
            # with no dependence on which entries happen to predate which
            # fix (unlike deleting suspect keys by hand, which is exactly
            # what proved race-prone earlier tonight).
            if hit is not None and "latency" in hit:
                return hit["text"], hit.get("cost", 0.0), True, None, hit["latency"], effective_effort
        try:
            resp = await client.chat(http, model, msgs, temperature=temperature,
                                     max_tokens=max_tokens, extra=extra)
            choice = resp["choices"][0]
            msg = choice["message"]
            content = (msg.get("content") or "").strip()
            reasoning = (msg.get("reasoning") or "").strip()
            finish_reason = choice.get("finish_reason")

            if content:
                text = content
            elif reasoning:
                # If content is empty, check if reasoning contains a structured output block
                fences = _FENCE.findall(reasoning)
                if fences:
                    text = fences[-1].strip()
                elif finish_reason == "length":
                    # Model exhausted tokens during internal reasoning before emitting output
                    return None, 0.0, False, "exhausted max_tokens during reasoning before emitting answer", time.monotonic() - t0, effective_effort
                else:
                    text = reasoning
            else:
                text = ""
                if finish_reason == "length":
                    return None, 0.0, False, "exhausted max_tokens before emitting answer", time.monotonic() - t0, effective_effort

            p_tok, c_tok, t_tok, cost = extract_usage(resp)
            break
        except Exception as e:
            last_err_str = str(e)
            reasoning_forced = ("reasoning" in last_err_str.lower()
                                 and ("mandatory" in last_err_str.lower()
                                      or "cannot be disabled" in last_err_str.lower()
                                      or "must be enabled" in last_err_str.lower()))
            if reasoning_forced and attempt == 0 and effort in _RUNGS[:-1]:
                console.print(f"[yellow]{model}: reasoning effort {effort!r} rejected "
                              f"({last_err_str}); retrying at "
                              f"{_RUNGS[_RUNGS.index(effort)+1]!r}.[/yellow]")
                effort = _RUNGS[_RUNGS.index(effort) + 1]
                effective_effort = effort
                continue
            # Any other failure (or a second failure) is a real failure: no
            # fabricated answer text gets returned for the scorer to grade.
            return None, 0.0, False, last_err_str, time.monotonic() - t0, effective_effort
    latency = time.monotonic() - t0
    if cache and text:
        cache.put(key, {
            "text": text,
            "cost": cost,
            "latency": latency,
            "prompt_tokens": p_tok,
            "completion_tokens": c_tok,
            "total_tokens": t_tok,
        })
    return text, cost, False, None, latency, effective_effort


async def _score(client, http, scorer, bench, candidate, rubric, cache, reasoning_effort="low"):
    msgs = _scorer_messages(bench, candidate, rubric)
    extra = {"reasoning": {"effort": reasoning_effort}} if reasoning_effort else None
    key = cache.key(kind=f"phase_score_{reasoning_effort}", model=scorer, messages=msgs) if cache else None
    if cache:
        hit = cache.get(key)
        if hit is not None and hit.get("raw"):
            # Re-validate score with robust parser
            revalidated_score = parse_score(hit.get("raw", ""))
            if revalidated_score is not None:
                return revalidated_score, hit.get("raw", ""), hit.get("cost", 0.0), None
    try:
        resp = await client.chat(http, scorer, msgs, temperature=0.0, max_tokens=None, extra=extra)
        msg = resp["choices"][0]["message"]
        raw = msg.get("content") or msg.get("reasoning") or ""
        p_tok, c_tok, t_tok, cost = extract_usage(resp)
    except Exception as e:
        return None, "", 0.0, str(e)
    score = parse_score(raw)
    error = None if score is not None else "unparseable_score"
    if cache:
        cache.put(key, {
            "score": score,
            "raw": raw,
            "error": error,
            "cost": cost,
            "prompt_tokens": p_tok,
            "completion_tokens": c_tok,
            "total_tokens": t_tok,
        })
    return score, raw, cost, error


TIEBREAK_THRESHOLD = 10  # points; see _consensus_score


def _consensus_score(scores: dict[str, Optional[float]]) -> tuple[Optional[float], bool]:
    """Combine a task's scorer results into one number.

    With two scorers: their mean, unless they disagree by more than
    TIEBREAK_THRESHOLD points, in which case the caller fetches a third
    scorer and this is called again with all three -- then the result is
    their median, which is robust to the one outlier a two-judge panel can't
    otherwise resolve. With one scorer (or after a tiebreak with a scorer
    that errored), falls back to whatever is available.

    Returns (consensus_score_or_None, needs_tiebreak).
    """
    vals = [v for v in scores.values() if isinstance(v, (int, float))]
    if len(vals) < 2:
        return (vals[0] if vals else None), False
    if len(vals) == 2:
        a, b = vals
        if abs(a - b) > TIEBREAK_THRESHOLD:
            return None, True  # caller must fetch a third scorer and retry
        return statistics.mean(vals), False
    return statistics.median(vals), False


async def run_phase_bench(
    benchmarks_path: Path,
    out_csv: Path,
    targets: list[str],
    scorers: list[str],
    *,
    phases: Optional[list[str]] = None,
    concurrency: int = 4,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    cache_path: Path = Path(".dss_cache.sqlite"),
    tiebreaker_scorer: Optional[str] = None,
    reasoning_effort: str = "none",
) -> list[dict]:
    doc = load_benchmarks(benchmarks_path)
    rubrics = doc.get("rubrics", {})
    sel = set(phases) if phases else None
    benches = [b for b in doc["benchmarks"] if b.get("ground_truth")]
    if sel:
        benches = [b for b in benches if b["task_type"] in sel]
    skipped = [b["id"] for b in doc["benchmarks"]
               if not b.get("ground_truth") and (sel is None or b["task_type"] in sel)]
    if not benches:
        console.print("[red]No benchmarks with ground truth for the selected phase(s).[/red]")
        return []
    if skipped:
        console.print(f"[yellow]Skipping {len(skipped)} task(s) awaiting ground truth: {skipped}[/yellow]")

    client = OpenRouterClient()
    cache = Cache(cache_path)
    sem = asyncio.Semaphore(concurrency)
    cost = 0.0

    async def bounded(coro):
        async with sem:
            return await coro

    rows: list[dict] = []
    timeout = httpx.Timeout(600.0, connect=45.0)
    async with httpx.AsyncClient(timeout=timeout) as http:
        vision = await _vision_capable(http, targets)
        # A text-only model cannot attempt an image-bearing task at all. Record
        # that as an explicit skip rather than letting it answer from memory of
        # published editions (which scores ~100 on a task it never saw) or 404
        # on the image payload — "can't" must stay distinguishable from "did
        # badly" in the CSV.
        pairs = [(b, t) for b in benches for t in targets
                 if not (b.get("image_path") and vision.get(t) is False)]
        no_vision = [(b["id"], t) for b in benches for t in targets
                     if b.get("image_path") and vision.get(t) is False]
        if no_vision:
            names = sorted({t for _, t in no_vision})
            console.print(
                f"[yellow]Skipping {len(no_vision)} image-bearing task(s): "
                f"no vision support in {names}[/yellow]")

        ans_tasks = {(b["id"], t): asyncio.create_task(
            bounded(_answer(client, http, t, b["prompt"], cache, temperature, max_tokens,
                            b.get("image_path"), reasoning_effort)))
            for b, t in pairs}
        n_ans, done_ans = len(ans_tasks), [0]

        def _ans_done(key):
            def cb(_fut):
                done_ans[0] += 1
                console.print(f"[dim]answered {done_ans[0]}/{n_ans}: {key[0]} ({key[1]})[/dim]")
            return cb
        for key, tk in ans_tasks.items():
            tk.add_done_callback(_ans_done(key))
        await asyncio.gather(*ans_tasks.values())

        def _blank_scores(row: dict, reason: str) -> None:
            for s in scorers:
                row[f"score::{s}"] = NA
                row[f"score_raw::{s}"] = ""
                row[f"score_error::{s}"] = reason
                row[f"score_cost_usd::{s}"] = 0.0
            if tiebreaker_scorer:
                row[f"score::{tiebreaker_scorer} (tiebreak)"] = NA
                row[f"score_raw::{tiebreaker_scorer} (tiebreak)"] = ""
                row[f"score_error::{tiebreaker_scorer} (tiebreak)"] = reason
                row[f"score_cost_usd::{tiebreaker_scorer} (tiebreak)"] = 0.0
                row["score_consensus"] = NA
                row["tiebreak_triggered"] = False

        for b in benches:
            rubric = rubrics.get(b["task_type"], rubrics.get("translation", {}))
            for t in targets:
                if (b["id"], t) not in ans_tasks:
                    row = {"benchmark": b["id"], "siglum": b.get("siglum", ""),
                           "task_type": b["task_type"], "model": t,
                           "verification_status": b.get("verification_status", ""),
                           "answer": "", "answer_cached": False,
                           "answer_cost_usd": 0.0, "answer_latency_s": 0.0,
                           "answer_reasoning_effort": reasoning_effort,
                           "answer_status": "skipped: model has no vision support"}
                    _blank_scores(row, "not_scored")
                    rows.append(row)
                    continue
                text, acost, _cached, err, alat, eff_effort = ans_tasks[(b["id"], t)].result()
                cost += acost
                row = {"benchmark": b["id"], "siglum": b.get("siglum", ""),
                       "task_type": b["task_type"], "model": t,
                       "verification_status": b.get("verification_status", ""),
                       "answer": text or "", "answer_cached": _cached,
                       "answer_cost_usd": acost, "answer_latency_s": round(alat, 2),
                       "answer_reasoning_effort": eff_effort}
                if not text:
                    row["answer_status"] = err or "failed"
                    _blank_scores(row, "not_scored")
                    rows.append(row)
                    continue
                if b.get("image_path") and claims_no_image(text):
                    # The image was sent; denying it is a failed task, not abstention.
                    row["answer_status"] = NO_IMAGE_STATUS
                    _blank_scores(row, "not_judged: claims no image")
                    row["score_consensus"] = 0.0
                    rows.append(row)
                    continue
                row["answer_status"] = "ok"
                sc_tasks = {s: asyncio.create_task(
                    bounded(_score(client, http, s, b, text, rubric, cache)))
                    for s in scorers}
                await asyncio.gather(*sc_tasks.values())
                scores: dict[str, Optional[float]] = {}
                for s in scorers:
                    score, raw, c, serr = sc_tasks[s].result()
                    cost += c
                    scores[s] = score
                    row[f"score::{s}"] = score if score is not None else NA
                    row[f"score_raw::{s}"] = raw
                    row[f"score_error::{s}"] = serr or ""
                    row[f"score_cost_usd::{s}"] = c

                if tiebreaker_scorer:
                    consensus, needs_tiebreak = _consensus_score(scores)
                    if needs_tiebreak:
                        # The two scorers disagree by more than
                        # TIEBREAK_THRESHOLD points -- bring in a third judge
                        # and use the median of all three rather than
                        # trusting whichever of the first two happened to be
                        # harsher or more lenient on this particular answer.
                        tb_score, tb_raw, tb_cost, tb_err = await bounded(
                            _score(client, http, tiebreaker_scorer, b, text, rubric, cache))
                        cost += tb_cost
                        col = f"{tiebreaker_scorer} (tiebreak)"
                        row[f"score::{col}"] = tb_score if tb_score is not None else NA
                        row[f"score_raw::{col}"] = tb_raw
                        row[f"score_error::{col}"] = tb_err or ""
                        row[f"score_cost_usd::{col}"] = tb_cost
                        scores[col] = tb_score
                        consensus, _ = _consensus_score(scores)
                        row["tiebreak_triggered"] = True
                    else:
                        col = f"{tiebreaker_scorer} (tiebreak)"
                        row[f"score::{col}"] = NA
                        row[f"score_raw::{col}"] = ""
                        row[f"score_error::{col}"] = "not_needed"
                        row[f"score_cost_usd::{col}"] = 0.0
                        row["tiebreak_triggered"] = False
                    row["score_consensus"] = round(consensus, 1) if consensus is not None else NA
                rows.append(row)
                console.print(f"[dim]scored {len(rows)}/{n_ans}: {row.get('benchmark')} "
                              f"({row.get('model')}) -> {row.get('score_consensus', '')}[/dim]")

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    tiebreak_col = f"{tiebreaker_scorer} (tiebreak)" if tiebreaker_scorer else None
    all_score_cols = list(scorers) + ([tiebreak_col] if tiebreak_col else [])
    cols = ["benchmark", "siglum", "task_type", "verification_status", "model",
            "answer_status", "answer_cached", "answer_cost_usd", "answer_latency_s", "answer",
            *[f"score::{s}" for s in all_score_cols],
            *(["score_consensus", "tiebreak_triggered"] if tiebreaker_scorer else []),
            *[f"score_raw::{s}" for s in all_score_cols],
            *[f"score_error::{s}" for s in all_score_cols],
            *[f"score_cost_usd::{s}" for s in all_score_cols]]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})
    console.print(f"[green]Wrote {out_csv}[/green] ({len(rows)} rows)  "
                  f"API cost this run: ${cost:.4f}")
    return rows


def phase_summary(rows: list[dict], scorers: list[str]) -> list[dict]:
    """Mean score per (model, phase) across scorers, N/A-safe, plus per-model overall.

    Uses each row's own "score_consensus" when present (mean of the two
    scorers, or the median of three when they disagreed by more than
    TIEBREAK_THRESHOLD -- see _consensus_score) so a resolved tiebreak is
    reflected in the summary; rows without that column (older runs, or a
    run with no tiebreaker configured) fall back to the plain scorer mean.
    """
    def numeric(r):
        if isinstance(r.get("score_consensus"), (int, float)):
            return r["score_consensus"]
        vals = [r[f"score::{s}"] for s in scorers
                if isinstance(r.get(f"score::{s}"), (int, float))]
        return statistics.mean(vals) if vals else None

    by: dict = {}
    per_model: dict = {}
    for r in rows:
        m = numeric(r)
        if m is None:
            continue
        by.setdefault((r["model"], r["task_type"]), []).append(m)
        per_model.setdefault(r["model"], []).append(m)
    out = [{"model": model, "phase": phase,
            "mean_score": round(statistics.mean(xs), 1), "n_tasks": len(xs)}
           for (model, phase), xs in sorted(by.items())]
    out += [{"model": model, "phase": "ALL_PHASES",
             "mean_score": round(statistics.mean(xs), 1), "n_tasks": len(xs)}
            for model, xs in sorted(per_model.items())]
    return out


def print_phase_summary(rows: list[dict], scorers: list[str]) -> None:
    summ = phase_summary(rows, scorers)
    console.print("\n[bold]=== SCORE BY MODEL x WORKFLOW PHASE ===[/bold]")
    console.print(f"{'model':32} {'phase':22} {'mean':>6} {'n':>4}")
    for s in summ:
        console.print(f"{s['model']:32} {s['phase']:22} {s['mean_score']:>6} {s['n_tasks']:>4}")
