"""Resolve original-page anchors to actual PDF pages without editing TeX/PDF.

Uses one PdfReader for destinations plus the body-only extraction helper.
The helper validates its analysis/text cache against the input PDF SHA-256.
Output ranges are conservative search ranges, not assertions that an index
term is present.
"""
from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata

from pypdf import PdfReader
from extract_body_text import extract_body_text


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def groups(text, offset=0):
    """Read successive brace groups (including nested groups)."""
    result = []
    while offset < len(text):
        while offset < len(text) and text[offset].isspace():
            offset += 1
        if offset >= len(text) or text[offset] != "{":
            break
        start = offset + 1
        level = 1
        offset += 1
        while offset < len(text) and level:
            if text[offset] == "{" and (offset == 0 or text[offset - 1] != "\\"):
                level += 1
            elif text[offset] == "}" and (offset == 0 or text[offset - 1] != "\\"):
                level -= 1
            offset += 1
        if level:
            break
        result.append(text[start:offset - 1])
    return result


GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "theta": "θ", "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν",
    "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "phi": "φ",
    "chi": "χ", "psi": "ψ", "omega": "ω", "Gamma": "Γ", "Delta": "Δ",
    "Theta": "Θ", "Lambda": "Λ", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ",
    "Omega": "Ω", "ell": "l", "infty": "∞",
}


def plain_tex(text):
    text = re.sub(r"\\(?:label|index)\{[^{}]*\}", "", text)
    for command, value in GREEK.items():
        text = re.sub(r"\\" + command + r"\b", lambda _: value, text)
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    return text.replace("\\", "").replace("{", "").replace("}", "").replace("$", "")


def normalized(text):
    text = unicodedata.normalize("NFKD", text).replace("µ", "μ")
    return "".join(c.casefold() for c in text if c.isalnum() and not unicodedata.combining(c))


def heading_text(text):
    match = re.search(r"\\(?:subsubsection|subsection|section)(?:link)?\*?\s*", text)
    if match:
        args = groups(text, match.end())
        if args:
            return args[0]
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--aux", type=Path)
    parser.add_argument("--research", type=Path)
    parser.add_argument("--entries", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--wide-threshold", type=int, default=5, help="Report ranges longer than this many physical PDF pages")
    args = parser.parse_args()
    root = args.root.resolve()
    pdf = args.pdf or root / "build/String_Polchinski1_jp.pdf"
    aux_path = args.aux or root / "build/String_Polchinski1_jp.aux"
    research_path = args.research or root / "indexing/page_mapping_research.json"
    entries_path = args.entries or root / "indexing/entries.json"
    output = args.output or root / "indexing/page_spans.json"
    text_path = root / "qa/page_span_pdf_text.txt"
    audit_path = root / "qa/page_span_resolution_audit.json"
    research = json.loads(research_path.read_text(encoding="utf-8"))
    entries = json.loads(entries_path.read_text(encoding="utf-8"))
    required = set()
    for entry in entries["entries"]:
        for ref in entry.get("source_references", []):
            required.update(ref.get("expanded_pages") or range(ref["start_page"], ref["end_page"] + 1))

    pdf_hash = digest(pdf)
    aux_hash = digest(aux_path)
    reader = PdfReader(pdf)
    page_count = len(reader.pages)
    named = reader.named_destinations
    destination_pages = {}
    for name, destination in named.items():
        number = reader.get_destination_page_number(destination)
        if number is not None and number >= 0:
            destination_pages[name] = number + 1
    pdf_page_labels = reader.page_labels
    page_label_lookup = defaultdict(list)
    for physical, label in enumerate(pdf_page_labels, 1):
        page_label_lookup[str(label)].append(physical)

    labels, toc = {}, []
    for line in aux_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\\newlabel", line)
        if match:
            outer = groups(line, match.end())
            if len(outer) >= 2:
                values = groups(outer[1])
                if len(values) >= 4:
                    labels[outer[0]] = {"printed_page": values[1], "destination": values[3]}
        match = re.search(r"\\contentsline\s*", line)
        if match:
            values = groups(line, match.end())
            if len(values) >= 4:
                numbered = re.search(r"\\numberline\s*\{([^{}]+)\}", values[1])
                toc.append({"level": values[0], "title": values[1], "number": numbered[1] if numbered else None,
                            "printed_page": values[2], "destination": values[3]})

    def location(item):
        dest = item.get("destination")
        candidates = page_label_lookup.get(item.get("printed_page", ""), [])
        if dest in destination_pages:
            if len(candidates) == 1 and candidates[0] != destination_pages[dest]:
                return candidates, "aux page label; inherited named destination is on another page"
            return [destination_pages[dest]], "PDF named destination"
        if len(candidates) == 1:
            return candidates, "aux page label resolved through PDF PageLabels"
        return [], "unresolved aux destination/page label"

    def label_location(label):
        return location(labels[label]) if label in labels else ([], "label absent from aux")

    expected_equations = {a["label"] for p in research["pages"] for a in p.get("equations", [])}
    absent_equations = sorted(expected_equations - labels.keys())
    mismatched_equations = []
    for key in expected_equations & labels.keys():
        item = labels[key]
        named_page = destination_pages.get(item["destination"])
        expected_pages = page_label_lookup.get(item["printed_page"], [])
        if named_page is None or (expected_pages and named_page not in expected_pages):
            mismatched_equations.append({"label": key, "aux_page_label": item["printed_page"], "pdf_destination_page": named_page})
    if absent_equations or mismatched_equations:
        raise RuntimeError(
            "PDF/aux do not form a complete matching build: "
            f"{len(absent_equations)} equation labels absent, {len(mismatched_equations)} destination/page mismatches. "
            "Rerun after the complete PDF and aux have both been produced."
        )

    section_pages = {}
    for item in toc:
        pages, _ = location(item)
        if pages:
            section_pages[(item["level"], item["number"])] = pages[0]
    named_section_starts = {}
    for item in toc:
        if item["level"] == "section":
            pages, _ = location(item)
            if pages:
                named_section_starts[normalized(plain_tex(item["title"]))] = pages[0]

    def find_section_start(title, default):
        key = normalized(title)
        return next((p for t, p in named_section_starts.items() if key == t), default)

    reference_start = find_section_start("参考文献", page_count)
    glossary_start = find_section_start("用語集", page_count)
    index_start = find_section_start("索引", page_count + 1)
    chapter_starts = {}
    for chapter in [str(i) for i in range(1, 10)] + ["A"]:
        pages, _ = label_location("app:A" if chapter == "A" else "ch:" + chapter)
        if pages:
            chapter_starts[chapter] = pages[0]
    ordered_chapters = [str(i) for i in range(1, 10)] + ["A"]
    chapter_scopes = {}
    for i, chapter in enumerate(ordered_chapters):
        start = chapter_starts.get(chapter, 1)
        end = chapter_starts.get(ordered_chapters[i + 1], reference_start) if i + 1 < len(ordered_chapters) else reference_start
        chapter_scopes[chapter] = (start, max(start, end - 1))
    original_chapter_starts = sorted({(p["source_page"], a["number"])
                                     for p in research["pages"] for a in p.get("chapter_headings", [])})

    def original_page_region(p):
        if p >= 359:
            return "glossary", (glossary_start, min(index_start - 1, page_count))
        if p >= 347:
            return "references", (reference_start, glossary_start - 1)
        chapter = next(ch for start, ch in reversed(original_chapter_starts) if start <= p)
        return "chapter " + chapter, chapter_scopes[chapter]

    # Embedded figure PDFs can retain invisible text outside their clip box.
    # The helper removes XObject invocations in an analysis copy before Poppler
    # extraction; the delivered PDF is never changed.
    process = extract_body_text(pdf, text_path, root / "build/index_text_body.pdf")
    if process.returncode:
        raise RuntimeError("Poppler extraction failed: " + process.stderr)
    texts = text_path.read_text(encoding="utf-8").split("\f")
    if texts and not texts[-1].strip():
        texts.pop()
    if len(texts) != page_count:
        raise RuntimeError(f"Poppler page count {len(texts)} != PDF page count {page_count}")
    norm_texts = [normalized(s) for s in texts]
    source_lines = {}

    def source_line(anchor):
        f = anchor.get("file")
        if not f or not anchor.get("line"):
            return ""
        if f not in source_lines:
            source_lines[f] = (root / f).read_text(encoding="utf-8").splitlines()
        n = anchor["line"] - 1
        return source_lines[f][n] if n < len(source_lines[f]) else ""

    def scope_for(anchor):
        f = anchor.get("file", "")
        match = re.search(r"ch(\d+)", f)
        if match:
            return chapter_scopes[str(int(match[1]))]
        if "appendixA" in f:
            return chapter_scopes["A"]
        if "glossary" in f:
            return glossary_start, min(index_start - 1, page_count)
        if "references_intro" in f:
            return reference_start, glossary_start - 1
        return 1, page_count

    def text_matches(phrase, scope):
        key = normalized(plain_tex(phrase))
        if not key:
            return []
        lo, hi = scope
        return [n for n in range(max(1, lo), min(page_count, hi) + 1) if key in norm_texts[n - 1]]

    equation_maxima = defaultdict(int)
    for key in labels:
        if key.startswith("eq:"):
            pages, _ = label_location(key)
            if pages:
                chapter = key[3:].split(".", 1)[0]
                equation_maxima[chapter] = max(equation_maxima[chapter], max(pages))

    resolved, methods = [], Counter()
    kinds = ["chapter_headings", "section_headings", "equations", "exercises", "figures",
             "glossary_entries", "manual_text_anchors", "reference_guide_headings", "bibliography_entries"]
    for page in research["pages"]:
        for kind in kinds:
            for sequence, anchor in enumerate(page.get(kind, [])):
                pages, method, attempted = [], "unresolved", []
                label = anchor.get("label")
                if label:
                    pages, method = label_location(label)
                if not pages and kind == "chapter_headings":
                    label = "app:A" if anchor["number"] == "A" else "ch:" + anchor["number"]
                    pages, method = label_location(label)
                if not pages and kind == "section_headings":
                    number = anchor["number"]
                    matching = [t for t in toc if t["level"] == "subsection" and t["number"] == number]
                    if matching:
                        pages, method = location(matching[0])
                if not pages and kind == "bibliography_entries":
                    destinations = ["cite." + k.strip() for k in anchor["bibtex_key"].split(",")]
                    if all(dest in destination_pages for dest in destinations):
                        pages = sorted(set(destination_pages[dest] for dest in destinations))
                        method = "PDF bibliography named destination (all volume keys)"
                if not pages and kind == "exercises":
                    # Later layout revisions add labels to exercises that were
                    # unlabelled when the research inventory was first made.
                    pages, method = label_location("ex:" + anchor["number"])
                if not pages and kind == "exercises":
                    # Starred exercise headings can have a TOC destination even
                    # when the original TeX did not define an ex: label.
                    title_key = normalized("演習" + anchor["number"])
                    matches = [t for t in toc if t["level"] == "subsubsection"
                               and normalized(plain_tex(t["title"])) == title_key]
                    if len(matches) == 1:
                        pages, method = location(matches[0])
                        method += "; exact exercise TOC destination"
                if not pages and kind == "exercises":
                    number = anchor["number"]
                    chapter = number.split(".", 1)[0]
                    lo, hi = chapter_scopes[chapter]
                    lo = max(lo, equation_maxima.get(chapter, lo))
                    pattern = re.compile(r"^[ \t]*" + re.escape(number) + r"(?:[ \t]{2,}|[ \t]*$)", re.M)
                    pages = [n for n in range(lo, min(hi, page_count) + 1) if pattern.search(texts[n - 1])]
                    method = "left-margin exercise number after final chapter equation"
                if not pages and kind in ("glossary_entries", "manual_text_anchors", "reference_guide_headings", "section_headings", "chapter_headings"):
                    if kind == "manual_text_anchors":
                        phrases = [anchor["tex_phrase"]]
                    elif kind == "glossary_entries":
                        phrases = [anchor["tex_heading"], anchor.get("english_match_key", "")]
                    else:
                        phrases = [heading_text(anchor.get("tex_heading") or source_line(anchor))]
                    for phrase in phrases:
                        attempted.append(phrase)
                        pages = text_matches(phrase, scope_for(anchor))
                        if pages:
                            method = "normalized exact PDF text match in anchored document region"
                            break
                    if len(pages) > 1 and kind == "manual_text_anchors":
                        line_text = source_line(anchor)
                        phrase = anchor["tex_phrase"]
                        if phrase in line_text:
                            extended = line_text[line_text.index(phrase):].split("\\footnote", 1)[0]
                            extended_pages = text_matches(extended, scope_for(anchor))
                            if extended_pages:
                                attempted.append(extended)
                                pages = extended_pages
                                method += "; exact extended passage disambiguates short phrase"
                    if len(pages) > 1 and kind == "reference_guide_headings":
                        key = normalized(plain_tex(phrases[0]))
                        standalone = [n for n in pages if any(normalized(line) == key for line in texts[n - 1].splitlines())]
                        if standalone:
                            pages = standalone
                            method += "; standalone heading line excludes inline references"
                item = {**anchor, "source_page": page["source_page"], "kind": kind, "sequence_in_kind": sequence,
                        "translated_pages": sorted(set(pages)), "resolution_method": method,
                        "resolved": bool(pages), "ambiguous": len(set(pages)) > 1 and kind != "bibliography_entries"}
                if attempted:
                    item["text_queries"] = attempted
                resolved.append(item)

    # Glossary entry order is an exact original/translation ordering constraint.
    glossary = sorted((a for a in resolved if a["kind"] == "glossary_entries"), key=lambda a: (a["source_page"], a.get("source_line", 0)))
    for i, anchor in enumerate(glossary):
        if len(anchor["translated_pages"]) <= 1:
            continue
        before = next((a["translated_pages"][0] for a in reversed(glossary[:i]) if len(a["translated_pages"]) == 1), glossary_start)
        after = next((a["translated_pages"][0] for a in glossary[i + 1:] if len(a["translated_pages"]) == 1), index_start - 1)
        constrained = [p for p in anchor["translated_pages"] if before <= p <= after]
        if constrained:
            anchor["original_text_candidate_pages"] = anchor["translated_pages"]
            anchor["translated_pages"] = constrained
            anchor["ambiguous"] = len(constrained) > 1
            anchor["resolution_method"] += "; bounded by surrounding uniquely matched glossary headings"

    by_source, floats = defaultdict(list), defaultdict(list)
    for anchor in resolved:
        methods[anchor["resolution_method"]] += 1
        if anchor["resolved"]:
            (floats if anchor["kind"] == "figures" else by_source)[anchor["source_page"]].append(anchor)
    for anchors in by_source.values():
        anchors.sort(key=lambda a: (a.get("source_line", 0), a["sequence_in_kind"]))

    available = sorted(by_source)
    result_pages = []
    for page in research["pages"]:
        p = page["source_page"]
        left_index, right_index = bisect_left(available, p) - 1, bisect_right(available, p)
        before_page = available[left_index] if left_index >= 0 else None
        after_page = available[right_index] if right_index < len(available) else None
        before = by_source[before_page][-1] if before_page is not None else None
        after = by_source[after_page][0] if after_page is not None else None
        own = by_source.get(p, [])
        candidates = [q for a in own for q in a["translated_pages"]]
        candidates += before["translated_pages"] if before else []
        candidates += after["translated_pages"] if after else []
        if not after and p >= 359:
            candidates.append(min(index_start - 1, page_count))
        if not candidates:
            raise RuntimeError(f"No conservative range is possible for original page {p}")
        lower, upper = min(candidates), max(candidates)
        before_clip = [lower, upper]
        region_name, region_bounds = original_page_region(p)
        lower, upper = max(lower, region_bounds[0]), min(upper, region_bounds[1])
        removed_all = lower > upper
        if removed_all:
            # A conservative full-region fallback is safer than guessing an
            # in-region page from anchors belonging to a neighbouring chapter.
            lower, upper = region_bounds
        def compact(a):
            return {k: a[k] for k in ("source_page", "kind", "number", "label", "file", "line", "source_line", "tex_heading", "translated_pages", "resolution_method") if k in a} if a else None
        result_pages.append({
            "source_page": p, "source_pdf_page": page["source_pdf_page"], "required_by_index": p in required,
            "translated_pages": list(range(lower, upper + 1)), "translated_page_range": [lower, upper],
            "document_region": region_name, "region_translated_page_range": list(region_bounds),
            "preclip_translated_page_range": before_clip,
            "chapter_or_section_boundary_clip_applied": before_clip != [lower, upper],
            "clipping_removed_all_anchor_pages": removed_all,
            "own_anchor_pages": sorted(set(q for a in own for q in a["translated_pages"])),
            "own_anchor_count": len(own), "previous_original_page_last_anchor": compact(before),
            "next_original_page_first_anchor": compact(after),
            "figure_candidate_pages": sorted(set(q for a in floats.get(p, []) for q in a["translated_pages"])),
            "used_nonadjacent_original_page_boundary": (before_page is not None and before_page != p - 1) or (after_page is not None and after_page != p + 1),
            "range_is_search_candidate_only": True,
        })

    if digest(pdf) != pdf_hash or digest(aux_path) != aux_hash:
        raise RuntimeError("PDF or aux changed during resolution; rerun after the build finishes.")
    missing_required = sorted(required - {p["source_page"] for p in result_pages})
    if missing_required:
        raise RuntimeError("Required original pages absent from research: " + str(missing_required))
    unresolved = [a for a in resolved if not a["resolved"]]
    ambiguous = [a for a in resolved if a["ambiguous"]]
    wide = [p for p in result_pages if len(p["translated_pages"]) > args.wide_threshold]
    report = {
        "schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "pdf": str(pdf), "pdf_sha256": pdf_hash, "aux": str(aux_path), "aux_sha256": aux_hash,
        "pdf_page_count": page_count, "physical_pdf_page_numbers": True, "pdf_page_labels": pdf_page_labels,
        "required_source_pages": sorted(required), "pages": result_pages,
        "anchors": resolved,
        "method": "All current-page nonfloat anchors plus the preceding original page's last and following page's first resolved nonfloat anchors. Fall back outward only where an adjacent original page has no resolved nonfloat anchor. Clip to chapter/reference/glossary boundaries established by named destinations. Figure anchors remain separate candidates.",
        "limitations": "Ranges are conservative PDF search scopes. Only term-specific actual text occurrences justify narrowing. No proportional page conversion is used.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "created_utc": report["created_utc"], "pdf_sha256": pdf_hash, "pdf_page_count": page_count,
        "source_pages": len(result_pages), "required_source_pages": len(required), "missing_required_source_pages": missing_required,
        "anchor_count": len(resolved), "resolved_anchor_count": len(resolved) - len(unresolved),
        "resolution_methods": dict(methods), "unresolved_anchors": unresolved, "ambiguous_anchors": ambiguous,
        "wide_threshold": args.wide_threshold, "wide_ranges": wide,
        "required_pages_without_own_anchor": [p for p in result_pages if p["required_by_index"] and not p["own_anchor_count"]],
        "text_extraction": str(text_path), "poppler_stderr": process.stderr.strip(),
    }
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pdf_pages": page_count, "source_pages": len(result_pages), "required_source_pages": len(required),
                      "anchors": len(resolved), "unresolved": len(unresolved), "ambiguous": len(ambiguous),
                      "wide_ranges": len(wide), "output": str(output)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
