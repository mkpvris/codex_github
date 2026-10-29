# 参考文献の取得・照合記録

照合日：2026年10月29日。対象原文：A. O. Caldeira and A. J. Leggett, *Path integral approach to quantum Brownian motion*, Physica A **121** (1983) 587–616。添付PDF最終ページの参考文献[1]–[38]を対象とした。

## 取得方法と引用番号

`ref.bib` には38件を収録した。本文の引用キーは、原文の番号に対応する `ref01`–`ref38` とした。19件は題名・著者・掲載誌・巻・開始ページ・年を照合できた INSPIRE-HEP の公式BibTeXを基礎に用いた。生の公式エクスポートは `refNN_official.bib`、対応するレコード全文は `refNN_inspire.json` に保存し、原本を変更していない。採用時は引用キーを変更した。原文にある刊行情報を落とさないための補充は、下記の18、26、27のみである。27の公式出力にある `month="1"` はプレプリントの日付なので、最終掲載誌の刊行月と誤認されないよう採用BibTeXでは除き、生の公式出力にはそのまま保持した。

INSPIRE-HEP で一致するレコードが見つからなかった文献は、著者・題名検索に加え、DOIのある論文についてはDOI検索も行い、Crossrefの出版社登録情報、出版社・学会・公的図書館等の情報で照合した。検索応答、DOIで取得したCrossrefの応答全文を保存した。種類に従って `@book`、`@article`、`@incollection`、`@phdthesis` として記述し、便宜的な `@misc` への置換は行っていない。

書籍の詳細な照合・取得失敗記録は [books_acquisition_notes.md](books_acquisition_notes.md) を参照。原文に題名のない学位論文[31]については、実際の題名と対応する公開書誌レコードを確認できなかった。推測した題名、DOI、URLは加えていない。

## 文献別の取得元

「公式」は INSPIRE-HEP 公式BibTeX、「代替」は同サイトで一致レコードを取得できなかったことを意味する。DOIのリンクは実際に取得した出版社登録情報のDOIである。

| 原文番号／キー | 取得元 | 照合結果・採用情報 |
|---|---|---|
| 1／ref01 | 代替：[Finna公的目録](https://www.finna.fi/Record/vaari.1650905) | Nelson Wax編、Selected Papers on Noise and Stochastic Processes、Dover、New York、1954。原文の版を保持。 |
| 2／ref02 | 公式：[INSPIRE 2736257](https://inspirehep.net/literature/2736257) | E. Kanai、Prog. Theor. Phys. 3 (1948) 440–442。DOI 10.1143/ptp/3.4.440。 |
| 3／ref03 | 代替：[CNRS目録7587](https://biblio.neel.cnrs.fr/index.php?id=7587&lang_sel=en_UK&lvl=notice_display) | W. H. Louisell、Quantum Statistical Properties of Radiation、Wiley、New York、1973。後年の再版へ置換していない。 |
| 4／ref04 | 代替：[出版社登録DOI](https://doi.org/10.1063/1.1678812) | M. D. Kostin、On the Schrödinger-Langevin Equation、J. Chem. Phys. 57 (1972) 3589–3591。 |
| 5／ref05 | 公式：[INSPIRE 50055](https://inspirehep.net/literature/50055) | E. Nelson、Phys. Rev. 150 (1966) 1079–1085。 |
| 6／ref06 | 公式：[INSPIRE 129193](https://inspirehep.net/literature/129193) | K. Yasue、Annals Phys. 114 (1978) 479。公式エクスポートのページ情報を保持。 |
| 7／ref07 | 代替：[APS原著ページ](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.16.2126) | H. Dekker、Quantization of the linearly damped harmonic oscillator、Phys. Rev. A 16 (1977) **2126–2134**。原文の2116は開始ページの誤記と照合。 |
| 8／ref08 | 公式：[INSPIRE 47054](https://inspirehep.net/literature/47054) | I. R. Senitzky、Phys. Rev. 119 (1960) 670–679。 |
| 9／ref09 | 公式：[INSPIRE 2736253](https://inspirehep.net/literature/2736253) | H. Mori、Prog. Theor. Phys. 33 (1965) 423–455。 |
| 10／ref10 | 公式：[INSPIRE 2735417](https://inspirehep.net/literature/2735417) | R. Zwanzig、J. Chem. Phys. 33 (1960) 1338。 |
| 11／ref11 | 公式：[INSPIRE 2736294](https://inspirehep.net/literature/2736294) | S. Nakajima、Prog. Theor. Phys. 20 (1958) 948–959。 |
| 12／ref12 | 公式：[INSPIRE 107282](https://inspirehep.net/literature/107282) | H. Haken、Rev. Mod. Phys. 47 (1975) 67–121。 |
| 13／ref13 | 代替：[Springer章ページ](https://link.springer.com/chapter/10.1007/BFb0044957) | F. Haake、Statistical treatment of open systems by generalized master equations、Quantum Statistics in Optics and Solid-State Physics、Springer Tracts in Modern Physics 66、Berlin、1973、98–168。 |
| 14／ref14 | 公式：[INSPIRE 163878](https://inspirehep.net/literature/163878) | R. H. Koch、D. J. Van Harlingen、John Clarke、Phys. Rev. Lett. 45 (1980) 2132–2135。 |
| 15／ref15 | 代替：[出版社登録DOI](https://doi.org/10.1103/PhysRevLett.46.1) | R. Benguria、M. Kac、Quantum Langevin Equation、Phys. Rev. Lett. 46 (1981) 1–4。 |
| 16／ref16 | 代替：[出版社登録DOI](https://doi.org/10.1063/1.1704304) | G. W. Ford、M. Kac、P. Mazur、Statistical Mechanics of Assemblies of Coupled Oscillators、J. Math. Phys. 6 (1965) 504–515。1966年の再録は採用していない。 |
| 17／ref17 | 代替：[出版社登録DOI](https://doi.org/10.1016/0378-4371(78)90194-2) | G. Iche、P. Nozieres、Quantum Brownian motion of a heavy particle: An adiabatic expansion、Physica A 91 (1978) 485–506。 |
| 18／ref18 | 公式：[INSPIRE 117200](https://inspirehep.net/literature/117200) | E. B. Davies、Quantum Theory of Open Systems、1976。公式出力にないAcademic Press、New Yorkを原文から補充。レコードの自由記述にはLondonがあるが、採用時は原文の出版地を保持。 |
| 19／ref19 | 公式：[INSPIRE 9385](https://inspirehep.net/literature/9385) | J. Schwinger、J. Math. Phys. 2 (1961) 407–432。 |
| 20／ref20 | 代替：[出版社登録DOI](https://doi.org/10.1007/BF01008729) | R. Zwanzig、Nonlinear generalized Langevin equations、J. Stat. Phys. 9 (1973) 215–220。 |
| 21／ref21 | 公式：[INSPIRE 176413](https://inspirehep.net/literature/176413) | A. O. Caldeira、A. J. Leggett、Quantum tunneling in a dissipative system、Annals Phys. 149 (1983) 374–456。原文では「to appear in Annals of Physics」と記載されていた。採用文献には確認済みの正式な刊行情報を用いた。 |
| 22／ref22 | 代替：[CERN公式目録100771](https://cds.cern.ch/record/100771) | R. P. Feynman、A. R. Hibbs、Quantum mechanics and path integrals、McGraw-Hill、New York、1965。公式exportの索引済み本文を取得。 |
| 23／ref23 | 公式：[INSPIRE 9391](https://inspirehep.net/literature/9391) | R. P. Feynman、F. L. Vernon、Annals Phys. 24 (1963) 118–173。2000年の再録ではなく1963年の公式エクスポート情報を採用。 |
| 24／ref24 | 代替：[CNRS目録3026](https://biblio.neel.cnrs.fr/index.php?id=3026&lvl=notice_display) | D. Forster、Hydrodynamic Fluctuations, Broken Symmetry, and Correlation Functions、Benjamin、New York、1975。 |
| 25／ref25 | 代替：[CERN公式目録102245](https://cds.cern.ch/record/102245) | P. M. Morse、H. Feshbach、Methods of Theoretical Physics、McGraw-Hill、New York、1953。原文のsect. 3.2を保持。 |
| 26／ref26 | 公式：[INSPIRE 3567](https://inspirehep.net/literature/3567) | L. V. Keldysh、Sov. Phys. JETP 20 (1965) 1018–1026。原文のKjeldyshは同著者の表記。公式DOI 10.1142/9789811279461_0007は後年の論文集収録版に対応するため保持し、レコードにあるJETP原著PDFのURLも補充した。 |
| 27／ref27 | 公式：[INSPIRE 4884](https://inspirehep.net/literature/4884)、[学会公開原著](https://www.sbfisica.org.br/bjp/download/v07/v07a19.pdf) | M. C. Nemes、A. F. R. de Toledo Piza、A Quantum Phenomenology of Viscosity。公式出力はプレプリントIFUSP/P-89のみ。題名と著者が一致するSBF原著を照合し、Revista Brasileira de Física 7, no. 2 (1977) 261–270とURLを補充。プレプリントの月1は最終刊行月として用いない。 |
| 28／ref28 | 代替：[出版社登録DOI](https://doi.org/10.1088/0305-4470/1/4/302) | G. J. Papadopoulos、Functional integrals in Brownian motion、J. Phys. A: General Phys. 1 (1968) **431–446**。原文の413は開始ページの誤記と照合。 |
| 29／ref29 | 公式：[INSPIRE 3198](https://inspirehep.net/literature/3198) | E. Wigner、Phys. Rev. 40 (1932) 749–760。 |
| 30／ref30 | 公式：[INSPIRE 128975](https://inspirehep.net/literature/128975) | M. V. Berry、Phil. Trans. Roy. Soc. Lond. A 287 (1977) 237–271。 |
| 31／ref31 | 原文の書誌記述 | A. O. Caldeira、Ph.D. Thesis、University of Sussex、1980、unpublished。実際の題名と公開書誌レコードは未確認。`@phdthesis`、`title={}` とし、論文種別の表示を実題名として重複させない。 |
| 32／ref32 | 代替：[University of Patras目録120557](https://bkp.upatras.gr/Record/120557/Details) | L. D. Landau、E. M. Lifshitz、Statistical Physics、Pergamon、1969。原文のLondon、p. 393を保持。INSPIRE 1411177は1980年版なので不採用。 |
| 33／ref33 | 公式：[INSPIRE 134075](https://inspirehep.net/literature/134075) | Y. Tikochinsky、J. Math. Phys. 19 (1978) 888–891。 |
| 34／ref34 | 代替：[出版社登録DOI](https://doi.org/10.1111/j.2164-0947.1977.tb02946.x) | H. Feshbach、Y. Tikochinsky、Quantization of the damped harmonic oscillator、Trans. New York Acad. Sci. 38 (1977) 44–53。原文のA Festschrift for I. I. Rabi、Series 2も保持。 |
| 35／ref35 | 代替：[出版社登録DOI](https://doi.org/10.1016/0370-1573(81)90033-8) | H. Dekker、Classical and quantum mechanics of the damped harmonic oscillator、Phys. Rep. 80 (1981) 1–110。 |
| 36／ref36 | 代替：[出版社原著ページ](https://www.sciencedirect.com/science/article/pii/0378437179900578) | H. Dekker、On the phase space quantization of the linearly damped harmonic oscillator、Physica A 95 (1979) 311–323。 |
| 37／ref37 | 公式：[INSPIRE 73218](https://inspirehep.net/literature/73218) | G. S. Agarwal、Phys. Rev. A 4 (1971) 739–747。 |
| 38／ref38 | 代替：[Math-Net原著書誌](https://www.mathnet.ru/php/archive.phtml?jrnid=tmf&option_lang=rus&paperid=3327&wshow=paper)、[Springer翻訳版](https://link.springer.com/article/10.1007/BF01051242) | I. R. Svin'in、Quantum description of Brownian motion in an external field。原文のロシア語誌27 (1976) 270–278を保持。英語版はTheor. Math. Phys. 27 (1976) 478–483で、DOIはこの翻訳版に対応する。 |

## 取得・照合の限界

- 参考文献[31]の実題名と対応公開レコードは確認できなかった。原文にある書誌情報のみを保持し、正しい文献型 `@phdthesis` の題名欄を空にした。BibTeXの `empty title in ref31` はこの既知の欠落に由来する意図的な警告である。架空の題名や二重の博士論文表記を生じさせず、本文引用の未解決を意味するものでもない。
- 一致するINSPIRE公式BibTeXを取得できなかった番号は、1、3、4、7、13、15、16、17、20、22、24、25、28、31、32、34、35、36、38である。これらをINSPIRE取得済みとは扱っていない。
- 書籍の一部の目録は検索サービスが返した公的目録本文で確認した。直接取得時の403、Anubis確認画面、証明書検証失敗、タイムアウトは `books_acquisition_notes.md` と `books_catalog_downloads.json` に区別して記録した。
- 文献27の学会PDFはWeb閲覧ツールで本文・著者・巻・年を確認できたが、Pythonからの直接保存は証明書検証に失敗した。失敗したダウンロードを取得成功とは記録していない。
- この文書は取得元と原文との相違を記録する作業記録であり、翻訳本文に独自の章・訳者注を加えるものではない。最終PDFの引用リンク検証は、コンパイル後の別の検証結果による。
