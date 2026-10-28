"""Final source-coordinate masks, with every crop box preserved exactly."""
from pathlib import Path
import io, json, sys
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader, PdfWriter

root=Path(__file__).resolve().parents[1]
manifest=root/'audit/ch05_equations.json'
entries=json.loads(manifest.read_text(encoding='utf-8'))
bykey={e['key']:e for e in entries}
source=PdfReader(root/'source/original.pdf')
masks={
    '32':[(164,464.5,201,473)],
    '52':[(195,381,215,390)],
    '67':[(260,543,270,554)],
    '71':[(48,470,398,486)],
    '114':[(48,135,140,145)],
    '131':[(48,440,398,455.5)],
    '132':[(48,526,398,541.5)],
    '147':[(48,136,398,149.5)],
    '161':[(48,349,398,363.4)],
    '169':[(48,291,398,306.2)],
    '198':[(139,226,159,233)],
}
for key,rectangles in masks.items():
    if len(sys.argv)>1 and key not in sys.argv[1:]:
        continue
    entry=bykey[key]
    sourcepage=source.pages[entry['pdf_page']-1]
    height=float(sourcepage.mediabox.height)
    target=root/'figures'/f'ch05_eq_{key}.pdf'
    old=PdfReader(target)
    writer=PdfWriter();page=writer.add_page(old.pages[0])
    original_box=list(page.mediabox)
    stream=io.BytesIO()
    canvas=Canvas(stream,pagesize=(float(sourcepage.mediabox.width),height))
    canvas.setFillColorRGB(1,1,1)
    for x0,top,x1,bottom in rectangles:
        canvas.rect(x0,height-bottom,x1-x0,bottom-top,fill=1,stroke=0)
    canvas.save();stream.seek(0)
    page.merge_page(PdfReader(stream).pages[0])
    assert list(page.mediabox)==original_box
    temporary=target.with_suffix('.pending.pdf')
    writer.write(temporary);temporary.replace(target)
    entry['final_cosmetic_masks_source_top']=rectangles
manifest.write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
print('Final cosmetic mask keys:',', '.join(masks))
