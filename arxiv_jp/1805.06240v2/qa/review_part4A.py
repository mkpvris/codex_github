import difflib, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
original = (ROOT/'original'/'SSBofDspv2.tex').read_text(encoding='utf-8')
original = original[original.index(r'\section{Summary and Outlook}'):original.index(r'\bibliography{bib}')]
jp = (ROOT/'parts'/'part4A.tex').read_text(encoding='utf-8')
norm = lambda text:re.sub(r'\s+','',text)
displays = lambda text:[(m.group(1),norm(m.group(2))) for m in re.finditer(r'\\begin\{(equation\*?|align\*?)\}(.*?)\\end\{\1\}',text,re.S)]
inline = lambda text:[norm(m) for m in re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$',text,re.S)]
original_displays, jp_displays = displays(original), displays(jp)
original_inline, jp_inline = inline(original), inline(jp)
refs = lambda text:re.findall(r'\\(?:eqref|ref|cite)\{([^}]+)\}',text)
labels = lambda text:re.findall(r'\\label\{([^}]+)\}',text)
result={'display_math_environment_count':len(original_displays),'display_math_environment_count_jp':len(jp_displays),'display_math_exact_ignoring_whitespace':original_displays==jp_displays,'inline_math_count':len(original_inline),'inline_math_count_jp':len(jp_inline),'inline_math_exact_ignoring_whitespace':original_inline==jp_inline,'reference_targets_in_order_identical':refs(original)==refs(jp),'labels_in_order_identical':labels(original)==labels(jp),'reference_sequence_original':refs(original),'reference_sequence_jp':refs(jp)}
if original_inline != jp_inline:
 result['inline_differences']=list(difflib.unified_diff(original_inline,jp_inline))
(ROOT/'qa'/'part4A_math_reference_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
