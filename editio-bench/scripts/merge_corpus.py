"""One-off migration: fold Track A's translation passages into data/benchmarks.json
as task_type=="translation" entries, then retire data/passages.jsonl.

Run once: python3 scripts/merge_corpus.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH_PATH = ROOT / "data" / "benchmarks.json"
PASSAGES_PATH = ROOT / "data" / "passages.jsonl"

LANG_NAME = {"QH": "Qumran Hebrew", "QA": "Qumran Aramaic", "GRC": "Greek", "LAT": "Latin"}

GENRE_BY_ID = {
    # existing two translation tasks didn't carry a "source"/"genre" field; backfill
    "translat-greek-marchalianus-siloam": (
        "narrative",
        "καὶ ὁ θεὸς τὸ σημεῖον τοῦ Σιλωὰμ διὰ τὸν προφήτην ἐποίησεν· ὅτι πρὸ τοῦ "
        "θανεῖν ὀλιγωρήσας ηὔξατο πιεῖν ὕδωρ καὶ εὐθέως ἀπεστάλη αὐτῷ ἐξ αὐτοῦ· διὰ "
        "τοῦτο ἐκλήθη Σιλωάμ, ὃ ἑρμηνεύεται ἀπεσταλμένος... ἐὰν οὖν οἱ Ἰουδαῖοι "
        "ἤρχοντο, ἐξήρχετο ὕδωρ· ἐὰν δὲ ἀλλόφυλοι, οὔ· διὸ ἕως σήμερον αἰφνιδίως "
        "ἐξέρχεται, ἵνα δειχθῇ τὸ μυστήριον.",
    ),
    "translat-latin-vatlat629-seraphim": (
        "hagiography",
        "Tradunt autem Hebraei duabus ex causis interfectum fuisse Esaiam : unum, "
        "quod eos appellauerit principes Sodomorum et populum Gomorrae ; alterum, "
        "quod, testante Domino ad Moysen « non poteris uidere faciem meam », iste "
        "ausus est exclamare : « Vidi Dominum sedentem super thronum excelsum... », "
        "non arbitrantes caecati mente Iudaei quod in sequentibus faciem et pedes "
        "Dei Seraphin texisse narrauerat ac media tantum eius uidisse scribat. "
        "Iacet sub quercu Rogel iuxta decursus aquarum.",
    ),
}


def load_jsonl(path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln and not ln.startswith("//"):
                rows.append(json.loads(ln))
    return rows


def main():
    doc = json.loads(BENCH_PATH.read_text(encoding="utf-8"))
    doc["dataset"] = "EditioBench-v0.5"
    doc["description"] = (
        "Ground-truth benchmark suite for the Penner SSHRC IDG \"Methodological "
        "Blueprint\". Grounded directly in the project's three transcribed primary "
        "manuscripts: Greek Vat.gr.2125_0029 (Codex Marchalianus), Latin "
        "Vat.lat.629_0016 (Vat. lat. 629 f. 3v), and Aramaic 4Q530 (Book of Giants), "
        "plus a pilot Qumran/Greek/Latin translation corpus (formerly a separate "
        "'translation track'), now merged into one suite. Evaluates LLMs across the "
        "complete scholarly-edition workflow: (1) Transcription, (2) Collation, "
        "(3) Translation & Lacuna Handling, (4) Annotation & TEI Encoding."
    )

    by_id = {b["id"]: b for b in doc["benchmarks"]}
    for bid, (genre, source) in GENRE_BY_ID.items():
        by_id[bid]["genre"] = genre
        by_id[bid]["source"] = source

    passages = load_jsonl(PASSAGES_PATH)
    added = []
    for p in passages:
        is_placeholder = p.get("reference_source") == "placeholder"
        entry = {
            "id": p["id"],
            "siglum": p["siglum"],
            "language": LANG_NAME.get(p["language"], p["language"]),
            "task_type": "translation",
            "genre": p.get("genre", ""),
            "source": p["source"],
            "prompt": (
                f"Translate into accurate scholarly English the following "
                f"{p.get('genre', 'passage')} ({p['siglum']}):\n\n'{p['source']}'"
            ),
            "ground_truth": None if is_placeholder else p["reference"],
            "source_citation": p["reference_source"],
            "notes": p.get("notes", ""),
            "verification_status": "NEEDS_GT" if is_placeholder else "ESTABLISHED_GT",
        }
        doc["benchmarks"].append(entry)
        added.append((entry["id"], entry["verification_status"]))

    BENCH_PATH.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    PASSAGES_PATH.unlink()
    print(f"merged {len(added)} translation-track passages into {BENCH_PATH}")
    for bid, status in added:
        print(f"  {status:14} {bid}")
    print(f"removed {PASSAGES_PATH}")


if __name__ == "__main__":
    main()
