from pathlib import Path
import re,json,collections
b=Path(__file__).resolve().parents[1]
src=(b/'audit/index_source_columns.txt').read_text(encoding='utf-8')
rows=(b/'audit/index_translation.tsv').read_text(encoding='utf-8').splitlines()
tex=['\\sectionlink*{索引}','\\begingroup\\small','\\setlength{\\parindent}{0pt}','\\setlength{\\parskip}{1pt}','\\newcommand{\\idxentry}[2]{\\par\\noindent\\hangindent=1em\\hangafter=1\\textbf{#1}\\quad#2\\par}','\\newcommand{\\idxsub}[2]{\\par\\noindent\\hangindent=2em\\hangafter=1\\hspace*{1em}#1\\quad#2\\par}','\\begin{multicols}{2}','\\raggedcolumns']
refs=[]
for row in rows:
    if not row.strip():continue
    term,pages=row.split('|',1)
    if pages.startswith('→'):
        val=pages.replace('→',r'$\to$',1)
    else:
        refs+=re.findall(r'\d+(?:–\d+)?',pages)
        val=re.sub(r'\d+',lambda m:r'\sourcepageref{'+m[0]+'}',pages).replace('–','--')
    tex.append(('\\idxsub' if term.startswith(' ') else '\\idxentry')+'{'+term.strip()+'}{'+val+'}')
tex+=['\\end{multicols}','\\endgroup','']
(b/'chapters/index.tex').write_text('\n'.join(tex),encoding='utf-8')
orig=[]
for line in src.splitlines():
    if line.startswith('==='):continue
    m=re.search(r'(?:^|,\s*)(\d+(?:–\d+)?(?:,\s*\d+(?:–\d+)?)*)[,]?\s*$',line)
    if m:orig+=re.findall(r'\d+(?:–\d+)?',m[1])
a=collections.Counter(orig);c=collections.Counter(refs)
print('rows',len(rows),'references',len(refs),'source refs',len(orig))
print('missing',a-c,'extra',c-a)
audit={'status':'complete','source_printed_pages':[409,416],'source_physical_pages':[420,427],'entry_and_subentry_count':len(rows),'source_reference_count':len(orig),'translated_reference_count':len(refs),'missing_reference_multiset':dict(a-c),'extra_reference_multiset':dict(c-a),'reference_generation':'Each source page number uses sourcepageref macro supplied by root; numeric ranges preserve original endpoints.','order':'Original English alphabetical order and subentry hierarchy preserved, entries translated to Japanese; names retain English spelling.','source_extraction':'pdfplumber cropped each original page into left and right columns before extracting.'}
(b/'audit/index_coverage.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
