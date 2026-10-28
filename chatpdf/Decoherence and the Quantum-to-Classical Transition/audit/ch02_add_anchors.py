from pathlib import Path
root=Path(__file__).resolve().parents[1]
items={
'01':{13:'本章の前半では',14:'続く2.7、',15:'もちろん古典物理学でも',16:'量子状態のこの壊れやすさ',17:'よく知られているように、Einstein',18:'さらにKochenとSpecker',19:'しかしこの解釈は、'},
'02':{20:r'\subsectionlink{重ね合わせ原理}',21:'重ね合わせを、その成分状態',22:r'\begin{figure}',23:'入射原子を、',24:'このように、重ね合わせの成分状態',25:r'\begin{equation}\begin{split}\varrho(x)',26:r'\begin{equation}\lvert\Psi\rangle=\frac1{\sqrt2}(\lvert g\rangle',27:'第1章の導入ですでに述べたように',28:'これは確かに「現象を救う」'},
'03':{29:'純粋なもつれ状態の例として',30:'量子もつれの特異な特徴は',31:'そのため、最初の測定という行為',32:'\\begin{quote}\n知識の一部が',33:'次に状態(2.9)について'},
'04':{34:r'\subsubsectionlink{純粋状態の密度行列とトレース演算}',35:'次に「$\\operatorname{Tr}$」',36:r'\begin{equation}\langle\hat O\rangle=\operatorname{Tr}(\hat\rho\hat O).\tag{2.17}',37:r'\begin{figure}',38:'混合状態で記述される系について行った',39:r'\begin{equation}\operatorname{Tr}\hat\rho=\sum_i'},
'05':{40:r'\begin{equation}\hat\rho^2=\sum_{ij}',41:r'\begin{equation}\varsigma=\sum',42:'これを説明するため、混合状態の密度行列',43:r'\subsubsectionlink{混合状態の密度行列と物理的集団}',44:r'\begin{equation}\langle\hat O\rangle=\sum_{i=1}^M p_i\operatorname{Tr}'},
'06':{45:r'\paragraph{デコヒーレンスとの関係}',46:'系$\\mathcal A$だけに作用する観測可能量',47:r'\paragraph{干渉の局所的測定可能性と識別可能性}',48:'たとえば、状態$\\lvert b_1',49:'そのため、縮約密度行列が混合状態の密度行列に形式上似ている'},
'07':{50:'上に示したように、測定問題',51:'その名前にもかかわらず、von Neumann測定方式',52:r'\begin{figure}',53:r'\subsubsectionlink{優先基底の問題}',54:'係数についてのこの条件が成り立たないと',55:'このような「優先観測可能量」'},
}
for file,spec in items.items():
    p=root/'chapters'/f'ch02_{file}.tex'
    text=p.read_text(encoding='utf-8-sig')
    for n,needle in spec.items():
        marker=f'\\label{{srcpage:{n}}}'
        if marker in text: continue
        assert needle in text,(file,n,needle)
        text=text.replace(needle,f'% 原文 p.{n}\n\\hypertarget{{srcpage:{n}}}{{}}{marker}\n'+needle,1)
    p.write_text(text,encoding='utf-8')
print('Inserted source-page anchors13-55')
