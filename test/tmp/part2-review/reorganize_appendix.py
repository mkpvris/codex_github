from pathlib import Path
import re

target = Path(r'C:\codex\EFTofOpenSystems\part2\template.tex')
s = target.read_text(encoding='utf-8')
original = s
assert '\\appendix\n' not in s, 'Appendix already exists; refusing duplicate transformation.'
blocks = {}

def move(key, prefix, end, replacement):
    global s
    marker = '\\supplement{' + prefix
    assert s.count(marker) == 1, (key, s.count(marker))
    start = s.index(marker)
    stop = s.index(end, start)
    blocks[key] = s[start:stop].strip()
    s = s[:start] + replacement.strip() + '\n\n' + s[stop:]

def ptr(label, text='計算と出典'):
    return r'\par\noindent ' + text + r'は付録\ref{' + label + r'}にまとめる。'

move('pop', '占有確率の式の成分計算', '\\subsectionlink{期待値から見る同じ減衰}', ptr('app:pop'))
move('dual', '双対性の意味と計算', '\\end{lecturesection}', ptr('app:dual', '随伴の定義と占有数の計算'))
move('double', '二重交換子への書き換え', '\\noindent\\textcolor{noteblue}', ptr('app:dephase', '二重交換子による書き換え'))
s = s.replace('\\noindent\\textcolor{noteblue}{\\textbf{動画の説明に戻る。}}\n', '')
move('dephase', '式の復元と留保', '\\end{lecturesection}', ptr('app:dephase', '式の校訂と定常状態に関する注意'))
move('entropy_conditions', '定理の使い方', '\\supplement{「基底状態へ行く」', ptr('app:entropy_conditions', '半群・有限次元の適用条件'))
move('entropy_example', '「基底状態へ行く」', '\\end{lecturesection}', r'減衰の途中でエントロピーが増える例もある。単調減少とは限らないことの具体例は付録\ref{app:entropy_example}に示す。')
move('notation', '記法の照合', '\\end{lecturesection}', r'トレース内の$O$は固定演算子である。描像と積分変数の記法は付録\ref{app:notation}で補足する。')
move('boundary', '数式と境界条件の照合', '\\end{lecturesection}', ptr('app:boundary', '初期状態と境界条件の補足'))
move('normalization', '演算子表示による確認', '\\end{lecturesection}', r'規格化された初期状態と、両枝で同じ実ソースを用いる。演算子表示による確認は付録\ref{app:normalization}に示す。')
move('turnaround', '対応式の照合と折返し点', '講義の休憩後には', r'折返し時刻$t_f$はすべての挿入時刻より後に選ぶ。余分な発展が相殺されることの確認は付録\ref{app:turnaround}に示す。')
move('ra', '規約と係数の照合', '\\subsectionlink{何がゼロになるのか}', ptr('app:ra', '規約の詳しい照合と混合相関の展開'))
move('alla', '全$a$相関が消える理由', '\\end{lecturesection}', ptr('app:alla', 'ソース微分による証明'))
move('initial', '初期条件と用語', '\\subsectionlink{系だけの有効作用}', r'積分の添字$\rho_{E,0}$には環境の初期密度行列による重みと終点のトレースを含む。詳細は付録\ref{app:initial}を参照。')
move('if', '模式的な「$S_{\\IF}\\ne0$なら開放系」', '\\subsectionlink{この動画で到達した点}', r'\supplement{非零の影響作用が必ず散逸を意味するわけではない。作用補正や記憶効果との区別は、文献\cite{Pajer:2026fuo}第4.3節に基づき付録\ref{app:if}で補う。}')

# Keep an essential assumption next to the definition, even after the detail moves.
s = s.replace('環境に依存する重みをまとめて\n',
    r'\supplement{この分離表示では因子化初期状態$\rho_{SE}(t_0)=\rho_S(t_0)\otimes\rho_E(t_0)$を仮定する（文献\cite{Pajer:2026fuo}第4.3節、式(4.54)；付録\ref{app:initial}）。}' + '\n環境に依存する重みをまとめて\n', 1)

table_start = s.index('\\section*{補足出典の対応表}')
table_end = s.index('\\bibliographystyle{utphys}', table_start)
table = s[table_start:table_end]
table = table.replace('\\section*{補足出典の対応表}\n\\addcontentsline{toc}{section}{補足出典の対応表}\n', '')
table = table.rstrip()
if table.endswith('\\clearpage'):
    table = table[:-len('\\clearpage')].rstrip()

def sub(title, label, keys):
    return '\n\\subsectionlink{' + title + '}\n\\label{' + label + '}\n' + '\n\n'.join(blocks[k] for k in keys) + '\n'

appendix = r'''
% ============================================================
% 付録：動画で省略された計算・適用条件・出典対応表
% ============================================================
\appendix
\renewcommand{\theequation}{\Alph{section}.\arabic{equation}}

\sectionlink{演算子形式の補足計算}
\label{app:operator}
本文第2・3節の追加計算をまとめる。以下は文献に基づく補足であり、動画の逐語的な再現ではない。
'''
appendix += sub('占有確率と定常分布', 'app:pop', ['pop'])
appendix += sub('随伴生成子と平均占有数', 'app:dual', ['dual'])
appendix += sub('位相緩和の二重交換子表示と校訂', 'app:dephase', ['double','dephase'])
appendix += r'''
\clearpage
\sectionlink{エントロピーの適用条件と検算例}
\label{app:entropy}
'''
appendix += sub('Unital性から時間に関する単調性を読む条件', 'app:entropy_conditions', ['entropy_conditions'])
appendix += sub('純粋状態から出発する減衰の例', 'app:entropy_example', ['entropy_example'])
appendix += r'''
\clearpage
\sectionlink{Schwinger--Keldysh形式の補足確認}
\label{app:sk}
'''
appendix += sub('演算子と積分変数の記法', 'app:notation', ['notation'])
appendix += sub('初期状態と境界条件', 'app:boundary', ['boundary'])
appendix += sub('生成汎関数の規格化', 'app:normalization', ['normalization'])
appendix += sub('折返し時刻の自由度', 'app:turnaround', ['turnaround'])
appendix += sub('混合相関の符号と係数', 'app:ra', ['ra'])
appendix += sub('全ての挿入が差の場である相関の消失', 'app:alla', ['alla'])
appendix += r'''
\clearpage
\sectionlink{影響作用の初期条件と解釈}
\label{app:influence}
'''
appendix += sub('因子化初期状態と環境のトレース', 'app:initial', ['initial'])
appendix += sub('作用の補正・散逸・記憶効果の区別', 'app:if', ['if'])
appendix += r'''
\clearpage
\sectionlink{補足出典の対応表}
\label{app:sources}
'''
appendix += table + '\n\\clearpage\n'

s = s[:table_start] + appendix + s[table_end:]
s = s.replace('動画にない導出や留保は「文献補足」と表示し、参照箇所を併記する。',
              '動画にない計算・詳しい留保は付録にまとめ、本文から参照する。必要な仮定は本文にも出典付きで示す。')
s = s.replace('表現の精密化を追加する場合は、その段落を文献補足として明示する。',
              '表現の精密化は付録にまとめ、対応する本文から参照する。付録の各補足にも文献の引用箇所を明示する。')
s = s.replace('各節は改ページし、式番号は節ごとに付す。青字は動画の対応時刻、赤茶色は文献補足を示す。',
              '各節は改ページし、式番号は本文では節番号、付録ではA.1などとする。青字は動画の対応時刻、赤茶色は文献補足を示す。')
s = s.replace('\\bibliographystyle{utphys}\n\\bibliography{ref}', r'''\renewcommand{\refname}{\hyperlink{toc}{参考文献}}
\bibliographystyle{utphys}%
\bibliography{ref}%参考文献リストを入れているファイル名。ref.bibから取り出す。

\newpage''')
# Relocated content must refer to the main text rather than imply it is still above it.
s = s.replace('動画の成分表示を整理するために次式を補った。', '本文の成分表示を整理するために次式を補った。')
s = s.replace('以下は第2節の占有確率の方程式から追加した検算例である。', '以下は本文の式\\eqref{eq:pauli}から追加した検算例である。')
s = s.replace('上の簡潔な導出は動画に合わせて位置の関数に限定している。', '本文第6節の導出は動画に合わせて位置の関数に限定している。')
s = s.replace('この恒等式から、後で$a$場だけの相関関数が消えることも導ける。', 'この恒等式から、付録\\ref{app:alla}のように$a$場だけの相関関数が消えることも導ける。')

# Validate relocation and source preservation before touching the requested file.
assert len(blocks) == 14
assert s.count('\\appendix\n') == 1
assert s.count('\\bibliographystyle{utphys}') == 1
labels = re.findall(r'\\label\{([^{}]+)\}', s)
assert len(labels) == len(set(labels)), 'Duplicate label after relocation'
for k, b in blocks.items():
    assert b.splitlines()[0].split('。')[0] in s, k
old_bibkeys=set(re.findall(r'\\cite\{([^}]+)\}', original))
assert old_bibkeys <= set(re.findall(r'\\cite\{([^}]+)\}', s))
backup=Path(r'C:\codex\test\tmp\part2-review\template-before-appendix.tex')
backup.write_text(original, encoding='utf-8')
target.write_text(s, encoding='utf-8')
print('Updated requested template.tex; moved 14 supplementary blocks into appendices A-D; source table is appendix E.')
