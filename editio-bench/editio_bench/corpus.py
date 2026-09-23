"""Single source of truth for the merged corpus (data/benchmarks.json).

Historically the translation track (chrF/BLEU/ELO/pairwise/human-review) read
a separate data/passages.jsonl while the phase track (transcription/collation/
translation/annotation/encoding, LLM-panel scored) read data/benchmarks.json.
Both now live in one file; this module reshapes the task_type=="translation"
entries back into the flat dict shape (id/siglum/genre/language/source/
reference/reference_source) that the translation-track code expects.
"""
from __future__ import annotations

import json
from pathlib import Path

# benchmarks.json stores full language names for display; the Prompt Library
# (prompts/protocols.yaml `languages:`) keys its profiles by short code.
_LANG_CODE = {
    "Greek": "GRC",
    "Latin": "LAT",
    "Qumran Hebrew": "QH",
    "Qumran Aramaic": "QA",
    "Aramaic": "QA",
}


def load_translation_tasks(benchmarks_path: Path, runnable_only: bool = True) -> list[dict]:
    doc = json.loads(benchmarks_path.read_text(encoding="utf-8"))
    out = []
    for b in doc.get("benchmarks", []):
        if b.get("task_type") != "translation":
            continue
        if runnable_only and not b.get("ground_truth"):
            continue  # NEEDS_GT backlog entry — placeholder reference, not runnable yet
        language = b.get("language", "")
        out.append({
            "id": b["id"],
            "siglum": b.get("siglum", b["id"]),
            "genre": b.get("genre", ""),
            "language": _LANG_CODE.get(language, language),
            "source": b.get("source", ""),
            "reference": b.get("ground_truth") or "",
            "reference_source": b.get("source_citation", ""),
            "notes": b.get("notes", ""),
        })
    return out
