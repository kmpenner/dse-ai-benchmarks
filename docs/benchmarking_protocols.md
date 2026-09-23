# Benchmarking Protocols

This document describes how `editio-bench` tests language models on the tasks of a scholarly edition, as run for the RESAC 2026 paper. The code is in `editio-bench/`. For how the answers are scored, see `benchmarks_and_scoring_report.md`. For how the ground truth was established, see `GROUND_TRUTH_POLICIES.md`.

---

## 1. API access

All models are called through **OpenRouter**, one endpoint with one key for every provider. `editio_bench/translate.py` sends requests with `httpx`. It retries with backoff and records the cost in US dollars reported for each call.

* **Credentials.** The key is read from the `OPENROUTER_API_KEY` environment variable and is never stored in the repository.
* **Generation settings** (`config.yaml`):
  * `temperature: 0.0`
  * `max_tokens: 65536`, because reasoning models can use their whole budget thinking before they answer.
* **Reasoning effort.** Each target model runs at `none`, `low` or `high` (`--reasoning`). Some models refuse `none`. For those, the runner retries once at the next level up and records the effort actually used.
* **Images.** Transcription tasks send the manuscript crop as a base64 JPEG in the same message as the prompt.
* **Cache.** Answers and scores are cached in SQLite (`.editio_cache.sqlite`), so an interrupted run can resume without paying twice. A run made mostly of cached answers replays an earlier run, so the clean suite excludes it (see §4).

## 2. The task suite

`data/benchmarks.json` defines **13 tasks** on three manuscripts:

* Codex Marchalianus (Vat. gr. 2125), in Greek
* Vat.lat.629, in Latin
* 4Q530, the Aramaic Book of Giants

| Phase | Greek | Latin | Aramaic |
| :--- | :--- | :--- | :--- |
| Transcription (from an image) | p. 11, lines 1–4 | f. 3v, lines 1–4 | col. ii, frg. 6 (infrared) |
| Collation | *Lives of the Prophets* | Isidore | Giants parallels |
| Translation | Siloam | Seraphim | — |
| Lacuna handling | — | — | Tree vision |
| Annotation | TEI morphosyntax | Abbreviations | Morphology |
| Encoding | TEI header | — | — |

Each task carries:

* a prompt
* a ground truth
* a source citation
* a list of scribal anomalies the answer should preserve
* a verification status: `ESTABLISHED_GT` (from a published edition or a checked project transcription) or `SELF_CONTAINED_GT` (derived from material given in the prompt)

The Greek and Latin images are Vatican Library crops, included with attribution. The Israel Antiquities Authority's 4Q530 image is not redistributed. The task's `image_source` gives the Leon Levy Dead Sea Scrolls Digital Library URL and a crop box, and the runner downloads and crops the image on first use.

## 3. Prompts

Every task is sent with the same system prompt:

> You are a strict philologist working on ancient manuscript texts (Dead Sea Scrolls, Septuagint, Latin parabiblica). Do NOT normalize spelling variations. Preserve all scribal anomalies exactly as transcribed. When text is broken (lacuna), say so explicitly and never present a conjectural restoration as certain.

The user message is the task's prompt from `benchmarks.json`. Transcription prompts ask for a diplomatic layer that follows the DJD sigla conventions.

`prompts/protocols.yaml` also defines three prompt protocols for the separate translation track (`editio_bench.cli run`): baseline, chain-of-thought and negative constraints. The RESAC results come from the workflow suite (`editio_bench.cli phase`), which does not vary the prompt.

## 4. Scoring

* **Judge panel.** Two models score each answer from 0 to 100 against the ground truth, using the rubric for the task's phase in `benchmarks.json`:
  * `minimax/minimax-m3`
  * `google/gemini-3.8-flash`

  If the two disagree by more than 10 points, a third model (`deepseek/deepseek-v4-flash`) also scores the answer, and the final score is the median of the three. Otherwise it is the mean of the two. The judges read text only; they do not see the image.
* **Transcription rubric.** Five dimensions:
  * diplomatic fidelity
  * no silent normalization
  * marking lacunae and uncertain letters
  * keeping the diplomatic and normalized layers distinct
  * epigraphic restraint
* **Character error rate.** On the three image tasks, `scripts/score_visual_cer.py` adds a deterministic character error rate beside the judges, because the judges proved unreliable there.
* **Eligibility for the clean suite.** A configuration enters the clean suite (`resac2026_clean_sweep.json`) only if:
  * at least 90% of its tasks are scored
  * it is not mostly a replay of cached answers

  An answer claiming that no image was attached counts as declined, not as epigraphic restraint. `resac2026/PROVENANCE.md` records these gates and every figure withdrawn under them.

## 5. Outputs

Each run writes one CSV to `results/`, named `phase_<model>_<effort>_<timestamp>.csv`, with one row per task. The columns include:

* the answer, its status, and whether it came from the cache
* cost and latency
* each judge's raw output, score, error and cost
* the consensus score, and whether a tie-break was triggered

The CSVs behind the paper are in `editio-bench/results/`, and `resac2026_clean_sweep.json` indexes them.

## 6. Running it

```bash
cd editio-bench
python -m editio_bench.cli phase --dry-run                                  # offline: list runnable tasks
python -m editio_bench.cli phase --model openai/gpt-5.5 --reasoning low     # one model, whole suite
python -m editio_bench.cli phase --phase transcription --phase collation    # selected phases, all config models
python -m pytest tests -q
```

Hosted models change without notice, so re-runs will drift from the published results. To reproduce the published numbers exactly, rebuild the scores and charts from the archived CSVs (see the Replication page).
