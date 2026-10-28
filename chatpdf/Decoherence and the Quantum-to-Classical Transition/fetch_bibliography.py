"""Retain original references and official INSPIRE/Crossref records and BibTeX."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import json,re,urllib.request,urllib.parse,time,unicodedata
root=Path(__file__).resolve().parent
out=root/'source/bibliography'; out.mkdir(exist_ok=True)
txt='\n'.join((root/'source'/f'page_{i:03}.txt').read_text(encoding='utf-8') for i in range(395,420))
txt=re.sub(r'^.*References.*$','',txt,flags=re.M)
matches=list(re.finditer(r'^[ \t]*(\d+)\.[ \t]+(?=\S)',txt,re.M))
refs=[]
for i,m in enumerate(matches):
    raw=txt[m.end():matches[i+1].start() if i+1<len(matches) else len(txt)].strip()
    raw=re.sub(r'(\w)-\s*\n\s*(\w)',r'\1\2',raw)
    raw=re.sub(r'\s+',' ',raw)
    refs.append({'number':int(m[1]),'original':unicodedata.normalize('NFC',raw)})
(out/'original_references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),encoding='utf-8')
def get(url):
    for a in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'BibliographicVerification/1.0','Accept':'application/json, text/plain, */*'})
            with urllib.request.urlopen(req,timeout=45) as r:return r.read()
        except Exception:
            if a==2:raise
            time.sleep(1+a)
def norm(s):return ' '.join(re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',s).lower()))
def title_in_ref(title,raw):
    a=set(norm(title).split()); b=set(norm(raw).split())
    return len(a&b)/max(1,len(a))
def candidate_ok(c,raw):
    title=c.get('title',[''])[0]
    words=norm(raw)
    exact=re.sub(r'[^a-z0-9]','',norm(title)) in re.sub(r'[^a-z0-9]','',words)
    family=norm(c.get('author',[{}])[0].get('family','')) if c.get('author') else ''
    author_ok=bool(family) and family in words
    year=c.get('published',c.get('issued',{})).get('date-parts',[[0]])[0][0] or 0
    years=[int(y) for y in re.findall(r'\b(?:18|19|20)\d{2}\b',raw)]
    year_ok=any(abs(y-year)<=1 for y in years)
    volume=c.get('volume',''); page=re.split(r'[-–]',c.get('page',''))[0]
    numbers=re.findall(r'\b\d+\b',raw)
    location_ok=bool(volume and page) and volume in numbers and page in numbers
    return len(norm(title).split())>=3 and author_ok and (exact or (year_ok and location_ok and title_in_ref(title,raw)>=.60))
def run(ref):
    n=ref['number']; raw=ref['original']; prefix=out/f'ref{n:03}'
    result={**ref,'status':'unresolved'}
    cache=prefix.with_suffix('.json')
    if cache.exists():
        old=json.loads(cache.read_text(encoding='utf-8'))
        if old['status'] not in ['error','not_found']:
            old['original']=raw
            return old
    try:
        # Exact arXiv identifiers take precedence where the original prints one.
        arx=re.search(r'(?:quant-ph|hep-th|gr-qc|cond-mat)/\d{7}|\b\d{4}\.\d{4,5}\b',raw)
        if arx:
            query='arxiv:'+arx[0]
            ins=json.loads(get('https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':query,'size':5})))
            prefix.with_name(prefix.name+'_inspire_search.json').write_text(json.dumps(ins,ensure_ascii=False),encoding='utf-8')
            hits=ins.get('hits',{}).get('hits',[])
            if hits:
                h=hits[0];result.update(inspire_id=h['id'],match_method='printed_arxiv',match_score=1)
        if 'inspire_id' not in result:
            # Crossref's complete reference search is used as a DOI candidate, not proof.
            cr=json.loads(get('https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':raw,'rows':3})))
            prefix.with_name(prefix.name+'_crossref_search.json').write_text(json.dumps(cr,ensure_ascii=False),encoding='utf-8')
            candidates=cr['message']['items']
            valid=[c for c in candidates if c.get('title') and candidate_ok(c,raw)]
            if valid:
                c=valid[0];doi=c['DOI'];result.update(doi=doi,crossref_title=c['title'][0],match_score=title_in_ref(c['title'][0],raw))
                ins=json.loads(get('https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'doi:'+doi,'size':5})))
                prefix.with_name(prefix.name+'_inspire_search.json').write_text(json.dumps(ins,ensure_ascii=False),encoding='utf-8')
                hits=ins.get('hits',{}).get('hits',[])
                if hits:result.update(inspire_id=hits[0]['id'],match_method='doi_title')
                else:
                    # Search by title also, since older INSPIRE records may omit DOI.
                    ins=json.loads(get('https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'t "'+c['title'][0]+'"','size':5})))
                    prefix.with_name(prefix.name+'_inspire_title_search.json').write_text(json.dumps(ins,ensure_ascii=False),encoding='utf-8')
                    hits=ins.get('hits',{}).get('hits',[])
                    for h in hits:
                        titles=[t['title'] for t in h['metadata'].get('titles',[])]
                        if titles and max(title_in_ref(t,raw) for t in titles)>=.9:
                            result.update(inspire_id=h['id'],match_method='title');break
            else:
                # Original author initials precede the title; use its first clause for search.
                parts=raw.split(', ');k=0
                while k<len(parts) and re.match(r'^(?:[A-Z]\.|[A-Z]-[A-Z]\.)',parts[k]):k+=1
                title=parts[k] if k<len(parts) else raw
                result['title_query']=title
                ins=json.loads(get('https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'t "'+title+'"','size':5})))
                prefix.with_name(prefix.name+'_inspire_title_search.json').write_text(json.dumps(ins,ensure_ascii=False),encoding='utf-8')
                for h in ins.get('hits',{}).get('hits',[]):
                    titles=[t['title'] for t in h['metadata'].get('titles',[])]
                    if titles and max(title_in_ref(t,raw) for t in titles)>=.9:
                        result.update(inspire_id=h['id'],match_method='original_title',match_score=max(title_in_ref(t,raw) for t in titles));break
        if 'inspire_id' in result:
            url=f"https://inspirehep.net/api/literature/{result['inspire_id']}?format=bibtex"
            bib=get(url);prefix.with_name(prefix.name+'_official.bib').write_bytes(bib)
            result.update(status='official_inspire',source_url=url,bib_file=prefix.name+'_official.bib')
        elif 'doi' in result:
            url='https://api.crossref.org/works/'+urllib.parse.quote(result['doi'],safe='')+'/transform/application/x-bibtex'
            bib=get(url);prefix.with_name(prefix.name+'_official.bib').write_bytes(bib)
            result.update(status='official_crossref',source_url=url,bib_file=prefix.name+'_official.bib')
        else:result['status']='not_found'
    except Exception as e:result.update(status='error',error=str(e))
    cache.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result
if __name__=='__main__':
    print('References:',len(refs),flush=True)
    results=[]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for future in as_completed([ex.submit(run,r) for r in refs]):
            r=future.result();results.append(r)
            if len(results)%10==0:print('Fetched',len(results),'/',len(refs),flush=True)
    results.sort(key=lambda x:x['number'])
    (out/'retrieval_manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print({s:sum(r['status']==s for r in results) for s in set(r['status'] for r in results)},flush=True)
