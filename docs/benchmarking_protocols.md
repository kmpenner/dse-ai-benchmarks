# API Integration & Benchmarking Protocols

This document outlines the architecture and protocols for Phase 1 and Phase 2 of the project, focusing on establishing a secure, reproducible environment for testing Generative AI against traditional scholarly editing tools.

---

## 1. API Integration Architecture

To benchmark multiple Large Language Models (LLMs) effectively and reproducibly, the software environment should be designed to handle multiple API endpoints without rewriting the core application logic.

### Recommended Framework: Unified API Router (OpenRouter)
Instead of managing separate API keys and billing accounts for OpenAI, Anthropic, and Google, we highly recommend using **OpenRouter**. OpenRouter acts as a unified endpoint that allows you to call hundreds of LLMs using the standard OpenAI API format.

**Benefits of OpenRouter for this SSHRC Project:**
1. **Simplified Grant Accounting:** You only need to fund a single OpenRouter account using the StFX research funds, rather than managing separate credit card billings across multiple corporate entities.
2. **Standardized Codebase:** The integration code is identical to using the official OpenAI Python package. You simply change the `base_url` to OpenRouter and use one universal API key.
3. **Unrestricted Model Access:** It provides instant access to the core commercial models (GPT-5.5, Claude Fable 5, Gemini 3.1 Pro) as well as open-weight models (like DeepSeek V4 or Qwen 3.6) for comprehensive benchmarking.

### Secure Environment Setup
*   **Credential Management:** Never hardcode API keys. Use a `.env` file loaded via the `python-dotenv` library to manage your single `OPENROUTER_API_KEY`.
*   **Reproducibility Parameters:** 
    *   Set `temperature = 0.0` for the initial benchmarking phase to ensure outputs are as deterministic and reproducible as possible. 
    *   Set `seed` values where supported (e.g., OpenAI) to lock generation consistency.
*   **Data Storage:** Save all API requests and responses in structured JSON/JSONL format. Every saved output must include: 
    *   The exact `system_prompt` and `user_prompt` used.
    *   Model name and version (e.g., `openai/gpt-5.5` or `anthropic/claude-fable-5`).
    *   Timestamps and token usage (to calculate the "Tokenization Tax").

### Target Models (Mid-2026 SOTA)
Based on current benchmarks, the following models should be prioritized in Phase 1:
*   **Anthropic Claude (Fable 5 & Opus 4.8):** Top choices for highly nuanced, literary translation and adhering to strict negative constraints.
*   **OpenAI (GPT-5.5):** Extremely capable at deep reasoning tasks, specifically useful for parsing Semitic morphology (*binyanim*) and explaining syntactical structures.
*   **Google Gemini (3.1 Pro):** Preferred for RAG workflows requiring massive context (1M+ tokens), such as passing entire lexicons.
*   **Specialized Models:** **DictaLM 3.0** (fine-tuned specifically for Hebrew base-level precision) and **DeepSeek V4 / Qwen 3.6** (for evaluating open-weight performance).

---

## 2. Benchmarking Protocols (Phase 2 & Phase 3)

The goal of the benchmarking process is not just to see if the AI gets the "right" answer, but to systematically analyze *how and why* it fails (Gap Analysis) compared to deterministic tools.

### 2.1 Dataset Preparation (The "Ground Truth")
*   Format the Ground Truth texts (Aramaic Dead Sea Scrolls, Greek *Lives of the Prophets*, etc.) into a consistent schema (e.g., TEI/XML or structured JSON).
*   Include the "anomalies" (e.g., scribal errors, high-variance spelling) explicitly in the metadata, as these are the exact features LLMs tend to "normalize" or erase (Formal Stuckness).

### 2.2 The Human-in-the-Loop (HITL) Evaluation Rubric
When the Undergraduate RAs evaluate the LLM outputs blindly, they will use a standardized rubric scoring the following dimensions (e.g., on a 1-5 scale or Pass/Fail):

1.  **Lexical Accuracy:** Did the model translate or transcribe the root word correctly?
2.  **Morphological Correctness:** Did the model correctly identify and segment the morphology? (e.g., correctly distinguishing between *aphel* and *pael* stems in Aramaic).
3.  **Handling of Uncertainty (Hallucination Index):** When faced with a lacuna (missing text), did the model confidently hallucinate a grammatically perfect but historically impossible reading, or did it express uncertainty/offer plausible alternatives?
4.  **Formal Stuckness Penalty:** Did the model silently "correct" a valid historical scribal anomaly into a standardized modern spelling?

### 2.3 Prompt Engineering Test Sequences (Phase 4 Prep)
The benchmarking pipeline must support rapid iteration of prompt variations. We will test:
*   **Zero-Shot vs. Few-Shot:** Testing if providing the LLM with 2-3 examples of standard philological annotations improves accuracy.
*   **Reasoning-Focused Prompts (Chain-of-Thought):** Forcing the model to explicitly state its morphological and syntactical reasoning (a "translator's notepad") *before* generating the final translation or transcription. This is critical for reducing hallucinations.
*   **Context Injection (RAG):** Passing excerpts from standard scholarly lexicons (e.g., BDB for Hebrew, LSJ for Greek) directly into the system prompt to overcome the model's struggle with rare terminology (tokenization tax).
*   **Negative Constraints:** Utilizing explicit system prompts such as: *"You are a strict philologist. Do NOT normalize spelling variations. Preserve all scribal anomalies exactly as transcribed."*

---

## 3. Recommended Technology Stack
*   **Programming Language:** Python 3.11+
*   **API Management:** `openai` Python package (pointed to the OpenRouter endpoint)
*   **Environment Management:** `uv` or `poetry` (to ensure identical software versions for the PI, PhD student, and URAs).
*   **Data Analysis:** `pandas` and `Jupyter Notebooks` for the PhD student to run the Gap Analysis on the grading data.
*   **Collaboration & File Sharing:** **Google Drive** (for sharing manuscript datasets, student grading sheets, and evaluation rubrics collaboratively with Undergraduate RAs).
*   **Version Control & Codebase:** **GitHub** (to store the python code, prompt libraries, and version-control the evolving "Methodological Blueprint" for open dissemination).
*   **Agentic Orchestration & Management:** **Google Antigravity** or **Hermes Desktop**. Use these agent managers as command centers to run, orchestrate, and trace parallel, long-running agentic tasks (such as batching runs across multiple target datasets) and monitoring execution histories.
