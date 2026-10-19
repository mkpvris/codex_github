from pathlib import Path
import re, json
from collections import Counter

base = Path(__file__).resolve().parents[1]
src = (base / 'original' / 'DeftfinArxiv2.tex').read_text(encoding='utf-8')
src = src[src.index('\\appendix'):src.index('\\begin{thebibliography}')]
out = (base / 'sections' / 'appendices.tex').read_text(encoding='utf-8')
report = {}
norm = lambda s: re.sub(r'\s+', '', s)
for cmd in ['label', 'ref', 'cite', 'includegraphics']:
    pattern = r'\\' + cmd + r'(?:\[[^\]]*\])?\{([^}]+)\}'
    a, b = [re.findall(pattern, t) for t in (src, out)]
    report[cmd] = {'source_count': len(a), 'translation_count': len(b), 'ordered_identical': a == b,
                   'missing': list((Counter(a)-Counter(b)).elements()), 'extra': list((Counter(b)-Counter(a)).elements())}
for cmd in ['footnote', 'caption', 'section', 'subsection']:
    pattern = r'\\' + cmd + r'(?:link)?\{'
    a, b = [len(re.findall(pattern, t)) for t in (src, out)]
    report[cmd] = {'source_count': a, 'translation_count': b, 'identical': a == b}
pat = r'\\(?:beq|bea|be)\b.*?\\(?:eeq|eea|ee)\b|\\begin\{(?:eqnarray|align|equation)\}.*?\\end\{(?:eqnarray|align|equation)\}'
a,b = [[norm(x) for x in re.findall(pat,t,re.S)] for t in (src,out)]
report['display_math'] = {'source_count':len(a), 'translation_count':len(b), 'ordered_identical':a==b,
                         'differences':[{'index':i, 'source':x, 'translation':y} for i,(x,y) in enumerate(zip(a,b)) if x!=y]}
a,b = [Counter(norm(x) for x in re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$',t,re.S)) for t in (src,out)]
report['inline_math'] = {'source_count':sum(a.values()), 'translation_count':sum(b.values()), 'multiset_identical':a==b,
                        'missing':list((a-b).elements()),'extra':list((b-a).elements())}
(base/'work'/'appendices_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
