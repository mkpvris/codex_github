from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import RectangleObject
import pdfplumber,re,json,copy
root=Path(__file__).resolve().parent
r=PdfReader(root/'source/original.pdf'); report=[]
with pdfplumber.open(root/'source/original.pdf') as pdf:
    for index in range(255,340):
        p=pdf.pages[index]
        caps=[]
        for m in p.search(r'Fig\.\s*([67])\.\s*(\d+)\.'):
            if any('BX' in c['fontname'] or 'Bold' in c['fontname'] for c in m['chars']):
                caps.append((int(m['groups'][0]),int(m['groups'][1]),m['top']))
        for ch,n,capy in caps:
            previous=max([c[2]+45 for c in caps if c[2]<capy]+[45])
            objects=[o for o in p.images+p.curves+p.rects+p.lines if o['bottom']<=capy-2 and o['top']>=previous and o['x1']>=50 and o['x0']<=400]
            objects=[o for o in objects if (o['x1']-o['x0']>1 or o['bottom']-o['top']>1)]
            if not objects:
                report.append({'chapter':ch,'figure':n,'physical_page':index+1,'error':'no graphics'});continue
            top=max(previous,min(o['top'] for o in objects)-12)
            overrides={3:42,4:43,5:363,10:43,11:348,12:42,14:42,16:375,17:341,19:44,20:43,23:278,24:405,27:360,28:390}
            if ch==6 and n in overrides:top=overrides[n]
            # Include labels immediately above the graphical object, without body paragraphs.
            low=min(o['bottom'] for o in objects)
            x0=45;x1=float(p.width)-42;bottom=capy-3
            page=copy.copy(r.pages[index]);h=float(p.height)
            rect=RectangleObject((x0,h-bottom,x1,h-top));page.mediabox=rect;page.cropbox=rect
            writer=PdfWriter();writer.add_page(page)
            name=f'ch{ch:02}_fig{n:02}.pdf'
            with open(root/'figures'/name,'wb') as f:writer.write(f)
            report.append({'chapter':ch,'figure':n,'physical_page':index+1,'bbox_top':[x0,top,x1,bottom],'file':name})
(root/'audit/ch06_ch07_crop_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
