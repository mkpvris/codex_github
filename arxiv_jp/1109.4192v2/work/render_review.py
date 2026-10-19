from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'work/rendered_final'
OUT.mkdir(exist_ok=True)
subprocess.run(['pdftoppm','-scale-to','1400','-png',str(ROOT/'pdf/1109.4192v2_jp.pdf'),str(OUT/'page')],check=True)
files=sorted(OUT.glob('page-*.png'))
for i in range(0,len(files),9):
 sheet=Image.new('RGB',(1500,2190),'#dddddd');d=ImageDraw.Draw(sheet)
 for j,p in enumerate(files[i:i+9]):
  im=Image.open(p);im.thumbnail((480,680));x=(j%3)*500+10;y=(j//3)*730+30
  sheet.paste(im,(x,y));d.text((x,y-22),str(i+j+1),fill='black',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20))
 sheet.save(OUT/f'contact_{i//9+1:02d}.jpg',quality=90)
print('Rendered',len(files),'pages and',(len(files)+8)//9,'contact sheets.')
