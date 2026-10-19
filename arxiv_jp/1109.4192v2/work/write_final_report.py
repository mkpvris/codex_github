from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
links=json.loads((ROOT/'work/pdf_link_and_numbering_check.json').read_text(encoding='utf-8'))
bib=json.loads((ROOT/'work/bibliography_report.json').read_text(encoding='utf-8'))
log=(ROOT/'pdf/1109.4192v2_jp.log').read_text(encoding='utf-8',errors='replace')
assert 'There were undefined references' not in log
assert 'Missing character:' not in log
assert 'Overfull \\hbox' not in log
text=f'''翻訳・最終ダブルチェック記録

対象: arXiv:1109.4192v2
Diana López Nacir, Rafael A. Porto, Leonardo Senatore, Matias Zaldarriaga
Dissipative effects in the Effective Field Theory of Inflation
原文版日付: 2012年1月18日
作業日: 2026年10月19日（日本時間）
保存先: C:\\codex\\arxiv_jp\\1109.4192v2
メイン原稿: 1109.4192v2_jp.tex
完成PDF: pdf/1109.4192v2_jp.pdf（{links['pages']}ページ）

1. 指示の二重確認
作業開始前と最終確認時の両方で、作業フォルダのAGENTS.mdとC:\\codex\\AGENTS.mdを再読した。
テンプレートを補助ファイルごと複製し、元のC:\\codex\\templateは変更していない。
元テンプレートの全9ファイルは作業前後のSHA-256が一致。utphys.bstも元と同一。
文書クラスltjsarticle、11pt、A4、余白25/25/30/30mm、本文フォント、文献フォント、目次・見出しリンクを維持。
テンプレート由来の旧生成物はtemplate_pdf_backupに保持した。

2. 翻訳範囲・独立照合
題名・著者所属・要旨・本文全9節・付録A〜I・謝辞を収録。
45脚注、15図版、9キャプション、244ラベル、326本文参照、116引用コマンドが原文と一致。
翻訳担当の照合に加え、別担当が全文・全脚注・全キャプションの意味を独立して読み合わせた。
数式は原文を保持し、数式中の説明語for、Noise、cyclic sumだけを日本語化した。
原文のTeXにあった閉じ括弧不足を修復。数学的な誤植候補は独断で修正していない。
人名・固有名詞を原綴りに統一（de Sitter、Goldstone、Green、Hubble、Einstein、Stückelberg等）。
一般用語は日本語とし、トラップ型インフレーション、温かいインフレーション、外部曲率等を統一。
原文の数式・記述の疑義: work/part1_notes.txt、work/part2_notes.txt、work/appendices_notes.txt。

3. 書誌
原文の56引用番号に属する65件を収録。
INSPIRE公式エクスポート61件、Crossref公式2件、CiNii Books公式1件。
Fetter–Walecka (1971) はINSPIREに一致する登録が見つからず、原文の完全な書誌を@bookとして転記し公的図書館目録と照合した。
手作業の@miscへの置換なし。公式取得の全フィールドを保持。取得元と生データ、ハッシュ、照合根拠を保存。
Calzetta–Huの出版者・年はINSPIRE出力に不整合があり、Cambridgeの初版奥付と原文に基づきCambridge University Press (2008)へ訂正。
Zhangの原文誌名Phys. Rev. Dは出版社のPhys. Rev. E 47, 3745 (1993)に訂正。
Forsterは2018再刊版を避け、1975初版の公式書誌を採用。原文のPerseus表記を注記。
原文で執筆中のhydro文献は、4著者と主題の一致から対応する後年の論文と判断。原文の題名と執筆中表記を注記に保持。
複数文献が同一番号にまとめられた箇所は、各文献をutphysでBibTeX整形した後、同じ番号の段落へ結合。
原文[1]〜[56]の順序を完全に維持。本文の引用キーは変更していない。
詳細: work/bibliography_report.json、work/bibliography_independent_review.txt、work/bibliography_cache/。

4. 生成とPDFリンク検証
build.ps1でLuaLaTeX → BibTeX → LuaLaTeX → LuaLaTeXを実行。
BibTeX直後にwork/group_bibliography.pyで上記の文献番号グループを復元する。
未解決参照・未解決引用・文字欠落・横方向のはみ出しはゼロ。
本文・数式・図・付録の全ラベル番号を原文TeXの実際のコンパイル結果と照合し差分ゼロ。
PDFの内部リンク{links['internal_link_count']}件の飛び先はすべて存在。うち引用リンク{links['citation_link_count']}件。
参考文献56個すべての着地点に、対応する印刷番号[n]があることを座標とPDFテキストで確認。
PDF外部リンク注釈{links['external_link_count']}件を検査し、文献に必要な{links['expected_external_urls']}種類のURLがすべて存在することを確認。
タイトルのarXivリンクは https://arxiv.org/pdf/1109.4192v2 。
このリンクから取得したPDFとユーザー指定PDFのSHA-256は完全一致:
72095ea661c7993d38d18b55ca6a54bf09f342448238f6119ba67dbeddbad063
個々の外部サイトの将来の稼働を保証する検査ではなく、完成PDFのリンク注釈・URLと公式取得書誌との照合を実施した。
詳細: work/pdf_link_and_numbering_check.json、work/structural_check.json。

5. 画像による確認と配置上の調整
全ページをPNGへ変換し、一覧と拡大画像で確認。文字化け・裁断・重なり・欠けなし。
図1・2の上下配置と説明を一致させた。図9は原文内の上下/左右の不一致を、実際の横並びに合わせて左右へ修正。
図5・8の原データの大きな白余白だけを切り詰めた。元EPSと未加工PDFも保持。
謝辞は見出しと本文を同じページにまとめた。文献のTeX引用符はテンプレートの書体を維持して正しく表示。
ログの微小な縦方向警告（2.7909pt）は付録F付近の脚注ページで、拡大画像で罫線・脚注・数式・頁番号の欠けや重なりがないことを確認。
BibTeX警告1件（iraeftのbooktitle未設定）は、INSPIRE公式エクスポートにも原文にも情報がないため推測で補わず保持。
数式用フォントの小サイズ代替はTeX既定動作。文字欠落なし。
画像確認記録: work/visual_review_01_27.txt、work/visual_review_28_54.txt、work/visual_review_55_75.txt。

6. 再生成
このフォルダでbuild.ps1を実行する。LuaLaTeX/BibTeXとPython 3（グループ化処理は標準ライブラリのみ）が必要。
本文・図版・参考文献への参照は成果物フォルダ内で完結。
work内の取得・検証スクリプトや中間生成物もAGENTS.mdの指定に従って保持した。
GitHub反映結果は別ファイルgithub_upload_verification.jsonで確認できる。
'''
(ROOT/'翻訳確認記録.txt').write_text(text,encoding='utf-8')
(ROOT/'README.txt').write_text('日本語訳 arXiv:1109.4192v2\n\n閲覧: pdf/1109.4192v2_jp.pdf\nTeX: 1109.4192v2_jp.tex\n再生成: build.ps1\n確認記録: 翻訳確認記録.txt\n原文の疑義: work/part1_notes.txt, work/part2_notes.txt, work/appendices_notes.txt\n\n参考文献はref.bibと元テンプレートのutphys.bstを使用します。\n',encoding='utf-8')
print('Final Japanese verification record written.')
