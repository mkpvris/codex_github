"""Bibliographic follow-up; separate override outputs, no mutation of root ref.bib."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import urllib.request,urllib.parse,json,re,time,unicodedata
root=Path(__file__).resolve().parent
folder=root/'source/bibliography'
out=folder/'followup_ch02';out.mkdir(exist_ok=True)
refs={r['number']:r['original'] for r in json.loads((folder/'original_references.json').read_text(encoding='utf-8'))}
def get(url):
    for a in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'BibliographyVerification/1.0','Accept':'application/json, text/plain, */*'})
            with urllib.request.urlopen(req,timeout=35) as r:return r.read()
        except Exception:
            if a==2:raise
            time.sleep(a+1)
def norm(s):return ''.join(x for x in unicodedata.normalize('NFKD',s).lower() if x.isalnum())
queries={
14:('arxiv:quant-ph/9908008',None),
17:('doi:10.1007/978-3-662-05328-7','10.1007/978-3-662-05328-7'),
19:('doi:10.1007/BF01397477','10.1007/BF01397477'),
40:('doi:10.1515/9781400854554','10.1515/9781400854554'),
62:('doi:10.1007/BF01343064','10.1007/BF01343064'),
70:('doi:10.1038/121580a0','10.1038/121580a0'),
98:('arxiv:quant-ph/9908066','10.1103/PhysRevLett.84.2525'),
108:('arxiv:quant-ph/9905004','10.1007/3-540-46657-6_2'),
111:('doi:10.1103/PhysRevA.72.042113','10.1103/PhysRevA.72.042113'),
128:('doi:10.1007/978-1-4757-0671-0_3','10.1007/978-1-4757-0671-0_3'),
137:('doi:10.1007/978-3-540-68001-7','10.1007/978-3-540-68001-7'),
152:('doi:10.1007/3-540-12732-1','10.1007/3-540-12732-1'),
175:('doi:10.1007/978-1-4615-6808-7','10.1007/978-1-4615-6808-7'),
189:('arxiv:quant-ph/0512136','10.1016/0375-9601(89)90066-2'),
214:('arxiv:cond-mat/9511011',None),
218:('doi:10.1142/4239','10.1142/4239'),
241:('doi:10.1007/978-3-642-79504-6','10.1007/978-3-642-79504-6'),
253:('doi:10.1002/0471713465','10.1002/0471713465'),
258:('doi:10.1007/BF01342460','10.1007/BF01342460'),
342:('doi:10.1145/167088.167097','10.1145/167088.167097'),
336:('arxiv:quant-ph/9708022','10.1088/0034-4885/61/2/002'),
344:('doi:10.1109/SFCS.1994.365700','10.1109/SFCS.1994.365700'),
367:('doi:10.1063/1.882692','10.1063/1.882692'),
374:('doi:10.1126/science.290.5491.498','10.1126/science.290.5491.498'),
459:('doi:10.1098/rspa.1996.0048','10.1098/rspa.1996.0048'),
469:('doi:10.1007/978-1-4684-8771-8_3','10.1007/978-1-4684-8771-8_3'),
}
def fetch(n,q,doi):
    path=out/f'ref{n:03}'
    result={'number':n,'original':refs[n],'query':q}
    cache=out/f'ref{n:03}_result.json'
    if cache.exists():
        old=json.loads(cache.read_text(encoding='utf-8'))
        if old.get('query')==q and not old.get('error'):return old
    try:
        searchurl='https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':q,'size':10})
        data=get(searchurl);path.with_suffix('.search.json').write_bytes(data)
        hits=json.loads(data).get('hits',{}).get('hits',[])
        result['inspire_candidates']=[{'id':h['id'],'title':[x.get('title') for x in h['metadata'].get('titles',[])],'authors':[x.get('full_name') for x in h['metadata'].get('authors',[])],'publication_info':h['metadata'].get('publication_info'),'arxiv':h['metadata'].get('arxiv_eprints')} for h in hits]
        for h in hits:
            url=f"https://inspirehep.net/api/literature/{h['id']}?format=bibtex"
            dest=out/f"ref{n:03}_inspire_{h['id']}.bib";dest.write_bytes(get(url))
        if doi:
            url='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
            data=get(url);path.with_suffix('.crossref.json').write_bytes(data)
            info=json.loads(data)['message']
            result['crossref']={k:info.get(k) for k in ['title','author','editor','published','issued','type','page','volume','publisher','DOI','ISBN','container-title']}
            biburl=url+'/transform/application/x-bibtex';dest=out/f'ref{n:03}_crossref.bib';dest.write_bytes(get(biburl))
    except Exception as e:result['error']=str(e)
    (out/f'ref{n:03}_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result
if __name__=='__main__':
    results=[]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for f in as_completed([ex.submit(fetch,n,q,d) for n,(q,d) in queries.items()]):
            r=f.result();results.append(r);print(r['number'],'done',r.get('error',''),flush=True)
    (out/'retrieval_manifest.json').write_text(json.dumps(sorted(results,key=lambda r:r['number']),ensure_ascii=False,indent=2),encoding='utf-8')
