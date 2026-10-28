from pathlib import Path
from PIL import Image,ImageDraw
base=Path(__file__).resolve().parent
folder=base/'final_render'
for start in range(0,120,12):
    sheet=Image.new('RGB',(1600,2350),'#d0d0d0');draw=ImageDraw.Draw(sheet)
    for j,p in enumerate(range(start+1,start+13)):
        f=folder/f'page-{p:03}.png'
        im=Image.open(f).convert('RGB');im.thumbnail((390,550));x=(j%4)*400;y=(j//4)*780
        sheet.paste(im,(x+(400-im.width)//2,y+35));draw.text((x+10,y+8),f'PDF {p}',fill='black')
    sheet.save(folder/f'qa_first120_{start//12+1:02}.jpg',quality=94)
print('Prepared first120pagecontact sheets from finalPDF pagePNGs')
