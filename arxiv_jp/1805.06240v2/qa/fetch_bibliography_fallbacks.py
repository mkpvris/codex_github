import concurrent.futures, json, re, urllib.parse
from fetch_bibliography import ROOT, CACHE, request

identifiers = {
 'TonerTu1': '10.1103/PhysRevLett.75.4326',
 'TonerTu2': '10.1103/PhysRevE.58.4828',
 'RevModPhys.85.1143': '10.1103/RevModPhys.85.1143',
 'Kuramoto': '10.1007/978-3-642-69689-3',
 'MoriKuramoto': '10.1007/978-3-642-80376-5',
 'PhysRevLett.96.230602': '10.1103/PhysRevLett.96.230602',
 'PhysRevLett.99.140402': '10.1103/PhysRevLett.99.140402',
 'Buca:2018ccq': '10.1038/s41467-019-09757-y',
 'PhysRevB.18.4913': '10.1103/PhysRevB.18.4913',
 'kamenev2011field': '10.1017/CBO9781139003667',
}

def fetch(pair):
    key, doi = pair
    safe = re.sub('[^A-Za-z0-9_.-]', '_', key)
    queries = ['doi ' + doi]
    if key == 'Buca:2018ccq': queries += ['eprint 1804.06744', 'title "Non-stationary coherent quantum many-body dynamics through dissipation"']
    rec = {'key': key, 'doi': doi, 'searches': [], 'status': None}
    for i, query in enumerate(queries):
        url = 'https://inspirehep.net/api/literature?' + urllib.parse.urlencode({'q': query, 'size': 10})
        path = CACHE / (safe + '_additional_' + str(i) + '.json')
        if not path.exists(): path.write_text(request(url), encoding='utf-8')
        data = json.loads(path.read_text(encoding='utf-8'))
        rec['searches'].append({'url': url, 'total': data['hits']['total']})
        if data['hits']['total'] == 1:
            hit = data['hits']['hits'][0]
            rec.update({'status': 'INSPIRE', 'id': hit['id'], 'source_url': hit['links']['bibtex']})
            (CACHE / (safe + '.bib')).write_text(request(rec['source_url']), encoding='utf-8')
            break
    if rec['status'] is None:
        rec['status'] = 'Crossref'
        rec['source_url'] = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='') + '/transform/application/x-bibtex'
        dest = CACHE / (safe + '.bib')
        if not dest.exists(): dest.write_text(request(rec['source_url']), encoding='utf-8')
        mdurl = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='')
        (CACHE / (safe + '_crossref.json')).write_text(request(mdurl), encoding='utf-8')
    print(rec, flush=True)
    return rec

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, identifiers.items()))
    key = 'Zinn1996quantum'
    url = 'https://inspirehep.net/api/literature/421719?format=bibtex'
    (CACHE / (key + '.bib')).write_text(request(url), encoding='utf-8')
    records.append({'key':key, 'status':'INSPIRE', 'id':'421719', 'source_url':url, 'match_reason':'1996 third edition: author, title, year, monograph volume 92, 1008 pages; other hits refer to other editions.'})
    (ROOT / 'qa' / 'bibliography_fallbacks.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
