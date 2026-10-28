"""Visual repairs to source equation crops; replacement is atomic."""
from pathlib import Path
import io
import json
import re
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
import pdfplumber

root = Path(__file__).resolve().parents[1]
source = PdfReader(root / 'source/original.pdf')
manifest_path = root / 'audit/ch05_equations.json'
entries = json.loads(manifest_path.read_text(encoding='utf-8'))
bykey = {e['key']: e for e in entries}
repairs = {
    '97': {'masks': [(54,373,104,386)]},
    '106': {'masks': [(48,178,110,194.3)]},
    '120': {'masks': [(54,553,101,566)]},
    '161': {'masks': [(49,360,115,374.5)], 'bottom': 400},
    '169': {'masks': [(49,303,104,316)]},
    '170': {'bottom': 548.2},
    '184': {'masks': [(49,462.8,103,475)]},
    '186': {'pdf_page': 246, 'bbox_top': [48,98,398,138], 'masks': [(54,89,82,101)]},
    '190': {'bbox_top': [48,182,398,250], 'masks': [(48,173.5,231,184.7)]},
    '203': {'top': 500, 'bottom': 541},
}
for key, repair in repairs.items():
    entry = bykey.get(key)
    if entry is None:
        entry = {'key': key, 'numbers': ['5.'+key], 'pdf_page': repair['pdf_page'], 'printed_page': repair['pdf_page']-14}
        entries.append(entry)
        bykey[key] = entry
    box = list(repair.get('bbox_top',entry.get('bbox_top',[])))
    if 'top' in repair: box[1] = repair['top']
    if 'bottom' in repair: box[3] = repair['bottom']
    writer = PdfWriter()
    page = writer.add_page(source.pages[entry['pdf_page']-1])
    height = float(page.mediabox.height)
    if repair.get('masks') or key != '186':
        stream = io.BytesIO()
        canvas = Canvas(stream, pagesize=(float(page.mediabox.width), height))
        canvas.setFillColorRGB(1,1,1)
        if key != '186':
            canvas.rect(box[0],height-box[1]-3,box[2]-box[0],3,fill=1,stroke=0)
        for x0, top, x1, bottom in repair.get('masks',[]):
            canvas.rect(x0,height-bottom,x1-x0,bottom-top,fill=1,stroke=0)
        canvas.save()
        stream.seek(0)
        page.merge_page(PdfReader(stream).pages[0])
    x0,top,x1,bottom = box
    rect = RectangleObject([x0,height-bottom,x1,height-top])
    page.cropbox = rect
    page.mediabox = RectangleObject(rect)
    destination = root / 'figures' / f'ch05_eq_{key}.pdf'
    temporary = destination.with_suffix('.pending.pdf')
    writer.write(temporary)
    temporary.replace(destination)
    entry['bbox_top'] = box
    entry['visual_repair'] = repair

# Retained, visually verified equation 5.133 from a previous crop run.
if '133' not in bykey:
    crop = PdfReader(root/'figures/ch05_eq_133.pdf').pages[0]
    height = float(source.pages[231].mediabox.height)
    b = crop.cropbox
    entry = {'key':'133','numbers':['5.133'],'pdf_page':232,'printed_page':218,
             'bbox_top':[float(b.left),height-float(b.top),float(b.right),height-float(b.bottom)],
             'visual_repair':'Retained complete crop, verified against source.'}
    entries.append(entry)

entries.sort(key=lambda e: int(re.match(r'\d+', e['key']).group()))
manifest_path.write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
print('Repaired:', ', '.join(repairs))
