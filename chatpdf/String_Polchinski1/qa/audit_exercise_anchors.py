"""Independently audit every exercise anchor after the build has finished.

Read-only for document/build inputs; writes only qa/exercise_anchor_audit.json.
Do not run while LuaLaTeX or the mapping/index generation is active.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def brace_fields(value):
    fields, level, start = [], 0, None
    for i, c in enumerate(value):
        if i and value[i - 1] == "\\":
            continue
        if c == "{":
            if level == 0:
                start = i + 1
            level += 1
        elif c == "}":
            level -= 1
            if level == 0 and start is not None:
                fields.append(value[start:i])
    return fields


def main():
    pdf = ROOT / "build/String_Polchinski1_jp.pdf"
    aux = ROOT / "build/String_Polchinski1_jp.aux"
    spans_path = ROOT / "indexing/page_spans.json"
    resolution_path = ROOT / "qa/page_span_resolution_audit.json"
    body_path = ROOT / "build/index_text_body.txt"
    research = json.loads((ROOT / "indexing/page_mapping_research.json").read_text(encoding="utf-8"))
    spans = json.loads(spans_path.read_text(encoding="utf-8"))
    resolution = json.loads(resolution_path.read_text(encoding="utf-8"))
    metadata = json.loads((ROOT / "build/index_text_body.json").read_text(encoding="utf-8"))
    pdf_hash, aux_hash = sha(pdf), sha(aux)
    assert pdf_hash == spans["pdf_sha256"] == resolution["pdf_sha256"] == metadata["source_sha256"], "Mixed/stale build inputs"
    assert aux_hash == spans["aux_sha256"], "Aux and mapping are from different builds"
    expected = [dict(a, source_page=p["source_page"]) for p in research["pages"] for a in p.get("exercises", [])]
    assert len(expected) == 106 and len({a["number"] for a in expected}) == 106
    mapped_list = [a for a in spans["anchors"] if a["kind"] == "exercises"]
    mapped = {a["number"]: a for a in mapped_list}
    labels = {}
    for line in aux.read_text(encoding="utf-8").splitlines():
        if not line.startswith(r"\newlabel{ex:"):
            continue
        outer = brace_fields(line[len(r"\newlabel"):])
        fields = brace_fields(outer[1])
        labels[outer[0]] = {"printed_page": fields[1], "destination": fields[3]}
    reader = PdfReader(pdf)
    named = reader.named_destinations
    page_labels = reader.page_labels
    body = body_path.read_text(encoding="utf-8").split("\f")
    assert len(body) in (len(reader.pages), len(reader.pages) + 1)
    # Entire-line headings only: inline references such as 演習5.1と5.2 cannot match.
    heading_matches = {}
    for page_number, content in enumerate(body[:len(reader.pages)], 1):
        for match in re.finditer(r"(?m)^[ \t]*演習[ \t]*([1-9A]\.\d+)[ \t]*$", content):
            heading_matches.setdefault(match.group(1), []).append({"page": page_number, "line": match.group(0).strip()})
    toc = (ROOT / "build/String_Polchinski1_jp.toc").read_text(encoding="utf-8")
    exercise_toc_entries = [line for line in toc.splitlines() if re.search(r"演習\s*[1-9A]\.\d+", line)]
    results, issues = [], []
    for anchor in expected:
        number = anchor["number"]
        key = "ex:" + number
        record = mapped.get(number, {})
        label = labels.get(key, {})
        location = label.get("destination")
        dest_page = None
        if location in named:
            zero = reader.get_destination_page_number(named[location])
            if zero is not None and zero >= 0:
                dest_page = zero + 1
        aux_pages = [i + 1 for i, x in enumerate(page_labels) if str(x) == label.get("printed_page")]
        matches = heading_matches.get(number, [])
        body_pages = sorted(set(x["page"] for x in matches))
        source = (ROOT / anchor["file"]).read_text(encoding="utf-8")
        source_pattern = r"\\subsubsection\*\{演習\s*" + re.escape(number) + r"\}\s*\\label\{ex:" + re.escape(number) + r"\}"
        source_found = bool(re.search(source_pattern, source))
        item_issues = []
        if not source_found:
            item_issues.append("starred heading and matching label not found in source")
        if not record.get("resolved") or record.get("ambiguous"):
            item_issues.append("mapping unresolved or ambiguous")
        if len(body_pages) != 1 or len(matches) != 1:
            item_issues.append("body exercise heading not unique")
        if record.get("translated_pages") != body_pages:
            item_issues.append("mapping and visible body heading disagree")
        if aux_pages != body_pages:
            item_issues.append("aux page and visible body heading disagree")
        if body_pages != ([dest_page] if dest_page else []):
            item_issues.append("named destination and visible body heading disagree")
        item = {
            "number": number, "label": key, "source_page": anchor["source_page"],
            "source_file": anchor["file"], "label_present_in_original_research": bool(anchor.get("label")),
            "starred_source_heading_and_label_present": source_found,
            "mapped_pages": record.get("translated_pages", []), "resolution_method": record.get("resolution_method"),
            "aux_printed_page": label.get("printed_page"), "aux_physical_pages": aux_pages,
            "pdf_named_destination": location, "pdf_named_destination_physical_page": dest_page,
            "visible_body_heading_matches": matches, "status": "passed" if not item_issues else "failed", "issues": item_issues,
        }
        results.append(item)
        if item_issues:
            issues.append({"number": number, "issues": item_issues})
    if len(mapped_list) != 106 or len(mapped) != 106:
        issues.append({"global": "Exercise mapping count or uniqueness differs from 106"})
    if exercise_toc_entries:
        issues.append({"global": "Individual exercise entries remain in the TOC"})
    if pdf_hash != sha(pdf) or aux_hash != sha(aux):
        raise RuntimeError("Build inputs changed during audit; output not written")
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "status": "passed" if not issues else "failed",
        "pdf": "build/String_Polchinski1_jp.pdf", "pdf_sha256": pdf_hash, "aux_sha256": aux_hash,
        "pdf_page_count": len(reader.pages), "input_hashes": {"page_spans": sha(spans_path), "resolution_audit": sha(resolution_path), "visible_body_text": sha(body_path)},
        "method": "Independent auxiliary-label parser and PDF destination lookup; exact entire-line visible-body heading search for all 106 exercises. No proportional inference, TOC matching, or figure XObject text used.",
        "summary": {"expected_exercises": 106, "mapped_exercises": len(mapped_list), "unique_mapped_numbers": len(mapped),
            "passed": sum(x["status"] == "passed" for x in results), "failed": sum(x["status"] == "failed" for x in results),
            "original_labels": sum(bool(x.get("label")) for x in expected), "new_labels": sum(not x.get("label") for x in expected),
            "by_chapter": dict(Counter(x["number"].split(".")[0] for x in expected)), "individual_exercise_toc_entries": len(exercise_toc_entries)},
        "resolution_audit_summary": {k: resolution[k] for k in ("anchor_count", "resolved_anchor_count", "unresolved_anchors", "ambiguous_anchors")},
        "exercises": results, "issues": issues, "document_or_mapping_files_modified": False,
    }
    output = ROOT / "qa/exercise_anchor_audit.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], **report["summary"], "issues": issues}, ensure_ascii=False))


if __name__ == "__main__":
    main()
