"""Render the subsection-only contents and retained linked body headings."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'pdf/String_Polchinski1_jp.pdf'
POPPLER = Path(r'C:\Users\false\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe')
toc = (ROOT / 'build/String_Polchinski1_jp.toc').read_text(encoding='utf-8')
reader = PdfReader(PDF)
first_body = re.search(r'\\contentsline \{section\}\{本書について\}\{(\d+)\}', toc)
subsub = re.search(r'\\contentsline \{subsubsection\}\{.*\}\{(\d+)\}\{[^}]+\}', toc)
index = re.search(r'\\contentsline \{section\}\{索引\}\{(\d+)\}', toc)
assert first_body and subsub and index
pages = sorted({2, int(first_body[1])-1, int(subsub[1]), int(index[1])})

def render(page):
    output = ROOT / f'qa/subsection-toc-revision-{page:03d}'
    subprocess.run([str(POPPLER), '-f', str(page), '-l', str(page), '-scale-to', '1500', '-png', '-singlefile',
                    str(PDF.relative_to(ROOT)), str(output.relative_to(ROOT))], cwd=ROOT, check=True)
    return str(output.with_suffix('.png').relative_to(ROOT))

with ThreadPoolExecutor(max_workers=3) as pool:
    outputs = list(pool.map(render, pages))
report = {'pdf_pages': len(reader.pages), 'toc_last_page': int(first_body[1])-1,
          'linked_body_heading_page': int(subsub[1]), 'index_first_page': int(index[1]),
          'rendered_pages': pages, 'outputs': outputs,
          'pdf_sha256': hashlib.sha256(PDF.read_bytes()).hexdigest()}
(ROOT / 'qa/subsection_toc_revision_render_audit.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
