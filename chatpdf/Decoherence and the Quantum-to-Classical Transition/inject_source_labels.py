from pathlib import Path
import re,json,sys
root=Path(__file__).resolve().parent
manual={1:'物理学において、よい実験',2:'確かに、量子論の先駆者',3:'逆説の第二の部分は',4:'基礎にある量子的領域から古典世界が',5:'このような相関はしばしば',6:'したがって、環境との相互作用',7:'この評価は誤りであることが',8:'その結果、物体のレベルで観測できる',9:'量子力学自体の内部からであった',10:'量子力学を実際に用いる多く',11:'デコヒーレンス研究の発展が一つの画期',12:'高まり続ける量子計算への関心'}
first=root/'chapters/ch01.tex';t=first.read_text(encoding='utf-8')
for n,phrase in manual.items():
    if f'{{srcpage:{n}}}' not in t:
        if phrase not in t:raise ValueError(f'Ch1 page {n} phrase absent')
        t=t.replace(phrase,f'\\hypertarget{{srcpage:{n}}}{{}}\\label{{srcpage:{n}}}'+phrase,1)
first.write_text(t,encoding='utf-8')
for f in sorted((root/'chapters').glob('*.tex')):
    if f.name.startswith(('ch05',)) and '--all' not in sys.argv:continue
    text=f.read_text(encoding='utf-8')
    def sub(m):
        n=m[1]
        if f'{{srcpage:{n}}}' in text:return m[0]
        return m[0]+f'\n\\hypertarget{{srcpage:{n}}}{{}}\\label{{srcpage:{n}}}'
    text=re.sub(r'^%\s*原文\s*p\.\s*(\d+)\b[^\n]*',sub,text,flags=re.M)
    f.write_text(text,encoding='utf-8')
seen=set()
for f in sorted((root/'chapters').glob('*.tex')):
    if f.name.startswith('ch05') and '--all' not in sys.argv:continue
    t=f.read_text(encoding='utf-8')
    def unique(m):
        n=m[1]
        if n in seen:return ''
        seen.add(n);return m[0]
    t=re.sub(r'\\hypertarget\{srcpage:(\d+)\}\{\}\\label\{srcpage:\1\}',unique,t)
    f.write_text(t,encoding='utf-8')
alltext='\n'.join(f.read_text(encoding='utf-8') for f in (root/'chapters').glob('*.tex'))
labels=re.findall(r'\\label\{srcpage:(\d+)\}',alltext)
needed={int(n) for n in re.findall(r'\\sourcepageref\{(\d+)\}',(root/'chapters/index.tex').read_text(encoding='utf-8'))}
result={'unique_labels':len(set(labels)),'missing_index_source_pages':sorted(needed-{int(n) for n in labels}),'duplicate_labels':sorted({n for n in labels if labels.count(n)>1})}
(root/'audit/source_label_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(result)
