import concurrent.futures, json, re, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'qa' / 'bibliography_cache'
CACHE.mkdir(exist_ok=True)
text = (ROOT / 'original' / 'SSBofDspv2.bbl').read_text(encoding='utf-8')
parts = re.split(r'\\bibitem\{([^}]+)\}', text)[1:]
records = []
for n in range(0, len(parts), 2):
    key, body = parts[n:n+2]
    blocks = re.split(r'\\newblock\s*', body)
    title = re.sub(r'\\em\s*|[{}$]', '', blocks[1]).strip().rstrip('.')
    title = re.sub(r'\\mathrm|\s+', ' ', title).strip()
    records.append({'number': n//2+1, 'key': key, 'original': body.strip(), 'title': title})

def request(url):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Academic translation bibliography verification contact local-user'})
            with urllib.request.urlopen(req, timeout=90) as res:
                return res.read().decode('utf-8')
        except Exception:
            if attempt == 4: raise
            time.sleep(2 ** attempt)

def fetch(record):
    key = record['key']
    cache_name = re.sub('[^A-Za-z0-9_.-]', '_', key)
    query = ('texkey ' + key) if ':' in key else ('title "' + record['title'] + '"')
    url = 'https://inspirehep.net/api/literature?' + urllib.parse.urlencode({'q': query, 'size': 10})
    dest = CACHE / (cache_name + '.json')
    if not dest.exists(): dest.write_text(request(url), encoding='utf-8')
    data = json.loads(dest.read_text(encoding='utf-8'))
    hits = data['hits']['hits']
    record['query_url'] = url
    record['hits_count'] = data['hits']['total']
    record['matches'] = []
    for hit in hits:
        md = hit['metadata']
        record['matches'].append({'id': hit['id'], 'titles': md.get('titles'), 'authors': [a['full_name'] for a in md.get('authors', [])], 'doi': md.get('dois'), 'arxiv': md.get('arxiv_eprints'), 'publication': md.get('publication_info'), 'bibtex_url': hit['links']['bibtex']})
    if len(hits) == 1:
        bibpath = CACHE / (cache_name + '.bib')
        if not bibpath.exists(): bibpath.write_text(request(hits[0]['links']['bibtex']), encoding='utf-8')
    print(record['number'], key, record['hits_count'], [m['titles'][0]['title'] for m in record['matches']], flush=True)
    return record

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, records))
    (ROOT / 'qa' / 'bibliography_searches.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
