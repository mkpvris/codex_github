from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
template=Path('C:/codex/template/template.tex').read_text(encoding='utf-8')
original=(ROOT/'original/DeftfinArxiv2.tex').read_text()
preamble=template.split(r'\begin{document}')[0]
preamble=preamble.replace(r'\title{\bfseries Write Theme Here}',r'''\title{\bfseries インフレーションの有効場理論における散逸効果\\[0.5em]
\large Dissipative effects in the Effective Field Theory of Inflation\\[0.4em]
\normalsize \href{https://arxiv.org/pdf/1109.4192v2}{arXiv:1109.4192v2 [hep-th]}}''')
preamble=preamble.replace(r'\author{著者}',r'''\author{\parbox{0.96\textwidth}{\centering
Diana L\'opez Nacir$^{1}$, Rafael A. Porto$^{2,3}$,\\
Leonardo Senatore$^{4,5}$, Matias Zaldarriaga$^{2}$\\[0.8em]
\small
$^1$Departamento de F\'isica, Facultad de Ciencias Exactas y Naturales,\\
UBA and IFIBA, CONICET. Ciudad Universitaria,\\
Pabell\'on 1, 1428, Buenos Aires, Argentina.\\[0.3em]
$^2$School of Natural Sciences, Institute for Advanced Study,\\
Einstein Drive, Princeton, NJ 08540, USA\\[0.3em]
$^3$Department of Physics \& ISCAP, Columbia University,\\
New York, NY 10027, USA\\[0.3em]
$^4$Stanford Institute for Theoretical Physics, Stanford University,\\
Stanford, CA 94305\\[0.3em]
$^5$KIPAC, Stanford University \& SLAC, Stanford, CA 94305
}}''')
preamble=preamble.replace(r'\date{\today}',r'\date{2012年1月18日（原文 v2）}')
macros=original[original.index(r'\newcommand'):original.index(r'\begin{document}')]
preamble+=r'''
% Original-source mathematics macros; template class, packages and geometry retained.
'''+macros+r'''
\graphicspath{{figures/}}
% Retain the template's bibliography font and interpret TeX quotation marks.
\AtBeginEnvironment{thebibliography}{\addfontfeatures{Ligatures=TeX}}
% Preserve the original equation numbers (1--212, A1, B1, ...).
\counterwithout{equation}{section}
\renewcommand{\theequation}{\arabic{equation}}
\appto\appendix{\renewcommand{\thesection}{\Alph{section}}\numberwithin{equation}{section}\renewcommand{\theequation}{\Alph{section}\arabic{equation}}\renewcommand{\thesubsection}{\arabic{subsection}}}
\hypersetup{pdftitle={インフレーションの有効場理論における散逸効果 — arXiv:1109.4192v2},pdfauthor={Diana López Nacir, Rafael A. Porto, Leonardo Senatore, Matias Zaldarriaga}}
'''
body=r'''\begin{document}
\maketitle
\begin{abstract}
単一の時計によるインフレーションの有効場理論を、散逸効果を含むように一般化する。ユニタリーゲージを用い、時間依存する空間微分同相変換の下での不変性のみを制約とする有効作用に、複合演算子の集合 $\calo_{\mu\nu\ldots}$ を結合させる。散逸を担う自由度が後期の密度摂動には寄与しない状況に限定する。このとき摂動の力学は「摩擦」項と雑音項の出現によって変化する。これらの複合演算子のGreen関数に一定の局所性を仮定すると、大きな摩擦項 $\gamma\gg H$ によって特徴づけられる領域が存在し、そこでは $\zeta$ の相関関数が雑音に支配され、パワースペクトルが大幅に増強され得ることを示す。また、広い種類の模型について3点関数 $\langle\zeta\zeta\zeta\rangle$ を計算し、どのような条件で大きな摩擦が非Gaussian性を増大させるかを論じる。とくに、本論文の仮定の下では、強い散逸と、対称性を非線形に実現するという要請とを合わせると、$|f_{\rm NL}|\sim\frac{\gamma}{c_s^2H}\gg1$ が導かれることを示す。典型例として、局所的な応答関数をもつ「トラップ型インフレーション」シナリオの変種を詳しく調べ、本論文の有効理論とのマッチングを行う。ここで述べるような、インフレーション中の散逸効果を取り入れることで生じる一般的な特徴が検出されれば、初期宇宙の力学に関する知見が得られ、インフレーション模型のパラメータ空間も広がるであろう。
\end{abstract}
\clearpage
\hypertarget{toc}{}
\tableofcontents
\clearpage
\input{ordered_keys}
\input{sections/part1}
\input{sections/part2}
\clearpage
\input{sections/appendices}
\clearpage
\renewcommand{\refname}{\hyperlink{toc}{参考文献}}
\bibliographystyle{utphys}
\bibliography{ref}
\end{document}
'''
(ROOT/'1109.4192v2_jp.tex').write_text(preamble+body,encoding='utf-8')
print('Main TeX prepared from unchanged template.')
