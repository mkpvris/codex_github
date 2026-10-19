from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
for path in (ROOT/'sections').glob('*.tex'):
 s=path.read_text(encoding='utf-8')
 for old,new in [('捕捉インフレーション','トラップ型インフレーション'),('温暖インフレーション','温かいインフレーション'),('優先される時計','優先的な時計'),('外的曲率','外部曲率'),('デカップリング','分離'),('応力テンソル','エネルギー運動量テンソル'),('有効場の理論','有効場理論')]:s=s.replace(old,new)
 # Two plot pairs described as top/bottom in the original, kept in that layout.
 for a,b in [('PowvsGamma','Powvsz0CG'),('deltag00Noloc4','deltag00Noloc40')]:
  old=r'\includegraphics[width=8.5cm]{'+a+'}\n'+r'\includegraphics[width=8.5cm]{'+b+'}'
  new=r'\centering\includegraphics[width=8.5cm]{'+a+r'}\par\smallskip'+'\n'+r'\includegraphics[width=8.5cm]{'+b+'}'
  s=s.replace(old,new)
 if path.name=='appendices.tex':
  s=s.replace(r'上：$\Gamma_\chi=100 H$（場合I）、下：$\Gamma_\chi=1000 H$（場合II）',r'左：$\Gamma_\chi=100 H$（場合I）、右：$\Gamma_\chi=1000 H$（場合II）')
  s=s.replace(r'\includegraphics[width=8.5cm]{Greengamma}',r'\centering\includegraphics[width=8.5cm]{Greengamma}')
  s=s.replace(r'\includegraphics[width=.48\linewidth]{Greengammasqrt}',r'\centering\includegraphics[width=.48\linewidth]{Greengammasqrt}')
  s=s.replace(r'\includegraphics[width=.48\linewidth]{TrapdecayCuadgama100HFin}',r'\centering\includegraphics[width=.48\linewidth]{TrapdecayCuadgama100HFin}')
 # Supply explicit, meaningful bookmark text without changing printed mathematics.
 mapping={
  r'$\cal O$の役割':'Oの役割',
  r'$\pi$の相互作用項':'πの相互作用項',
  r'$\calo\delta g^{00}$':'O δg⁰⁰',
  r'$f(t)\calo$ I：線形応答':'f(t)O I：線形応答',
  r'$f(t)\calo$ II：非線形応答':'f(t)O II：非線形応答',
  r'局所的なトラップ型インフレーション：$f(t)\calo\to\sum_i(\phi-\phi_i)^2\chi_i^2+\calL(\chi_i)$':'局所的なトラップ型インフレーション：f(t)O → Σᵢ(φ−φᵢ)²χᵢ² + L(χᵢ)',
  r'$\hat\calo\delta K^{\mu}_{\mu}$についての考察':'Ô δKについての考察',
  r'$ f(t)\calo_1$と$\calo_2 g^{00}$':'f(t)O₁とO₂g⁰⁰',
  r'$\gamma\dot\pi$型の散逸を伴う$\calo\delta g^{00}$模型':'γ π̇型の散逸を伴うO δg⁰⁰模型',
 }
 for a,b in mapping.items():
  for cmd in ['sectionlink','subsectionlink']:
   s=s.replace('\\'+cmd+'{'+a+'}','\\'+cmd+'{\\texorpdfstring{'+a+'}{'+b+'}}')
 path.write_text(s,encoding='utf-8')
print('Terminology, figure placement and mathematical bookmarks aligned.')
