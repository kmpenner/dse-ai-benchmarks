# Findings: Latin Vision Benchmark, Vat.lat.629 f. 3v (Isidore, *De ortu et obitu Patrum* §36–40)

> **[2026-08-29] Re-scored; headline figures unchanged.** Runs re-scored with the
> corrected scorer (content-filter exclusion; the §6 incomplete-capture rule is
> now enforced in code — §1's truncated rows are `scored: false` in the
> regenerated `_scored.json` files and must not be ranked). §6's open question on
> Gemini 3.1 Pro's WER 1.000 remains open (re-confirmed on re-score). Numbers of
> record: `PROVENANCE.md` §2.

**Evidence memo for the RESAC 2026 paper** — Ken Penner & Demarquis Moss, SSHRC IDG *Generative AI in Digital Humanities Research Methodology*. Updated 2026-08-21.

**Latest Run:** `benchmark_results/latin_isidore_transcriptions_results_1787330166.json` (17 models, one page, temperature 0, identical system prompt [`prompts/latin_isidore.md`](../prompts/latin_isidore.md), 300 s timeout).  
**Scoring:** [`score_transcription.py --profile latin`](../score_transcription.py) → [`benchmark_results/latin_isidore_transcriptions_results_1787330166_scored.json`](../benchmark_results/latin_isidore_transcriptions_results_1787330166_scored.json).  
**Consensus analysis:** [`consensus_check.py --profile latin`](../consensus_check.py).  

**Ground truth:** Diplomatic TEI transcription of the whole page, both columns, `transcription/data/raw_xml/Vat.lat.629_0016_fa_0003v.xml` (Ken Penner & Demarquis Moss), staged as [`latin_isidore_transcriptions.json`](../latin_isidore_transcriptions.json). **3,697 comparable characters, 678 word tokens.** Critical edition for reference: Chaparro Gómez 1985, 163–169.

---

## 1. Headline Results (Full 17-Model Suite)

Two CERs are reported, and the difference between them is the point:
- **CER** is the *letter-identification* layer: case folded, combining marks (titulus/macron) stripped, and palaeographic allographs folded to their modern equivalents — long ſ → s, dotless ı → i, r rotunda ꝛ → r, u/v and i/j merged, ligatures expanded. This is the direct analogue of the Greek scorer's collapse of all four sigma forms: a model that renders the scribe's letterform faithfully has read the letter correctly and is not charged for the rendering.
- **CER (strict)** keeps every abbreviation mark. The gap between the two columns is the model's **abbreviation fidelity**.

WER is computed on the diplomatic layer directly — unlike Greek majuscule, this scribe divides his words — so it charges for word division across line breaks as well as for lexical error.

| Rank | Model | CER (Letter ID) | CER (strict) | WER | Length Ratio | Cost ($) | Elapsed Time (s) | Status / Notes |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | **`google/gemini-3.1-pro-preview`** | **0.042** | 0.111 | 1.000 | **1.004** | $0.2489 | 139.2 s | **Top Letter Accuracy** (Full 2-column capture) |
| 2 | **`google/gemini-3.7-flash`** | **0.058** | 0.104 | **0.289** | **1.002** | **$0.0083** | **36.6 s** | **High Precision & Fast** |
| 3 | **`meta/muse-spark-1.2`** | **0.069** | 0.128 | **0.254** | **1.005** | **$0.0312** | **50.4 s** | **Lowest WER & Clean Layout** |
| 4 | **`x-ai/grok-4.6`** | **0.090** | 0.154 | **0.335** | **0.998** | **$0.0426** | 104.4 s | **Outstanding Debut** (Clean word division) |
| 5 | **`anthropic/claude-opus-5`** | **0.098** | 0.172 | **0.329** | 1.062 | $0.2552 | 137.8 s | Full double-column capture |
| 6 | **`openai/gpt-5.5`** | **0.105** | 0.165 | **0.302** | 1.052 | $0.2407 | 105.8 s | High lexical fidelity |
| 7 | **`xiaomi/mimo-v2.5`** | **0.186** | 0.248 | **0.504** | **1.071** | **$0.0043** | 217.2 s | **Best Budget Model** |
| 8 | **`moonshotai/kimi-k3`** | **0.200** | 0.265 | 0.988 | 1.155 | $0.1600 | 194.9 s | Solid letter capture |
| 9 | **`qwen/qwen3.8-max`** | **0.246** | 0.312 | 0.470 | 1.157 | $0.1493 | 439.8 s | Moderate lexical accuracy |
| 10 | **`openai/gpt-5.6-sol`** | 0.705 | 0.705 | 0.997 | 0.352 | $0.0743 | 74.1 s | Partial column capture |
| 11 | **`anthropic/claude-opus-4.8`** | 0.760 | 0.774 | 0.971 | 0.411 | $0.0480 | 18.7 s | Truncated run (partial page) |
| 12 | **`qwen/qwen3-vl-235b-thinking`** | 0.788 | 0.802 | 0.988 | 0.336 | $0.0047 | 16.8 s | Partial column capture |
| 13 | **`openai/gpt-5.6-luna`** | 0.841 | 0.849 | 0.976 | 0.198 | **$0.0034** | **12.6 s** | Partial column capture |
| 14 | **`openai/gpt-4o`** | 0.962 | 0.962 | 0.999 | 0.039 | $0.0034 | 4.9 s | Truncated sample |
| 15 | **`openai/gpt-5.6-terra`** | 0.963 | 0.965 | 0.963 | 0.037 | $0.0352 | 17.4 s | Truncated sample |
| — | **`google/gemini-2.5-pro`** | — | — | — | — | — | 339.2 s | **ERROR** (504 Gateway Timeout) |
| — | **`google/gemma-4-31b-it:free`** | — | — | — | — | — | 2.8 s | **RATE_LIMITED** (429) |

---

## 2. The Allograph Trap: A Metric Choice That Reorders the Field

Models transcribing in palaeographic characters (such as dotless `ı`, `ꝛ` for r rotunda, `ẏ`, `ł`, and long `ſ`) require allograph folding to fairly measure letter identification. Under a naive fold — case and combining marks only — models using faithful scribal ligatures score poorly, whereas with allographs folded they score in the top tier.

**For diplomatic transcription, the evaluation metric is itself an editorial theory, and it must be declared before the numbers mean anything.** A benchmark that does not state its folding rules is not reporting a model property.

---

## 3. Failure Modes & Behavioral Observations

1. **Section Isolation:** With the updated section splitter isolating diplomatic layers from normalized editions, models outputting structured multi-tier editions (**`meta/muse-spark-1.2`** at **`CER = 0.069`**, **`WER = 0.254`**, and **`google/gemini-3.7-flash`** at **`CER = 0.058`**) show exceptional full-page accuracy.
2. **Clean Word Division in `x-ai/grok-4.6`:** Grok 4.6 scored **`CER = 0.090`** and **`WER = 0.335`**, transcribing both columns fully with high abbreviation awareness at low cost ($0.0426).
3. **Budget Vision Efficiency in `xiaomi/mimo-v2.5`:** MiMo v2.5 achieved **`CER = 0.186`** and completed both columns for less than half a cent ($0.0043), making it the most cost-effective open model on Latin minuscule.
4. **Degenerate Looping in GPT-4o:** Reaches short output ceiling with repetitive truncation.
5. **Long-s Collapse in Qwen 3 VL:** Emitted standard `f` for long `ſ` (`tranfiu fuo diuifus` for `tranſitu ſuo diuiſuſ`).

---

## 4. Convergent Disagreement: 96 Characters (2.6%) for Human Re-Collation

Under the project's human-in-the-loop protocol, loci where ≥3 models agree with each other *against* the human transcription are routed back to the editor:

### (a) Transcription slips in the human ground truth — to be corrected in TEI:
| Ground Truth | Convergent Reading | Models | Chaparro 1985 | Assessment |
|---|---|:---:|---|---|
| `iertin` | `ierlm` | 6/6 | *Hierusalem* | Scribe's contraction for Jerusalem (`ierlḿ`). |
| `daniel de i ribu uida` | `daniel de tribu iuda` | 6/6 | *Danihel, de tribu Iuda* | Two adjacent letter slips (`t`→`i`, transposed `i`). |
| `coipore` | `corpore` | 6/6 | *corpore castus* | Typo; transcribed correctly elsewhere. |
| `baliloné` | `babilone` | 6/6 | *in Babylone* | Typo. |
| `caeleſtui` | `caelesti` | 6/6 | *caelestium* | Typo. |
| `Preſeuiſ` | `presciuis` | 5/6 | *praescius* | Missed `sci` ligature. |
| `ieiunuf` | `ieiuniis` | 5/6 | *ieiuniis* | Typo plus long-s error. |
| `caſutate` | `castitate` | 5/6 | *castitatem* | Typo. |
| `ſrmulacru` | `simulacru` | 5/6 | *simulacrum* | Typo. |
| `elisit oracone` | `elisit dracone` | 5/6 | *draconem* | Typo. |
| `ou afpectu` | `et aspectu` | 5/6 | *et aspectu* | Misread tironian *et*. |
| `Terribilif`, `uirtutefum`, `afpectu`, `beliſ f`, `meruitfaementa` | `-s` in each | 5–6/6 | — | Systematic `f`-for-`ſ` keyboard slip. |

### (b) Model normalization against the printed edition:
| Ground Truth | Convergent Reading | Models | Assessment |
|---|---|:---:|---|
| `ezechihel` | `ezechiel` | 6/6 | MS and Chaparro read *Ezechihel*. Models normalize. |
| `conuerti aquas` | `conuertit aquas` | 5/6 | Chaparro prints infinitive *conuerti*. Models supply finite verb. |
| `famem` | `famen` | 5/6 | Needs visual re-collation. |

---

## 5. Associated Corpus Data Files

* **Target Image:** `transcription/Vat.lat.629_0016_fa_0003v.jpg`
* **Master TEI XML Ground Truth:** `transcription/data/raw_xml/Vat.lat.629_0016_fa_0003v.xml`
* **Benchmark Package:** `latin_isidore_transcriptions.json`
* **Complete Scored Results JSON (17 Models):** `benchmark_results/latin_isidore_transcriptions_results_1787330166_scored.json`

---

## 6. Reproducibility: an independent third run of the same page

*Added 2026-08-21. This section reports a separate run and does not modify the analysis above.*

`benchmark_results/latin_isidore_transcriptions_results_1787342463.json` — same page, same prompt, same 17-model roster, temperature 0, run roughly twelve minutes after the run tabulated in §1. Scored with the same `score_transcription.py --profile latin`.

| Model | §1 run (`…1787330166`) | this run (`…1787342463`) | Δ |
|---|---:|---:|---:|
| google/gemini-3.1-pro-preview | 0.042 | 0.041 | ~0 |
| google/gemini-3.7-flash | 0.058 | 0.054 | ~0 |
| x-ai/grok-4.6 | 0.090 | 0.087 | ~0 |
| anthropic/claude-opus-5 | 0.098 | 0.045 | −0.053 |
| openai/gpt-5.5 | 0.105 | 0.076 | −0.029 |
| meta/muse-spark-1.2 | 0.069 | 0.121 | +0.052 |
| qwen/qwen3.8-max | 0.246 | 0.163 | −0.083 |
| **openai/gpt-5.6-sol** | **0.705** | **0.073** | **−0.632** |
| **anthropic/claude-opus-4.8** | **0.760** | **0.052** | **−0.708** |
| **qwen/qwen3-vl-235b-a22b-thinking** | **0.788** | **0.160** | **−0.628** |
| **openai/gpt-5.6-terra** | **0.963** | **0.111** | **−0.852** |
| **google/gemini-2.5-pro** | ERROR (504) | **0.052** | — |
| openai/gpt-5.6-luna | 0.841 | 0.880 | +0.039 |
| xiaomi/mimo-v2.5 | 0.186 | 0.877 (content_filter) | +0.691 |
| openai/gpt-4o | 0.962 | 3.396 | +2.434 |
| moonshotai/kimi-k3 | 0.200 | — (empty, hit length ceiling) | — |

**Temperature 0 is not determinism, and one run does not establish a ranking.**

- The three leaders are stable to ±0.004 across runs. Their positions are real.
- **Five models move by more than 0.6 CER.** In every case the §1 figure reflects a run that stopped early — §1 annotates them "truncated run (partial page)", "partial column capture" — while in this run the same models returned the whole page. Claude Opus 4.8 moves from rank 11 (0.760) to a figure that would place it joint third (0.052); GPT-5.6-sol from 0.705 to 0.073; Gemini 2.5 Pro from a 504 timeout to 0.052.
- The movement is not model quality. It is **whether the response completed**, which is an infrastructure property of the call, not a palaeographic property of the model. A CER computed over a truncated response measures truncation.

### What follows for the paper

1. **Ranks 5–15 of the §1 table should not be published as a ranking.** The stable claim is that a leading group (Gemini 3.1 Pro, Gemini 3.7 Flash, Grok 4.6, and on this run Claude Opus 4.8/5 and Gemini 2.5 Pro) transcribes this page at 0.04–0.09 CER, and that GPT-4o fails degenerately. The ordering inside the middle of the field is run-to-run noise.
2. **Truncated and completed responses must not share a column.** Length ratio already exposes this — every large mover in §1 has a length ratio of 0.04–0.41, i.e. it returned a third of the page or less. A response with a length ratio below ~0.8 should be reported as an incomplete capture, not scored as a transcription.
3. **Runs must be repeated.** Three runs minimum for any model not already at the floor, reporting median and range. The Aramaic infrared run (17 models × 12 units) is single-shot and carries the same caveat.
4. Open question on the §1 table: Gemini 3.1 Pro is listed at WER 1.000 alongside CER 0.042, while Gemini 3.7 Flash shows WER 0.289 at CER 0.058. A WER of 1.000 with near-perfect characters indicates the WER tokenizer found no aligned words — probably a section-splitting artifact on that model's output format rather than a real result. Worth re-checking before the number is published.
