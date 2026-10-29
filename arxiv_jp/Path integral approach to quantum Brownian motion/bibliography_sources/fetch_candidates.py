from pathlib import Path
import json, urllib.request, urllib.parse, time
from concurrent.futures import ThreadPoolExecutor

BASE = Path(__file__).resolve().parent
refs = json.loads((BASE/'inspire_references.json').read_text(encoding='utf-8-sig'))
def fetch(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AcademicBibliographyVerification/1.0'}),timeout=45) as r:
                return r.read().decode('utf-8')
        except Exception:
            if attempt == 3: raise
            time.sleep(2+attempt)

def one(x):
    r=x['reference']; n=int(r['label']); record=x.get('record',{}).get('$ref'); log=[]
    if record:
        js=fetch(record); (BASE/f'ref{n:02}_inspire.json').write_text(js,encoding='utf-8')
        bib=fetch(record+'?format=bibtex'); (BASE/f'ref{n:02}_official.bib').write_text(bib,encoding='utf-8')
        m=json.loads(js)['metadata']; log.append({'number':n,'record':record,'title':m.get('titles'),'doi':m.get('dois'),'pub':m.get('publication_info')})
    else:
        author=r.get('authors',[{}])[0].get('full_name','').split(',')[0]
        title=r.get('title',{}).get('title')
        year=r.get('publication_info',{}).get('year')
        q=('title "'+title+'"') if title else ('a '+author+((' and date '+str(year)) if year else ''))
        if n==21:q='a Caldeira and a Leggett and date 1983'
        if n==31:q='a Caldeira and date 1980'
        url='https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':q,'size':15})
        js=fetch(url); (BASE/f'ref{n:02}_inspire_search.json').write_text(js,encoding='utf-8')
        hits=json.loads(js)['hits']
        log.append({'number':n,'query':q,'total':hits['total'],'candidates':[{'id':h['id'],'title':h['metadata'].get('titles'),'doi':h['metadata'].get('dois'),'pub':h['metadata'].get('publication_info')} for h in hits['hits']]})
    return log[0]

with ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(one,refs))
(BASE/'candidate_summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for x in results: print(json.dumps(x,ensure_ascii=False))
