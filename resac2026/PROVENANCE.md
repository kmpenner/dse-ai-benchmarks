# Benchmark Number Provenance Registry

**SSHRC IDG** · Compiled 2026-08-29 · Maintainer note: update this file whenever a
number is quoted in any deliverable (paper, slides, scorecard, memos).

**Purpose.** Every figure the project publishes must trace to a scored file in this
repository, and this document is the index of those traces. After the 2026-08-29
coherence review, three classes of entries exist:

- **VERIFIED** — recomputed from the raw run file; matches the source.
- **CORRECTED** — the previously quoted figure was wrong; the entry records both.
- **WITHDRAWN** — no repository evidence exists; do not cite.

**Scoring policy in force since 2026-08-29** (both `score_greek_q.py` and
`score_transcription.py`):

1. `finish_reason=content_filter` / `status=BLOCKED` → unscored, tallied as
   `units_content_blocked`. (Claude Opus 5's three Aramaic responses under a
   content-filter cut were previously scored as transcriptions.)
2. On a **lacuna-free** ground truth, `length_ratio < 0.80` → unscored as an
   incomplete capture, tallied as `units_incomplete_capture` (HANDOFF item 7).
   Deliberately *not* applied to lacunose ground truths (4Q530), where short honest
   output is the correct behaviour.
3. Greek WER is computed against the corpus's **normalized ground truth**
   (`greek_q_transcriptions.json`, keyed by `page_id`), reported with
   `wer_basis="gt-normalized"`, or n/a if the model supplied no normalized edition.
   The old behaviour (Levenshtein over the diplomatic stream's line-blob tokens)
   produced WERs of 6–11 and is dead.
4. Hebrew corpora keep WER on the diplomatic layer (that scribe divides words);
   Latin likewise.

---

## 1. Ground-truth registry

| Corpus | Canonical GT | Staged package | Comparable size | Status |
|---|---|---|---|---|
| Latin (Vat.lat.629 f. 3v, Isidore §36–40) | `transcription/XML Transcription/Vat.lat.629_0016_fa_0003v.xml` | `latin_isidore_transcriptions.json` | 3,697 chars / 678 words | FROZEN, verified |
| Aramaic (4Q530, *Book of Giants*) | `transcription/data/raw_xml/4Q530-1.xml` + word division from `4Q530.txt` | `aramaic_4q530_transcriptions.json` / `aramaic_4q530_ir_transcriptions.json` | 692 of 707 words, 14 units (12 benchmarkable) | FROZEN, verified |
| Greek (Vat.gr.2125 p. 11) | `transcription/XML Transcription/Vat.gr.2125_0029_pa_0011_m_correct.xml`, `<div subtype="diplomatic">` | `greek_q_transcriptions.json` | 1,287 chars | FROZEN, verified (Ruling: State C adopted; heading ΤΩΝ omitted in diplomatic layer) |

Superseded Greek ground truths (do **not** score against these):
`greek_q_results_1787071894.json`'s embedded GT ("state A": 1,365-char stream,
duplicated heading, normalized layer staged as diplomatic — condemned in
`resac2026/greek_q_ground_truth_audit_and_loci.md` §1) and the phantom
"1,276 comparable characters" of chat report §5.1 (exists in no file).

## 2. Latin — Vat.lat.629 f. 3vision benchmark

Authoritative run: `latin_isidore_transcriptions_results_1787342463.json` (third
run, complete captures; re-scored 2026-08-29 with the incomplete-capture rule).

| Claim | Value | Source | Status |
|---|---|---|---|
| Best Latin CER | 0.041 (Gemini 3.1 Pro; 0.042 in the §1 run) | `…1787342463_scored.json` / `…1787330166_scored.json` | VERIFIED |
| Leading group | 0.041–0.087 (Gem 3.1 Pro, Opus 5, Gem 2.5 Pro, Opus 4.8, Gem 3.7 Flash, gpt-5.6-sol, gpt-5.5, Grok 4.6) | `…1787342463_scored.json` | VERIFIED |
| Best WER | 0.195 (Gemini 2.5 Pro) / 0.212 (Gem 3.7 Flash) | `…1787342463_scored.json` | VERIFIED |
| Allograph swing (Claude 4.8) | 0.188 raw → 0.053 folded | `…1787330166_scored.json` (CER 0.760 raw-string era figure; 0.053 from Ken's run) | VERIFIED as reported in findings §2 |
| GT size | 3,697 / 678 | memo §Header | VERIFIED |
| GPT-4o degenerate looping | CER 3.396, len ratio 3.69 | `…1787342463_scored.json` | VERIFIED |

CORRECTED by the incomplete-capture rule: in the §1 run (…1787330166), the rows
0.705 (gpt-5.6-sol), 0.760 (Claude 4.8), 0.788 (qwen-vl), 0.841 (gpt-5.6-luna),
0.962 (gpt-4o), 0.963 (gpt-5.6-terra) are now `scored: false` (truncations); they
must never again be published as a ranking (findings §6 conclusion 1, now enforced
by the scorer). Open item from findings §6.4 (Gemini 3.1 Pro WER 1.000 in the §1
run) stands: the re-scored §1 run still shows WER 1.000 for that model — treat
Greek-vs-Latin WER anomalies as a section-splitter artifact, not a result.

## 3. Greek — Vat.gr.2125 p. 11 benchmark

**Ground truth settled** (2026-08-31 Ken ruling: State C adopted, heading verbatim `ΟΝΟΜΑΤΑ ΠΡΟΦΗΤΩΝ`, 1,287 chars).
Authoritative run: `greek_q_transcriptions_results_1787590116_scored.json`:

| Model | CER | WER (gt-normalized) | note |
|---|---:|---:|---|
| google/gemini-3.1-pro-preview | 0.0365 | 0.117 | |
| google/gemini-3.7-flash | 0.0777 | 0.154 | blocked in the Aug 21 run; transcribes under state C staging |
| anthropic/claude-opus-4.8 | 0.1080 | 0.244 | |
| x-ai/grok-4.6 | 0.1204 | 0.293 | |
| openai/gpt-5.5 | 0.1290 | 0.301 | |
| openai/gpt-4o | 1.266 | 1.635 | degenerate loop, rep 0.984 |

| Historical claim | Quoted | Reality | Status |
|---|---|---|---|
| "Greek best CER 0.121" (deleted paper §3, slides 5/8) | 0.121 | chat report §5.1 only; scored against a GT state that exists in no file; not reproducible | WITHDRAWN |
| "Gemini 3.1 Pro 0.064 / WER 0.204" (slides 8) | 0.064 | same origin as above | WITHDRAWN |
| "Claude 4.8 CER 0.149 / WER 0.281" (findings_greek_q.md) | 0.149 | real numbers **against state A** with the old splitter; the A-run re-scored under the fixed scorer reads 0.139/0.248 (Claude), 0.095/0.210 (Gemini 3.1 Pro) | CORRECTED — supersede pending ruling |
| "1,276 comparable characters" | 1,276 | state A = 1,365; state C = 1,290 | WITHDRAWN |
| Gemini 3.7 Flash 100% content block on Isaiah page | — | `greek_q_results_1787071894.json`: status BLOCKED, 0 output tokens | VERIFIED (clean refusal case) |

Note: the Aug 21 leaderboard inversion at the top (Gemini 3.1 Pro "0.603") was an
artifact of the old scorer's section-splitter counting normalized-edition text as
diplomatic. Any Greek number printed before 2026-08-29 is superseded.

## 4. Aramaic — 4Q530 benchmark

Authoritative run: `aramaic_4q530_ir_transcriptions_results_1787338140_scored.json`
(17 models × 12 units = 204 calls, re-scored 2026-08-29).

| Claim | Value | Source | Status |
|---|---|---|---|
| Best CER | 0.7541 (meta/muse-spark-1.2); WER 1.030 | re-scored file | VERIFIED |
| "WER ≈ 1.000 for every model" | — | per-model WERs 0.961–1.273 | VERIFIED (say "at or near 1.0", not "0.980") |
| Claude Opus 5 | **0/12 scored, 12 content-blocked, $0.4856 billed** | re-scored file | CORRECTED — three units were scored as transcriptions before; nuance: visible output was disciplined abstention prose under a `content_filter` cut (see §6) |
| Colour-run control (7 models × 9 blank images) | Gemini 3.1 Pro 9/9 text; Claude 4.8 & GPT-4o 0/9 | `…1787315575_scored.json` | VERIFIED |
| "Hallucinators ranked first and third" | — | actual colour-run CER order: 3.7-flash, 3.1-pro, gpt-5.5, 2.5-pro, qwen-vl, claude-4.8, gpt-4o(unscored) | CORRECTED — prolific hallucinators took 1st–2nd; abstainers unscored/bottom. Inversion argument unaffected |
| Outcome taxonomy (204 calls) | 94 scoreable | now **91** (3 opus-5 rows unscored) | CORRECTED in findings memo |
| Cost | ~$9 total; Kimi K3 $2.87 | memo §4 | VERIFIED (Kimi $2.87 in run) |
| GT size | 692 of 707 words, 14 units / 12 benchmarkable | memo §Header | VERIFIED |
| "204 calls" vs "14 units" | 204 = 17 × **12** | run files | CORRECTED in deleted draft; 12-unit framing required |

## 5. Phase panel (editio-bench)

Source: `editio-bench/results/phase_panel_31models_minimax_grok.csv` (403 rows).
Authoritative table: `benchmark_results/cross_phase_scorecard.md` (regenerated
2026-08-29; regeneration method and every correction listed in its §4). Summary:
31 models now all tabulated (qwen3.8-max 0/13, $0.3279 spent); cost column =
per-model CSV sums; transcription phase mean 48.9; the old $0.040/$0.022
efficiency figures are WITHDRAWN (not in the CSV). Judge-independence caveat
(self-family scoring) is disclosed in the scorecard.

## 5c. Visual-transcription CER (2026-09-22)

Source: `resac2026/clean_suite_visual_cer.csv`, built by `scripts/score_visual_cer.py`
from each sweep config's results CSV and the `Line N:` ground truth in
`editio-bench/data/benchmarks.json`. CER = edit distance of the GT letter stream to
the best-matching span of the model's diplomatic layer ÷ GT length (free ends,
because GT covers only the 4 cropped lines); `hyp_ratio` records over-generation.
Greek: majuscule only, sigma/omega folded. Latin: loose (letters) and strict
(abbreviation marks). Aramaic: extant letters only on both sides. Cache-replay
configs appear in the CSV but inherit the gates of §5b. Recall: no diplomatic
transcription of either page is published (Ken, 2026-09-22). The published editions
(Schermann 1907 for the *Vitae Prophetarum*; Chaparro Gómez 1985 for Isidore) are
normalized, so reciting them produces minuscule letters and expanded abbreviations.
Greek majuscule-only CER and strict Latin CER count those as errors. Loose Latin CER
folds abbreviation marks, so it tells reading from recall less well.
`declined` also covers "cannot perform this transcription" phrasings and answers
gated under §5d. `claims_no_image` marks the §5d case separately, so it is never
confused with an abstention about the manuscript itself (blank leather, "no ink
visible"), which stays creditable.

## 5d. No-image-claim gate (2026-09-22)

**Rule (enforced in `editio_bench/phase_bench.py`, `NO_IMAGE_CLAIM_RE`):** on an
image task, an answer claiming that no image was attached or provided is
recorded as `answer_status = declined: claims no image attached`. It is not sent
to the judges and scores **0**, because the image is always sent, so denying it
is a failed task (Ken, 2026-09-22; first applied as N/A, then changed to 0).
Reason: the judges are text-only and cannot see the image. The rubric's "full
credit for epigraphic restraint" is meant for located judgments about the
manuscript, but it lets "you attached nothing" pass as restraint.

| Corrected claim | Reality | Status |
|---|---|---|
| mimo-v2.6-flash (none), `trans-aramaic-4q530-f2ii` = 100 (quality 60.88, 13/13) | The answer states "no image file has actually been attached". The judges scored it minimax-m3 0, gemini-3.8-flash 100, deepseek tiebreak 100. The image *was* delivered: the cached call used 572 prompt tokens, identical to three 2026-09-22 re-sends with the image attached (all of which transcribed); a text-only re-send uses 228. So this is a false claim by the model, not an invalid run. | CORRECTED → 0; quality **53.19**, 13/13 scored |

Applied retroactively by `scripts/regate_no_image_claims.py`. It checks that each
results CSV reproduces its sweep entry before touching it, keeps the judges'
raw scores in their columns, and is idempotent. A scan of all 450 image-task
answers under `editio-bench/results/` found no other no-image claim. Downstream
effect: Aramaic visual mean 8.9 → 7.0 (best 35); best-per-task routing over
configs under $0.20 falls from 95.4 to 89.2. The Pareto frontier is unchanged.

## 5b. Clean suite (editio-bench resac2026_clean_sweep) — 2026-09-10 audit

Registry for `resac2026/clean_suite_master.csv` + `clean_chart_*.png` (both
rebuilt by `scripts/build_clean_suite_report.py` and
`scripts/build_per_task_pareto.py` from `editio-bench/resac2026_clean_sweep.json`).

**Chart-eligibility gates (enforced in code 2026-09-10; do not cite excluded
configs as suite results):**

1. **Coverage ≥ 90%**: a quality mean over a mostly-unscored suite is
   survivorship bias.
2. **Cache-replay exclusion**: a run whose CSV is majority
   `answer_cached=true` is a replay of an earlier config (the
   reasoning-escalation retry in `phase_bench._answer` stores answers under
   the escalated effort's key), not an independent measurement. Both members
   of a replay pair must never be plotted together — duplicates can never be
   Pareto-dominated.

**WITHDRAWN figures (pre-gate charts/leaderboards showed these as results):**

| Withdrawn claim | Reality | Status |
|---|---|---|
| gemma-4-31b-it:free (none) = 70.5, "cheapest frontier anchor" | Mean of the only 2/13 tasks that survived free-tier 429s (11 empty answers, unscored); latency 186s/task = queueing, not inference | WITHDRAWN as a suite result |
| claude-fable-5.1 (low) = 90.33 | 12/13 rows are cache replays of the (none) run — one measurement, not two | WITHDRAWN (duplicate of none) |
| gpt-6-astra (low) = 83.54 | 13/13 cache replays of (none) | WITHDRAWN (duplicate of none) |
| gemini-3.5-flash-lite (low) = 67.5 | 13/13 cache replays of (none) | WITHDRAWN (duplicate of none) |
| deepseek-r1 (low) = 79.8 | 10/13 cache replays of (none) | WITHDRAWN (duplicate of none) |
| claude-3-haiku / claude-opus-4.7 / gpt-5.5 / gpt-5 (none) sweep figures | 100%/12-of-13 replayed rows from runs not in the sweep JSON — cost/latency inherited, not measured | WITHDRAWN pending clean re-run |

**VERIFIED today (13/13 scored, fresh runs, 2026-09-10):**

| Config | Quality | Cost | Latency | Source |
|---|---:|---:|---:|---|
| deepseek/deepseek-v4.1-flash (low) | 70.50 | $0.2192 | 568.7s | `results/phase_deepseek__deepseek-v4.1-flash_sweep.csv` |
| nex-agi/nex-n2.5-pro:free (low) | 60.73 | $0.5674 | 12,436.8s | `results/phase_nex-agi__nex-n2.5-pro_free_sweep.csv` |
| nex-agi/nex-n2.5-mini:free (low) | 36.00 | $0.3210 | 1,661.8s | `results/phase_nex-agi__nex-n2.5-mini_free_sweep.csv` |

(Free-slug costs are answer+judge billing; the target itself bills $0.)

Current cost/latency frontier after gating: gemini-3.7-flash (low/none) →
gpt-6-astra (none) → claude-fable-5.1 (none). gemma-4-31b-it (paid, 55.15)
anchors the cheap end and is genuine (three independently-timed runs).

## 6. Narrative claims to carry into the rewrite (verified)

1. **Script & Damage Gradient** — real, but the Greek tier must be restated after
   the GT ruling: with state C the gradient is two-tier (0.04–0.12 for readable
   scripts; ~0.75+ for 4Q530 IR), and *part of the old Greek "difficulty" was a GT
   artifact*. This is itself a finding about benchmark construction.
2. **Abstention inversion** — verified on blank-leather control (9/9 vs 0/9) and in
   the IR run (length-ratio column). Abstention as a scored outcome class is now
   partially enforced by the scorer (abstained/declined/blocked/incomplete are
   distinct `failure_mode` values and never enter CER).
3. **Content filtering as infrastructure risk** — verified for Gemini 3.7 Flash on
   Greek (0 tokens) and Opus 5 on Aramaic (12/12 `content_filter`, $0.49). The
   honest description of Opus 5 is mixed: vendor cut the response, but the text that
   arrived was disciplined abstention, not refusal — which *supports* the
   abstention-disposition finding (same model, same behaviour, colour and IR runs)
   while still evidencing the filter (finish_reason) and the billing.
4. **Temperature 0 ≠ determinism; repeat before ranking** — verified (Latin §6);
   now structurally enforced for full pages by the incomplete-capture rule.

## 7. Where the deleted deliverables lived

`resac2026/RESAC_2026_paper.md`, `resac2026/RESAC_2026_slides.md`,
`docs/conferences/resac2026/RESAC_2026_paper.md` were deleted 2026-08-29 pending
rewrite after the open issues resolve. `task.md` §3 still references them (left
untouched by request). Git history retains all three.
