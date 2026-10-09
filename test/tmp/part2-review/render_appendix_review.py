from pathlib import Path
import subprocess,json
from PIL import Image,ImageOps,ImageDraw
from pypdf import PdfReader

folder=Path(r'C:\codex\test\tmp\part2-review')
out=folder/'appendix-final'
out.mkdir(exist_ok=True)
pdf=Path(r'C:\codex\EFTofOpenSystems\part2\pdf\template.pdf')
subprocess.run(['pdftoppm','-r','85','-png',str(pdf),str(out/'page')],check=True)
pages=len(PdfReader(pdf).pages)
for group in range((pages+5)//6):
    sheet=Image.new('RGB',(1100,2450),'#ddd')
    for offset in range(6):
        n=group*6+offset+1
        if n>pages: break
        im=Image.open(out/f'page-{n:02d}.png').convert('RGB')
        im.thumbnail((540,775))
        x=offset%2*550+5
        y=offset//2*815+20
        sheet.paste(im,(x,y))
        ImageDraw.Draw(sheet).text((x+4,y-16),f'PDF page {n}',fill='black')
    sheet.save(out/f'contact-{group+1}.png')
print(f'Rendered {pages} pages.')
