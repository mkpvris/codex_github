from pathlib import Path
import json, urllib.request, urllib.parse
BASE=Path(__file__).resolve().parent
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AcademicBibliographyVerification/1.0'}),timeout=45) as r:return r.read()
doi='10.1007/BF01051242'
txt=fetch('https://inspirehep.net/api/literature?'+urllib.parse.urlencode({'q':'doi:'+doi,'size':5}))
(BASE/'ref38_doi_inspire_search.json').write_bytes(txt)
for hit in json.loads(txt)['hits']['hits']:
    url='https://inspirehep.net/api/literature/'+str(hit['id'])
    (BASE/'ref38_inspire.json').write_bytes(fetch(url))
    (BASE/'ref38_official.bib').write_bytes(fetch(url+'?format=bibtex'))
    print('ref38',hit['id'])
(BASE/'ref38_crossref_exact.json').write_bytes(fetch('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')))
(BASE/'ref27_publisher.pdf').write_bytes(fetch('https://www.sbfisica.org.br/bjp/download/v07/v07a19.pdf'))
for n,url in [(7,'https://journals.aps.org/pra/abstract/10.1103/PhysRevA.16.2126'),(38,'https://www.mathnet.ru/php/archive.phtml?jrnid=tmf&option_lang=eng&paperid=3327&wshow=paper')]:
    try:(BASE/f'ref{n:02}_publisher.html').write_bytes(fetch(url))
    except Exception as e:print('html error',n,str(e))
print('Special references fetched')
