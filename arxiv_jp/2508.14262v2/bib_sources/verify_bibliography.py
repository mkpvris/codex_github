import json,re,urllib.parse,concurrent.futures,difflib,unicodedata
from collect_bibliography import fetch,OUT,rows

def search(q):
    url='https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':q,'size':100})
    return url,json.loads(fetch(url))
def norm(s): return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s.lower()))
def verify(row):
    key=row['key']; old=OUT/(key+'_collection.json')
    if not old.exists(): return None
    log=json.loads(old.read_text(encoding='utf-8'))
    if key in ['BP2002','Weiss2011','Kleinert2009','AlickiLendi2007']:
        q={
          'BP2002':'t "The theory of open quantum systems" and a Breuer',
          'Weiss2011':'t "Quantum Dissipative Systems" and a Weiss',
          'Kleinert2009':'t "Path Integrals in Quantum Mechanics" and a Kleinert',
          'AlickiLendi2007':'t "Quantum Dynamical Semigroups" and a Alicki'
        }[key]
    elif log.get('inspire_total')==0:
        cross=OUT/(key+'_crossref.json')
        if not cross.exists(): return None
        msg=json.loads(cross.read_text(encoding='utf-8'))['message']
        title=msg.get('title',[''])[0]
        q='t "'+re.sub('[^a-zA-Z0-9 -]',' ',title)+'"'
    else: return None
    url,obj=search(q)
    (OUT/(key+'_inspire_secondary_search.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    hits=obj['hits']['hits']
    summary=[dict(id=x['id'],titles=x['metadata'].get('titles'),authors=x['metadata'].get('authors'),publication_info=x['metadata'].get('publication_info'),imprints=x['metadata'].get('imprints'),dois=x['metadata'].get('dois'),document_type=x['metadata'].get('document_type')) for x in hits]
    log['secondary_query_url']=url; log['secondary_candidates']=summary
    (OUT/(key+'_verification.json')).write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    print(key+': '+json.dumps([dict(id=x['id'],titles=x['titles'],publication_info=x['publication_info'],imprints=x['imprints'],dois=x['dois']) for x in summary],ensure_ascii=False),flush=True)
    return log
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: list(ex.map(verify,rows))
