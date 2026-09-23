# editio-bench — scholarly-edition workflow LLM benchmarking

Case-study infrastructure for the **Penner SSHRC IDG**: *validating AI-driven
methods for scholarly editing of low-resource ancient languages* (Qumran
Hebrew/Aramaic, Septuagint Greek, Latin parabiblica), all via a single
[OpenRouter](https://openrouter.ai) key.

Formerly `dss-bench` (a merge of two earlier prototypes, `dss-bench` +
`dss_benchmark`); renamed because the project outgrew its Dead-Sea-Scrolls-only
origin and now covers three manuscript traditions across the full scholarly
editing pipeline. What used to be two separate tracks — a translation-only
tournament and a five-phase task suite — is now **one corpus, one CLI**.

## One suite, five workflow phases

Every task lives in `data/benchmarks.json`, tagged by `task_type`:
**transcription, collation, translation, annotation, encoding**. Each task
carries its own ground truth and rubric; a target model answers, and a scorer
panel grades 0–100 against the ground truth (`editio-bench phase`).

Translation-type tasks additionally support the older evaluation machinery —
chrF++/BLEU, a pairwise ELO tournament, and multi-rater human review — via
`run` / `pairwise` / `report` / `review`, sharing the same corpus file and the
same OpenRouter client/cache as `phase`.

Grounded in the project's three primary manuscripts — Greek Vat.gr.2125_0029
(Codex Marchalianus), Latin Vat.lat.629_0016 (f. 3v), and Aramaic 4Q530 (Book
of Giants) — plus a pilot Qumran/Greek/Latin translation corpus inherited from
the original translation-tournament prototype.

`docs/task-register.html` documents all thirteen tasks — the exact prompt and
image each model receives, the ground truth, and the rubric handed to the
scorers. Regenerate it from the data with
`python3 docs/build_task_register.py`.

## Install
macOS/Linux:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENROUTER_API_KEY=sk-or-v1-...
```

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENROUTER_API_KEY="sk-or-v1-..."
```

## Dataset readiness / RA handoff
```bash
python -m editio_bench.cli readiness
python -m editio_bench.cli readiness --out readiness.md
```
Summarizes, per workflow phase, which tasks are runnable (real ground truth)
versus backlog (`verification_status: NEEDS_GT`, usually a placeholder
reference awaiting an RA). Run this before production runs so placeholder
references never masquerade as scholarly ground truth.

## Benchmark a model across every phase (single OpenRouter slug)
```bash
python -m editio_bench.cli phase --model openai/gpt-5.5            # whole suite
python -m editio_bench.cli phase --model x-ai/grok-5 --phase transcription --phase collation
python -m editio_bench.cli phase --dry-run                          # offline, lists tasks
python -m editio_bench.cli phase                                    # all candidate_models from config
```
Output: `results/phase_<slug>_<ts>.csv` + a score-by-(model × phase) summary.
Backlog tasks (`verification_status: NEEDS_GT`) are skipped until an RA
supplies ground truth. The CSV preserves the model answer, scorer raw output,
scorer errors, and per-call costs so the Human-in-the-Loop validation trail
stays auditable.

Phase coverage: transcription (Latin, Greek diplomatic; Aramaic HTR pending),
collation (Greek, Latin apparatus), translation/reading/lacuna (Book of Giants
Aramaic, Marchalianus Greek, Vat. lat. 629, plus the pilot Qumran corpus),
annotation (Greek Jn 1:1, Theodotion Dan 3:53, TEI lemma/msd), encoding (Codex
Marchalianus TEI header).

## Translation-task tournament (chrF/BLEU, ELO, human review)
Runs only over the `task_type: "translation"` tasks in the same
`data/benchmarks.json`:
```bash
python -m editio_bench.cli tokentax --out tokentax.md            # 0. offline tax analysis
python -m editio_bench.cli run --out results/run1.jsonl          # 1. translate + rubric
python -m editio_bench.cli pairwise --results results/run1.jsonl --out results/comps1.jsonl \
    --judge google/gemini-2.5-pro --max-pairs-per-passage 40  # 2. ELO tournament
python -m editio_bench.cli report results/run1.jsonl --comparisons results/comps1.jsonl --out report.md
python -m editio_bench.cli review --comparisons results/comps1.jsonl --results results/run1.jsonl --out review.html
python -m editio_bench.cli agreement votes_*.json                # human κ
```
The unit of comparison is a **candidate = (model × prompt protocol)**, drawn
from the Prompt Library (`prompts/protocols.yaml`).

## Tests
```bash
python -m pytest tests/ -q
```

## Data provenance
English Book-of-Giants ground truth: Wise, Abegg & Cook, *The Dead Sea Scrolls:
A New Translation* (1996), pp. 246–250. Greek annotation/encoding gold answers:
the PI's `Benchmarks.ipynb` prototype (also the source of the `GRC_Ode_Dan3_81`
translation task). Aramaic consonantal transcriptions and any task awaiting
ground truth (`verification_status: NEEDS_GT`) must be populated by the RA from
a critical edition (Stuckenbruck 1997; Puech DJD 31; Milik 1976) and the Leon
Levy DSS Digital Library before scoring. The ten Qumran Hebrew/Aramaic pilot
translation tasks (`1QS_1_1`, `CD_1_1-2`, `1QM_1_1`, `1QpHab_7_1-2`,
`1QHa_9_1`, `4QMMT_C_26-27`, `1QapGen_20_2-3`, `11QPsa_154_1-3`) and the two
DEMO Greek/Latin tasks carry `ground_truth: null` pending the PI's preferred
scholarly reference translations; the DEMO tasks use standard printed texts,
not manuscript collations. When a task has no ground truth yet, `phase` and
`run` skip it rather than scoring against a placeholder.

**Verify model slugs** against OpenRouter's live list before a production run.
Avoid using the same model as both candidate and judge for production evidence;
the CLI warns when `judge_model` also appears in `candidate_models`.
