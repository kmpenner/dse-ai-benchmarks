# Digitizing Ancient Religious Texts in the Age of Artificial Intelligence

## From Author to Editor

**Conference:** RESAC 2026 (*Teaching, Technology, and the Future of Religious Studies*) **Session:** Saturday, September 26, 2026 · 1:30–3:00 PM · Panel 4, Memorial University **Format:** 11 Slides · ~15:45 Delivery (+ Q\&A) **Co-presenters:** Dr. Ken M. Penner (Principal Investigator, St. Francis Xavier University) and Demarquis Moss (Lead Research Assistant) **Project:** SSHRC Insight Development Grant (`R0253025`)

**Thesis:** AI does not remove the scholar. It moves every member of the team up one rung: the drafting moves to the machine, and human effort shifts to the start and end of a project, where the most discernment is needed.

**Who speaks:** Demarquis speaks in the first person where the evidence is his own work (his timings on Slide 1, the benchmark, the 90/10/1 flow, the limits, his example on Slide 8, the recommendations; about 7 minutes). Ken opens, carries the argument and closes (about 8½ minutes). Each slide names its speaker; in the scripts, a name marks each change of speaker.

**Sources:** Every figure comes from `resac2026/clean_suite_master.csv` / `clean_suite_visual_cer.csv` (57 configurations of 44 models that pass the coverage and cache-replay gates, rebuilt 2026-09-22) or from `resac2026/PROVENANCE.md`. The timing figures on Slides 1 and 3 are the project's own experience and are presented as such.

---

### Slide 1: The Pace Shift

* **Slide Timing:** 0:00 – 1:15 (1 min 15 sec)
* **Speaker:** Ken → Demarquis → Ken
* **Visual Layout:**
  * **Title:** Digitizing Ancient Religious Texts in the Age of Artificial Intelligence
  * **Subtitle:** From Author to Editor
  * **Two horizontal time bars, nothing else on the slide:**
    * *Transcribing a Greek manuscript page:* **4–5 hours** by hand → **~20 minutes** to check the AI's draft
    * *Lemmas & morphosyntactic tags:* **days** → **~5 minutes** of AI plus a human check (checking runs **5–10×** faster than tagging from scratch)
* **Speaker Script:**
  > **KEN:** Thank you, and good afternoon. I'm Ken Penner, and this is Demarquis Moss, the research assistant on our SSHRC project. We'll start with two numbers from our own work.
  >
  > **DEMARQUIS:** It took me four to five hours to transcribe a single page of a Greek manuscript by hand. Checking the AI's transcription of that page, thoroughly, now takes me about twenty minutes.
  >
  > The same thing happened with lemmatization and morphological tagging. What used to take days is now a five-minute pass by the machine, followed by a human check that runs five to ten times faster than doing the tagging ourselves.
  >
  > **KEN:** So the question is no longer whether AI saves time in editing ancient texts. The question is where the saved time goes, and what that does to the people who do the work. That's what we want to talk about today.

---

### Slide 2: What We Tested

* **Slide Timing:** 1:15 – 2:30 (1 min 15 sec)
* **Speaker:** Demarquis
* **Visual Layout:**
  * **Header:** One benchmark, three manuscripts, the whole editorial workflow
  * **Top row — three manuscript crops along a damage gradient:**
    * `crop_latin_vatlat629_f3v_lines1_4.jpg` — Latin, *Vat.lat.629* f. 3v (Caroline minuscule)
    * `crop_greek_marchalianus_p11_lines1_4.jpg` — Greek, *Vat. gr. 2125* p. 11 (Codex Marchalianus, uncial)
    * `crop_aramaic_4q530_frag6.jpg` — Aramaic, 4Q530 (*Book of Giants*, IAA infrared)
  * **Bottom strip — six workflow phases:** Visual transcription → Collation → Translation → Lacuna handling → Annotation (lemma/MSD) → TEI encoding
  * **Footer:** 13 scored tasks · 44 models · 57 verified configurations · three-judge consensus scoring
* **Speaker Script:**
  > **DEMARQUIS:** Those timings come from practice, so we also wanted a controlled test.
  >
  > We built an open benchmark, editio-bench, on three manuscripts that run from easy to very hard: a clean twelfth-century Latin page of Isidore, a sixth-century Greek uncial page of the Lives of the Prophets from Codex Marchalianus, and a damaged Dead Sea Scrolls fragment of the Aramaic Book of Giants.
  >
  > We didn't stop at transcription. The thirteen tasks cover the whole editorial workflow: transcribing from the image, collating witnesses, translating, handling lacunae, lemma and morphological annotation, and TEI encoding.
  >
  > We ran forty-four models in fifty-seven configurations, and a panel of three AI judges scored every answer against our human ground truth. We also audited the benchmark itself, and when some of our own headline numbers failed that audit, we withdrew them. Ken will come back to that, because it turns out to be part of the argument.

---

### Slide 3: The Escalation Cascade — 90 / 10 / 1

* **Slide Timing:** 2:30 – 4:00 (1 min 30 sec)
* **Speaker:** Demarquis
* **Visual Layout:**
  * **Header:** The saving comes from a filter, not from full automation
  * **Funnel graphic:**
    * **100%** — Computer drafts everything
    * **~10%** — R.A. revises
    * **~1%** — escalated to the Supervisor
  * **Evidence box:** Greek p. 11: best model CER **0.0365** — about 96% of characters right before a human touches them. The R.A.'s 20-minute check *is* the 10% step.
  * **Footnote on slide:** *90/10/1 is our working impression, not a measured rate.*
* **Speaker Script:**
  > **DEMARQUIS:** Here's how the work actually flows now. Our rough impression is ninety, ten, one.
  >
  > About ninety percent of what the AI drafts is right as it stands. I revise the other ten percent. And about a tenth of those revisions, one percent of the whole, are hard enough that I take them to Ken.
  >
  > Those proportions are an impression, not a measurement. But they fit the benchmark: on our Greek page the best model's character error rate is under four percent. That's the text I'm checking in my twenty minutes.
  >
  > So the saving doesn't come from the machine doing the edition. It comes from a filter. The machine does the bulk, I catch what's wrong, and only the genuinely difficult questions reach Ken. That's where the order-of-magnitude reduction in human effort comes from.

---

### Slide 4: Limitations — Where the Cascade Breaks

* **Slide Timing:** 4:00 – 5:30 (1 min 30 sec)
* **Speaker:** Demarquis
* **Visual Layout:**
  * **Header:** The machine's draft is only as good as the page
  * **Three manuscript crops side by side, each labelled with its median character error rate (57 configurations, four cropped lines):**

| Manuscript | Median CER | Configurations at or below 0.05 |
| :--- | :---: | :---: |
| Latin, *Vat.lat.629* (clean Caroline minuscule) | **0.03** | 37 of 57 |
| Greek, *Vat. gr. 2125* (uncial, *scriptio continua*) | **0.13** | 14 of 56 |
| Aramaic, 4Q530 (carbon ink on damaged leather) | **0.80** (best 0.63) | none |

  * **Small note:** Judge scores agree: Aramaic visual transcription averages **7.0/100**, against 72–87 for the text-based phases.
* **Speaker Script:**
  > **DEMARQUIS:** That cascade has a precondition: the first draft has to be mostly right. And whether it is depends far more on the manuscript than on the model.
  >
  > On the clean Latin page, the typical configuration gets ninety-seven percent of characters right, and most configurations have an error rate under five percent. On the Greek uncial page, the median is around thirteen percent error, and a good share of models are excellent.
  >
  > On the Dead Sea Scrolls fragment, carbon ink on dark, broken leather, the median error rate is eighty percent, and even the best model gets sixty-three percent of characters wrong. There is nothing there worth editing.
  >
  > So the cascade breaks exactly where the material is hardest. On a legible page, I'm an editor. On a fragment like 4Q530, the scholar is still the author.

---

### Slide 5: Use Different Models for Different Tasks and Languages

* **Slide Timing:** 5:30 – 7:00 (1 min 30 sec)
* **Speaker:** Ken
* **Visual Layout:**
  * **Header:** No single model is best at everything
  * **Embedded chart:** `clean_chart_pareto_cost_by_task.png` (or the table below)

| Task or language | Leader (score /100) |
| :--- | :--- |
| Collation | Grok 4.7 (96.7) · GPT-6 Astra (94.5) |
| Translation | Gemini 3.1 Pro · Grok 4.7 (97.0 each) |
| Latin | Gemini 3.7 Flash (92.4) |
| Greek | Gemini 3.1 Pro (91.7) |
| Aramaic | Claude Fable 5.1 (87–91); next best 78.5 |

  * **Callout:** Best model per task, drawn only from configurations under **$0.20** per full suite → **89.2**. Single best model → **90.3** at **$1.72**.
* **Speaker Script:**
  > **KEN:** The second lesson is that there's no single best model. The leader changes from task to task and from language to language.
  >
  > For collation, Grok 4.7 and GPT-6 Astra lead. For translation, Gemini 3.1 Pro and Grok 4.7 tie. For Latin as a whole, Gemini 3.7 Flash; for Greek, Gemini 3.1 Pro; and for Aramaic one model, Claude Fable, is well ahead of everyone else.
  >
  > That has a practical consequence. If you pick the best model for each task, and restrict yourself to cheap configurations under twenty cents for the whole suite, you get within about one point of the single best model, which costs at least eight times as much.
  >
  > So the question for a project isn't 'which AI should we use?' It's 'which model for which step, and in which language?'

---

### Slide 6: Speed and Cost Tend to Correlate

* **Slide Timing:** 7:00 – 8:15 (1 min 15 sec)
* **Speaker:** Ken
* **Visual Layout:**
  * **Header:** A guiding principle: fast is usually cheap, and slow is not better
  * **Embedded chart:** `clean_chart_pareto_latency.png`
  * **Two statistics (57 configurations):** log cost vs. log latency **r = 0.57** · quality vs. latency **r ≈ 0.04**
  * **Reasoning-effort table (the three leading models):**

| Model | None | Low | High | Extra cost of high |
| :--- | :---: | :---: | :---: | :--- |
| Claude Fable 5.1 | 90.3 | — | 83.6 | +22% |
| GPT-6 Astra | 83.5 | — | 80.2 | 4.4× cost, 5× time |
| Gemini 3.7 Flash | 78.1 | 80.4 | 77.5 | 2× cost |

* **Speaker Script:**
  > **KEN:** Third, a principle that should guide decisions and standards: speed and cost tend to go together. Across our fifty-seven configurations, the models that take longer are, on the whole, the ones that cost more.
  >
  > What doesn't go with time is quality. The correlation between how long a model takes and how well it scores is essentially zero.
  >
  > We tested this directly by turning up the models' reasoning effort, telling them to think longer. For the three leading models, the high-effort setting cost more, took longer, and scored lower. GPT-6 Astra at high effort cost four times as much, took five times as long, and lost three points.
  >
  > So waiting longer for the machine doesn't buy you a better draft.

---

### Slide 7: Where Human Effort Goes — The Shaping Stages

* **Slide Timing:** 8:15 – 10:15 (2 min 00 sec)
* **Speaker:** Ken
* **Visual Layout:**
  * **Header:** Human effort moves to the beginning and the end
  * **Two effort profiles across project time:**
    * *Before AI:* effort bulges in the middle (trial-and-error transcription, tagging, collation)
    * *With AI:* a bow-tie — effort concentrates at the **beginning** (shaping the input: parameters, standards, goals, methods) and the **end** (shaping the output: interpreting and presenting)
  * **Case-study boxes (our own project):**
    * **Beginning — a standards decision:** our first Greek ground truth staged the normalized edition as diplomatic (best CER **0.095**). The State C ruling on the diplomatic baseline → best Greek CER **0.0365**.
    * **End — an interpretation decision:** a "70.5" score based on 2 of 13 tasks; "separate" runs that were cache replays; judges giving 100/100 to a model that answered "no image was attached". All caught by people, not by scripts; all withdrawn or corrected.
* **Speaker Script:**
  > **KEN:** So where does the saved time go? Before AI, most of an editor's effort sat in the middle of a project: the trial and error of transcribing, tagging, collating. AI compresses that middle. What's left concentrates at the two ends.
  >
  > At the beginning, we shape the input: we set the parameters, the standards, the goals, the methods. At the end, we shape the output: we interpret the results and decide how to present them. I'd argue that's exactly where human effort belongs, because those are the stages that need the highest-level discernment.
  >
  > Our own benchmark is the best illustration we have. At the beginning: our best early Greek error rate was about ten percent. Much of that turned out not to be the models' fault. Our ground truth had staged the normalized edition as if it were the diplomatic transcription. Once we made a ruling on the diplomatic baseline, the best Greek error rate fell below four percent. Part of the 'difficulty' had been manufactured by our standards.
  >
  > At the end: our audit found a score of seventy-point-five that rested on only two of thirteen tasks. We found 'separate' runs that were really replays of the same run. And just this week we found two of our three AI judges giving a perfect score to a model that claimed no image had been attached, when it had been. No script flagged any of these. People did.
  >
  > That's what discernment at the ends of a project looks like.

---

### Slide 8: Everyone Moves Up a Rung

* **Slide Timing:** 10:15 – 12:00 (1 min 45 sec)
* **Speaker:** Ken → Demarquis → Ken
* **Visual Layout:**
  * **Header:** From author to editor, at every level
  * **Before/after ladder diagram — each role's box slides up one rung:**

```
BEFORE AI                          WITH AI
P.I.         ─────────────►        P.I.        (higher-level questions)
Supervisor   ─────────────►        Supervisor  ← what the P.I. used to do
R.A.         ─────────────►        R.A.        ← what a supervisor used to do
Computer     ─────────────►        Computer    ← what an R.A. used to do
```

  * **Example box:** Our R.A. ruled on disputed Latin ground-truth readings against Chaparro Gómez (1985) and audited the benchmark's tasks and judges — editorial work a supervisor would once have done.
* **Speaker Script:**
  > **KEN:** Put those pieces together and you get what we think is the real change. The tasks a computer can do now are the tasks a research assistant used to do. The tasks a research assistant can do now are the tasks a supervisor used to do. And so on up. Every person on the team does higher-level work. Demarquis?
  >
  > **DEMARQUIS:** You can see it in my own work this summer, which went well beyond typing transcriptions. I ruled on disputed readings in our Latin ground truth against Chaparro Gómez's critical edition, and I audited whether our benchmark tasks and our AI judges were testing the right things. A few years ago, that would have been a supervisor's job.
  >
  > **KEN:** At every level, the human role shifts from author, the person who produces the first draft, to editor: the person who judges it, corrects it, and takes responsibility for it.

---

### Slide 9: Teaching the Ladder — The Digital Methods Course

* **Slide Timing:** 12:00 – 13:30 (1 min 30 sec)
* **Speaker:** Ken
* **Visual Layout:**
  * **Header:** One phase a week, taught three ways
  * **10 × 3 grid:**
    * *Rows (weeks):* Cataloguing · Imaging · Transcribing · Normalizing · Collating · Lexical & morphological markup · Translating · Annotating · Presentation · Publication
    * *Columns (meetings):* **1. By hand** (human only) · **2. Pre-AI tools** (deterministic algorithms, bespoke applications) · **3. General-purpose LLMs** (humans shape the input, curate the output)
  * **Highlight:** In column 3, mark the human's role at the input end and the output end.
* **Speaker Script:**
  > **KEN:** This is a teaching conference, so let me take the argument into the classroom.
  >
  > If everyone moves up a rung, students need to learn the whole ladder. My Digital Methods course spends one week on each phase of a digital scholarly edition, from cataloguing and imaging through transcription, collation, markup and translation, to presentation and publication.
  >
  > Each week we meet three times on the same task. First, by hand: we type the data ourselves. Second, with pre-AI computer tools, deterministic algorithms and purpose-built applications that do the same work more efficiently. Third, with general-purpose language models: we put the input into a form the model can work with, and then we curate what it produces.
  >
  > That third meeting trains exactly the shaping stages I described. And the first meeting is what makes the third possible: you can't judge a transcription you couldn't have made yourself.

---

### Slide 10: Model Recommendations — This Week's Snapshot

* **Slide Timing:** 13:30 – 15:00 (1 min 30 sec)
* **Speaker:** Demarquis
* **Visual Layout:**
  * **Header:** What to use this week
  * **Banner:** *Snapshot of September 2026 runs — expect it to be out of date in weeks, perhaps days.*

| Need | Use | Clean-suite evidence |
| :--- | :--- | :--- |
| Budget | Gemini 3.7 Flash (low) | 80.4 · $0.14 per suite · 87 s |
| Balanced | GPT-6 Astra (none) | 83.5 · $0.60 · 292 s |
| Highest quality | Claude Fable 5.1 (none) | 90.3 · $1.72 · 504 s |
| Collation | Grok 4.7 (low) / GPT-6 Astra | 96.7 / 94.5 |
| Translation | Gemini 3.1 Pro / Grok 4.7 (none) | 97.0 / 97.0 |

  * **Practice rules:**
    * Set reasoning effort as low as possible — off if the model allows it.
    * Free tiers are fine for trying things out, but expect lower quality than paid tiers, and on a larger project they will often run out of quota.
    * Run two model families and review where they disagree.
  * **Bottom line:** AI speeds up your work by moving you from author to editor — not by becoming the author in your place.
* **Speaker Script:**
  > **DEMARQUIS:** People always ask which model to use, so here's our answer, with a warning: this is a snapshot of this month's runs, and it will be out of date in weeks, maybe days.
  >
  > On a budget, Gemini 3.7 Flash at low effort: about eighty out of a hundred for fourteen cents for the entire suite. For balance, GPT-6 Astra. For the highest quality, and especially for Aramaic, Claude Fable, at about twelve times the cost of Flash.
  >
  > Three rules will last longer than the table. Turn reasoning effort down as far as it goes. Free tiers are fine for experimenting, but don't expect paid-tier quality, and on a real project you'll hit their quotas. And run two different model families side by side: where they disagree is where you should look.
  >
  > Above all, the AI isn't doing the work for you. It speeds the work up by making you the editor instead of the author. The model list will change; that division of labour won't. So before you commit to a model, test it on a few pages of your own material.

---

### Slide 11: Close — From Author to Editor

* **Slide Timing:** 15:00 – 15:45 (45 sec)
* **Speaker:** Ken
* **Visual Layout:**
  * **Header:** From Author to Editor
  * **One line:** AI moves every member of the team up one rung. Human effort moves to shaping the input and interpreting the output.
  * **Open deliverables & QR code:** `editio-bench` (benchmark suite) · `PROVENANCE.md` (every number traced to its run) · Project URL: `github.com/kmpenner/IDG`
  * **Contact:** Dr. Ken M. Penner (`kpenner@stfx.ca`) · Demarquis Moss
* **Speaker Script:**
  > **KEN:** To sum up: AI doesn't replace the scholar. It moves every member of the team up one rung. The machine drafts, the research assistant edits, and the scholar's effort goes where it counts most: shaping the input at the start, and interpreting the output at the end.
  >
  > The benchmark, the data, and the record of every number we've shown you are openly available.
  >
  > Thank you. Demarquis and I look forward to your questions.

---

## Q\&A Cheat Sheet (For Panel Discussion)

* **Q1: Aren't the models just reciting published editions of these texts?**
  * *Answer:* Not for what we measured. No diplomatic transcription of this Greek page is published. The published Latin edition (Chaparro Gómez) is normalized, not diplomatic, so a model can't reproduce the scribe's abbreviations and letterforms by recalling it. The Aramaic fragment is where recall would help most, and it's where every model failed.
* **Q2: What does this cost in practice?**
  * *Answer:* The budget configuration (Gemini 3.7 Flash, low effort) ran the full 13-task suite for $0.14 including judging — about a cent per task. The most expensive frontier configuration was about $1.72 for the suite.
* **Q3: How solid is the 90/10/1 figure?**
  * *Answer:* It's our working impression from the project, not a measured rate, and it only holds on legible material (Slide 4). On a legible Greek page, the best model gets about 96% of characters right, which is consistent with it.
* **Q4: Doesn't this deskill students and RAs?**
  * *Answer:* That's why the course keeps the by-hand meeting every week (Slide 9). The editor's judgment depends on being able to do the author's work; what changes is how much of it they have to do.
* **Q5: How do you handle intellectual property and library image rights?**
  * *Answer:* All images (Vatican DigiVatLib, IAA Leon Levy) are ingested under academic fair dealing / research exceptions at calibrated resolutions, with raw high-resolution facsimiles remaining under institutional ownership.
