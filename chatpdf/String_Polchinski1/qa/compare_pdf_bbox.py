"""Read two PDFs with Poppler and compare per-page text and word coordinates.

Only files under --output-dir are written. Input PDFs are never modified.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stat_signature(path: Path) -> tuple[int, int]:
    st = path.stat()
    return st.st_size, st.st_mtime_ns


def extract(executable: str, pdf: Path, target: Path) -> dict:
    before = stat_signature(pdf)
    command = [executable, "-bbox", "-enc", "UTF-8", str(pdf), str(target)]
    process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if process.returncode:
        raise RuntimeError(f"Poppler failed for {pdf.name}: {process.stderr}")
    if stat_signature(pdf) != before:
        raise RuntimeError(f"Input PDF changed during extraction: {pdf}")
    result = []
    document = ET.parse(target)
    for element in document.iter():
        if element.tag.rsplit("}", 1)[-1] != "page":
            continue
        words = []
        for word in element.iter():
            if word.tag.rsplit("}", 1)[-1] == "word":
                words.append({
                    "text": "".join(word.itertext()),
                    "bbox": [float(word.attrib[k]) for k in ("xMin", "yMin", "xMax", "yMax")],
                })
        result.append({"size": [float(element.attrib[k]) for k in ("width", "height")], "words": words})
    return {
        "pdf": str(pdf), "bytes": before[0], "mtime_ns": before[1],
        "sha256": sha256(pdf), "pages": result, "poppler_stderr": process.stderr.strip(),
    }


def different(a: list[float], b: list[float], tolerance: float) -> bool:
    return any(abs(x - y) > tolerance for x, y in zip(a, b))


def compare_page(old: dict | None, new: dict | None, page: int, tolerance: float) -> dict:
    if old is None or new is None:
        return {"page": page, "changed": True, "reason": "page_added" if old is None else "page_removed"}
    old_words, new_words = old["words"], new["words"]
    old_text, new_text = [w["text"] for w in old_words], [w["text"] for w in new_words]
    size_changed = different(old["size"], new["size"], tolerance)
    text_changed = old_text != new_text
    coordinate_changes = []
    operations = []
    matcher = SequenceMatcher(a=old_text, b=new_text, autojunk=False)
    for operation, i, j, k, l in matcher.get_opcodes():
        if operation == "equal":
            for oi, ni in zip(range(i, j), range(k, l)):
                if different(old_words[oi]["bbox"], new_words[ni]["bbox"], tolerance):
                    coordinate_changes.append({
                        "text": old_words[oi]["text"], "old_word_index": oi, "new_word_index": ni,
                        "old_bbox": old_words[oi]["bbox"], "new_bbox": new_words[ni]["bbox"],
                    })
        else:
            operations.append({
                "operation": operation, "old_word_range": [i, j], "new_word_range": [k, l],
                "old_text": " ".join(old_text[i:j]), "new_text": " ".join(new_text[k:l]),
            })
    changed = size_changed or text_changed or bool(coordinate_changes)
    result = {
        "page": page, "changed": changed, "page_size_changed": size_changed,
        "word_sequence_changed": text_changed,
        "word_multiset_changed": Counter(old_text) != Counter(new_text),
        "old_word_count": len(old_words), "new_word_count": len(new_words),
        "matching_words_with_changed_bbox": len(coordinate_changes),
    }
    if changed:
        result.update({"text_edit_operations": operations, "coordinate_changes": coordinate_changes})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old_pdf", type=Path)
    parser.add_argument("new_pdf", type=Path)
    parser.add_argument("--pdftotext", default=r"C:\texlive\2026\bin\windows\pdftotext.exe")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--coordinate-tolerance", type=float, default=0.00001, help="PDF points")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    old_pdf, new_pdf = args.old_pdf.resolve(), args.new_pdf.resolve()
    old = extract(args.pdftotext, old_pdf, args.output_dir / "old_bbox.html")
    new = extract(args.pdftotext, new_pdf, args.output_dir / "new_bbox.html")
    old_pages, new_pages = old.pop("pages"), new.pop("pages")
    pages = [compare_page(
        old_pages[n] if n < len(old_pages) else None,
        new_pages[n] if n < len(new_pages) else None, n + 1, args.coordinate_tolerance,
    ) for n in range(max(len(old_pages), len(new_pages)))]
    changed = [p["page"] for p in pages if p["changed"]]
    result = {
        "audit_time_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Poppler pdftotext -bbox; page word sequence, matching-word bounding boxes, and page size",
        "coordinate_tolerance_pt": args.coordinate_tolerance,
        "old": old, "new": new, "old_page_count": len(old_pages), "new_page_count": len(new_pages),
        "changed_pages": changed, "unchanged_page_count": len(pages) - len(changed), "pages": pages,
        "limitations": "Text bounding-box comparison does not examine PDF links, annotations, or non-text graphics. Changed pages require visual review.",
    }
    target = args.output_dir / "pdf_bbox_comparison.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "old_page_count": len(old_pages), "new_page_count": len(new_pages),
        "changed_pages": changed, "unchanged_page_count": result["unchanged_page_count"],
        "result": str(target),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
