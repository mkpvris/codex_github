from pathlib import Path
import json, re, hashlib
from collections import Counter

base=Path(__file__).resolve().parents[1]
report=json.loads((base/'work/bibliography_report.json').read_text(encoding='utf-8'))
groups=json.loads((base/'work/bibliography_groups.json').read_text(encoding='utf-8'))
source=(base/'original/DeftfinArxiv2.tex').read_text(encoding='utf-8')
source=source[source.index('\\begin{thebibliography}'):source.index('\\end{thebibliography}')]
bib=(base/'ref.bib').read_text(encoding='utf-8')

def parse_bib(text):
    result={}
    for match in re.finditer(r'(?m)^\s*@(\w+)\{([^,]+),',text):
        fields={}; pos=match.end()
        while pos<len(text):
            while pos<len(text) and text[pos] in ' \t\r\n,':pos+=1
            if pos>=len(text) or text[pos]=='}':break
            key=re.match(r'([\w]+)\s*=\s*',text[pos:])
            if not key:raise ValueError(text[pos:pos+100])
            name=key[1].lower();pos+=key.end()
            start=pos
            if text[pos]=='{':
                depth=1;pos+=1
                while pos<len(text) and depth:
                    if text[pos]=='{' and text[pos-1]!='\\':depth+=1
                    if text[pos]=='}' and text[pos-1]!='\\':depth-=1
                    pos+=1
                value=text[start+1:pos-1]
            elif text[pos]=='"':
                pos+=1; depth=0
                while pos<len(text):
                    if text[pos]=='{' and text[pos-1]!='\\':depth+=1
                    if text[pos]=='}' and text[pos-1]!='\\':depth-=1
                    if text[pos]=='"' and text[pos-1]!='\\' and depth==0:break
                    pos+=1
                value=text[start+1:pos];pos+=1
            else:
                while pos<len(text) and text[pos] not in ',}\r\n':pos+=1
                value=text[start:pos]
            fields[name]=value
        result[match[2]]={'type':match[1].lower(),'fields':fields}
    return result

entries=parse_bib(bib)
source_keys=re.findall(r'\\bibitem(?:\[[^]]+\])?\{([^}]+)\}',source)
out={'counts':{'original_numbers':len(source_keys),'records':len(report['records']),'bib_entries':len(entries)},
     'original_number_order_matches_groups': source_keys==[g['key'] for g in groups],
     'bib_key_order_matches_records': list(entries)==[r['citation_key'] for r in report['records']],
     'source_counts':dict(Counter(r['source'] for r in report['records'])),
     'raw_hash_mismatches':[], 'removed_fields':[], 'field_changes':[], 'arxiv_mismatches':[]}
normalize=lambda x:re.sub(r'\s+','',x).replace('–','--')
for r in report['records']:
    raw_path=base/r['raw_file'];raw=raw_path.read_text(encoding='utf-8')
    if hashlib.sha256(raw_path.read_bytes()).hexdigest()!=r['raw_sha256']:out['raw_hash_mismatches'].append(r['citation_key'])
    raw_entry=list(parse_bib(raw).values())[0]
    current=entries[r['citation_key']]
    for k,v in raw_entry['fields'].items():
        if k not in current['fields']:out['removed_fields'].append([r['citation_key'],k])
        elif normalize(v)!=normalize(current['fields'][k]):out['field_changes'].append([r['citation_key'],k,v,current['fields'][k]])
    if r['match'].get('arxiv'):
        arxiv=r['match']['arxiv']
        if arxiv not in r['original_entry'] or current['fields'].get('eprint')!=arxiv:out['arxiv_mismatches'].append(r['citation_key'])
original_arxivs=set(re.findall(r'(?:hep-(?:ph|th)|gr-qc|astro-ph)/\d{7}|(?<!\d)\d{4}\.\d{4}(?!\d)',source))
final_arxivs={e['fields']['eprint'] for e in entries.values() if 'eprint' in e['fields']}
out['arxiv_coverage']={'original_count':len(original_arxivs),'final_count':len(final_arxivs),
                       'missing':sorted(original_arxivs-final_arxivs),'extra':sorted(final_arxivs-original_arxivs)}
out['multiwork_groups']=[g for g in groups if len(g['members'])>1]
out['misc_entries']=[k for k,v in entries.items() if v['type']=='misc']
bbl=(base/'pdf/1109.4192v2_jp.bbl').read_text(encoding='utf-8')
aux=(base/'pdf/1109.4192v2_jp.aux').read_text(encoding='utf-8')
out['bbl_original_number_order']=re.findall(r'\\bibitem\{([^}]+)\}',bbl)==source_keys
out['aux_original_number_order']=re.findall(r'\\bibcite\{([^}]+)\}\{([^}]+)\}',aux)==[(k,str(i+1)) for i,k in enumerate(source_keys)]
ungrouped=(base/'work/1109.4192v2_jp_ungrouped.bbl').read_text(encoding='utf-8')
norm_bbl=lambda z:re.sub(r'\s+','',re.sub(r'\\bibitem\{[^}]+\}|\\par\\smallskip % Continuation of original reference \[\d+\]','',z))
out['bbl_content_preserved_after_grouping']=norm_bbl(ungrouped)==norm_bbl(bbl)
(base/'work/bibliography_independent_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True,indent=2))
