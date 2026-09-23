# Greek Ground-Truth Decision Memo — Codex Marchalianus (Vat. gr. 2125 p. 11)

**For:** Ken Penner (ruling requested) · **Prepared:** 2026-08-29
**Question on the table:** which of the two Greek benchmark ground truths is canonical,
state **A** (the ground truth in `benchmark_results/greek_q_results_1787071894.json`,
used for all Aug 21 Greek scoring) or state **C** (the ground truth in
`greek_q_transcriptions.json` / `benchmark_results/greek_q_transcriptions_results_1787590116.json`,
used for the Aug 28–29 runs and the editio-bench phase task).

**Recommendation (verification result, not yet a ruling): adopt state C.**
It is byte-identical to the diplomatic `<div subtype="diplomatic">` layer of the frozen
master `transcription/XML Transcription/Vat.gr.2125_0029_pa_0011_m_correct.xml`
(1,290 comparable characters; a character-stream diff of staged-C vs. the XML returns
**zero** differences). State A is the deprecated output of the pre-restructuring parser
and is documented as buggy in the project's own audit (below). **Two readings in C are
not covered by any recorded ruling and need your eyes on the plate** — see §4.

---

## 1. The three ground-truth states

| | **State A** (Aug 21) | (intermediate, Aug 22) | **State C** (Aug 25→28) |
|---|---|---|---|
| Where | `greek_q_results_1787071894.json` (embedded per-run) | `greek_q_transcriptions_results_1787325850.json` (single EMPTY run; cited by nothing) | `greek_q_transcriptions.json`, all Aug 28–29 run files, `editio-bench/data/benchmarks.json` |
| Comparable stream | 1,365 chars | 1,285 | 1,290 |
| Content | Title block **twice**; body is the **normalized** layer (polytonal, word-spaced, nomina sacra expanded: ΘΕΟΣ, ΔΑΥΙΔ) | — | Diplomatic layer: majuscule, scriptio continua, title once, lunate sigmas, nomina sacra contracted (ΘΣ, ΔΑΔ), physical line breaks |
| Provenance | `parse_tei_q.py` fallback path: the then-current XML had **no** diplomatic div, so the parser concatenated the whole body and staged the normalized edition | intermediate re-stage | Staged from the restructured two-tier XML (audit remediation step 2–3, executed Aug 24–25); **byte-identical to the frozen XML today** |
| Used by | `findings_greek_q.md` leaderboard; Demarquis's qualitative table (CER 0.149 etc.); chat report §5 "v1" column | nothing | Aug 28–29 scored runs; editio-bench `trans-greek-marchalianus-p11` |

There is also a phantom fourth state: the deleted paper's "1,276 comparable characters"
(chat report §5, "v2 corrected"), which matches **no file in the repository** — that
re-scoring was never checked in. Its headline numbers (Claude 0.121 / Gemini-3.1-Pro
0.064) are therefore unreproducible from repo data.

## 2. Why state A exists (documented, not mysterious)

`resac2026/greek_q_ground_truth_audit_and_loci.md` (Aug 24) audited the XML against
`GROUND_TRUTH_POLICIES.md` and found the file had *only* a normalized edition div:

> **Finding:** "contains *only* `<div type="edition" subtype="normalized">` … Automated
> parsers (`parse_tei_q.py`) fall back to parsing the entire XML body, which **extracted
> the heading twice** and stored modern accented words as `diplomatic_ground_truth` in
> `greek_q_correct.json`."

The remediation (restructure the XML into compliant diplomatic + normalized tiers,
re-run ingestion, re-score) produced what is now state C. The Aug 24–25 re-collation
(`collation_worksheet_Q11.md`, all 30 loci decided, full-page sweep ticked) is the
human authority behind C's readings.

## 3. State A vs. state C: the complete residual diff

After the scorer's normalization (case-fold, strip diacritics, fold all four sigma
forms — which erases A's σ/ς-vs-Ϲ differences *as far as CER is concerned*), A and C
differ in exactly **5 blocks, +75 characters in A**:

| # | Block (sigma-folded) | What it is | Authority |
|---|---|---|---|
| 1 | A inserts a second copy of `ΟΝΟΜΑΤΑΤΩΝ…ΚΕΙΝΤΑΙΗ` (+~68 chars) and reads `…ΜΑΝΑΣΣΗ**ΕΝ**ΠΡΙΣΕΙ` where C reads `…ΜΑΝΑΣΣΗΠΡΙΣΘΕΙΣ` | (a) duplicated heading — the parser bug of audit §1; (b) `ΕΝ ΠΡΙΣΕΙ` was v1's slip, ruled **ΠΡΙϹΘΕΙϹ** (worksheet locus 2) | audit §1 Finding; worksheet #2 |
| 2 | A `…ΚΑΙΟΘ**ΕΟ**ΣΤΟΣΗΜΕΙΟΝ…` vs C `…ΚΑΙΟΘΣΤΟΣΗΜΕΙΟΝ…` | nomen sacrum **expanded** (ΘΕΟΣ) in A's normalized body; C keeps contracted ΘΣ with overline (XML L121) | audit §4 item 4 |
| 3 | A `…ΑΥΤΟΝΕΠ**Ι**ΜΕΛΩΣ…` vs C `…ΑΥΤΟΝΕΠ**Ε**ΜΕΛΩΣ…` | A has the normalized spelling ἐπιμελῶς; C's diplomatic reads **ΕΠΕΜΕΛΩΣ** (ms spelling, word split by a physical line break: `ΕΠΕ<lb break="no"/>ΜΕΛΩϹ`, XML L130). **Not covered by any worksheet ruling — spot-check §4.1** | — (needs your eyes) |
| 4 | A `…ΤΑΦΟΥΣΤΟΥΔΑ**ΥΙ**…` vs C `…ΤΑΦΟΥΣΤΟΥΔΑ…` | same expansion issue for the second ΔΑΔ-class nomen sacrum | audit §4 item 4 |
| 5 | A `…ΜΥΣΤΗΡΙΟΝΔΑ**ΥΙΔ**ΚΑΙΣΟΛΟΜΩΝΟΣ…` vs C `…ΜΥΣΤΗΡΙΟΝΔΑ**Δ**ΚΑΙΣΟΛΟΜΩΝΟΣ…` | ΔΑΥΙΔ written out in A; C restores the manuscript's overlined **ΔΑΔ** (XML L141) | audit §4 item 4 (worksheet #30 context) |

Everything else that differs between the two states is sigma form only (A uses σ/ς
majuscule Σ, C uses lunate Ϲ) — invisible to the scorer by design, and correctly so.

**Bottom line of the diff:** every A-vs-C difference is either (i) a documented parser
bug (duplication), (ii) a documented v1→v2 re-collation ruling, (iii) the
normalized-for-diplomatic substitution the audit explicitly condemns (expanded nomina
sacra, accents/word-division in the diplomatic stream), or (iv) the one ungoverned
reading in §4.1. Nothing in A is a rival *reading* of the page that C overruled without
process.

## 4. What needs your spot-check before the ruling

State C's authority chain is strong (frozen XML + 30 ruled loci + full-page sweep), but
two readings rest on no recorded decision, and the audit itself notes convergent
disagreement cannot surface errors the models also made:

1. **ΕΠΕΜΕΛΩΣ vs ΕΠΙΜΕΛΩΣ** — line beginning ΕΠΕΙΔΗ ΔΙΑ ΤΟΥ ΗΣΑΪΟΥ (XML L130;
   ἐπιμελῶς/ἐπεμελῶς). C reads the itacism/variant **ΕΠΕΜΕΛΩΣ**; state A (and every
   model, presumably) reads ΕΠΙΜΕΛΩΣ. Not in the worksheet's 30 loci. If the ms really
   has ΕΠΕΜΕΛΩΣ, C is right and the models are being correctly charged for
   normalization; if it is a v2 typo, one character of GT needs fixing.
2. **Overlined ΔΑΔ (XML L141) and ΘΣ (L121)** — confirm on the plate that the
   contracted sacra forms (not ΔΑΥΙΔ / ΘΕΟΣ) are what stands there. (The worksheet and
   audit both assert this; a 10-second look settles it.)
3. **Title once, no ΤΩΝ** — C's line 1 is the single rubric `ΟΝΟΜΑΤΑΤΩΝΠΡΟΦΗΤΩΝ…ΠΟΥ`
   (worksheet locus 1 ruled: ΤΩΝ only in the normalized tier). Confirm the plate's
   heading is not physically repeated.

## 5. What each choice costs (the actual trade-off for benchmarking)

**Keeping A would mean:**

- Benchmarking against text the project itself has condemned as non-compliant
  (audit: 8 policy non-conformances, two rated CRITICAL/HIGH for exactly this).
- Every model is charged ~68 phantom characters of duplicated title (~5% CER floor)
  plus the normalized layer's expansions — a systematic penalty unrelated to vision.
- A *rewards* normalization: a model that silently writes ΘΕΟΣ for overlined ΘΣ gets
  free matches in A's body, while a faithful diplomatic transcriber is punished. That
  inverts the paper's own "Formal Stuckness" argument (§4b of the deleted draft).
- The frozen, sweep-verified XML would disagree with the benchmark GT — an auditor's
  gift.

**Adopting C means:**

- GT = the frozen diplomatic standard, byte-identical to the XML. Clean provenance.
- The Aug 21 leaderboard inverts at the top: under C, **Gemini 3.1 Pro scores CER
  0.039** (it was 0.603 under A — the duplication+normalization penalty, not vision).
  Claude 4.8 drops 0.149 → 0.110; Grok 4.6 → 0.123. *Caveat:* the Aug 28 run is a
  different API pass, so run variance is confounded with the GT change; the isolation
  experiment (re-scoring the stored Aug 21 outputs against C) is part of the scorer fix
  and will separate the two. Single-shot caveat (HANDOFF item 7) applies either way.
- **The Greek tier of the Script & Damage Gradient compresses.** With best Greek CER at
  0.04–0.08 rather than 0.12–0.15, Greek looks much closer to Latin than to Aramaic;
  the paper's clean three-tier story becomes two tiers (readable scripts 0.04–0.12 vs.
  DSS ~0.75+). This is a *finding* — part of the Greek "difficulty" was a GT artifact —
  but it must be written that way, not hidden.
- **WER needs a scorer fix:** C's diplomatic stream has no word division, so the
  current WER path emits nonsense (values of 6–11 are in the Aug 28 scored files). The
  staged corpus carries a proper normalized layer; the fix computes WER of each model's
  normalized edition against *that* (the design the scorer docstring always claimed).
  Until fixed, Greek WER should be reported as n/a.

## 6. Requested ruling

1. Confirm **C = canonical** Greek benchmark GT (or identify a reading to correct in the
   XML first, re-stage, and re-freeze).
2. Rule on §4.1 ΕΠΕΜΕΛΩΣ after a look at the plate.
3. On confirmation: I re-score every Greek run against C with the fixed scorer, and the
   paper/slides/scorecard get regenerated from those files only.
