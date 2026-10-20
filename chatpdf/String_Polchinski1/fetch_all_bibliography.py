"""Read public INSPIRE metadata and exports for the supplied bibliography.

Only GET requests to https://inspirehep.net are issued. No credentials are read,
no remote data is changed, and local output is confined to source/bibliography.
Candidates are retained for review; this program never silently selects a record.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import difflib
import json
import re
import time
import unicodedata
import sys
import urllib.parse
import urllib.request

root = Path(__file__).resolve().parent
out = root / "source" / "bibliography" / "all_candidates"
out.mkdir(exist_ok=True)
references = json.loads((out.parent / "original_reference_list.json").read_text(encoding="utf-8"))["references"]

def norm(text):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower())

def get(url):
    if not url.startswith("https://inspirehep.net/"):
        raise ValueError("Only public INSPIRE URLs are permitted")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=40) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 + attempt)

def task(ref):
    number = ref["original_order"]
    result_path = out / f"{number:03d}_candidates.json"
    if result_path.exists():
        return json.loads(result_path.read_text(encoding="utf-8"))
    title = ref["title_original"]
    original = ref["original_text"]
    surname = ref["authors_original"].split(",")[0].strip()
    arxiv = ref["arxiv_identifiers_in_source"]
    queries = []
    if arxiv:
        queries.append("arxiv:" + arxiv[0])
    if surname == "Weinberg" and ref["year_original"] == "1964":
        queries.append("doi:10.1103/PhysRev.135.B1049")
    query_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    query_title = re.sub(r"[^A-Za-z0-9 =]", " ", query_title)
    queries.append('t "' + " ".join(query_title.split()) + '"')
    queries.append(f"a {surname} and date {ref['year_original'][:4]}")
    queries_used = []
    hits_by_id = {}
    for query in queries:
        url = "https://inspirehep.net/api/literature?" + urllib.parse.urlencode({"q": query, "size": 25})
        data = json.loads(get(url))
        queries_used.append(url)
        for hit in data.get("hits", {}).get("hits", []):
            meta = hit["metadata"]
            titles = [t["title"] for t in meta.get("titles", [])]
            score = max([difflib.SequenceMatcher(None, norm(title), norm(t)).ratio() for t in titles] or [0])
            if score >= .46 or query.startswith(("arxiv:", "doi:")):
                hits_by_id[hit["id"]] = {
                    "id": hit["id"], "title_score": round(score, 4),
                    "titles": titles, "authors": [a.get("full_name") for a in meta.get("authors", [])],
                    "publication_info": meta.get("publication_info"), "imprints": meta.get("imprints"),
                    "dois": meta.get("dois"), "arxiv_eprints": meta.get("arxiv_eprints"),
                    "isbns": meta.get("isbns"), "document_type": meta.get("document_type"),
                }
        if any(h["title_score"] > .94 for h in hits_by_id.values()):
            break
    candidates = sorted(hits_by_id.values(), key=lambda h: -h["title_score"])[:5]
    for hit in candidates:
        url = f"https://inspirehep.net/api/literature/{hit['id']}?format=bibtex"
        name = f"{number:03d}_{hit['id']}.bib"
        (out / name).write_bytes(get(url))
        hit["bibtex_url"] = url
        hit["bib_file"] = name
    result = {"original_order": number, "original_text": original,
              "title_original": title, "queries": queries_used,
              "candidates": candidates, "selection_status": "requires_review"}
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result

if "--followup" in sys.argv:
    plans = {
        38: ['t "Scale and Conformal" and a Gatto', 'a Gatto and date 1973'],
        69: ['a Martinec and t "gravity" and date 1991->1993', 't "solvable string"'],
        72: ['t "Measure for" and a Moore', 'j "Nucl.Phys.B,266,58"'],
        73: ['t "Tata" and a Mumford'],
        87: ['a Quigg and date 1983 and t "Gauge"', 'isbn:0805360204'],
        94: ['t "first 15 years"', 't "Superstrings" and a Schwarz and date 1985'],
        104: ['a Thorn and t "String field theory"', 'j "Phys.Rept.,175,1"'],
    }
    followdir = out.parent / "followup"
    followdir.mkdir(exist_ok=True)
    for number, queries in plans.items():
        target = followdir / f"{number:03d}_candidates.json"
        if target.exists():
            print(f"{number:03d}: cached", flush=True)
            continue
        hits, used = {}, []
        for query in queries:
            url = "https://inspirehep.net/api/literature?" + urllib.parse.urlencode({"q": query, "size": 50})
            data = json.loads(get(url))
            used.append(url)
            for hit in data.get("hits", {}).get("hits", []):
                meta = hit["metadata"]
                record_id = hit["id"]
                name = f"{number:03d}_{record_id}.bib"
                bib_url = f"https://inspirehep.net/api/literature/{record_id}?format=bibtex"
                if record_id not in hits:
                    (followdir / name).write_bytes(get(bib_url))
                hits[record_id] = {
                    "id": record_id,
                    "titles": [t["title"] for t in meta.get("titles", [])],
                    "authors": [a.get("full_name") for a in meta.get("authors", [])],
                    "publication_info": meta.get("publication_info"),
                    "imprints": meta.get("imprints"), "dois": meta.get("dois"),
                    "isbns": meta.get("isbns"), "bib_file": name, "bibtex_url": bib_url,
                }
        target.write_text(json.dumps({"original_order": number, "queries": used,
                                     "candidates": list(hits.values())},
                                    ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{number:03d}: {len(hits)} followup candidate(s)", flush=True)
    sys.exit(0)

results, errors = [], []
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(task, ref): ref["original_order"] for ref in references}
    for future in as_completed(futures):
        number = futures[future]
        try:
            result = future.result()
            results.append(result)
            print(f"{number:03d}: {len(result['candidates'])} candidate(s)", flush=True)
        except Exception as exc:
            errors.append({"original_order": number, "error": str(exc)})
            print(f"{number:03d}: retrieval error: {exc}", flush=True)
results.sort(key=lambda r: r["original_order"])
(out / "all_candidates.json").write_text(json.dumps({"results": results, "errors": errors}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Saved {len(results)} searches; {len(errors)} retrieval errors. Records still require comparison.")
