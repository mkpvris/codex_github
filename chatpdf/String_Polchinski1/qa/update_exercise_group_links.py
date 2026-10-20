from pathlib import Path
import re, json

root = Path(__file__).resolve().parents[1]
files = sorted((root / 'sections').glob('ch*.tex')) + [root / 'sections' / 'appendixA.tex']
audit = []
total = 0
for path in files:
    old = path.read_bytes().decode('utf-8')
    new = old
    groups = list(re.finditer(r'\\subsection\*\{(演習|演習問題|第\d+章の演習)\}', old))
    exercise_ids = re.findall(r'\\(?:paragraph\{([1-9A]\.\d+)\}|noindent\\textbf\{([1-9A]\.\d+)\})', old)
    exercise_ids = [a or b for a, b in exercise_ids]
    total += len(exercise_ids)
    for match in groups:
        new = new.replace(match.group(0), match.group(0).replace('\\subsection*', '\\subsectionlink*'), 1)
    added_toc = None
    if groups and not re.search(r'\\addcontentsline\{toc\}\{subsection\}\{[^}]*演習[^}]*\}', old):
        chapter = re.search(r'ch(\d+)', path.name)
        added_toc = f'第{int(chapter.group(1))}章の演習' if chapter else '付録Aの演習'
        newline = '\r\n' if '\r\n' in old else '\n'
        new = re.sub(r'(\\subsectionlink\*\{(?:演習|演習問題|第\d+章の演習)\})', lambda m: m.group(1) + newline + r'\addcontentsline{toc}{subsection}{' + added_toc + '}', new, count=1)
    assert re.findall(r'\\label\{ex:[^}]+\}', old) == re.findall(r'\\label\{ex:[^}]+\}', new)
    assert re.findall(r'\\subsubsection\*\{', old) == re.findall(r'\\subsubsection\*\{', new)
    for heading in exercise_ids:
        assert old.count('{' + heading + '}') == new.count('{' + heading + '}')
    if new != old:
        path.write_bytes(new.encode('utf-8'))
        audit.append({'file': path.name, 'group_headings_changed': len(groups), 'exercise_count': len(exercise_ids), 'exercise_ids': exercise_ids, 'toc_added': added_toc, 'original_exercise_labels': re.findall(r'\\label\{(ex:[^}]+)\}', old)})

assert sum(a['group_headings_changed'] for a in audit) == 10
assert total == 106
(root / 'qa' / 'exercise_group_link_changes.json').write_text(json.dumps({'total_exercises_unchanged': total, 'changes': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
report = ['演習グループ見出しリンク変更（2026-10-21）', '最新のユーザー指定に従い、目次に載る演習グループだけに目次バックリンクを付与。', '変更: 全10グループの \\subsection* → \\subsectionlink*。', '本文、全106問の個別見出し書式、既存の全exラベル、通常のsubsubsection*は変更していない。', '既存7か所のaddcontentslineは保持。第5章・第7章・付録Aの3か所にのみ目次項目を追加。', '本番マクロ定義とassemble.pyは変更していない。ビルドはroot担当。', '']
for a in audit:
    report.append(f"{a['file']}: グループ {a['group_headings_changed']}、個別演習 {a['exercise_count']} 問（変更なし）、目次追加={a['toc_added'] or 'なし（既存を保持）'}")
(root / 'qa' / 'exercise_group_link_changes.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
print(json.dumps({'changed_files': len(audit), 'group_headings': 10, 'unchanged_exercises': total}, ensure_ascii=False))
