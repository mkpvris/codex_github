from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent;out=root/'audit/figure_renders';out.mkdir(exist_ok=True)
files=sorted((root/'figures').glob('ch06_fig*.pdf'))
def render(f):
    prefix=out/f.stem
    subprocess.run(['pdftoppm','-scale-to','700','-singlefile','-png',str(f),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return prefix.with_suffix('.png')
with ThreadPoolExecutor(max_workers=4) as pool:images=list(pool.map(render,files))
for start in range(0,len(images),8):
    sheet=Image.new('RGB',(1500,1440),'white');draw=ImageDraw.Draw(sheet)
    for j,f in enumerate(images[start:start+8]):
        im=Image.open(f);im.thumbnail((730,320));x=(j%2)*750;y=(j//2)*360
        sheet.paste(im,(x+(750-im.width)//2,y+30));draw.text((x+10,y+8),f.stem,fill='black')
    sheet.save(root/'audit'/f'ch06_figures_sheet_{start//8+1}.jpg',quality=94)
print('Figure sheets:',(len(images)+7)//8)
