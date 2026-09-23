# Ground Truth Transcription Policies & Standards

**Project:** SSHRC Insight Development Grant (IDG) — *Generative AI in Digital Humanities Research Methodology*  
**Authors:** Dr. Ken M. Penner & Demarquis Moss  
**Document Version:** 1.0 (August 2026)  
**Applicability:** Master TEI XML transcriptions, benchmark ingestion packages, and human-in-the-loop collation across Greek (*Codex Marchalianus*), Latin (*Vat.lat.629*), and Dead Sea Scrolls Aramaic (*4Q530*).

---

## 1. Core Philological Architecture: The Two-Tier Standard

Every ground truth record must represent two distinct philological layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MASTER TEI XML FILE                           │
│       Contains unified <choice>, <w>, <orig>/<reg>, <abbr>/<expan>      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                  ┌──────────────────┴──────────────────┐
                  ▼                                     ▼
   ┌─────────────────────────────┐       ┌─────────────────────────────┐
   │      DIPLOMATIC LAYER       │       │     NORMALIZED EDITION      │
   │  • Physical layout & lines  │       │  • Regularized word tokens  │
   │  • Scriptio continua (Greek)│       │  • Expanded abbreviations   │
   │  • Exact scribal brevigraphs│       │  • Standard orthography     │
   │  • Unexpanded Nomina Sacra  │       │  • Breathings, accents, &   │
   │  • Authentic scribal sigla  │       │    modern punctuation       │
   └─────────────────────────────┘       └─────────────────────────────┘
```

1. **Diplomatic Tier (Reading Surface Standard):**
   * Encodes strictly what is physically inscribed on the manuscript.
   * Preserves authentic scribal letterforms (e.g. lunate sigmas `Ϲ`, long `ſ`), unexpanded abbreviations, *nomina sacra*, and scribal spacing (*scriptio continua* in uncial Greek; authentic physical word spacing in DSS/Latin).
   * Used to compute **Character Error Rate (CER)** and evaluate visual letter recognition.

2. **Normalized Tier (Editorial / Lexical Standard):**
   * Encodes a regularized scholarly reading with modern word boundaries, expanded abbreviations, full lemma associations, and standard diacritics/punctuation.
   * Used to compute **Word Error Rate (WER)** and evaluate syntactic/lexical comprehension.

---

## 2. Master TEI XML Encoding Guidelines

To maintain full compatibility between scholarly TEI EpiDoc standards and automated benchmarking ingestion scripts (`parse_tei_*.py`), all manuscript features must be marked using standard TEI structures:

### A. Nomina Sacra and Scribal Contractions
Wrap all *nomina sacra* and scribal contractions in `<choice>` with `<abbr>` and `<expan>`:

```xml
<!-- Greek Nomina Sacra (e.g. Vat.gr.2125) -->
<w lemma="θεός" msd="NNSM">
    <choice>
        <abbr>ΘϹ</abbr>
        <expan>θεός</expan>
    </choice>
</w>

<w lemma="Δαυίδ" msd="NIDF">
    <choice>
        <abbr>ΔΑΔ</abbr>
        <expan>Δαυίδ</expan>
    </choice>
</w>

<!-- Latin Scribal Contractions (e.g. Vat.lat.629) -->
<w lemma="Hierusalem" msd="NIDF">
    <choice>
        <abbr>ierlḿ</abbr>
        <expan>Hierusalem</expan>
    </choice>
</w>

<w lemma="dominus" msd="NMSM">
    <choice>
        <abbr>dn̄s</abbr>
        <expan>dominus</expan>
    </choice>
</w>
```

### B. Abbreviations, Macrons, & Brevigraphs
Represent the physical abbreviation in `<abbr>` using canonical precomposed Unicode characters:

| Scribal Mark | Description | Diplomatic `<abbr>` Encoding | Normalized `<expan>` Encoding |
| :--- | :--- | :--- | :--- |
| **Nasal Titulus** | Horizontal overline for *-m / -n* | Precomposed macrons: `ā, ē, ī, ō, ū` | Full lexical ending: `-am, -em, -um, etc.` |
| **Enclitic *-que*** | Semicolon / colon dot ligature | `q;` or `q:` | `que` |
| **Per / Prae / Pro** | Cross-stroke on descender | `p̄` (or `p` with stroke) | `per-`, `prae-`, `pro-` |
| **Tironian *et*** | Shorthand symbol | `⁊` | `et` |
| **Est suspension** | `e` with cross-stroke | `ē` | `est` |

```xml
<!-- Example: Latin Nasal Titulus -->
<w lemma="mugitus" msd="NASM">
    <choice>
        <abbr>mugitū</abbr>
        <expan>mugitum</expan>
    </choice>
</w>

<!-- Example: Enclitic -que -->
<w lemma="eiusque" msd="RP3GSM+C">
    <choice>
        <abbr>eiuſq<am>;</am></abbr>
        <expan>eiusque</expan>
    </choice>
</w>
```

### C. Scribal Errors and Orthographic Variations
When the scribe departs from standard orthography or makes a slip:

```xml
<!-- Orthographic variation / Historical allograph -->
<choice>
    <orig>ſebaſtia</orig>
    <reg>sebastia</reg>
</choice>

<!-- Scribal spelling slip -->
<choice>
    <sic>conuerti</sic>
    <corr>conuertit</corr>
</choice>
```

---

## 3. Language-Specific Conventions

### 3.1 Greek Majuscule (*Codex Marchalianus* / Vat. gr. 2125)
1. **Scriptio Continua:** The diplomatic stream contains **no word spaces**. Spaces are supplied only in the normalized tier.
2. **Lunate Sigma:** The diplomatic layer uses strictly **lunate sigma (`Ϲ` / `ϲ`)** across both titles and body text. Standard lowercase sigmas (`σ` / `ς`) belong exclusively to the normalized tier.
3. **Punctuation:** Only original punctuation (medial point `·`, punctus, high dot) is recorded diplomatically. Modern commas, question marks, and apostrophes are excluded from the diplomatic layer.
4. **Diacritics:** Breathing marks, accents, and iota subscripts belong in the normalized layer, not the diplomatic uncial stream.

### 3.2 Latin Minuscule (*Vat.lat.629*, Isidore *De ortu et obitu Patrum*)
1. **Lineation & Columns:** Scribe word-breaks at line ends are preserved in the diplomatic stream. Column breaks are marked explicitly (`<cb n="a"/>`, `<cb n="b"/>`).
2. **Long *s* (`ſ`):** In the diplomatic stream, `ſ` is retained for medial/initial positions; standard `s` is used for final positions.
3. **Palaeographical Vowel/Consonant Distinctions:** Diplomatic layer preserves `u` for both `u` and `v`, `i` for both `i` and `j`, and `e` for `ae/oe`. Classical regularizations belong in the normalized layer.

### 3.3 Dead Sea Scrolls Aramaic / Hebrew (*4Q530*, *Book of Giants*)
Transcription follows **DJD I (pp. 46–48)** and **DJD 31 (p. xviii)** conventions:

| Siglum / Character | Meaning | TEI / EpiDoc Encoding | Benchmark Stream Representation |
| :--- | :--- | :--- | :--- |
| **Circle above (`א֯` / U+05AF)** | Very probable reading | `<unclear cert="high">א</unclear>` | `א°` (Letter + degree sign `U+00B0`) |
| **Dot above (`א̇` / U+0307)** | Uncertain reading | `<unclear cert="low">א</unclear>` | `א°` |
| **Middle dot / circle (`·` / `◌`)** | Unidentified trace of ink | `<gap reason="illegible" quantity="1" unit="character"/>` | `·` (`U+00B7`) |
| **Square brackets (`[ ]`)** | Lacuna (lost parchment) | `<supplied reason="lost">...</supplied>` | `[...]` |
| **Curly braces (`{ }`)** | Superfluous / scribal erasure | `<del>...</del>` | Stripped from diplomatic stream |
| **Angle carets (`< >`)** | Supralinear scribal correction | `<add place="above">...</add>` | Included in stream |
| **Vacat (`〚 〛`)** | Scribal blank space | `<space type="vacat"/>` | `[vacat]` |

#### Canonical Authority Rule for 4Q530:
* The Morphosyntactic Database (MSD) XML divides words morphologically (e.g. `<w>עלו</w> <w>הי</w>`). 
* **`4Q530.txt` is the canonical project authority** for orthographic word boundaries and diplomatic readings. Ground truth text must preserve authentic scribal spacing, not morphological sub-tokens.

---

## 4. Human-in-the-Loop (HITL) Convergent Disagreement & Re-Collation

To ensure the Ground Truth is not treated as infallible dogma, the project implements a **two-way Human-in-the-Loop verification protocol**:

```
Model Predictions (17 Models) ──┐
                                 ├──> Consensus Check (consensus_check.py)
Ground Truth TEI ───────────────┘                   │
                                                    ▼
                             Flag Loci: ≥3 Models Agree against Ground Truth
                                                    │
                                                    ▼
                                  Human Visual Re-Collation against
                                      High-Resolution Facsimile
                                                    │
                   ┌────────────────────────────────┴────────────────────────────────┐
                   ▼                                                                 ▼
      [ True Ground Truth Error ]                                       [ Model Normalization Bias ]
  • Typo / keyboard slips                                           • Models normalized archaic form
  • Misread ligatures (e.g. sci, et)                                • Printed edition training bias
  ──> Update TEI XML Ground Truth (v2)                              ──> Retain Ground Truth; Document in Apparatus
```

1. **Trigger Threshold:** Any locus where **≥ 3 independent vision models** agree on a reading that differs from the Ground Truth must be surfaced in a collation worksheet (`build_collation_worksheet.py`).
2. **Visual Inspection Requirement:** The editor re-examines the high-resolution digital facsimile (under infrared for DSS) specifically at the flagged coordinates.
3. **Ground Truth Correction:** If the models identified a genuine transcription slip (e.g., `ΕΙϹΟΔΟΝ` vs `ΕΙϹΟΛΟΝ`, `ierlm` vs `iertin`), the TEI XML file is updated with a version increment and documented in the revision history.

---

## 5. Scoring & Benchmark Ingestion Standards

1. **Parser Automation (`parse_tei_*.py`):**
   * Benchmark ingestion scripts must automatically extract both `diplomatic_ground_truth` and `normalized_ground_truth` directly from `<choice>` structures.
2. **Allograph Folding in Evaluation:**
   * **Letter Identification CER (Headline):** Folds case, diacritics/tituli, long-s (`ſ` → `s`), u/v, i/j, and lunate sigmas (`Ϲ` → `Σ`).
   * **Abbreviation Strict CER:** Preserves all abbreviation marks (`ā`, `p̄`, `q;`, `ΘϹ`), measuring the model's abbreviation fidelity.
   * **Normalized WER:** Evaluates the model's segmented normalized edition against the scholarly normalized edition.
3. **Categorical Handling of Non-Transcriptions:**
   * Failures, abstentions (`[...]` only), refusals, and content-filter blocks must be recorded as explicit categorical outcomes and never conflated with 0.0 or missing CER values.
