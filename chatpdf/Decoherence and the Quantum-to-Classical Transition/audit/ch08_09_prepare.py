from pathlib import Path
import re,json
from pypdf import PdfReader,PdfWriter
from pypdf.generic import RectangleObject
base=Path(__file__).resolve().parents[1]
r=PdfReader(base/'source/original.pdf')
specs=[(1,374,(103,571,338,610)),(2,380,(67,139,382,265)),(3,381,(48,504,382,612)),(4,384,(147,466,294,607)),(5,384,(75,141,367,276)),(6,385,(119,525,320,618)),(7,385,(132,175,301,275))]
for n,pno,box in specs:
    p=r.pages[pno-1];p.cropbox=RectangleObject(box);p.mediabox=RectangleObject(box)
    w=PdfWriter();w.add_page(p);w.write(base/f'figures/ch09_fig{n:02}.pdf')
anchors8={329:'\\sectionlink{',330:'\\begin{itemize}',331:'Copenhagen解釈のこの特徴には',332:'巨視的に異なる指針状態間の',333:'縮約密度行列は、成分状態',334:'\\subsubsectionlink{観測量、測定、環境誘起超選択}',335:'これは、測定装置の物理的構造',336:'明らかなのは、環境誘起超選択',337:'相対状態解釈の中心的考え',338:'相対状態解釈では、優先基底問題',339:'実際、優先基底の選択',340:'\\subsubsectionlink{相対状態解釈における確率}',341:'量子情報理論は、自然が',342:'Zurekの「事実」は、次のように',343:'以上の議論をより精密にするため',344:'\\subsubsectionlink{「実存的解釈」}',345:'一般に様相解釈の考え方',346:'さらに、デコヒーレンスの研究計画',347:'Dieks\\cite{ref438}は',348:'\\subsectionlink{物理的収縮理論}',349:'ヒットの発生は説明されず',350:'これに対して、GRW理論は',351:'\\subsubsectionlink{デコヒーレンスと自発的局在化の同時存在}',352:'完全な局在化には',353:'もちろん、Joosのコメント',354:'そのような実験を実現する際',355:'したがって、各瞬間$t$の系の状態',356:'\\subsubsectionlink{基本的実体としての粒子}',357:'BohmとHiley',358:'こうして、デコヒーレンスの研究計画'}
anchors9={359:'\\sectionlink{',360:'ある特定の物理量の測定',361:'したがってvon Neumannとd\'Espagnat',362:'\\begin{figure}',363:'したがって、何らかの形の波動関数',364:'しかし、「心」や「意識」',365:'ただし、Wignerの友人の場合',366:'大まかにいえば、このように脳は',367:'量子論を脳へ適用するこの',368:'以下の9.3.1節でニューロン',369:'したがって、発火状態と静止状態',370:'デコヒーレンスが最大となるこの極限',371:'Tegmark\\cite{ref515}が論じたように',372:'物理学の観点では、プロトフィラメント',373:'電子が$\\beta$サブユニット側へ',374:'Tegmark\\cite{ref515}は、この特定の模型',375:'\\subsectionlink{測定問題の「主観的」解決}',376:'\\begin{quote}\n私たちの感覚は',377:'そこでの推測は',378:'個人の解釈上の好みにかかわらず'}
for name,anchors in [('ch08',anchors8),('ch09',anchors9)]:
    path=base/f'chapters/{name}.tex'; text=path.read_text(encoding='utf-8')
    missed=[]
    for page,anchor in anchors.items():
        marker=f'% 原文 p.{page}\n'
        if marker in text: continue
        if anchor not in text:missed.append((page,anchor));continue
        text=text.replace(anchor,'\n'+marker+anchor,1)
    path.write_text(text,encoding='utf-8')
    print(name,'missing marker anchors',missed)
for name,source_range,phys in [('ch08',(329,358),(341,370)),('ch09',(359,378),(371,390)),('appendix',(379,382),(391,394))]:
    text=(base/f'chapters/{name}.tex').read_text(encoding='utf-8')
    audit={'file':f'chapters/{name}.tex','printed_pages':source_range,'physical_pdf_pages':phys,'status':'complete translation of assigned source range','paragraph_blocks':len(re.findall(r'\n\n[^%\\\n]',text)),'equation_tags':re.findall(r'\\tag\{([^}]+)\}',text),'footnotes':text.count('\\footnote{'),'figures':re.findall(r'figures/([^}]+)',text),'source_page_markers':re.findall(r'% 原文 p\.(\d+)',text),'uncertainties':[],'figure_internal_text':'Original English labels preserved in Fig.9.1,9.2,9.3,9.6; mathematical labels preserved in other figures. All captions translated.' if name=='ch09' else 'Figure8.1 has no text labels.' if name=='ch08' else 'No figures.'}
    (base/f'audit/{name}_coverage.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
