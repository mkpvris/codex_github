from pathlib import Path
import re, json, hashlib

root = Path(__file__).resolve().parents[1]
files = sorted((root / 'sections').glob('*.tex'))
all_changes = []
file_audit = []
exercise_ids = []
normal_count = 0

def sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

for path in files:
    old = path.read_bytes().decode('utf-8')
    changes = []
    def normal(match):
        changes.append({'kind': 'existing_subsubsection', 'before': match.group(0), 'after': match.group(0).replace('subsubsection', 'subsubsectionlink'), 'old_line': old[:match.start()].count('\n')+1})
        return changes[-1]['after']
    new = re.sub(r'\\subsubsection(?=\*|\{|\[)', normal, old)
    normal_count += len(changes)
    def exercise(match):
        num = match.group('paragraph') or match.group('bold')
        label = match.group('label') or ''
        replacement = r'\subsubsectionlink*{演習' + num + '}' + label
        changes.append({'kind': 'exercise', 'number': num, 'before': match.group(0), 'after': replacement})
        exercise_ids.append(num)
        return replacement
    new = re.sub(r'(?m)^\\(?:paragraph\{(?P<paragraph>[1-9A]\.\d+)\}|noindent\\textbf\{(?P<bold>[1-9A]\.\d+)\})(?P<label>\\label\{ex:[^}]+\})?(?:\\quad)?', exercise, new)
    if not changes:
        continue
    # Reversing just the declared substitutions must exactly recover every byte
    # of the original UTF-8 text, including line endings and original spacing.
    recovered = new
    for change in reversed(changes):
        recovered = recovered.replace(change['after'], change['before'], 1)
    assert recovered == old, f'Unexpected body change in {path.name}'
    labels_before = re.findall(r'\\label\{[^}]+\}', old)
    labels_after = re.findall(r'\\label\{[^}]+\}', new)
    assert labels_before == labels_after
    equations_before = re.findall(r'\\tag\{[^}]+\}', old)
    equations_after = re.findall(r'\\tag\{[^}]+\}', new)
    assert equations_before == equations_after
    assert re.findall(r'\\addcontentsline\{[^\n]+', old) == re.findall(r'\\addcontentsline\{[^\n]+', new)
    path.write_bytes(new.encode('utf-8'))
    for change in changes:
        change['file'] = path.name
    all_changes.extend(changes)
    file_audit.append({'file': path.name, 'before_sha256': sha(old), 'after_sha256': sha(new), 'existing_subsubsections': sum(x['kind']=='existing_subsubsection' for x in changes), 'exercises': sum(x['kind']=='exercise' for x in changes), 'labels_preserved': len(labels_before), 'equation_tags_preserved': len(equations_before), 'body_exactly_preserved_after_reversing_heading_substitutions': True})

assert normal_count == 102, normal_count
assert len(exercise_ids) == 106, len(exercise_ids)
assert len(set(exercise_ids)) == 106
expected = {**{str(i): n for i,n in enumerate([9,17,14,6,3,15,15,12,10],1)}, 'A':5}
for chap,count in expected.items():
    assert {x for x in exercise_ids if x.startswith(chap+'.')} == {chap+'.'+str(i) for i in range(1,count+1)}
report = {'date':'2026-10-21', 'ordinary_subsubsections_converted':normal_count, 'exercises_converted':len(exercise_ids), 'total_new_linked_headings':normal_count+len(exercise_ids), 'chapter_exercise_counts':expected, 'files':file_audit, 'changes':all_changes}
(root/'qa'/'subsub_heading_link_changes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines = ['小見出しの目次掲載・バックリンク変更（2026-10-21、最新指定）', '既存subsubsection*: 102か所をsubsubsectionlink*へ変更。既存の非star小見出しは0か所。', '個別演習: 全106問をsubsubsectionlink*{演習N.m}へ変更。既存番号とexラベルを保持。', '章別: 1章9問、2章17問、3章14問、4章6問、5章3問、6章15問、7章15問、8章12問、9章10問、付録A 5問。', '通常の小見出しの題名は一切変更していない。個別演習は元の番号だけを見出しに用い、本文を題名へ移動していない。', '前段で変更した演習グループsubsectionlink*および手動addcontentslineはそのまま保持。', '用語集は元からsubsubsectionではないため未変更。main/assemble.py/マクロ定義も未変更。', '差分監査: 宣言した見出し置換を逆変換すると元ファイル全体の文字列（改行を含む）と完全一致。全label・全tagおよびaddcontentslineの並びも一致。', '個別変更一覧と前後SHA256は同名JSONに保存。', '']
for item in file_audit:
    lines.append(f"{item['file']}: 通常小見出し {item['existing_subsubsections']}、演習 {item['exercises']}、label {item['labels_preserved']}件保持、tag {item['equation_tags_preserved']}件保持")
(root/'qa'/'subsub_heading_link_changes.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'files':len(file_audit),'subsubsections':normal_count,'exercises':len(exercise_ids),'all_body_and_labels_preserved':True}))
