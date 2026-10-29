# 書籍・学位論文の文献照合記録

照合日：2026年10月29日。対象は添付原文の参考文献番号1、3、22、24、25、31、32。

## INSPIRE-HEP の照合

著者と題名を組み合わせた追加検索の応答全文を `refNN_inspire_book_search.json` に保存した。実際のクエリURLと候補書誌は `books_inspire_summary.json` に記録している。

|番号|追加検索|結果|
|---|---|---|
|1|`t "Selected papers on noise"`|0件。原文の編者・出版社・年を保ち、公的図書館目録で照合。|
|3|`a Louisell and t radiation`|0件。1973年版を研究機関目録で照合。1990年の再版へ置換していない。|
|22|`a Feynman and a Hibbs and t quantum`|0件。CERN公式目録の1965年版に対応するキャッシュ済み公式BibTeXを取得。|
|24|`a Forster and t hydrodynamic`|0件。研究機関目録の1975年版と照合。|
|25|`a Morse and a Feshbach and t methods`|0件。CERN公式目録の1953年版と照合。原文の引用箇所 sect. 3.2 を保持。|
|31|`a Caldeira and date 1980 and document_type thesis`|0件。原文に題名が示されておらず、題名を推測して補っていない。|
|32|`a Landau and a Lifshitz and t statistical`|1件、1411177。ただし1980年Butterworth-Heinemann版であり、原文の1969年Pergamon版とは異なるため採用しなかった。|

原文と一致する INSPIRE 書籍レコードは取得できなかったため、INSPIRE の別版や別論文の BibTeX を流用していない。

## 採用した公開書誌情報

- **1**：Finland National Repository Library / Finna の [vaari.1650905](https://www.finna.fi/Record/vaari.1650905)。題名、Nelson Wax 編、Dover、New York、1954年が原文と一致する。書誌情報は検索サービスが返した公的目録の索引済み本文で確認した。直接取得はHTTP403で失敗した。
- **3**：CNRS Grenoble 図書館の [record 7587](https://biblio.neel.cnrs.fr/index.php?id=7587&lang_sel=en_UK&lvl=notice_display)。Louisell、題名、John Wiley & Sons、New York、1973年が一致する。検索サービスが返した目録本文で確認した。直接取得は証明書の検証エラーとなった。
- **22**：CERN Document Server [record 100771](https://cds.cern.ch/record/100771)、[公式BibTeX export](https://cds.cern.ch/record/100771/export/hx)。検索サービスが返した公式exportの索引済み本文を `ref22_cern_cached_export.bib` にそのまま保存し、採用ファイルでは引用キーだけを `ref22` に変更した。直接取得はAnubis確認画面であり、`ref22_catalog_source.html` はその応答記録であってBibTeXではない。
- **24**：CNRS Grenoble 図書館の [record 3026](https://biblio.neel.cnrs.fr/index.php?id=3026&lvl=notice_display)。Forster、題名、W.A. Benjamin、New York、1975年が一致する。検索サービスが返した目録本文で確認した。直接取得は証明書の検証エラーとなった。
- **25**：CERN Document Server [record 102245](https://cds.cern.ch/record/102245?ln=en)。Morse、Feshbach、題名、McGraw-Hill、New York、1953年を検索サービスが返した公式目録本文で確認した。直接取得はAnubis確認画面であり、`ref25_catalog_source.html` はその応答記録である。公式BibTeX exportの実データは取得できなかったので、原文と確認済み目録の情報から `@book` として記述した。
- **31**：原文にある A.O. Caldeira、Ph.D. Thesis、University of Sussex、1980、unpublished を保持した。文献型を `@phdthesis`、`title={}` とし、様式が出力する博士論文の記述を用いる。原文の一般的な文献種別を実題名として重ねて表示しない。対応する公開書誌レコードと実題名は確認できなかったため、未確認のURL・DOI・題名は加えていない。BibTeXの `empty title in ref31` はこの既知の原文情報欠落に由来する意図的な警告であり、未解決の本文参照ではない。
- **32**：University of Patras 図書館 [record 120557](https://bkp.upatras.gr/Record/120557/Details)。Landau・Lifshitz、Statistical Physics、Pergamon、1969年、第2改訂増補版という書誌を検索サービスが返した大学目録本文で確認した。目録の出版地はOxford、原文表記はLondonである。採用BibTeXでは原文のLondonと引用ページ393を保持した。1980年版のINSPIRE1411177は不採用。直接取得は接続タイムアウトとなった。

`books_catalog_downloads.json` は直接取得結果の記録である。上記の目録本文は検索サービスの索引結果で照合しており、失敗した直接ダウンロードを成功扱いにはしていない。証明書検証やアクセス制限の回避は行っていない。
