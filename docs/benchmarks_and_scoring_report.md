# Benchmark Tests & Scoring Reference — SSHRC IDG

**Suite:** `dss-benchmark-merged` — dataset `DSS-ScholarlyEdition-Workflow-v0.4`
**Generated:** 2026-09-16, from `data/benchmarks.json`, `dss_bench/phase_bench.py`, `dss_bench/judge.py`, and `prompts/protocols.yaml`.

Two evaluation tracks share one OpenRouter client and SQLite cache:

| Track | What it tests | Unit of comparison | Scoring |
|---|---|---|---|
| **B. Four-phase task track** (`dss-bench phase`) | Transcription, Collation, Translation, Lacuna handling, Annotation, TEI Encoding | target model × task, graded against per-task ground truth | Scorer panel of LLMs grades 0–100 (plus deterministic CER/WER in the standalone vision scripts) |
| **A. Translation tournament** (`dss-bench run` / `pairwise`) | Qumran translation quality | candidate = model × prompt protocol (baseline / cot / negative) | 6-dimension LLM judge (1–5) + pairwise ELO tournament with bootstrap CIs |

---

## How scoring works (Track B — `phase_bench.py`)

**Scorer system prompt** (the task's full JSON rubric is injected verbatim):

```
You are an expert evaluator of ancient-language scholarship. Score the
candidate answer against the ground truth using this rubric:
<rubic JSON: scale, dimensions, instructions>
```

**Scorer user prompt:**

```
TASK TYPE: <task_type>

PROMPT GIVEN TO THE MODEL:
<the full task prompt>

GROUND TRUTH:
<the task's ground truth>

CANDIDATE ANSWER:
<the model's raw output>

Return ONLY your integer score 0-100 inside a fenced markdown code block.
```

**Scorer panel** (`config.yaml`): `minimax/minimax-m3`, `deepseek/deepseek-v4-flash` (panel average reported; falls back to `judge_model` `anthropic/claude-opus-4.8` if unset). Scores are parsed from a fenced markdown block; the CSV preserves raw scorer output for audit.

**Target-model system prompt** (all tasks):

```
You are a strict philologist working on ancient manuscript texts (Dead Sea
Scrolls, Septuagint, Latin parabiblica). Do NOT normalize spelling variations.
Preserve all scribal anomalies exactly as transcribed. When text is broken
(lacuna), say so explicitly and never present a conjectural restoration as certain.
```

---


## Phase 1 — Transcription

### `trans-greek-marchalianus-p11`
- **Witness:** Vat. gr. 2125 p. 11 (Marchalianus) (Greek) — Vat.gr.2125_0029_pa_0011_m_correct.xml (Codex Marchalianus, BAV Vat. gr. 2125 p. 11).
- **Status:** ESTABLISHED_GT
- **Anomalies under test:** Lunate sigmas (Ϲ) must not be normalized to standard sigma in diplomatic layer.; Scriptio continua and diaeresis (Ϊ, Ϋ) must be retained diplomatically.
- **Ground truth (482 chars):**

```
(1) DIPLOMATIC LAYER (exact majuscule, scriptio continua, lunate sigma Ϲ, puncta preserved):
ΟΝΟΜΑΤΑΠΡΟΦΗΤΩΝΚΑΙΠΟΘΕΝΕΙϹΙΚΑΙΠΟΥ
ΑΠΕΘΑΝΟΝΚΑΙΠΩϹΚΑΙΠΟΥΚΕΙΝΤΑΙ
ΗϹΑΪΑϹΑΠΟΪΕΡΟΥϹΑΛΗΜΘΝΗϹΚΕΙΫΠΟΜΑΝΑϹϹΗΠΡΙϹΘΕΙϹΕΙϹΔΥΟ•ΚΑΙΕΤΕΘΗΫΠΟΚΑΤΩ
ΔΡΥΟϹΡΩΓΗΛ·

(2) NORMALIZED LAYER (word division, accents, standard sigma σ/ς, expanded names):
Ὀνόματα προφητῶν καὶ πόθεν εἰσὶ καὶ ποῦ ἀπέθανον καὶ πῶς καὶ ποῦ κεῖνται.
Ἠσαΐας ἀπὸ Ἱερουσαλὴμ θνῄσκει ὑπὸ Μανασσῆ πρισθεὶς εἰς δύο· καὶ ἐτέθη ὑποκάτω δρυὸς Ῥωγήλ·
```
- **Prompt sent to the tested model:**

```
TRANSCRIPTION TASK. Provide two transcription layers for the opening lines of Lives of the Prophets: Isaiah from Codex Marchalianus (Vat. gr. 2125, p. 11): (1) a DIPLOMATIC layer in majuscules preserving scriptio continua, lunate sigmas (Ϲ), Nomina Sacra abbreviations with overlines (if present), puncta (• / ·), and line breaks; (2) a NORMALIZED critical layer with lower-case Greek letters, breathings/accents, expanded Nomina Sacra, and standard word division.

SOURCE TEXT (Codex Marchalianus p. 11 opening lines):
ΟΝΟΜΑΤΑ ΠΡΟΦΗΤΩΝ ΚΑΙ ΠΟΘΕΝ ΕΙϹΙ ΚΑΙ ΠΟΥ
ΑΠΕΘΑΝΟΝ ΚΑΙ ΠΩϹ ΚΑΙ ΠΟΥ ΚΕΙΝΤΑΙ
ΗϹΑΪΑϹ ΑΠΟ ΪΕΡΟΥϹΑΛΗΜ ΘΝΗϹΚΕΙ ΫΠΟ ΜΑΝΑϹϹΗ ΠΡΙϹΘΕΙϹ ΕΙϹ ΔΥΟ• ΚΑΙ ΕΤΕΘΗ ΫΠΟΚΑΤΩ
ΔΡΥΟϹ ΡΩΓΗΛ·
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Diplomatic fidelity: is every character reproduced exactly, including archaic/anomalous orthography?
> - No silent normalization (Formal Stuckness): scribal forms (e.g. scriptio continua, lunate sigmas, Nomina Sacra, medieval suspensions, long-s) are preserved, not modernized, in the diplomatic layer.
> - Lacuna/uncertainty marking: gaps and doubtful letters are flagged, never invented.
> - Layer discipline: diplomatic vs normalized layers are kept distinct when both are requested.
>
> **Instructions:** Score 0-100. A publishable diplomatic transcription reproduces the source exactly and NEVER silently normalizes an anomaly. Deduct heavily if the model "corrects" a scribal anomaly in the diplomatic layer or invents text for a lacuna. Return your integer score inside a fenced markdown code block, e.g. ```\n85\n```.

### `trans-latin-vatlat629-f3v`
- **Witness:** Vat. lat. 629 f. 3v (§37 Esaias) (Latin) — Vat.lat.629_0016_fa_0003v_correct.xml (Vat. lat. 629 f. 3v, Isidore §37).
- **Status:** SELF_CONTAINED_GT
- **Anomalies under test:** Scribal abbreviations (p̄phe = prophetae, paſtoꝝ = pastorum, ierl̄m = Hierusalem) must be preserved in diplomatic layer and expanded only in normalized layer.
- **Ground truth (487 chars):**

```
(1) DIPLOMATIC LAYER (exact scribal forms preserved):
Eſaiaſ filiuſ amoſ. non illiuſ p̄phe. ſed alteriuſ qui ſimile nuncupat̄ ē nomine. Hic enim ex numero paſtoꝝ fuit. de oppido thecue. Hic autē genere nobili ortuſ ē. ierl̄m.

(2) NORMALIZED LAYER (expanded abbreviations and classical orthography):
Esaias filius Amos, non illius prophetae, sed alterius qui simile nuncupatus est nomine. Ille (Hic) enim ex numero pastorum fuit de oppido Thecue, hic genere nobilis ortus in Hierusalem.
```
- **Prompt sent to the tested model:**

```
TRANSCRIPTION TASK. Provide two transcription layers for the opening lines of Isidore's De ortu et obitu patrum §37 (Esaias) from Vat. lat. 629 f. 3v:
(1) DIPLOMATIC layer reproducing exact scribal forms, long-s (ſ), suspensions and abbreviations (p̄phe, nuncupat̄ ē, paſtoꝝ, ierl̄m, ppl̄i, dn̄i), and line breaks.
(2) NORMALIZED critical layer expanding all abbreviations in classical orthography (prophetae, nuncupatus est, pastorum, Hierusalem, populi, Domini).

SOURCE DIPLOMATIC LINE:
Eſaiaſ filiuſ amoſ. non illiuſ p̄phe. ſed alteriuſ qui ſimile nuncupat̄ ē nomine. Hic enim ex numero paſtoꝝ fuit. de oppido thecue. Hic autē genere nobili ortuſ ē. ierl̄m.
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Diplomatic fidelity: is every character reproduced exactly, including archaic/anomalous orthography?
> - No silent normalization (Formal Stuckness): scribal forms (e.g. scriptio continua, lunate sigmas, Nomina Sacra, medieval suspensions, long-s) are preserved, not modernized, in the diplomatic layer.
> - Lacuna/uncertainty marking: gaps and doubtful letters are flagged, never invented.
> - Layer discipline: diplomatic vs normalized layers are kept distinct when both are requested.
>
> **Instructions:** Score 0-100. A publishable diplomatic transcription reproduces the source exactly and NEVER silently normalizes an anomaly. Deduct heavily if the model "corrects" a scribal anomaly in the diplomatic layer or invents text for a lacuna. Return your integer score inside a fenced markdown code block, e.g. ```\n85\n```.

### `trans-aramaic-4q530-f2ii`
- **Witness:** 4Q530 f2ii+6-12 (Consonantal Sigla) (Aramaic) — 4Q530.xml; Puech, DJD 31, pp. 28-35; Stuckenbruck 1997.
- **Status:** ESTABLISHED_GT
- **Anomalies under test:** Preserve scribal orthography and lacuna brackets strictly.
- **Ground truth (875 chars):**

```
Diplomatic transcription reproducing Qumran Aramaic forms without normalization:
[ב֯הדין ליליא חזה הוית בחלמי והא גנתא ... גננין ומשקן הויו ...] שרשין רברבין נפקו מן עקר[הון ... וכול מיא ונורא דלקת בכול ...] כולהא

Acceptable Epigraphic Variants:
- Lacuna / Reconstruction Brackets: Either the continuous bracketed reconstruction as above or segmented brackets distinguishing extant ink on the fragment ([ב֯הדין ליליא חזה הוית בחלמי והא גנתא ...] גננין ומשקן הויו [...] שרשין רברבין נפקו מן עקר[הון ... וכול מיא ונורא דלקת בכול ...] כולהא) are fully acceptable, as גננין represents extant preserved leather ink (Puech, DJD 31).
- Doubtful Letter Siglum: Either supralinear circellus (ב֯) or dot (ב̇) is correct.
- Key Philological Requirement: Strict preservation of Qumran Aramaic orthography without silent normalization, vowel pointing, or Rabbinic/Biblical modernization.
```
- **Prompt sent to the tested model:**

```
TRANSCRIPTION TASK. Provide a diplomatic transcription of the following fragmentary line of 4Q530 col. 2 (Book of Giants). Observe Dead Sea Scrolls epigraphic conventions: preserve Qumran Aramaic defective/plene orthography (כול, גננין, שרשין, רברבין, כולהא), mark doubtful letters with a supralinear circellus or dot (ב֯ or ב̇), preserve lacuna brackets and lacuna indicators without modernizing or vocalizing:

[ב֯הדין ליליא חזה הוית בחלמי והא גנתא ... גננין ומשקן הויו ...] שרשין רברבין נפקו מן עקר[הון ... וכול מיא ונורא דלקת בכול ...] כולהא
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Diplomatic fidelity: is every character reproduced exactly, including archaic/anomalous orthography?
> - No silent normalization (Formal Stuckness): scribal forms (e.g. scriptio continua, lunate sigmas, Nomina Sacra, medieval suspensions, long-s) are preserved, not modernized, in the diplomatic layer.
> - Lacuna/uncertainty marking: gaps and doubtful letters are flagged, never invented.
> - Layer discipline: diplomatic vs normalized layers are kept distinct when both are requested.
>
> **Instructions:** Score 0-100. A publishable diplomatic transcription reproduces the source exactly and NEVER silently normalizes an anomaly. Deduct heavily if the model "corrects" a scribal anomaly in the diplomatic layer or invents text for a lacuna. Return your integer score inside a fenced markdown code block, e.g. ```\n85\n```.


## Phase 2 — Collation

### `coll-greek-marchalianus-vitae`
- **Witness:** Vat. gr. 2125 p. 11 vs. Schermann 1907 (Greek) — Vat.gr.2125_0029_pa_0011_m_correct.xml compared against Schermann (1907) critical edition of Vitae Prophetarum.
- **Status:** SELF_CONTAINED_GT
- **Anomalies under test:** Accurate lemma brackets and siglum attribution required.
- **Ground truth (357 chars):**

```
Apparatus:
1. [ἔχει δὲ εἴσοδον] ἥτις ἔχει εἴσοδον M ; (SUBSTITUTION of relative pronoun ἥτις for conjunction δὲ)
2. [οἱ πολέμιοι] + πόθεν πίνουσιν M ; (ADDITION in M of explanatory clause "from where they drink")
3. [καὶ ἐδόθη αὐτοῖς χρησμὸς] ὅτι καὶ χρησμὸς ἐδόθη αὐτοῖς M ; (TRANSPOSITION and ADDITION of causal conjunction ὅτι with word order variation).
```
- **Prompt sent to the tested model:**

```
COLLATION TASK. Collate the readings of Codex Marchalianus (Vat. gr. 2125, p. 11 = M) against the standard critical base text of Lives of the Prophets (Schermann 1907 = S) for the following three loci:
1. Base S: ἔχει δὲ εἴσοδον ἀπὸ Γαβαών vs M: ἥτις ἔχει εἴσοδον ἀπὸ Γαβαών
2. Base S: ἠρώτων γὰρ οἱ πολέμιοι vs M: ἠρώτων γὰρ οἱ πολέμιοι πόθεν πίνουσιν
3. Base S: καὶ ἐδόθη αὐτοῖς χρησμὸς vs M: ὅτι καὶ χρησμὸς ἐδόθη αὐτοῖς
Produce a critical apparatus classifying each variant (addition, omission, substitution, or transposition) with standard apparatus notation [lemma] reading Siglum ;.
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Variant detection: are ALL points of difference among the witnesses identified (none missed, none invented)?
> - Correct alignment: are the witnesses aligned at the right words so the apparatus lemma/reading pairing is right?
> - Variant typology: are omissions, additions, substitutions/lexical variants, and orthographic variants classified correctly?
> - Apparatus discipline: is the critical apparatus well-formed (lemma, supporting sigla, variant readings) and free of editorializing beyond the evidence?
>
> **Instructions:** Score 0-100 for a critical apparatus collating the supplied witnesses. Full credit requires every real variant found and correctly typed, with no invented variants. All evidence needed is IN THE PROMPT, so hallucinated readings should be penalized heavily. Return your integer score inside a fenced markdown code block.

### `coll-latin-vatlat629-isidore`
- **Witness:** Vat. lat. 629 f. 3v vs. Chaparro Gómez 1985 (Latin) — Vat.lat.629_0016_fa_0003v_correct.xml compared against Chaparro Gómez (1985).
- **Status:** SELF_CONTAINED_GT
- **Ground truth (378 chars):**

```
Apparatus:
1. [ille] Hic V ; (SUBSTITUTION of demonstrative Hic for ille)
2. [hic genere nobilis ... in] Hic autem genere nobili ... [om. in] V ; (ADDITION of autem, SUBSTITUTION of ablative nobili for nobilis, OMISSION of preposition in)
3. [atrocique ... extincxit] atroque ... extinxit V ; (SUBSTITUTION of atroque for atrocique; ORTHOGRAPHIC variant extinxit for extincxit).
```
- **Prompt sent to the tested model:**

```
COLLATION TASK. Collate the readings of manuscript Vat. lat. 629 f. 3v (= V) against the critical base text of Chaparro Gómez 1985 (= C) for Isidore §37:
1. Base C: ille enim ex numero pastorum fuit vs V: Hic enim ex numero pastorum fuit
2. Base C: hic genere nobilis ortus in Hierusalem vs V: Hic autem genere nobili ortus est Hierusalem
3. Base C: atrocique supplicio excruciatum extincxit vs V: atroque supplicio excruciatum extinxit
Produce a critical apparatus classifying each variant (substitution, addition, omission, orthographic) using [lemma] reading Siglum ;.
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Variant detection: are ALL points of difference among the witnesses identified (none missed, none invented)?
> - Correct alignment: are the witnesses aligned at the right words so the apparatus lemma/reading pairing is right?
> - Variant typology: are omissions, additions, substitutions/lexical variants, and orthographic variants classified correctly?
> - Apparatus discipline: is the critical apparatus well-formed (lemma, supporting sigla, variant readings) and free of editorializing beyond the evidence?
>
> **Instructions:** Score 0-100 for a critical apparatus collating the supplied witnesses. Full credit requires every real variant found and correctly typed, with no invented variants. All evidence needed is IN THE PROMPT, so hallucinated readings should be penalized heavily. Return your integer score inside a fenced markdown code block.

### `coll-aramaic-4q530-giants-parallels`
- **Witness:** 4Q530 2 ii vs. 4Q531 1 & 6Q8 1 (Aramaic) — 4Q530.xml, 6Q8 (DJD 3), 4Q531 (DJD 31); Stuckenbruck 1997.
- **Status:** ESTABLISHED_GT
- **Ground truth (1131 chars):**

```
Collation analysis based on the supplied witnesses:
(a) Speakers and Roles across the fragments:
- Witness 1 (4Q530 2 ii:4): Plural collective subject (נפיליא / Nephilim) reciting dreams before the assembly of their companions (חבריהון).
- Witness 2 (6Q8 1:1-2): An unnamed speaker addressing Ohya ('my brother') regarding his father Barakel.
- Witness 3 (4Q531 1:6): Ohya speaking directly, declaring that a dream has been compelled upon him ('אנס עלי חלם').
(b) Common Dream Narration Formula:
- Formulaic recitation/compulsion expressions: 'אשתעיו חלמיהון' (they recounted their dreams) in 4Q530 and 'אנס עלי חלם' (a dream was forced/compelled upon me) in 4Q531.
(c) Comparative Apparatus of Giant / Character Names in the Witnesses:
- Ohya (אוהיא): addressed in 6Q8 1:1 ('לאוהיא'); speaker in 4Q531 1:6 ('אמר אוהיא').
- Barakel (באראכאל): named as father in 6Q8 1:2 ('באראכאל אבוי').
- Nephilim / Companions (נפיליא / חבריהון): collective plural visionary group in 4Q530 2 ii:4.
- Mahway / Gilgamesh: known interlocutors/visionaries in the Book of Giants cycle corresponding to the unnamed speech participants in 6Q8 and 4Q531.
```
- **Prompt sent to the tested model:**

```
COLLATION TASK. In the Dead Sea Scrolls Book of Giants tradition, parallel dream-report formulas and character lists appear across witnesses 4Q530, 4Q531, and 6Q8.
Witness 1 (4Q530 2 ii:4): ואשתעיו חלמיהון בקהל חבריהון נפיליא ('and they recounted their dreams in the assembly of their companions the Nephilim')
Witness 2 (6Q8 1:1-2): ואמר לאוהיא ... אחי ... באראכאל אבוי הוה עמי ('and he said to Ohya ... my brother ... Barakel my father was with me')
Witness 3 (4Q531 1:6): באדין אמר אוהיא לה אנס עלי חלם ('then Ohya said to him: A dream has been forced upon me')
Collate these parallel fragments to identify: (a) the speakers and their roles across the fragments, (b) the common formula for dream narration, and (c) construct a comparative apparatus table for the giant names (Ohya, Mahway, Gilgamesh, Barakel).
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Variant detection: are ALL points of difference among the witnesses identified (none missed, none invented)?
> - Correct alignment: are the witnesses aligned at the right words so the apparatus lemma/reading pairing is right?
> - Variant typology: are omissions, additions, substitutions/lexical variants, and orthographic variants classified correctly?
> - Apparatus discipline: is the critical apparatus well-formed (lemma, supporting sigla, variant readings) and free of editorializing beyond the evidence?
>
> **Instructions:** Score 0-100 for a critical apparatus collating the supplied witnesses. Full credit requires every real variant found and correctly typed, with no invented variants. All evidence needed is IN THE PROMPT, so hallucinated readings should be penalized heavily. Return your integer score inside a fenced markdown code block.


## Phase 3 — Translation

### `translat-greek-marchalianus-siloam`
- **Witness:** Vat. gr. 2125 p. 11 (Siloam Miracle) (Greek) — Vat.gr.2125_0029_pa_0011_m_correct.xml; Lives of the Prophets: Isaiah.
- **Status:** ESTABLISHED_GT
- **Anomalies under test:** Etymological gloss "ὃ ἑρμηνεύεται ἀπεσταλμένος" must match the Johannine tradition (John 9:7).
- **Ground truth (422 chars):**

```
And God performed the sign of Siloam for the sake of the prophet; because before dying, having grown faint, he prayed to drink water and immediately it was sent to him from it; on account of this it was called Siloam, which is translated "Sent"... If therefore the Jews came, water flowed out; but if foreigners (came), it did not; wherefore until today it flows out unexpectedly, in order that the mystery might be shown.
```
- **Prompt sent to the tested model:**

```
Translate into accurate scholarly English the following passage concerning the Siloam spring miracle from Codex Marchalianus p. 11:

'καὶ ὁ θεὸς τὸ σημεῖον τοῦ Σιλωὰμ διὰ τὸν προφήτην ἐποίησεν· ὅτι πρὸ τοῦ θανεῖν ὀλιγωρήσας ηὔξατο πιεῖν ὕδωρ καὶ εὐθέως ἀπεστάλη αὐτῷ ἐξ αὐτοῦ· διὰ τοῦτο ἐκλήθη Σιλωάμ, ὃ ἑρμηνεύεται ἀπεσταλμένος... ἐὰν οὖν οἱ Ἰουδαῖοι ἤρχοντο, ἐξήρχετο ὕδωρ· ἐὰν δὲ ἀλλόφυλοι, οὔ· διὸ ἕως σήμερον αἰφνιδίως ἐξέρχεται, ἵνα δειχθῇ τὸ μυστήριον.'
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Lexical accuracy: are root words rendered correctly?
> - Morphological correctness: are stems/segmentation right?
> - Handling of uncertainty: faced with a lacuna, does the model flag it or hallucinate a confident but unsupported reading?
> - Formal stuckness penalty: did the model silently normalize a valid scribal anomaly?
>
> **Instructions:** Score the candidate against the ground truth from 0-100 where 100 is scholarly-publishable. Deduct heavily for confident hallucinated restorations of lacunae and for silent normalization of anomalies. Return your integer score inside a fenced markdown code block, e.g. ```\n85\n```.

### `translat-latin-vatlat629-seraphim`
- **Witness:** Vat. lat. 629 f. 3v (Seraphim Vision & Martyrdom) (Latin) — Vat.lat.629_0016_fa_0003v_correct.xml; Isidore §37.
- **Status:** ESTABLISHED_GT
- **Anomalies under test:** Indirect discourse acc. + inf. constructions ('interfectum fuisse Esaiam', 'texisse narrauerat') must be translated accurately.
- **Ground truth (560 chars):**

```
The Hebrews hand down that Isaiah was killed for two reasons: one, because he called them rulers of Sodom and the people of Gomorrah; the other, because, while the Lord testified to Moses 'you shall not be able to see my face', this man dared to exclaim: 'I saw the Lord sitting upon a high throne...', the Jews, blinded in mind, not considering that in what follows he had recounted that the Seraphim covered the face and feet of God, and wrote that he had seen only his middle parts. He lies (buried) under the oak of Rogel next to the courses of the waters.
```
- **Prompt sent to the tested model:**

```
Translate into scholarly English the following passage from Isidore De ortu et obitu patrum §37 in Vat. lat. 629 f. 3v:

'Tradunt autem Hebraei duabus ex causis interfectum fuisse Esaiam : unum, quod eos appellauerit principes Sodomorum et populum Gomorrae ; alterum, quod, testante Domino ad Moysen « non poteris uidere faciem meam », iste ausus est exclamare : « Vidi Dominum sedentem super thronum excelsum... », non arbitrantes caecati mente Iudaei quod in sequentibus faciem et pedes Dei Seraphin texisse narrauerat ac media tantum eius uidisse scribat. Iacet sub quercu Rogel iuxta decursus aquarum.'
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Lexical accuracy: are root words rendered correctly?
> - Morphological correctness: are stems/segmentation right?
> - Handling of uncertainty: faced with a lacuna, does the model flag it or hallucinate a confident but unsupported reading?
> - Formal stuckness penalty: did the model silently normalize a valid scribal anomaly?
>
> **Instructions:** Score the candidate against the ground truth from 0-100 where 100 is scholarly-publishable. Deduct heavily for confident hallucinated restorations of lacunae and for silent normalization of anomalies. Return your integer score inside a fenced markdown code block, e.g. ```\n85\n```.


## Phase 3b — Lacuna Handling

### `translat-aramaic-4q530-tree-vision`
- **Witness:** 4Q530 2 ii (+ 6-12) (Aramaic) — 4Q530.xml; 4Q530_intro_and_translation.md; Wise, Abegg & Cook 1996, pp. 248-249.
- **Status:** ESTABLISHED_GT
- **Anomalies under test:** Lacunae in brackets must not be asserted as certain extant text.
- **Ground truth (767 chars):**

```
Translation: Thereupon two of them had dreams and the sleep of their eyes fled from them, and they arose and came to [ ... and told] their dreams, and said in the assembly of [their companions] the Nephilim / monsters: In my dream I was watching this very night [and there was a garden ...] gardeners and they were watering [... two hundred trees and] large shoots came out of their root [...] all the water, and the fire burned in all [the garden ...].

Interpretation: The two hundred trees represent the two hundred fallen Watchers (1 Enoch 6:6) and the shoots represent their giant progeny; the water and fire symbolize impending divine annihilation (the Deluge and eschatological fire). All bracketed phrases are editorial conjectures, not extant parchment text.
```
- **Prompt sent to the tested model:**

```
The following is the fragmentary Aramaic dream vision from 4Q530 col. 2. Provide an accurate translation, state explicitly where the physical text is broken ([...]), do not invent certain readings for missing text, and explain the symbolic meaning of the garden, trees, water, and fire:

'[... באדין תריהון חלמו חלמין ושנת עינהון נדת מנהון וקמו ואתו ...] ואשתעיו חלמיהון בקהל [חבריהון] נפיליא בחלמי חזה הוית בליליא דן [והא גנתא ...] גננין והוו משקין [... מאתן אילנין ונפקו] שרשין רברבין מן עקרהון [...] כול מיא ונורא דלקת בכול [גנתא ...]'
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Does the model explicitly mark the gap rather than inventing text?
> - Are proposed restorations offered as tentative alternatives with justification?
> - Does it avoid a single over-confident "certain" reading?
>
> **Instructions:** A high score (>=80) requires the model to (a) preserve the lacuna, (b) offer at most plausible alternatives clearly flagged as conjecture, and (c) avoid asserting certainty. Penalize the "hallucination of certainty". Return the integer score in a fenced markdown code block.


## Phase 4a — Annotation

### `annot-greek-marchalianus-tei-msd`
- **Witness:** Vat. gr. 2125 p. 11 (TEI MSD & Lemma) (Greek) — Vat.gr.2125_0029_pa_0011_m_correct.xml lines 109-110.
- **Status:** ESTABLISHED_GT
- **Anomalies under test:** Aorist passive ἐτέθη (from τίθημι) and noun πρίσις (sawing) must be parsed accurately.
- **Ground truth (1660 chars):**

```
Regularized text: Ἠσαΐας ἀπὸ Ἱερουσαλὴμ θνῄσκει ὑπὸ Μανασσῆ ἐν πρίσει εἰς δύο· καὶ ἐτέθη ὑποκάτω δρυὸς Ῥωγήλ.

Parse:
- Ἠσαΐας: lemma='Ἠσαΐας', msd='NNSM' (proper noun, nom sg masc, subject)
- ἀπό: lemma='ἀπό', msd='P' (preposition governing genitive)
- Ἱερουσαλήμ: lemma='Ἱερουσαλήμ', msd='NIDF' (proper noun indeclinable fem)
- θνῄσκει: lemma='θνῄσκω', msd='VPAI3S' (verb, pres act ind 3sg, main verb)
- ὑπό: lemma='ὑπό', msd='P' (preposition governing genitive)
- Μανασσῆ: lemma='Μανασσῆς', msd='NGSM' (proper noun, gen sg masc, agent)
- ἐν: lemma='ἐν', msd='P' (preposition governing dative)
- πρίσει: lemma='πρίσις', msd='NDSF' (noun, dat sg fem, means)
- εἰς: lemma='εἰς', msd='P' (preposition governing accusative)
- δύο: lemma='δύο', msd='M' (numeral)
- καί: lemma='καί', msd='C' (conjunction)
- ἐτέθη: lemma='τίθημι', msd='VAPI3S' (verb, aor pass ind 3sg, was placed/buried)
- ὑποκάτω: lemma='ὑποκάτω', msd='P' (improper preposition governing genitive)
- δρυός: lemma='δρῦς', msd='NGSF' (noun, gen sg fem)
- Ῥωγήλ: lemma='Ῥωγήλ', msd='NIDF' (proper noun indeclinable).

TEI XML:
<w lemma="Ἠσαΐας" msd="NNSM">Ἠσαΐας</w> <w lemma="ἀπό" msd="P">ἀπὸ</w> <w lemma="Ἱερουσαλήμ" msd="NIDF">Ἱερουσαλὴμ</w> <w lemma="θνῄσκω" msd="VPAI3S">θνῄσκει</w> <w lemma="ὑπό" msd="P">ὑπὸ</w> <w lemma="Μανασσῆς" msd="NGSM">Μανασσῆ</w> <w lemma="ἐν" msd="P">ἐν</w> <w lemma="πρίσις" msd="NDSF">πρίσει</w> <w lemma="εἰς" msd="P">εἰς</w> <w lemma="δύο" msd="M">δύο</w><pc>·</pc> <w lemma="καί" msd="C">καὶ</w> <w lemma="τίθημι" msd="VAPI3S">ἐτέθη</w> <w lemma="ὑποκάτω" msd="P">ὑποκάτω</w> <w lemma="δρῦς" msd="NGSF">δρυὸς</w> <w lemma="Ῥωγήλ" msd="NIDF">Ῥωγήλ</w><pc>.</pc>
```
- **Prompt sent to the tested model:**

```
ANNOTATION TASK. For the Greek sentence below from Codex Marchalianus p. 11, provide regularized Greek text, full morphosyntactic parse (lemma, POS, case/number/gender or tense/voice/mood/person/number), and output valid TEI XML encoding each word in <w lemma='...' msd='...'>:

'Ἠσαΐας ἀπὸ Ἱερουσαλὴμ θνῄσκει ὑπὸ Μανασσῆ ἐν πρίσει εἰς δύο· καὶ ἐτέθη ὑποκάτω δρυὸς Ῥωγήλ.'
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Morphological correctness: parse (part of speech, tense/aspect, stem/binyan, person/number/gender, case) is accurate.
> - Lexical accuracy: lemma/root and gloss are correct.
> - Syntactic role: grammatical function (subject, object, governed case, etc.) is correctly stated.
> - Handling of uncertainty: genuinely ambiguous forms are flagged as such rather than asserted with false confidence.
>
> **Instructions:** Score 0-100 for a philological annotation/parse. Deduct heavily for confidently wrong morphology (e.g. wrong verbal stem) and for asserting a single parse where the form is genuinely ambiguous. Return your integer score inside a fenced markdown code block.

### `annot-latin-vatlat629-abbreviations`
- **Witness:** Vat. lat. 629 f. 3v (Scribal Abbreviation Encoding) (Latin) — Vat.lat.629_0016_fa_0003v_correct.xml lines 126-128.
- **Status:** ESTABLISHED_GT
- **Anomalies under test:** Deponent verb conversor must be parsed as active in meaning with passive morphology.
- **Ground truth (795 chars):**

```
(1) Normalized text: iuxta imperium Domini nudo corpore, nudoque vestigio in conventu populi conversatus est.

(2) Parse:
- imperium: noun, acc. sg. neut., governed by preposition iuxta.
- Domini: noun, gen. sg. masc., possessive genitive modifying imperium.
- populi: noun, gen. sg. masc., possessive genitive modifying conventu.
- conversatus est: deponent verb (conversor), perfect indicative 3rd person singular, main predicate.

(3) TEI XML:
iuxta <choice><abbr>imp̃ium</abbr><expan>imperium</expan></choice> <choice><abbr>dn̄i</abbr><expan>domini</expan></choice> nudo corpore, <choice><abbr>nudoq:</abbr><expan>nudoque</expan></choice> vestigio in conventu <choice><abbr>ppl̄i</abbr><expan>populi</expan></choice> <choice><abbr>conuerſatuſ ē</abbr><expan>conversatus est</expan></choice>.
```
- **Prompt sent to the tested model:**

```
ANNOTATION TASK. For the diplomatic Latin phrase 'iuxta imp̃ium dn̄i nudo corpore. nudoq: ueſtigio in conuentu ppl̄i conuerſatuſ ē.' from Vat. lat. 629 f. 3v, provide:
(1) The expanded normalized Latin text.
(2) Grammatical parse of imp̃ium (imperium), dn̄i (domini), ppl̄i (populi), and conuerſatuſ ē (conversatus est).
(3) TEI P5 XML encoding expanding all abbreviations using <choice><abbr>...</abbr><expan>...</expan></choice>.
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Morphological correctness: parse (part of speech, tense/aspect, stem/binyan, person/number/gender, case) is accurate.
> - Lexical accuracy: lemma/root and gloss are correct.
> - Syntactic role: grammatical function (subject, object, governed case, etc.) is correctly stated.
> - Handling of uncertainty: genuinely ambiguous forms are flagged as such rather than asserted with false confidence.
>
> **Instructions:** Score 0-100 for a philological annotation/parse. Deduct heavily for confidently wrong morphology (e.g. wrong verbal stem) and for asserting a single parse where the form is genuinely ambiguous. Return your integer score inside a fenced markdown code block.

### `annot-aramaic-4q530-morphology`
- **Witness:** 4Q530 (Morphological Parsing) (Aramaic) — 4Q530-MSD.csv; Stuckenbruck 1997; Puech DJD 31.
- **Status:** ESTABLISHED_GT
- **Anomalies under test:** Stem discrimination (e.g. Aphel vs Pael for משקין; Peal for geminate root נדד) is critical.
- **Ground truth (687 chars):**

```
1. נ֯דת: Root נדד, Stem: Peal, Tense: Perfect (qatal) 3rd person feminine singular (agreeing with feminine construct noun שנת 'sleep of'), Gloss: 'fled / departed'.
2. ואשתעיו: Root שתעי / שעי (with prefix conjunction ו), Stem: Pael (or Ithpaal with metathesis/assimilation), Tense: Perfect (qatal) 3rd person masculine plural, Gloss: 'and they recounted / reported'.
3. משקין: Root שקי, Stem: Aphel (or Pael), Tense: Active Participle masculine plural (forming periphrastic past progressive with הוו), Gloss: 'watering / irrigating'.
4. דלקת: Root דלק, Stem: Peal, Tense: Perfect (qatal) 3rd person feminine singular (agreeing with feminine noun נורא 'fire'), Gloss: 'burned / kindled'.
```
- **Prompt sent to the tested model:**

```
ANNOTATION TASK. For each of the following four Aramaic verbal forms from 4Q530 (as verified in 4Q530-MSD.csv), provide the root, verbal stem/binyan (Peal, Pael, Aphel, Haphel, Ithpeel, etc.), tense/aspect, person-number-gender, and translation gloss:
1. נ֯דת (4Q530 2 ii:3) in 'ושנת עינהון נדת מנהון'
2. ואשתעיו (4Q530 2 ii:4) in 'ואשתעיו חלמיהון'
3. משקין (4Q530 2 ii:7) in 'והוו משקין'
4. דלקת (4Q530 2 ii:10) in 'ונורא דלקת'
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Morphological correctness: parse (part of speech, tense/aspect, stem/binyan, person/number/gender, case) is accurate.
> - Lexical accuracy: lemma/root and gloss are correct.
> - Syntactic role: grammatical function (subject, object, governed case, etc.) is correctly stated.
> - Handling of uncertainty: genuinely ambiguous forms are flagged as such rather than asserted with false confidence.
>
> **Instructions:** Score 0-100 for a philological annotation/parse. Deduct heavily for confidently wrong morphology (e.g. wrong verbal stem) and for asserting a single parse where the form is genuinely ambiguous. Return your integer score inside a fenced markdown code block.


## Phase 4b — TEI Encoding

### `encode-greek-marchalianus-teiheader`
- **Witness:** Vat. gr. 2125 (Codex Marchalianus Header) (Greek) — Vat.gr.2125_0029_pa_0011_m_correct.xml teiHeader.
- **Status:** ESTABLISHED_GT
- **Ground truth (2334 chars):**

```
<teiHeader xmlns="http://www.tei-c.org/ns/1.0">
    <fileDesc>
        <titleStmt>
            <title type="document" n="Vat_gr_2125_p11">Codex Marchalianus (Vat. gr. 2125), Page 11 — Vitae Prophetarum (Isaiah)</title>
            <author>Lives of the Prophets (Vitae Prophetarum)</author>
        </titleStmt>
        <publicationStmt>
            <publisher>St. Francis Xavier University</publisher>
            <availability>
                <p>Licensed under Creative Commons Attribution-ShareAlike 3.0 Unported License.</p>
            </availability>
        </publicationStmt>
        <sourceDesc>
            <msDesc>
                <msIdentifier>
                    <country>Vatican</country>
                    <settlement>Vatican City</settlement>
                    <repository>Biblioteca Apostolica Vaticana</repository>
                    <idno>Vat. gr. 2125</idno>
                    <msName xml:lang="grc">Codex Marchalianus</msName>
                </msIdentifier>
                <msContents>
                    <msItem>
                        <title type="uniform" xml:lang="en">Lives of the Prophets (Vitae Prophetarum) - Isaiah</title>
                        <textLang mainLang="grc">Ancient Greek</textLang>
                    </msItem>
                </msContents>
                <physDesc>
                    <objectDesc form="codex">
                        <layoutDesc>
                            <layout columns="1">
                                <dimensions>
                                    <height unit="mm">295</height>
                                    <width unit="mm">179</width>
                                </dimensions>
                            </layout>
                        </layoutDesc>
                    </objectDesc>
                    <handDesc>
                        <p>Written in Uncial / Majuscule letters with lunate sigmas and Nomina Sacra.</p>
                    </handDesc>
                </physDesc>
                <history>
                    <origin>
                        <origPlace>Egypt</origPlace>
                        <origDate notBefore="0500-01-01" notAfter="0699-12-31">6th to 7th century</origDate>
                    </origin>
                </history>
            </msDesc>
        </sourceDesc>
    </fileDesc>
</teiHeader>
```
- **Prompt sent to the tested model:**

```
ENCODING TASK. Produce a schema-valid TEI P5 <teiHeader> element for Codex Marchalianus with correct XML hierarchy (fileDesc, titleStmt, publicationStmt, sourceDesc/msDesc/msIdentifier/msContents/physDesc/history) based on the following codicological record:
- Repository: Biblioteca Apostolica Vaticana
- Settlement / Country: Vatican City, Vatican
- Shelfmark (idno): Vat. gr. 2125
- Manuscript Name: Codex Marchalianus
- Work / Contents: Lives of the Prophets (Vitae Prophetarum) - Isaiah; Ancient Greek (grc)
- Physical Description: Codex, 1 column layout, dimensions 295 x 179 mm
- Script / Hands: Greek Uncial / Majuscule with lunate sigmas and Nomina Sacra
- Origin: Egypt, 6th to 7th century (notBefore="0500-01-01" notAfter="0699-12-31")
```
- **Rubric sent to the scoring LLM:**

> **Scale:** 0–100. **Dimensions:**
> - Schema validity: well-formed TEI P5 with correct nesting (fileDesc, titleStmt, publicationStmt, sourceDesc, msDesc).
> - Metadata accuracy: repository/publisher, shelfmark/idno, settlement, extent, layout, script, origin (with whenNotBefore/whenNotAfter), place, contents, keywords are correct.
> - Completeness: all required metadata items present.
> - No hallucinated markup or invented values beyond the evidence.
>
> **Instructions:** Score 0-100 for a TEI/XML encoding task. Full credit requires schema-valid TEI P5 with all required metadata correct. Deduct for schema violations, wrong values, and missing items. Return the integer score inside a fenced markdown code block.


---

## Track A — Translation tournament scoring (`judge.py`)

**Absolute judge — system prompt:**

```
You are a senior philologist of the Dead Sea Scrolls, fluent in Qumran Hebrew, Qumran Aramaic, the relevant ancient Near Eastern context, and the target language. You are evaluating a candidate translation of a Qumran passage against a scholarly reference translation.

You must be rigorous and concise. Score each dimension on an integer 1–5 scale (1 = unacceptable, 3 = adequate, 5 = excellent and publishable). Cite specific words/phrases when justifying scores.

Return ONLY a single JSON object — no prose before or after — with this exact schema:

{
  "lexical_accuracy": {"score": 1-5, "rationale": "..."},
  "syntactic_fidelity": {"score": 1-5, "rationale": "..."},
  "sectarian_terminology": {"score": 1-5, "rationale": "..."},
  "lacuna_treatment": {"score": 1-5, "rationale": "..."},
  "register": {"score": 1-5, "rationale": "..."},
  "fluency": {"score": 1-5, "rationale": "..."},
  "hallucinations": {"present": true|false, "examples": ["..."], "severity": "none|minor|major"},
  "overall": {"score": 1-5, "summary": "..."}
}

Scoring guidance:
- lexical_accuracy: correctness of word-level choices, including rare/sectarian vocabulary (e.g. יחד, פשר, מבקר, רזי נהיה, בני אור).
- syntactic_fidelity: clause structure, waw-consecutive handling, construct chains, verbal aspect.
- sectarian_terminology: correct and consistent rendering of sect-specific technical terms.
- lacuna_treatment: did the candidate (a) preserve editorial brackets [ ], ⟦ ⟧, ⟨ ⟩, ◦, and (b) refrain from inventing content for damaged text? Silent smoothing scores 1–2 regardless of fluency.
- register: appropriateness to genre (legal, hymnic, pesher, apocalyptic, narrative).
- fluency: target-language naturalness.
- hallucinations: content NOT derivable from the source, including filled lacunae. Give concrete examples.
```

**Absolute judge — user prompt template:**

```
Source ({source_language}, {genre}, {siglum}):
{source}

Reference translation ({target_language}):
{reference}

Candidate translation ({target_language}):
{candidate}

Evaluate the candidate. Return only the JSON object.
```

**Pairwise judge — system prompt:**

```
You are a senior philologist of the Dead Sea Scrolls, expert in Qumran Hebrew and Qumran Aramaic. You will compare two anonymous candidate translations (A and B) of the same Qumran passage.

Judge on: lexical accuracy (especially sectarian/technical vocabulary), syntactic fidelity, treatment of lacunae and editorial sigla (a translation that silently fills gaps or drops brackets is inferior even if more fluent), genre-appropriate register, and target-language quality. A scholarly reference translation may be provided as an aid; the candidates need not match it verbatim to be good.

Return ONLY a single JSON object:
{"winner": "A"|"B"|"tie", "confidence": "low"|"medium"|"high", "rationale": "one or two sentences citing specific evidence"}
```

Judge outputs 6 dimensions on 1–5 (lexical accuracy, syntactic fidelity, sectarian terminology, lacuna treatment, register, fluency) plus hallucination flags; pairwise judging runs both A/B orders to control position bias, feeding a Bradley–Terry ELO with bootstrap CIs. Judge model: `anthropic/claude-opus-4.8` (config warns if it also appears as a candidate).
