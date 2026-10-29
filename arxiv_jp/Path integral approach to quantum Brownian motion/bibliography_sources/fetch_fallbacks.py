from pathlib import Path
import json, urllib.request, urllib.parse, time
from concurrent.futures import ThreadPoolExecutor
BASE=Path(__file__).resolve().parent
def fetch(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AcademicBibliographyVerification/1.0'}),timeout=45) as r:return r.read().decode('utf-8')
        except Exception:
            if attempt==3:raise
            time.sleep(2)
queries={
4:'Kostin Journal Chemical Physics 57 3589 1972',7:'Dekker Physical Review A 16 2116 1977',
13:'Haake Statistical treatment open systems Springer Tracts Modern Physics 66 1973',
15:'Benguria Kac Physical Review Letters 46 1 1981',16:'Ford Kac Mazur Journal Mathematical Physics 6 504 1965',
17:'Iche Nozieres Physica 91 485 1978',20:'Zwanzig Journal Statistical Physics 9 215 1973',
28:'Papadopoulos Journal Physics A 1 413 1968',34:'Feshbach Tikochinsky Transactions New York Academy Sciences 38 44 1977',
35:'Dekker Physics Reports 80 1 1981',36:'Dekker Physica A 95 311 1979',38:'Svinin Theoretical Mathematical Physics 27 270 1976'}
additional={18:'117200',21:'176413',27:'4884',30:'128975'}
def cross(item):
    n,q=item
    js=fetch('https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':q,'rows':3}))
    (BASE/f'ref{n:02}_crossref_search.json').write_text(js,encoding='utf-8')
    return {'number':n,'candidates':[{'doi':m.get('DOI'),'title':m.get('title'),'author':m.get('author'),'pub':m.get('container-title'),'volume':m.get('volume'),'page':m.get('page'),'year':m.get('published')} for m in json.loads(js)['message']['items']]}
with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(cross,queries.items()))
for n,recid in additional.items():
    uri='https://inspirehep.net/api/literature/'+recid
    (BASE/f'ref{n:02}_inspire.json').write_text(fetch(uri),encoding='utf-8')
    (BASE/f'ref{n:02}_official.bib').write_text(fetch(uri+'?format=bibtex'),encoding='utf-8')
    m=json.loads((BASE/f'ref{n:02}_inspire.json').read_text(encoding='utf-8'))['metadata']
    print('INSPIRE',n,recid,json.dumps(m.get('authors')),json.dumps(m.get('imprints')),json.dumps(m.get('publication_info')))
(BASE/'crossref_summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for x in results:print(json.dumps(x,ensure_ascii=False))
