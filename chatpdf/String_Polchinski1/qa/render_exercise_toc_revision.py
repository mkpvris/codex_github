"""Render the current TOC and affected sections after removing exercise entries."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "pdf/String_Polchinski1_jp.pdf"
POPPLER = Path(r"C:\Users\false\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")
toc = (ROOT / "build/String_Polchinski1_jp.toc").read_text(encoding="utf-8")
sections = {}
for title in ["第1章の演習", "付録Aの演習", "参考文献", "用語集", "索引"]:
    match = re.search(r"\\contentsline \{[^}]+\}\{" + re.escape(title) + r"\}\{(\d+)\}", toc)
    assert match, title
    sections[title] = int(match[1])
pages = sorted({2, sections["第1章の演習"], sections["付録Aの演習"], sections["用語集"], sections["索引"]})

def render(page):
    output = ROOT / f"qa/exercise-toc-revision-{page:03d}"
    subprocess.run([str(POPPLER), "-f", str(page), "-l", str(page), "-scale-to", "1500", "-png", "-singlefile",
                    str(PDF.relative_to(ROOT)), str(output.relative_to(ROOT))], cwd=ROOT, check=True)
    return str(output.with_suffix(".png").relative_to(ROOT))

with ThreadPoolExecutor(max_workers=3) as pool:
    outputs = list(pool.map(render, pages))
report = {"pdf_pages": len(PdfReader(PDF).pages), "sections": sections,
          "rendered_pages": pages, "outputs": outputs,
          "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest()}
(ROOT / "qa/exercise_toc_revision_render_audit.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
