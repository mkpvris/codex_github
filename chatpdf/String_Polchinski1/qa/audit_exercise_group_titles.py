"""Compare both PDF editions after changing only the ten exercise TOC titles.

Run --capture-baseline once before rebuilding. Run without it only after the
parent confirms that both final PDFs and their TOC files are stable.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from pypdf import PdfReader

from audit_subsub_links import contents_records, named_annotation_target, outline_records


CONFIG = {
    'normal': {'file':'String_Polchinski1_jp.pdf', 'pages':372, 'index_start':349,
               'expected_old_sha256':'55c57a0e861219db8d0ffa96a8d87f38353ddbcf6c9258f7a28964eda63753e1',
               'subsub_toc_links':0, 'build':'build'},
    'extended': {'file':'String_Polchinski1_jp_index_extended.pdf', 'pages':374, 'index_start':351,
                 'expected_old_sha256':'895d44d95beba30cdcf89e538e299c8d41c72a1a3f925656974ed65eb46d9743',
                 'subsub_toc_links':102, 'build':'build_index_extended'},
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(path, config):
    data = path.read_bytes()
    reader = PdfReader(path)
    named = {name:reader.get_destination_page_number(dest)+1 for name,dest in reader.named_destinations.items()}
    outline = outline_records(reader)
    groups = [row for row in outline if '演習' in row['title']]
    if len(groups) != 10:
        raise ValueError(f'{path.name}: expected ten exercise groups, found {len(groups)}')
    if any(re.search(r'演習[1-9A]\.\d+', row['title']) for row in groups):
        raise ValueError('An individual exercise is unexpectedly present in the outline')
    toc_start = named['toc']
    toc_end = min(named[row['target']] for row in outline)-1
    group_targets = {row['target'] for row in groups}
    group_pages = {named[target] for target in group_targets}
    links, index_links, backlinks, toc_links = [], [], [], []
    body_text = {}
    toc_text = []
    for page_number, page in enumerate(reader.pages, 1):
        if page_number in group_pages:
            body_text[str(page_number)] = digest(page.extract_text().encode('utf-8'))
        if toc_start <= page_number <= toc_end:
            toc_text.append(page.extract_text())
        for ref in page.get('/Annots', []):
            annotation = ref.get_object()
            if annotation.get('/Subtype') != '/Link':
                continue
            target = named_annotation_target(annotation)
            if target is None:
                continue
            row = {'source_page':page_number, 'target':target,
                   'target_page':named.get(target),
                   'rect':[round(float(value),3) for value in annotation.get('/Rect', [])]}
            if target == 'toc':
                backlinks.append(row)
            if toc_start <= page_number <= toc_end:
                toc_links.append(row)
                if target in group_targets:
                    links.append(row)
            if page_number >= config['index_start'] and re.fullmatch(r'page\.\d+', target):
                index_links.append(row)
    return {'path':str(path.resolve()), 'sha256':digest(data), 'bytes':len(data),
            'pages':len(reader.pages), 'named_destination_pages':named, 'outline':outline,
            'toc_pages':[toc_start,toc_end], 'exercise_groups':groups,
            'exercise_group_toc_annotations':links, 'toc_annotations':toc_links,
            'toc_backlinks':backlinks, 'index_start':config['index_start'],
            'index_page_annotations':index_links,
            'exercise_group_body_page_text_sha256':body_text,
            'printed_toc_exercise_problem_count':re.sub(r'\s+','', ''.join(toc_text)).count('演習問題')}


def compare(name, current, old, toc_text):
    config = CONFIG[name]
    errors = []
    if current['pages'] != config['pages']:
        errors.append(f"Expected {config['pages']} pages, found {current['pages']}")
    before, after = old['named_destination_pages'], current['named_destination_pages']
    missing = sorted(set(before)-set(after))
    added = sorted(set(after)-set(before))
    moved = [{'target':key, 'before':before[key], 'after':after[key]}
             for key in before.keys() & after.keys() if before[key] != after[key]]
    if missing or added or moved:
        errors.append('Named destination set or physical page mapping changed')
    if len(current['toc_backlinks']) != 261:
        errors.append('The 261 existing body-to-TOC backlinks were not preserved')
    if current['toc_backlinks'] != old['toc_backlinks']:
        errors.append('Body-to-TOC annotation positions or destinations changed')
    if current['index_page_annotations'] != old['index_page_annotations']:
        errors.append('Index page.N annotation sequence, rectangles, or targets changed')
    bad_index = [row for row in current['index_page_annotations']
                 if row['target_page'] != int(row['target'].split('.')[1])]
    if not current['index_page_annotations'] or bad_index:
        errors.append('An index page.N target does not resolve to its displayed physical page')
    if current['exercise_group_body_page_text_sha256'] != old['exercise_group_body_page_text_sha256']:
        errors.append('Extracted text changed on an exercise-group body page')
    records = contents_records(toc_text)
    by_target = {row['destination']:row for row in records}
    outline_by_target = {row['target']:row for row in current['outline']}
    groups = []
    for baseline_group in old['exercise_groups']:
        target = baseline_group['target']
        record = by_target.get(target)
        outline = outline_by_target.get(target)
        annotations = [row for row in current['exercise_group_toc_annotations'] if row['target']==target]
        good = bool(record and record['level']=='subsection' and record['title_tex']=='演習問題'
                    and outline and outline['title']=='演習問題' and len(annotations)==1
                    and annotations[0]['target_page']==before[target])
        groups.append({'target':target, 'record':record, 'outline':outline,
                       'toc_annotations':annotations, 'passed':good})
    if not all(row['passed'] for row in groups):
        errors.append('Not all ten exercise-group TOC/outline titles equal 演習問題 with their original destinations')
    if current['printed_toc_exercise_problem_count'] != 10:
        errors.append('The printed PDF TOC does not contain exactly ten 演習問題 titles')
    subsub = [row for row in records if row['level']=='subsubsection']
    subsub_targets = {row['destination'] for row in subsub}
    subsub_links = [row for row in current['toc_annotations'] if row['target'] in subsub_targets]
    subsub_outline = [row for row in current['outline'] if row['target'] in subsub_targets]
    if len(subsub) != 102 or len(subsub_links) != config['subsub_toc_links']:
        errors.append('Ordinary subsubsection TOC visibility differs from this edition\'s policy')
    if len(subsub_outline) != config['subsub_toc_links']:
        errors.append('Ordinary subsubsection outline visibility differs from this edition\'s policy')
    if any(re.search(r'演習[1-9A]\.\d+', row['title_tex']) for row in records):
        errors.append('An individual exercise has reappeared in TOC records')
    old_group_targets = {row['target'] for row in old['exercise_groups']}
    old_other_outline = [row for row in old['outline'] if row['target'] not in old_group_targets]
    new_other_outline = [row for row in current['outline'] if row['target'] not in old_group_targets]
    if old_other_outline != new_other_outline:
        errors.append('An outline entry outside the ten exercise groups changed')
    summary = {'edition':name, 'pdf':current['path'], 'pdf_sha256':current['sha256'],
               'pages':current['pages'], 'bytes':current['bytes'],
               'named_destinations':len(after), 'named_destinations_missing':len(missing),
               'named_destinations_added':len(added), 'named_destinations_moved':len(moved),
               'exercise_group_titles_passed':sum(row['passed'] for row in groups),
               'printed_toc_exercise_problem_titles':current['printed_toc_exercise_problem_count'],
               'toc_backlinks':len(current['toc_backlinks']),
               'subsubsection_toc_annotations':len(subsub_links),
               'subsubsection_outline_entries':len(subsub_outline),
               'index_page_annotations':len(current['index_page_annotations']),
               'index_annotations_unchanged':current['index_page_annotations']==old['index_page_annotations'],
               'exercise_body_page_text_unchanged':current['exercise_group_body_page_text_sha256']==old['exercise_group_body_page_text_sha256'],
               'errors':errors, 'ok':not errors}
    return {'summary':summary, 'exercise_groups':groups,
            'named_destination_changes':{'missing':missing,'added':added,'moved':moved},
            'invalid_index_annotations':bad_index}


def main():
    base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-baseline', action='store_true')
    parser.add_argument('--normal-toc', type=Path, default=base/'build'/'String_Polchinski1_jp.toc')
    parser.add_argument('--extended-toc', type=Path, default=base/'build_index_extended'/'String_Polchinski1_jp.toc')
    args = parser.parse_args()
    baseline_path = base/'qa'/'exercise_group_titles_baseline.json'
    current = {}
    for name, config in CONFIG.items():
        current[name] = snapshot(base/'pdf'/config['file'], config)
        if args.capture_baseline:
            if current[name]['sha256'] != config['expected_old_sha256']:
                raise ValueError(f'{name}: old PDF hash differs; refusing to overwrite baseline')
            if current[name]['pages'] != config['pages']:
                raise ValueError(f'{name}: old page count differs')
    if args.capture_baseline:
        baseline_path.write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({name:{'pages':row['pages'],'sha256':row['sha256'],
                                'named_destinations':len(row['named_destination_pages']),
                                'toc_groups':len(row['exercise_group_toc_annotations']),
                                'toc_backlinks':len(row['toc_backlinks']),
                                'index_annotations':len(row['index_page_annotations'])}
                          for name,row in current.items()},ensure_ascii=True,indent=2))
        return 0
    old = json.loads(baseline_path.read_text(encoding='utf-8'))
    reports = {}
    for name in CONFIG:
        toc_path = args.normal_toc if name=='normal' else args.extended_toc
        reports[name] = compare(name,current[name],old[name],toc_path.read_text(encoding='utf-8'))
    output = base/'qa'/'exercise_group_titles_audit'
    output.with_suffix('.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
    summaries = {name:report['summary'] for name,report in reports.items()}
    output.with_suffix('.txt').write_text('両版の演習グループ目次名・全移動先・索引リンク監査\n'+
                                        json.dumps(summaries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summaries,ensure_ascii=True,indent=2))
    return 0 if all(row['ok'] for row in summaries.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
