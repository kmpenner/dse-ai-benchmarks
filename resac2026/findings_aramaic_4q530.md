# Findings: Aramaic Vision Benchmark, 4Q530 (4QEnGiants^b ar, *Book of Giants*)

> **[2026-08-29] Partly superseded — re-scored.** The underlying run data is
> unchanged, but three items were corrected by the 2026-08-29 scorer fixes and
> coherence review: (1) Claude Opus 5 is now **0/12 scored, 12 content-blocked**
> (three responses arriving under a `content_filter` cut had been scored as
> transcriptions; their visible content was disciplined abstention prose, not a
> refusal — the §3 characterization simplifies); (2) the §2 "ranked first and
> third" claim is corrected to "first and second" (see `PROVENANCE.md` §4);
> (3) scoreable calls: 91, not 94. The Greek gradient figure in §3 ("Greek
> majuscule 0.064") is withdrawn pending the ground-truth ruling in
> `greek_gt_decision_memo.md`. Authoritative numbers: `PROVENANCE.md` §4 and the
> re-scored `_scored.json`.

**Evidence memo for the RESAC 2026 paper** — Ken Penner & Demarquis Moss, SSHRC IDG *Generative AI in Digital Humanities Research Methodology*. Written 2026-08-21.

Ground truth: diplomatic TEI, `transcription/data/raw_xml/4Q530-1.xml`, with scribal word division taken from `4Q530.txt` (the XML's `<w>` elements are morphemes, not orthographic words). Staged by [`parse_tei_4q530.py`](../parse_tei_4q530.py) → [`aramaic_4q530_transcriptions.json`](../aramaic_4q530_transcriptions.json). **14 units, 707 words, 43 lacunae; 12 units and 692 words benchmarkable.**
Scoring: [`score_transcription.py --profile hebrew`](../score_transcription.py). Consensus: [`consensus_check.py`](../consensus_check.py).

Two pipeline problems had to be solved before a single model could be scored, and both are results in their own right.

---

## 1. Getting the ground truth and the image to describe the same object

**Column vs. fragment.** The transcription is segmented by *reconstructed scroll column*; the photographs are per *physical fragment*. Three ground-truth units therefore correspond to no single photograph. These are now benchmarked against crops of the DJD 31 Planche II composite (`build_composite.py` → `build_column_images.py`), and the XML's `f6` and `f10-12` divs — which cut through the middle of line 3 of column ii — are re-joined on line number, yielding the 24-line column DJD 31 p. 9 describes. This raised the benchmarkable corpus from **89 words to 692 of 707**.

**Morpheme vs. word (Canonical Standard).** The TEI encodes `עלוהי` as `<w>עלו</w> <w>הי</w>`. While valid for the Morphosyntactic Database (MSD) layer, it is incompatible with diplomatic scoring where Qumran scribes divide orthographic words with physical spaces. Per project authority, **`4Q530.txt` is canonical** whenever in conflict with the MSD XML data. Word division and diplomatic character readings are sourced directly from `4Q530.txt`, preserving authentic scribal spacing and resolving morphological encoding artifacts (such as the duplicate determined-state `ה` in col. ii lines 7–8 `גנתה`).

---

## 2. The exposure problem: the colour run measured nothing

The first run (`benchmark_results/aramaic_4q530_transcriptions_results_1787315575.json`, 7 models × 12 units) used the Leon Levy **colour** exposures for the nine single-fragment units. That was an error in the pipeline, and the models caught it before I did.

Dead Sea Scroll ink is read under **infrared**. On the colour plate of frg. 13 the fragment is dark brown, crackled leather carrying a modern stamped inventory number and **no visible ancient script whatsoever**. The paired infrared exposure of the same fragment shows the ink plainly. The colour images are photographs of an object; the infrared images are the scholarly reading surface.

This turned an accidental control into the most diagnostic experiment in the corpus: **seven models were handed nine images with no legible ancient text on them and asked for a diplomatic transcription.**

| Model | produced text | abstained (traces only) | declined as illegible | infrastructure |
|---|---:|---:|---:|---:|
| anthropic/claude-opus-4.8 | **0** | 7 | 2 | 0 |
| openai/gpt-4o | **0** | 2 | 6 | 1 |
| openai/gpt-5.5 | **1** | 5 | 3 | 0 |
| qwen/qwen3-vl-235b-a22b-thinking | **2** | 2 | 5 | 0 |
| google/gemini-3.7-flash | **5** | 4 | 0 | 0 |
| google/gemini-2.5-pro | **8** | 0 | 0 | 1 |
| google/gemini-3.1-pro-preview | **9** | 0 | 0 | 0 |

*"Abstained" = the model returned a transcription consisting entirely of `[...]` and unidentified-trace marks, claiming no letter. "Declined" = the model reported in prose that the image carried no legible script.*

**Gemini 3.1 Pro produced a confident Aramaic transcription for every one of the nine blank images.** On frg. 13 it read `[...]ן° חזין[...]`, described the letters as "clear and well-preserved in the characteristic Herodian square script", and supplied a paragraph of palaeographic argument about whether a descending stroke is a final *nun* or an elongated *waw* — about an image containing no ancient ink. The word it invented, `חזין`/`וחזין` ("visions"), is thematically apt for the Book of Giants: the model is generating from its knowledge of the composition, not from the photograph.

### Why this is the paper's central exhibit

Under the CER leaderboard, **the two models that hallucinated on every blank image ranked first and third**, because CER can only score a model that produces text. Claude Opus 4.8 and GPT-4o, which abstained on every unreadable image — the scholarly correct answer, and the one the system prompt's constraint 9 explicitly invited — appear at the bottom of the table or as "unscored".

A benchmark that reports CER alone does not merely miss this: **it inverts it.** Abstention has to be a scored outcome, not a missing value. The scorer now classifies non-transcriptions into *abstained*, *declined*, *no script*, and *infrastructure failure*, and those categories belong in the headline table beside CER.

This also supplies the concrete answer to "why keep the human in the loop": the failure was invisible from the outputs, which were fluent, technically argued and self-consistent. It was visible from the *image* — which is where the editor is, and the metric is not.

---

## 3. The infrared run: every model fails, and the ranking still misleads

`benchmark_results/aramaic_4q530_ir_transcriptions_results_1787338140.json` — **17 models × 12 units = 204 calls**, infrared exposures for the nine single-fragment units, Planche II composite crops for the three column units, temperature 0, [`prompts/aramaic_4q530.md`](../prompts/aramaic_4q530.md).

| Model | CER | CER extant | WER | Length ratio | Units w/ text | Cost |
|---|---:|---:|---:|---:|---:|---:|
| meta/muse-spark-1.2 | **0.754** | 0.742 | 1.030 | 0.66 | 6/12 | $0.17 |
| moonshotai/kimi-k3 | 0.806 | 0.787 | 1.000 | 0.41 | 8/12 | $2.87 |
| x-ai/grok-4.6 | 0.818 | 0.784 | 0.961 | 0.35 | 5/12 | $0.27 |
| openai/gpt-5.6-sol | 0.839 | 0.829 | 1.000 | 0.26 | 3/12 | $0.56 |
| openai/gpt-4o | 0.844 | 0.815 | 1.000 | 0.38 | 3/12 | $0.71 |
| openai/gpt-5.5 | 0.879 | 0.837 | 0.981 | 0.21 | 7/12 | $1.20 |
| google/gemini-3.7-flash | 0.881 | 0.844 | 0.986 | 0.19 | 11/12 | $0.05 |
| google/gemini-3.1-pro-preview | 0.903 | 0.873 | 0.982 | 0.15 | **12/12** | $0.78 |
| google/gemini-2.5-pro | 0.907 | 0.883 | 1.004 | 0.19 | **12/12** | $0.48 |
| qwen/qwen3.8-max | 0.915 | 0.897 | 0.980 | 0.16 | 11/12 | $0.64 |
| anthropic/claude-opus-4.8 | 0.983 | 0.974 | 0.997 | **0.03** | 7/12 | $0.51 |
| qwen/qwen3-vl-235b-a22b-thinking | 0.985 | 0.984 | 1.000 | 0.02 | 1/12 | $0.09 |
| **anthropic/claude-opus-5** | — | — | — | — | **0/12 — blocked** | $0.49 |
| google/gemma-4-31b-it:free | — | — | — | — | 0/12 — rate-limited | — |
| openai/gpt-5.6-luna, -terra; xiaomi/mimo-v2.5 | 0.86–0.97 | | | | 0–4/12 | |

**Not one model transcribes this manuscript.** The best CER in the field is 0.754 — three of every four characters wrong — and WER is at or near 1.000 for every model in the table: across 204 calls, essentially no word of 4Q530 is transcribed correctly by anyone. The best result on any single unit is CER 0.500 (frg. 15, two words). Infrared raised the best single-model CER from 0.865 to 0.754 and roughly tripled how much text models were willing to produce; it did not make the task tractable.

This is a clean negative result, and it is worth the paper stating plainly: **for fragmentary, lacunose Qumran Aramaic, generative vision models are not at the "human-in-the-loop correction" stage. They are not yet useful at all.** The gradient across the project's three corpora — Latin book hand 0.043, Greek majuscule 0.064, Qumran Aramaic 0.754 — is more than an order of magnitude, and it maps onto physical damage and lacunosity rather than onto script, language, or the volume of training data.

### The ranking inverts again, in the opposite direction

The two models that produced text for all 12 units, Gemini 3.1 Pro and 2.5 Pro, sit **eighth and ninth** on CER. Claude Opus 4.8 sits second from bottom at 0.983 — but its length ratio is 0.03, meaning it transcribed 3% of the expected characters and marked the rest as unidentified traces. Its CER is high because it declined to guess, and CER charges omissions as errors.

Compare with §2: on the *blank* colour images the same production/abstention axis appeared, in the same order. **A model's willingness to produce text is a stable disposition, not a response to what is on the image.** Gemini answered confidently whether or not there was ink; Claude abstained heavily whether or not there was ink. Neither behaviour is informative about legibility, and neither is rewarded correctly by CER: it penalises the abstainer for omissions and pays the hallucinator for volume.

The practical implication for the project's methodology is direct. **Abstention must be reported as its own outcome class**, beside CER, and a benchmark table without it is actively misleading. Of the 204 calls: 94 produced scoreable text, 65 abstained (transcription consisting only of `[...]` and trace marks), 15 declined in prose, 22 failed on infrastructure, 7 answered with no Aramaic, 1 mis-sectioned.

### Content filtering, second vendor, second corpus

**Claude Opus 5 returned `content_filter` on all 12 units — a 100% refusal rate on the Book of Giants.** No fragment was transcribed; the account was billed $0.49 for the refusals.

The Greek run lost Gemini 3.7 Flash to a `PROHIBITED_CONTENT` block on the martyrdom of Isaiah. The blocked material there was a sixth-century hagiography; here it is a Second Temple Aramaic narrative about the Nephilim. Two vendors, two corpora, two of the project's three case studies. This is no longer an anecdote: **frontier content filters systematically block the primary literature of ancient religious traditions**, and a digital-humanities pipeline cannot assume a model will be permitted to read its sources. For a project whose corpus *is* religious literature, this is a first-order infrastructure risk and belongs in the paper's methodology section, not a footnote.

Note also that Gemini 3.7 Flash, blocked on the Greek page, transcribed 11 of 12 Aramaic fragments without complaint — the same inconsistency the Latin run showed. The filter is not tracking subject matter in any way a researcher can plan around.

---

## 4. The convergent-disagreement audit does not work here — and that is a finding

Run against the infrared results, `consensus_check.py` returns **one locus across the entire corpus** (4 characters of 127 in frg. 1, where 3 of 10 models omit `תפלט`). On the Greek page the same instrument flagged 30 loci (2.8%); on the Latin page, 79 loci (2.6%).

The audit works by finding places where models agree with each other and disagree with the human. That requires the models to agree with the human nearly everywhere else. At CER 0.75–0.99 they agree with the human almost nowhere, and their disagreements are uncorrelated noise rather than convergent signal.

**Convergent-disagreement auditing therefore has a precondition: a baseline of model competence on the material.** It is a tool for auditing a good transcription of a readable page, not a tool for hard cases. That boundary is worth stating explicitly in the paper, because the intuition runs the other way — one would expect the audit to be most valuable exactly where the reading is hardest, and it is least valuable there.

---

## 4. Open items

1. **f5 and f19 have no photographs.** f5's plate position is measured (903, 516); no image in the Leon Levy set of 15 is f5. f19 was never reproduced (DJD 31: "non reproduit Pl. II"). The IAA request should name f5 explicitly. 15 words of ground truth are unbenchmarkable until then.
2. **The column-ii crop is not line-registered, and should not be read as a column reconstruction.** On the plate, f6 occupies y 147–403 and f10+f11+f12 occupies y 530–930 — a vertical separation of at least 127 plate px between fragments that the ground truth treats as sharing line 3. The crop faithfully reproduces the plate; the plate is an arrangement of fragments, not a registered column. Every model that answered described exactly this — Gemini 3.7 Flash returned an "Upper Section", a "(Gap between upper and lower fragment clusters)", and a "Lower Section". **The layout is final and approved and has not been re-fitted**; this is reported as a measurement, and what to do about it is Ken's call. The character-stream CER does not depend on line numbering, so the effect is bounded, but any line-level metric on this unit would be meaningless.
3. **The two `גנתהה` characters** (§1 above) need an encoding decision.
5. **Cost and time are now recorded per call** (`cost`, `elapsed_seconds` in the scored JSON). The 204-call infrared run cost roughly **$9**, unevenly: Kimi K3 alone was $2.87 and took 32 minutes of wall clock, Gemini 3.7 Flash cost $0.05 for more units and better CER. For a grant-funded project buying API credits, cost per scored unit belongs in the reporting.
6. **The runner writes results only after the final call.** A 204-call run that dies at call 200 loses everything; this run stalled twice on the rate-limited free-tier model and came close. It should checkpoint per unit.
7. **`google/gemma-4-31b-it:free` returned 429 on 10 of 12 units** and should be dropped from the roster or given a retry-with-backoff; as it stands it contributes nothing but wall-clock time.
4. **Corpus difficulty ordering.** Latin (legible book hand, no lacunae) → Greek (damaged majuscule) → Aramaic (fragmentary, lacunose, requires infrared). The three case studies form a difficulty gradient, which is a better spine for §5 of the paper than the current draft's focus on human error.
