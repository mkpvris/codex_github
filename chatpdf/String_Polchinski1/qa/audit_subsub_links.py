"""Audit TOC/body links after the parent confirms that the final PDF is ready.

Uses named destinations from the actual .toc/.aux and PDF annotation rectangles;
it does not depend on extracted Japanese/math heading text matching exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from pypdf import PdfReader


def tex_group(text: str, pos: int) -> tuple[str, int]:
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != '{':
        raise ValueError(f'Expected TeX group near {text[pos:pos+80]!r}')
    start = pos + 1
    pos += 1
    depth = 1
    while pos < len(text):
        char = text[pos]
        if char == '\\' and pos + 1 < len(text) and text[pos + 1] in '{}':
            pos += 2
            continue
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if not depth:
                return text[start:pos], pos + 1
        pos += 1
    raise ValueError('Unbalanced TeX group')


def contents_records(text: str) -> list[dict]:
    records = []
    for match in re.finditer(r'\\contentsline\b', text):
        pos = match.end()
        args = []
        for _ in range(4):
            arg, pos = tex_group(text, pos)
            args.append(arg)
        record = dict(zip(['level', 'title_tex', 'printed_page', 'destination'], args))
        record['toc_command_offset'] = match.start()
        records.append(record)
    return records


def exercise_label_records(text: str) -> list[dict]:
    records = []
    for match in re.finditer(r'\\newlabel\{ex:([1-9A]\.\d+)\}', text):
        value, _ = tex_group(text, match.end())
        fields, pos = [], 0
        while pos < len(value):
            field, pos = tex_group(value, pos)
            fields.append(field)
        if len(fields) < 4:
            raise ValueError(f'Incomplete exercise label: {match.group(1)}')
        records.append({'number':match.group(1), 'printed_page':fields[1],
                        'title_tex':fields[2], 'destination':fields[3]})
    return records


def deref(value):
    return value.get_object() if hasattr(value, 'get_object') else value


def named_annotation_target(annotation):
    action = deref(annotation.get('/A', {}))
    target = action.get('/D') if action.get('/S') == '/GoTo' else annotation.get('/Dest')
    if isinstance(target, str):
        return str(target).removeprefix('/')
    return None


def numeric(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def outline_records(reader):
    """Keep the original named /GoTo target instead of text/page heuristics."""
    root = deref(reader.trailer['/Root'].get('/Outlines', {}))
    rows = []
    visited = set()

    def walk(reference, depth):
        while reference:
            key = (getattr(reference, 'idnum', None), getattr(reference, 'generation', None))
            if key != (None, None):
                if key in visited:
                    raise ValueError('Cycle in PDF outline linked list')
                visited.add(key)
            node = deref(reference)
            rows.append({'title':str(deref(node.get('/Title', ''))),
                         'target':named_annotation_target(node), 'depth':depth})
            if node.get('/First'):
                walk(node['/First'], depth+1)
            reference = node.get('/Next')

    if root.get('/First'):
        walk(root['/First'], 0)
    return rows


def main() -> int:
    base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path, default=base/'pdf'/'String_Polchinski1_jp.pdf')
    parser.add_argument('--toc', type=Path, default=base/'build'/'String_Polchinski1_jp.toc')
    parser.add_argument('--aux', type=Path, default=base/'build'/'String_Polchinski1_jp.aux')
    parser.add_argument('--baseline', type=Path, default=base/'qa'/'individual_exercise_removal_baseline.json')
    parser.add_argument('--output-prefix', type=Path, default=base/'qa'/'audit_subsub_links')
    args = parser.parse_args()
    pdf_bytes = args.pdf.read_bytes()
    toc_text = args.toc.read_text(encoding='utf-8')
    aux_text = args.aux.read_text(encoding='utf-8')
    baseline = json.loads(args.baseline.read_text(encoding='utf-8'))
    reader = PdfReader(args.pdf)
    named = reader.named_destinations
    outlines = outline_records(reader)
    outline_by_destination = {}
    for row in outlines:
        if row['target']:
            outline_by_destination.setdefault(row['target'], []).append(row)
    records = contents_records(toc_text)
    aux_records = contents_records(aux_text)
    subsub = [r for r in records if r['level'] == 'subsubsection']
    groups = [r for r in records if r['level'] == 'subsection' and '演習' in r['title_tex']]
    selected = subsub + groups
    errors = []
    depth_drop = re.search(r'\\setcounter\s*\{tocdepth\}\s*\{2\}', toc_text)
    subsub_after_depth_drop = [r for r in subsub if depth_drop and r['toc_command_offset'] > depth_drop.start()]
    if not depth_drop:
        errors.append('No tocdepth=2 transition before references/glossary in .toc')
    if subsub_after_depth_drop:
        errors.append('Subsubsection TOC records appear after the appendix-A scope boundary')
    glossary_source = (base/'sections'/'glossary01.tex').read_text(encoding='utf-8')
    glossary_hangindent = bool(re.search(r'\\hangindent\s*=?\s*1\.5em', glossary_source))
    glossary_hangafter = bool(re.search(r'\\hangafter\s*=?\s*1\b', glossary_source))
    if len(subsub) != 102:
        errors.append(f'Expected 102 ordinary subsubsection TOC records, found {len(subsub)}')
    if len(groups) != 10:
        errors.append(f'Expected 10 exercise-group TOC records, found {len(groups)}')
    exercise_numbers = []
    for record in records:
        match = re.search(r'演習([1-9A]\.\d+)', record['title_tex'])
        if match:
            exercise_numbers.append(match.group(1))
    expected_counts = {'1':9,'2':17,'3':14,'4':6,'5':3,'6':15,'7':15,'8':12,'9':10,'A':5}
    expected_numbers = {f'{chapter}.{n}' for chapter, count in expected_counts.items() for n in range(1,count+1)}
    if exercise_numbers:
        errors.append('Individual exercise entries remain in the TOC')
    aux_exercise_contents = [r for r in aux_records if re.search(r'演習[1-9A]\.\d+', r['title_tex'])]
    outline_exercises = [r for r in outlines if re.search(r'演習[1-9A]\.\d+', r['title'])]
    if aux_exercise_contents:
        errors.append('Individual exercise contentsline records remain in the AUX')
    if outline_exercises:
        errors.append('Individual exercise entries remain in the PDF outline')
    source_files = sorted((base/'sections').glob('ch*.tex')) + [base/'sections'/'appendixA.tex']
    source_text = '\n'.join(p.read_text(encoding='utf-8') for p in source_files)
    source_exercises = re.findall(r'\\subsubsection\*\s*\{演習([1-9A]\.\d+)\}', source_text)
    linked_source_exercises = re.findall(r'\\subsubsectionlink\*?\s*\{演習([1-9A]\.\d+)\}', source_text)
    source_exercise_labels = re.findall(r'\\label\{ex:([1-9A]\.\d+)\}', source_text)
    if Counter(source_exercises) != Counter(expected_numbers):
        errors.append('The source does not preserve exactly one ordinary heading for each of the 106 exercises')
    if linked_source_exercises:
        errors.append('Individual exercise headings still use the backlink macro in source')
    if Counter(source_exercise_labels) != Counter(expected_numbers):
        errors.append('The source does not contain exactly one label for each of the 106 exercises')
    exercise_labels = exercise_label_records(aux_text)
    if Counter(r['number'] for r in exercise_labels) != Counter(expected_numbers):
        errors.append('The AUX does not contain exactly one label for each of the 106 exercises')
    destination_counts = Counter(r['destination'] for r in selected)
    duplicates = {name:n for name,n in destination_counts.items() if n != 1}
    if duplicates:
        errors.append(f'Duplicate selected TOC destinations: {duplicates}')
    aux_by_destination = {r['destination']:r for r in aux_records}
    destinations = {}
    for name, dest in named.items():
        destinations[name] = {'page':reader.get_destination_page_number(dest)+1,
                              'top':numeric(dest.get('/Top')), 'left':numeric(dest.get('/Left')),
                              'type':str(dest.get('/Type'))}
    if 'toc' not in destinations:
        errors.append('No named destination toc')
    toc_page = destinations.get('toc', {}).get('page')
    body_pages = [destinations[r['destination']]['page'] for r in records
                  if r['destination'] in destinations and r['destination'] != 'toc']
    first_body_page = min(body_pages) if body_pages else None
    if toc_page is None or first_body_page is None or first_body_page <= toc_page:
        errors.append(f'Cannot infer a TOC page range: toc={toc_page}, first body={first_body_page}')
    annotations = []
    for pno, page in enumerate(reader.pages,1):
        for index, reference in enumerate(page.get('/Annots', [])):
            annotation = deref(reference)
            if annotation.get('/Subtype') != '/Link':
                continue
            target = named_annotation_target(annotation)
            if target is None:
                continue
            rect = [float(x) for x in annotation.get('/Rect', [])]
            if len(rect) != 4:
                continue
            annotations.append({'id':f'{pno}:{index}', 'page':pno, 'target':target,
                                'rect':rect, 'target_page':destinations.get(target,{}).get('page')})
    forward_by_destination = {}
    back_by_page = {}
    for ann in annotations:
        if toc_page is not None and first_body_page is not None and toc_page <= ann['page'] < first_body_page:
            forward_by_destination.setdefault(ann['target'],[]).append(ann)
        if ann['target'] == 'toc':
            back_by_page.setdefault(ann['page'],[]).append(ann)
    total_toc_backlinks = sum(len(rows) for rows in back_by_page.values())
    if total_toc_backlinks != baseline['expected_remaining_toc_target_annotations']:
        errors.append(f"Expected {baseline['expected_remaining_toc_target_annotations']} toc-target annotations after removing 106 exercises; found {total_toc_backlinks}")
    exercise_details = []
    for record in exercise_labels:
        result = dict(record)
        result['issues'] = []
        name = record['destination']
        dest = destinations.get(name)
        result['named_destination'] = dest
        if dest is None:
            result['issues'].append('Missing exercise label PDF destination')
        else:
            printed = record['printed_page'].strip()
            if not printed.isdecimal() or int(printed) != dest['page']:
                result['issues'].append('Exercise label page differs from actual destination')
            nearby = []
            if dest['top'] is not None:
                for ann in back_by_page.get(dest['page'], []):
                    delta = dest['top'] - ann['rect'][3]
                    if -6 <= delta <= 25:
                        nearby.append(ann)
            result['nearby_toc_backlinks'] = nearby
            if nearby:
                result['issues'].append('A toc backlink remains at the individual exercise heading position')
        if forward_by_destination.get(name):
            result['issues'].append('A TOC link remains to the individual exercise destination')
        if outline_by_destination.get(name):
            result['issues'].append('A PDF outline entry remains at the individual exercise destination')
        result['passed'] = not result['issues']
        exercise_details.append(result)
    failed_exercises = [r for r in exercise_details if not r['passed']]
    if failed_exercises:
        errors.append(f'{len(failed_exercises)} individual exercises failed removal/preservation verification')
    details = []
    # Link rectangles are in PDF coordinates (origin at bottom left). The named
    # heading anchor is normally a few points above the title. Only annotations
    # in the same 48pt vertical neighborhood are eligible, and each rectangle
    # must belong to exactly one selected heading. This prevents accepting an
    # unrelated backlink merely because it is on the same PDF page.
    for record in selected:
        name = record['destination']
        result = dict(record)
        result['kind'] = 'subsubsection' if record in subsub else 'exercise_group'
        result['issues'] = []
        result['pdf_outline_entries'] = outline_by_destination.get(name, [])
        if len(result['pdf_outline_entries']) != 1:
            result['issues'].append('Expected exactly one PDF outline entry with this named target')
        dest = destinations.get(name)
        result['named_destination'] = dest
        if dest is None:
            result['issues'].append('Missing PDF named destination')
        aux_record = aux_by_destination.get(name)
        result['aux_agrees'] = bool(aux_record and aux_record['level'] == record['level'] and
                                   aux_record['printed_page'] == record['printed_page'])
        if not result['aux_agrees']:
            result['issues'].append('TOC/AUX destination or page disagreement')
        forward = forward_by_destination.get(name,[])
        result['toc_to_body_annotations'] = forward
        if not forward:
            result['issues'].append('No TOC-to-body annotation with this exact named target')
        if dest:
            printed = record['printed_page'].strip()
            result['printed_page_matches_physical_page'] = printed.isdecimal() and int(printed)==dest['page']
            if not result['printed_page_matches_physical_page']:
                result['issues'].append('TOC printed page does not equal actual PDF destination page')
            candidates = []
            if dest['top'] is not None:
                for ann in back_by_page.get(dest['page'],[]):
                    delta = dest['top'] - ann['rect'][3]
                    if -6 <= delta <= 48 and ann['target_page'] == toc_page:
                        candidate = dict(ann)
                        candidate['heading_anchor_minus_rect_top_pt'] = round(delta,3)
                        candidates.append(candidate)
            candidates.sort(key=lambda a:abs(a['heading_anchor_minus_rect_top_pt']))
            result['body_backlink_candidates'] = candidates
            result['selected_body_to_toc_annotation'] = candidates[0] if candidates else None
            if not candidates:
                result['issues'].append('No nearby body-to-TOC backlink at the heading position')
        details.append(result)
    assigned = Counter(r['selected_body_to_toc_annotation']['id'] for r in details
                       if r.get('selected_body_to_toc_annotation'))
    for result in details:
        ann = result.get('selected_body_to_toc_annotation')
        if ann and assigned[ann['id']] > 1:
            result['issues'].append('Backlink rectangle ambiguously shared with another heading')
        result['passed'] = not result['issues']
    failed = [r for r in details if not r['passed']]
    if failed:
        errors.append(f'{len(failed)} selected headings failed positional/link verification')
    math_bookmarks = []
    for record in records:
        title = record['title_tex']
        expected = None
        if re.search(r'\$\s*\\beta\s*\\gamma\s*\$', title):
            expected = ['βγ CFT']
        elif '$D_2$' in title:
            expected = ['D₂およびRP₂上の閉弦']
        elif '$bc$' in title:
            expected = ['bc CFT']
        elif '$T$' in title:
            expected = ['T 双対性']
        elif '$c=1$' in title:
            expected = ['c=1 の CFT']
        if expected:
            entries = outline_by_destination.get(record['destination'], [])
            ok = len(entries) == 1 and all(s in entries[0]['title'] for s in expected)
            math_bookmarks.append({'destination':record['destination'], 'title_tex':title,
                                   'expected_strings':expected, 'outline_entries':entries, 'passed':ok})
    if len(math_bookmarks) != 10 or not all(r['passed'] for r in math_bookmarks):
        errors.append('The ten mathematical headings are not all present as readable PDF outline text')
    summary = {'pdf':str(args.pdf), 'pdf_sha256':hashlib.sha256(pdf_bytes).hexdigest(),
               'toc':str(args.toc), 'aux':str(args.aux), 'pdf_pages':len(reader.pages),
               'toc_physical_pages':[toc_page,first_body_page-1 if first_body_page else None],
               'subsubsection_count':len(subsub), 'ordinary_subsubsection_count':len(subsub)-len(exercise_numbers),
               'individual_exercises_in_toc':len(exercise_numbers), 'exercise_groups':len(groups),
               'individual_exercises_in_aux_contents':len(aux_exercise_contents),
               'individual_exercises_in_outline':len(outline_exercises),
               'individual_exercises_preserved_in_source':len(source_exercises),
               'individual_exercise_labels_in_source':len(source_exercise_labels),
               'individual_exercises_preserved_in_pdf':sum(r['passed'] for r in exercise_details),
               'individual_exercises_failed':len(failed_exercises),
               'baseline_pdf_sha256':baseline['pdf_sha256'],
               'baseline_toc_target_annotations':baseline['toc_target_annotations'],
               'toc_target_annotations':total_toc_backlinks,
               'removed_toc_target_annotations':baseline['toc_target_annotations']-total_toc_backlinks,
               'tocdepth_returns_to_2_after_appendix_A':bool(depth_drop),
               'subsubsection_records_after_scope_boundary':len(subsub_after_depth_drop),
               'glossary_source_hangindent_1_5em':glossary_hangindent,
               'glossary_source_hangafter_1':glossary_hangafter,
               'pdf_outline_entry_count':len(outlines),
               'subsubsection_outline_count':sum(len(outline_by_destination.get(r['destination'],[])) for r in subsub),
               'readable_math_bookmarks':sum(r['passed'] for r in math_bookmarks),
               'all_selected_headings':len(details), 'passed':sum(r['passed'] for r in details),
               'failed':len(failed), 'errors':errors, 'ok':not errors}
    report = {'summary':summary, 'headings':details, 'mathematical_bookmarks':math_bookmarks,
              'individual_exercises':exercise_details}
    args.output_prefix.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines = ['小見出し・演習グループ PDF相互リンク監査', json.dumps(summary,ensure_ascii=False,indent=2),
             '検証: .tocと.auxのnamed destination、PDFの実移動先ページ、目次内annotation、',
             '本文見出しanchorの同一ページ・48pt以内にあるtoc行きannotation、矩形の一意な割当を確認。',
             'さらに102小見出し・10演習グループのPDFしおりnamed targetと数式見出し10件のUnicode表記を確認。',
             '個別演習106問の本文見出し・ラベル保全、目次/しおり/バックリンク削除と注釈総数106件減を確認。',
             '本文見出しの数式・日本語の文字抽出一致には依存していない。']
    for result in failed:
        lines.append(f"FAIL {result['level']} {result['title_tex']} [{result['destination']}]: {'; '.join(result['issues'])}")
    for result in failed_exercises:
        lines.append(f"FAIL exercise {result['number']} [{result['destination']}]: {'; '.join(result['issues'])}")
    args.output_prefix.with_suffix('.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 0 if summary['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
