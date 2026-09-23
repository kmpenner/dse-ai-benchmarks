# Replication

```bash
git clone https://github.com/kmpenner/dse-ai-benchmarks && cd dse-ai-benchmarks
uv venv && source .venv/bin/activate
uv pip install -r editio-bench/requirements.txt
```

## Rebuild scores and charts (no API key)

```bash
python scripts/score_visual_cer.py
python scripts/build_clean_suite_report.py
python scripts/build_per_task_pareto.py
```

## Re-run the models

You need an [OpenRouter](https://openrouter.ai) key:

```bash
export OPENROUTER_API_KEY=...
cd editio-bench
python -m editio_bench.cli phase --dry-run                    # offline: lists the runnable tasks
python -m editio_bench.cli phase --model openai/gpt-5.5       # one model, whole suite
```

Hosted models change without notice, so new runs will drift from the published results. The answers we scored are archived in `editio-bench/results/`.

## The 4Q530 image

The Israel Antiquities Authority image of 4Q530 is not redistributed here. On first run, the runner downloads the infrared photograph of fragment 6 from the [Leon Levy Dead Sea Scrolls Digital Library](https://www.deadseascrolls.org.il/) and crops it to the region used in the paper (URL and crop box are in `benchmarks.json`). The copy served today differs slightly from the one we scored (mean pixel difference about 8 on a 0–255 scale), so Aramaic transcription results may vary a little.
