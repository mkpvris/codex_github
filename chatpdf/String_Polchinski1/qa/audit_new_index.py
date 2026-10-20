"""Verify every displayed index page link against its physical PDF destination."""
from pathlib import Path
from pypdf import PdfReader
import json
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "pdf/String_Polchinski1_jp.pdf"
reader = PdfReader(PDF)
dests = reader.named_destinations
toc = (ROOT / "build/String_Polchinski1_jp.toc").read_text(encoding="utf-8")
index_match = re.search(r"\\contentsline \{section\}\{索引\}\{(\d+)\}", toc)
if not index_match:
    raise RuntimeError("Index is absent from table of contents")
start = int(index_match[1])
xml_path = ROOT / "qa/index_words.html"
poppler = Path(r"C:\texlive\2026\bin\windows\pdftotext.exe")
subprocess.run([str(poppler), "-f", str(start), "-bbox", str(PDF.relative_to(ROOT)), str(xml_path.relative_to(ROOT))], cwd=ROOT, check=True)
tree = ET.parse(xml_path)
xml_pages = list(tree.iter("{http://www.w3.org/1999/xhtml}page"))
links = []
errors = []
for no, page in enumerate(reader.pages, 1):
    if no < start:
        continue
    word_nodes = list(xml_pages[no-start].iter("{http://www.w3.org/1999/xhtml}word"))
    height = float(page.mediabox.height)
    for a in page.get("/Annots", []):
        a = a.get_object()
        action = a.get("/A", {})
        target = str(action.get("/D", a.get("/Dest", "")))
        if not re.fullmatch(r"page\.\d+", target):
            continue
        expected = int(target.split(".")[1])
        actual = reader.get_destination_page_number(dests[target]) + 1
        x0, y0, x1, y1 = map(float, a["/Rect"])
        top, bottom = height - y1, height - y0
        overlapping = []
        for w in word_nodes:
            wx0, wx1 = float(w.attrib["xMin"]), float(w.attrib["xMax"])
            wy0, wy1 = float(w.attrib["yMin"]), float(w.attrib["yMax"])
            if wx1 > x0 and wx0 < x1 and wy1 > top and wy0 < bottom:
                # Approximate per-character centers when a range is one word.
                text = w.text or ""
                for m in re.finditer(r"\d+", text):
                    center = wx0 + (m.start() + m.end()) / 2 / max(1, len(text)) * (wx1-wx0)
                    if x0 - 1 <= center <= x1 + 1:
                        overlapping.append(int(m[0]))
        item = {"index_page": no, "destination": target, "actual_pdf_page": actual,
                "displayed_numbers": overlapping}
        links.append(item)
        if actual != expected or expected not in overlapping:
            errors.append(item)
page_anchor_errors = []
for no in range(1, len(reader.pages)+1):
    target = "page." + str(no)
    if target not in dests or reader.get_destination_page_number(dests[target])+1 != no:
        page_anchor_errors.append(no)
report = {"pdf_pages": len(reader.pages), "index_first_page": start,
          "index_page_links_checked": len(links), "page_anchor_errors": page_anchor_errors,
          "displayed_number_or_destination_errors": errors, "links": links}
(ROOT / "qa/index_pdf_link_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k != "links"}, ensure_ascii=False))
if errors or page_anchor_errors or not links:
    raise SystemExit(1)
