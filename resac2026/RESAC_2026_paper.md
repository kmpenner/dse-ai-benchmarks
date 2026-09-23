# Digitizing Ancient Religious Texts in the Age of Artificial Intelligence: From Author to Editor

**Dr. Ken M. Penner** (St. Francis Xavier University)
**Demarquis Moss** (St. Francis Xavier University)

*Proceedings of the Research in Religious Studies Association of Canada (RESAC 2026)*
*Annual Meeting: Teaching, Technology, and the Future of Religious Studies*
*Memorial University of Newfoundland · September 26, 2026*
*Project: SSHRC Insight Development Grant (IDG) — Generative AI in Digital Humanities Research Methodology (`R0253025`)*

---

### Abstract

Generative AI has made the basic labour of editing ancient texts dramatically faster. In our project, transcribing a page of a Greek manuscript by hand took four to five hours; checking an AI draft of the same page takes about twenty minutes. Lemmatization and morphological tagging have changed in the same way. This paper asks where the saved time goes, and what the change does to the people who do the work.

We report an open benchmark, `editio-bench`, that tests 44 models in 57 configurations on thirteen editorial tasks across three manuscripts: a Latin Caroline minuscule page (*Vat.lat.629*), a Greek uncial page (Codex Marchalianus, *Vat. gr. 2125*), and a damaged Aramaic Dead Sea Scrolls fragment (4Q530). The findings support five claims:

1. The saving comes from an escalation cascade rather than full automation. The machine drafts, a research assistant revises roughly a tenth, and roughly a tenth of that reaches a supervisor.
2. The cascade depends on the condition of the manuscript more than on the model. It works on legible pages and breaks on the Dead Sea Scrolls.
3. Different models lead on different tasks and languages.
4. Speed and cost go together, but quality does not follow time. For the leading models, more "reasoning effort" cost more and scored lower.
5. Human effort does not disappear. It concentrates at the beginning of a project (shaping the input) and at its end (shaping the output), where the highest-level discernment is needed.

AI thus moves every member of a research team up one rung, shifting each person's role from author to editor. We describe a course that teaches this ladder, and we close with time-limited model recommendations.

---

## 1. Introduction: Where Does the Saved Time Go?

Two numbers from our own project frame this paper. Transcribing a single page of a Greek manuscript by hand took Demarquis Moss, the project's research assistant, four to five hours. Checking an AI transcription of that page thoroughly now takes him about twenty minutes. Lemmatization and morphosyntactic (MSD) tagging changed the same way. What took days is now a five-minute machine pass followed by a human check, and the check runs five to ten times faster than doing the tagging from scratch. These are practitioner estimates from our own work, not controlled measurements, and we present them as such.

Figures like these invite two familiar responses in the digital humanities. One is enthusiasm that the machine can now "read" ancient manuscripts. The other is dismissal of generative AI as untrustworthy. Neither asks the question that interests us: if the basic labour of editing takes a fraction of the time it did, where does the saved time go, and what happens to the people who used to spend it?

Our answer is that AI does not remove the scholar. It moves every member of a research team up one rung. The drafting moves to the machine. Human effort moves to the start and end of a project, where the most discernment is needed. The human role, at every level, shifts from *author* (the person who produces the first draft) to *editor* (the person who judges it, corrects it, and takes responsibility for it).

The rest of the paper builds that argument from a controlled benchmark:

- **Section 2** describes the benchmark.
- **Sections 3 and 4** describe how editorial work now flows and where that flow breaks.
- **Sections 5 and 6** turn to choosing models.
- **Sections 7 and 8** make the central argument about the shaping stages and about role elevation.
- **Section 9** describes how we teach it.
- **Section 10** gives recommendations, explicitly dated.

---

## 2. Method: `editio-bench`

### 2.1 Three manuscripts along a damage gradient

We chose three manuscripts that run from easy to very hard.

| Manuscript | Script and condition | Visual task |
| :--- | :--- | :--- |
| **Latin:** *Vat.lat.629*, fol. 3v; Isidore of Seville, *De ortu et obitu patrum* §36–40 | 12th-century Caroline minuscule; clean two-column layout, high contrast, standard abbreviations | Four cropped lines |
| **Greek:** *Vat. gr. 2125* (Codex Marchalianus, Q), p. 11; *Vitae Prophetarum* (Isaiah) | 6th-century uncial majuscule; *scriptio continua*, no accents, lunate sigma, *nomina sacra* | Four cropped lines |
| **Aramaic:** 4Q530 (*Book of Giants*), col. 2, frag. 6, lines 6–9 | Carbon ink on delaminated, broken leather; IAA infrared image | Four lines of a fragment |

Human ground truth for each is frozen and registered in the project's provenance registry (`resac2026/PROVENANCE.md`). For the Greek page, the ground truth is the diplomatic layer of a two-tier TEI transcription; its history matters to our argument and is discussed in Section 7.

### 2.2 Thirteen tasks across the editorial workflow

Transcription is only the first step of an edition, so the benchmark covers the workflow as a whole:

- **Visual transcription (3 tasks):** a diplomatic transcription, one task per manuscript, made from the image alone.
- **Collation (3):** the Greek page against Schermann's edition; the Latin page against Chaparro Gómez's edition; and 4Q530 against the parallel fragments 4Q531 and 6Q8.
- **Translation (2):** Greek and Latin passages.
- **Lacuna handling (1):** reading and translating the Aramaic fragment across its physical breaks without inventing text.
- **Annotation (3):** Greek lemma and MSD tagging in TEI, Latin abbreviation encoding, and Aramaic morphological parsing.
- **Encoding (1):** a TEI header for the Greek codex.

### 2.3 Models and scoring

We ran 44 models, several at more than one reasoning-effort setting, for 57 configurations that pass the benchmark's integrity gates (Section 2.4). All calls went through OpenRouter at temperature 0.

Each answer is scored 0–100 against the ground truth by two judge models (MiniMax-M3 and Gemini 3.8 Flash) using a task-specific rubric. When the two differ by more than ten points, a third judge (DeepSeek-V4 Flash) is called and the median of the three is taken. A configuration's quality is its mean score across the thirteen tasks. Cost includes the judging, and latency is the wall-clock time of the model's own answers.

Judges are fallible, and on transcription they can disagree widely about answers whose letters are identical. We therefore also compute a deterministic character error rate (CER) on the three image tasks. This is the edit distance between the ground truth's letter stream and the best-matching span of the model's diplomatic layer, divided by the ground truth's length. Greek is scored on majuscule letters only. Latin is scored both loosely (letters) and strictly (with abbreviation marks). Aramaic is scored on the extant letters.

### 2.4 Auditing the benchmark

A benchmark is itself an edition of sorts, and it needed editing. Our audit found and corrected several problems. We withdrew each affected figure and recorded the correction in the provenance registry:

- **Survivorship bias.** A free-tier configuration had been ranked at 70.5 on the strength of only two of thirteen tasks; rate limits had emptied the rest. Configurations must now have at least 90% of their tasks scored.
- **Cache replays.** Some runs listed as separate configurations were replays of cached answers from another setting. Such replays are now excluded.
- **A false "no image" claim.** One model answered the Aramaic image task by asserting that no image had been attached. Two of three judges scored the answer 100, as if it were scholarly restraint. The call's token count shows that the image *was* delivered. Answers to image tasks that deny receiving the image now score 0.

Section 7 returns to these corrections, because they turn out to be evidence for our central claim.

### 2.5 What the benchmark cannot show

The benchmark measures single responses to single tasks. It does not measure the time a human needs to correct a draft, and the practitioner estimates in Sections 1 and 3 fill that gap only roughly. The judges are language models reading text; they do not see the manuscript image.

The Greek and Latin texts have published critical editions: Schermann (1907) for the *Vitae Prophetarum* and Chaparro Gómez (1985) for Isidore. However, no diplomatic transcription of either page is published, and both editions are normalized. A model that recited an edition would produce minuscule letters and expanded abbreviations, which our Greek and strict Latin scoring count as errors. Our loose Latin CER, which folds abbreviation marks, is less able to tell reading from recall.

---

## 3. The Escalation Cascade

How does editorial work flow once a machine drafts it? Our working impression, from a summer of doing it, can be stated in three numbers: **90 / 10 / 1**.

- About **90%** of the AI's draft is right as it stands.
- The **research assistant** revises the remaining **~10%**.
- About a tenth of those revisions (**~1%** of the whole) are hard enough that the research assistant escalates them to a **supervisor**.

These proportions are an impression, not a measured rate. They are, however, consistent with the benchmark. On the full Greek page, the best model's character error rate against the diplomatic ground truth is 0.0365 (Gemini 3.1 Pro; `PROVENANCE.md` §3). In other words, about 96% of characters are right before a human touches them. Demarquis's twenty-minute check is the "10%" step in practice.

Disagreement between models is also useful for locating that ten percent. In one early exercise we compared four models' Greek transcriptions against a draft human transcription and listed every locus where at least three of the four agreed on a different reading. That produced a worksheet of 30 loci (`collation_worksheet_Q11.md`), each decided by a person against the image at high magnification. Many turned out to be slips in the draft transcription rather than errors by the models. The worksheet's own procedure is clear that model agreement only *surfaces* a locus; it is not evidence for any reading.

The saving, then, comes from a filter rather than from full automation. The machine does the bulk. The research assistant catches what is wrong. Only the genuinely difficult questions reach the most senior person on the team. This is the mechanism behind the order-of-magnitude reduction in human effort that the timings in Section 1 describe.

---

## 4. Where the Cascade Breaks: The Page, Not the Model

The cascade has a precondition: the first draft has to be mostly right. Whether it is depends far more on the manuscript than on the model.

**Table 1. Visual transcription: character error rate on four cropped lines, by manuscript (clean-suite configurations).**

| Manuscript | Configurations scored | Median CER | Configurations at or below 0.05 |
| :--- | :---: | :---: | :---: |
| Latin, *Vat.lat.629* | 57 | 0.03 | 37 |
| Greek, *Vat. gr. 2125* | 56 | 0.13 | 14 |
| Aramaic, 4Q530 | 53 | 0.80 | 0 |

*Source: `resac2026/clean_suite_visual_cer.csv`.*

The typical configuration gets 97% of the Latin characters right. On the Greek uncial page the median is worse, but a substantial group of models is excellent. On the Dead Sea Scrolls fragment the median error rate is 80%, and no configuration gets below 0.62. The lowest figure, 0.63, came from an answer two hundred times longer than the ground truth. The lowest from an answer of plausible length was 0.66. The judge scores agree. Visual transcription as a phase averages 24.1 out of 100, and Aramaic visual transcription only 7.0, against 62.8–87.2 for the text-based phases (Table 2).

**Table 2. Mean score by workflow phase (57 configurations, 0–100).**

| Phase | Mean |
| :--- | :---: |
| Visual transcription | 24.1 |
| TEI encoding | 62.8 |
| Collation | 72.8 |
| Annotation | 76.7 |
| Lacuna handling | 77.6 |
| Translation | 87.2 |

*Source: `resac2026/clean_suite_master.csv`.*

On a legible page, then, the research assistant is an editor. On a fragment like 4Q530 there is nothing worth editing, and the scholar is still the author.

What a failed draft looks like matters too, because the editor has to be able to recognize one. In an earlier control experiment, we gave seven vision models nine images of blank, uninscribed Qumran leather. Gemini 3.1 Pro produced a transcription for all nine. Claude Opus 4.8 and GPT-4o produced text for none (`PROVENANCE.md` §4). A draft can be fluent, confident, and entirely invented. An editor can only catch that if they are able to read the fragment themselves, which is a point we return to in Section 9.

---

## 5. Different Models for Different Tasks and Languages

No single model leads everywhere. The leader changes with the task and with the language.

**Table 3. Leaders by phase and by language (mean score, 0–100).**

| Task or language | Leader |
| :--- | :--- |
| Collation | Grok 4.7, low effort (96.7); GPT-6 Astra (94.5) |
| Translation | Gemini 3.1 Pro and Grok 4.7 (97.0 each) |
| Latin (all tasks) | Gemini 3.7 Flash (92.4) |
| Greek (all tasks) | Gemini 3.1 Pro (91.7) |
| Aramaic (all tasks) | Claude Fable 5.1 (87.2–91.3); next best GPT-6 Astra (78.5) |

The practical consequence is that a project can mix and match. Suppose we choose, for each task, the best configuration among those costing under $0.20 for the whole suite. That combination scores 89.2. The single best configuration (Claude Fable 5.1, no added reasoning) scores 90.3 at $1.72, more than eight times the cost ceiling. The question for a project is therefore not "which AI should we use?" but "which model for which step, and in which language?"

**Table 4. Leading configurations on the clean suite.**

| Configuration | Quality | Tasks scored | Cost (USD) | Latency (s) |
| :--- | :---: | :---: | :---: | :---: |
| Claude Fable 5.1 (none) | 90.33 | 12/13 | 1.72 | 504 |
| GPT-6 Astra (none) | 83.54 | 13/13 | 0.60 | 292 |
| Gemini 3.1 Pro (none) | 83.15 | 13/13 | 0.69 | 319 |
| Gemini 3.7 Flash (low) | 80.38 | 13/13 | 0.14 | 87 |
| Gemini 3.8 Flash (none) | 79.08 | 13/13 | 0.15 | 122 |
| Muse Spark 1.2 (none) | 78.27 | 13/13 | 0.22 | 301 |
| Kimi K3 (none) | 77.50 | 13/13 | 0.32 | 116 |
| Claude Opus 4.8 (none) | 77.31 | 13/13 | 0.61 | 316 |

*Source: `resac2026/clean_suite_master.csv`. Cost includes judging. Claude Fable 5.1 left one task unscored.*

---

## 6. Speed, Cost, and Reasoning Effort

A principle that should guide decisions and standards is that speed and cost tend to go together. Across the 57 configurations, the correlation between log cost and log latency is r = 0.57. Quality does not go with time: the correlation between quality and log latency is r ≈ 0.04. A slower model is not, on the whole, a better one.

We tested this directly by raising the models' reasoning effort, which instructs a model to deliberate longer before answering. For the three leading models, the high-effort setting cost more, took longer, and scored lower than the best lower setting (Table 5).

**Table 5. Reasoning effort for the three leading models (quality, 0–100).**

| Model | None | Low | High | Cost and time of high vs. best lower setting |
| :--- | :---: | :---: | :---: | :--- |
| Claude Fable 5.1 | 90.3 | — | 83.6 | +22% cost |
| GPT-6 Astra | 83.5 | — | 80.2 | 4.4× cost, 5× time |
| Gemini 3.7 Flash | 78.1 | 80.4 | 77.5 | 2× cost, 3.7× time |

The pattern is not universal. Eleven models were run at more than one setting. For six of them, a higher setting scored better, by one to seven points; GPT-6 Luna, for example, rose from 64.4 to 70.5 and GPT-4o from 49.1 to 56.3. For the other five, it scored the same or worse. The gains came mostly in the middle and lower tiers and usually at higher cost and latency. None of them lifted a model into the leading group, and every leading configuration in Table 4 ran with reasoning off or low.

Free tiers illustrate the same point from the other side. Nex N2.5 Pro scored 60.7 on its free endpoint but took nearly three and a half hours (12,437 s) to finish the suite, almost all of it waiting in the provider's queue. Waiting longer for the machine does not buy a better draft.

---

## 7. Where Human Effort Goes: The Shaping Stages

If the machine drafts and the research assistant edits, where does the rest of the human effort go? Before AI, most of an editor's effort sat in the middle of a project: the trial and error of transcribing, tagging, and collating. AI compresses that middle. What remains concentrates at the two ends:

- **At the beginning,** people shape the input: they set the parameters, standards, goals, and methods.
- **At the end,** people shape the output: they interpret the results and decide how to present them.

We argue that this is where human effort belongs, because these are the stages that need the highest-level discernment. Our own benchmark supplies the evidence.

### 7.1 The beginning: a standards decision

Our first Greek ground truth was produced by a parser that, finding no diplomatic layer in the TEI file of the time, staged the *normalized* edition as if it were the diplomatic transcription. It also included the title block twice. Scored against that ground truth, the best model's Greek CER was 0.095 (Gemini 3.1 Pro).

After an audit (`greek_q_ground_truth_audit_and_loci.md`) and a decision memo (`greek_gt_decision_memo.md`), the principal investigator ruled on 31 August 2026 that the diplomatic layer, "State C", is canonical. The same model's CER against it is 0.0365 (`PROVENANCE.md` §3). Part of the apparent difficulty of the Greek page had been manufactured by the standards, not by the models. No model could have made that ruling; it required a scholar's judgment about what a diplomatic transcription of this page should contain.

### 7.2 The end: interpretation decisions

The benchmark's integrity audit (Section 2.4) is the counterpart at the end of the project:

- A score of 70.5 rested on two of thirteen tasks.
- Runs presented as independent measurements were replays of one another.
- Two of three AI judges gave a perfect score to a model that falsely claimed no image had been attached.
- An earlier master sheet, since archived, had a "transcription" column whose image had never actually been sent to the models.

None of these was flagged by a script. All were caught by people asking whether a number made sense, and all were withdrawn or corrected, with the correction recorded.

### 7.3 The verification gates as shaping stages

The project formalizes this division of labour as three human verification gates, run by the research assistant as the project's scholarly quality auditor:

- **Gate 1 (diagnostic validity):** do the tasks test genuine philological competence?
- **Gate 2 (judge efficacy):** do the rubrics and judges penalize what they should?
- **Gate 3 (calibration):** do automated scores agree with human judgment?

The first two gates shape the input; the third shapes the output. We report honestly that the gates are still being worked through. In the current audit sheet (`hitl_comprehensive_audit.csv`), two of sixteen audit rows, both Greek transcription tasks, have been calibrated, with judge and human scores agreeing within one point.

---

## 8. Everyone Moves Up a Rung

Put these pieces together and the real change comes into view. The tasks a computer can do now are the tasks a research assistant used to do. The tasks a research assistant can do now are the tasks a supervisor used to do. The supervisor can take on what used to be the principal investigator's work, and the principal investigator can turn to questions that were previously out of reach.

**Figure 1. Role elevation.**

```
BEFORE AI                          WITH AI
P.I.         ─────────────►        P.I.        (new, higher-level questions)
Supervisor   ─────────────►        Supervisor  ← what the P.I. used to do
R.A.         ─────────────►        R.A.        ← what a supervisor used to do
Computer     ─────────────►        Computer    ← what an R.A. used to do
```

Our own project shows the shift. The research assistant's work this summer went well beyond typing transcriptions. He adjudicated disputed readings in the Latin ground truth against Chaparro Gómez's critical edition, deciding for example between the manuscript's *Ezechihel* and the normalized *ezechiel* (`monday_debrief_deliverables.md` §1). He also audited whether the benchmark's tasks and judges were testing the right things. A few years ago that would have been a supervisor's job.

At every level, then, the human role shifts from author to editor. This is not a diminished role. The editor is the person who judges the draft, corrects it, and takes responsibility for it, and that requires the same expertise the author had. It also requires the confidence to exercise it on someone else's work, including a machine's.

---

## 9. Teaching the Ladder: A Digital Methods Course

If every rung moves up, students have to learn the whole ladder. The first author's course in digital methods spends one week on each phase of a digital scholarly edition:

1. Cataloguing
2. Imaging
3. Transcribing
4. Normalizing
5. Collating
6. Lexical and morphological markup
7. Translating
8. Annotating
9. Presentation
10. Publication

Each week meets three times on the same task:

1. **By hand.** Students type the data themselves; the work is human only.
2. **With pre-AI tools.** Deterministic algorithms and purpose-built applications do the same work more efficiently.
3. **With general-purpose language models.** Students put the input into a form the model can work with, then curate what it produces.

The three meetings follow the ladder of Section 8: human, then computer tool, then AI. The third meeting trains exactly the shaping stages of Section 7: shaping the input and curating the output. The first meeting is what makes the third possible. The blank-leather experiment of Section 4 shows why. A model can produce a fluent transcription of nothing, and the only defence is an editor who could have made the transcription themselves. You cannot judge a transcription you could not have made yourself.

---

## 10. Recommendations: A Dated Snapshot

Readers will ask which models to use. Our answer comes with a warning: it is a snapshot of runs made in September 2026, and it will be out of date in weeks, perhaps days, as new models appear.

**Table 6. Recommendations as of September 2026.**

| Need | Use | Clean-suite evidence |
| :--- | :--- | :--- |
| Budget | Gemini 3.7 Flash (low) | 80.4 · $0.14 per suite · 87 s |
| Balanced | GPT-6 Astra (none) | 83.5 · $0.60 · 292 s |
| Highest quality, especially Aramaic | Claude Fable 5.1 (none) | 90.3 · $1.72 · 504 s |
| Collation | Grok 4.7 (low) or GPT-6 Astra | 96.7 / 94.5 |
| Translation | Gemini 3.1 Pro or Grok 4.7 (none) | 97.0 / 97.0 |

Three practices will outlast the table:

1. **Set reasoning effort as low as possible, off if the model allows it.** In our runs, every leading configuration ran with reasoning off or low. Raising it usually cost more and helped only some weaker models, and only modestly (Section 6).
2. **Use free tiers for trying things out, not for production.** Their quality cannot be expected to match paid tiers, and on a larger project they will frequently run out of quota.
3. **Run two model families side by side.** Where they disagree is where the editor should look first (Section 3).

Above all, AI does not do the work *for* the scholar. It speeds the work up by moving the scholar from author to editor, not by becoming the author in the scholar's place. The model list will change; that division of labour will not. Before committing to a model, a project should test it on a few pages of its own material.

---

## 11. Conclusion

Generative AI has made the basic labour of editing ancient texts dramatically faster, at least on legible manuscripts. It has not made editors unnecessary. Our benchmark and our practice both point to the same structure:

- The machine drafts.
- The research assistant edits.
- The hardest questions rise to the most experienced people.
- The scholar's effort moves to where it counts most: shaping the input at the start, and interpreting the output at the end.

Where the manuscript is too damaged for a usable draft, as on the Dead Sea Scrolls, the scholar remains the author.

AI moves every member of the team up one rung. The task for religious studies, in research and in the classroom, is to train people for the rung above the one they used to occupy.

---

### Data and Code Availability

All benchmark tasks, rubrics, scored runs, and the registry that traces every figure in this paper to its source are version-controlled in the project repository:

- **Number registry:** `resac2026/PROVENANCE.md`
- **Clean-suite results:** `resac2026/clean_suite_master.csv`, `resac2026/clean_suite_visual_cer.csv`
- **Benchmark suite:** `editio-bench/` (tasks in `editio-bench/data/benchmarks.json`)

### References

Chaparro Gómez, César, ed. 1985. *Isidoro de Sevilla: De ortu et obitu patrum*. Paris: Les Belles Lettres.

Puech, Émile. 2001. *Qumrân Grotte 4.XXII: Textes araméens, première partie (4Q529–549)*. Discoveries in the Judaean Desert 31. Oxford: Clarendon Press.

Schermann, Theodor, ed. 1907. *Prophetarum vitae fabulosae, indices apostolorum discipulorumque Domini Dorotheo, Epiphanio, Hippolyto aliisque vindicata*. Leipzig: Teubner.
