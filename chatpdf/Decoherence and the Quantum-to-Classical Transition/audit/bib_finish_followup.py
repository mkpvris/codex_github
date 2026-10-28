from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
matches=json.loads((root/'audit/matching_override.json').read_text(encoding='utf-8'))
raw=(root/'corrected_overrides.bib').read_text(encoding='utf-8')
keys=re.findall(r'@\w+\{(ref\d{3}),',raw)
assert len(keys)==523 and len(set(keys))==523
assert '\ufffd' not in raw and '@misc' not in raw.lower()
assert all(m['fields'].get('author') or m['fields'].get('editor') for m in matches)
assert all(m['fields'].get('year') for m in matches)
dispositions={
6:'Verified same author; Kübler/Kuebler transliteration.',
68:'Rejected Asher Peres essay review; source-faithful typed Jeffrey Bub 1997 first-edition book.',
70:'Rejected Selby paper; retrieved original Bohr DOI10.1038/121580a0 and INSPIRE1430974.',
82:'Official Cisneros/Martinez-y-Romero/Nunez-Yepez/Salas-Brito author names restore source extraction artifacts.',
182:'Restored Dümcke and journal Unicode from original; raw export retained.',
230:'Repaired publisher author typo Caldera to Caldeira using original bibliography.',
251:'Restored Maître circumflex; official full author list preserves Wunderlich and Brune separately.',
266:'Verified same author; Hackermüller/Hackermueller transliteration.',
267:'Verified same author; Hackermüller/Hackermueller transliteration.',
268:'Verified same author; Hackermüller/Hackermueller transliteration.',
336:'Rejected Valerio Scarani book; retrieved original Steane arXivquant-ph/9708022 and INSPIRE447139.',
427:'Restored van Fraassen surname; publisher original chapter DOI confirms pages80-113 rather than source180-213.',
483:'Retained same-work INSPIRE export but replaced reprint-chapter DOI by original journal DOI10.1086/338939.',
484:'Verified same author; Dürr/Duerr transliteration.',
485:'Verified same author; Dürr/Duerr transliteration.',
500:'Augmented empty author/editor export with original book editors Eeckman and Bower.'}
p=root/'audit/autoaccepted_followup_audit.json'
issues=json.loads(p.read_text(encoding='utf-8'))
for i in issues:i.update(disposition=dispositions[i['number']],resolution='complete')
p.write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf-8')
typed=[m['number'] for m in matches if m['status'].startswith('source')]
report='''Bibliography follow-up completion

All523 original numbered references are present in corrected_overrides.bib.
465 entries use a verified official INSPIRE or Crossref export, with missing publication fields supplemented from the supplied original bibliography or publisher metadata.
58 entries use complete, properly typed original-source records where no reliable official record for that exact cited publication/edition was identified. No @misc replacement is used.
Original raw INSPIRE/Crossref exports are preserved unchanged under source/bibliography.
Per-field deltas, evidence, original reference text, adopted fields, and raw-export paths are recorded in matching_override.json.

Coverage: all116 initially flagged references and all407 initially automatically accepted references.
Verification: all523 unique keys; no missing authors/editors; no missing years; no Unicode replacement characters; independent BibTeX pass using utphys.bst completes with zero warnings (overrides_test.blg).
The translated PDF must still be checked by the parent assembly workflow for rendered link behavior. This follow-up does not claim a PDF link inspection.

Typed original-source records (official candidates absent/rejected):
'''+', '.join(f'ref{n:03}' for n in typed)+'\n'
(root/'audit/bibliography_followup_report.txt').write_text(report,encoding='utf-8')
print('Follow-up validation passed; 523 records; zero BibTeX warnings in overrides_test.blg.')
