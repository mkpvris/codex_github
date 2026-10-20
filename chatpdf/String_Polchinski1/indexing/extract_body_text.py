"""Extract visible typeset prose, excluding imported figure XObjects.

Some cropped source figures retain clipped-away source-page text. Removing Do
operations in an analysis-only copy prevents those invisible words from being
mistaken for translated prose. The deliverable PDF is never modified.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream

POPPLER = Path(r"C:\texlive\2026\bin\windows\pdftotext.exe")


def extract_body_text(pdf_path, output_txt, analysis_pdf=None):
    pdf_path, output_txt = Path(pdf_path), Path(output_txt)
    analysis_pdf = Path(analysis_pdf or pdf_path.with_name("index_text_body.pdf"))
    canonical_text = analysis_pdf.with_suffix(".txt")
    metadata = analysis_pdf.with_suffix(".json")
    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    previous = json.loads(metadata.read_text(encoding="utf-8")) if metadata.exists() else {}
    if previous.get("source_sha256") != digest or not canonical_text.exists():
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        writer.clone_document_from_reader(reader)
        removed = 0
        for page in writer.pages:
            if page.get_contents() is None:
                continue
            content = ContentStream(page.get_contents(), writer)
            operations = content.operations
            content.operations = [(operands, op) for operands, op in operations if op != b"Do"]
            removed += len(operations) - len(content.operations)
            page.replace_contents(content)
        with analysis_pdf.open("wb") as stream:
            writer.write(stream)
        result = subprocess.run([str(POPPLER), "-layout", "-enc", "UTF-8", str(analysis_pdf), str(canonical_text)],
                                capture_output=True, text=True, check=True)
        metadata.write_text(json.dumps({"source_sha256": digest, "removed_xobject_draw_operations": removed,
                                        "source_pdf_unchanged": True, "method": "analysis copy with imported image/form drawing operations removed"}, indent=2), encoding="utf-8")
    else:
        result = subprocess.CompletedProcess(args=[str(POPPLER), "cached analysis text"], returncode=0, stdout="", stderr="")
    output_txt.parent.mkdir(parents=True, exist_ok=True)
    if output_txt.resolve() != canonical_text.resolve():
        shutil.copyfile(canonical_text, output_txt)
    return result
