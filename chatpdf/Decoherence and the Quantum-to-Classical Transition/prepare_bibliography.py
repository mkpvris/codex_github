from pathlib import Path
import json,re,unicodedata
root=Path(__file__).resolve().parent; folder=root/'source/bibliography'
refs=json.loads((folder/'original_references.json').read_text(encoding='utf-8'))
overrides={}
override_evidence={}
if (root/'audit/matching_override.json').exists():
    override_evidence={r['number']:r for r in json.loads((root/'audit/matching_override.json').read_text(encoding='utf-8'))}
op=root/'corrected_overrides.bib'
if op.exists():
    ot=op.read_text(encoding='utf-8-sig')
    for m in re.finditer(r'@\w+\s*\{\s*(ref\d+)\s*,',ot):
        j=m.end();depth=1
        while j<len(ot) and depth:
            if ot[j]=='{' and ot[j-1]!='\\':depth+=1
            elif ot[j]=='}' and ot[j-1]!='\\':depth-=1
            j+=1
        if depth:raise ValueError('Incomplete bibliography override '+m[1])
        overrides[m[1]]=ot[m.start():j]
def asciiword(s):
    return ''.join(c for c in unicodedata.normalize('NFKD',s).lower() if c.isalnum())
def fields(text):
    result={}
    for m in re.finditer(r'\b([A-Za-z]+)\s*=\s*',text):
        j=m.end();start=j
        if text[j:j+1]=='{':
            depth=1;j+=1;start=j
            while j<len(text) and depth:
                if text[j]=='{' and text[j-1]!='\\':depth+=1
                elif text[j]=='}' and text[j-1]!='\\':depth-=1
                j+=1
            value=text[start:j-1]
        elif text[j:j+1]=='"':
            start=j+1;j=start
            while j<len(text) and not(text[j]=='"' and text[j-1]!='\\'):j+=1
            value=text[start:j]
        else:value=text[j:].split(',')[0].strip()
        result[m[1].lower()]=value
    return result
def esc(s):
    s=s.replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
    return s
def primary_parts(raw):
    parts=raw.split(', ');i=0
    while i<len(parts) and re.match(r'^(?:[A-Z]\.|[A-Z]-[A-Z]\.)',parts[i]):i+=1
    return ' and '.join(parts[:i]),', '.join(parts[i:])
booknums={29,34,43,46,49,71,152,169,213,395,458,472,473,488,499,501,502,508}
def fallback(n,raw):
    authors,rest=primary_parts(raw)
    # Bibliographic information from the supplied book is kept in full, in order.
    # The proper entry type is retained, never an invented @misc substitute.
    typ='book' if n in booknums else ('incollection' if ', in:' in raw else 'article')
    if n in {324,503}:typ='unpublished'
    title,sep,note=rest.partition(', ')
    if typ=='incollection':
        title,_,note=rest.partition(', in: ')
    yearmatch=re.findall(r'\b(?:18|19|20)\d{2}\b',raw)
    vals={'author':authors,'title':'{'+esc(title)+'}'}
    if yearmatch:vals['year']=yearmatch[-1]
    if typ=='incollection':vals['booktitle']='{'+esc(note.split(', ')[0])+'}'
    if note:vals['note']=esc(note)
    if n==214:
        vals['eprint']='cond-mat/9511011';vals['archivePrefix']='arXiv'
    if n==391:vals['url']='http://plato.stanford.edu/archives/win2003/entries/qm-decoherence/'
    return '@'+typ+'{ref'+f'{n:03},\n'+''.join('  '+k+' = {'+v+'},\n' for k,v in vals.items())+'}\n'
entries=[];audit=[]
for ref in refs:
    n=ref['number'];raw=ref['original'];path=folder/f'ref{n:03}.json'
    if f'ref{n:03}' in overrides:
        entries.append('% Verified override; raw exports and deltas retained in audit.\n'+overrides[f'ref{n:03}']+'\n')
        audit.append({**ref,**override_evidence.get(n,{'status':'verified_override'}),'override_file':'corrected_overrides.bib'})
        continue
    meta=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'status':'not_found'}
    official=folder/meta.get('bib_file','MISSING')
    if official.is_file():
        bib=official.read_text(encoding='utf-8-sig'); f=fields(bib)
        primary=raw.split(', in:')[0]
        title=asciiword(f.get('title',''))
        words=set(re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',f.get('title','')).lower()))
        sourcewords=set(re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',primary).lower()))
        score=len(words&sourcewords)/max(1,len(words))
        years=[int(y) for y in re.findall(r'\b(?:18|19|20)\d{2}\b',raw)]
        bibyear=re.search(r'\d{4}',f.get('year',''))
        yearok=bool(bibyear) and any(abs(int(bibyear[0])-y)<=1 for y in years)
        arxivok=meta.get('match_method')=='printed_arxiv'
        titleok=(bool(title) and title in asciiword(primary)) or score>=.85
        accepted=(titleok and yearok) or arxivok
        # Earlier editions and reprinted chapters must not silently replace originals.
        if accepted:
            bib=re.sub(r'(@\w+\s*\{)[^,]+,',lambda m:m[1]+f'ref{n:03},',bib,count=1)
            entries.append('% '+meta.get('source_url','')+'\n'+bib+'\n')
            audit.append({**ref,'status':meta['status'],'source_url':meta.get('source_url'),'official_key':re.search(r'@\w+\s*\{([^,]+)',official.read_text(encoding='utf-8-sig'))[1],'title_score':score,'year_checked':yearok})
            continue
        meta={**meta,'status':'match_needs_review','export_title':f.get('title'),'export_year':f.get('year'),'title_score':score}
    entries.append('% Original bibliography retained; official matching unresolved.\n'+fallback(n,raw))
    audit.append({**ref,**{k:v for k,v in meta.items() if k not in ['original']}})
(root/'ref.bib').write_text('\n'.join(entries),encoding='utf-8')
(root/'audit/bibliography_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
unresolved=[r for r in audit if r['status'] in {'error','not_found','match_needs_review','unresolved'}]
(root/'audit/bibliography_unresolved.txt').write_text('\n'.join(f"[{r['number']}] {r['status']}: {r['original']}\n  Export: {r.get('export_title','')} ({r.get('export_year','')})" for r in unresolved),encoding='utf-8')
print('Entries:',len(entries),'Official:',sum(r['status'].startswith('official') for r in audit),'Source records:',sum(r['status'].startswith('source') for r in audit),'Unresolved:',len(unresolved))
