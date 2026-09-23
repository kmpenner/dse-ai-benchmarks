# Phase 3: Collation & Critical Apparatus Benchmarking

This directory contains benchmarking protocols, datasets, runners, and evaluation results for **Phase 3 (Collation & Variant Analysis)** of the SSHRC IDG project.

---

## 1. Objectives & Evaluation Scope
Collation evaluates whether vision and language models can act as reliable scholarly assistants in comparing multiple textual witnesses:
1. **Variant Detection:** Identifying all substantive differences among witnesses without omitting genuine variants or inventing phantom readings.
2. **Text Alignment:** Aligning witnesses correctly despite word order shifts, omissions, and defective orthography.
3. **Typology Classification:** Correctly distinguishing omissions, additions, substitutions, and minor orthographic variance.
4. **Apparatus Formatting:** Formatting output into standardized critical apparatus notation (`[lemma] reading Siglum ;`).

---

## 2. Benchmark Tasks in Suite
The active collation benchmarks are maintained in [`editio-bench/data/benchmarks.json`](../editio-bench/data/benchmarks.json):
- `coll-greek-three-witnesses`: Three-witness Septuagint clause alignment (Gen 1:4 LXX template; substitution $\Theta\mathrm{EO}\Sigma/\mathrm{K}\Upsilon\mathrm{PIO}\Sigma$, omission of $\mathrm{OTI}$).
- `coll-latin-two-witnesses`: Two-witness Latin clause alignment (Gen 1:5 Vetus Latina/Vulgate; omission of *uespere et*, substitution *unus*/*primus*).

---

## 3. How to Run

### Run Full Collation Benchmark (Configured Roster)
```bash
./collation/run_collation_benchmark.py
```

### Run a Specific Model
```bash
./collation/run_collation_benchmark.py --model google/gemini-3.1-pro-preview
./collation/run_collation_benchmark.py --model anthropic/claude-opus-4.8
```

### Dry Run (Task inspection)
```bash
./collation/run_collation_benchmark.py --dry-run
```

---

## 4. Scoring & Ground Truth Protocol
- **Evaluation Scale:** 0–100 scored by dual frontier philologist judges (`anthropic/claude-opus-4.8` and `google/gemini-3.1-pro-preview`).
- **Penalties:** Heavy point deductions for hallucinated variant readings and for editorializing beyond the provided witness evidence.

