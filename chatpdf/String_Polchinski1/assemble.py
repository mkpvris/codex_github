"""Assemble explicitly reviewed translation components with the original template."""
from pathlib import Path
import json
import shutil
import re

root = Path(__file__).resolve().parent
state = json.loads((root / "assembly_manifest.json").read_text(encoding="utf-8-sig"))
template = (root / "template_original" / "template.tex").read_text(encoding="utf-8-sig")
preamble = template.split(r"\begin{document}")[0]
title = r"""\title{\bfseries 弦理論\\[0.4em]第I巻：ボソン弦入門\\[0.8em]
\small\mdseries\href{https://www.cambridge.org/core/books/string-theory/30409AF2BDE27D53E275FDA395AB667A}{String Theory}\\
\small Volume I: An Introduction to the Bosonic String}"""
preamble = preamble.replace(r"\title{\bfseries Write Theme Here}", title)
preamble = preamble.replace(r"\author{著者}", r"""\author{Joseph Polchinski\\
\small Institute for Theoretical Physics\\
\small University of California at Santa Barbara}""")
preamble = preamble.replace(r"\date{\today}", r"\date{2026年10月21日}")
preamble = preamble.replace(
    r"\newcommand{\sectionlink}[1]{\section[#1]{\hyperlink{toc}{#1}}}",
    r"""\makeatletter
\newcommand{\sectionlink}{\@ifstar{\sectionlinkstar}{\sectionlinknumbered}}
\makeatother
\newcommand{\sectionlinknumbered}[1]{\section[#1]{\hyperlink{toc}{#1}}}
\newcommand{\sectionlinkstar}[1]{%
  \section*{\hyperlink{toc}{#1}}%
  \addcontentsline{toc}{section}{#1}%
}"""
)
# References has original introductory prose before the list. Use one heading
# and one contents entry for that whole original section.
preamble = re.sub(r"\\BeforeBeginEnvironment\{thebibliography\}\{%.*?\n\s*\}", "", preamble, flags=re.S)
preamble += r"""
% 明示的な原書式番号に対しても一意のリンク先を生成する。
\numberwithin{figure}{section}
\hypersetup{hypertexnames=false,pdftitle={弦理論 第I巻：ボソン弦入門 日本語訳},
pdfauthor={Joseph Polchinski},bookmarksnumbered=true}
\emergencystretch=2em
\setcounter{tocdepth}{3}
\setcounter{secnumdepth}{3}
\NewDocumentCommand{\subsubsectionlink}{s m}{%
  \IfBooleanTF{#1}{%
    \subsubsection*{\hyperlink{toc}{#2}}%
    \addcontentsline{toc}{subsubsection}{#2}%
  }{\subsubsection[#2]{\hyperlink{toc}{#2}}}%
}
\usepackage{makeidx}
\makeindex
\newcommand{\indexitalic}[1]{\textit{\hyperpage{#1}}}
\newcommand{\indexfollowing}[1]{\hyperpage{#1}\,ff.}
\newcommand{\indexitalicfollowing}[1]{\textit{\hyperpage{#1}\,ff.}}
\DeclareRobustCommand{\indexcrossref}[2]{#1}
% Keep the original one-column index layout for long bilingual entries.
\makeatletter
\renewenvironment{theindex}{%
  \clearpage\sectionlink*{索引}%
  斜体のページ番号は演習を指す。\par\medskip
  \small\parindent\z@\parskip\z@ \@plus .3\p@\relax
  \let\item\@idxitem
}{\par\clearpage}
\makeatother
\RenewDocumentCommand{\subsectionlink}{s m}{%
  \IfBooleanTF{#1}{%
    \subsection*{\hyperlink{toc}{#2}}%
  }{\subsection[#2]{\hyperlink{toc}{#2}}}%
}
"""
main = preamble + "\n\\begin{document}\n\\input{sections/reference_keys}\n"
main += "\\input{sections/reference_order}\n\\maketitle\n"
main += "\\hypertarget{toc}{}\n\\tableofcontents\n\\setcounter{tocdepth}{3}\n\\clearpage\n\\input{sections/frontmatter}\n"
for group in state["chapters"]:
    main += "\\clearpage\n"
    for name in group:
        if not (root / "sections" / (name + ".tex")).is_file():
            raise FileNotFoundError(name)
        main += "\\input{sections/" + name + "}\n"
if state["appendix"]:
    main += "\\clearpage\n\\appendix\n\\renewcommand{\\thefigure}{\\Alph{section}.\\arabic{figure}}\n\\input{sections/appendixA}\n"
main += r"""
\addtocontents{toc}{\protect\setcounter{tocdepth}{2}}
\setcounter{tocdepth}{2}
\clearpage
\input{sections/references_intro}
\begingroup
\RenewDocumentCommand{\section}{s o m}{}
\bibliographystyle{utphys}
\bibliography{ref}
\endgroup
"""
for group in state["backmatter"]:
    main += "\\clearpage\n"
    for name in group:
        main += "\\input{sections/" + name + "}\n"
main += "\\end{document}\n"
(root / "String_Polchinski1_jp.tex").write_text(main, encoding="utf-8")
shutil.copyfile(root / "ref_complete.bib", root / "ref.bib")
print(f"Assembled {state['edition']} with all 113 original bibliography items.")
