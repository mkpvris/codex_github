import json,math
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image,ImageDraw,ImageFont
from pypdf import PdfReader
r=Path(__file__).parent
src=r/'source/2607.14351v1-ja.pdf'
out=r/'qa-render';out.mkdir(exist_ok=True)
doc=pdfium.PdfDocument(src)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
thumbs=[]; stats=[]
for i in range(len(doc)):
    p=doc[i]
    im=p.render(scale=1.65).to_pil().convert('RGB')
    im.save(out/f'page-{i+1:03}.png')
    txt=p.get_textpage().get_text_range()
    stats.append({'page':i+1,'characters':len(txt),'replacement':txt.count('\ufffd'),'question_marks':txt.count('??'),'size':p.get_size()})
    im.thumbnail((360,510))
    cell=Image.new('RGB',(380,550),'#e8eaed');cell.paste(im,((380-im.width)//2,30))
    ImageDraw.Draw(cell).text((10,7),f'Page {i+1}',font=font,fill='#333333')
    thumbs.append(cell)
    p.close()
for k in range(math.ceil(len(thumbs)/12)):
    sheet=Image.new('RGB',(1520,1650),'#c7cbd1')
    for j,im in enumerate(thumbs[k*12:k*12+12]):sheet.paste(im,((j%4)*380,(j//4)*550))
    sheet.save(out/f'sheet-{k+1:02}.jpg',quality=92)
(r/'qa-pages.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print('Rendered',len(doc),'pages;',math.ceil(len(thumbs)/12),'contact sheets')
print('Potential text issues:',[s for s in stats if s['replacement'] or s['question_marks'] or s['characters']<30])
reader=PdfReader(src)
print('metadata:',reader.metadata)
print('outlines:',len(reader.outline))
