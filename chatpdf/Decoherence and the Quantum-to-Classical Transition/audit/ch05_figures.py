from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
root=Path(__file__).resolve().parents[1]
reader=PdfReader(root/'source/original.pdf')
specs={
1:(188,(115,51,320,179)),
2:(203,(112,50,337,187)),
3:(204,(113,401,337,537)),
4:(210,(52,60,389,490)),
5:(227,(108,398,327,517)),
6:(230,(110,49,337,188)),
7:(231,(88,50,339,181)),
8:(241,(68,267,372,468)),
}
for number,(physical,bbox) in specs.items():
    writer=PdfWriter(); page=writer.add_page(reader.pages[physical-1]); height=float(page.mediabox.height)
    x0,y0,x1,y1=bbox; box=RectangleObject([x0,height-y1,x1,height-y0]); page.cropbox=box; page.mediabox=RectangleObject(box)
    writer.write(root/'figures'/f'ch05_fig{number:02}.pdf')
print('8 vector figure crops saved.')
