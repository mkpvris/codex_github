from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import RectangleObject
root=Path(__file__).resolve().parent
r=PdfReader(root/'source/original.pdf')
for page,x0,top,x1,bottom,name in [(17,55,386,387,486,'ch01_fig01')]:
    p=r.pages[page-1]
    h=float(p.mediabox.height)
    rect=RectangleObject((x0,h-bottom,x1,h-top))
    p.mediabox=rect;p.cropbox=rect
    w=PdfWriter();w.add_page(p)
    with open(root/'figures'/f'{name}.pdf','wb') as f:w.write(f)
