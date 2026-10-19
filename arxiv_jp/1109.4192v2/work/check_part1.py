from pathlib import Path
import re,json
from collections import Counter
b=Path(__file__).resolve().parents[1]
o='\n'.join((b/'original/DeftfinArxiv2.tex').read_text(encoding='utf-8').splitlines()[61:705])
t=(b/'sections/part1.tex').read_text(encoding='utf-8')
r={}
for name,pat in [('labels',r'\\label\{([^}]+)\}'),('refs',r'\\ref\{([^}]+)\}'),('cites',r'\\cite\{([^}]+)\}')]:
    a=re.findall(pat,o);z=re.findall(pat,t)
    r[name]={'original':len(a),'translation':len(z),'same_sequence':a==z,'missing':list((Counter(a)-Counter(z)).elements()),'added':list((Counter(z)-Counter(a)).elements())}
for name,pat in [('footnotes',r'\\footnote\{'),('equation_begins',r'\\(?:beq|bea|be)\b|\\begin\{(?:equation|eqnarray|align)\}')]:
    r[name]={'original':len(re.findall(pat,o)),'translation':len(re.findall(pat,t))}
norm=lambda s:re.sub(r'\s+','',s)
a=Counter(map(norm,re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$',o,re.S)))
z=Counter(map(norm,re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$',t,re.S)))
r['inline_math']={'original':sum(a.values()),'translation':sum(z.values()),'missing':list((a-z).elements()),'added':list((z-a).elements())}
pat=r'\\beq\b(.*?)\\eeq\b|\\bea\b(.*?)\\eea\b|\\be\b(.*?)\\ee\b|\\begin\{(equation|eqnarray|align)\}(.*?)\\end\{\4\}'
extract=lambda s:[norm(next(x for x in m if x and x not in ('equation','eqnarray','align'))) for m in re.findall(pat,s,re.S)]
a=extract(o);z=extract(t)
r['display_math']={'original':len(a),'translation':len(z),'identical':a==z}
for i,(aa,zz) in enumerate(zip(a,z)):
    if aa!=zz:r.setdefault('math_differences',[]).append({'i':i,'original':aa,'translation':zz})
(b/'work/part1_checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(r,ensure_ascii=False,indent=2))
