# HITL Evaluation Rubric (Book of Giants case study)

Undergraduate RAs and the LLM evaluators score every candidate output **0–100**
on the four dimensions from `benchmarking_protocols.md`. The automated scorer
returns a single integer inside a fenced markdown block; RAs record dimension
sub-scores on the shared Google Sheet.

1. **Lexical accuracy** — correct root/word rendering.
2. **Morphological correctness** — correct stem and segmentation (e.g. distinguishing
   *aphel* from *pael* in Aramaic).
3. **Handling of uncertainty (Hallucination Index)** — at a lacuna, did the model flag
   the gap and offer tentative alternatives, or confidently hallucinate a grammatically
   perfect but historically impossible reading?
4. **Formal Stuckness penalty** — did the model silently "correct" a valid historical
   scribal anomaly into a standardized modern spelling? Deduct.

Blind grading: RAs do not see which model produced an output. Two independent
evaluator models (`scorer: true` in `models.json`) score each candidate; the pipeline
records both columns (Score 1, Score 2) for inter-rater analysis in Phase 3.
