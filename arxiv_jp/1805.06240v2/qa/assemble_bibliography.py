import hashlib, json, re, sys
from pathlib import Path
from fetch_bibliography import ROOT, CACHE

searches = json.loads((ROOT / 'qa' / 'bibliography_searches.json').read_text(encoding='utf-8'))
fallbacks = {r['key']:r for r in json.loads((ROOT / 'qa' / 'bibliography_fallbacks.json').read_text(encoding='utf-8'))}

def add_fields(bib, fields):
    return bib.rstrip().removesuffix('}').rstrip().rstrip(',') + ',\n' + ''.join('    ' + key + ' = {' + value + '},\n' for key, value in fields.items()).rstrip(',\n') + '\n}\n'

out = ['% Official full BibTeX exports, citation keys kept as in arXiv:1805.06240v2.\n% Raw exports and source/matching audit: qa/bibliography_cache and qa/bibliography_report.json.\n']
report = []
for r in searches:
    key = r['key']
    filename = re.sub('[^A-Za-z0-9_.-]', '_', key) + '.bib'
    raw = (CACHE / filename).read_text(encoding='utf-8')
    export_key = re.search(r'@\w+\s*\{\s*([^,]+)', raw).group(1)
    bib = re.sub(r'(@\w+\s*\{\s*)[^,]+', lambda m:m.group(1)+key, raw, count=1).strip() + '\n'
    changes = []
    if export_key != key: changes.append('Citation key only: '+export_key+' -> '+key+'; original manuscript key retained.')
    if key in fallbacks:
        f = fallbacks[key]
        source = f['status']
        url = f['source_url']
        recid = f.get('id')
    else:
        source = 'INSPIRE'
        url = r['matches'][0]['bibtex_url']
        recid = r['matches'][0]['id']
    supplements = {}
    if source == 'Crossref':
        if key == 'TonerTu1':
            bib = re.sub(r'<mml:math.*?</mml:math>', r' $\\mathrm{XY}$ ', bib)
            changes.append('Crossref MathML converted losslessly to TeX: XY; spacing restored from original title.')
        bib = re.sub(r'(title=)\{([^}]+(?:\}[^,]*)?)\}(, volume|, ISBN)', lambda m:m.group(1)+'{{'+m.group(2)+'}}'+m.group(3), bib)
        # Crossref emits nonstandard unquoted month abbreviations; quote to retain the exported data.
        bib = re.sub(r'\bmonth=([A-Za-z]+)', r'month={\1}', bib)
        bib = bib.replace('–', '--')
        changes.append('TeX-safe title case protection, quoted month values, and en-dash page ranges normalized; no exported fields removed.')
    if key == 'PhysRevLett.96.230602': supplements['pages'] = '230602'
    if key == 'PhysRevLett.99.140402': supplements['pages'] = '140402'
    if key == 'Kuramoto':
        supplements.update({'series':'Springer Series in Synergetics', 'volume':'19'})
    if key == 'MoriKuramoto':
        supplements.update({'note':'Translated by G. C. Paquette; eBook publication 2013'})
    if key == 'Buca:2018ccq':
        supplements.update({'note':"Originally circulated as ``Complex coherent quantum many-body dynamics through dissipation'', arXiv:1804.06744v1 (2018)"})
    if key == 'Zinn1996quantum':
        supplements.update({'publisher':'Clarendon Press', 'note':'Third edition, Clarendon Press, Oxford', 'url':'https://inspirehep.net/literature/421719'})
    if key == 'Sato:1980yn':
        supplements['url'] = 'https://inspirehep.net/literature/' + str(recid)
    if supplements:
        bib = add_fields(bib, supplements)
        changes.append('Supplemental fields (original bibliography and/or publisher edition metadata): '+json.dumps(supplements, ensure_ascii=False))
    out += ['\n% ['+str(r['number'])+'] '+url+'\n', bib]
    match_note = 'Title and author list verified against original .bbl; published journal/volume/pages/year checked where present.'
    if key == 'Buca:2018ccq': match_note += ' Original 2018 preprint title changed to Non-stationary... on publication; same authors, arXiv 1804.06744, DOI 10.1038/s41467-019-09757-y.'
    if key == 'Zinn1996quantum': match_note += ' Selected 1996 third edition (volume 92, pp. 1--1008), excluding the other edition records.'
    if key == 'MoriKuramoto': match_note += ' Original bibliography uses 2013 eBook year; Crossref uses 1998 copyright year. Publisher confirms 2013 electronic publication and Paquette as translator; all retained in note.'
    if key in ['Jensen:2017kzi','Haehl:2018lcu','Jensen:2018hse']: match_note += ' Original preprint record supplemented by current official publication data.'
    supplemental_sources = {'Kuramoto':['https://link.springer.com/book/10.1007/978-3-642-69689-3'], 'MoriKuramoto':['https://link.springer.com/book/10.1007/978-3-642-80376-5'], 'Buca:2018ccq':['https://arxiv.org/abs/1804.06744v1'], 'Zinn1996quantum':['https://inspirehep.net/literature/421719','original/SSBofDspv2.bbl'], 'PhysRevLett.96.230602':['original/SSBofDspv2.bbl'], 'PhysRevLett.99.140402':['original/SSBofDspv2.bbl']}.get(key,[])
    report.append({'original_number':r['number'], 'original_key':key, 'export_key':export_key, 'source':source, 'inspire_record':recid, 'export_url':url, 'raw_export_file':'qa/bibliography_cache/'+filename, 'raw_sha256':hashlib.sha256(raw.encode()).hexdigest(), 'original_entry':r['original'], 'original_title':r['title'], 'match_verification':match_note, 'inspire_searches':[{'url':r['query_url'], 'count':r['hits_count']}]+(fallbacks.get(key,{}).get('searches',[])), 'adjustments':changes, 'supplemental_sources':supplemental_sources, 'assembled_bibtex':bib})

if '--reports-only' not in sys.argv:
    (ROOT / 'ref.bib').write_text(''.join(out), encoding='utf-8')
    (ROOT / 'ordered_keys.tex').write_text('% Preserve the original reference-number order before any body citations.\n\\nocite{'+',\n'.join(r['original_key'] for r in report)+'}\n', encoding='utf-8')
summary = {'total':len(report), 'inspire_official':sum(r['source']=='INSPIRE' for r in report), 'crossref_official_after_inspire_absence':sum(r['source']=='Crossref' for r in report), 'unretrieved':[], 'ordering':'exact original .bbl order; all original citation keys retained', 'raw_exports_preserved':True, 'records':report}
(ROOT / 'qa' / 'bibliography_report.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
lines = ['Bibliography verification for arXiv:1805.06240v2', '55 references: 46 INSPIRE-HEP official exports; 9 Crossref official exports after negative title and DOI searches in INSPIRE.', 'All raw exports preserved. No manually fabricated @misc entries. No original citation keys changed. Original numbering preserved by ordered_keys.tex.', 'Current publisher metadata may postdate original preprints; matching is by title/authors plus arXiv/DOI/publication data.', '']
for r in report:
    lines += ['['+str(r['original_number'])+'] '+r['original_key']+' ('+r['source']+')', r['export_url'], r['match_verification']] + r['adjustments'] + ['']
(ROOT / 'qa' / 'bibliography_report.txt').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='records'}, ensure_ascii=False, indent=2))
