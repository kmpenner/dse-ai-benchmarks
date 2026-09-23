"""Tokenization Tax analysis.

Measures how heavily standard LLM tokenizers fragment the source texts —
the "tokenization tax" on non-Latin-script, morphologically dense languages.
Semitic roots split across many tokens both raise cost and plausibly degrade
the model's grip on morphology.

Metrics per (tokenizer, passage):
  tokens_per_word   — tokens / whitespace-delimited words (fertility)
  tokens_per_char   — tokens / characters
  tax_vs_reference  — fertility(source) / fertility(reference translation);
                      >1 means the ancient text costs more tokens per word
                      than its modern-language rendering.

Tokenizers: tiktoken encodings (o200k_base = GPT-4o/GPT-5 family,
cl100k_base = GPT-4 family) by default; any HuggingFace tokenizer can be
added in config under `tokenizers_hf` (requires `pip install transformers`).
Runs fully offline for tiktoken — no API cost.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Callable, Optional

from .metrics import has_usable_reference
from .corpus import load_translation_tasks


def _tiktoken_encoders() -> dict[str, Callable[[str], int]]:
    out: dict[str, Callable[[str], int]] = {}
    try:
        import tiktoken
    except ImportError:
        return out
    for name in ("o200k_base", "cl100k_base"):
        try:
            enc = tiktoken.get_encoding(name)
            out[f"tiktoken:{name}"] = (
                lambda s, _e=enc: len(_e.encode(s, disallowed_special=()))
            )
        except Exception:
            pass
    return out


def _hf_encoders(names: list[str]) -> dict[str, Callable[[str], int]]:
    out: dict[str, Callable[[str], int]] = {}
    if not names:
        return out
    try:
        from transformers import AutoTokenizer
    except ImportError:
        return out
    for n in names:
        try:
            tok = AutoTokenizer.from_pretrained(n)
            out[f"hf:{n}"] = (
                lambda s, _t=tok: len(_t.encode(s, add_special_tokens=False))
            )
        except Exception:
            pass
    return out


def _fertility(text: str, count: Callable[[str], int]) -> tuple[float, float]:
    words = max(len(text.split()), 1)
    chars = max(len(text), 1)
    n = count(text)
    return n / words, n / chars


def analyse(
    passages_path: Path,
    hf_tokenizers: Optional[list[str]] = None,
) -> dict:
    encoders = {**_tiktoken_encoders(), **_hf_encoders(hf_tokenizers or [])}
    if not encoders:
        raise RuntimeError(
            "No tokenizers available. pip install tiktoken (and optionally "
            "transformers for HuggingFace tokenizers)."
        )

    passages = load_translation_tasks(passages_path, runnable_only=False)

    rows = []
    for p in passages:
        src = p.get("source", "")
        ref = p.get("reference", "")
        has_ref = has_usable_reference(ref, p.get("reference_source"))
        for name, count in encoders.items():
            tpw_src, tpc_src = _fertility(src, count)
            row = {
                "tokenizer": name,
                "passage_id": p["id"],
                "language": p.get("language", "?"),
                "tokens_per_word_source": round(tpw_src, 3),
                "tokens_per_char_source": round(tpc_src, 4),
            }
            if has_ref:
                tpw_ref, _ = _fertility(ref, count)
                row["tokens_per_word_reference"] = round(tpw_ref, 3)
                row["tax_vs_reference"] = round(tpw_src / tpw_ref, 3)
            rows.append(row)

    # Aggregate per (tokenizer, language)
    agg: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        agg[(r["tokenizer"], r["language"])].append(r)
    summary = []
    for (tok, lang), rs in sorted(agg.items()):
        taxes = [r["tax_vs_reference"] for r in rs if "tax_vs_reference" in r]
        summary.append({
            "tokenizer": tok,
            "language": lang,
            "n_passages": len(rs),
            "mean_tokens_per_word": round(
                mean(r["tokens_per_word_source"] for r in rs), 3
            ),
            "mean_tax_vs_reference": round(mean(taxes), 3) if taxes else None,
        })
    return {"per_passage": rows, "summary": summary}


def to_markdown(result: dict) -> str:
    lines = ["# Tokenization Tax\n"]
    lines.append(
        "_Fertility = tokens per whitespace word. Tax = source fertility / "
        "reference-translation fertility; >1 means the ancient text is more "
        "expensive per word than its modern rendering. Rows without a tax "
        "value are passages whose reference is still a placeholder._\n"
    )
    lines.append("## Summary (per tokenizer × language)\n")
    lines.append("| Tokenizer | Lang | Passages | Mean tokens/word | Mean tax |")
    lines.append("|---|---|---:|---:|---:|")
    for s in result["summary"]:
        tax = f"{s['mean_tax_vs_reference']:.2f}" if s["mean_tax_vs_reference"] else "—"
        lines.append(
            f"| `{s['tokenizer']}` | {s['language']} | {s['n_passages']} | "
            f"{s['mean_tokens_per_word']:.2f} | {tax} |"
        )
    lines.append("\n## Per passage\n")
    lines.append("| Tokenizer | Passage | Lang | tokens/word | Tax |")
    lines.append("|---|---|---|---:|---:|")
    for r in result["per_passage"]:
        tax = f"{r['tax_vs_reference']:.2f}" if "tax_vs_reference" in r else "—"
        lines.append(
            f"| `{r['tokenizer']}` | {r['passage_id']} | {r['language']} | "
            f"{r['tokens_per_word_source']:.2f} | {tax} |"
        )
    return "\n".join(lines)
