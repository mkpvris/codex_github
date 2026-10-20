"""Parse only the user-provided book's reference list and local INSPIRE exports.

No network access.  Original extraction lines are preserved in the JSON.
"""
from pathlib import Path
import json
import re
import unicodedata
import sys

sys.stdout.reconfigure(encoding="utf-8")

folder = Path(__file__).resolve().parent
source = folder.parent
entries = []
current = None
start_pattern = re.compile(r"^(.+?)\s+\((\d{4}[a-z]?)\)\.\s+(.*)$")
for page in range(374, 381):
    text = (source / f"poppler_{page:03d}.txt").read_text(encoding="utf-8")
    lines = text.splitlines()
    if page == 374:
        first = next(i for i, line in enumerate(lines) if line.lstrip().startswith("Alvarez, O."))
        lines = lines[first:]
    else:
        lines = lines[1:]  # running head and printed page number
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        matched = start_pattern.match(stripped)
        if matched:
            if current:
                entries.append(current)
            current = {
                "original_order": len(entries) + 1,
                "source_pdf_page": page,
                "source_printed_page": page - 22,
                "original_lines": [raw],
                "authors_original": matched.group(1),
                "year_original": matched.group(2),
                "body_parts": [matched.group(3)],
            }
        else:
            if current is None:
                raise ValueError((page, stripped))
            current["original_lines"].append(raw)
            current["body_parts"].append(stripped)
if current:
    entries.append(current)

publication_markers = (
    "Nuclear Physics", "Annals of Physics", "Physics Letters", "Physical Review",
    "Reviews of Modern Physics", "Communications in Mathematical Physics",
    "Canadian Journal of Mathematics", "Physics Reports",
    "Proceedings of the National Academy of Sciences",
    "Nuovo Cimento Supplement", "Supplement to Progress in Theoretical Physics",
    "Progress of Theoretical Physics", "International Journal of Modern Physics",
    "CERN report", "In ", "Cambridge:", "Menlo Park:", "Oxford:", "New York:",
    "Leuven:", "Berlin:", "San Francisco:", "Boston:", "Chur, Switzerland:",
    "Reading:", "Singapore:",
)
marker_regex = re.compile(r"[.?]\s+(?=" + "|".join(re.escape(s) for s in publication_markers) + ")")
for entry in entries:
    body = unicodedata.normalize("NFC", " ".join(entry.pop("body_parts")))
    entry["original_text"] = " ".join(line.strip() for line in entry["original_lines"])
    entry["authors_original"] = unicodedata.normalize("NFC", entry["authors_original"])
    split = marker_regex.search(body)
    if split is None:
        raise ValueError(("publication split failed", entry["original_order"], body))
    title_end = split.start() + (1 if body[split.start()] == "?" else 0)
    entry["title_original"] = body[:title_end]
    entry["publication_original"] = body[split.end():]
    entry["arxiv_identifiers_in_source"] = re.findall(r"(?:hep-[a-z]+|gr-qc|math-ph|quant-ph)/\d{7}", body)
    entry["dois_in_source"] = re.findall(r"10\.\d{4,9}/[^\s]+", body)
    entry["matching_status"] = "pending"
    entry["parse_notes"] = []
    if entry["title_original"] == "Nonlinear models in 2 + . dimensions":
        entry["title_original"] = "Nonlinear models in 2 + ε dimensions"
        entry["parse_notes"].append(
            "The Poppler text extraction renders the symbol after 2 + as a full stop. "
            "Original page image source376.png visually confirms epsilon; recovered in title_original, "
            "while original_text/original_lines preserve the extraction literally."
        )
    if entry["authors_original"].startswith("Gross."):
        entry["parse_notes"].append("Source punctuation is Gross. D. J. rather than Gross, D. J.; preserved.")

chosen = {
    "misner1973": ("95654", "Misner", "1973", "exact", []),
    "gsw1987v2": (
        "252419", "Green", "1987", "same_book_volume_year_discrepancy",
        ["Source reference covers two volumes (1987); preface specifically refers to volume 2.",
         "INSPIRE publication free text says 1987; official BibTeX year is 1988 (imprint 1988-07).",
         "Keep the original prose citation year 1987 and preserve official export unchanged.",
         "The full-book reference should account for volume 1 as well; its existing export is gsw1987v2_250488.bib."]
    ),
    "cheng1991": (
        "221340", "Cheng", "1991", "same_book_year_discrepancy",
        ["Original book cites 1991; INSPIRE's matched original textbook record gives 1984.",
         "Record 527190 is the distinct Problems and solutions book (2000) and is rejected.",
         "Official export includes ORCID bracket text in author field; retain export and document any display-only cleanup separately."]
    ),
    "weinberg1979": (
        "159043", "Weinberg", "1979", "same_chapter_year_discrepancy",
        ["Original source cites 1979; official INSPIRE BibTeX export gives 1980.",
         "Title, parent book, author, and pages 790--831 match."]
    ),
    "goddard1973": ("80965", "Goddard", "1973", "exact", []),
    "rebbi1974": ("94478", "Rebbi", "1974", "exact", []),
    "scherk1975": ("838", "Scherk", "1975", "exact", ["BibTeX key contains 1974 but publication year in export and original is 1975."]),
    "brink1973": ("228663", "Brink", "1973", "exact", []),
}
candidate_data = json.loads((folder / "initial_candidates.json").read_text(encoding="utf-8"))
selection = []
for candidate in candidate_data:
    alias = candidate["key"]
    if alias not in chosen:
        rejection_notes = {
            "quigg1983": [
                "Record 154711 (Quigg:1980kn) is a 1981 lecture contribution, not the 1983 book.",
                "Record 1263594 (Quigg:2013ufa) is the 2013 second edition, not the 1983 first edition.",
                "Primary INSPIRE search snippets confirm a separately indexed first-edition title, "
                "Gauge Theories Of Strong, Weak, And Electromagnetic Interactions : First Edition, "
                "Front.Phys. 56 (1983) 1-334, but an exact record and official export have not yet been retrieved.",
            ],
            "weinberg1964": [
                "Original source abbreviates the article title.",
                "Target DOI supplied by root: 10.1103/PhysRev.135.B1049.",
                "Full INSPIRE-indexed title seen in primary reference snippets: "
                "Photons and Gravitons in $S$-Matrix Theory: Derivation of Charge Conservation "
                "and Equality of Gravitational and Inertial Mass.",
                "No exact record or official BibTeX export retrieved yet.",
            ]
        }
        selection.append({
            "alias": alias, "status": "pending_exact_official_export",
            "bibtex_key": None, "selected_record_id": None, "notes": rejection_notes[alias],
            "rejected_existing_records": [m["record_id"] for m in candidate["matches"]]
        })
        continue
    record_id, lead, year, status, notes = chosen[alias]
    selected = next(m for m in candidate["matches"] if m["record_id"] == record_id)
    bib = (folder / selected["bib_file"]).read_text(encoding="utf-8")
    match = re.search(r"@\w+\{([^,]+),", bib)
    export_year = re.search(r'year\s*=\s*"([^"]+)"', bib).group(1)
    entry = next(e for e in entries if e["authors_original"].startswith(lead) and e["year_original"] == year)
    entry["matching_status"] = status
    entry["selected_inspire_record_id"] = record_id
    entry["selected_bibtex_key"] = match.group(1)
    entry["official_export_file"] = selected["bib_file"]
    entry["matching_notes"] = notes
    selection.append({
        "alias": alias, "status": status, "original_order": entry["original_order"],
        "bibtex_key": match.group(1), "selected_record_id": record_id,
        "official_export_file": selected["bib_file"], "official_export_url": selected["bibtex_url"],
        "original_year": year, "official_export_year": export_year,
        "notes": notes,
        "rejected_existing_records": [m["record_id"] for m in candidate["matches"] if m["record_id"] != record_id],
    })

result = {
    "source": "String_Polchinski1_original.pdf",
    "source_pdf_pages": list(range(374, 381)),
    "source_printed_pages": list(range(352, 359)),
    "original_reference_labels": "author-year, alphabetical bibliography; no numeric labels in original",
    "count": len(entries),
    "method": "Parsed the user-provided PDF's Poppler text extraction; all original lines preserved. NFC only in parsed fields.",
    "references": entries,
}
(folder / "original_reference_list.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(folder / "initial_selected_matches.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"entries": len(entries), "selected_initial": len(chosen), "pending_initial": len(selection)-len(chosen), "arxiv_in_source": sum(bool(e["arxiv_identifiers_in_source"]) for e in entries)}, ensure_ascii=False))
for e in entries:
    print(f'{e["original_order"]:03d} p{e["source_pdf_page"]} {e["authors_original"]} ({e["year_original"]}). {e["title_original"]}')
