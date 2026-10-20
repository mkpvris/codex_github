"""Apply the user's 2026-10-21 title and heading corrections idempotently."""
from pathlib import Path
import re
import json

root = Path(__file__).resolve().parent
front_path = root / "sections/frontmatter.tex"
front = front_path.read_text(encoding="utf-8")
backup = root / "qa/frontmatter_before_user_format.tex"
if not backup.exists():
    backup.write_text(front, encoding="utf-8")
front = re.sub(r"% 原書PDF 1：画像表紙内の文字。.*?(?=% 原書PDF 3。)", "", front, flags=re.S)
front = re.sub(r"\\section\*\{([^\n]+)\}\n\\addcontentsline\{toc\}\{section\}\{\1\}", r"\\sectionlink*{\1}", front)
front = front.replace(r"\subsection*{", r"\subsectionlink*{")
front = front.replace("\\subsectionlink*{著者について}\n", "")
front_path.write_text(front, encoding="utf-8")

path = root / "sections/references_intro.tex"
text = path.read_text(encoding="utf-8")
text = text.replace("\\section*{\\hyperlink{toc}{参考文献案内}}\n\\addcontentsline{toc}{section}{参考文献案内}", "\\sectionlink*{参考文献}")
path.write_text(text, encoding="utf-8")

path = root / "sections/glossary01.tex"
text = path.read_text(encoding="utf-8")
text = text.replace("\\section*{\\hyperlink{toc}{用語集}}\n\\addcontentsline{toc}{section}{用語集}", "\\sectionlink*{用語集}")
path.write_text(text, encoding="utf-8")

path = root / "assembly_manifest.json"
state = json.loads(path.read_text(encoding="utf-8-sig"))
state["edition"] = "前付け・第1--8章・付録A・参考文献（組立管理用、本文非表示）"
state["status"] = "用語集と索引、第9章を準備中。本文には作業状況を印字しない。"
if ["ch08a", "ch08b"] not in state["chapters"]:
    state["chapters"].append(["ch08a", "ch08b"])
state["appendix"] = True
path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
print("User title and unnumbered heading preferences applied.")
