"""Prompt Library: named prompt protocols and language profiles.

Protocols are an experimental variable: every candidate is a
(model × protocol) pair, so protocols compete in the same rubric scoring and
pairwise ELO tournament as models. Edit prompts/protocols.yaml to add or
refine protocols — that file is the deposit-ready Prompt Library.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

DEFAULT_SIGLA_NOTE = (
    "Preserve editorial sigla in your translation: [brackets] mark "
    "reconstructions, ⟦double brackets⟧ mark scribal deletions, "
    "⟨angle brackets⟩ mark supralinear additions, ◦ marks unidentifiable "
    "letter traces."
)

DEFAULT_LANGUAGES = {
    "QH": "Qumran Hebrew (post-biblical Hebrew of the Dead Sea Scrolls; note plene orthography, sectarian technical lexicon, late waw-consecutive usage)",
    "QA": "Qumran Aramaic (the Aramaic dialect of the Dead Sea Scrolls, distinct from both Biblical Aramaic and Targumic Aramaic)",
    "GRC": "post-classical Greek of biblical manuscripts (Septuagint/Hexaplaric traditions; note itacism, nomina sacra, and marginal sigla)",
    "LAT": "Late/medieval Latin of biblical and parabiblical manuscript traditions (note abbreviations, orthographic variation, and Vulgate-influenced diction)",
}


@dataclass
class Protocol:
    name: str
    system: str
    user_suffix: str = ""
    extract_marker: Optional[str] = None  # if set, keep only text after marker
    description: str = ""


@dataclass
class PromptLibrary:
    protocols: dict[str, Protocol] = field(default_factory=dict)
    languages: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_LANGUAGES))
    sigla_note: str = DEFAULT_SIGLA_NOTE

    @classmethod
    def load(cls, path: Optional[Path]) -> "PromptLibrary":
        lib = cls()
        if path is None or not Path(path).exists():
            lib.protocols["baseline"] = Protocol(
                name="baseline", system=_FALLBACK_SYSTEM
            )
            return lib
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        for name, spec in (raw.get("protocols") or {}).items():
            lib.protocols[name] = Protocol(
                name=name,
                system=spec["system"],
                user_suffix=spec.get("user_suffix", ""),
                extract_marker=spec.get("extract_marker"),
                description=spec.get("description", ""),
            )
        if raw.get("languages"):
            lib.languages.update(raw["languages"])
        if raw.get("sigla_note"):
            lib.sigla_note = raw["sigla_note"]
        if not lib.protocols:
            lib.protocols["baseline"] = Protocol(
                name="baseline", system=_FALLBACK_SYSTEM
            )
        return lib

    def language_profile(self, code: str) -> str:
        return self.languages.get(code, code)


_FALLBACK_SYSTEM = (
    "You are a specialist translator of ancient manuscript texts. Translate "
    "faithfully, preserving the philological character of the source. Do not "
    "modernise or paraphrase. Where the source has lacunae, mark them in the "
    "translation rather than inventing content."
)


def extract_translation(text: str, protocol: Protocol) -> str:
    """Apply the protocol's post-processing (e.g. strip CoT reasoning)."""
    text = (text or "").strip()
    if protocol.extract_marker and protocol.extract_marker in text:
        text = text.split(protocol.extract_marker, 1)[1].strip()
    return text


def candidate_id(model: str, protocol: str) -> str:
    return f"{model} [{protocol}]"
