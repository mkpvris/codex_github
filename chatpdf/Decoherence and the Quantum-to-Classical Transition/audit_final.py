from pathlib import Path
from pypdf import PdfReader
import json,re,hashlib,collections
root=Path(__file__).resolve().parent
config=json.loads((root/'project_config.json').read_text(encoding='utf-8'))
pdf=root/'pdf'/config['pdf_filename']
reader=PdfReader(pdf);dests=reader.named_destinations
uris=[];gotos=[];invalid=[];samples=[]
for i,p in enumerate(reader.pages,1):
    for a in p.get('/Annots',[]):
        a=a.get_object();action=a.get('/A',{})
        if action.get('/S')=='/URI':uris.append({'page':i,'uri':str(action['/URI'])})
        target=action.get('/D',a.get('/Dest'))
        if target is not None and isinstance(target,str):
            gotos.append({'page':i,'target':target})
            if target not in dests:invalid.append({'page':i,'target':target})
            if target.startswith('cite.ref') and len(samples)<12:
                dp=reader.get_destination_page_number(dests[target])
                samples.append({'from_pdf_page':i,'destination':target,'target_pdf_page':dp+1,'target_is_bibliography':bool(re.search(r'\[\s*\d+\s*\]',reader.pages[dp].extract_text()))})
keys=re.findall(r'\\bibitem\{(ref\d+)\}',(root/'build/Schlosshauer_Decoherence_jp.bbl').read_text(encoding='utf-8'))
citations=[g for g in gotos if g['target'].startswith('cite.ref')]
uri_values=[u['uri'] for u in uris]
result={'pdf_pages':len(reader.pages),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'bibliography_entries':len(keys),'bibliography_original_order_preserved':keys==[f'ref{i:03}' for i in range(1,524)],'named_citation_destinations':sum(n.startswith('cite.ref') for n in dests),'source_page_anchors':sum(n.startswith('srcpage:') for n in dests),'internal_links':len(gotos),'citation_links':len(citations),'unresolved_internal_destinations':invalid,'external_links':len(uris),'doi_links':sum('doi.org/' in x for x in uri_values),'arxiv_links':sum('arxiv.org/' in x for x in uri_values),'publisher_cover_link':any(u['page']==1 and u['uri']=='https://link.springer.com/book/10.1007/978-3-540-35775-9' for u in uris),'citation_destination_samples':samples}
(root/'audit/final_pdf_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'audit/final_external_links.json').write_text(json.dumps(uris,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='citation_destination_samples'},ensure_ascii=False,indent=2))
assert result['bibliography_original_order_preserved'] and result['named_citation_destinations']==523
assert not invalid and result['publisher_cover_link']
assert all(x['target_is_bibliography'] for x in samples)
