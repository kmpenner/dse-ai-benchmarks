# Scoring

- **Judge panel.** Two LLM judges score each answer against the ground truth. When they disagree by more than 10 points, a third judge also scores the answer and the final score is the median of the three; otherwise it is the mean of the two. The judges read text only.
- **Character error rate.** On the three image tasks the judges proved unreliable, so [`scripts/score_visual_cer.py`](https://github.com/kmpenner/dse-ai-benchmarks/blob/master/scripts/score_visual_cer.py) adds a deterministic CER:
    - **Greek:** majuscule, diacritics stripped, sigma forms folded.
    - **Latin:** a loose CER that measures letter identification, and a strict CER that measures abbreviation fidelity.
    - **Aramaic:** extant letters only, so editorial restorations are neither charged nor credited.

For the full method, see the [benchmarks and scoring report](docs/benchmarks_and_scoring_report.md).
