# Phase 1 & 2: Transcription & Text Establishment

This folder contains all datasets, scripts, prompt templates, and evaluation results for **Phase 1 & 2 (Transcription & Text Establishment)** of the SSHRC IDG project.

---

## Directory Structure

```
transcription/
├── data/
│   ├── raw_xml/               # Demarquis's TEI XML manuscript transcriptions
│   └── greek_q_transcriptions.json  # Parsed ground-truth benchmark entries
├── scripts/
│   ├── parse_tei_q.py         # TEI XML ingestion & diplomatic layer extraction
│   └── run_greek_q_benchmark.py # Vision & text LLM benchmark runner (via OpenRouter)
├── results/                   # Benchmark output logs (.json / .csv)
├── transcription_phase_guide.md # Task assignment & responsibilities guide
└── greek_transcription_q_plan.md # Specific plan for Codex Marchalianus (Q)
```

---

## Quick Start

### 1. Ingest TEI XML Transcriptions
Place Demarquis's TEI XML files into `transcription/data/raw_xml/` and parse them:
```bash
python transcription/scripts/parse_tei_q.py --xml_dir transcription/data/raw_xml/ --output transcription/data/greek_q_transcriptions.json
```

### 2. Run Benchmarks Across LLMs
Execute the vision and text HTR benchmarking suite:
```bash
python transcription/scripts/run_greek_q_benchmark.py --input transcription/data/greek_q_transcriptions.json --output_dir transcription/results/ --models google/gemini-2.5-pro anthropic/claude-3.7-sonnet openai/gpt-4o
```
