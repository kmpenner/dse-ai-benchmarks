# Ground Truth Audit & Manuscript Collation Worklist

**Target Document:** `transcription/XML Transcription/Vat.gr.2125_0029_pa_0011_m_correct.xml`  
**Facsimile Image:** `transcription/Vat.gr.2125_0029_pa_0011_m.jpg`  
**Reference Policies:** `transcription/GROUND_TRUTH_POLICIES.md` and `demarquis_instruction_manual.md`  
**Date:** August 24, 2026  
**Auditor / Roles:** Demarquis Moss (Lead URA) & Dr. Ken Penner (PI)

---

## 1. Loci Requiring Visual Inspection by Demarquis

Following the **Human-in-the-Loop (HITL) Convergent Disagreement Protocol** (Policy §4), whenever ≥ 3 independent vision models agree on a reading that departs from the human transcription, the locus must be surfaced for physical re-examination against the high-resolution digital facsimile.

### Codex Marchalianus (*Vat. gr. 2125*, Page 11 — Greek Q)
Below are the **30 flagged consensus loci** (accounting for 36 characters / 2.8% of the text surface) that Demarquis needs to inspect under high magnification on `transcription/Vat.gr.2125_0029_pa_0011_m.jpg`.

| # | TEI `<w>` | Manuscript Context | Ground Truth v1 | Model Consensus | Votes | What Demarquis Needs to Visually Verify |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | 1 | `…ΟΝΟΜΑΤΑ [ΤΩΝ] ΠΡΟΦΗΤΩΝ…` | `ΤΩΝ` | `∅` (Omitted) | 4/10 | Check if the rubricated line has `ΤΩΝ` or if the heading begins `ΟΝΟΜΑΤΑ ΠΡΟΦΗΤΩΝ`. |
| **2** | 21 | `…ϋπο μαναϲϲη εν [τριϲειϲ] ειϲ δυο…` | `ΤΡΙϹΕΙϹ` | `Θ` (`ΠΡΙΣΕΙ`) | 3/10 | Check initial letter: uncial `Π` (sawn in two / *πρίσει*) vs misread `Τ`. |
| **3** | 35 | `…υδατων ων [ατωλεϲεν] εζεκιαϲ…` | `Τ` in `ΑΤΩΛΕϹΕΝ` | `Π` (`ΑΠΩΛΕΣΕΝ`) | 3/10 | Check for descenders: `Π` (*ἀπώλεσεν*) vs `Τ`. |
| **4** | 53 | `…προ του [αποθανειν] ολιγνρησασ…` | `ΑΠΟ` in `αποθανειν` | `∅` (`ΘΑΝΕΙΝ`) | 3/10 | Check if the scribe wrote simplex `ΘΑΝΕΙΝ` or compound `ΑΠΟΘΑΝΕΙΝ`. |
| **5** | 53 | `…προ του [αποθανειν] ολιγνρησασ…` | `Ν` in `αποθανειν` | `∅` | 3/10 | Check terminal nu or abbreviation stroke. |
| **6** | 54 | `…προ του θανειν [ολιγνρησασ]…` | `Ν` in `ΟΛΙΓΝΡΗΣΑΣ` | `Ω` (`ΟΛΙΓΩΡΗΣΑΣ`) | 4/10 | Check uncial omega `Ω` vs uncial `Ν` in *ὀλιγωρήσας*. |
| **7** | 64 | `…απεσταλη αυτω εξ [αυτον]…` | `Ν` in `ΑΥΤΟΝ` | `Υ` (`ΑΥΤΟΥ`) | 3/10 | Check genitive singular `ΑΥΤΟΥ` vs accusative `ΑΥΤΟΝ`. |
| **8** | 66 | `…εξ αυτου δια [τον] το εκληθη…` | `Ν` in `ΤΟΝ` | `Υ` (`ΤΟΥΤΟ`) | 3/10 | Check whether the scribe wrote `ΔΙΑ ΤΟΥΤΟ` or `ΔΙΑ ΤΟΝ ΤΟ`. |
| **9** | 78 | `…επι του εζεκια [προσ] τον…` | `Σ` in `ΠΡΟΣ` | `∅` (`ΠΡΟ`) | 4/10 | Check for terminal lunate sigma `Ϲ` in *πρός* vs *πρό*. |
| **10** | 79 | `…επι του εζεκια προσ [τον] ποιη…` | `Ν` in `ΤΟΝ` | `Υ` (`ΤΟ`) | 3/10 | Check neuter articular infinitive `ΤΟ ΠΟΙΗΣΑΙ` vs `ΤΟΝ`. |
| **11** | 80 | `…προσ τον [ποιηεσαι] τουσ…` | `Ε` in `ΠΟΙΗΕΣΑΙ` | `∅` (`ΠΟΙΗΣΑΙ`) | 4/10 | Check if an extra `Ε` is physically written or an OCR insertion. |
| **12** | 100 | `…εν συγκλεισμω [αλλοφυλων]…` | `Ν` in `ΑΛΛΟΦΥΛΩΝ` | `∅` | 3/10 | Check terminal line end: nasal titulus over `Ω` or full letter `Ν`. |
| **13** | 113 | `…ηρωτουν γαρ οι [πολεωοι]…` | `Ω` in `ΠΟΛΕΩΟΙ` | `ΜΙ` (`ΠΟΛΕΜΙΟΙ`) | 3/10 | Disambiguate Caroline/uncial `ΜΙ` vs round `Ω` in *πολέμιοι*. |
| **14** | 127 | `…εαν ουν οι [ϊουλαι] οι ηρχοντο…` | `Λ` in `ΪΟΥΛΑΙ` | `Δ` (`ΙΟΥΔΑΙΟΙ`) | 3/10 | Angular shape check: `Δ` (delta in *Ἰουδαῖοι*) vs `Λ` (lambda). |
| **15** | 143 | `…αιφνιδιωσ εξερχεται ϊνα [λειχυη]…` | `Λ` in `ΛΕΙΧΥΗ` | `Δ` (`ΔΕΙΧΘΗ`) | 3/10 | Check `Δ` (delta) vs `Λ` (lambda) in *δειχθῇ*. |
| **16** | 143 | `…αιφνιδιωσ εξερχεται ϊνα [λειχυη]…` | `Υ` in `ΛΕΙΧΥΗ` | `Θ` (`ΔΕΙΧΘΗ`) | 4/10 | Check uncial oval `Θ` (theta with crossbar) vs `Υ` (upsilon). |
| **17** | 150 | `…και επειδη δια του [ησαιυ]…` | `∅` in `ΗΣΑΙΥ` | `Ο` (`ΗΣΑΙΟΥ`) | 3/10 | Check genitive ending: `ΟΥ` digraph or omitted `Ο`. |
| **18** | 167 | `…ενδοξωσ ϊνα δια [ευχων] αυτου…` | `Ν` in `ΕΥΧΩΝ` | `∅` | 3/10 | Check for terminal suspension stroke over `Ω`. |
| **19** | 182 | `…οτι και χρησμοσ [ελοσθη] αυτοισ…` | `Λ` in `ΕΛΟΣΘΗ` | `Δ` (`ΕΔΟΘΗ`) | 3/10 | Check `Δ` (delta in *ἐδόθη*) vs `Λ` (lambda). |
| **20** | 182 | `…οτι και χρησμοσ [ελοσθη] αυτοισ…` | `Σ` in `ΕΛΟΣΘΗ` | `∅` (`ΕΔΟΘΗ`) | 3/10 | Check if phantom `Ϲ` exists before `Θ` (*ἐδόθη*). |
| **21** | 194 | `…ταφου των [βαιλεων]…` | `∅` in `ΒΑΙΛΕΩΝ` | `Σ` (`ΒΑΣΙΛΕΩΝ`) | 4/10 | Check for faded/abraded `Ϲ` in *βασιλέων*. |
| **22** | 194 | `…ταφου των [βαιλεων]…` | `∅` in `ΒΑΙΛΕΩΝ` | `ΛΕ` | 4/10 | Check letter sequence `ϹΙΛΕ` in *βασιλέων*. |
| **23** | 194 | `…ταφου των [βαιλεων]…` | `Ν` in `ΒΑΙΛΕΩΝ` | `∅` | 3/10 | Check terminal nu / margin truncation. |
| **24** | 203 | `…επι το μεροσ [τοποσ] νοτον…` | `∅` in `ΤΟΠΟΣ` | `Ρ` (`ΤΟ ΠΡΟΣ`) | 3/10 | Check `ΤΟ ΠΡΟΣ ΝΟΤΟΝ` vs misread `ΤΟΠΟΣ`. |
| **25** | 205 | `…το προσ νοτον [ο] αλωμων…` | `Ο` in `Ο` | `Σ` (`ΣΟΛΟΜΩΝ`) | 3/10 | Check if article `Ο` is separate or initial `Ϲ` of *Σολομών*. |
| **26** | 218 | `…κατ ανατολασ τησ [ιον]…` | `Ο` in `ΙΟΝ` | `Ω` (`ΣΙΩΝ`) | 3/10 | Check `ΣΙΩΝ` (Zion) vs misread `ΙΟΝ`. |
| **27** | 221 | `…ητισ εχει [εισολον] απο γαβαων…` | `Λ` in `ΕΙΣΟΛΟΝ` | `Δ` (`ΕΙΣΟΔΟΝ`) | 3/10 | Check `Δ` (delta in *εἴσοδον*) vs `Λ` (lambda). |
| **28** | 239 | `…και εστιν εωσ τησ [σημερον]…` | `Ν` in `ΣΗΜΕΡΟΝ` | `∅` | 3/10 | Check line break / suspension mark for terminal `Ν`. |
| **29** | 249 | `…εκει [σιχεν] ο βασιλευσ…` | `Σ` in `ΣΙΧΕΝ` | `Ε` (`ΕΙΧΕΝ`) | 3/10 | Check uncial `Ε` (*εἶχεν*) vs lunate `Ϲ` (*σιχεν*). |
| **30** | 272 | `…το μυστηριον δαδ [κι] αλωμωνοϲ…` | `∅` in `ΚΙ` | `Α` (`ΚΑΙ`) | 4/10 | Check conjunction `ΚΑΙ` vs abbreviation `ΚϹ` / `ΚΙ`. |

---

### Supplementary Loci across Other Corpora

#### Latin Isidore (*Vat.lat.629*, Folio 3v)
1. **`ierlḿ` vs `iertin`** (Col. 1, lines 11, 23): Verify suspension stroke over `m` for *Hierusalem*.
2. **`Preſciuſ` vs `Preſeuiſ`** (Col. 1, line 38): Inspect Caroline `ſci` ligature in *praescius*.
3. **`conuerti` vs `conuertit`** (Col. 2, line 14): Confirm infinitive `conuerti` (*retro conuerti aquas*).
4. **`Famem` vs `Famen`** (Col. 1, line 17): Confirm terminal `m`.
5. **`f` vs `ſ` (Long-s) Audit**: Check remaining initial/medial instances (`Terribiliſ`, `beliſ`, `capilliſ`).

#### Dead Sea Scrolls Aramaic (*4Q530*, Book of Giants)
1. **Column ii, Lines 7–8**: Check `גנתה` vs `גנתהה` against infrared facsimile.
2. **Column ii, Line 3**: Inspect line-registration between `f6` and `f10+f11+f12`.
3. **Fragment 1 & Fragment 13 (IR)**: Inspect ink trace visibility under IR vs visible cracks to separate authentic readings (`אתקטלו`, `שיזב`) from crack illusions.

---

## 2. Policy Compliance Audit of the Ground Truth

An audit of `transcription/XML Transcription/Vat.gr.2125_0029_pa_0011_m_correct.xml` against `transcription/GROUND_TRUTH_POLICIES.md` identified **8 non-conformance issues**:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             GROUND TRUTH AUDIT SUMMARY                           │
├────────────────────────────────────────────────────┬─────────────┬───────────────┤
│ Requirement (GROUND_TRUTH_POLICIES.md)             │ Status      │ Severity      │
├────────────────────────────────────────────────────┼─────────────┼───────────────┤
│ 1. Two-Tier Standard (Diplomatic & Normalized)     │ NON-COMPLIANT│ CRITICAL      │
│ 2. Scriptio Continua (Greek Majuscule §3.1.1)      │ NON-COMPLIANT│ HIGH          │
│ 3. Lunate Sigma (Ϲ/ϲ Standard §3.1.2)              │ NON-COMPLIANT│ HIGH          │
│ 4. Nomina Sacra & Contractions (<choice> §2.A)     │ NON-COMPLIANT│ HIGH          │
│ 5. Diacritics & Breathing Separation (§3.1.4)      │ NON-COMPLIANT│ MEDIUM        │
│ 6. Physical Line Breaks (<lb break="no"/> §3.2.1)  │ NON-COMPLIANT│ HIGH          │
│ 7. Original vs Modern Punctuation (§3.1.3)         │ NON-COMPLIANT│ MEDIUM        │
│ 8. TEI Header Revision History (<revisionDesc>)    │ NON-COMPLIANT│ LOW           │
└────────────────────────────────────────────────────┴─────────────┴───────────────┘
```

---

### Detailed Audit Breakdown

### 1. Missing Diplomatic Layer & Two-Tier Architecture (Policy §1 & §2)
* **Policy Requirement:** Every master TEI file must provide both a **Diplomatic Tier** (what is physically on parchment) and a **Normalized Tier** (regularized scholarly reading), encoded either via inline `<choice>` tags (`<abbr>`/`<expan>`, `<orig>`/`<reg>`) or dedicated `<div subtype="diplomatic">` and `<div subtype="normalized">`.
* **Finding:** `Vat.gr.2125_0029_pa_0011_m_correct.xml` contains *only* `<div type="edition" subtype="normalized">` (lines 96–399). It has no diplomatic div and no inline `<choice>` tags.
* **Downstream Consequence:** Automated parsers (`parse_tei_q.py`) fall back to parsing the entire XML body, which extracted the heading twice and stored modern accented words as `diplomatic_ground_truth` in `greek_q_correct.json`.

### 2. Greek Scriptio Continua Violation (Policy §3.1.1)
* **Policy Requirement:** The diplomatic stream for Greek majuscule manuscripts must contain **no word spaces**. Spaces are supplied only in the normalized tier.
* **Finding:** Because `Vat.gr.2125_0029_pa_0011_m_correct.xml` only contains normalized `<w>` tokens, the ground truth cannot emit an authentic diplomatic *scriptio continua* string without relying on regex stripping scripts.

### 3. Lunate Sigma Standard (`Ϲ` / `ϲ`) (Policy §3.1.2)
* **Policy Requirement:** The diplomatic layer must use strictly **lunate sigma (`Ϲ` / `ϲ`)**. Standard lowercase sigmas (`σ` / `ς`) belong exclusively to the normalized tier.
* **Finding:** In `Vat.gr.2125_0029_pa_0011_m_correct.xml`, all body words use standard Greek sigmas (`σ` and `ς`, e.g. `πρίσει`, `εἰς`, `δρυὸς`, `διαβάσεως`). Only the sub-head in line 94 contains `Ηϲαϊαϲ`.

### 4. Missing Nomina Sacra & Brevigraph Markup (Policy §2.A & §3.1)
* **Policy Requirement:** All *nomina sacra* must be wrapped in `<choice>` with `<abbr>` and `<expan>` (e.g. `<w lemma="θεός"><choice><abbr>ΘϹ</abbr><expan>θεός</expan></choice></w>`).
* **Finding:** In `Vat.gr.2125_0029_pa_0011_m_correct.xml`:
  - Line 144: `<w lemma="θεός" msd="NNSM">θεὸς</w>` is written out in full (manuscript has overline `ΘϹ`).
  - Lines 331, 390: `<w lemma="Δαυίδ" msd="NIDF">Δαυὶδ</w>` is written out in full (manuscript has overline `ΔΑΔ`).
  - Lines 324, 392: `<w lemma="Σολομών" msd="NNSM">Σολομὼν</w>` is normalized without preserving scribal orthography (`ϹΑΛΩΜΩΝ`).
  - Line 384: `<w lemma="Εֲζεκίας" msd="NNSM">Ἐζεκίας</w>` loses the scribal overline contraction `ΟΕΖΕΚΙΑϹ`.

### 5. Contamination of Diplomatic Stream by Diacritics (Policy §3.1.4)
* **Policy Requirement:** Breathing marks, acute/grave accents, and iota subscripts belong in the normalized layer, not the diplomatic uncial stream.
* **Finding:** Accents and breathings (`Ἠσαΐας`, `Ἱερουσαλὴμ`, `ἀπώλεσεν`) are directly on the main word text without an unaccented diplomatic alternative.

### 6. Missing Physical Line Breaks & Word Division (Policy §3.2.1)
* **Policy Requirement:** Physical manuscript lineation and word divisions across lines must be preserved using `<lb/>` and `<lb break="no"/>`.
* **Finding:** In `Vat.gr.2125_0029_pa_0011_m_correct.xml`, there is only one `<lb/>` at line 114. The remaining ~39 physical line breaks from `Vat.gr.2125_0029_pa_0011_m_unnormalized.md` (e.g. `μανας/ση`, `αυ/τα`, `ευ/θεωσ`, `απεσταλ/μενος`, `δα/δαδ`, `στααδι/οισ`) are missing.

### 7. Modern Punctuation in Main Stream (Policy §3.1.3)
* **Policy Requirement:** Only original scribal punctuation (medial point `·`, punctus) is recorded diplomatically. Modern commas (`,`) and ellipses (`...`) belong in the normalized tier.
* **Finding:** Modern editorial commas appear throughout (lines 173, 197, 215, 236, 243, 251, 264, 276, 292, 310, 329, 337, 354, 393), along with an untagged editorial ellipsis at line 397 (`...`).

### 8. Missing Revision History Header (Policy §4.3 & HANDOFF.md #9)
* **Policy Requirement:** The `<teiHeader>` must contain a `<revisionDesc>` and `<respStmt>` describing changes, dates, and editors involved in collation.
* **Finding:** The header in `Vat.gr.2125_0029_pa_0011_m_correct.xml` ends at line 70 without a `<revisionDesc>`.

---

## 3. Recommended Remediation Plan for Demarquis

1. **Conduct Physical Verification of the 30 Loci:**
   - Use the worklist above to check each locus against `transcription/Vat.gr.2125_0029_pa_0011_m.jpg`.
   - Log final decisions directly in `resac2026/collation_worksheet_Q11.md`.

2. **Structure the Master TEI XML (`Vat.gr.2125_0029_pa_0011_m_correct.xml`) into Two Canonical Tiers:**
   - Model the file after the compliant Latin master file (`transcription/XML Transcription/Vat.lat.629_0016_fa_0003v.xml`) using `<choice>` elements:
     ```xml
     <w lemma="θεός" msd="NNSM">
         <choice>
             <abbr><hi rend="overline">ΘϹ</hi></abbr>
             <expan>θεός</expan>
         </choice>
     </w>
     ```
   - Restore physical `<lb/>` and `<lb break="no"/>` line breaks from `Vat.gr.2125_0029_pa_0011_m_unnormalized.md`.
   - Add `<revisionDesc>` and `<respStmt>` documenting the v2 collation updates.

3. **Re-run Ingestion and Benchmarking:**
   - Run `python3 parse_tei_q.py --xml_path "transcription/XML Transcription/Vat.gr.2125_0029_pa_0011_m_correct.xml"` to regenerate `greek_q_transcriptions.json`.
   - Re-score model outputs with `score_greek_q.py` to produce final CER and WER metrics for the RESAC 2026 conference paper.
