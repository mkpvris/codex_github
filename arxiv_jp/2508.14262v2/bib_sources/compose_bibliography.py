import pathlib,json,re,hashlib
from collect_bibliography import OUT,BASE,rows

def keyreplace(s,key):
    return re.sub(r'(@\w+\s*\{)\s*[^,]+,',lambda m:m.group(1)+key+',',s,count=1)
def addfields(s,fields):
    fields=dict(fields)
    for k,v in list(fields.items()):
        pattern=r'(?i)(\b'+re.escape(k)+r'\s*=\s*)(?:"[^"\n]*"|\{[^{}\n]*\})'
        if re.search(pattern,s):
            s=re.sub(pattern,lambda m:m.group(1)+'{'+v+'}',s,count=1)
            fields.pop(k)
    if not fields: return s
    p=s.rfind('}')
    prefix=s[:p].rstrip()
    if not prefix.endswith(','): prefix+=','
    return prefix+'\n'+''.join('    '+k+' = {'+v+'},\n' for k,v in fields.items())+'}\n'
texts=[]; record=[]
for row in rows:
    k=row['key']; logpath=OUT/(k+'_collection.json')
    log=json.loads(logpath.read_text(encoding='utf-8')) if logpath.exists() else {}
    extras={}; match=''; discarded=''
    if k=='BP2002':
        source=OUT/'BP2002_verified_inspire.bib'; bib=source.read_text(encoding='utf-8')
        url='https://inspirehep.net/api/literature/609205?format=bibtex'
        extras={'publisher':'Oxford University Press'}
        match='著者 Breuer / Petruccione、完全一致題名、2002年（pubinfo_freetextもOxford 2002）を照合。公式BibTeXにない出版社のみ原文BBLから補完。'
        discarded='初回検索のrecord 2155295は別著者・別題名で不採用。record 2702141は2007年版のため不採用。'
        method='INSPIRE-HEP公式BibTeX'
    elif k=='Weiss2011':
        source=BASE/'source/main.bbl'
        bib='@book{Weiss2011,\n    author = {Weiss, U.},\n    title = {Quantum Dissipative Systems},\n    publisher = {World Scientific},\n    year = {2011}\n}\n'
        url='source/main.bbl'
        match='原文の著者・題名・出版社・2011年を全項目保持してbookとして復元。版の記載は原文にないため付加しない。'
        discarded='INSPIREの同名著書record 2111850は2021年版（DOI 10.1142/12402）のため不採用。2011年に一致する公式exportを特定できなかった。'
        method='原論文の完全な書籍書誌（INSPIREの同名別版は不採用）'
    elif k in ['Note1','Note2','SuppMat']:
        source=BASE/'source/main.bbl'; url='source/main.bbl'
        notes={
            'SuppMat':r'式~(6) の導出とデコヒーレンス汎関数 $S_r[\Delta X]$ の端点項の評価の詳細については、補足資料を参照。',
            'Note1':r"ここで $\mathcal{S}'(\mathbb{R})$ は、$\mathbb{R}$ 上の緩増加超関数の空間、すなわち Schwartz 関数の空間 $\mathcal{S}(\mathbb{R})$ の連続双対を表す。",
            'Note2':r'$H_{\rm eff}$ の添字「eff」は、式~\eqref{eq:me} の微視的導出において、Hamiltonian の寄与に $\hat{H}_S$ に含まれない追加の Lamb シフトや振動数の繰り込み項が含まれうることを示す。'
        }
        bib='@misc{'+k+',\n    note = {'+notes[k]+'}'
        if k=='SuppMat': bib+=',\n    url = {https://arxiv.org/pdf/2508.14262v2#page=7}'
        bib+='\n}\n'
        method='原論文の注記・同梱補足資料の参照'
        match='書誌論文ではなく原文の注記なのでmisc型を使用し、注記全文を日本語化。引用順・キーを保持。'
        if k=='SuppMat': match+=' 補足資料の開始は原文PDFの7ページ目であることを確認し、同じv2のPDFの#page=7へリンク。'
    elif (OUT/(k+'_inspire.bib')).exists() and k not in ['Kleinert2009']:
        source=OUT/(k+'_inspire.bib'); bib=source.read_text(encoding='utf-8')
        url=log['inspire_bib_url']; method='INSPIRE-HEP公式BibTeX'
        if row['doi']:
            dois=[x['value'].lower() for x in log.get('inspire_dois',[])]
            assert row['doi'].lower() in dois,(k,'DOI mismatch')
            match='原文のDOI '+row['doi']+' と公式レコードのDOIが一致。著者・雑誌・巻・年も原文BBLと照合。'
        elif row['arxiv']:
            assert row['arxiv'] in [x['value'] for x in log.get('inspire_arxiv',[])]
            match='原文のarXiv番号 '+row['arxiv']+' が一致。Xu / Vadimov / Krug / Stockburger / Ankerhold、2023年と照合。'
        elif k=='Homa2019':
            assert log['inspire_id']=='3047998'
            match='著者 Homa / Bernád / Lisztes、Eur. Phys. J. D 73, 53 (2019) が一致。公式レコードでDOIとarXiv番号も確認。'
        else: raise ValueError(k)
        if k=='Aurell2020':
            extras={'journal':'Journal of Physics A: Mathematical and Theoretical','volume':'53','number':'27','pages':'275303','year':'2020','month':'6'}
            match+=' INSPIRE exportはpreprint書誌で雑誌・巻・論文番号が欠落し、year=2019/month=12だった。原文BBLの出版書誌とDOI一致Crossref公式レコードを照合し、journal/volume/number/pagesを補完、出版年2020・オンライン出版月6に訂正。公式export自体は変更せず別保存。'
    else:
        source=OUT/(k+'_crossref.bib'); bib=source.read_text(encoding='utf-8')
        url=log['crossref_bib_url']; method='Crossref公式BibTeX'
        c=json.loads((OUT/(k+'_crossref.json')).read_text(encoding='utf-8'))['message']
        assert c['DOI'].lower()==row['doi'].lower(),(k,'Crossref DOI mismatch')
        match='原文のDOI '+row['doi']+' とCrossref公式レコードのDOIが一致。著者・雑誌・巻・年も原文BBLと照合。INSPIREはDOI・題名の両検索で該当なし。'
        if k=='Kleinert2009':
            match='原文のDOI 10.1142/7305、著者Hagen Kleinert、完全一致題名、World Scientific、2009年が一致。'
            discarded='INSPIRE record 656613は2004年版のため不採用。2009年版の公式exportは特定できなかった。'
        if k=='Wilner2015':
            extras['pages']='195143'
            match+=' Crossref BibTeXで欠落している論文番号195143を原文BBLから補完。'
        if k=='AlickiLendi2007':
            extras={'title':'Quantum Dynamical Semigroups and Applications','author':'Alicki, R. and Lendi, K.'}
            match+=' Crossref JSONには完全一致題名があるがBibTeXのtitle/authorが欠落するため、題名を公式JSON、著者を原文BBLから補完。'
            discarded='題名の二次INSPIRE検索で得たrecord 2976737は別著作のため不採用。Springerページはanti-bot画面となったため独立の著者照合根拠には使用しない。'
    bib=keyreplace(bib,k)
    if extras: bib=addfields(bib,extras)
    # Preserve official content otherwise; Unicode page ranges are converted to standard BibTeX ranges only for Crossref-derived entries.
    if method=='Crossref公式BibTeX': bib=bib.replace('–','--')
    texts.append('% ['+str(row['number'])+'] '+method+'; '+url+'\n'+bib.strip()+'\n')
    rec=dict(number=row['number'],key=k,method=method,source=str(source.relative_to(BASE)),url=url,matching=match,rejected_or_unavailable=discarded,added_fields=extras,sha256=hashlib.sha256(source.read_bytes()).hexdigest(),inspire_queries=log.get('queries',[]))
    if k=='Aurell2020': rec['additional_bibliographic_source']='https://api.crossref.org/works/10.1088%2F1751-8121%2Fab9274'
    secondary=OUT/(k+'_verification.json')
    if secondary.exists(): rec['inspire_secondary_query']=json.loads(secondary.read_text(encoding='utf-8')).get('secondary_query_url','')
    record.append(rec)
(BASE/'ref.bib').write_text('@string{sept = "September"}\n\n'+'\n'.join(texts),encoding='utf-8')
(BASE/'reference_order.tex').write_text('% 原文 main.bbl の引用順（注記2件・補足参照を含む）\n\\nocite{'+','.join(r['key'] for r in rows)+'}\n',encoding='utf-8')
(OUT/'verified_selection.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
intro='参考文献取得・照合記録\n対象: arXiv:2508.14262v2 / 提供PDFに対応する原稿 main.bbl\n取得日: 2026-10-28 (Asia/Tokyo)\n\n原文49項目の順序・引用キーを保持。最初の引用より前にreference_order.texを入力する。\n書誌にINSPIRE公式BibTeXがある場合はその全フィールドを原則保持。公式BibTeXが欠落させた原文情報のみ補完し、preprint年と出版年が異なる場合はDOI一致の公式出版書誌に合わせて出典付き訂正。補完・訂正項目を下記に記録し、取得した公式export自体は別保存。Crossrefのページ範囲のen dashはBibTeX標準の--に正規化。\n原文BBLのCaldeiraLeggettAの破損DOIは10.1016/0378-4371(83)90013-4に修復。複数文献のdoi.org二重付加は正しい公式DOIに統一。\nNote1=[28]、Note2=[36]は原文の参考文献欄に置かれた注記。SuppMat=[27]は同PDFに収録された補足資料の案内。これら3項目のmisc型は論文書誌の置換ではない。\n\n集計: INSPIRE-HEP公式BibTeX '+str(sum(r['method']=='INSPIRE-HEP公式BibTeX' for r in record))+'件、Crossref公式BibTeX '+str(sum(r['method']=='Crossref公式BibTeX' for r in record))+'件、原文の書籍書誌1件、原文注記・補足参照3件。\n未確定: Weiss2011は原文年2011に一致する版の公式BibTeXを特定できず、原文の書誌情報を省略せず保持した。書誌項目自体の欠落は0件。\n\n'
out=[intro]
for r in record:
    out.append('['+str(r['number'])+'] '+r['key']+'\n  採用: '+r['method']+'\n  取得元: '+r['url']+'\n  補助取得元: '+r.get('additional_bibliographic_source','なし')+'\n  保存: '+r['source']+'\n  照合: '+r['matching']+'\n  検索: '+' ; '.join(r['inspire_queries']+[r.get('inspire_secondary_query','')])+'\n  補完・訂正: '+json.dumps(r['added_fields'],ensure_ascii=False)+'\n  不採用・未取得: '+(r['rejected_or_unavailable'] or 'なし')+'\n  取得データSHA256: '+r['sha256']+'\n')
(BASE/'BIBLIOGRAPHY_SOURCES.txt').write_text('\n'.join(out),encoding='utf-8')
print(intro)
