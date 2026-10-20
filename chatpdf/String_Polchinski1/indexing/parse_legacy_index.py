#!/usr/bin/env python3
"""Parse the bilingual legacy index without changing its TeX source.

Run from any directory with Python 3.10+; no third-party packages are required.
The immutable default input is indexing/index_legacy.tex. The default outputs
are indexing/entries.json and qa/index_makeidx_parse_audit.json.
Display TeX is retained verbatim. English math transcriptions below affect sorting
only; they never replace the displayed mathematical expressions.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata


MATH_SORT_NAMES = {
    r"c=1": "c equals 1",
    r"bc": "bc",
    r"\beta\gamma": "beta gamma",
    r"\chi": "chi",
    r"T": "T",
    r"CPT": "CPT",
    r"[\alpha_m^\mu,\alpha_n^\nu]": "alpha oscillator commutator",
    r"\{b_n,c_n\}": "b c ghost anticommutator",
    r"[\delta_{\tau_1},\delta_{\tau_2}]": "delta tau transformation commutator",
    r"[G_I,G_J]": "G constraint commutator",
    r"[j_m^i,j_n^j]": "j current mode commutator",
    r"[L_m,L_n]": "L Virasoro generator commutator",
    r"[L_m,\mathcal O_n]": "L Virasoro generator O operator commutator",
    r"[N^{\mathrm g},b_m]": "N ghost number b ghost commutator",
    r"[N^{\mathrm g},c_m]": "N ghost number c ghost commutator",
    r"[p_\mu,x^\nu]": "p momentum x position commutator",
    r"[Q,\mathcal A]": "Q charge A operator commutator",
    r"[Q_1,Q_2]": "Q charge Q charge commutator",
    r"\{Q_B,b_m\}": "Q BRST charge b ghost anticommutator",
    r"\{Q_B,L_m\}": "Q BRST charge L Virasoro generator anticommutator",
    r"\{Q_B,Q_B\}": "Q BRST charge Q BRST charge anticommutator",
    r"[X_L(z),X_L(z')]": "X left moving field commutator",
    r"\times": "times",
    r"d\geq3": "d greater than or equal to 3",
    r"A": "A",
    r"B": "B",
    r"SO(8192)": "SO 8192",
    r"L_0": "L zero",
    r"X^\mu": "X mu",
    r"T_{ab}": "T ab energy momentum tensor",
    r"\exp(-1/g_{\mathrm c})": "exponential of minus one over closed string coupling",
    r"O(k,k,\mathbb R)": "O k k real",
    r"O(k,k,\mathbb Z)": "O k k integer",
    r"z": "z",
    r"\bar z": "z bar",
    r"\mathcal A_i\,\mathcal A_j": "A i A j operator product",
    r"b\,b": "b b ghost operator product",
    r"b\,c": "b c ghost operator product",
    r"c\,c": "c c ghost operator product",
    r"\beta\,\beta": "beta beta operator product",
    r"\beta\,\gamma": "beta gamma operator product",
    r"\gamma\,\gamma": "gamma gamma operator product",
    r"\partial X^\mu\,\partial X_\mu": "partial X mu partial X mu operator product",
    r":e^{ik\cdot X}:\,{:e^{ik'\cdot X}:}": "exponential vertex exponential vertex operator product",
    r":\mathcal F:\,{:\mathcal G:}": "F G normal ordered operator product",
    r"j_{\mathrm B}\,b": "j BRST current b ghost operator product",
    r"j_{\mathrm B}\,c": "j BRST current c ghost operator product",
    r"j_{\mathrm B}\,\mathcal O^{\mathrm m}": "j BRST current matter operator product",
    r"j_{\mathrm B}\,j_{\mathrm B}": "j BRST current j BRST current operator product",
    r"j_{\mathrm B}\,\mathcal V": "j BRST current V vertex operator product",
    r"j^i\,j^j": "j i j j current operator product",
    r"j^\mu\,{:e^{ik\cdot X}:}": "j mu current exponential vertex operator product",
    r"\mathcal O_i\,\mathcal O_j": "O i O j operator product",
    r"T\,\mathcal A": "T energy momentum tensor A operator product",
    r"T\,e^{ik\cdot X}": "T energy momentum tensor exponential vertex operator product",
    r"T\,j": "T energy momentum tensor j current operator product",
    r"T\,j_{\mathrm B}": "T energy momentum tensor j BRST current operator product",
    r"T\,\mathcal O": "T energy momentum tensor O operator product",
    r"T\,T": "T energy momentum tensor T energy momentum tensor operator product",
    r"T\,\widetilde T": "T energy momentum tensor T tilde operator product",
    r"\mathcal V\,\mathcal V'": "V vertex V prime vertex operator product",
    r"X_{\mathrm L}\,X_{\mathrm L}": "X left X left operator product",
    r"X_{\mathrm L}\,X_{\mathrm R}": "X left X right operator product",
    r"X_{\mathrm R}\,X_{\mathrm R}": "X right X right operator product",
    r"X^\mu\,X^\nu": "X mu X nu operator product",
    r"PSL(2,\mathbb C)": "PSL 2 complex",
    r"PSL(2,\mathbb R)": "PSL 2 real",
    r"PSL(2,\mathbb Z)": "PSL 2 integer",
    r"b_0": "b zero",
    r"SL(2,\mathbb C)": "SL 2 complex",
    r"SL(2,\mathbb R)": "SL 2 real",
    r"SO(D-2)": "SO D minus 2",
    r"SO(D-1)": "SO D minus 1",
    r"SO(n)": "SO n",
    r"Sp(k)": "Sp k",
    r"SU(n)": "SU n",
    r"SU(2)\times SU(2)": "SU 2 times SU 2",
    r"SU(3)\times SU(2)\times U(1)": "SU 3 times SU 2 times U 1",
    r"S": "S",
    r"s,t,u": "s t u",
    r"U(n)": "U n",
    r"L_{-1}\cdot": "L minus one action",
    r"L_0\cdot": "L zero action",
    r"R\to0": "R approaches zero",
}

REFERENCE_MARKERS = (
    ("の補集合を参照", "see_complement", "see complement of"),
    ("の項を参照", "see_under", "see under"),
    ("も参照", "see_also", "see also"),
    ("を参照", "see", "see"),
    ("と同じ", "same_as", "same as"),
)


def parse_group(text: str, start: int) -> tuple[str, int]:
    """Read one balanced TeX argument; escaped braces are not group delimiters."""
    if text[start] != "{":
        raise ValueError(f"Expected '{{' at offset {start}")
    depth = 1
    i = start + 1
    while i < len(text):
        if text[i] == "\\":
            i += 2  # Escaped braces, or the first character of a control word.
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
        i += 1
    raise ValueError(f"Unclosed TeX group at offset {start}")


def ascii_sort_key(english_tex: str) -> tuple[str, list[dict]]:
    substitutions = []

    def replace_math(match):
        expression = match.group(1)
        if expression not in MATH_SORT_NAMES:
            raise ValueError(f"Unmapped math sort expression: {expression!r}")
        words = MATH_SORT_NAMES[expression]
        substitutions.append({"math_tex": expression, "english_sort_text": words})
        return " " + words + " "

    words = re.sub(r"\$([^$]*)\$", replace_math, english_tex)
    if "\\" in words:
        raise ValueError(f"Unmapped TeX control sequence in label: {english_tex!r}")
    words = unicodedata.normalize("NFKD", words)
    words = "".join(c for c in words if not unicodedata.combining(c))
    if any(ord(c) > 127 and c.isalpha() for c in words):
        raise ValueError(f"Non-Latin name needs an explicit English sort key: {english_tex!r}")
    # Keep makeindex's metacharacters ! @ | and quote out of sort keys.
    key = re.sub(r"[^a-z0-9]+", " ", words.lower()).strip()
    return key, substitutions


def strip_italics(tex: str) -> tuple[str, list[tuple[int, int]]]:
    plain = ""
    spans = []
    offset = 0
    for match in re.finditer(r"\\textit\{([^{}]*)\}", tex):
        plain += tex[offset : match.start()]
        begin = len(plain)
        plain += match.group(1)
        spans.append((begin, len(plain)))
        offset = match.end()
    plain += tex[offset:]
    return plain, spans


def expand_range_end(first: int, printed_end: str) -> int:
    last = int(printed_end)
    if len(printed_end) < len(str(first)):
        modulus = 10 ** len(printed_end)
        last += first // modulus * modulus
        if last < first:
            last += modulus
    if last < first:
        raise ValueError(f"Descending reference range: {first}–{printed_end}")
    return last


def parse_page_references(tex: str) -> tuple[list[dict], list[dict]]:
    references = []
    groups = []
    if not tex.strip():
        return references, groups
    for group_no, group_tex in enumerate(tex.split("；")):
        plain, italics = strip_italics(group_tex)
        qualifier_japanese = qualifier_english = ""
        qualifier = re.match(r"\s*(.*?)（(.*?)）\s*", plain)
        numeric_start = 0
        if qualifier:
            qualifier_japanese, qualifier_english = qualifier.groups()
            numeric_start = qualifier.end()
        matches = list(re.finditer(r"(?P<start>\d+)(?:[–−-](?P<end>\d+))?(?P<ff>ff)?", plain[numeric_start:]))
        remaining = re.sub(r"\d+(?:[–−-]\d+)?(?:ff)?", "", plain[numeric_start:])
        if remaining.strip(" ,\t\r\n"):
            raise ValueError(f"Unparsed reference material: {group_tex!r}")
        first_ref = len(references)
        for match in matches:
            first = int(match.group("start"))
            printed_end = match.group("end")
            last = expand_range_end(first, printed_end) if printed_end else first
            begin = numeric_start + match.start()
            end = numeric_start + match.end()
            italic = any(a <= begin and end <= b for a, b in italics)
            raw = match.group(0)
            references.append({
                "raw_tex": r"\textit{" + raw + "}" if italic else raw,
                "raw_text": raw,
                "start_page": first,
                "end_page": last,
                "printed_range_end": printed_end,
                "is_range": printed_end is not None,
                "expanded_pages": list(range(first, last + 1)),
                "italic": italic,
                "refers_to_exercise": italic,
                "following_unspecified": bool(match.group("ff")),
                "group_index": group_no,
                "qualifier_japanese_tex": qualifier_japanese,
                "qualifier_english_tex": qualifier_english,
            })
        groups.append({
            "raw_tex": group_tex,
            "qualifier_japanese_tex": qualifier_japanese,
            "qualifier_english_tex": qualifier_english,
            "reference_indices": list(range(first_ref, len(references))),
        })
    return references, groups


def split_targets(text: str) -> list[str]:
    depth = 0
    start = 0
    parts = []
    for i, char in enumerate(text):
        if char in "（(":
            depth += 1
        elif char in "）)":
            depth -= 1
        elif char == "、" and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    parts.append(text[start:].strip())
    return parts


def parse_cross_reference(tex: str) -> dict | None:
    for suffix, kind, original_marker in REFERENCE_MARKERS:
        if tex.endswith(suffix):
            body = tex[: -len(suffix)].strip()
            break
    else:
        return None
    shared_qualifier = ""
    if body.endswith("の各 CFT"):
        body = body[: -len("の各 CFT")]
        shared_qualifier = "CFT"
    # These are hierarchical destinations, not two independent destinations.
    hierarchy_overrides = {
        "作用（action）、Polyakov": ["action", "Polyakov"],
        "経路積分（path integral）、Polyakov": ["path integral", "Polyakov"],
        "ハンドル、退化（handle, degenerating）": ["handle", "degenerating"],
    }
    fragments = [body] if body in hierarchy_overrides else split_targets(body)
    targets = []
    for fragment in fragments:
        labeled = re.fullmatch(r"(.*?)（(.*?)）", fragment)
        if labeled:
            japanese, english = labeled.groups()
        else:
            japanese = ""
            english = fragment
        path = hierarchy_overrides.get(body)
        if path:
            english = ", ".join(path)
            japanese = fragment
        elif shared_qualifier:
            english += " " + shared_qualifier
        key, substitutions = ascii_sort_key(english)
        targets.append({
            "raw_tex": fragment,
            "japanese_tex": japanese,
            "english_tex": english,
            "english_path_tex": path or [english],
            "sort_key": key,
            "math_sort_substitutions": substitutions,
            "generic_reference": english == "specific gauges",
        })
    return {
        "type": kind,
        "original_english_marker": original_marker,
        "raw_tex": tex,
        "targets": targets,
        "shared_qualifier": shared_qualifier,
    }


def parse_document(text: str) -> list[dict]:
    entries = []
    stack = []
    page_markers = [(m.start(), int(m.group(1))) for m in re.finditer(r"^% Original index: p\.(\d+)", text, re.M)]
    for match in re.finditer(r"^\\idx(?=\{)", text, re.M):
        cursor = match.end()
        args = []
        for _ in range(4):
            while text[cursor].isspace():
                cursor += 1
            argument, cursor = parse_group(text, cursor)
            args.append(argument)
        level_string, japanese, english, ref_tex = args
        level = int(level_string)
        if level > len(stack):
            raise ValueError(f"Hierarchy jumps from {len(stack) - 1} to {level}")
        stack = stack[:level]
        entry_id = f"idx{len(entries) + 1:04d}"
        parent_id = stack[-1] if stack else None
        crossref = parse_cross_reference(ref_tex)
        continuation = not japanese and not english
        if continuation and not crossref:
            raise ValueError(f"Unnamed entry has no cross-reference: {entry_id}")
        effective_english = english or japanese
        if continuation:
            sort_key = crossref["original_english_marker"]
            math_substitutions = []
        else:
            sort_key, math_substitutions = ascii_sort_key(effective_english)
        references, reference_groups = ([], []) if crossref else parse_page_references(ref_tex)
        original_page = next((p for offset, p in reversed(page_markers) if offset < match.start()), None)
        entry = {
            "id": entry_id,
            "source_order": len(entries) + 1,
            "source_line": text.count("\n", 0, match.start()) + 1,
            "original_index_page": original_page,
            "level": level,
            "parent_id": parent_id,
            "ancestor_ids": list(stack),
            "child_ids": [],
            "japanese_tex": japanese,
            "english_tex": english,
            "effective_english_tex": effective_english,
            "english_is_fallback": not bool(english),
            "sort_key": sort_key,
            "math_sort_substitutions": math_substitutions,
            "display_english_first_tex": english + "（" + japanese + "）" if english and japanese else effective_english,
            "is_cross_reference_continuation": continuation,
            "cross_reference_owner_id": parent_id if continuation else entry_id,
            "reference_raw_tex": ref_tex,
            "source_references": references,
            "reference_groups": reference_groups,
            "cross_references": [crossref] if crossref else [],
            "legacy_arguments": args,
            "legacy_raw_tex": text[match.start():cursor],
        }
        entries.append(entry)
        if parent_id:
            entries[int(parent_id[3:]) - 1]["child_ids"].append(entry_id)
        stack.append(entry_id)
    return entries


def make_audit(entries: list[dict], source_info: dict) -> dict:
    levels = Counter(e["level"] for e in entries)
    kinds = Counter(x["type"] for e in entries for x in e["cross_references"])
    math_uses = defaultdict(list)
    collision_groups = defaultdict(list)
    crossref_rows = []
    following = []
    for entry in entries:
        for substitution in entry["math_sort_substitutions"]:
            math_uses[substitution["math_tex"]].append(entry["id"])
        if not entry["is_cross_reference_continuation"]:
            collision_groups[(entry["parent_id"], entry["sort_key"])].append(entry["id"])
        for reference in entry["source_references"]:
            if reference["following_unspecified"]:
                following.append({"entry_id": entry["id"], "raw_text": reference["raw_text"]})
        for crossref in entry["cross_references"]:
            crossref_rows.append({
                "entry_id": entry["id"], "owner_id": entry["cross_reference_owner_id"],
                "source_line": entry["source_line"], "english_tex": entry["effective_english_tex"],
                **crossref,
            })
    refs = [r for e in entries for r in e["source_references"]]
    counts = {
        "entries": len(entries),
        "levels": {str(k): v for k, v in sorted(levels.items())},
        "max_level": max(levels),
        "named_entries": sum(not e["is_cross_reference_continuation"] for e in entries),
        "unnamed_cross_reference_continuations": sum(e["is_cross_reference_continuation"] for e in entries),
        "source_reference_tokens": len(refs),
        "range_reference_tokens": sum(r["is_range"] for r in refs),
        "italic_reference_tokens": sum(r["italic"] for r in refs),
        "italic_tokens_by_original_index_page": {
            str(page): sum(r["italic"] for e in entries if e["original_index_page"] == page for r in e["source_references"])
            for page in sorted({e["original_index_page"] for e in entries})
        },
        "cross_reference_rows": len(crossref_rows),
        "cross_reference_targets": sum(len(x["targets"]) for x in crossref_rows),
        "cross_reference_types": dict(sorted(kinds.items())),
        "entries_with_math_sort_substitutions": sum(bool(e["math_sort_substitutions"]) for e in entries),
        "unique_math_sort_expressions": len(math_uses),
        "following_unspecified_references": len(following),
    }
    warnings = []
    for entry in entries:
        if entry["level"] >= 3:
            warnings.append({
                "type": "makeindex_depth_exceeds_three",
                "entry_id": entry["id"], "level": entry["level"],
                "path_ids": entry["ancestor_ids"] + [entry["id"]],
                "action": "Preserved unchanged; generator must combine the two lowest labels.",
            })
    return {
        "source": source_info,
        "counts": counts,
        "validation": {
            "all_four_arguments_preserved": all(len(e["legacy_arguments"]) == 4 for e in entries),
            "all_argument_roundtrips_exact": all(e["legacy_raw_tex"] == r"\idx" + "".join("{" + a + "}" for a in e["legacy_arguments"]) for e in entries),
            "all_sort_keys_ascii_and_safe": all(bool(re.fullmatch(r"[a-z0-9 ]+", e["sort_key"])) for e in entries),
            "all_parent_depths_preserved": all(len(e["ancestor_ids"]) == e["level"] for e in entries),
            "all_reference_tokens_parsed": True,
            "all_original_page_ranges_valid": all(1 <= r["start_page"] <= r["end_page"] <= 402 for r in refs),
            "unknown_math_expressions": [],
            "translation_page_numbers_assigned": False,
            "source_modified": False,
        },
        "warnings": warnings,
        "same_parent_sort_key_collisions": [
            {"parent_id": p, "sort_key": k, "entry_ids": ids}
            for (p, k), ids in collision_groups.items() if len(ids) > 1
        ],
        "cross_references": crossref_rows,
        "math_sort_substitutions": [
            {"math_tex": math, "english_sort_text": MATH_SORT_NAMES[math], "entry_ids": ids}
            for math, ids in math_uses.items()
        ],
        "following_unspecified_references": following,
        "notes": [
            "English and Japanese display labels are kept as original TeX; ASCII keys affect sorting only.",
            "Blank-name cross-reference rows belong to their parent and must not become separate index headings.",
            "same_as, see_under, and see_complement preserve the original semantics rather than silently becoming see.",
            "ff references retain their explicit first page; an unspecified ending is never invented.",
            "This parser preserves original page references; assigning translated PDF pages is a separate generation step.",
        ],
    }


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=project / "indexing/index_legacy.tex")
    parser.add_argument("--output", type=Path, default=project / "indexing/entries.json")
    parser.add_argument("--audit", type=Path, default=project / "qa/index_makeidx_parse_audit.json")
    options = parser.parse_args()
    raw = options.input.read_bytes()
    text = raw.decode("utf-8-sig")
    entries = parse_document(text)
    source_info = {
        "path": options.input.relative_to(project).as_posix() if options.input.is_relative_to(project) else str(options.input),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "encoding": "UTF-8",
        "original_index_pages": sorted({e["original_index_page"] for e in entries}),
    }
    audit = make_audit(entries, source_info)
    if len(entries) != 1050:
        raise ValueError(f"Expected 1050 legacy entries, found {len(entries)}")
    if audit["counts"]["italic_reference_tokens"] != 120:
        raise ValueError("The 120 original italic numeric references were not all preserved")
    if not all(v for k, v in audit["validation"].items() if k.startswith("all_")):
        raise ValueError("Parse validation failed")
    document = {"schema_version": 1, "source": source_info, "counts": audit["counts"], "entries": entries}
    output = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    audit["entries_json_sha256"] = hashlib.sha256(output).hexdigest()
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.audit.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_bytes(output)
    options.audit.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if options.input.read_bytes() != raw:
        raise RuntimeError("Legacy source changed during parsing")
    print(json.dumps(audit["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
