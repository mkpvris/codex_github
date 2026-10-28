from pathlib import Path
import re, argparse,json
parser=argparse.ArgumentParser();parser.add_argument('--exclude',default='');args=parser.parse_args()
excluded={int(n) for n in args.exclude.split(',') if n}
root=Path(__file__).resolve().parent
config=json.loads((root/'project_config.json').read_text(encoding='utf-8'))
template=(root/'template_copy/template.tex').read_text(encoding='utf-8')
preamble=template.split('\\title{')[0]
preamble+=r'''
% Original template retained. Extensions needed for book hierarchy and figures.
\usepackage{tikz}
\usepackage{longtable}
\usepackage{array}
\usepackage{float}
\usepackage{multicol}
\usepackage{xparse}
\RenewDocumentCommand{\sectionlink}{s m}{\IfBooleanTF{#1}{\phantomsection\section*{\hyperlink{toc}{#2}}\addcontentsline{toc}{section}{#2}}{\section[#2]{\hyperlink{toc}{#2}}}}
\RenewDocumentCommand{\subsectionlink}{s m}{\IfBooleanTF{#1}{\subsection*{\hyperlink{toc}{#2}}}{\subsection[#2]{\hyperlink{toc}{#2}}}}
\NewDocumentCommand{\subsubsectionlink}{s m}{\IfBooleanTF{#1}{\subsubsection*{\hyperlink{toc}{#2}}}{\subsubsection[#2]{\hyperlink{toc}{#2}}}}
\newcommand{\paragraphlink}[1]{\paragraph[#1]{\hyperlink{toc}{#1}}}
\newcommand{\sourcepageref}[1]{\hyperlink{srcpage:#1}{\pageref*{srcpage:#1}}}
\numberwithin{figure}{section}
\numberwithin{table}{section}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}
\renewcommand{\figurename}{図}
\renewcommand{\tablename}{表}
\hypersetup{pdftitle={デコヒーレンスと量子から古典への移行},pdfauthor={Maximilian Schlosshauer},urlcolor=blue,citecolor=blue,bookmarksnumbered=true,hypertexnames=false}
\title{\bfseries デコヒーレンスと\\量子から古典への移行\\[1ex]{\large\normalfont Decoherence and the Quantum-to-Classical Transition}}
\author{Maximilian Schlosshauer\\[1ex]{\small The University of Melbourne, School of Physics}\\{\small Melbourne, Victoria, 3010, Australia}\\[1ex]{\small\href{https://link.springer.com/book/10.1007/978-3-540-35775-9}{Springer：原著}}}
\date{2026年10月28日}
\begin{document}
'''
# Calling nocite first preserves the 523 original reference numbers.
preamble+='\\nocite{'+','.join(f'ref{i:03}' for i in range(1,524))+'}\n'
body=r'''
\pagenumbering{roman}
\maketitle
\thispagestyle{empty}
\clearpage
'''
for name in ['publication','preface']:
    if (root/'chapters'/f'{name}.tex').exists():body+='\\input{chapters/'+name+'}\n'
body+='\\hypertarget{toc}{}\n\\tableofcontents\n\\clearpage\n\\pagenumbering{arabic}\n'
for ch in range(1,10):
    if ch in excluded:continue
    files=sorted((root/'chapters').glob(f'ch{ch:02}*.tex'))
    if ch==6 and (root/'chapters/ch06.tex').exists():files=[root/'chapters/ch06.tex']
    if files:
        body+=f'\\clearpage\n\\setcounter{{section}}{{{ch-1}}}\n\\setcounter{{footnote}}{{0}}\n'
        for f in files:body+='\\input{chapters/'+f.stem+'}\n'
for f in sorted((root/'chapters').glob('appendix*.tex')):
    body+='\\clearpage\n\\setcounter{footnote}{0}\n\\input{chapters/'+f.stem+'}\n'
body+=r'''
\clearpage
\renewcommand{\refname}{\hyperlink{toc}{参考文献}}
\bibliographystyle{utphys}
\bibliography{ref}
'''
if (root/'chapters/index.tex').exists():body+='\\clearpage\n\\input{chapters/index}\n'
if (root/'chapters/series_back.tex').exists():body+='\\clearpage\n\\input{chapters/series_back}\n'
body+='\\end{document}\n'
(root/config['tex_filename']).write_text(preamble+body,encoding='utf-8')
for f in ['utphys.bst']:(root/f).write_bytes((root/'template_copy'/f).read_bytes())
print('Assembled:',[f.name for f in sorted((root/'chapters').glob('*.tex'))])
