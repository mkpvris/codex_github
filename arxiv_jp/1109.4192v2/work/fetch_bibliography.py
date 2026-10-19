import concurrent.futures, json, re, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'work' / 'bibliography_cache'
CACHE.mkdir(exist_ok=True)
source = (ROOT / 'original' / 'DeftfinArxiv2.tex').read_text()
parts = re.split(r'\\bibitem\{([^}]+)\}', source.split(r'\begin{thebibliography}')[1].split(r'\end{thebibliography}')[0])[1:]
queries = {
 'peskin': 'title "An Introduction to quantum field theory" and a Peskin',
 'calzetta': 'title "Nonequilibrium Quantum Field Theory" and a Calzetta',
 'hydro': 'title "Dissipative effects in the Effective Field Theory for hydrodynamics"',
 'weiss': 'title "Quantum Dissipative Systems" and a Weiss',
 'Zhang': 'doi 10.1103/PhysRevD.47.3745',
 'Fetter': 'title "Quantum Theory of Many-Particle Systems"',
 'forster': 'a Forster and title Hydrodynamic',
 'weinberg': 'title Cosmology and a Weinberg and date 2008',
}

def request(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Academic-bibliography-verification/1.0'}), timeout=45) as res:
                return res.read().decode()
        except Exception:
            if attempt == 3: raise
            time.sleep(2 ** attempt)

def fetch(row):
    key = row['key']; out=[]
    ids=row['arxiv']
    for i, aid in enumerate(ids):
        name=re.sub(r'[^A-Za-z0-9_.-]','_',key)+f'_{i+1}'
        url='https://inspirehep.net/api/arxiv/'+aid
        jp=CACHE/(name+'.json'); bp=CACHE/(name+'.bib')
        if not jp.exists(): jp.write_text(request(url),encoding='utf-8')
        data=json.loads(jp.read_text(encoding='utf-8'))
        md=data['metadata']; actual=[a['value'] for a in md.get('arxiv_eprints',[])]
        if aid not in actual: raise ValueError((aid,actual))
        burl=url+'?format=bibtex'
        if not bp.exists(): bp.write_text(request(burl),encoding='utf-8')
        out.append({'arxiv':aid,'bibtex_url':burl,'file':bp.name,'titles':md.get('titles'),'authors':[a['full_name'] for a in md.get('authors',[])],'doi':md.get('dois'),'publication':md.get('publication_info')})
    if not ids:
        url='https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':queries[key],'size':10})
        jp=CACHE/(key+'_search.json')
        if not jp.exists(): jp.write_text(request(url),encoding='utf-8')
        data=json.loads(jp.read_text(encoding='utf-8'))
        row['search_url']=url
        row['search_hits']=[]
        for hit in data.get('hits',{}).get('hits',[]):
            md=hit['metadata']
            row['search_hits'].append({'id':hit['id'],'titles':md.get('titles'),'authors':[a['full_name'] for a in md.get('authors',[])],'doi':md.get('dois'),'publication':md.get('publication_info'),'imprints':md.get('imprints'),'bibtex_url':hit['links']['bibtex']})
    row['matches']=out
    print(row['number'],key,len(out),json.dumps(row.get('search_hits',[]),ensure_ascii=False),flush=True)
    return row

rows=[]
for n in range(0,len(parts),2):
    key,body=parts[n:n+2]; body=re.sub(r'(?m)%.*$','',body).strip()
    ids=list(dict.fromkeys(re.findall(r'(?:\d{4}\.\d{4,5}|(?:hep-th|hep-ph|gr-qc|astro-ph)/\d{7})',body)))
    rows.append({'number':n//2+1,'key':key,'original':body,'arxiv':ids})
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(fetch,rows))
(ROOT/'work/bibliography_matches.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
