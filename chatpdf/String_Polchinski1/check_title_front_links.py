from pathlib import Path
from pypdf import PdfReader
import json

root = Path(__file__).resolve().parent
reader = PdfReader(root / "pdf/String_Polchinski1_jp.pdf")
publisher = "https://www.cambridge.org/core/books/string-theory/30409AF2BDE27D53E275FDA395AB667A"
headings = ["本書について", "ハードカバー版の書評より",
            "Cambridge Monographs on Mathematical Physics", "刊行情報",
            "第II巻の構成", "序文", "まえがき", "記法"]
found = {}
for item in reader.outline:
    if isinstance(item, list):
        continue
    title = str(item.title).replace(" ", "")
    for heading in headings:
        if title == heading.replace(" ", ""):
            page_number = reader.get_destination_page_number(item) + 1
            page = reader.pages[page_number - 1]
            back_links = []
            for annot in page.get("/Annots", []):
                annot = annot.get_object()
                action = annot.get("/A", {})
                if str(action.get("/D")) == "toc":
                    back_links.append([float(x) for x in annot["/Rect"]])
            found[heading] = {"page": page_number, "back_link_rectangles": back_links}
first_page = reader.pages[0]
title_links = [str(x.get_object().get("/A", {}).get("/URI")) for x in first_page.get("/Annots", [])]
report = {
    "title_publisher_uri_present": publisher in title_links,
    "front_matter_backlinks": found,
    "all_eight_headings_have_backlinks": len(found) == 8 and all(x["back_link_rectangles"] for x in found.values()),
    "removed_text_absent": {
        term: not any(term in page.extract_text() for page in reader.pages[:16])
        for term in ["原書表紙の表記", "添付された原文PDF", "逐次翻訳版", "本書はarXiv論文ではない"]
    },
}
(root / "qa/title_front_link_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
assert report["title_publisher_uri_present"]
assert report["all_eight_headings_have_backlinks"]
assert all(report["removed_text_absent"].values())
