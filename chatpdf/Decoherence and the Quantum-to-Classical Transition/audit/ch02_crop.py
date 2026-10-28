from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import RectangleObject
root=Path(__file__).resolve().parents[1]
r=PdfReader(root/'source/original.pdf')
specs=[(36,'ch02_fig01',55,55,389,215),(38,'ch02_fig02',55,375,389,512),(51,'ch02_fig03',80,57,351,151),(66,'ch02_fig04',99,57,339,169),(76,'ch02_fig05',85,61,358,205),(106,'ch02_fig06',98,365,342,501),(121,'ch02_fig07',130,426,306,546),(122,'ch02_fig08',88,52,355,171),(122,'ch02_fig09',88,447,355,547)]
for i,name,x0,top,x1,bottom in specs:
    p=r.pages[i]
    h=float(p.mediabox.height)
    p.cropbox=RectangleObject([x0,h-bottom,x1,h-top])
    w=PdfWriter()
    w.add_page(p)
    w.write(root/'figures'/f'{name}.pdf')
