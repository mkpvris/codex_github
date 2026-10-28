"""Remove visually identified residual prose at crop boundaries."""
from pathlib import Path
import json, io, re
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas

root = Path(__file__).resolve().parents[1]
manifest = root/'audit/ch05_equations.json'
entries = json.loads(manifest.read_text(encoding='utf-8'))
bykey = {e['key']:e for e in entries}
source = PdfReader(root/'source/original.pdf')
top = {'4':(157,419),'8':(100,156),'13':(129,184),'32':(32,66),
       '50':(46,53),'52':(339,343),'58':(339,345),'65':(76,164),
       '79':(358,472),'130':(181,199),'131':(205,221),'132':(366,372),
       '135':(155,161),'138':(209,213),'141':(175,181),'160':(23,113),
       '162':(181,224),'171':(16,86),'179':(316,319),'180':(114,118),
       '107':(256,331),'147':(266,272),'166a_166b_166c':(57,60),
       '178':(278,281),'194':(459,463),'67':[(25,31),(312,316)]}
bottom = {'57':(329,336),'84':(64,245),'138':(60,66),'144':(138,169),
          '175':(293,327),'178':(224,234),'24':(220,228),
          '81':(161,228),'158':(286,294)}
for key in sorted(set(top)|set(bottom),key=lambda k:int(re.match(r'\d+',k).group())):
    entry=bykey[key]
    x0, y0, x1, y1 = entry['bbox_top']
    sourcepage=source.pages[entry['pdf_page']-1]
    height=float(sourcepage.mediabox.height)
    reader=PdfReader(root/'figures'/f'ch05_eq_{key}.pdf')
    writer=PdfWriter()
    page=writer.add_page(reader.pages[0])
    overlay=io.BytesIO()
    canvas=Canvas(overlay,pagesize=(float(sourcepage.mediabox.width),height))
    canvas.setFillColorRGB(1,1,1)
    changes=[]
    for edge, ranges in [('top',top),('bottom',bottom)]:
        if key not in ranges: continue
        spans = ranges[key] if isinstance(ranges[key][0],(list,tuple)) else [ranges[key]]
        for a,b in spans:
            left=x0+a*350/600-1
            right=x0+b*350/600+1
            low,high=(y0-1,y0+3.5)if edge=='top'else(y1-3.5,y1+2)
            canvas.rect(left,height-high,right-left,high-low,fill=1,stroke=0)
            changes.append({'edge':edge,'source_bbox_top':[left,low,right,high]})
    canvas.save();overlay.seek(0)
    page.merge_page(PdfReader(overlay).pages[0])
    destination=root/'figures'/f'ch05_eq_{key}.pdf'
    temporary=destination.with_suffix('.pending.pdf')
    writer.write(temporary);temporary.replace(destination)
    entry['edge_cleanup']=changes
manifest.write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
print('Cleaned edge fragments in',len(set(top)|set(bottom)),'equation crops.')
