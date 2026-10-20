from fetch_initial_bibliography import task, out
from concurrent.futures import ThreadPoolExecutor
import json

jobs = [
    ("quigg1983_more", 'a Quigg and date 1983', "Quigg (1983), first-edition book"),
    ("weinberg1964_more", 'doi:10.1103/PhysRev.135.B1049', "Weinberg (1964), Photons and gravitons in S matrix theory"),
]
with ThreadPoolExecutor(max_workers=2) as pool:
    result = list(pool.map(task, jobs))
(out / "followup_candidates.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
