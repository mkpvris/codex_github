from pathlib import Path
import json
import re
import shutil

root = Path(__file__).resolve().parent
replacements = {
    "ch08b": [
        (r"Buscher (1987, 1988)、", r"Buscher (1987, 1988)\cite{Buscher:1987sk,Buscher:1987qj}、"),
        (r"Roček \& Verlinde (1992)。", r"Roček \& Verlinde (1992)\cite{Rocek:1991ps}。"),
    ],
    "ch09b": [
        (r"McClain \& Roth (1987)。", r"McClain \& Roth (1987)\cite{McClain:1986id}。"),
    ],
}
for name, pairs in replacements.items():
    path = root / "sections" / (name + ".tex")
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")

chapters = [
    ["ch01a", "ch01b"], ["ch02a", "ch02b"], ["ch03a", "ch03b", "ch03c"],
    ["ch04"], ["ch05"], ["ch06a", "ch06b"], ["ch07"],
    ["ch08a", "ch08b"], ["ch09a", "ch09b"],
]
backmatter = [[f"glossary{i:02d}" for i in range(1, 7)], ["index"]]
required = ["frontmatter", "appendixA", "references_intro"]
required += [x for group in chapters + backmatter for x in group]
for name in required:
    if not (root / "sections" / (name + ".tex")).is_file():
        raise FileNotFoundError(name)

state = {
    "edition": "全巻（組立管理用、本文非表示）",
    "status": "前付け、第1--9章、付録A、参考文献、用語集、索引を収録。",
    "chapters": chapters,
    "appendix": True,
    "backmatter": backmatter,
}
(root / "assembly_manifest.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

texts = {name: (root / "sections" / (name + ".tex")).read_text(encoding="utf-8") for name in required}
labels = {x for text in texts.values() for x in re.findall(r"\\label\{([^}]+)\}", text)}
unresolved = []
for name, text in texts.items():
    for target in re.findall(r"\\(?:eqref|ref)\{([^}]+)\}|\\hyperref\[([^\]]+)\]", text):
        target = target[0] or target[1]
        if target not in labels:
            unresolved.append({"file": name, "label": target})
(root / "qa/prebuild_reference_audit.json").write_text(json.dumps(unresolved, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Prepared full volume; {len(labels)} labels, {len(unresolved)} static unresolved targets.")
if unresolved:
    print(json.dumps(unresolved, ensure_ascii=False, indent=2))
