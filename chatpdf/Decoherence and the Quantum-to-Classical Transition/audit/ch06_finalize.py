from pathlib import Path
import re,json
base=Path(__file__).resolve().parents[1]
p=base/'chapters/ch06.tex';t=p.read_text(encoding='utf-8')
start=t.index('% 原文 p.248')
end=t.index('共振器の周波数が、',start)
figs=t[start:end]
t=t[:start]+t[end:]
pos=t.index('% 原文 p.249')
t=t[:pos]+figs+t[pos:]
p.write_text(t,encoding='utf-8')
texts='\n'.join((base/f'chapters/{f}').read_text(encoding='utf-8') for f in ['ch06.tex','ch06_b.tex','ch06_c.tex','ch06_d.tex','ch06_e.tex'])
audit={'status':'complete','printed_pages':[243,291],'physical_pages':[256,304],'equation_tags':re.findall(r'\\tag\{([^}]+)\}',texts),'figures':re.findall(r'figures/([^}]+)',texts),'source_page_markers':re.findall(r'% 原文 p\.(\d+)',texts),'paragraph_blocks':len(re.findall(r'\n\n[^%\\\n]',texts)),'footnotes':texts.count('\\footnote{'),'uncertainties':[],'original_source_issues_preserved':[{'equation':'6.33','page':273,'issue':'Original visually prints a positive +hbar^2/(2C) second-derivative kinetic term; preserved without silent correction.'},{'page':257,'issue':'Original says coherence restored in C2 despite preceding discussion referring to C1; preserved.'}],'figure_extraction':'Handled by root agent. All captions translated; original internal labels retained as needed.'}
(base/'audit/ch06_coverage.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
import pdfplumber
pdf=pdfplumber.open(base/'source/original.pdf')
parts=[]
for physical in range(420,428):
    page=pdf.pages[physical-1]; w=page.width;h=page.height
    for side,bbox in [('L',(42,40,w/2,h-40)),('R',(w/2,40,w-35,h-40))]:
        parts.append(f'\n=== PRINTED {physical-11} {side} ===\n'+(page.crop(bbox).extract_text(layout=False) or ''))
(base/'audit/index_source_columns.txt').write_text('\n'.join(parts),encoding='utf-8')
print('Ch6 complete; index extracted')
