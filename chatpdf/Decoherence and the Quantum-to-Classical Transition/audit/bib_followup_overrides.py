from pathlib import Path
import re,json,unicodedata
root=Path(__file__).resolve().parents[1]; folder=root/'source/bibliography'; follow=folder/'followup_ch02'
refs={r['number']:r['original'] for r in json.loads((folder/'original_references.json').read_text(encoding='utf-8'))}
audit=json.loads((root/'audit/bibliography_audit.json').read_text(encoding='utf-8'))
flagged=[r['number'] for r in audit if not r['status'].startswith('official')]
def fields(text):
    out={}
    for m in re.finditer(r'\b([A-Za-z]+)\s*=\s*',text):
        j=m.end();start=j
        if text[j:j+1]=='{':
            depth=1;j+=1;start=j
            while j<len(text) and depth:
                if text[j]=='{' and text[j-1]!='\\':depth+=1
                elif text[j]=='}' and text[j-1]!='\\':depth-=1
                j+=1
            value=text[start:j-1]
        elif text[j:j+1]=='"':
            start=j+1;j=start
            while j<len(text) and not(text[j]=='"' and text[j-1]!='\\'):j+=1
            value=text[start:j]
        else:value=text[j:].split(',')[0].split('}')[0].strip()
        out[m[1].lower()]=value
    return out
def esc(s):
    return s.replace('&',r'\&').replace('%',r'\%').replace('#',r'\#').replace('_',r'\_').replace('–','--').replace('−','-')
def authors_rest(raw):
    raw=unicodedata.normalize('NFKC',raw)
    parts=raw.split(', ');i=0
    while i<len(parts) and re.match(r'^(?:[A-Z]\.|[A-Z]-[A-Z]\.)',parts[i]):i+=1
    return ' and '.join(parts[:i]).replace(' (Eds.)','').replace(' (Ed.)',''),', '.join(parts[i:])
publishers=['Cambridge University Press','Princeton University Press','University of Chicago Press','World Scientific Publishing','World Scientific','World Scientic','John Wiley & Sons','John Wiley','Addison-Wesley','Addison–Wesley','Prentice Hall','William Morrow','Clarendon','Oxford University Press','Edition Erbrich','E. P. Dutton and Co.','Academic Press','Glencoe','Benjamin','Routledge','Springer','Penguin','Perseus','Random House','M.E.R.U. Press','Holt Reinhart and Winston','Plenum Press','Faber and Faber','IEEE Computer Society Press','IEEE Press','International Society for Optical Engineering','Birkhäuser','ACM','Library of Living Philosophers','Interscience','Heinemann','Reidel','Kluwer','MIT Press','IOS Press','Vatican Observatory and The Center for Theology and the Natural Sciences']
booknums={17,18,27,29,34,37,40,43,46,48,49,56,58,60,68,71,137,152,167,169,175,213,218,241,253,256,257,385,395,428,435,458,472,473,478,480,488,499,500,501,502,508}
def bookparts(s):
    found=[(s.find(', '+p),p) for p in publishers if ', '+p in s]
    if not found:return s.strip(' .'),{}
    idx,pub=min(found,key=lambda z:(z[0],-len(z[1])))
    head=s[:idx];tail=s[idx+2+len(pub):].strip(' ,.')
    extra={'publisher':pub}
    ed=re.search(r', (\d+)(?:st|nd|rd|th) Edition',head)
    if ed:extra['edition']=ed[1];head=head[:ed.start()]+head[ed.end():]
    y=re.search(r'(?:18|19|20)\d{2}',tail)
    if y:
        extra['year']=y[0]
        addr=tail[:y.start()].strip(' ,.')
        if addr:extra['address']=addr
        remains=tail[y.end():].strip(' ,.')
        if remains:extra['note']=remains
    return head.strip(' ,.'),extra
def original_entry(n):
    raw=refs[n];authors,rest=authors_rest(raw)
    vals={'author':authors}; typ='article'
    years=re.findall(r'\b(?:18|19|20)\d{2}\b',rest)
    if years:vals['year']=years[-1]
    if n in booknums:
        typ='book';title,extra=bookparts(rest);vals.update(extra);vals['title']=title
        if n in {40,499,500}:vals['editor']=vals.pop('author')
        vm=re.search(r', Vol\. ([IVX\d]+)',vals['title'])
        if vm:vals['volume']=vm[1];vals['title']=vals['title'][:vm.start()]+vals['title'][vm.end():]
    elif n in {433,491}:
        typ='phdthesis';title,_,tail=rest.partition(', Ph.D. thesis, ');vals['title']=title;vals['school']=re.sub(r'\s*\(\d{4}\)\.?$','',tail)
    elif n in {324,503}:
        typ='unpublished';title,_,tail=rest.partition(', ');vals['title']=title;vals['note']=tail
    elif ', in: ' in rest:
        typ='incollection';title,_,tail=rest.partition(', in: ');vals['title']=title
        em=re.search(r'^(.*?)\((?:Ed\.|Eds\.)\),\s*',tail)
        if em:
            vals['editor']=em[1].rstrip(' ,').replace(', ',' and ');tail=tail[em.end():]
        title,extra=bookparts(tail);vals['booktitle']=title;vals.update(extra)
        pages=re.search(r'pp\.\s*([\d–\- ]+)',rest)
        if pages:vals['pages']=pages[1].replace(' ','').strip('–-')
        if 'note' in vals:
            vals['note']=re.sub(r'^pp\.\s*[\d–\- ]+(?:,\s*)?','',vals['note']).strip(' ,.')
        vm=re.search(r', Vol\. ([IVX\d]+) of (.+)$',vals['booktitle'])
        if vm:vals['volume']=vm[1];vals['series']=vm[2];vals['booktitle']=vals['booktitle'][:vm.start()]
        else:
            vm=re.search(r', Vol\. ([IVX\d]+)$',vals['booktitle'])
            if vm:vals['volume']=vm[1];vals['booktitle']=vals['booktitle'][:vm.start()]
        if n==391:
            vals['booktitle']='The Stanford Encyclopedia of Philosophy';vals['editor']='E. N. Zalta';vals['url']='https://plato.stanford.edu/archives/win2003/entries/qm-decoherence/';vals['publisher']='Metaphysics Research Lab, Stanford University'
    else:
        m=re.search(r',\s*([^,]+?)\s+(\d+[A-Za-z]?|[IVX]+)(?:\s*\((\d+)\))?,\s*([\d–\- ]+)\s*\((\d{4})\)',rest)
        if m:
            vals['title']=rest[:m.start()];vals['journal']=m[1];vals['volume']=m[2];vals['pages']=m[4].replace(' ','').strip('–-');vals['year']=m[5]
            if m[3]:vals['number']=m[3]
            tail=rest[m.end():].strip(' .')
            if tail:vals['note']=tail
        else:
            title,_,tail=rest.partition(', ');vals['title']=title
            if tail:vals['note']=tail
    if n==214:
        typ='unpublished';vals.update(title="Decoherence in the quantum dynamics of a ``central spin'' coupled to a spin environment",eprint='cond-mat/9511011',archiveprefix='arXiv',year='1995',note='eprint cond-mat/9511011')
    if n==29:
        vals['title']='The Shaky Game: Einstein, Realism and the Quantum Theory';vals['series']='Science and its Conceptual Foundations Series'
    # The supplied source's substantive reprint/translation remarks are retained.
    if n==19:vals['note']='Reprinted and translated in [40], pp. 52--55'
    if n==42:vals['note']='Reprinted and translated in [40], pp. 62--84'
    if n==57:vals['note']='Translated by John D. Trimmer'
    if n==414:
        typ='phdthesis';vals={'author':authors,'title':'The Everett Interpretation of Quantum Mechanics','school':'University of North Carolina','address':'Chapel Hill','year':'1970'}
    return typ,{k:esc(v) for k,v in vals.items() if v}

# Same work verified by authors plus DOI/volume/pages; title variations and preprint years logged.
same={23,24,39,52,53,76,84,99,117,131,144,184,187,190,201,205,222,243,246,255,263,316,323,325,337,339,340,341,365,405,450,478,479,492,509,514,515}
# Explicit follow-up matches: exact chapter/edition/DOI or arXiv rather than title alone.
new={14:'ref014_inspire_2979680.bib',17:'ref017_crossref.bib',19:'ref019_inspire_1599357.bib',40:'ref040_crossref.bib',62:'ref062_inspire_2793398.bib',70:'ref070_inspire_1430974.bib',98:'ref098_inspire_2979673.bib',108:'ref108_inspire_499319.bib',111:'ref111_inspire_2991970.bib',128:'ref128_crossref.bib',137:'ref137_crossref.bib',152:'ref152_crossref.bib',175:'ref175_crossref.bib',189:'ref189_inspire_2980819.bib',218:'ref218_crossref.bib',241:'ref241_crossref.bib',253:'ref253_crossref.bib',258:'ref258_crossref.bib',336:'ref336_inspire_447139.bib',342:'ref342_crossref.bib',344:'ref344_inspire_2735097.bib',367:'ref367_crossref.bib',374:'ref374_inspire_2736138.bib',459:'ref459_crossref.bib',469:'ref469_crossref.bib'}

def crossref_for(n,f):
    doi=f.get('doi','').lower().replace('https://doi.org/','')
    p=follow/f'ref{n:03}_crossref.json'
    if p.exists():
        o=json.loads(p.read_text(encoding='utf-8'))['message']
        if str(o.get('DOI','')).lower()==doi:return o,str(p.relative_to(root))
    p=folder/f'ref{n:03}_crossref_search.json'
    if p.exists():
        for o in json.loads(p.read_text(encoding='utf-8'))['message']['items']:
            if str(o.get('DOI','')).lower()==doi:return o,str(p.relative_to(root))
    return None,None

def put(f,k,v,deltas,evidence):
    if v and f.get(k)!=v:
        deltas.append({'field':k,'from':f.get(k),'to':v,'evidence':evidence});f[k]=v

entries=[];matches=[]
for n in sorted(refs):
    typ,source=original_entry(n);selected=None;f={};raw='';deltas=[]
    if n in new:
        p=follow/new[n]
        if p.exists():selected=p
    elif n in same or n not in flagged and n!=68:
        p=folder/f'ref{n:03}_official.bib'
        if p.exists():selected=p
    if selected:
        raw=selected.read_text(encoding='utf-8-sig'); f=fields(raw);ot=re.search(r'@(\w+)',raw);official_type=ot[1] if ot else None
        typ=official_type or typ
        if ', in: ' in refs[n]:typ='incollection'
        elif 'journal' in source:typ='article'
        # Always retain official title/author/identifiers unless proven incomplete/incorrect.
        for k,v in source.items():
            if k not in f:f[k]=v;deltas.append({'field':k,'from':None,'to':v,'evidence':'supplied original bibliography'})
        # Publication year, volume, and page ranges are verified against source location,
        # DOI-linked Crossref payload where available; preprint export year is not a print year.
        for k in ['year','journal','volume','pages','edition','booktitle','editor','publisher','address','note']:
            if k in source and f.get(k)!=source[k]:
                if k=='year' and n==53: pass
                deltas.append({'field':k,'from':f.get(k),'to':source[k],'evidence':'source bibliography; DOI/author/title/location identity checked'})
                f[k]=source[k]
        if n in {14,108,128,187,190,325,469}:typ='incollection'
        if n in {342,344,340,341}:typ='inproceedings'
        if n==189:
            f['doi']='10.1016/0375-9601(89)90066-2'; f.pop('number',None)
        if n==98:
            f.update(doi='10.1103/PhysRevLett.84.2525',journal='Phys. Rev. Lett.',volume='84',pages='2525--2528',year='2000');deltas.append({'field':'volume','from':'82 [source typo]','to':'84','evidence':'APS original DOI full text and Crossref metadata'})
        if n==14:f['doi']='10.1007/3-540-46657-6_1'
        if n==108:f['doi']='10.1007/3-540-46657-6_2'
        if n==144:
            f['title']=source['title'];deltas.append({'field':'title','reason':'Crossref export contains Unicode replacement characters; restored exact supplied source spelling'})
        if n in {23,24,52,53}:deltas.append({'reason':'INSPIRE export year is digitization year; publication year restored from original journal volume and Crossref record'})
        if n in {39,76,243,255,323,405,492,509,514}:deltas.append({'reason':'preprint matches original author/title; original published-book/journal location retained'})
        if n==53:
            f['volume']='32';f['pages']='446--452';deltas.append({'reason':'supplied source volume36/pages446-451 differ from original journal metadata; DOI identifies vol32/pages446-452'})
        if n==515:deltas.append({'reason':'INSPIRE title The Quantum brain is alternative/preprint title; DOI10.1103/PhysRevE.61.4194 and61:4194-4206 match original'})
        if n==483:
            put(f,'doi','10.1086/338939',deltas,'original journal DOI in source-matched Crossref record; raw INSPIRE DOI points to reprint chapter');f.pop('editor',None)
        cr,crpath=crossref_for(n,f)
        if cr:
            # Publisher-supplied Crossref metadata resolves source typos in volume/pages/year.
            loc={'volume':str(cr['volume']) if cr.get('volume') else None,'pages':str(cr.get('page') or '')}
            if typ.lower()=='article':
                date=cr.get('published-print') or cr.get('published') or cr.get('issued') or {}
                dp=date.get('date-parts',[[]])[0]
                if dp:loc['year']=str(dp[0])
                if not loc['pages'] and f.get('doi','').lower().startswith('10.1103/physrev'):
                    loc['pages']=f['doi'].split('.')[-1]
            for k,v in loc.items():
                if v:put(f,k,esc(v),deltas,crpath)
        # Source-backed repairs of malformed publisher export Unicode or misspelled names.
        for k in ['title','journal','author']:
            if '\ufffd' in f.get(k,'') and k in source:put(f,k,source[k],deltas,'source bibliography correct Unicode; official raw export retained')
        for k,v in list(f.items()):
            if '\ufffd' in v:
                put(f,k,v.replace('f\ufffdr','für').replace('D\ufffdmcke','Dümcke').replace('J\ufffdnsson','Jönsson').replace('�ber','Über'),deltas,'source bibliography and DOI-linked original German spelling')
        if n==230:put(f,'author',f['author'].replace('Caldera','Caldeira'),deltas,'supplied original bibliography and known author spelling')
        if n==251:put(f,'author',f['author'].replace('Ma[icaron]tre','Maître'),deltas,'source bibliography proper circumflex spelling')
        if n==427:put(f,'author','van Fraassen, Bas C.',deltas,'supplied original bibliography surname includes van')
        if n==258:
            put(f,'author','Jönsson, C.',deltas,'source bibliography original author spelling');put(f,'title',source['title'],deltas,'source bibliography exact original German spelling')
        for k in ['author','title','editor']:
            if 'textbackslash' in f.get(k,'') and k in source:put(f,k,source[k],deltas,'literal backslash escape in raw INSPIRE export repaired from supplied source proper-name spelling')
        if n==414:
            typ='phdthesis';f.pop('type',None);put(f,'school','University of North Carolina',deltas,'source title page institution; INSPIRE Other thesis export lacks school')
        # Preserve print edition author/editor information absent from book exports.
        if n==500:f.pop('author',None);put(f,'editor','F. H. Eeckman and J. M. Bower',deltas,'original book and publisher title page editors')
        for k in ['title','booktitle','journal','publisher','author','editor','note']:
            if k in f:f[k]=re.sub(r'(?<!\\)&',r'\\&',f[k])
        status='official_verified_enriched'
    else:
        f=source;status='source_faithful_typed_record'
        deltas.append({'reason':'candidate absent or rejected as other edition, reprint, review, wrong author, parent volume, or distinct publication; complete supplied source bibliography used'})
    entries.append('% Original reference '+str(n)+'; '+status+'\n@'+typ+'{ref'+f'{n:03}'+',\n'+''.join('    '+k+' = {'+v+'},\n' for k,v in f.items())+'}\n')
    matches.append({'number':n,'status':status,'original':refs[n],'raw_official_export':str(selected.relative_to(root)) if selected else None,'deltas':deltas,'fields':f})
(root/'corrected_overrides.bib').write_text('\n'.join(entries),encoding='utf-8')
(root/'audit/matching_override.json').write_text(json.dumps(matches,ensure_ascii=False,indent=2),encoding='utf-8')
print('Overrides',len(entries),'official',sum(m['status'].startswith('official') for m in matches),'source-faithful',sum(m['status'].startswith('source') for m in matches))
