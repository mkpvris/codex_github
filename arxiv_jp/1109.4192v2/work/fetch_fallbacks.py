import json,urllib.request,urllib.parse,concurrent.futures,sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'work/bibliography_cache'
requests={
'peskin_1.bib':'https://inspirehep.net/api/literature/407703?format=bibtex',
'calzetta_1.bib':'https://inspirehep.net/api/literature/1384872?format=bibtex',
'weinberg_1.bib':'https://inspirehep.net/api/literature/794379?format=bibtex',
'Zhang_1.bib':'https://api.crossref.org/works/10.1103/PhysRevE.47.3745/transform/application/x-bibtex',
'weiss_1.bib':'https://api.crossref.org/works/10.1142/6738/transform/application/x-bibtex',
'forster_1.bib':'https://api.crossref.org/works/10.1201/9780429493683/transform/application/x-bibtex',
'weiss_search3.json':'https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'doi 10.1142/6738','size':10}),
'Zhang_search3.json':'https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'doi 10.1103/PhysRevE.47.3745','size':10}),
'weiss_crossref.json':'https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':'Ulrich Weiss Quantum Dissipative Systems 2008','rows':5}),
'forster_crossref.json':'https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':'Dieter Forster Hydrodynamic Fluctuations Broken Symmetry Correlation Functions','rows':3}),
'Fetter_search2.json':'https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'a Fetter and a Walecka','size':10}),
'Zhang_search2.json':'https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'title "Path-integral formalism for classical Brownian motion"','size':10}),
'weiss_search2.json':'https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'title "Quantum Dissipative Systems" and date 2008','size':10}),
'forster_search2.json':'https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'title "Hydrodynamic Fluctuations"','size':10}),
'hydro_search2.json':'https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'a Endlich and a Nicolis and a Porto and a Wang','size':10}),
}
def fetch(kv):
 k,u=kv;p=C/k
 if not p.exists():
  with urllib.request.urlopen(u,timeout=60) as r:p.write_bytes(r.read())
 if k.endswith('.bib'):print(k,p.read_text(encoding='utf-8'),flush=True)
 else:
  d=json.loads(p.read_text(encoding='utf-8'));hits=d.get('hits',{}).get('hits')
  if hits is not None:print(k,[(h['id'],h['metadata'].get('titles')) for h in hits],flush=True)
  else:print(k,[(h.get('DOI'),h.get('title'),h.get('published')) for h in d['message']['items']],flush=True)
 return {'file':k,'url':u}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:out=list(p.map(fetch,requests.items()))
(ROOT/'work/fallback_sources.json').write_text(json.dumps(out,indent=2))

