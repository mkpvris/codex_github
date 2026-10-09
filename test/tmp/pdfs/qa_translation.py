import re,json,collections
from pathlib import Path
root=Path(__file__).parent
d=json.loads((root/'translation_data.json').read_text(encoding='utf-8'))
t={}
for f in sorted((root/'translations').glob('*.txt')):
    s=f.read_text(encoding='utf-8')
    s=s.replace('Gauss','ガウス').replace('ユニタリー','ユニタリ').replace('地平面','地平線')
    f.write_text(s,encoding='utf-8')
    t.update({int(m[1]):m[2].strip() for m in re.finditer(r'^@@(\d+)\n([\s\S]*?)(?=^@@\d+\n|\Z)',s,re.M)})
orig=(root/'source/Open_Quantum_System_lecture_notes.tex').read_text(encoding='utf-8',errors='replace')
orig=re.sub(r'(?<!\\)%[^\n]*','',orig).split(r'\begin{document}',1)[1]
labels=json.loads((root/'label_translations.json').read_text(encoding='utf-8'))
for original,translated in labels.items():orig=orig.replace(original,translated)
dst=(root/'source/2607.14351v1-ja.tex').read_text(encoding='utf-8').split(r'\begin{document}',1)[1]
patterns={
    'labels':r'\\label\{[^}]+\}',
    'citations':r'\\cite(?:\[[^\]]*\])?\{[^}]+\}',
    'references':r'\\(?:ref|eqref)\{[^}]+\}',
    'figures':r'\\includegraphics(?:\[[^\]]*\])?\{[^}]+\}',
    'equation_environments':r'\\(?:begin|end)\{(?:equation|align|eqnarray|gather|multline)\*?\}|\\(?:be|ee)\b',
    'inline_math':r'(?<!\\)\$[^$]*?(?<!\\)\$|\\\([\s\S]*?\\\)',
}
results={}
for name,pattern in patterns.items():
    a=collections.Counter(re.findall(pattern,orig));b=collections.Counter(re.findall(pattern,dst))
    results[name]={'original':sum(a.values()),'translated':sum(b.values()),'match':a==b}
    if a!=b:print(name,'removed',list((a-b).items())[:8],'added',list((b-a).items())[:8])
math=[x['text'] for x in d['tokens'] if x['kind']=='raw' and re.match(r'\\begin\{(?:equation|align|eqnarray|gather|multline)|\\\[|\\be\b',x['text'])]
for original,translated in labels.items():math=[m.replace(original,translated) for m in math]
norm=lambda x:re.sub(r'\s+','',x)
normalized=norm(dst)
results['display_math']={'count':len(math),'all_present':all(norm(m) in normalized for m in math)}
results['translated_segments']=len(t)
results['untranslated_segments']=[{'id':s['id'],'text':s['text'].strip()} for s in d['segments'] if s['id'] not in t]
results['unreplaced_markers']=bool(re.search(r'⟦\d+⟧',dst))
(root/'qa-structure.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in results.items() if k!='untranslated_segments'},ensure_ascii=False,indent=2))
