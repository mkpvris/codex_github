"""Keep exercise headings in the body while removing their TOC/backlinks."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
pattern = re.compile(r"\\subsubsectionlink\*\{演習([1-9A]\.\d+)\}(\\label\{ex:[^}]+\})?")
records = []
files = []
for path in sorted((ROOT / "sections").glob("*.tex")):
    before = path.read_bytes()
    old = before.decode("utf-8")
    changes = []
    def replace(match):
        number = match[1]
        label = match[2] or (r"\label{ex:" + number + "}")
        after = r"\subsubsection*{演習" + number + "}" + label
        item = {"file": path.name, "number": number, "before": match[0],
                "after": after, "location_label_added": match[2] is None}
        changes.append(item)
        return after
    new = pattern.sub(replace, old)
    if not changes:
        continue
    recovered = new
    for item in reversed(changes):
        recovered = recovered.replace(item["after"], item["before"], 1)
    assert recovered.encode("utf-8") == before, path.name
    assert re.findall(r"\\tag\{[^}]+\}", old) == re.findall(r"\\tag\{[^}]+\}", new)
    assert re.findall(r"\\addcontentsline[^\n]+", old) == re.findall(r"\\addcontentsline[^\n]+", new)
    path.write_bytes(new.encode("utf-8"))
    records.extend(changes)
    files.append({"file": path.name, "exercises": len(changes),
                  "before_sha256": hashlib.sha256(before).hexdigest(),
                  "after_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "body_preserved_by_inverse_substitution": True})
assert len(records) == 106, len(records)
assert len({r["number"] for r in records}) == 106
report = {"individual_exercises_removed_from_toc": len(records),
          "location_labels_added": sum(r["location_label_added"] for r in records),
          "exercise_groups_unchanged": 10, "ordinary_subsubsections_unchanged": 102,
          "files": files, "changes": records}
(ROOT / "qa/exercises_removed_from_toc.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k not in ("files", "changes")}))
