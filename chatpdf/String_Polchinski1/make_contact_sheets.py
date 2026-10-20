from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import sys

root = Path(__file__).resolve().parent / "qa"
prefix = sys.argv[1] if len(sys.argv) > 1 else "compiled-ch01"
paths = sorted(root.glob(prefix + "-*.png"))
cell_w, cell_h = 360, 535
for start in range(0, len(paths), 12):
    batch = paths[start:start+12]
    sheet = Image.new("RGB", (cell_w*4, cell_h*3), "#cccccc")
    draw = ImageDraw.Draw(sheet)
    for j, path in enumerate(batch):
        image = Image.open(path).convert("RGB")
        image.thumbnail((cell_w-12, cell_h-28))
        x = (j % 4)*cell_w + (cell_w-image.width)//2
        y = (j//4)*cell_h + 24
        sheet.paste(image, (x,y))
        draw.text(((j % 4)*cell_w+8, (j//4)*cell_h+5), path.stem, fill="black")
    target = root / f"contact_{prefix}_{start//12+1:02d}.png"
    sheet.save(target)
    print(target)
