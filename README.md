# DSE AI Benchmarks

This is the replication package for **"From Author to Editor"**, presented at RESAC 2026 (Memorial University of Newfoundland, 26 September 2026).

- Authors: Ken M. Penner and Demarquis Moss (St. Francis Xavier University)
- Funding: SSHRC Insight Development Grant R0253025

The study benchmarks large language models on digital scholarly editing tasks in Greek, Latin, Aramaic and Hebrew: transcription, collation, annotation, encoding, lacuna handling and translation.

**Website:** https://kmpenner.github.io/dse-ai-benchmarks/

## Contents

| Path | What it holds |
| :--- | :--- |
| `resac2026/` | Paper, slides, charts, result CSVs, findings notes, `PROVENANCE.md` (the source of every number in the paper) |
| `editio-bench/` | Benchmark harness, tasks and ground truth (`data/benchmarks.json`), prompts, the clean-sweep registry and per-run result CSVs |
| `docs/` | Test protocols, ground-truth policies and scoring documentation |
| `scripts/` | Deterministic scorers (CER) and chart builders |

## Replicate

1. Set up the environment:

   ```bash
   uv venv && . .venv/bin/activate
   uv pip install -r editio-bench/requirements.txt
   ```

2. Re-derive the figures from the published runs. No API key is needed for this step.

   ```bash
   python scripts/score_visual_cer.py          # resac2026/clean_suite_visual_cer.csv
   python scripts/build_clean_suite_report.py  # leaderboard, heatmaps, Pareto charts
   python scripts/build_per_task_pareto.py     # per-task Pareto charts
   ```

3. Re-run the models. This needs an [OpenRouter](https://openrouter.ai) key and costs money.

   ```bash
   export OPENROUTER_API_KEY=...
   cd editio-bench && python -m editio_bench.phase_bench --help
   ```

Hosted models change over time, so fresh runs will not reproduce the published scores exactly. The published CSVs are the record.

## Images

- The Vatican crops (Vat. lat. 629; Vat. gr. 2125) are © Biblioteca Apostolica Vaticana. They are reproduced for non-commercial scholarly use.
- The 4Q530 image is not redistributed. Obtain it from the Leon Levy Dead Sea Scrolls Digital Library (Israel Antiquities Authority).

## Licence

- Code: MIT (`LICENSE`).
- Data, documentation, paper and charts: CC BY 4.0 (`LICENSE-data`).
- Citation metadata is in `CITATION.cff`.
