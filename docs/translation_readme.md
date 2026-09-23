# Phase 4: Translation & Lacuna Handling Benchmarking

This directory contains benchmarking protocols, datasets, runners, and evaluation results for **Phase 4 (Translation & Philological Interpretation)** of the SSHRC IDG project.

---

## 1. Objectives & Evaluation Scope
Translation benchmarks evaluate LLMs on ancient fragmentary texts (Aramaic Dead Sea Scrolls, Greek Septuagint):
1. **Lexical & Morphological Accuracy:** Translating ancient roots and verbal stems accurately according to historical grammar.
2. **Lacuna Discipline & Anti-Hallucination:** Preserving bracketed lacunae (`[...]`) and refusing to fabricate missing narrative text with false certainty.
3. **Reading Comprehension:** Understanding allegorical/symbolic narrative structures (e.g. the 200 trees in the Book of Giants dream vision).
4. **Prompt Protocol Variations:** Testing how Baseline vs. Chain-of-Thought (CoT) vs. Negative Constraint prompts affect translation quality and hallucination rates.

---

## 2. Benchmark Tasks in Suite
Maintained in [`editio-bench/data/benchmarks.json`](../editio-bench/data/benchmarks.json):
- `bg-4q530-2ii-tablet`: Reading comprehension and lacuna handling on the 4Q530 col. 2 dream vision (200 trees and consuming fire).
- `bg-4q530-2-enoch-tablet`: Enoch's tablet of judgment to Shemihaza (4Q530 frag. 2); evaluating whether models flag conjectural restorations rather than claiming certainty.
- `bg-6q8-1-ohya-mahway`: Character relationships and rhetorical questions in 6Q8 1 (Ohya and Mahway).
- `bg-4q531-1-gilgamesh`: First-person speech and divine confrontation in 4Q531 1 (appearance of Gilgamesh in Jewish Aramaic text).
- `bg-2q26-tablet-water`: Extreme fragmentation and dream symbolism (immersed tablet in 2Q26).

---

## 3. How to Run

### Run Full Translation / Reading Benchmark
```bash
./translation/run_translation_benchmark.py
```

### Run a Specific Model
```bash
./translation/run_translation_benchmark.py --model google/gemini-3.1-pro-preview
./translation/run_translation_benchmark.py --model anthropic/claude-opus-4.8
```

### Dry Run
```bash
./translation/run_translation_benchmark.py --dry-run
```

---

## 4. Scoring & Ground Truth Protocol
- **Evaluation Scale:** 0–100 scored by dual frontier judges against the critical published translations of Wise, Abegg & Cook (1996, pp. 246–250).
- **Deductions:** Heavy penalties for confident hallucinated restorations of lacunae.

