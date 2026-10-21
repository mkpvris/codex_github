"""Prepare both existing layouts for a bounded terminology-only rebuild."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]/'tmp/github_sync/repository'
GIT=Path(r'C:\Users\false\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe')
SNAP=ROOT/'qa/toc_title_build_inputs'
SNAP.mkdir(exist_ok=True)
EXT=ROOT/'build_index_extended'
EXT.mkdir(exist_ok=True)
STEM='String_Polchinski1_jp'
for suffix in ['aux','bbl','blg','toc','out','idx','ind','ilg']:
    data=subprocess.check_output([str(GIT),'-C',str(REPO),'show',f'f1725f6d08cbcf6318b1dd484cfbbc4913b3caf4:chatpdf/String_Polchinski1/build/{STEM}.{suffix}'])
    (EXT/f'{STEM}.{suffix}').write_bytes(data)
for variant,filename in [('normal',STEM+'.pdf'),('extended',STEM+'_index_extended.pdf')]:
    target=ROOT/'pdf/history'/('before_toc_titles_'+variant+'.pdf')
    assert not target.exists(), target
    shutil.copy2(ROOT/'pdf'/filename,target)
changes=[]
for p in sorted((ROOT/'sections').glob('*.tex')):
    old=p.read_bytes().decode('utf-8')
    new,n=re.subn(r'\\addcontentsline\{toc\}\{subsection\}\{(?:第\d+章の演習|付録Aの演習)\}',lambda m:r'\addcontentsline{toc}{subsection}{演習問題}',old)
    terms=new.count('無ゴースト定理')
    new=new.replace('無ゴースト定理','ノーゴースト定理')
    if new!=old:
        p.write_bytes(new.encode('utf-8'))
        changes.append({'file':str(p.relative_to(ROOT)),'toc_titles':n,'no_ghost_terms':terms,'before_sha256':hashlib.sha256(old.encode()).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert sum(x['toc_titles'] for x in changes)==6
assert sum(x['no_ghost_terms'] for x in changes)==7
for name in ['index_legacy.tex','entries.json','page_mapping_research.json','page_spans.json']:
    p=ROOT/'indexing'/name
    data=p.read_bytes()
    p.write_bytes(data.replace('無ゴースト定理'.encode(),'ノーゴースト定理'.encode()))
for variant,folder in [('normal',ROOT/'build'),('extended',EXT)]:
    for suffix in ['idx','ind']:
        p=folder/f'{STEM}.{suffix}'
        p.write_bytes(p.read_bytes().replace('無ゴースト定理'.encode(),'ノーゴースト定理'.encode()))
        shutil.copy2(p,SNAP/f'{variant}.{suffix}')
    p=folder/f'{STEM}.toc'
    text=p.read_text(encoding='utf-8').replace('無ゴースト定理','ノーゴースト定理')
    text=re.sub(r'(\\contentsline \{subsection\}\{)(?:第\d+章の演習|付録Aの演習)(\})',lambda m:m[1]+'演習問題'+m[2],text)
    p.write_text(text,encoding='utf-8')
for options in [[],['--extended-contents']]:
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'assemble.py'),*options],cwd=ROOT,check=True)
report={'changes':changes,'source_toc_titles_changed':6,'source_terminology_replacements':7,'existing_index_pages_preserved':True}
(ROOT/'qa/toc_title_source_edits.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
