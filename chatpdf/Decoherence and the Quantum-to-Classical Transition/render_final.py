from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw
from pypdf import PdfReader
root=Path(__file__).resolve().parent;out=root/'audit/final_render';out.mkdir(exist_ok=True)
config=json.loads((root/'project_config.json').read_text(encoding='utf-8'))
pdf=root/'pdf'/config['pdf_filename']
old_manifest=out/'render_manifest.json'
if old_manifest.exists():
    old_data=json.loads(old_manifest.read_text(encoding='utf-8'))
    (out/('render_history_'+old_data['pdf_sha256']+'.json')).write_text(json.dumps(old_data,indent=2),encoding='utf-8')
else:
    old_data={}
previous={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('page-*.png')}
subprocess.run(['pdftoppm','-scale-to','1000','-png',str(pdf),str(out/'page')],check=True)
pages=sorted(out.glob('page-*.png'))
for start in range(0,len(pages),12):
    sheet=Image.new('RGB',(1600,2350),'#d0d0d0');draw=ImageDraw.Draw(sheet)
    for j,f in enumerate(pages[start:start+12]):
        im=Image.open(f).convert('RGB');im.thumbnail((390,550));x=(j%4)*400;y=(j//4)*780
        sheet.paste(im,(x+(400-im.width)//2,y+35));draw.text((x+10,y+8),f'PDF {start+j+1}',fill='black')
    sheet.save(out/f'sheet_{start//12+1:02}.jpg',quality=92)
current={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in pages}
changed=[name for name,value in current.items() if previous.get(name)!=value]
manifest={'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pdf_pages':len(PdfReader(pdf).pages),'rendered_pages':len(pages),'sheets':(len(pages)+11)//12,'unchanged_rendered_pages':len(current)-len(changed),'changed_page_images':changed}
manifest['previous_pdf_sha256']=old_data.get('pdf_sha256')
(out/'render_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Rendered',len(pages),'pages and',(len(pages)+11)//12,'sheets')
