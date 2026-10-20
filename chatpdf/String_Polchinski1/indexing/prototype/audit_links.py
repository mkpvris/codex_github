from pathlib import Path
from pypdf import PdfReader
import json, re

base = Path(__file__).resolve().parent
pdf = PdfReader(base / 'index_prototype.pdf')
destinations = {name: pdf.get_destination_page_number(dest) + 1 for name, dest in pdf.named_destinations.items()}
links = []
for pno, page in enumerate(pdf.pages, 1):
    for ref in page.get('/Annots', []):
        annot = ref.get_object()
        if annot.get('/Subtype') != '/Link':
            continue
        action = annot.get('/A', {})
        target = action.get('/D') if action.get('/S') == '/GoTo' else annot.get('/Dest')
        if isinstance(target, str):
            links.append({'from_physical_page': pno, 'target': target, 'to_physical_page': destinations.get(target)})
index_links = [x for x in links if x['from_physical_page'] == 4 and x['target'].startswith('page.')]
for link in index_links:
    link['displayed_number'] = int(link['target'].split('.')[1])
    link['matches'] = link['displayed_number'] == link['to_physical_page']
assert len(pdf.pages) == 4
assert index_links and all(x['matches'] for x in index_links)
assert any(x['from_physical_page'] == 4 and x['target'] == 'toc' and x['to_physical_page'] == 1 for x in links)
assert any(x['from_physical_page'] == 1 and x['to_physical_page'] == 4 for x in links)
ind = (base / 'index_prototype.ind').read_text(encoding='utf-8')
assert '\\hyperpage{1--3}' in ind
report = {'pdf': str(base / 'index_prototype.pdf'), 'pages': len(pdf.pages), 'destinations': destinations, 'all_links': links, 'index_page_links': index_links, 'index_numbers_correct': True, 'heading_backlink_to_contents': True, 'contents_link_to_index': True, 'range_1_to_3_present': True}
(base / 'link_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'pages': len(pdf.pages), 'index_links_verified': len(index_links), 'heading_backlink_to_contents': True, 'contents_link_to_index': True}))
