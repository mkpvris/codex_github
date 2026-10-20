from pathlib import Path
import json
import re
from pypdf import PdfReader

root = Path(__file__).resolve().parent
reader = PdfReader(root / "source" / "String_Polchinski1_original.pdf")
pages = []
for i, page in enumerate(reader.pages, 1):
    text = page.extract_text(extraction_mode="layout") or ""
    (root / "source" / f"page_{i:03d}.txt").write_text(text, encoding="utf-8")
    pages.append({
        "pdf_page": i,
        "characters": len(text),
        "width": float(page.mediabox.width),
        "height": float(page.mediabox.height),
        "head": text[:500],
    })
(root / "source" / "page_inventory.json").write_text(
    json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(pages[10:32], ensure_ascii=False, indent=2))
