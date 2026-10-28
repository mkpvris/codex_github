from pathlib import Path
import json,re,unicodedata
root=Path(__file__).resolve().parents[1];folder=root/'source/bibliography'
audit=json.loads((root/'audit/bibliography_audit.json').read_text(encoding='utf-8'))
issues=[]
for r in audit:
    if not r['status'].startswith('official'):continue
    n=r['number'];raw=unicodedata.normalize('NFKC',r['original']);p=folder/f'ref{n:03}_official.bib';text=p.read_text(encoding='utf-8-sig')
    m=re.search(r'\bauthor\s*=\s*(?:"([^"]+)"|\{([^\n]+)\})',text,re.I)
    official=unicodedata.normalize('NFKC',(m[1] or m[2]) if m else '')
    first=raw.split(', ')[0];surname=re.sub(r'^(?:[A-Z]\.?[- ]?)+\s*','',first).strip()
    norm=lambda s:''.join(c for c in unicodedata.normalize('NFKD',s).lower() if c.isalnum())
    reason=[]
    if official and norm(surname) and norm(surname) not in norm(official):reason.append('author mismatch')
    if not official and 'editor' not in text:reason.append('missing author/editor')
    crfile=folder/f'ref{n:03}_crossref_search.json'
    if crfile.exists():
        cr=json.loads(crfile.read_text(encoding='utf-8'))['message']['items'];meta=json.loads((folder/f'ref{n:03}.json').read_text(encoding='utf-8'))
        expected=meta.get('doi','').lower();bibdoi=re.search(r'\bdoi\s*=\s*["{]([^"}]+)',text,re.I)
        if expected and bibdoi and expected!=bibdoi[1].lower():reason.append('INSPIRE DOI differs from original-matched Crossref DOI')
    if reason:issues.append({'number':n,'original':raw,'official_author':official,'surname':surname,'issues':reason,'raw_export':text})
(root/'audit/autoaccepted_followup_audit.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf-8')
print('Potential automatic-match issues',len(issues));print([(x['number'],x['issues']) for x in issues])
