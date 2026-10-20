from pathlib import Path
import json
import re

root = Path(__file__).resolve().parent
template = (root / "template_original" / "template.tex").read_text(encoding="utf-8-sig")
preamble = template.split(r"\begin{document}")[0]
preamble = preamble.replace(
    r"\title{\bfseries Write Theme Here}",
    r"""\title{\bfseries 弦理論\\[0.4em]
第I巻：ボソン弦入門\\[0.8em]
\large 前付け・第1--5章 日本語訳\\
\normalsize\href{../source/String_Polchinski1_original.pdf}{添付された原文PDF}}"""
)
preamble = preamble.replace(
    r"\author{著者}",
    r"""\author{Joseph Polchinski\\
\small Institute for Theoretical Physics\\
\small University of California at Santa Barbara}"""
)
preamble = preamble.replace(r"\date{\today}", r"\date{逐次翻訳版：2026年10月21日}")
preamble += r"""
% 原書の図番号（章.図）を保持するための最小限の追加。
\numberwithin{figure}{section}
\hypersetup{hypertexnames=false,pdftitle={弦理論 第I巻：ボソン弦入門（前付け・第1--5章 日本語訳）},
pdfauthor={Joseph Polchinski},bookmarksnumbered=true}
\emergencystretch=2em
"""
main = preamble + r"""
\begin{document}
\maketitle
\noindent
本PDFは全巻の逐次翻訳のうち、前付けと第1--5章（原書本文1--165ページ）を収録する。
第6--9章、付録A、全巻の参考文献解説・用語集・索引は作業中であり、この版には未収録である。
原書の歴史的記述・式番号を保持する。本書はarXiv論文ではないため、arXiv番号は付さない。

\hypertarget{toc}{}
\tableofcontents
\clearpage
\input{sections/frontmatter}
\clearpage
\input{sections/ch01a}
\input{sections/ch01b}
\clearpage
\input{sections/ch02a}
\input{sections/ch02b}
\clearpage
\input{sections/ch03a}
\input{sections/ch03b}
\input{sections/ch03c}
\clearpage
\input{sections/ch04}
\clearpage
\input{sections/ch05}
\clearpage
\renewcommand{\refname}{\hyperlink{toc}{参考文献（収録範囲の引用）}}
\bibliographystyle{utphys}
\bibliography{ref}
\end{document}
"""
(root / "String_Polchinski1_jp.tex").write_text(main, encoding="utf-8")

# Retain raw official exports separately. Supplement missing publisher/URL fields
# using the supplied book's bibliography and the matched INSPIRE record.
chosen = [
    ("Green, Schwarz, Witten (1987), volume II", "gsw1987v2_252419.bib", "252419",
     "原文1987年、INSPIRE公式エクスポート1988年。著者・巻・題名の一致を確認。公式出力は改変しない。"),
    ("Misner, Thorne, Wheeler (1973)", "misner1973_95654.bib", "95654",
     "著者・題名・出版社・1973年が一致。"),
]
bib_parts = []
for item in chosen:
    raw = (root / "source" / "bibliography" / item[1]).read_text(encoding="utf-8").rstrip()
    fields = f'    url = "https://inspirehep.net/literature/{item[2]}"'
    if item[2] == "252419":
        fields = '    publisher = "Cambridge University Press",\n    address = "Cambridge",\n' + fields
    raw = raw[:-1].rstrip() + ",\n" + fields + "\n}\n"
    bib_parts.append(raw)
(root / "ref.bib").write_text("\n".join(bib_parts), encoding="utf-8")
records = [{"original": x[0], "file": x[1],
            "url": f"https://inspirehep.net/api/literature/{x[2]}?format=bibtex",
            "match_note": x[3],
            "supplements": "照合済みINSPIREレコードURLを追加。GSWのみ原書参考文献から出版社・出版地を補完。既存の公式フィールドは保持。"} for x in chosen]
(root / "qa" / "included_bibliography.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

front_path = root / "sections" / "frontmatter.tex"
front = front_path.read_text(encoding="utf-8")
# Insert citations immediately after the literal original author-year mention.
if r"\cite{Green:1987mn}" not in front:
    front, n1 = re.subn(r"(Green[^\n]*Schwarz[^\n]*Witten[^\n]*1987[）)])",
                       r"\1\\cite{Green:1987mn}", front, count=1)
    if n1 != 1:
        raise RuntimeError("Locate Green--Schwarz--Witten citation manually")
if r"\cite{Misner:1973prb}" not in front:
    front, n2 = re.subn(r"(Misner[^\n]*Thorne[^\n]*Wheeler[^\n]*1973[）)])",
                       r"\1\\cite{Misner:1973prb}", front, count=1)
    if n2 != 1:
        raise RuntimeError("Locate Misner--Thorne--Wheeler citation manually")
front_path.write_text(front, encoding="utf-8")
part = root / "sections" / "ch02b.tex"
text = part.read_text(encoding="utf-8")
text = re.sub(r"重み(?!付け)", "ウェイト", text)
part.write_text(text, encoding="utf-8")
print("Assembled front matter and chapters 1-5; two original citations linked.")
