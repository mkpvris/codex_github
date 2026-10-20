from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
root = Path(__file__).resolve().parent
paths = [root / f'ch06_08_layout-{n}.png' for n in range(151,248)]
for batch in range(0,len(paths),12):
    canv = Image.new('RGB',(1320,2580),'#d9d9d9')
    draw = ImageDraw.Draw(canv)
    for i,p in enumerate(paths[batch:batch+12]):
        im = Image.open(p).convert('RGB')
        im.thumbnail((420,610))
        x=(i%3)*440+10; y=(i//3)*645+25
        canv.paste(im,(x,y))
        draw.text((x,y-18),f'PDF {p.stem[-3:]}',fill='black')
    canv.save(root / f'ch06_08_contact-{batch//12+1:02d}.png')
print('9 contact sheets ready')
