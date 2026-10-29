from pathlib import Path
import json, urllib.request, urllib.parse, time
from concurrent.futures import ThreadPoolExecutor
BASE=Path(__file__).resolve().parent
DOIS={4:'10.1063/1.1678812',7:'10.1103/PhysRevA.16.2126',13:'10.1007/BFb0044957',15:'10.1103/PhysRevLett.46.1',16:'10.1063/1.1704304',17:'10.1016/0378-4371(78)90194-2',20:'10.1007/BF01008729',28:'10.1088/0305-4470/1/4/302',34:'10.1111/j.2164-0947.1977.tb02946.x',35:'10.1016/0370-1573(81)90033-8',36:'10.1016/0378-4371(79)90057-8'}
def fetch(url):
    for i in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'AcademicBibliographyVerification/1.0'})
            with urllib.request.urlopen(req,timeout=45) as r:return r.read().decode('utf-8')
        except Exception:
            if i==2:raise
            time.sleep(2)
def process(item):
    n,doi=item
    txt=fetch('https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'doi:'+doi,'size':5}))
    (BASE/f'ref{n:02}_doi_inspire_search.json').write_text(txt,encoding='utf-8')
    data=json.loads(txt);hits=data['hits']['hits']
    for hit in hits:
        rid=hit['id'];url='https://inspirehep.net/api/literature/'+str(rid)
        (BASE/f'ref{n:02}_inspire.json').write_text(fetch(url),encoding='utf-8')
        (BASE/f'ref{n:02}_official.bib').write_text(fetch(url+'?format=bibtex'),encoding='utf-8')
    raw=fetch('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''))
    (BASE/f'ref{n:02}_crossref_exact.json').write_text(raw,encoding='utf-8')
    return {'number':n,'doi':doi,'inspire_hits':[x['id'] for x in hits]}
with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(process,DOIS.items()))
(BASE/'doi_inspire_summary.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
for r in results:print(json.dumps(r))
