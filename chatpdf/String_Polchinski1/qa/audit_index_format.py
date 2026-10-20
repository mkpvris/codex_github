"""Read-only audit of generated MakeIndex files; writes index_format_audit.json.

Run after the final index generation for a complete .idx hash check. While
LaTeX is running, .idx may temporarily be empty; .ind/.ilg are still audited.
No TeX, MakeIndex, generator, or approval operation is invoked.
"""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import runpy


ROOT = Path(__file__).resolve().parents[1]
STEM = "String_Polchinski1_jp"


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


def split_key(key):
    """Decode sort@display!components without splitting quoted metacharacters."""
    parts = []
    sort = display = ""
    in_display = False
    i = 0
    backslashes = 0
    while i < len(key):
        char = key[i]
        quoted = char == '"' and backslashes % 2 == 0
        if quoted:
            i += 1
            if i == len(key):
                raise ValueError("Dangling MakeIndex quote")
            char = key[i]
        elif char == "@" and not in_display:
            in_display = True
            i += 1
            backslashes = 0
            continue
        elif char == "!":
            parts.append((sort, normalized(display)))
            sort = display = ""
            in_display = False
            i += 1
            backslashes = 0
            continue
        if in_display:
            display += char
        else:
            sort += char
        backslashes = backslashes + 1 if char == "\\" else 0
        i += 1
    parts.append((sort, normalized(display)))
    return tuple(parts)


def main():
    paths = {
        "entries": ROOT / "indexing/entries.json",
        "helper": ROOT / "indexing/index_format.py",
        "idx": ROOT / "build" / (STEM + ".idx"),
        "ind": ROOT / "build" / (STEM + ".ind"),
        "ilg": ROOT / "build" / (STEM + ".ilg"),
        "generation_audit": ROOT / "qa/index_translation_page_audit.json",
    }
    raw = {name: path.read_bytes() for name, path in paths.items()}
    entries = json.loads(raw["entries"])["entries"]
    by_id = {entry["id"]: entry for entry in entries}
    helper = runpy.run_path(str(paths["helper"]))
    parse_group = runpy.run_path(str(ROOT / "indexing/parse_legacy_index.py"))["parse_group"]
    generation = json.loads(raw["generation_audit"])
    ind = raw["ind"].decode("utf-8-sig")
    ilg = raw["ilg"].decode("utf-8-sig")
    expected_paths = {}
    entry_paths = {}
    qualified_paths = {}
    expected_cross = Counter()
    for entry in entries:
        components = split_key(helper["key_for"](entry, by_id))
        entry_paths[entry["id"]] = tuple(display for _, display in components)
        for end in range(1, len(components) + 1):
            expected_paths[tuple(display for _, display in components[:end])] = components[end - 1][0]
        for reference in entry["source_references"]:
            if reference["qualifier_english_tex"] or reference["qualifier_japanese_tex"]:
                key = helper["qualified_key_for"](entry, by_id, reference)
                qualified = split_key(key)
                display_path = tuple(display for _, display in qualified)
                qualified_paths[reference["qualifier_english_tex"]] = display_path
                expected_paths[display_path] = qualified[-1][0]
        for record in helper["cross_reference_records"](entry, by_id):
            path = tuple(display for _, display in split_key(record["key"]))
            encap = record["encap"]
            text, _ = parse_group(encap, encap.index("{"))
            expected_cross[(path, normalized(text), str(record.get("page", 0)))] += 1

    possible_children = defaultdict(list)
    for path in expected_paths:
        possible_children[path[:-1]].append(path[-1])
    actual_paths = []
    actual_cross = Counter()
    unmatched_blocks = []
    order_violations = []
    previous_sort = {}
    matches = list(re.finditer(r"(?m)^\s*\\(item|subitem|subsubitem)\s+", ind))
    stack = []
    for ordinal, match in enumerate(matches):
        level = {"item": 0, "subitem": 1, "subsubitem": 2}[match.group(1)]
        block = ind[match.end():matches[ordinal + 1].start() if ordinal + 1 < len(matches) else len(ind)]
        text = normalized(block)
        parent = tuple(stack[:level])
        candidates = [label for label in possible_children[parent] if text.startswith(label) and
                      (len(text) == len(label) or text[len(label)] in " ,\\")]
        if not candidates:
            unmatched_blocks.append({"ordinal": ordinal, "level": level, "parent": parent, "text": text[:300]})
            continue
        label = max(candidates, key=len)
        path = parent + (label,)
        stack = list(path)
        actual_paths.append(path)
        sort = expected_paths[path]
        if parent in previous_sort and previous_sort[parent] > sort:
            order_violations.append({"parent": parent, "previous": previous_sort[parent], "current": sort})
        previous_sort[parent] = sort
        for xref in re.finditer(r"\\indexcrossref(?=\{)", block):
            text_arg, cursor = parse_group(block, xref.end())
            while block[cursor].isspace():
                cursor += 1
            page_arg, _ = parse_group(block, cursor)
            actual_cross[(path, normalized(text_arg), page_arg)] += 1
    actual_set = set(actual_paths)
    coverage = []
    missing_entries = []
    for entry in entries:
        path = entry_paths[entry["id"]]
        if entry["is_cross_reference_continuation"]:
            retained = path in actual_set and all(
                actual_cross[(tuple(d for _, d in split_key(record["key"])),
                              normalized(parse_group(record["encap"], record["encap"].index("{"))[0]), "0")] > 0
                for record in helper["cross_reference_records"](entry, by_id))
            method = "cross_reference_on_parent"
        elif path in actual_set:
            retained = True
            method = "displayed_heading"
        else:
            # The level-2 'in terms of' parent is retained in both flattened
            # parent: child labels, rather than as a redundant empty heading.
            children = [by_id[c] for c in entry["child_ids"]]
            merged_children = [c for c in children if c["level"] == 3 and entry_paths[c["id"]] in actual_set]
            retained = entry["level"] == 2 and bool(merged_children) and len(merged_children) == len(children)
            method = "retained_in_merged_child_labels" if retained else "missing"
        coverage.append({"id": entry["id"], "retained": retained, "method": method})
        if not retained:
            missing_entries.append({"id": entry["id"], "display_path": path})
    scan = re.search(r"\((\d+) entries accepted, (\d+) rejected\)", ilg)
    warnings = re.search(r"\d+ lines written, (\d+) warnings", ilg)
    accepted, rejected = (int(scan[1]), int(scan[2])) if scan else (None, None)
    warning_count = int(warnings[1]) if warnings else None
    idx_pending = not raw["idx"]
    idx_hash_matches = None if idx_pending else hashlib.sha256(raw["idx"]).hexdigest() == generation["idx_sha256"]
    idx_records = None if idx_pending else len(re.findall(rb"(?m)^\\indexentry\{", raw["idx"]))
    collapsed = [{"id": e["id"], "display_path": entry_paths[e["id"]],
                  "retained": entry_paths[e["id"]] in actual_set} for e in entries if e["level"] == 3]
    qualifiers = [{"english": label, "display_path": path, "retained": path in actual_set}
                  for label, path in qualified_paths.items()]
    checks = {
        "all_1050_entries_retained": len(entries) == 1050 and not missing_entries,
        "all_ind_headings_recognized": not unmatched_blocks,
        "english_ascii_sort_keys_in_order": not order_violations,
        "two_four_level_entries_retained_after_collapse": len(collapsed) == 2 and all(x["retained"] for x in collapsed),
        "two_qualifier_labels_retained": len(qualifiers) == 2 and all(x["retained"] for x in qualifiers),
        "all_29_cross_references_retained": sum(expected_cross.values()) == 29 and actual_cross == expected_cross,
        "zero_rejected_rows": rejected == 0,
        "zero_makeindex_warnings": warning_count == 0,
        "accepted_count_matches_generation": accepted == generation["makeindex_records"],
        "idx_hash_matches_generation": idx_hash_matches,
        "idx_count_matches_accepted": None if idx_pending else idx_records == accepted,
    }
    failures = [name for name, value in checks.items() if value is False]
    report = {
        "status": "failed" if failures else "passed_pending_final_idx" if idx_pending else "passed",
        "scope": "Read-only .ind/.ilg/.idx and source-structure audit; no build or generator invoked.",
        "files": {name: {"path": str(path.relative_to(ROOT)), "bytes": len(raw[name]),
                         "sha256": hashlib.sha256(raw[name]).hexdigest()} for name, path in paths.items()},
        "checks": checks,
        "counts": {"legacy_entries": len(entries), "ind_headings": len(actual_paths),
                   "accepted_records": accepted, "rejected_records": rejected, "makeindex_warnings": warning_count,
                   "cross_references_expected": sum(expected_cross.values()), "cross_references_found": sum(actual_cross.values()),
                   "coverage_methods": dict(Counter(x["method"] for x in coverage))},
        "collapsed_four_level_entries": collapsed,
        "qualified_labels": qualifiers,
        "missing_entries": missing_entries,
        "unmatched_ind_blocks": unmatched_blocks,
        "sort_order_violations": order_violations,
        "cross_reference_missing": [{"path": p, "text": t, "page_argument": n, "count": c}
                                    for (p, t, n), c in (expected_cross - actual_cross).items()],
        "cross_reference_unexpected": [{"path": p, "text": t, "page_argument": n, "count": c}
                                       for (p, t, n), c in (actual_cross - expected_cross).items()],
        "entry_coverage": coverage,
        "notes": ["The temporary empty .idx is expected during LaTeX's makeindex initialization. Re-run this audit after final generation."] if idx_pending else [],
    }
    (ROOT / "qa/index_format_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": checks, "counts": report["counts"],
                      "failures": failures, "missing_entries": missing_entries,
                      "unmatched_ind_blocks": unmatched_blocks[:3], "sort_order_violations": order_violations[:5]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
