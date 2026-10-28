from pathlib import Path
import re,json,collections
b=Path(__file__).resolve().parents[1]
def nums(x):
    out=[]
    for tok in x.split(','):
        tok=tok.strip()
        if not re.fullmatch(r'\d+(?:[–-]\d+)?',tok): continue
        ns=list(map(int,re.findall(r'\d+',tok)))
        if len(ns)==1:out.append(ns[0])
        else:out.extend(range(ns[0],ns[1]+1))
    return out
allqa={}
for ch,srcf,texfs in [('ch06','ch06_source.txt',['ch06.tex','ch06_b.tex','ch06_c.tex','ch06_d.tex','ch06_e.tex']),('ch08','ch08_source.txt',['ch08.tex']),('ch09','ch09_source.txt',['ch09.tex']),('appendix','appendix_source.txt',['appendix.tex'])]:
    src=(b/f'audit/{srcf}').read_text(encoding='utf-8')
    t='\n'.join((b/f'chapters/{f}').read_text(encoding='utf-8') for f in texfs)
    sc=[]
    for match in re.findall(r'\[([^\]]+)\]',src):
        if re.match(r'^\d',match):
            sc+=nums(re.split(r',\s*(?:p\.|pp\.|Sect\.|Chap\.)',match)[0])
    tc=[]
    for match in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}',t):
        tc+=list(map(int,re.findall(r'ref(\d+)',match)))
    unknown=[m for m in re.findall(r'[A-Za-z]{8,}(?: [A-Za-z]{3,}){4,}',t) if not any(s in m for s in ['Copyright','American','Springer','Reprinted','for','Ich','Der','Denn'])]
    allqa[ch]={'source_citation_set':sorted(set(sc)),'translated_citation_set':sorted(set(tc)),'missing_citation_numbers':sorted(set(sc)-set(tc)),'additional_citation_numbers':sorted(set(tc)-set(sc)),'missing_citation_multiset':dict(collections.Counter(sc)-collections.Counter(tc)),'additional_citation_multiset':dict(collections.Counter(tc)-collections.Counter(sc)),'citation_counts':[len(sc),len(tc)],'footnotes':t.count('\\footnote{'),'equation_tags':re.findall(r'\\tag\{([^}]+)\}',t),'english_prose_candidates':unknown}
(b/'audit/qa_assigned_sections.json').write_text(json.dumps(allqa,ensure_ascii=False,indent=2),encoding='utf-8')
for k,v in allqa.items():print(k,{x:v[x] for x in ['missing_citation_numbers','additional_citation_numbers','citation_counts','footnotes','english_prose_candidates']})
preamble=(b/'Schlosshauer_Decoherence_jp.tex').read_text(encoding='utf-8').split(r'\begin{document}')[0]
body=r'''\begin{document}
\setcounter{section}{5}
\input{chapters/ch06.tex}
\clearpage\setcounter{section}{7}
\input{chapters/ch08.tex}
\clearpage
\input{chapters/ch09.tex}
\clearpage
\input{chapters/appendix.tex}
\clearpage
\input{chapters/index.tex}
\end{document}
'''
(b/'audit/qa_assigned_sections.tex').write_text(preamble+body,encoding='utf-8')
