"""Compare both final PDFs against their pre-title-change snapshots.

Run only after the final-build notification. Document inputs remain unchanged;
all extraction and comparison outputs stay under qa/.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
import hashlib
import json
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/toc_titles_pdf_comparison"
PDFTOTEXT = Path(r"C:\texlive\2026\bin\windows\pdftotext.exe")
CONFIG = [
    {"edition": "normal", "old": "pdf/history/before_toc_titles_normal.pdf",
     "new": "pdf/String_Polchinski1_jp.pdf", "expected_pages": 372, "toc_pages": [1, 2, 3, 4]},
    {"edition": "extended", "old": "pdf/history/before_toc_titles_extended.pdf",
     "new": "pdf/String_Polchinski1_jp_index_extended.pdf", "expected_pages": 374,
     "toc_pages": [1, 2, 3, 4, 5, 6]},
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(text):
    return re.sub(r"\s+", "", text)


def canonical_old(text, page, toc_pages):
    result = compact(text).replace("無ゴースト定理", "ノーゴースト定理")
    if page in toc_pages:
        # Some groups were already 演習問題; only chapter/appendix-prefixed
        # old titles are changed. The optional suffix prevents 問題 duplication.
        result = re.sub(r"(?:第[1-9]章の演習|付録Aの演習)(?:問題)?", "演習問題", result)
    return result


def extract(job):
    edition, version, relative_path = job
    pdf = ROOT / relative_path
    digest_before = sha(pdf)
    target = OUT / f"{edition}_{version}.txt"
    completed = subprocess.run(
        [str(PDFTOTEXT), "-layout", "-enc", "UTF-8", str(pdf), str(target)],
        check=True, capture_output=True, text=True,
    )
    if sha(pdf) != digest_before:
        raise RuntimeError(f"Input PDF changed during extraction: {relative_path}")
    pages = target.read_text(encoding="utf-8").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return {
        "edition": edition, "version": version, "path": relative_path,
        "sha256": digest_before, "bytes": pdf.stat().st_size,
        "page_count": len(pages), "extraction": target.relative_to(ROOT).as_posix(),
        "poppler_stderr": completed.stderr, "pages": pages,
    }


def diff_windows(old, new):
    windows = []
    for tag, a, b, c, d in SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        windows.append({
            "operation": tag, "old_position": [a, b], "new_position": [c, d],
            "old": old[a:b], "new": new[c:d],
            "old_context": old[max(0, a - 50):min(len(old), b + 50)],
            "new_context": new[max(0, c - 50):min(len(new), d + 50)],
        })
    return windows


def main():
    OUT.mkdir(exist_ok=True)
    jobs = [(config["edition"], version, config[version])
            for config in CONFIG for version in ("old", "new")]
    with ThreadPoolExecutor(max_workers=4) as pool:
        extracted = {(x["edition"], x["version"]): x for x in pool.map(extract, jobs)}
    reports = []
    for config in CONFIG:
        old = extracted[(config["edition"], "old")]
        new = extracted[(config["edition"], "new")]
        old_pages = old.pop("pages")
        new_pages = new.pop("pages")
        old_compact = [compact(x) for x in old_pages]
        new_compact = [compact(x) for x in new_pages]
        allowed_old = [canonical_old(x, i, config["toc_pages"]) for i, x in enumerate(old_pages, 1)]
        raw_changed, allowed_only, unexpected = [], [], []
        page_details = []
        for i in range(max(len(old_pages), len(new_pages))):
            a = old_compact[i] if i < len(old_compact) else ""
            b = new_compact[i] if i < len(new_compact) else ""
            transformed = allowed_old[i] if i < len(allowed_old) else ""
            detail = {"page": i + 1, "old_characters_without_whitespace": len(a),
                      "new_characters_without_whitespace": len(b),
                      "equal_after_whitespace_removal": a == b,
                      "equal_after_allowed_changes": transformed == b}
            if a != b:
                raw_changed.append(i + 1)
                if transformed == b:
                    allowed_only.append(i + 1)
                    detail["allowed_changes"] = diff_windows(a, b)
                else:
                    unexpected.append(i + 1)
                    detail["unexpected_changes_after_allowances"] = diff_windows(transformed, b)
            elif transformed != b:
                unexpected.append(i + 1)
                detail["unexpected_changes_after_allowances"] = diff_windows(transformed, b)
            page_details.append(detail)
        joined_equal = "".join(allowed_old) == "".join(new_compact)
        counts_ok = old["page_count"] == new["page_count"] == config["expected_pages"]
        stale_terms = [i + 1 for i, page in enumerate(new_compact) if "無ゴースト定理" in page]
        old_toc_titles = [i for i in config["toc_pages"]
                          if i <= len(new_compact) and re.search(r"第[1-9]章の演習|付録Aの演習", new_compact[i - 1])]
        toc_group_counts = {str(i): new_compact[i - 1].count("演習問題") for i in config["toc_pages"] if i <= len(new_compact)}
        passed = counts_ok and not unexpected and not stale_terms and not old_toc_titles and sum(toc_group_counts.values()) == 10
        reports.append({
            "edition": config["edition"], "status": "passed" if passed else "failed",
            "old": old, "new": new, "expected_pages": config["expected_pages"], "page_counts_unchanged": counts_ok,
            "toc_allowance_pages": config["toc_pages"], "changed_pages_without_whitespace": raw_changed,
            "pages_with_only_allowed_changes": allowed_only, "unexpected_changed_pages": unexpected,
            "complete_document_text_equal_after_allowed_changes": joined_equal,
            "pagination_shift_detected": joined_equal and bool(unexpected),
            "new_pages_containing_old_no_ghost_term": stale_terms,
            "new_toc_pages_containing_old_exercise_titles": old_toc_titles,
            "toc_exercise_group_counts_per_page": toc_group_counts,
            "toc_exercise_group_count": sum(toc_group_counts.values()),
            "page_details": page_details,
        })
    # A second hash check protects the entire audit interval, not just extraction.
    for result in extracted.values():
        if sha(ROOT / result["path"]) != result["sha256"]:
            raise RuntimeError(f"Input PDF changed during comparison: {result['path']}")
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if all(x["status"] == "passed" for x in reports) else "failed",
        "method": "Poppler -layout UTF-8 text for every page. Remove all whitespace, then compare each physical page independently. Only old 無ゴースト定理→ノーゴースト定理 globally and old 第[1-9]章の演習/付録Aの演習→演習問題 on the specified TOC pages are allowed.",
        "editions": reports, "document_files_modified": False,
        "limitations": "Text and page-flow comparison; not a pixel comparison. A page break or textual change beyond the explicit allowances is reported, even if it is only a reflow between adjacent pages.",
    }
    (ROOT / "qa/toc_titles_pdf_comparison.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "editions": [
        {key: item[key] for key in ("edition", "status", "page_counts_unchanged", "changed_pages_without_whitespace", "unexpected_changed_pages", "pagination_shift_detected", "toc_exercise_group_count")}
        for item in reports]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
