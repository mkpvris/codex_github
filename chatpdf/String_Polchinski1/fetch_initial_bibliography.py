"""Download official INSPIRE exports; retain metadata for source matching."""
from pathlib import Path
import json
import urllib.parse
import urllib.request
import time
from concurrent.futures import ThreadPoolExecutor

root = Path(__file__).resolve().parent
out = root / "source" / "bibliography"
out.mkdir(exist_ok=True)
jobs = [
    ("misner1973", 't "Gravitation" and a Misner', "Misner, Thorne, Wheeler (1973), Gravitation"),
    ("gsw1987v2", 't "Superstring Theory" and a Witten and date 1987', "Green, Schwarz, Witten (1987), volume 2"),
    ("quigg1983", 't "Gauge Theories of the Strong" and a Quigg', "Quigg (1983), Gauge Theories of the Strong, Weak, and Electromagnetic Interactions"),
    ("cheng1991", 't "Gauge Theory of Elementary Particle Physics" and a Cheng', "Cheng and Li (1991), Gauge Theory of Elementary Particle Physics"),
    ("weinberg1979", 't "Ultraviolet Divergences in Quantum Theories of Gravitation"', "Weinberg (1979), Einstein Centenary Survey, pp.790-831"),
    ("goddard1973", 'doi:10.1016/0550-3213(73)90223-X', "Goddard, Goldstone, Rebbi, Thorn (1973), Nucl.Phys.B56,109"),
    ("rebbi1974", 't "Dual Models and Relativistic Quantum Strings"', "Rebbi (1974), Phys.Rept.12,1"),
    ("scherk1975", 't "An Introduction to the Theory of Dual Models and Strings"', "Scherk (1975), Rev.Mod.Phys.47,123"),
    ("brink1973", 'doi:10.1016/0370-2693(73)90048-8', "Brink and Nielsen (1973), Phys.Lett.B45,332"),
    ("weinberg1964", 't "Photons and Gravitons in S Matrix Theory"', "Weinberg (1964), Phys.Rev.135,B1049"),
]

def fetch(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)

def task(job):
    key, query, original = job
    search_url = "https://inspirehep.net/api/literature?" + urllib.parse.urlencode({"q": query, "size": 15})
    raw = fetch(search_url)
    (out / f"{key}_search.json").write_bytes(raw)
    data = json.loads(raw)
    matches = []
    for hit in data.get("hits", {}).get("hits", []):
        record_id = hit["id"]
        meta = hit["metadata"]
        export_url = f"https://inspirehep.net/api/literature/{record_id}?format=bibtex"
        bib = fetch(export_url)
        (out / f"{key}_{record_id}.bib").write_bytes(bib)
        matches.append({
            "record_id": record_id, "bibtex_url": export_url,
            "titles": meta.get("titles"), "authors": [a.get("full_name") for a in meta.get("authors", [])],
            "publication_info": meta.get("publication_info"), "imprints": meta.get("imprints"),
            "dois": meta.get("dois"), "isbns": meta.get("isbns"),
            "bib_file": f"{key}_{record_id}.bib",
        })
    return {"key": key, "original": original, "query_url": search_url, "matches": matches}

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as pool:
        result = list(pool.map(task, jobs))
    (out / "initial_candidates.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
