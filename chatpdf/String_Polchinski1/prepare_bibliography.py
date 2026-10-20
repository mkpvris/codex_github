"""Assemble reviewed INSPIRE exports, retaining original metadata and provenance."""
from pathlib import Path
import json
import re
import unicodedata

root = Path(__file__).resolve().parent
base = root / "source" / "bibliography"
references = json.loads((base / "original_reference_list.json").read_text(encoding="utf-8"))["references"]
searched = json.loads((base / "all_candidates" / "all_candidates.json").read_text(encoding="utf-8"))["results"]
overrides = {
    10: ["181166"], 15: ["216859"], 21: ["81406"], 29: ["17034"],
    43: ["80965"], 46: ["250488", "252419"], 47: ["260776"],
    65: ["89934"], 69: ["321375"], 71: ["95654"], 72: ["216489"],
    79: ["245671"], 87: ["195708"], 94: ["228673", "228674"],
    104: ["265248"], 111: ["220076"],
}
fallback = {
    38: r"""@book{Gatto:1973scale,
    editor = "Gatto, R.",
    title = "{Scale and Conformal Symmetry in Hadron Physics}",
    publisher = "Wiley",
    address = "New York",
    year = "1973"
}""",
    73: r"""@book{Mumford:1983theta,
    author = "Mumford, David",
    title = "{Tata Lectures on Theta}",
    volume = "I--III",
    publisher = "Birkh{\"a}user",
    address = "Boston",
    year = "1983",
    doi = "10.1007/978-1-4899-2843-6"
}""",
}
supplements = {
    7: {"publisher": "Addison Wesley", "address": "Menlo Park"},
    46: {"publisher": "Cambridge University Press", "address": "Cambridge"},
    63: {"publisher": "Springer-Verlag", "address": "Berlin", "series": "Lecture Notes in Physics"},
    86: {"publisher": "Harwood", "address": "Chur, Switzerland"},
    94: {"publisher": "World Scientific", "address": "Singapore"},
    97: {"publisher": "World Scientific", "address": "Singapore"},
    109: {"publisher": "Cambridge University Press", "address": "Cambridge"},
}

def tex_escape(value):
    value = unicodedata.normalize("NFC", value)
    value = value.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")
    value = value.replace("2 + . dimensions", r"$2+\epsilon$ dimensions")
    return value

def field_value(raw, name):
    match = re.search(r"^\s*" + re.escape(name) + r'\s*=\s*"([^"]*)"', raw, re.M | re.I)
    return match[1] if match else None

def add_fields(raw, fields):
    additions = []
    for name, value in fields.items():
        if re.search(r"^\s*" + re.escape(name) + r"\s*=", raw, re.M | re.I):
            continue
        # Brace values allow literal quotation marks in the original metadata.
        additions.append("    " + name + " = {" + value + "}")
    if not additions:
        return raw.rstrip() + "\n"
    return raw.rstrip()[:-1].rstrip().rstrip(",") + ",\n" + ",\n".join(additions) + "\n}\n"

all_records, parts, map_lines, keys_in_order = [], [], [], []
for ref, search in zip(references, searched):
    number = ref["original_order"]
    assert number == search["original_order"]
    if number in fallback:
        choices = [(None, None, fallback[number])]
    else:
        ids = overrides[number] if number in overrides else [search["candidates"][0]["id"]]
        choices = []
        for record_id in ids:
            candidates = sorted(base.rglob("*_" + record_id + ".bib"))
            if not candidates:
                raise RuntimeError(f"Missing downloaded export {number}: {record_id}")
            path = candidates[0]
            choices.append((record_id, path, path.read_text(encoding="utf-8")))
    these_keys = []
    for record_id, path, raw in choices:
        match = re.match(r"@(\w+)\{([^,]+),", raw)
        if not match:
            raise RuntimeError("Malformed BibTeX")
        kind, key = match.groups()
        these_keys.append(key)
        keys_in_order.append(key)
        additions = dict(supplements.get(number, {}))
        if record_id:
            additions["url"] = "https://inspirehep.net/literature/" + record_id
        export_year = field_value(raw, "year")
        original_year = ref["year_original"][:4]
        selected_candidate = next((c for c in search["candidates"] if c["id"] == record_id), None)
        title_diff = selected_candidate and selected_candidate.get("title_score", 1) < .98
        reasons = []
        if kind.lower() != "article":
            reasons.append("書籍・会議録の原書記載（編集者、収録書、出版地、出版社、頁、刊行状況を含む）を保持")
        if export_year and export_year != original_year:
            reasons.append(f"原書年{original_year}と公式年{export_year}が異なる")
        if title_diff or number in (43, 72, 78, 94):
            reasons.append("題名・著者表記・頁・年の相違を原書記載と併記")
        if reasons and "note" not in additions and not re.search(r"^\s*note\s*=", raw, re.M | re.I):
            additions["note"] = tex_escape(ref["original_text"])
        result = add_fields(raw, additions)
        parts.append("% Original alphabetical entry " + str(number) + "\n" + result)
        all_records.append({
            "original_order": number, "original": ref["original_text"], "citation_key": key,
            "inspire_id": record_id,
            "raw_export": str(path.relative_to(root)).replace("\\", "/") if path else None,
            "export_url": f"https://inspirehep.net/api/literature/{record_id}?format=bibtex" if record_id else None,
            "matching": "著者・題名および原書の掲載誌／巻／開始頁、arXiv番号の一致を目視照合。誤候補を除外。"
                        if record_id else "INSPIRE照合レコード未取得。原書書誌をbookとして転記。miscへの置換なし。",
            "supplementary_fields": additions, "notes": reasons,
        })
    map_lines.append(r"\expandafter\def\csname refkey@" + str(number) + r"\endcsname{" + ",".join(these_keys) + "}")

assert len(references) == 113
assert len(keys_in_order) == len(set(keys_in_order))
(root / "ref_complete.bib").write_text("\n".join(parts), encoding="utf-8")
macro = r"""
% 原書のアルファベット順113項目を、公式BibTeXの引用キーへ対応させる。
\newcommand{\refcite}[1]{%
  \begingroup
  \edef\tempcite{\endgroup\noexpand\cite{\csname refkey@#1\endcsname}}%
  \tempcite}
"""
(root / "sections" / "reference_keys.tex").write_text(macro + "\n".join(map_lines) + "\n", encoding="utf-8")
(root / "sections" / "reference_order.tex").write_text(
    "% 原書のアルファベット順を保持（元の文献一覧には番号がない）。\n" +
    "\\nocite{" + ",".join(keys_in_order) + "}\n", encoding="utf-8")
audit = {
    "source_entries": 113, "output_bibtex_entries": len(keys_in_order),
    "inspire_matched_original_entries": 111,
    "not_retrieved_from_inspire": [38, 73],
    "multiple_volume_records": [46, 94],
    "raw_exports_modified": False,
    "policy": "公式エクスポートの既存フィールドを保持し、原書の欠落情報・相違はnote等で補足。追加を全件記録。",
    "records": all_records,
    "fallback_sources": {
        "38": ["添付PDF376ページ（原書354）",
               "https://w3.lnf.infn.it/farewell-to-raoul-gatto/?lang=en",
               "https://cds.cern.ch/record/145691/files/CM-P00066689.pdf"],
        "73": ["添付PDF378ページ（原書356）",
               "https://link.springer.com/book/10.1007/978-1-4899-2843-6",
               "https://www.dam.brown.edu/people/mumford/alg_geom/papers/Tata2.pdf"],
    },
}
(root / "qa" / "complete_bibliography_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Prepared {len(keys_in_order)} BibTeX entries for 113 original references; 111 INSPIRE matches, 2 documented book fallbacks.")
