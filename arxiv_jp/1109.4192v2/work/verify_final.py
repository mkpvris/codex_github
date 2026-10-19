from pathlib import Path
import json,re,hashlib,collections,sys
from pypdf import PdfReader
import pdfplumber
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
pdf=ROOT/'pdf/1109.4192v2_jp.pdf'
reader=PdfReader(pdf);destinations=reader.named_destinations
groups=json.loads((ROOT/'work/bibliography_groups.json').read_text(encoding='utf-8'))
links=[];missing=[];citation_links=[];uris=[]
for pn,page in enumerate(reader.pages,1):
 for ref in page.get('/Annots',[]):
  a=ref.get_object()
  if a.get('/Subtype')!='/Link':continue
  action=a.get('/A',{});dest=a.get('/Dest') or action.get('/D')
  if action.get('/S')=='/URI':uris.append({'page':pn,'url':str(action['/URI'])})
  elif dest is not None:
   links.append({'page':pn,'destination':str(dest)})
   if isinstance(dest,str) and dest not in destinations:missing.append({'page':pn,'destination':dest})
   if isinstance(dest,str) and dest.startswith('cite.'):citation_links.append({'page':pn,'destination':dest})
results=[]
with pdfplumber.open(pdf) as doc:
 for g in groups:
  dest=destinations['cite.'+g['key']];p=reader.get_destination_page_number(dest)
  top=float(doc.pages[p].height)-float(dest.top)
  labels=[w for w in doc.pages[p].extract_words() if w['text']=='['+str(g['number'])+']' and 60<=w['x0']<=100]
  offsets=[w['top']-top for w in labels]
  good=any(-4<=d<=27 for d in offsets)
  results.append({'number':g['number'],'key':g['key'],'page':p+1,'correct_printed_number_at_destination':good,'offsets':offsets})
 def aux_labels(path):return dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',path.read_text(encoding='utf-8')))
 original_labels=aux_labels(ROOT/'work/original_reference/DeftfinArxiv2.aux');translated_labels=aux_labels(ROOT/'pdf/1109.4192v2_jp.aux')
 label_diff=[(k,v,translated_labels.get(k)) for k,v in original_labels.items() if k not in ['LastBibItem','LastPage'] and translated_labels.get(k)!=v]
 aux=(ROOT/'pdf/1109.4192v2_jp.aux').read_text(encoding='utf-8')
 refs=dict(re.findall(r'\\bibcite\{([^}]+)\}\{([^}]+)\}',aux))
 ref_diff=[(g['key'],g['number'],refs.get(g['key'])) for g in groups if str(g['number'])!=refs.get(g['key'])]
 bbl=(ROOT/'pdf/1109.4192v2_jp.bbl').read_text(encoding='utf-8')
 expected=set(re.findall(r'\\(?:href|url)\{([^}]+)\}',bbl))
 actual={u['url'] for u in uris}
 title_url='https://arxiv.org/pdf/1109.4192v2'
 checks={'pages':len(reader.pages),'internal_link_count':len(links),'citation_link_count':len(citation_links),'external_link_count':len(uris),'dangling_internal_links':missing,'reference_destinations':results,'all_reference_destinations_correct':all(r['correct_printed_number_at_destination'] for r in results),'label_number_mismatches':label_diff,'reference_number_mismatches':ref_diff,'expected_external_urls':len(expected),'missing_external_urls':sorted(expected-actual),'title_v2_pdf_link_present':any(x['page']==1 and x['url']==title_url for x in uris),'input_matches_title_link_pdf':hashlib.sha256((ROOT/'original/1109.4192v2.pdf').read_bytes()).hexdigest()==hashlib.sha256((ROOT/'work/arxiv_1109.4192v2_verification.pdf').read_bytes()).hexdigest(),'bibliography_pages':sorted(set(r['page'] for r in results)),'external_links':uris,'all_page_text_present':all(bool(p.extract_text()) for p in doc.pages)}
 (ROOT/'work/pdf_link_and_numbering_check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in checks.items() if k not in ['reference_destinations','external_links']},ensure_ascii=False,indent=2))
 assert not missing and not label_diff and not ref_diff and not(expected-actual)
 assert checks['all_reference_destinations_correct'] and checks['title_v2_pdf_link_present'] and checks['input_matches_title_link_pdf'] and checks['all_page_text_present']
 source=(ROOT/'original/DeftfinArxiv2.tex').read_text(encoding='utf-8'); source=source[source.index(r'\section{'):source.index(r'\begin{thebibliography}')]
 target='\n'.join((ROOT/'sections'/f).read_text(encoding='utf-8') for f in ['part1.tex','part2.tex','appendices.tex'])
 structural={}
 for name,pat in {'labels':r'\\label\{([^}]+)\}','citations':r'\\cite\{([^}]+)\}','refs':r'\\(?:eq)?ref\{([^}]+)\}','footnotes':r'\\footnote\{','figures':r'\\includegraphics','captions':r'\\caption\{','sections':r'\\section(?:link)?\{','subsections':r'\\subsection(?:link)?\{'}.items():
  a=re.findall(pat,source);b=re.findall(pat,target)
  if name in ['sections','subsections']:a=['heading']*len(a);b=['heading']*len(b)
  structural[name]={'original':len(a),'translation':len(b),'matched':collections.Counter(a)==collections.Counter(b)}
 assert all(c['matched'] for c in structural.values())
 (ROOT/'work/structural_check.json').write_text(json.dumps(structural,indent=2),encoding='utf-8')
 baseline=json.loads((ROOT/'work/template_hashes.json').read_text(encoding='utf-8'));current={str(p.relative_to(Path('C:/codex/template'))):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('C:/codex/template').rglob('*') if p.is_file()}
 assert baseline==current
 assert hashlib.sha256((ROOT/'utphys.bst').read_bytes()).hexdigest()==hashlib.sha256(Path('C:/codex/template/utphys.bst').read_bytes()).hexdigest()
 print('All structural counts and original template hashes match.')
