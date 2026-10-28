from pathlib import Path
import json, re, io
from reportlab.pdfgen.canvas import Canvas
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

root = Path(__file__).resolve().parents[1]
reader = PdfReader(root/'source/original.pdf')
entries = []
seen_numbers = set()
with pdfplumber.open(root/'source/original.pdf') as pdf:
    for index in range(184, 255):
        page = pdf.pages[index]
        words = page.extract_words(x_tolerance=2, y_tolerance=2, extra_attrs=['fontname'])
        rows = []
        for w in sorted(words,key=lambda w:w['top']):
            row = next((r for r in rows if abs(r[0]['top']-w['top'])<2),None)
            if row is None: rows.append([w])
            else: row.append(w)
        body = []
        for row in rows:
            row.sort(key=lambda w:w['x0'])
            english=[w for w in row if re.fullmatch(r'[A-Za-z][A-Za-z-]+[,.:;!?]?',w['text'])]
            mathwords={'exp','cos','sin','coth','tanh','sinh','ln','log','Tr','TrS','TrE','Re','Im','if','for','int','fluc','therm','tot','eff','tunnel','pos','mom','max','dt','dq','dx','dX','dP','const'}
            prose = any(w['text'].strip('.,:;!?') not in mathwords for w in english) or row[0]['text'].startswith(('i.e.','e.g.'))
            if row[0]['x0']<85 and prose:
                body.append({'top':min(w['top'] for w in row),'bottom':max(w['bottom'] for w in row),'text':' '.join(w['text'] for w in row),'words':row})
        tags = []
        for word in words:
            m = re.fullmatch(r'\(5\.(\d+[a-z]?)\)[.,]?', word['text'])
            if m and word['x0'] > 340 and m.group(1) not in seen_numbers and not any(abs(w['top']-word['top'])<2 for w in body):
                tags.append((m.group(1), word))
                seen_numbers.add(m.group(1))
        for tag, word in tags:
            before = [w for w in body if w['bottom'] < word['top']]
            after = [w['top'] for w in body if w['top'] > word['bottom']]
            prev = max(before, key=lambda w:w['bottom']) if before else None
            top = prev['top'] + 8 if prev else 44
            bottom = min(after, default=591) - 2
            other = [t for t,w in tags if w['top'] >= top-3 and w['bottom'] <= bottom+3]
            # Consecutive subequations with no prose form one image block.
            key = '_'.join(other)
            if not key or any(e['key']==key for e in entries):
                continue
            writer = PdfWriter()
            outpage = writer.add_page(reader.pages[index])
            height = float(outpage.mediabox.height)
            if prev:
                stream = io.BytesIO()
                canvas = Canvas(stream, pagesize=(float(outpage.mediabox.width),height))
                canvas.setFillColorRGB(1,1,1)
                for w in prev['words']:
                    if w['bottom']>=top:
                        canvas.rect(w['x0']-.5,height-w['bottom']-.5,w['x1']-w['x0']+1,w['bottom']-w['top']+1,fill=1,stroke=0)
                canvas.save()
                stream.seek(0)
                outpage.merge_page(PdfReader(stream).pages[0])
            box = RectangleObject([48, height-bottom, 398, height-top])
            outpage.cropbox = box
            outpage.mediabox = RectangleObject(box)
            target=root/'figures'/f'ch05_eq_{key}.pdf'
            temporary=target.with_suffix('.pending.pdf')
            writer.write(temporary)
            temporary.replace(target)
            entries.append({'key':key,'numbers':['5.'+t for t in other],'pdf_page':index+1,'printed_page':index-13,'bbox_top':[48,top,398,bottom]})
(root/'audit/ch05_equations.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
found={int(re.match(r'\d+',n[2:]).group()) for e in entries for n in e['numbers']}
print('Blocks',len(entries),'missing numbered equations',sorted(set(range(1,206))-found))
print('\n'.join(str(e) for e in entries[:35]))
