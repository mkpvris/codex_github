"""Render the revised TOC, exercises, glossary and index for visual QA."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
POPPLER = Path(r"C:\Users\false\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")
PAGES = [2, 45, 326, 332, 333, 354, 367, 377]


def render(page):
    output = ROOT / f"qa/final-revision-{page:03d}"
    subprocess.run([str(POPPLER), "-f", str(page), "-l", str(page), "-scale-to", "1500", "-png", "-singlefile",
                    "pdf/String_Polchinski1_jp.pdf", str(output.relative_to(ROOT))], cwd=ROOT, check=True)
    return output.with_suffix(".png")


with ThreadPoolExecutor(max_workers=3) as pool:
    outputs = list(pool.map(render, PAGES))
comparisons = {}
for page, old in [(2, "revised-toc-preview.png"), (326, "revised-glossary-preview.png"), (354, "revised-index-preview.png")]:
    comparisons[str(page)] = ((ROOT / f"qa/final-revision-{page:03d}.png").read_bytes() == (ROOT / "qa" / old).read_bytes())
report = {"rendered_pages": PAGES, "layout_unchanged_after_bookmark_fix": comparisons,
          "pdf_sha256": hashlib.sha256((ROOT / "pdf/String_Polchinski1_jp.pdf").read_bytes()).hexdigest(),
          "outputs": [str(p.relative_to(ROOT)) for p in outputs]}
(ROOT / "qa/final_revision_render_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
