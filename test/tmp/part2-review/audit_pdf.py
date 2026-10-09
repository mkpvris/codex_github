from pathlib import Path
import json,re
from pypdf import PdfReader

root=Path(r'C:\codex\EFTofOpenSystems\part2')
r=PdfReader(root/'pdf/template.pdf')
dests=r.named_destinations
links=[]
broken=[]
for n,p in enumerate(r.pages,1):
    for ref in p.get('/Annots',[]):
        a=ref.get_object()
        if a.get('/Subtype')!='/Link': continue
        action=a.get('/A',{})
        if hasattr(action,'get_object'): action=action.get_object()
        d=a.get('/Dest') or action.get('/D')
        uri=action.get('/URI')
        if isinstance(d,str):
            if d not in dests: broken.append({'page':n,'dest':d})
            links.append({'page':n,'dest':d,'rect':[float(x) for x in a.get('/Rect',[])]})
        if uri: links.append({'page':n,'uri':str(uri)})
toc=(root/'pdf/template.toc').read_text(encoding='utf-8')
sections=[]
for line in toc.splitlines():
    if line.startswith('\\contentsline {section}'):
        match=re.search(r'\}\{(\d+)\}\{([^{}]+)\}%',line)
        if match: sections.append({'toc':line,'page':int(match.group(1)),'destination':match.group(2)})
refs=next(x['page'] for x in sections if '}{参考文献}' in x['toc'])
report={
  'pages':len(r.pages),
  'toc_page':r.get_destination_page_number(dests['toc'])+1,
  'sections':sections,
  'reference_page':refs,
  'reference_heading_links_to_toc':[x for x in links if x['page']==refs and x.get('dest')=='toc'],
  'bibliography_links':[x for x in links if x['page']==refs and 'uri' in x],
  'citation_link_count':sum(x.get('dest','').startswith('cite.') for x in links),
  'appendix_link_count':sum('appendix.' in x.get('dest','') or 'subsection.' in x.get('dest','') for x in links),
  'broken_named_links':broken,
  'page_text_lengths':[len(p.extract_text() or '') for p in r.pages]
}
assert not broken, broken
assert report['reference_heading_links_to_toc'], 'Missing bibliography heading -> TOC link'
assert len(report['bibliography_links'])>=2
Path(r'C:\codex\test\tmp\part2-review\appendix-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
