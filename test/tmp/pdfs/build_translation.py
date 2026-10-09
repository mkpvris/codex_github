import json,re,collections,shutil
from pathlib import Path
root=Path(__file__).parent
d=json.loads((root/'translation_data.json').read_text(encoding='utf-8'))
t={}
for f in sorted((root/'translations').glob('*.txt')):
 s=f.read_text(encoding='utf-8')
 for m in re.finditer(r'^@@(\d+)\n([\s\S]*?)(?=^@@\d+\n|\Z)',s,re.M):
  i=int(m[1]);assert i not in t,(i,f);t[i]=m[2].strip()
for i,txt in t.items():
 original=d['segments'][i]['text']
 assert collections.Counter(re.findall(r'⟦\d+⟧',txt))==collections.Counter(re.findall(r'⟦\d+⟧',original)),('markers',i)
 assert txt.count('{')-txt.count('}')==original.count('{')-original.count('}'),('braces',i)
out=[d['preamble'],r'\begin{document}']
for token in d['tokens']:
 if token['kind']=='raw':
  txt=token['text']
  if re.match(r'\\begin\{(?:equation|align|eqnarray|gather|multline)|\\\[|\\be\b',txt):txt=re.sub(r'\n\s*\n','\n',txt)
  out.append(txt);continue
 seg=d['segments'][token['id']]
 txt=t.get(seg['id'],seg['text'])
 for j,x in enumerate(seg['protected']):txt=txt.replace('⟦'+str(j)+'⟧',x)
 out.append('\n'+txt+'\n')
dest=root/'source/2607.14351v1-ja.tex'
assembled=''.join(out)
for original,translated in json.loads((root/'label_translations.json').read_text(encoding='utf-8')).items():
 assembled=assembled.replace(original,translated)
assembled=assembled.replace(r'\begin{document}',r'\hypersetup{pdftitle={開放系と宇宙論の講義（日本語訳）},pdfauthor={Enrico Pajer},pdfsubject={Lectures on Open Systems and Cosmology / Japanese translation}}'+'\n'+r'\begin{document}',1)
dest.write_text(assembled,encoding='utf-8')
print('translated:',len(t),'of',len(d['segments']))
print('saved',dest)
