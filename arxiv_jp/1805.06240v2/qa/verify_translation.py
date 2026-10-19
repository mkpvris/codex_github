from pathlib import Path
from collections import Counter
import re, json, hashlib
from pypdf import PdfReader

root = Path(__file__).resolve().parents[1]
def read(p): return (root/p).read_text(encoding='utf-8')
def active(s):
    return re.sub(r'(?<!\\)%[^\n]*', '', s)
def norm(s): return re.sub(r'\s+', '', s)
def mathnorm(s):
    return norm(s.replace(r'\text{およびその微分}', r'\text{and its derivatives.}').replace(r'\quad\text{およびそれらの微分}', r'{\rm ~and~their~derivatives}'))
def math(s):
    return re.findall(r'\\begin\{(align\*?|equation\*?|gather\*?|multline\*?)\}(.*?)\\end\{\1\}', active(s), re.S)
def get_group(s, command):
    return re.findall(r'\\' + command + r'\{([^}]+)\}', active(s))
src = active(read('original/SSBofDspv2.tex'))
src = src[src.index('\\section{Introduction}'):src.index('\\bibliography{bib}')]
parts = ['parts/part12.tex','parts/part3.tex','parts/part4A.tex']
dst = '\n'.join(read(p) for p in parts)
sm, dm = math(src), math(dst)
mathdiff = []
for i, (a,b) in enumerate(zip(sm,dm),1):
    if mathnorm(a[1]) != mathnorm(b[1]) or a[0] != b[0]:
        mathdiff.append({'index':i,'source':a,'translation':b})
src_labels, dst_labels = get_group(src,'label'), get_group(dst,'label')
src_cites, dst_cites = get_group(src,'cite'), get_group(dst,'cite')
orig_aux = read('qa/original_build/SSBofDspv2.aux')
new_aux = read('pdf/1805.06240v2_jp.aux')
label_re = r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}'
ol, nl = dict(re.findall(label_re,orig_aux)), dict(re.findall(label_re,new_aux))
label_number_diff = {k:[v,nl.get(k)] for k,v in ol.items() if nl.get(k)!=v}
orig_bib_order = get_group(read('original/SSBofDspv2.bbl'),'bibitem')
new_bib_order = get_group(read('pdf/1805.06240v2_jp.bbl'),'bibitem')
bbl=read('pdf/1805.06240v2_jp.bbl')
expected_urls = re.findall(r'\\(?:href|url)\{([^}]+)\}',bbl)
pdf = PdfReader(root/'pdf/1805.06240v2_jp.pdf')
names = pdf.named_destinations
uris=[]; cite_links=[]; broken=[]; internal=[]
for pn,p in enumerate(pdf.pages,1):
    for ar in p.get('/Annots',[]):
        a=ar.get_object()
        if a.get('/Subtype')!='/Link': continue
        act=a.get('/A')
        if act:
            act=act.get_object()
            if act.get('/S')=='/URI':
                uris.append({'page':pn,'uri':str(act.get('/URI'))})
            if act.get('/S')=='/GoTo':
                d=act.get('/D'); internal.append({'page':pn,'destination':str(d)})
                if isinstance(d,str):
                    if d not in names: broken.append({'page':pn,'destination':d})
                    if d.startswith('cite.'):
                        citedest = names.get(d)
                        target_page = pdf.get_destination_page_number(citedest)+1 if citedest else None
                        cite_links.append({'page':pn,'destination':d,'target_page':target_page})
        d=a.get('/Dest')
        if isinstance(d,str) and d not in names: broken.append({'page':pn,'destination':d})
pdftext='\n'.join(p.extract_text() or '' for p in pdf.pages)
log=read('pdf/1805.06240v2_jp.log')
report = {
 'original_pages':len(PdfReader(root/'original/1805.06240v2.pdf').pages),
 'translation_pages':len(pdf.pages),
 'display_math_blocks':{'original':len(sm),'translation':len(dm),'mathematical_differences':mathdiff,'translated_prose_only':['and its derivatives. → およびその微分','and their derivatives → およびそれらの微分']},
 'labels':{'original':len(src_labels),'translation':len(dst_labels),'same_multiset':Counter(src_labels)==Counter(dst_labels),'number_differences':label_number_diff},
 'citations':{'original_occurrences':len(src_cites),'translation_occurrences':len(dst_cites),'same_sequence':src_cites==dst_cites,'same_multiset':Counter(src_cites)==Counter(dst_cites),'bibliography_order_matches':orig_bib_order==new_bib_order,'reference_count':len(new_bib_order)},
 'footnotes':{'original':len(re.findall(r'\\footnote\{',src)),'translation':len(re.findall(r'\\footnote\{',dst))},
 'figures':{'original':len(re.findall(r'\\begin\{figure\}',src)),'translation':len(re.findall(r'\\begin\{figure\}',dst))},
 'links':{'total_internal':len(internal),'citation_links':len(cite_links),'distinct_citation_targets':len(set(x['destination'] for x in cite_links)),'broken_internal':broken,'uris':uris,'citation_destinations':cite_links,'versioned_title_link':any(x['page']==1 and x['uri']=='https://arxiv.org/pdf/1805.06240v2' for x in uris),'expected_bibliography_urls':len(set(expected_urls)),'missing_bibliography_urls':[u for u in sorted(set(expected_urls)) if u not in {x['uri'] for x in uris}]},
 'log':{'undefined_references':bool(re.search(r'(undefined references|Citation .* undefined|Reference .* undefined)',log)),'missing_characters':bool(re.search(r'Missing character:',log)),'overfull':re.findall(r'Overfull \\[hv]box[^\n]*',log)},
 'template_bst_unchanged':hashlib.sha256((root/'utphys.bst').read_bytes()).hexdigest()==hashlib.sha256(Path('C:/codex/template/utphys.bst').read_bytes()).hexdigest(),
}
(root/'qa/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'qa/final_text.txt').write_text(pdftext,encoding='utf-8')
brief={k:v for k,v in report.items() if k!='links'}
brief['links']={k:v for k,v in report['links'].items() if k not in ['uris','citation_destinations']}
print(json.dumps(brief,ensure_ascii=False,indent=2))
