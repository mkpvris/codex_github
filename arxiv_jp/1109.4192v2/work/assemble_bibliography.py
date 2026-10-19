import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CACHE=ROOT/'work/bibliography_cache'
rows=json.loads((ROOT/'work/bibliography_matches.json').read_text(encoding='utf-8'))
def add_fields(s,fields):
 return s.rstrip().removesuffix('}').rstrip().rstrip(',')+',\n'+',\n'.join('    '+k+' = {'+v+'}' for k,v in fields.items())+'\n}\n'
def set_quoted_field(s,k,value):
 return re.sub(r'(?m)(\s*'+k+r'\s*=\s*)"[^"\n]*"',lambda m:m[1]+'"'+value+'"',s,count=1)
sources={
 'peskin':('INSPIRE','peskin_1.bib','https://inspirehep.net/api/literature/407703?format=bibtex'),
 'calzetta':('INSPIRE','calzetta_1.bib','https://inspirehep.net/api/literature/1384872?format=bibtex'),
 'hydro':('INSPIRE','hydro_1.bib','https://inspirehep.net/api/literature/1204617?format=bibtex'),
 'weinberg':('INSPIRE','weinberg_1.bib','https://inspirehep.net/api/literature/794379?format=bibtex'),
 'weiss':('Crossref','weiss_1.bib','https://api.crossref.org/works/10.1142/6738/transform/application/x-bibtex'),
 'Zhang':('Crossref','Zhang_1.bib','https://api.crossref.org/works/10.1103/PhysRevE.47.3745/transform/application/x-bibtex'),
 'forster':('CiNii Books','forster_1975.bib','https://cir.nii.ac.jp/crid/1971712334715945767.bib'),
 'Fetter':('Original bibliography; checked against library catalogues','Fetter_original.bib','https://library.kaist.ac.kr/search/ctlgSearch/posesn/view.do?bibctrlno=11584&ty=B'),
}
(CACHE/'Fetter_original.bib').write_text(r'''@book{Fetter:1971,
    author = {Fetter, Alexander L. and Walecka, John Dirk},
    title = {Quantum Theory of Many-Particle Systems},
    publisher = {McGraw-Hill},
    address = {San Francisco},
    year = {1971},
    url = {https://library.kaist.ac.kr/search/ctlgSearch/posesn/view.do?bibctrlno=11584&ty=B}
}
''',encoding='utf-8')
allkeys=[]; groups=[]; report=[];out=['% arXiv:1109.4192v2 bibliography. Official exports retained in work/bibliography_cache.\n% Citation-key changes and documented supplements only; see work/bibliography_report.json.\n']
for row in rows:
 key=row['key']; matches=row['matches']
 if not matches:
  kind,file,url=sources[key];matches=[{'file':file,'bibtex_url':url,'source':kind}]
 group=[]
 for i,m in enumerate(matches):
  cite=key if i==0 else key+'__'+str(i+1);group.append(cite);allkeys.append(cite)
  raw=(CACHE/m['file']).read_text(encoding='utf-8'); kind=m.get('source','INSPIRE')
  oldkey=re.search(r'@\w+\s*\{\s*([^,]+)',raw)[1]
  bib=re.sub(r'(@\w+\s*\{\s*)[^,]+',lambda x:x[1]+cite,raw,count=1)
  changes=[]
  if oldkey!=cite:changes.append('Citation key: '+oldkey+' -> '+cite)
  if kind=='Crossref':
   bib=re.sub(r'\bmonth=([A-Za-z]+)',r'month={\1}',bib).replace('–','--')
   changes.append('TeX-safe quoted month and page-range hyphen normalization; all fields retained.')
  if key=='calzetta':
   bib=set_quoted_field(bib,'publisher','Cambridge University Press')
   bib=set_quoted_field(bib,'year','2008')
   bib=add_fields(bib,{'note':'First edition cited in the original paper; the DOI links to the Cambridge Open Access reissue'})
   changes.append('Corrected INSPIRE export publisher Oxford University Press and year 2009 to Cambridge University Press, 2008 using the original and publisher front matter. DOI and all ISBN values retained. Evidence: https://assets.cambridge.org/97805216/41685/frontmatter/9780521641685_frontmatter.pdf')
  if key=='hydro':
   bib=add_fields(bib,{'note':r'原文では同著者による「Dissipative effects in the Effective Field Theory for hydrodynamics」、執筆中として引用。ここには対応する後年の公刊情報を記載'})
   changes.append('Original in-progress title retained in a note; full author quartet and subject match the later published work 1211.6461.')
  if key=='Zhang':
   changes.append('Original journal Phys. Rev. D is a typo. Publisher confirms Phys. Rev. E 47, 3745 (1993). Title and author match. https://journals.aps.org/pre/abstract/10.1103/PhysRevE.47.3745')
  if key=='forster':
   bib=add_fields(bib,{'note':'原文の出版社表記は Perseus Books。1975年初版の書誌を採用'})
   changes.append('Exact 1975 edition from CiNii Books; original publisher Perseus Books noted; rejected Crossref 2018 reissue.')
  if key=='weinberg':
   bib=add_fields(bib,{'publisher':'Oxford University Press','url':'https://inspirehep.net/literature/794379'})
   changes.append('Publisher supplemented from original bibliography and INSPIRE pubinfo_freetext; record URL added.')
  if key=='weiss':
   bib=add_fields(bib,{'edition':'3','series':'Series in Modern Condensed Matter Physics','volume':'13'})
   changes.append('2008 third edition verified by DOI and Crossref; rejected INSPIRE 2021 fifth edition. Series and volume supplemented from publisher data.')
  if key=='memory':
   bib=add_fields(bib,{'note':'一例として本論文およびその参考文献を参照（原文の注記）'})
  if key=='eftrev' and i==0:
   bib=add_fields(bib,{'note':'レビューとして参照（原文の注記）'})
  out.append('\n% Original reference ['+str(row['number'])+'] '+m['bibtex_url']+'\n'+bib.strip()+'\n')
  report.append({'original_number':row['number'],'original_key':key,'citation_key':cite,'official_key':oldkey,'source':kind,'url':m['bibtex_url'],'raw_file':'work/bibliography_cache/'+m['file'],'raw_sha256':hashlib.sha256((CACHE/m['file']).read_bytes()).hexdigest(),'original_entry':row['original'],'match':m,'adjustments':changes})
 groups.append({'number':row['number'],'key':key,'members':group})
(ROOT/'ref.bib').write_text(''.join(out),encoding='utf-8')
(ROOT/'ordered_keys.tex').write_text('% Establish original reference order, including grouped works.\n\\nocite{'+',\n'.join(allkeys)+'}\n',encoding='utf-8')
(ROOT/'work/bibliography_groups.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'reference_numbers':len(groups),'works':len(report),'source_counts':{s:sum(r['source']==s for r in report) for s in sorted(set(r['source'] for r in report))},'official_export_unretrieved':['[39] Fetter and Walecka (1971): no matching INSPIRE record found; complete original @book transcribed and library catalogue checked.'],'numbering':'utphys formats every work via BibTeX; group_bibliography.py joins continuation items under the original reference number without changing formatted entry text.','records':report}
(ROOT/'work/bibliography_report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='records'},ensure_ascii=True,indent=2))
