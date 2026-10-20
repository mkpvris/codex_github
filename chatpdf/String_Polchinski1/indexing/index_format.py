"""Pure formatting helpers for the translated MakeIndex index.

API:
    key_for(entry, by_id) -> str
        ASCII-sort@English (Japanese) components, joined by !; no encapsulator.
    qualified_key_for(entry, by_id, reference) -> str
        Same, with a reference qualifier appended to the terminal component.
    cross_reference_records(entry, by_id) -> list[dict]
        Each dict has key, encap, and page=0. Write it as
        \\indexentry{KEY|ENCAP}{0} without adding hyperpage.

Required preamble definition (the second argument deliberately disappears):
    \\DeclareRobustCommand{\\indexcrossref}[2]{#1}

This module performs no file writes or builds. Display TeX is retained.
"""

from __future__ import annotations

import re
import unicodedata


LATEX_ENCAP_DEFINITION = r"\DeclareRobustCommand{\indexcrossref}[2]{#1}"


def escape_makeindex(text: str) -> str:
    """Quote MakeIndex's four metacharacters; leave TeX display intact.

    A quote immediately following an odd number of backslashes is a TeX
    control symbol, not MakeIndex's quote operator, and is retained.
    """
    result = []
    backslashes = 0
    for char in text:
        if char == '"' and backslashes % 2:
            result.append(char)
        elif char in '!@|"':
            result.append('"' + char)
        else:
            result.append(char)
        backslashes = backslashes + 1 if char == "\\" else 0
    return "".join(result)


def bilingual(english: str, japanese: str) -> str:
    """English first, avoiding duplicate identical names or mathematical labels."""
    if english and japanese and english != japanese:
        return f"{english} ({japanese})"
    return english or japanese


def _owner(entry: dict, by_id: dict) -> dict:
    if entry.get("is_cross_reference_continuation"):
        owner_id = entry.get("cross_reference_owner_id") or entry.get("parent_id")
        if owner_id is None:
            raise ValueError(f"Cross-reference continuation has no owner: {entry.get('id')}")
        return by_id[owner_id]
    return entry


def _path(entry: dict, by_id: dict) -> list[dict]:
    entry = _owner(entry, by_id)
    return [by_id[i] for i in entry.get("ancestor_ids", [])] + [entry]


def _component(entry: dict) -> dict:
    return {
        "sort": entry["sort_key"],
        "english": entry.get("effective_english_tex") or entry.get("english_tex") or entry.get("japanese_tex", ""),
        "japanese": entry.get("japanese_tex", ""),
    }


def _components(entry: dict, by_id: dict) -> list[dict]:
    components = [_component(e) for e in _path(entry, by_id)]
    if len(components) > 3:
        # Preserve every label while respecting MakeIndex's three-level limit.
        tail = components[2:]
        components = components[:2] + [{
            "sort": " ".join(c["sort"] for c in tail),
            "english": ": ".join(c["english"] for c in tail),
            "japanese": ": ".join(c["japanese"] for c in tail),
        }]
    return components


def _render_key(components: list[dict]) -> str:
    result = []
    for component in components:
        sort_key = component["sort"]
        if not sort_key or not sort_key.isascii():
            raise ValueError(f"Expected a nonempty ASCII sort key: {sort_key!r}")
        display = bilingual(component["english"], component["japanese"])
        result.append(escape_makeindex(sort_key) + "@" + escape_makeindex(display))
    return "!".join(result)


def key_for(entry: dict, by_id: dict) -> str:
    """Return a complete hierarchical sort/display key without |encap."""
    return _render_key(_components(entry, by_id))


def _qualifier_sort(english: str) -> str:
    words = unicodedata.normalize("NFKD", english)
    words = "".join(c for c in words if not unicodedata.combining(c))
    if any(ord(c) > 127 and c.isalpha() for c in words):
        raise ValueError(f"Qualifier requires an explicit ASCII transcription: {english!r}")
    return re.sub(r"[^a-z0-9]+", " ", words.lower()).strip()


def qualified_key_for(entry: dict, by_id: dict, reference: dict) -> str:
    """Keep a reference's semantic qualifier in the terminal displayed label.

    The five qualified reference tokens belong to idx0612. Their two labels
    are CFT asymptotics and divergences from; no extra hierarchy is introduced.
    """
    english = reference.get("qualifier_english_tex", "")
    japanese = reference.get("qualifier_japanese_tex", "")
    if not english and not japanese:
        return key_for(entry, by_id)
    if not english:
        raise ValueError("A qualified reference needs an English sorting label")
    components = _components(entry, by_id)
    terminal = components[-1]
    terminal["sort"] += " " + _qualifier_sort(english)
    terminal["english"] += ": " + english
    terminal["japanese"] += ": " + (japanese or english)
    return _render_key(components)


def _target_display(target: dict, shared_qualifier: str = "") -> str:
    english = target.get("english_tex", "")
    japanese = target.get("japanese_tex", "")
    if len(target.get("english_path_tex", [])) > 1:
        # The parser retains the complete bilingual source fragment for these
        # hierarchical destinations. Remove its embedded English repetition.
        japanese = re.sub(r"（[^）]*）", "", japanese)
    if shared_qualifier and japanese and not japanese.endswith(shared_qualifier):
        japanese += " " + shared_qualifier
    return bilingual(english, japanese)


def cross_reference_records(entry: dict, by_id: dict) -> list[dict]:
    """Return {key, encap, page: 0} records preserving each reference meaning.

    The encapsulator becomes \\indexcrossref{TEXT}{0} in the .ind output.
    Its macro ignores the second argument, so no page 0 is printed.
    """
    suffixes = {
        "see": "を参照",
        "see_also": "も参照",
        "same_as": "と同じ",
        "see_under": "の項を参照",
        "see_complement": "の補集合を参照",
    }
    records = []
    for reference in entry.get("cross_references", []):
        kind = reference["type"]
        if kind not in suffixes:
            raise ValueError(f"Unknown cross-reference type: {kind}")
        targets = [
            _target_display(target, reference.get("shared_qualifier", ""))
            for target in reference["targets"]
        ]
        text = "、".join(targets) + " " + suffixes[kind]
        records.append({
            "key": key_for(entry, by_id),
            "encap": "indexcrossref{" + escape_makeindex(text) + "}",
            "page": 0,
        })
    return records
