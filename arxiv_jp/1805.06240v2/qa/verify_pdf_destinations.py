from pathlib import Path
import re,json
from pypdf import PdfReader
import pdfplumber
root=Path(__file__).resolve().parents[1]
path=root/'pdf/1805.06240v2_jp.pdf'
r=PdfReader(path)
keys=re.findall(r'\\bibitem\{([^}]+)\}',(root/'original/SSBofDspv2.bbl').read_text())
results=[]
with pdfplumber.open(path) as doc:
    for number,key in enumerate(keys,1):
        dest=r.named_destinations['cite.'+key]
        p=r.get_destination_page_number(dest)
        top=float(doc.pages[p].height)-float(dest.top)
        excerpt=doc.pages[p].crop((65,max(0,top-3),535,min(float(doc.pages[p].height),top+35))).extract_text() or ''
        labels=[w for w in doc.pages[p].extract_words() if w['text']=='['+str(number)+']' and 65<=w['x0']<=90]
        offsets=[w['top']-top for w in labels]
        good=any(-3<=delta<=25 for delta in offsets)
        results.append({'number':number,'key':key,'page':p+1,'correct_reference_number_within_25pt_below_target':good,'label_vertical_offset_pt':offsets,'target_text':excerpt})
report={'all_55_citation_destinations_land_on_correct_numbered_reference':all(x['correct_reference_number_within_25pt_below_target'] for x in results),'method':'Hyperref anchors sit just above bibliography items; verify expected printed [n] in label column within 25pt below each named target.','results':results}
(root/'qa/pdf_destination_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Correct numbered citation destinations:',sum(x['correct_reference_number_within_25pt_below_target'] for x in results),'/',len(results))
assert report['all_55_citation_destinations_land_on_correct_numbered_reference']
