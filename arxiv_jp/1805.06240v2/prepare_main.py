from pathlib import Path
import re

root = Path(__file__).parent
template = (root / 'template_original.tex').read_text(encoding='utf-8')
preamble = template.split('\\title{', 1)[0]
macros = r'''
% 原文で定義された数式用マクロ。テンプレートの設定は保持する。
\newcommand{\mx}{{\text{mix}}}

\newcommand{\Pcal}{{\mathcal{P}}}
\newcommand{\hOcal}{{\hat{\mathcal{O}}}}
\newcommand{\with}{{\quad\mathrm{with}}\quad}
\newcommand{\msr}{{\mathrm{MSR}}}
\newcommand{\hx}{\hat{x}}
\newcommand{\hp}{\hat{p}}
\newcommand{\average}[1]{\langle#1\rangle_{\mathrm{eq}}}
\graphicspath{{original/}}
\renewcommand{\thefootnote}{\arabic{footnote}}
\hypersetup{pdftitle={非平衡開放系における時間並進対称性の破れの有効場理論},
pdfauthor={Masaru Hongo, Suro Kim, Toshifumi Noumi, Atsuhisa Ota}}
'''
body = r'''
\title{\bfseries 非平衡開放系における\\時間並進対称性の破れの有効場理論\\[0.5em]
\large Effective field theory of time-translational symmetry breaking in nonequilibrium open system\\[0.6em]
\normalsize \href{https://arxiv.org/pdf/1805.06240v2}{arXiv:1805.06240v2 [hep-th]}}
\author{Masaru Hongo$^{a}$, Suro Kim$^{b}$,\\Toshifumi Noumi$^{b}$, Atsuhisa Ota$^{c}$}
\date{原文：2018年8月19日（v2）}
\begin{document}
\maketitle
\begin{center}
\small
KOBE-COSMO-18-05\\[0.4em]
$^{a}$iTHEMS Program, RIKEN, Wako 351-0198, Japan\\[0.3em]
$^{b}$Department of Physics, Kobe University, Kobe 657-8501, Japan\\[0.3em]
$^{c}$Institute for Theoretical Physics and Center for Extreme Matter and Emergent Phenomena,\\
Utrecht University, Princetonplein 5, 3584 CC Utrecht, The Netherlands\\[0.5em]
E-mail: \href{mailto:masaru.hongo@riken.jp}{masaru.hongo@riken.jp},
\href{mailto:s-kim@stu.kobe-u.ac.jp}{s-kim@stu.kobe-u.ac.jp},\\
\href{mailto:tnoumi@phys.sci.kobe-u.ac.jp}{tnoumi@phys.sci.kobe-u.ac.jp},
\href{mailto:a.ota@uu.nl}{a.ota@uu.nl}
\end{center}
\begin{abstract}
Schwinger-Keldysh形式に基づき、非平衡開放系における時間並進対称性の破れを扱う有効場理論（EFT）的手法を展開する。Schwinger-Keldysh形式では、閉時間経路に沿った時間発展を記述するために力学的な場が二重化されることに本質的に由来して、微視的なLagrangianのすべての対称性も二重化される。開放系の有効Lagrangianは、この微視的なSchwinger-Keldysh Lagrangianを粗視化することによって得られる。粗視化の結果、ノイズと散逸の効果が現れ、二重化された時間並進対称性を対角部分へと陽に破る。したがって、開放系の対称性の破れた相におけるNambu-GoldstoneボソンのEFTを構築する際には、この対称性構造を取り込む必要がある。この観察とSchwinger-Keldysh作用の整合性に基づき、特に同期現象、時間結晶、および宇宙のインフレーションへの応用を念頭に置いて、時間並進対称性の破れに対する一般的なEFTを構築し、調べる。
\end{abstract}
\clearpage
\hypertarget{toc}{}
\tableofcontents
\clearpage
% 原文の参考文献番号を、初出順（脚注を含む）のまま固定する。
\input{ordered_keys.tex}
\input{parts/part12.tex}
\input{parts/part3.tex}
\input{parts/part4A.tex}
\clearpage
\renewcommand{\refname}{\hyperlink{toc}{参考文献}}
\bibliographystyle{utphys}
\bibliography{ref}
\end{document}
'''
(root / '1805.06240v2_jp.tex').write_text(preamble + macros + body, encoding='utf-8')

if not (root/'ordered_keys.tex').exists():
    keys = re.findall(r'\\bibitem\{([^}]+)\}', (root/'original/SSBofDspv2.bbl').read_text())
    (root/'ordered_keys.tex').write_text('\\nocite{' + ','.join(keys) + '}\n')


