from pathlib import Path
import json,hashlib,re
root=Path(__file__).resolve().parent
config=json.loads((root/'project_config.json').read_text(encoding='utf-8'))
audit=json.loads((root/'audit/final_pdf_audit.json').read_text(encoding='utf-8'))
render=json.loads((root/'audit/final_render/render_manifest.json').read_text(encoding='utf-8'))
pdf=root/'pdf'/config['pdf_filename'];sha=hashlib.sha256(pdf.read_bytes()).hexdigest()
assert audit['pdf_sha256']==sha==render['pdf_sha256']
assert render['rendered_pages']==audit['pdf_pages']
assert not audit['unresolved_internal_destinations']
expected_changes={151,157,160,161,176,181,184,188,191,197}
actual_changes={int(Path(x).stem.split('-')[1]) for x in render['changed_page_images']}
assert actual_changes and actual_changes<=expected_changes
peer=json.loads((root/'audit/final_affected_page_qa_peer.json').read_text(encoding='utf-8'))
assert peer['pdf_sha256']==sha and peer['status']=='passed'
assert set(peer['pages'])=={181,184,188,191,197}
assert 'Warning--' not in (root/'build'/(config['build_jobname']+'.blg')).read_text(encoding='utf-8',errors='replace')
prior_review=json.loads((root/'audit/final_visual_qa_121_240.json').read_text(encoding='utf-8'))
prior_changed=prior_review['changed_pages_inspected_full_resolution']
prior_manifest={'pdf_sha256':prior_review['reviewed_pdf_sha256'],'pdf_pages':348,'rendered_pages':348,'sheets':29,'unchanged_rendered_pages':348-len(prior_changed),'changed_page_images':[f'page-{n:03}.png' for n in prior_changed],'provenance':'Previous render_manifest.json values retained from the task tool output and the independent reviewer report before the final cosmetic rerender.'}
prior_archive=root/'audit/final_render'/('render_history_'+prior_manifest['pdf_sha256']+'.json')
if not prior_archive.exists():
    prior_archive.write_text(json.dumps(prior_manifest,indent=2),encoding='utf-8')
render['previous_pdf_sha256']=prior_manifest['pdf_sha256']
(root/'audit/final_render/render_manifest.json').write_text(json.dumps(render,indent=2),encoding='utf-8')
log=(root/'build/final_cosmetic_console.txt').read_text(encoding='utf-8',errors='replace')
assert not re.search(r'Overfull \\[hv]box|Missing character|Undefined control|undefined references',log)
root_review={'pdf_sha256':sha,'pdf_pages':list(range(241,349)),'contact_sheets_reviewed':list(range(21,30)),'full_page_checks':[258,307,340,348],'status':'pass','notes':'No clipping, overlap, missing glyphs or unfinished prose. These pages remain pixel-identical after equation image cleanup.'}
(root/'audit/final_visual_qa_241_348.json').write_text(json.dumps(root_review,ensure_ascii=False,indent=2),encoding='utf-8')
first=root/'audit/final_visual_qa_001_120.json'
first_data=json.loads(first.read_text(encoding='utf-8'))
first_data.update({'revalidated_pdf_sha256':sha,'revalidation':'All page images1–120 remain pixel-identical through both subsequent equation asset repair renderings. See render_manifest.json and render_history_*.json.','final_pdf':'pdf/'+config['pdf_filename']})
first.write_text(json.dumps(first_data,ensure_ascii=False,indent=2),encoding='utf-8')
middle=root/'audit/final_visual_qa_121_240.json'
middle_data=json.loads(middle.read_text(encoding='utf-8'))
middle_data.update({'final_pdf_sha256':sha,'final_pdf_diff_review_pending':False,'final_pdf_diff_review_status':'passed','final_pdf_diff_review_root_pages':[151,157,160,161,176],'final_pdf_diff_review_peer_report':'audit/final_affected_page_qa_peer.json','status':'passed'})
middle.write_text(json.dumps(middle_data,ensure_ascii=False,indent=2),encoding='utf-8')
overall={'pdf_sha256':sha,'all_348_pages_rendered':True,'visual_status':'passed','unchanged_final_page_images':render['unchanged_rendered_pages'],'changed_final_page_images_reviewed':sorted(actual_changes),'final_review_root_pages':[151,157,160,161,176],'final_review_peer_pages':peer['pages'],'unresolved_internal_destinations':[],'source_pdf_sha256':hashlib.sha256((root/'source/original.pdf').read_bytes()).hexdigest(),'original_template_files_verified_identical':9}
(root/'audit/final_completion_audit.json').write_text(json.dumps(overall,ensure_ascii=False,indent=2),encoding='utf-8')
report=f'''翻訳と確認事項

書籍：Decoherence and the Quantum-to-Classical Transition
著者：Maximilian Schlosshauer
対象：添付の訂正第3刷（2008年）。原文PDF428ページ。
保存先：{config['destination']}
TeX：{config['tex_filename']}
PDF：pdf\\{config['pdf_filename']}（{audit['pdf_pages']}ページ）

翻訳範囲
序文、全9章、付録、脚注、図69点と全キャプション、表6点、参考文献523件、索引639項目、前後の原書掲載情報を収録。
原文にない導入、要約、訳者注、進捗説明は本文へ追加していない。
人名・固有名詞と所属機関は原則として原語の綴りを維持。
図中の英語ラベルは多くを原図のまま保持。第5章の表示数式は主に原文からのベクトル切り抜きを使用し、式番号5.1～5.205を保持。数式周囲の本文混入・端の欠けは修正し、独立点検済み。

テンプレート・表紙
C:\\Users\\false\\codex\\template を丸ごと保存し、元の9ファイルが変更されていないことをSHA-256で確認。
日本語題名を主題、その下に小さく英語原題。日付欄は日付だけ。
表紙の原著リンクは出版社ページ https://link.springer.com/book/10.1007/978-3-540-35775-9 。書籍のためタイトルにarXiv番号は記載していない。
番号なし見出しにも目次へのリンクを設定。

参考文献
523件すべてをBibTeXで処理。465件は照合したINSPIRE-HEPまたはCrossrefの公式エクスポートを使用し、不足する出版情報を確認のうえ補完。
同じ題名の別版、再録、書評、親書籍の記録を排除し、正確な刊行物・版の公式記録が得られなかった58件は、原文の書誌情報を省略しない適切な種類のBibTeXレコードとして保持。@miscへの置換なし。
取得元、採否、不一致、補完・修正の根拠、原文情報、公式エクスポート原本の所在は audit/matching_override.json と audit/bibliography_followup_report.txt に記録。
原文引用番号1～523と本文の対応順を保持。本文の引用1200箇所の文献番号の多重集合が原文と一致。
LuaLaTeX → BibTeX → LuaLaTeX2回で生成し、画像修正後の再生成でも相互参照とページ構成の安定を確認。BibTeX警告0件。

完成PDFの検証
文字欠落・はみ出し・未解決参照の警告なし。全ページを画像化し、分担目視確認。修正した数式画像は拡大確認。
本文・序文からの引用リンク{audit['citation_links']}箇所、参考文献の内部リンク先523件、本文原ページに対応する索引用リンク先379件を確認。
内部リンク{audit['internal_links']}件に未解決のリンク先なし。完成PDFにDOI・arXiv・出版社等への外部リンク{audit['external_links']}個のリンク注釈があることを確認。代表DOI・arXiv・出版社URLの到達先も確認。全外部サイトの将来の可用性を保証するものではない。
詳細：audit/final_pdf_audit.json、audit/final_external_links.json、audit/final_render/render_manifest.json、audit/final_visual_qa_*.json。
原文自体に誤記と思われる数式表記は勝手に訂正せず、章別の監査ファイルに記録。

PDF SHA-256：{sha}
'''
(root/'翻訳と確認事項.txt').write_text(report,encoding='utf-8')
print('Completion report saved. Final PDF:',audit['pdf_pages'],'pages, SHA-256',sha)
