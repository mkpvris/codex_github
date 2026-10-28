import re,json,pathlib,urllib.request,urllib.parse,concurrent.futures,time
BASE=pathlib.Path(__file__).resolve().parent.parent
OUT=BASE/'bib_sources'; OUT.mkdir(exist_ok=True)
BBL=(BASE/'source/main.bbl').read_text(encoding='utf-8')
CHUNKS=re.split(r'\\bibitem ',BBL)[1:]
def group(s,p):
    p=s.index('{',p); depth=1; end=p+1
    while depth:
        if s[end]=='{' and (end==0 or s[end-1]!='\\'): depth+=1
        elif s[end]=='}' and s[end-1]!='\\': depth-=1
        end+=1
    return s[p+1:end-1],end
def fields(s,field):
    vals=[]
    for m in re.finditer(r'\\bibinfo\s*\{\s*'+field+r'\s*\}',s):
        vals.append(group(s,m.end())[0])
    return vals
def tidy(s): return re.sub(r'\s+',' ',s).strip()
rows=[]
for num,s in enumerate(CHUNKS,1):
    key=re.search(r'\]\{([^}]+)\}',s).group(1)
    urls=re.findall(r'https://(?:doi.org/|arxiv.org/abs/)([^}]+)',s)
    doi=next((u[u.index('10.'):].strip() for u in urls if '10.' in u),'')
    if key=='CaldeiraLeggettA': doi='10.1016/0378-4371(83)90013-4'
    if key=='Lindblad1976': doi='10.1007/BF01608499'
    row=dict(number=num,key=key,doi=doi,arxiv=urls[0] if key=='Xu2023' else '',original_bbl=s)
    for f in ['author','title','journal','volume','pages','year','publisher','note']:
        row[f]=[tidy(t) for t in fields(s,f)]
    rows.append(row)
(OUT/'original_bbl_metadata.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
def fetch(url,accept=None):
    req=urllib.request.Request(url,headers={'User-Agent':'Bibliographic verification for scholarly translation','Accept':accept or 'application/json'})
    err=None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=45) as r: return r.read().decode('utf-8')
        except Exception as e:
            err=e
            if attempt<2: time.sleep(1+attempt*2)
    raise err
def collect(r):
    key=r['key']; log={'key':key,'number':r['number'],'doi':r['doi'],'arxiv':r['arxiv'],'queries':[]}
    if key in ['SuppMat','Note1','Note2']: return log
    if r['doi']: query='doi:'+r['doi']
    elif r['arxiv']: query='arxiv:'+r['arxiv']
    elif r['title']: query='t "'+r['title'][0]+'"'
    else: query='a Homa and date 2019 and j "Eur.Phys.J.D"'
    url='https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':query,'size':5})
    log['queries'].append(url)
    try:
        data=fetch(url); (OUT/(key+'_inspire_search.json')).write_text(data,encoding='utf-8')
        obj=json.loads(data); hits=obj.get('hits',{}).get('hits',[])
        total=obj.get('hits',{}).get('total',0); log['inspire_total']=total
        if hits:
            hit=hits[0]; meta=hit.get('metadata',{}); log['inspire_id']=hit['id']
            log['inspire_title']=meta.get('titles',[]); log['inspire_dois']=meta.get('dois',[])
            log['inspire_authors']=meta.get('authors',[]); log['inspire_arxiv']=meta.get('arxiv_eprints',[])
            biburl='https://inspirehep.net/api/literature/'+hit['id']+'?format=bibtex'
            bib=fetch(biburl,'application/x-bibtex'); (OUT/(key+'_inspire.bib')).write_text(bib,encoding='utf-8')
            log['inspire_bib_url']=biburl
    except Exception as e: log['inspire_error']=str(e)
    if r['doi']:
        url='https://api.crossref.org/works/'+urllib.parse.quote(r['doi'],safe='')
        try:
            data=fetch(url); (OUT/(key+'_crossref.json')).write_text(data,encoding='utf-8')
            log['crossref_url']=url
            biburl=url+'/transform/application/x-bibtex'
            bib=fetch(biburl,'application/x-bibtex'); (OUT/(key+'_crossref.bib')).write_text(bib,encoding='utf-8')
            log['crossref_bib_url']=biburl
        except Exception as e: log['crossref_error']=str(e)
    print(key+': INSPIRE='+str(log.get('inspire_total','error'))+' CROSSREF='+str('crossref_url' in log),flush=True)
    (OUT/(key+'_collection.json')).write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    return log
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        logs=list(ex.map(collect,rows))
    (OUT/'collection_summary.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding='utf-8')
