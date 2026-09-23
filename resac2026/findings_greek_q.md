# Comprehensive Research Report: Greek Vision Benchmark & TEI Collation (v2 Ground Truth)

> **[2026-08-29] SUPERSEDED — do not cite the numbers in this memo.** The ground
> truth described here was later found to be the normalized layer staged as
> diplomatic (duplicated title, expanded nomina sacra); the corrected diplomatic
> ground truth and the full state-A/C analysis are in
> `greek_gt_decision_memo.md`. The §2 leaderboard also predates the scorer fixes
> of 2026-08-29 (content-filter exclusion, incomplete-capture rule, WER against
> the normalized GT). Current figures of record: `PROVENANCE.md` §3 and the
> re-scored `benchmark_results/*_scored.json`. Retained for the collation
> narrative (§3–§6) only.

**Project:** SSHRC IDG – Generative AI in Digital Humanities Research Methodology  
**Target Manuscript:** Codex Marchalianus (*Vat. gr. 2125*), Page 11 (*Vitae Prophetarum* – Life of Isaiah)  
**Date:** August 21, 2026  
**Researchers:** Demarquis Moss & Dr. Ken Penner  

---

## 1. Executive Summary & Benchmark Scope

This report documents the updated multi-model vision benchmark evaluation conducted on **Codex Marchalianus (Vat. gr. 2125), Page 11**, an uncial/majuscule Greek manuscript from the 6th–7th century containing the *Vitae Prophetarum* (Lives of the Prophets).

Following human-in-the-loop (HITL) collation and error reconciliation against the high-resolution digital facsimile, the ground truth was updated to **v2** (`transcription/XML Transcription/Vat.gr.2125_0029_pa_0011_m_correct.xml`). The benchmark suite was executed across an expanded 17-model roster, recording Character Error Rate (CER), Word Error Rate (WER), length ratio, API cost, and execution latency.

---

## 2. Updated Multi-Model Benchmark Leaderboard (v2 Ground Truth)

| Rank | Model | CER (Diplomatic) | WER (Normalized) | Length Ratio | Repetition Score | Cost ($) | Elapsed Time (s) | Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **`anthropic/claude-opus-4.8`** | **0.149** | **0.281** | 0.95 | 0.000 | $0.1505 | — | **Gold Standard Leader** |
| 2 | **`x-ai/grok-4.6`** | **0.170** | **0.310** | 0.93 | 0.000 | **$0.0566** | 125.8 s | **Top Cost-to-Performance** |
| 3 | **`openai/gpt-5.5`** | 0.226 | 0.431 | 0.94 | 0.000 | $0.3431 | — | Strong accuracy |
| 4 | **`qwen/qwen3-vl-235b-thinking`** | 0.392 | 0.865 | 0.95 | 0.000 | $0.1092 | 611.7 s | High reasoning latency |
| 5 | **`xiaomi/mimo-v2.5`** | 0.398 | 0.601 | 0.72 | 0.000 | **$0.0052** | 205.2 s | Ultra-budget vision |
| 6 | **`openai/gpt-5.6-luna`** | 0.434 | 0.918 | 0.81 | 0.000 | **$0.0048** | **31.0 s** | Fastest / lowest cost |
| 7 | **`google/gemini-3.1-pro-preview`** | 0.603 | *n/a* | 1.43 | 0.003 | $0.1621 | 85.3 s | Output formatting repetition |
| 8 | **`qwen/qwen3.8-max`** | 0.748 | *n/a* | 1.50 | 0.000 | $0.1743 | 508.9 s | Output verbosity bloat |
| 9 | **`meta/muse-spark-1.2`** | 0.753 | *n/a* | 1.52 | 0.002 | $0.0260 | 47.8 s | Output verbosity bloat |
| 10 | **`google/gemini-2.5-pro`** | 0.817 | *n/a* | 1.50 | 0.000 | $0.1317 | 109.5 s | Formatting bloat |
| — | **`google/gemini-3.7-flash`** | — | — | — | — | — | 31.9 s | **BLOCKED** (`content_filter SAFETY`) |
| — | **`google/gemma-4-31b-it:free`** | — | — | — | — | — | 1.0 s | **RATE_LIMITED** (429) |
| — | **`anthropic/claude-opus-5`** | — | — | — | — | — | 1.0 s | **402** (Payment Required) |
| — | **`openai/gpt-5.6-sol`** | — | — | — | — | — | 1.1 s | **EMPTY** |
| — | **`openai/gpt-5.6-terra`** | — | — | — | — | — | 1.5 s | **EMPTY** |
| — | **`openai/gpt-4o`** | — | — | — | — | $0.0050 | 3.1 s | **EMPTY** |
| — | **`moonshotai/kimi-k3`** | — | — | — | — | — | 970.9 s | **TIMEOUT** (970s) |

---

## 3. Key Philological & Technical Findings

1. **Impact of v2 Ground Truth Correction:**
   * Aligning the benchmark target to Demarquis's corrected TEI standard eliminated artificial OCR shape-confusion discrepancies (e.g. `ΕΙΣΟΛΟΝ` $\rightarrow$ `ΕΙΣΟΔΟΝ`, `ΠΟΛΕΩΟΙ` $\rightarrow$ `ΠΟΛΕΜΙΟΙ`, `ΙΟΥΛΑΙΟΙ` $\rightarrow$ `ΙΟΥΔΑΙΟΙ`).
   * Consequently, the normalized Word Error Rate (WER) improved significantly: **Claude Opus 4.8 dropped from 0.370 to 0.281**, and **Grok 4.6 achieved 0.310**.

2. **Emergence of `x-ai/grok-4.6` as a Tier-1 Vision Performer:**
   * Grok 4.6 delivered the second-highest accuracy overall (**`CER = 0.170`**, **`WER = 0.310`**) at a fraction of the cost (**$0.0566** vs $0.1505 for Claude Opus and $0.3431 for GPT-5.5).

3. **Content Filtering Bottleneck on Ancient Texts:**
   * Gemini 3.7 Flash consistently triggers commercial safety content filtering on the martyrdom narrative of Isaiah (`πρισθεὶς εἰς δύο` / sawn in two under Manasseh), illustrating the critical need for academic safety-filter exemption agreements in digital humanities research.

---

## 4. Associated Corpus Data Files

* **Target Image:** `transcription/Vat.gr.2125_0029_pa_0011_m.jpg`
* **Master TEI XML Ground Truth:** `transcription/XML Transcription/Vat.gr.2125_0029_pa_0011_m_correct.xml`
* **Benchmark Ingestion Package:** `greek_q_transcriptions.json`
* **Complete Scored Results JSON:** `benchmark_results/greek_q_results_1787071894_scored.json`
