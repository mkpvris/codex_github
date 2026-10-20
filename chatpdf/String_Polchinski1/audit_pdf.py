from pathlib import Path
from pypdf import PdfReader
from collections import Counter, defaultdict
import json
import re
import sys

root = Path(__file__).resolve().parent
pdf_path = root / "pdf" / "String_Polchinski1_jp.pdf"
reader = PdfReader(pdf_path)
destinations = reader.named_destinations
links = []
for page_no, page in enumerate(reader.pages, 1):
    for annotation in page.get("/Annots", []):
        annotation = annotation.get_object()
        if annotation.get("/Subtype") != "/Link":
            continue
        action = annotation.get("/A", {})
        target = action.get("/D", annotation.get("/Dest"))
        links.append({"page": page_no, "action": str(action.get("/S")),
                      "destination": str(target) if target is not None else None,
                      "uri": str(action.get("/URI")) if action.get("/URI") else None,
                      "file": str(action.get("/F")) if action.get("/F") else None})
missing_targets = [x for x in links if x["action"] == "/GoTo" and x["destination"] not in destinations]
aux = (root / "build" / "String_Polchinski1_jp.aux").read_text(encoding="utf-8")
by_destination = defaultdict(list)
for line in aux.splitlines():
    match = re.search(r"\\newlabel\{(eq:[^}]+)\}.*\{((?:equation|AMS)\.[^}]+)\}", line)
    if match:
        by_destination[match[2]].append(match[1])
duplicates = {k: v for k, v in by_destination.items() if len(v) > 1}
log = (root / "build" / "String_Polchinski1_jp.log").read_text(encoding="utf-8", errors="replace")
warnings = [line for line in log.splitlines() if re.search(
    r"Overfull|Missing character|undefined|duplicate destination|multiply defined", line)]
report = {
    "pdf": str(pdf_path), "pages": len(reader.pages),
    "link_action_counts": dict(Counter(x["action"] for x in links)),
    "citation_links": [x for x in links if (x["destination"] or "").startswith("cite.")],
    "external_uris": sorted({x["uri"] for x in links if x["uri"]}),
    "original_pdf_links": [x for x in links if x["action"] == "/GoToR"],
    "unresolved_internal_links": missing_targets,
    "equation_anchor_count": len(by_destination),
    "equation_anchor_aliases": duplicates,
    "significant_tex_warnings": warnings,
    "visual_review": "Separate PNG inspection required; this script does not establish visual correctness.",
}
(root / "qa" / "pdf_link_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
if missing_targets or any("duplicate destination" in x or "undefined" in x or "Missing character" in x for x in warnings):
    sys.exit(1)
