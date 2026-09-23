# Transcription Phase: Action Plan & Responsibilities

**Project:** SSHRC Insight Development Grant (IDG) – *Generative AI in Digital Humanities Research Methodology*
**Phase:** 1 & 2 – Transcription & Text Establishment
**Target Texts:**

* **Aramaic:** *Book of Giants* (Dead Sea Scrolls; fragment lacunae)
* **Greek:** *Lives of the Prophets* (Codex Marchalianus / Vat. gr. 2125; vision/HTR & manuscript anomalies)
* **Latin:** Isidore of Seville, *De Ortu et Obitu Patrum* (Vat.lat.629, f. 3v — see [latin_isidore_ortu_obitu_patrum_plan.md](latin_isidore_ortu_obitu_patrum_plan.md); replaces the earlier *Ascension of Isaiah* / Vat.lat.5750 target, abandoned as an unworkable triple-layer palimpsest — see [latin_ascension_isaiah_5750_plan.md](latin_ascension_isaiah_5750_plan.md) for that investigation)

---

## Overview

In the **Transcription** phase, we evaluate how Large Language Models (LLMs) compare to traditional deterministic OCR/HTR tools in converting ancient manuscript images or raw fragmentary text into digital representations. We test whether LLMs accurately transcribe low-resource ancient scripts, preserve historical scribal anomalies, and handle missing/damaged text (*lacunae*) without hallucinating plausible but fake readings.

---

## 1. Principal Investigator Tasks (Dr. Ken Penner)

### A. Dataset & Ground Truth Oversight

* [x] **Select & Verify Ground Truth Transcriptions:** Provide or approve verified critical editions for the three target corpora (*Book of Giants*; Codex Marchalianus; Isidore, *De Ortu et Obitu Patrum*). Latin ground-truth edition (Chaparro Gómez 1985) in hand and cross-checked against Vat.lat.629 f. 3v.
* [ ] **Define Scribal Anomaly Categories:** Catalog authentic historical spelling variations, scribal corrections, and lacuna tags (`[...]`) in the ground truth text to ensure they are explicitly tested.

### B. Prompt Engineering Architecture & System Guidelines

* [ ] **Draft Baseline Prompts:** Write the initial system prompts and negative constraints (e.g., *"Do NOT normalize scribal orthography. Preserve all anomalies exactly as transcribed"*).
* [ ] **Define Few-Shot Exemplars:** Select 2–3 high-quality examples of philologically annotated transcriptions to include in few-shot prompt templates.

### C. Scholarly Review & Methodological Calibration

* [ ] **Review Initial Benchmark Runs:** Conduct spot-checks on early model outputs to validate Demarquis’s blind grading consistency and refine scoring rubrics.
* [ ] **Gap Analysis Guidance:** Interpret linguistic failure points (e.g., morphological segmentation failures, tokenization boundaries in Semitic roots).

---

## 2. Lead Undergraduate RA Tasks (Demarquis Moss)

### A. Environment & Data Ingestion

* [ ] **Prepare OpenRouter Environment:** Ensure `.env` file contains valid `OPENROUTER_API_KEY` and local Python scripts point to OpenRouter base URL (`https://openrouter.ai/api/v1`).
* [ ] **Format Ground Truth Files:** Convert ground-truth manuscript texts and images into clean, structured JSON/TEI format in the project directory.
* [ ] **Latin Diplomatic Transcription (NEW — Vat.lat.629, f. 3v):** See [latin_isidore_ortu_obitu_patrum_plan.md](latin_isidore_ortu_obitu_patrum_plan.md) §4 (case study/image) and §5 (task checklist) for full detail, image URL, and ground-truth page references. Whole page (both columns: end of Eliseus §36, all of Isaiah §37, Jeremiah §38, Ezekiel §39, start of Daniel §40) is the case study — same diplomatic TEI conventions as the Greek Q page (preserve abbreviation marks/suspensions as `<abbr>`/`<expan>`, rubricated initials as `<hi rend="rubric">`, do not silently expand).

### B. Execution of Benchmark Runs

* [ ] **Run Benchmark Scripts:** Execute transcription benchmark runs across target model suites:
  * **OpenAI (GPT-5.5 / O3):** Reasoning & text transcription.
  * **Anthropic Claude (Fable 5 / Opus 4.8):** Adherence to strict negative constraints.
  * **Google Gemini (3.1 Pro / Vision):** Multimodal image-to-text transcription (HTR).
  * **Specialized/Open-Weight (DictaLM 3.0, DeepSeek V4, Qwen 3.6):** Localized Hebrew/Aramaic precision.
* [ ] **Verify Execution Parameters:** Ensure `temperature = 0.0` and seed values are set for reproducibility.
* [ ] **Maintain Execution Logs:** Confirm all runs output structured `.json` / `.jsonl` files storing prompts, model responses, token counts, and timestamps.

### C. Human-in-the-Loop (HITL) Blind Grading

* [ ] **Anonymize Model Outputs:** Ensure model identifiers are stripped before grading to avoid bias.
* [ ] **Score Outputs (1–5 Rubric):** Grade each output on the 4 transcription rubric dimensions:
  1. **Lexical Accuracy:** Are the individual words/letters correctly identified?
  2. **Preservation of Anomalies:** Did the model keep scribal errors, or did it "fix" them (Formal Stuckness)?
  3. **Lacuna Handling:** Did the model admit uncertainty over missing text (`[...]`), or did it hallucinate?
  4. **Character/OCR Precision (Vision HTR):** For Greek manuscript images, how accurately were ligatures and letterforms recognized?
* [ ] **Log Evaluation Results:** Enter blind scores into the master Google Drive grading spreadsheet.

---

## 3. AI Agentic Co-Pilot Tasks (Automated Assistance)

* **Script & Data Automation:** Convert raw manuscript text files to JSON/JSONL benchmark formats.
* **Batch Execution:** Automate API batch calls to OpenRouter across multiple models.
* **Metric Calculation:** Calculate tokenization metrics, token-per-second stats, and cost per transcription batch.
* **Initial Anomaly Flagging:** Automatically highlight discrepancies between ground truth and model output for faster human review.

---

## 4. Immediate Next Steps

1. **Ken (PI):** Finalize the ground-truth text sample for the first batch (e.g., Aramaic *Book of Giants* fragments or Greek Codex Marchalianus images).
2. **Demarquis (URA):** Confirm OpenRouter environment setup, run a test 5-item prompt script, and set up the master evaluation spreadsheet.
3. **AI Co-Pilot:** Generate benchmarking runner scripts for the initial transcription test suite.
