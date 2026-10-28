from pathlib import Path
import re, json

root = Path(__file__).resolve().parent
pages = (root/'source/original_layout.txt').read_text(encoding='utf-8').split('\f')
if not pages[-1].strip(): pages.pop()
inventory=[]
for i,t in enumerate(pages,1):
    (root/'source'/f'page_{i:03}.txt').write_text(t,encoding='utf-8')
    inventory.append({'pdf_page':i,'first_lines':t.strip().splitlines()[:4],'characters':len(t)})
(root/'source/page_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
print('Physical pages:',len(pages))
for i,t in enumerate(pages,1):
    if any(x in t[:300] for x in ['Introducing Decoherence','Basic Formalism and Interpretation','Decoherence Is Everywhere','Master-Equation Formulations','World of Spins','Of Buckey Balls','7 Decoherence','8 The Role','9 Observations','Appendix:','References','Index']):
        if len(t.strip().splitlines()[0])<75: print(i,repr(t.strip().splitlines()[:3]))
