import re,json
from pathlib import Path
root=Path(__file__).parent
s=(root/'source/Open_Quantum_System_lecture_notes.tex').read_text(encoding='utf-8',errors='replace')
s=re.sub(r'(?<!\\)%[^\n]*','',s)
pre,body=s.split(r'\begin{document}',1)
pre=pre.replace(r'\newtheorem{definition}{Definition}',r'\newtheorem{definition}{定義}')
pre=pre.replace(r'\usepackage{hyperref}',r'\usepackage[unicode]{hyperref}')
ja=r'''
\usepackage{luatexja-fontspec}
\setmainjfont[Path=C:/Windows/Fonts/,BoldFont=yumindb.ttf]{yumin.ttf}
\setsansjfont[Path=C:/Windows/Fonts/,BoldFont=YuGothB.ttc]{YuGothM.ttc}
\renewcommand{\contentsname}{目次}
\renewcommand{\refname}{参考文献}
\renewcommand{\figurename}{図}
\renewcommand{\tablename}{表}
\setlength{\emergencystretch}{2em}
'''
pre=pre.replace(r'\usepackage[margin=1in]{geometry}',ja+'\n'+r'\usepackage[margin=1in]{geometry}')
display=r'\\begin\{(equation\*?|align\*?|eqnarray\*?|gather\*?|multline\*?|tikzpicture)\}[\s\S]*?\\end\{\1\}|\\\[[\s\S]*?\\\]|\\be\b[\s\S]*?\\ee\b'
parts=[];pos=0
for m in re.finditer(display,body):
 parts.append(('prose',body[pos:m.start()]));parts.append(('math',m.group()));pos=m.end()
parts.append(('prose',body[pos:]))
segments=[];tokens=[]
for typ,txt in parts:
 if typ=='math': tokens.append({'kind':'raw','text':txt});continue
 for chunk in re.split(r'(\n\s*\n)',txt):
  if not chunk:continue
  protected=[]
  def protect(m):
   protected.append(m.group());return '⟦'+str(len(protected)-1)+'⟧'
  # Keep mathematical objects, citations and targets byte-for-byte.
  masked=re.sub(r'(?<!\\)\$[^$]*?(?<!\\)\$|\\\([\s\S]*?\\\)|\\(?:label|eqref|ref|cite|includegraphics|bibliography|bibliographystyle|url)\*?(?:\[[^\]]*\])?\{[^{}]*\}|\\href\{[^{}]*\}',protect,chunk)
  visible=re.sub(r'\\[A-Za-z]+\*?|[{}\[\]\d]|⟦\d+⟧','',masked)
  if re.search(r'[A-Za-z]{2}',visible):
   idx=len(segments);segments.append({'id':idx,'text':masked,'protected':protected,'original':chunk});tokens.append({'kind':'segment','id':idx})
  else:tokens.append({'kind':'raw','text':chunk})
data={'preamble':pre,'tokens':tokens,'segments':segments}
(root/'translation_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'translations').mkdir(exist_ok=True)
print('segments',len(segments),'masked_chars',sum(len(x['text']) for x in segments),'words',sum(len(x['text'].split()) for x in segments))
for x in segments[:45]:print(str(x['id'])+' | '+x['text'].strip())
