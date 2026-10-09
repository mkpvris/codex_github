from pathlib import Path
p=Path(r'C:\codex\EFTofOpenSystems\part2\template.tex')
s=p.read_text(encoding='utf-8')
old=r'''基底状態への緩和に対応して占有数はゼロへ向かう。ゼロ点エネルギー$\omega/2$と占有数は別の量である。

\par\noindent 随伴の定義と占有数の計算は付録\ref{app:dual}にまとめる。'''
new=r'''基底状態への緩和に対応して$\av N\to0$となる。ゼロ点エネルギー$\omega/2$と占有数は別の量である（計算は付録\ref{app:dual}）。'''
assert s.count(old)==1
p.write_text(s.replace(old,new),encoding='utf-8')
print('Removed a one-line continuation page in section 2.')
