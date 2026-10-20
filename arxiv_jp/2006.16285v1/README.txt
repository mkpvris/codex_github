有効場の理論入門 — 日本語訳
Riccardo Penco, An Introduction to Effective Field Theories
対象版：arXiv:2006.16285v1
原文PDF：https://arxiv.org/pdf/2006.16285v1
作成日：2026-10-20

主要ファイル
  2006.16285v1_jp.tex        メインTeX原稿
  sections/                 日本語訳の全本文
  pdf/2006.16285v1_jp.pdf    完成PDF（57ページ）
  ref.bib / utphys.bst      参考文献データとテンプレートの文献スタイル
  imgs/ / graphs.*          原文の図版とFeynman図の生成物
  original/                 提供PDFと、同じ版の公式arXiv TeXソース一式
  template_pdf_backup/      テンプレートに含まれていたPDF・補助生成物の保存
  bibliography_sources/     INSPIRE-HEP公式BibTeX・取得元メタデータ
  bibliography_verification.txt
                             参考文献52件の取得・照合記録
  verification/             数式・参照・リンク検証、ページ画像、原文の確認候補
  build.ps1                 再生成用PowerShellスクリプト

範囲と方針
題名、著者・所属、要旨、全4節・23小節、演習、数式、図表、脚注、
謝辞、参考文献を収録しました。原文に内容のある付録はありません。
本文の要約や省略はしていません。元のC:\codex\templateは変更していません。
テンプレートの文書クラス・基本パッケージ・余白・フォント・目次と見出しリンク・
文献スタイルを維持し、原文の図や演習枠に必要な設定のみ追加しました。
式番号は原文の通し番号を保持するため、テンプレートの節別番号設定を解除しました。
長い数式3か所には局所的な改ページ抑制を加えました。
参考文献では、同じフォントのままTeX引用符・ダッシュの合字処理を有効にしました。
人名・固有名詞は原則として英語表記を保っています。

参考文献
52件すべてINSPIRE-HEP公式エクスポートを取得し、原文の引用番号順でBibTeX処理しました。
未加工の公式エクスポートを保存した上で、ref.bibでは原文の引用キーを使用し、
元の版・会議・出版社情報が公式データに不足する箇所を注記等で補っています。
詳細はbibliography_verification.txtを参照してください。
現行の公式データとutphys.bstの組合せによるBibTeX警告が5件残ります：
  [15]、[16]、[35]のbooktitleの欠落、
  [24]のauthor/editor併記とpublisherの欠落。
これらは公式エクスポートに由来する任意書誌項目・スタイル上の警告です。
52件の文献生成・本文参照・リンクはすべて解決しており、コンパイルエラーはありません。
原文の刊行情報は失わないよう注記に保持しています。

検証
LuaLaTeX → BibTeX → LuaLaTeX 2回の処理を実施し、図にはMetaPostも使用しました。
最終調整後も再コンパイルし、参照情報を確定しました。
原文・翻訳の数式内容、引用キーと順序、図表・脚注等の構造を照合済みです。
原文と同一の157個の数式リンク先を確認しています。
最終PDF内で全52件の本文引用リンク、367個の内部リンク、
78個の外部リンク、タイトルの同じ版の原文PDFリンクを検証しました。
未解決参照、リンク先の欠落、文字欠け、はみ出しは検出されませんでした。
ページ画像による全57ページの目視確認も実施しました。
原文で見つかった誤植等の候補は本文を独断で直さず、
verification/source_notes.txtに分けて記録しました。

再生成
LuaLaTeX、BibTeX、MetaPostを利用できる環境で、このフォルダを丸ごと保存し、
build.ps1を実行してください。直接実行する場合は、このフォルダで次の順に実行します。

  lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf 2006.16285v1_jp.tex
  mpost -interaction=nonstopmode pdf/graphs.mp
  bibtex pdf/2006.16285v1_jp
  lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf 2006.16285v1_jp.tex
  lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf 2006.16285v1_jp.tex

参考文献や図版の相対参照は、このフォルダ内で完結しています。
