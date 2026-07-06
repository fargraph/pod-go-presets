"""Spike — understand POD Go Edit's catalog structure: what PGModelCatalog.json lists
(the UI picker) vs the raw *.models defs, the mono/stereo split, and why amps/cabs/preamps
show 0 'ui_exposed'."""
import glob
import json
import os
from collections import Counter

R = os.environ.get("POD_GO_EDIT_RESOURCES",
                   "/Applications/Line6/POD Go Edit.app/Contents/Resources")

pg = json.load(open(os.path.join(R, "PGModelCatalog.json"), encoding="utf-8"))
print("=== PGModelCatalog.json categories (the UI model picker) ===")
ui_ids, total = set(), 0
for c in pg["categories"]:
    ms = c.get("models", [])
    total += len(ms)
    for m in ms:
        ui_ids.add(m.get("id"))
    print(f"  id={c.get('id'):>2}  {str(c.get('shortName')):14} {str(c.get('name')):24} models={len(ms)}")
print(f"total models listed in PGModelCatalog: {total}")

# raw .models by category + mono/stereo suffix
allids = []
for f in sorted(glob.glob(os.path.join(R, "*.models"))):
    cat = os.path.basename(f)[:-len(".models")]
    d = json.load(open(f, encoding="utf-8"))
    for m in d:
        if isinstance(m, dict) and m.get("symbolicID"):
            allids.append((cat, m["symbolicID"]))

print("\n=== symbolicID suffix pattern across all *.models ===")
suf = Counter("Stereo" if i.endswith("Stereo") else "Mono" if i.endswith("Mono")
              else "other" for _, i in allids)
print(f"  {dict(suf)}   (total {len(allids)})")

print("\n=== per .models category: how many appear in the UI picker? ===")
bycat = {}
for cat, i in allids:
    bycat.setdefault(cat, []).append(i)
for cat in sorted(bycat):
    in_ui = sum(1 for i in bycat[cat] if i in ui_ids)
    mono = sum(1 for i in bycat[cat] if i.endswith("Mono"))
    stereo = sum(1 for i in bycat[cat] if i.endswith("Stereo"))
    print(f"  {cat:14} total={len(bycat[cat]):3}  in_UI={in_ui:3}  "
          f"mono={mono:3} stereo={stereo:3} other={len(bycat[cat])-mono-stereo:3}")
