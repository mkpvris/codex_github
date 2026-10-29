from pathlib import Path
import json, re
BASE=Path(__file__).resolve().parent
PROJECT=BASE.parent
OFFICIAL=[2,5,6,8,9,10,11,12,14,18,19,21,23,26,27,29,30,33,37]
FALLBACK=[4,7,13,15,16,17,20,28,34,35,36,38]
def append_fields(entry, fields):
    p=entry.rfind('}')
    body=entry[:p].rstrip()
    if not body.endswith(','):body+=','
    return body+'\n'+''.join('    '+k+' = {'+v+'},\n' for k,v in fields.items())+'}\n'
def entry_text(kind,n,fields):
    return '@'+kind+'{ref'+f'{n:02}'+',\n'+''.join('    '+k+' = {'+str(v)+'},\n' for k,v in fields.items() if v is not None)+'}\n'
def tex(x):
    return x.replace('&',r'\&').replace('_',r'\_').replace('%',r'\%')
def parse_entries(txt):
    pieces=re.split(r'(?m)(?=^@)',txt)
    out={}
    for p in pieces:
        m=re.match(r'@\w+\{(ref\d\d),',p)
        if m:out[int(m.group(1)[3:])]=p.strip()+'\n'
    return out
entries={}
for n in OFFICIAL:
    raw=(BASE/f'ref{n:02}_official.bib').read_text(encoding='utf-8')
    entry=re.sub(r'(@\w+\{)[^,]+,',lambda m:m.group(1)+f'ref{n:02},',raw,count=1)
    if n==18:entry=append_fields(entry,{'publisher':'Academic Press','address':'New York'})
    if n==26:entry=append_fields(entry,{'url':'http://www.jetp.ras.ru/cgi-bin/dn/e_020_04_1018.pdf'})
    if n==27:
        # The official month refers to the preprint, not the final journal issue.
        # Keep the raw export intact, but do not present it as a publication month.
        entry=re.sub(r'\n\s*month\s*=\s*"[^"]*",?','',entry)
        entry=append_fields(entry,{'journal':r'Revista Brasileira de F\'{i}sica','volume':'7','number':'2','pages':'261--270','url':'https://www.sbfisica.org.br/bjp/download/v07/v07a19.pdf'})
    entries[n]=entry
for n in FALLBACK:
    m=json.loads((BASE/f'ref{n:02}_crossref_exact.json').read_text(encoding='utf-8'))['message']
    authors=' and '.join(x['family']+', '+x.get('given','') for x in m['author'])
    year=m.get('published-print',m['published'])['date-parts'][0][0]
    title=m['title'][0].rstrip('*')
    fields={'author':tex(authors),'title':'{'+tex(title)+'}','doi':m['DOI'],'journal':tex(m.get('container-title',[''])[0]),'volume':m.get('volume'),'number':m.get('issue'),'pages':m.get('page','').replace('-','--'),'year':str(year)}
    if n==13:
        fields.pop('journal',None)
        fields.update({'booktitle':'Quantum Statistics in Optics and Solid-State Physics','series':'Springer Tracts in Modern Physics','volume':'66','publisher':'Springer','address':'Berlin'})
        entries[n]=entry_text('incollection',n,fields)
    else:
        if n==34:fields['note']='In: A Festschrift for I. I. Rabi, Series 2'
        if n==38:
            fields['journal']='Teoreticheskaya i Matematicheskaya Fizika'
            fields['volume']='27';fields['number']='2';fields['pages']='270--278'
            fields['url']='https://www.mathnet.ru/eng/tmf3327'
        entries[n]=entry_text('article',n,fields)
books=BASE/'fallback_bib_books.bib'
if books.exists():entries.update(parse_entries(books.read_text(encoding='utf-8')))
# Ref31 is correctly typed as a doctoral thesis, with an intentionally empty
# title: the original gives no actual title. The expected BibTeX missing-title
# warning is documented; do not fabricate a title or repeat "Ph.D. Thesis".
missing=sorted(set(range(1,39))-entries.keys())
if missing:raise SystemExit('Missing entries: '+str(missing))
text='% References [1]--[38], in original citation order.\n% Matching INSPIRE exports retained in bibliography_sources; keys mapped to refNN.\n% Missing publication fields supplemented only where recorded in acquisition_report.md.\n\n'
text+='\n'.join(entries[n].strip() for n in range(1,39))+'\n'
(PROJECT/'ref.bib').write_text(text,encoding='utf-8')
print('Wrote',len(entries),'entries; official INSPIRE bases',len(OFFICIAL))
for n in range(1,39):print(n,re.match(r'@(\w+)',entries[n]).group(1))
