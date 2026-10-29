from pathlib import Path
from pypdf import PdfReader
import json, re

base=Path(__file__).resolve().parent
stem='Path_integral_approach_to_quantum_Brownian_motion_jp'
reader=PdfReader(base/'pdf'/f'{stem}.pdf')
destinations=reader.named_destinations
dest_pages={n:reader.get_destination_page_number(d)+1 for n,d in destinations.items()}
links=[]; broken=[]
for page_n,page in enumerate(reader.pages,1):
    for ar in page.get('/Annots',[]):
        a=ar.get_object()
        if a.get('/Subtype')!='/Link':continue
        act=a.get('/A',{})
        d=act.get('/D',a.get('/Dest'))
        if act.get('/S')=='/URI':
            links.append({'page':page_n,'type':'URI','target':str(act.get('/URI'))})
        elif d is not None:
            if isinstance(d,str):
                resolved=dest_pages.get(d)
                if resolved is None:broken.append({'page':page_n,'target':d})
                links.append({'page':page_n,'type':'GoTo','target':d,'target_page':resolved})
            else:links.append({'page':page_n,'type':'GoToArray','target':str(d)})
citations=[x for x in links if x.get('target','').startswith('cite.')]
bib=(base/'pdf'/f'{stem}.bbl').read_text(encoding='utf-8')
bibkeys=re.findall(r'\\bibitem\{([^}]+)\}',bib)
expected=[f'ref{x:02}' for x in range(1,39)]
eq_labels=[]
for f in sorted((base/'sections').glob('part*.tex')):
    eq_labels+=re.findall(r'\\label\{(eq:[^}]+)\}',f.read_text(encoding='utf-8'))
text='\n'.join(p.extract_text() for p in reader.pages)
ref_start=dest_pages['cite.ref01']
assert len(bibkeys)==38 and bibkeys==expected, bibkeys
assert not broken,broken
assert len(eq_labels)==len(set(eq_labels))
assert len(eq_labels)==124,len(eq_labels)
assert all(dest_pages['cite.'+k]>=ref_start for k in expected)
assert len([n for n in dest_pages if n.startswith('page.')])==len(reader.pages)
assert len([x for x in links if x['page']==1 and x['type']=='URI'])>=2
assert '??' not in text
assert '\ufffd' not in text
aux=(base/'pdf'/f'{stem}.aux').read_text(encoding='utf-8')
eq_anchors=re.findall(r'\\newlabel\{(eq:[^}]+)\}\{\{.*?\}\}\{(\d+)\}\{.*?\}\{([^}]+)\}',aux)
assert len(eq_anchors)==124,len(eq_anchors)
assert all(dest_pages[a]==int(p) for _,p,a in eq_anchors)
assert len({a for _,_,a in eq_anchors})==124
log=(base/'pdf'/f'{stem}.log').read_text(encoding='utf-8')
assert not re.search(r'Overfull|Missing character|ignoring duplicate destination|There were undefined references',log)
bibsource=(base/'ref.bib').read_text(encoding='utf-8')
dois=re.findall(r'(?im)^\s*doi\s*=\s*["{]([^"}]+)',bibsource)
uris={x['target'] for x in links if x['type']=='URI'}
assert all(any(u.endswith('/'+doi) for u in uris) for doi in dois)
assert all(any(x['target']=='cite.'+key for x in citations) for key in expected)
result={
 'pdf_pages':len(reader.pages),'equation_labels':len(eq_labels),'bibliography_entries':len(bibkeys),
 'bibliography_order':bibkeys,'bibliography_first_page':ref_start,
 'citation_links':len(citations),'all_internal_links_resolve':not broken,
 'equation_links_match_numbered_pages':True,'duplicate_pdf_destinations':False,
 'all_reference_doi_links_match_bibtex':True,'reference_doi_count':len(dois),
 'internal_link_count':len([x for x in links if x['type'].startswith('GoTo')]),
 'external_link_count':len([x for x in links if x['type']=='URI']),
 'cover_links':[x for x in links if x['page']==1 and x['type']=='URI'],
 'citation_destinations':{k:dest_pages['cite.'+k] for k in expected},
 'page_destinations':{k:v for k,v in dest_pages.items() if k.startswith('page.')},
 'links':links,
}
(base/'qa').mkdir(exist_ok=True)
(base/'qa'/'link_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(base/'qa'/'final_pdf_text.txt').write_text(text,encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('links','page_destinations','citation_destinations','bibliography_order')},ensure_ascii=True))
