from pathlib import Path
from collections import Counter
import re,json
root=Path(__file__).resolve().parent
ranges={1:(16,27),2:(28,129),3:(130,166),4:(167,184),5:(185,255),6:(256,304),7:(305,340),8:(341,370),9:(371,390)}
def source_refs(s):
    out=[]
    for m in re.finditer(r'\[((?:\s*\d+(?:\s*[–−-]\s*\d+)?\s*,?)+)([^\]]*)\]',s):
        if re.search(r'\b0\b',m[1]):continue # numerical intervals, not references
        if m[2].strip() and not re.match(r'^,?\s*(?:p\.|pp\.|Sect|Sec\.|Ch|Fig|Eq)',m[2].strip()):continue
        for part in m[1].split(','):
            q=re.fullmatch(r'\s*(\d+)\s*[–−-]\s*(\d+)\s*',part)
            nums=range(int(q[1]),int(q[2])+1) if q else [int(x) for x in re.findall(r'\d+',part)]
            out.extend(n for n in nums if 1<=n<=523)
    return Counter(out)
out=[]
for ch,(a,b) in ranges.items():
    src='\n'.join((root/'source'/f'page_{i:03}.txt').read_text(encoding='utf-8') for i in range(a,b+1))
    tgt='\n'.join(f.read_text(encoding='utf-8') for f in sorted((root/'chapters').glob(f'ch{ch:02}*.tex')))
    expected=source_refs(src);found=Counter()
    for m in re.finditer(r'\\cite(?:\[[^\]]*\])*\{([^}]+)\}',tgt):
        found.update(int(x) for x in re.findall(r'ref(\d+)',m[1]))
    missing=expected-found;extra=found-expected
    out.append({'chapter':ch,'source_citations':sum(expected.values()),'translated_citations':sum(found.values()),'possible_missing':dict(missing),'possible_extra':dict(extra)})
(root/'audit/citation_comparison.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
