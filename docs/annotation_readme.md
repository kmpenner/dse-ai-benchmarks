# Phase 5: Annotation & TEI Encoding Benchmarking

This directory contains benchmarking protocols, datasets, runners, and evaluation results for **Phase 5 (Annotation & TEI Structuring)** of the SSHRC IDG project.

---

## 1. Objectives & Evaluation Scope
Annotation and encoding evaluate whether LLMs can perform rigorous morphosyntactic parsing and generate schema-valid TEI EpiDoc XML:
1. **Morphosyntactic Description (MSD):** Correctly assigning part-of-speech, tense/aspect, voice/mood, person/number/gender, and case across low-resource ancient languages (Ancient Greek, Dead Sea Scroll Aramaic, Biblical Hebrew).
2. **Stem Disambiguation:** Resolving ambiguous consonantal forms (e.g. Aramaic *peal* vs. *pael* vs. *aphel*).
3. **Lexical Lemmatization:** Providing standardized dictionary headwords.
4. **TEI P5 XML Structuring:** Generating schema-valid `<teiHeader>`, `<msDesc>`, and `<w lemma="..." msd="...">` attributes without invalid attributes or hallucinated tags.

---

## 2. Benchmark Tasks in Suite
Maintained in [`editio-bench/data/benchmarks.json`](../editio-bench/data/benchmarks.json):
- `annot-greek-jn1-1-parse`: Word-by-word morphosyntactic and syntactic parse of John 1:1a ($\mathrm{E}\nu\ \dot{\alpha}\rho\chi\tilde{\eta}\ \tilde{\eta}\nu\ \dot{o}\ \lambda\acute{o}\gamma\mathrm{os}$).
- `annot-greek-dan353-theodotion-firstword`: Precision identification of first word in Theodotion Dan 3:53 ($\epsilon\dot{\upsilon}\lambda\mathrm{o}\gamma\eta\mu\acute{\epsilon}\nu\mathrm{os}$ vs $\epsilon\dot{\upsilon}\lambda\mathrm{o}\gamma\eta\tau\acute{\mathrm{o}}\mathrm{s}$).
- `annot-greek-tei-lemma-msd-b54k3v81`: Full TEI XML `<ab>` element annotation with `lemma` and `msd` attributes, Nomina Sacra expansion, and syntax explanation.
- `encode-greek-teiheader-marchalianus`: Production of schema-valid TEI P5 `<teiHeader>` with complete manuscript metadata for *Codex Marchalianus* (Vat. gr. 2125).

---

## 3. How to Run

### Run Full Annotation & Encoding Benchmark
```bash
./annotation/run_annotation_benchmark.py
```

### Run a Specific Model
```bash
./annotation/run_annotation_benchmark.py --model google/gemini-3.1-pro-preview
./annotation/run_annotation_benchmark.py --model anthropic/claude-opus-4.8
```

### Dry Run
```bash
./annotation/run_annotation_benchmark.py --dry-run
```

---

## 4. Scoring & Ground Truth Protocol
- **Evaluation Scale:** 0–100 scored by dual frontier philologist judges against established gold standards.
- **Deductions:** Heavy penalties for incorrect verbal stems, ungrounded certainty on ambiguous forms, and Oxygen XML schema validation failures.

