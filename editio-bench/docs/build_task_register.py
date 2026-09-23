"""Regenerate docs/task-register.html from the benchmark data.

Run:  python3 editio-bench/docs/build_task_register.py

Reads data/benchmarks.json plus the manuscript crops under resac2026/ and
fills task-register.template.html, so the published register can never drift
from the prompts and ground truth the suite actually runs.
"""
import json, base64, html, pathlib
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent   # repo root; manuscript crops live at resac2026/
EB = ROOT/"editio-bench"
doc = json.loads((EB/"data/benchmarks.json").read_text(encoding="utf-8"))
B, R = doc["benchmarks"], doc["rubrics"]
e = html.escape

def img64(p):
    return base64.b64encode((ROOT/p).read_bytes()).decode()

WIT = [
 ("marchalianus", "Vat. gr. 2125", "Codex Marchalianus", "Greek",
  "Biblioteca Apostolica Vaticana · Egypt, 6th–7th c. · uncial majuscule, lunate sigma, nomina sacra. "
  "Page 11 carries the opening of <em>Vitae Prophetarum</em>: Isaiah.", "Greek"),
 ("vatlat629", "Vat. lat. 629", "Isidore, <em>De ortu et obitu patrum</em> §37", "Latin",
  "Folio 3v, opening of the Esaias chapter under a red rubricated initial. "
  "Heavy suspension system: <span class='ms'>p̄phe</span>, <span class='ms'>nuncupat̄ ē</span>, "
  "<span class='ms'>paſtoꝝ</span>, <span class='ms'>ierl̄m</span>; the scribe mixes round and long s.", "Latin"),
 ("4q530", "4Q530", "Book of Giants, column ii", "Aramaic",
  "Qumran Cave 4, infrared plate (IAA PAM 43.568). Fragment 6 preserves the top of the column, "
  "lines 6–9 in Puech's numbering (DJD 31, 28–35).", "Aramaic"),
]

TASKMETA = {
 "transcription": ("Transcription", "Read the ink off the plate and lay it out in two layers: diplomatic, then normalized."),
 "collation":     ("Collation", "Build a critical apparatus from witnesses supplied in the prompt."),
 "translation":   ("Translation", "Render a passage into scholarly English."),
 "lacuna_handling":("Lacuna handling", "Translate a broken text without closing the gaps."),
 "annotation":    ("Annotation", "Parse morphology and emit the corresponding markup."),
 "encoding":      ("Encoding", "Produce schema-valid TEI P5 from a codicological record."),
}

SYSTEM_PROMPT = ("You are a strict philologist working on ancient manuscript texts (Dead Sea "
 "Scrolls, Septuagint, Latin parabiblica). Do NOT normalize spelling variations. "
 "Preserve all scribal anomalies exactly as transcribed. When text is broken "
 "(lacuna), say so explicitly and never present a conjectural restoration as certain.")

def block(cls, text):
    return f'<pre class="slab {cls}">{e(text)}</pre>'

def task_card(b):
    tt = b["task_type"]
    label, _ = TASKMETA[tt]
    vis = bool(b.get("image_path"))
    lang_cls = {"Greek":"grc","Latin":"lat","Aramaic":"heb"}.get(b.get("language",""),"")
    parts = [f'<article class="task" id="{e(b["id"])}">']
    parts.append('<header class="task-head">')
    parts.append(f'<span class="chip chip-{tt}">{e(label)}</span>')
    if vis: parts.append('<span class="chip chip-img">image input</span>')
    parts.append(f'<span class="chip chip-gt">{e(b["verification_status"].replace("_"," ").lower())}</span>')
    parts.append(f'<h4>{b["siglum"]}</h4>')
    parts.append(f'<p class="taskid">{e(b["id"])}</p>')
    parts.append('</header>')

    parts.append('<div class="slot"><h5>Given to the model</h5>')
    if vis:
        parts.append(f'<figure class="plate"><img alt="Manuscript crop supplied to the model: {e(b["siglum"])}" '
                     f'src="data:image/jpeg;base64,{img64(b["image_path"])}">'
                     f'<figcaption>{e(pathlib.Path(b["image_path"]).name)} — attached as a base64 <code>image_url</code> part '
                     f'alongside the text below.</figcaption></figure>')
    parts.append(block("prompt "+lang_cls, b["prompt"]))
    parts.append('</div>')

    parts.append('<div class="slot"><h5>Ideal response</h5>')
    parts.append(block("gt "+lang_cls, b["ground_truth"]))
    parts.append(f'<p class="cite">{b["source_citation"]}</p>')
    parts.append('</div>')

    if b.get("anomalies"):
        parts.append('<div class="slot"><h5>What the task is actually testing</h5><ul class="anom">')
        for a in b["anomalies"]:
            parts.append(f'<li>{a}</li>')
        parts.append('</ul></div>')
    parts.append('</article>')
    return "\n".join(parts)

def rubric_block(name, r):
    lab, blurb = TASKMETA[name]
    dims = "\n".join(f'<li>{d}</li>' for d in r["dimensions"])
    return (f'<section class="rubric" id="rubric-{name}">'
            f'<h4><span class="chip chip-{name}">{e(lab)}</span></h4>'
            f'<p class="rub-blurb">{blurb}</p>'
            f'<p class="rub-lab">Dimensions the scorer weighs</p><ol class="dims">{dims}</ol>'
            f'<p class="rub-lab">Instructions handed to the scorer</p>'
            f'<blockquote>{e(r["instructions"])}</blockquote></section>')

witness_html = []
for slug, sig, name, lang, blurb, _l in WIT:
    tasks = [b for b in B if b["language"] == lang]
    order = {"transcription":0,"collation":1,"translation":2,"lacuna_handling":2,"annotation":3,"encoding":4}
    tasks.sort(key=lambda b: order[b["task_type"]])
    witness_html.append(
      f'<section class="witness" id="w-{slug}">'
      f'<div class="wit-head"><p class="sig">{e(sig)}</p><h3>{name}</h3><p class="wit-blurb">{blurb}</p>'
      f'<p class="wit-count">{len(tasks)} tasks</p></div>'
      + "\n".join(task_card(b) for b in tasks) + '</section>')

toc = []
for slug, sig, name, lang, _b, _l in WIT:
    sub = "".join(f'<li><a href="#{e(b["id"])}">{e(TASKMETA[b["task_type"]][0])}</a></li>'
                  for b in sorted([x for x in B if x["language"]==lang],
                                  key=lambda b: {"transcription":0,"collation":1,"translation":2,"lacuna_handling":2,"annotation":3,"encoding":4}[b["task_type"]]))
    toc.append(f'<li><a href="#w-{slug}" class="toc-w">{e(sig)}</a><ul>{sub}</ul></li>')

rubric_order = ["transcription","collation","translation","lacuna_handling","annotation","encoding"]
rubrics_html = "\n".join(rubric_block(k, R[k]) for k in rubric_order)

counts = {}
for b in B: counts[b["task_type"]] = counts.get(b["task_type"],0)+1

TPL = open(HERE/"task-register.template.html", encoding="utf-8").read()
out = (TPL.replace("<!--WITNESSES-->", "\n".join(witness_html))
          .replace("<!--RUBRICS-->", rubrics_html)
          .replace("<!--TOC-->", "".join(toc))
          .replace("<!--SYSPROMPT-->", e(SYSTEM_PROMPT)))
pathlib.Path(HERE/"task-register.html").write_text(out, encoding="utf-8")
print("ok", len(out))
