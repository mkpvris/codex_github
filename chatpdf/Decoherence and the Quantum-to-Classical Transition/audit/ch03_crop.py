from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

base = Path(__file__).resolve().parents[1]
reader = PdfReader(base / 'source' / 'original.pdf')
# Bounding boxes use source points, measured from the top left.
specs = {
    1: (131, (55, 455, 389, 560)),
    2: (135, (110, 56, 330, 176)),
    3: (135, (95, 210, 350, 309)),
    4: (155, (100, 389, 345, 516)),
    5: (157, (114, 49, 324, 168)),
    6: (158, (103, 334, 331, 481)),
    7: (160, (97, 382, 333, 537)),
    8: (161, (107, 50, 337, 491)),
    9: (162, (96, 381, 337, 529)),
    10: (163, (121, 429, 315, 556)),
    11: (164, (101, 52, 333, 538)),
}
for number, (physical, bbox) in specs.items():
    writer = PdfWriter()
    page = writer.add_page(reader.pages[physical - 1])
    height = float(page.mediabox.height)
    x0, y0, x1, y1 = bbox
    rectangle = RectangleObject([x0, height - y1, x1, height - y0])
    page.cropbox = rectangle
    page.mediabox = RectangleObject(rectangle)
    writer.write(base / 'figures' / f'ch03_fig{number:02}.pdf')
print('Saved 11 vector figure crops.')
