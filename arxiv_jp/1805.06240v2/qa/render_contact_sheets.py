from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
root=Path(__file__).resolve().parents[1]
pages=sorted((root/'qa/rendered').glob('page-*.png'))
for i in range(0,len(pages),4):
    canvas=Image.new('RGB',(1600,2320),'#b6bbc1')
    d=ImageDraw.Draw(canvas)
    for j,p in enumerate(pages[i:i+4]):
        im=Image.open(p).convert('RGB')
        im.thumbnail((780,1100))
        x=(j%2)*800+10; y=(j//2)*1160+35
        canvas.paste(im,(x,y))
        d.text((x,y-22),p.stem,fill='black')
    canvas.save(root/f'qa/contact_{i+1:02d}_{min(i+4,len(pages)):02d}.png')
print(f'{len(pages)} pages, {(len(pages)+3)//4} contact sheets')
