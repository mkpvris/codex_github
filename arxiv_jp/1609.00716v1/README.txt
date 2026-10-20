Lectures on Inflation §3.5 日本語訳
対象：Leonardo Senatore, arXiv:1609.00716v1、原文40～49ページ。

完成PDF：pdf/1609.00716v1_jp.pdf
本文TeX：1609.00716v1_jp.tex、part1.tex～part3.tex
再生成：LuaLaTeX と BibTeX が利用できる環境で build.ps1 を実行する。

C:\codex\template の文書クラス、パッケージ、余白、基本フォント、目次、見出しリンク、utphys.bstを引き継いだ。
元テンプレートからコピーされたPDF・補助生成物は保持し、template_pdf_backupにも保存した。
template_ref_backup.bib は元テンプレートの文献ファイル。

式(151)～(187)と図16・17は提供された原文PDFから切り出した600dpiの高精細画像。
assets_raw は元PDFからの切り出し。assets のPDFは同じ原本で、PNGはそれをPopplerで600dpi描画したもの。完成版にはPNGを用い、非表示の周辺原文が検索やコピーに混入しないようにしている。数式と図は画像として配置されているため、本文TeXから数式文字列を直接編集する形式ではない。
数式画像は原文の表記を保持しており、原文の疑義を本文TeXで勝手に修正していない。
crop_manifest.json に元PDFのページ番号と切り出し範囲を記録した。

ref.bib はINSPIRE-HEPから取得した公式BibTeX。取得元と照合内容はbib_sources.json。
build.ps1 は BibTeX の出力に原文の引用番号を対応させ、原文[28]の2論文を1項目にまとめる。
文献書誌自体はutphys.bstによるBibTeX出力を使用。未加工の出力はpdf/1609.00716v1_jp.bibtex_original.bblに保存。
validation.json には参照・リンク・収録範囲・PDFハッシュの検証結果を保存。

原著掲載ページ：https://arxiv.org/abs/1609.00716v1
原著PDF：https://arxiv.org/pdf/1609.00716v1
arXivで確認されたライセンス：https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html
公開ライセンスから翻訳物の第三者への再配布許諾は確認されていない。本訳は利用者から提供されたPDFに基づく非公式訳。
