from pathlib import Path

base=Path(__file__).resolve().parent
template=Path(r'C:\Users\false\codex\template\template.tex').read_text(encoding='utf-8')
template=template.replace(r'\newcommand{\sectionlink}[1]{\section[#1]{\hyperlink{toc}{#1}}}',r'''\RenewDocumentCommand{\sectionlink}{s m}{%
  \IfBooleanTF{#1}{%
    \section*{\hyperlink{toc}{#2}}%
    \phantomsection\addcontentsline{toc}{section}{#2}%
  }{\section[#2]{\hyperlink{toc}{#2}}}%
}''')
# The command is already declared by the template at this point; replace its
# declaration with the new star-aware declaration in the copied document only.
template=template.replace(r'\RenewDocumentCommand{\sectionlink}',r'\NewDocumentCommand{\sectionlink}')
template=template.replace(r'\newfontfamily\bibfontface{',r'\newfontfamily\bibfontface[Ligatures=TeX]{')
template=template.replace(r'\allowdisplaybreaks',r'''% Explicit original equation tags leave amsmath's counter unchanged.
% Step it separately to keep the automatic PDF destinations unique.
\BeforeBeginEnvironment{equation}{\stepcounter{equation}}
\allowdisplaybreaks''')
template=template.replace(r'\newcommand{\papertitlejp}{日本語題名}',r'\newcommand{\papertitlejp}{量子 Brownian 運動への経路積分アプローチ}')
template=template.replace(r'\newcommand{\papertitleen}{English title}',r'\newcommand{\papertitleen}{Path integral approach to quantum Brownian motion}')
template=template.replace(r'\newcommand{\paperarxivurl}{}',r'\newcommand{\paperarxivurl}{https://doi.org/10.1016/0378-4371(83)90013-4}')
template=template.replace(r'\newcommand{\paperarxivlabel}{}',r'\newcommand{\paperarxivlabel}{Physica A 121 (1983) 587--616 (DOI)}')
template=template.replace(r'\newcommand{\paperinspireurl}{}',r'\newcommand{\paperinspireurl}{https://inspirehep.net/literature/176411}')
template=template.replace(r'\newcommand{\paperinspirelabel}{}',r'\newcommand{\paperinspirelabel}{INSPIRE-HEP: 176411}')
template=template.replace(r'\author{著者}',r'''\input{sections/frontmatter}
\author{\paperauthors}
\hypersetup{pdftitle={量子 Brownian 運動への経路積分アプローチ},pdfauthor={A.O. Caldeira and A.J. Leggett}}
\pdfstringdefDisableCommands{\def\hyperlink#1#2{#2}}''')
template=template.replace(r'\date{\today}',r'\date{2026年10月29日}')
start=template.index(r'\begin{document}')
template=template[:start]+r'''\begin{document}
\maketitle
\begin{center}\small\originalreceiptdates\end{center}
\begin{abstract}
\paperabstract
\end{abstract}
\clearpage
\hypertarget{toc}{}
\tableofcontents
\clearpage
% Keep original reference numbering even when a citation appears later in prose.
\nocite{'''+','.join(f'ref{i:02}' for i in range(1,39))+r'''}
\input{sections/part1}
\input{sections/part2}
\input{sections/part3}
\clearpage
\renewcommand{\refname}{\hyperlink{toc}{参考文献}}
\bibliographystyle{utphys}
\bibliography{ref}
\end{document}
'''
(base/'Path_integral_approach_to_quantum_Brownian_motion_jp.tex').write_text(template,encoding='utf-8')
print('Main document assembled from unchanged original template.')
