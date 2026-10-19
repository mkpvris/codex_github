from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
bbl=ROOT/'pdf/1109.4192v2_jp.bbl'
text=bbl.read_text(encoding='utf-8')
(ROOT/'work/1109.4192v2_jp_ungrouped.bbl').write_text(text,encoding='utf-8')
groups=json.loads((ROOT/'work/bibliography_groups.json').read_text(encoding='utf-8'))
for g in groups:
 for key in g['members'][1:]:
  replacement=(' \n'+r'\makeatletter\immediate\write\@auxout{\string\bibcite{'+key+'}{'+str(g['number'])+r'}}\makeatother % Continuation of original reference ['+str(g['number'])+']\n')
  text=re.sub(r'\s*\\bibitem\{'+re.escape(key)+r'\}\s*',lambda m:replacement,text)
assert len(re.findall(r'\\bibitem\{',text))==56
bbl.write_text(text,encoding='utf-8')
print('Grouped BibTeX-generated entries into 56 original reference numbers.')
