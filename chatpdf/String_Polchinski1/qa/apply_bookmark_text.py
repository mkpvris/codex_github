"""Apply the ten reviewed PDF-bookmark alternatives after the active build ends.

The TeX argument of each texorpdfstring remains byte-for-byte identical to the
original mathematics. This script is deliberately separate from assembly.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


CHANGES = [
    ('ch02a.tex', r'\subsubsectionlink*{$bc$ CFT}',
     r'\subsubsectionlink*{\texorpdfstring{$bc$}{bc} CFT}'),
    ('ch02a.tex', r'\subsubsectionlink*{$\beta\gamma$ CFT}',
     r'\subsubsectionlink*{\texorpdfstring{$\beta\gamma$}{βγ} CFT}'),
    ('ch02b.tex', r'\subsubsectionlink*{$bc$ CFT}',
     r'\subsubsectionlink*{\texorpdfstring{$bc$}{bc} CFT}'),
    ('ch06a.tex', r'\subsectionlink{$bc$ CFT}',
     r'\subsectionlink{\texorpdfstring{$bc$}{bc} CFT}'),
    ('ch06b.tex', r'\subsubsectionlink*{$D_2$および$RP_2$上の閉弦}',
     r'\subsubsectionlink*{\texorpdfstring{$D_2$}{D₂}および\texorpdfstring{$RP_2$}{RP₂}上の閉弦}'),
    ('ch07.tex', r'\subsubsectionlink*{$bc$ CFT}',
     r'\subsubsectionlink*{\texorpdfstring{$bc$}{bc} CFT}'),
    ('ch08a.tex', r'\sectionlink{トーラスコンパクト化と $T$ 双対性}',
     r'\sectionlink{トーラスコンパクト化と \texorpdfstring{$T$}{T} 双対性}'),
    ('ch08a.tex', r'\subsectionlink{閉弦と $T$ 双対性}',
     r'\subsectionlink{閉弦と \texorpdfstring{$T$}{T} 双対性}'),
    ('ch08a.tex', r'\subsubsectionlink*{$T$ 双対性}',
     r'\subsubsectionlink*{\texorpdfstring{$T$}{T} 双対性}'),
    ('ch08b.tex', r'\subsubsectionlink*{$c=1$ の CFT}',
     r'\subsubsectionlink*{\texorpdfstring{$c=1$}{c=1} の CFT}'),
]


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    before = {}
    after = {}
    changes = []
    # Validate every exact match before modifying any source file.
    for name, old, new in CHANGES:
        if name not in before:
            before[name] = (base/'sections'/name).read_bytes()
            after[name] = before[name]
        old_b, new_b = old.encode('utf-8'), new.encode('utf-8')
        if after[name].count(old_b) != 1:
            raise RuntimeError(f'{name}: expected one unmodified heading: {old}')
        line = after[name][:after[name].index(old_b)].count(b'\n') + 1
        after[name] = after[name].replace(old_b, new_b, 1)
        changes.append({'file':name, 'line':line, 'old':old, 'new':new})
    # Invert exactly the declared replacements to prove all other bytes survived.
    restored = dict(after)
    for name, old, new in reversed(CHANGES):
        restored[name] = restored[name].replace(new.encode('utf-8'), old.encode('utf-8'), 1)
    assert restored == before, 'Unexpected alteration outside reviewed heading replacements'
    files = []
    for name, original in before.items():
        path = base/'sections'/name
        if path.read_bytes() != original:
            raise RuntimeError(f'{name} changed after validation; no source writes begun')
        files.append({'file':name, 'before_sha256':hashlib.sha256(original).hexdigest(),
                      'after_sha256':hashlib.sha256(after[name]).hexdigest()})
    for name, content in after.items():
        (base/'sections'/name).write_bytes(content)
    report = {'applied_at_utc':datetime.now(timezone.utc).isoformat(),
              'heading_count':len(changes), 'file_count':len(files),
              'inverse_replacements_reproduce_original_bytes':True,
              'printed_math_and_TOC_preserved':True, 'changes':changes, 'files':files,
              'source':'TeX Live 2026 hyperref-doc.tex, lines 1710–1725: texorpdfstring'}
    prefix = base/'qa'/'bookmark_text_changes'
    prefix.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines = ['数式見出しのPDFしおり文字列修正',
             f'{len(changes)}見出し、{len(files)}ファイル。TeXの数式表記・本文・TOC組版は保持。',
             '宣言した置換の逆変換で元ファイル全バイトに一致。',
             'PDFしおりだけ bc、βγ、D₂、RP₂、T、c=1 の代替文字列を使用。']
    for item in changes:
        lines.extend([f"{item['file']}:{item['line']}", '  '+item['old'], '  '+item['new']])
    prefix.with_suffix('.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'headings':len(changes),'files':len(files),'audit':str(prefix.with_suffix('.json'))},ensure_ascii=False))


if __name__ == '__main__':
    main()
