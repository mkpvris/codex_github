from pathlib import Path
import json
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
root=Path(__file__).resolve().parents[1]
manifest=root/'audit/ch05_equations.json'
entries=json.loads(manifest.read_text(encoding='utf-8'))
source=PdfReader(root/'source/original.pdf')
keys={'60','110','146','156','197'}
for entry in entries:
    if entry['key'] not in keys: continue
    path=root/'figures'/('ch05_eq_'+entry['key']+'.pdf')
    reader=PdfReader(path);writer=PdfWriter();page=writer.add_page(reader.pages[0])
    height=float(source.pages[entry['pdf_page']-1].mediabox.height)
    box=list(entry['bbox_top']);box[3]=600
    rect=RectangleObject([box[0],height-box[3],box[2],height-box[1]])
    page.cropbox=rect;page.mediabox=RectangleObject(rect)
    temporary=path.with_suffix('.pending.pdf');writer.write(temporary);temporary.replace(path)
    entry['bbox_top']=box
    entry['bottom_extension']='Extended to600pt source blank margin after visual comparison; complete delimiters and denominators retained.'
manifest.write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
print('Extended math bottoms:', ', '.join(sorted(keys,key=int)))
