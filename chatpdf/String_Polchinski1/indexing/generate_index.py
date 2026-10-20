"""Generate a MakeIndex input using the compiled translation's actual pages.

Original index references are retained in entries.json. Equation, heading and
paragraph correspondences bound their translated passages. A literal index-term
match can narrow a single source-page reference; otherwise the full bounded
passage is retained rather than inventing a precise occurrence.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import subprocess
import unicodedata

from index_format import key_for, cross_reference_records
from extract_body_text import extract_body_text

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
STEM = "String_Polchinski1_jp"
POPPLER = Path(r"C:\Users\false\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftotext.exe")


def normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"[^\w\u3040-\u30ff\u3400-\u9fff]", "", text)


def text_variants(tex):
    # Drop TeX-only formatting while retaining human-readable names.
    tex = re.sub(r"\\(?:text|mathrm|mathit|mathbf|operatorname|mbox|emph)\{([^{}]*)\}", r"\1", tex)
    tex = re.sub(r"\\[A-Za-z]+", " ", tex)
    full = normalize(tex)
    candidates = [full]
    # Parenthetical qualifiers usually specify a subtopic of the same term.
    bare = re.sub(r"[（(][^）)]*[）)]", "", tex)
    candidates.append(normalize(bare))
    # Japanese inflections used in the index need not be identical in prose.
    for value in list(candidates):
        for suffix in ("したもの", "するもの", "について", "として", "に対する", "における", "との関係"):
            if value.endswith(suffix):
                candidates.append(value[:-len(suffix)])
    return {x for x in candidates if len(x) >= (2 if re.search(r"[\u3040-\u9fff]", x) else 4)}


def main():
    entries = json.loads((ROOT / "indexing/entries.json").read_text(encoding="utf-8"))["entries"]
    by_id = {e["id"]: e for e in entries}
    spans_data = json.loads((ROOT / "indexing/page_spans.json").read_text(encoding="utf-8"))
    spans = {p["source_page"]: sorted(set(p["translated_pages"] + p.get("figure_candidate_pages", []))) for p in spans_data["pages"]}
    text_path = BUILD / "index_body.txt"
    extract_body_text(BUILD / (STEM + ".pdf"), text_path, BUILD / "index_text_body.pdf")
    pages = [normalize(p) for p in text_path.read_text(encoding="utf-8").split("\f")]
    records = collections.defaultdict(set)
    audit = []
    cross_count = 0
    for entry in entries:
        key = key_for(entry, by_id)
        variants = text_variants(entry["japanese_tex"]) | text_variants(entry["effective_english_tex"])
        for reference in entry["source_references"]:
            original_pages = reference["expanded_pages"]
            missing = [p for p in original_pages if p not in spans or not spans[p]]
            if missing:
                raise RuntimeError(f"{entry['id']} has unmapped source pages: {missing}")
            candidates = sorted({q for p in original_pages for q in spans[p]})
            matches = [q for q in candidates if any(v in pages[q - 1] for v in variants)]
            # A source range refers to its discussion as a whole. Keep that
            # range even when a literal term occurs only on its first page.
            selected = matches if len(original_pages) == 1 and matches else candidates
            encap = "indexitalic" if reference["italic"] else "hyperpage"
            if reference["following_unspecified"]:
                # 'ff.' has no stated final page in the original index.
                selected = [min(selected)]
                encap = "indexitalicfollowing" if reference["italic"] else "indexfollowing"
            qualified_key = key
            qualifier = reference["qualifier_english_tex"] or reference["qualifier_japanese_tex"]
            if qualifier:
                # Helper may supply an explicit formatter for the few
                # qualified reference groups without changing their meaning.
                from index_format import qualified_key_for
                qualified_key = qualified_key_for(entry, by_id, reference)
            for q in selected:
                records[(qualified_key, encap)].add(q)
            audit.append({"id": entry["id"], "original_reference": reference["raw_tex"],
                          "source_pages": original_pages, "candidate_pages": candidates,
                          "literal_matches": matches, "translated_pages": selected,
                          "method": "literal_match_in_corresponding_passage" if selected == matches else "corresponding_passage_range",
                          "italic": reference["italic"], "following_unspecified": reference["following_unspecified"]})
        for record in cross_reference_records(entry, by_id):
            records[(record["key"], record["encap"])].add(record.get("page", 0))
            cross_count += 1
    # When prose and an exercise share the same translated page, retain one
    # italic link: it still identifies the exercise on that page.
    duplicate_style_pages = 0
    for (key, encap), numbers in list(records.items()):
        if encap == "indexitalic" and (key, "hyperpage") in records:
            duplicate_style_pages += len(numbers & records[(key, "hyperpage")])
            records[(key, "hyperpage")] -= numbers
    lines = []
    for (key, encap), numbers in records.items():
        for number in sorted(numbers):
            lines.append(r"\indexentry{" + key + "|" + encap + "}{" + str(number) + "}")
    idx_path = BUILD / (STEM + ".idx")
    content = "\n".join(lines) + "\n"
    idx_path.write_text(content, encoding="utf-8")
    report = {"input_entries": len(entries), "original_reference_tokens": len(audit),
              "cross_reference_records": cross_count, "makeindex_records": len(lines),
              "same_page_regular_and_exercise_references_shown_once_in_italics": duplicate_style_pages,
              "methods": dict(collections.Counter(a["method"] for a in audit)),
              "idx_sha256": hashlib.sha256(idx_path.read_bytes()).hexdigest(),
              "all_references": audit,
              "passage_mapping_note": "Unmatched terms retain the complete bounded translated passage; no proportional page-number conversion is used."}
    (ROOT / "qa/index_translation_page_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "all_references"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
