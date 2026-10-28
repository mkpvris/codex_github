from pathlib import Path
import re,json,collections
b=Path(__file__).resolve().parents[1]
src=(b/'audit/ch05_4_source.txt').read_text(encoding='utf-8').split('5.4 Spin-Environment Models',1)[1].split('\n5.5 Summary\n',1)[0]
t=(b/'chapters/ch05_08.tex').read_text(encoding='utf-8')
def nums(x):
    out=[]
    for tok in x.split(','):
        tok=tok.strip()
        if not re.fullmatch(r'\d+(?:[–-]\d+)?',tok):continue
        ns=list(map(int,re.findall(r'\d+',tok)))
        out+=ns if len(ns)==1 else list(range(ns[0],ns[1]+1))
    return out
sc=[]
for m in re.findall(r'\[([^\]]+)\]',src):
    if re.match(r'^\d',m):sc+=nums(re.split(r',\s*(?:p\.|pp\.|Sect\.|Chap\.)',m)[0])
tc=[]
for m in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}',t):tc+=list(map(int,re.findall(r'ref(\d+)',m)))
keys=re.findall(r'\\chfiveeq\{([^}]+)\}',t)
eqs=json.loads((b/'audit/ch05_equations.json').read_text(encoding='utf-8'))
sourcekeys=[q['key'] for q in eqs if any(150<=int(re.search(r'5\.(\d+)',n)[1])<=201 for n in q['numbers'])]
if '186' not in sourcekeys:sourcekeys.append('186')
qa={'status':'complete','scope':'Entire5.4 startheading p222 through5.4.3 finalparagraph p237 before5.5','file':'chapters/ch05_08.tex','printed_pages':[222,237],'source_page_markers':re.findall(r'% 原文 p\.(\d+)',t),'equation_crop_keys':keys,'missing_equation_crop_keys':sorted(set(sourcekeys)-set(keys)),'extra_equation_crop_keys':sorted(set(keys)-set(sourcekeys)),'footnotes':t.count('\\footnote{'),'citation_counts':[len(sc),len(tc)],'missing_citation_multiset':dict(collections.Counter(sc)-collections.Counter(tc)),'additional_citation_multiset':dict(collections.Counter(tc)-collections.Counter(sc)),'caption':'Figure5.8 translated; owner agent supplies vector crop.','uncertainties':[]}
(b/'audit/ch05_4_coverage.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(qa,ensure_ascii=False))
