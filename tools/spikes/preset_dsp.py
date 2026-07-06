"""Spike — sum each registry preset's DSP load (via the catalog) and split by working/
broken status, to derive/validate POD Go's DSP budget. Reads the snapshot; no app needed.
"""
import json
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import podgo          # noqa: E402
import podgo_models   # noqa: E402

REPO = os.path.dirname(TOOLS)
cat = podgo_models.load()
IO_BASELINE = 10.99 * 2   # Input + Output blocks are always present

combos = json.load(open(os.path.join(REPO, "registry", "combinations.json"),
                       encoding="utf-8"))["presets"]

rows = []
for p in combos:
    path = os.path.join(REPO, p["file"])
    try:
        data, _ = podgo.load_pgp(path)
    except (OSError, ValueError):
        continue
    mids = podgo.models(data)
    block_load, unknown = 0.0, []
    for mid in mids:
        m = cat.get(mid)
        if m and m.get("dsp_load") is not None:
            block_load += m["dsp_load"]
        else:
            unknown.append(mid)
    b = p.get("blocks", {})
    rows.append({"status": p["status"], "fb": p["free_blocks"], "tax": p["taxonomy"],
                 "amp": b.get("amp"), "cab": b.get("cab"),
                 "n_blocks": len(mids), "block_load": round(block_load, 1),
                 "total": round(block_load + IO_BASELINE, 1), "unknown": unknown})

print(f"I/O baseline (Input+Output) = {IO_BASELINE:.1f}\n")
for st in ("working", "broken", "untested"):
    sub = [r for r in rows if r["status"] == st]
    if not sub:
        continue
    tots = [r["total"] for r in sub]
    print(f"=== {st.upper()}  (n={len(sub)})   total DSP: "
          f"min={min(tots)}  max={max(tots)}  avg={sum(tots)/len(tots):.1f} ===")
    for r in sorted(sub, key=lambda x: x["total"]):
        amp = "amp" if r["amp"] else "NO-AMP"
        cab = "cab" if r["cab"] else "no-cab"
        print(f"   total={r['total']:>5}  block_load={r['block_load']:>5}  "
              f"free={r['fb']:>2}  blocks={r['n_blocks']:>2}  "
              f"{r['tax']:<16} {amp:<6} {cab}")
    print()
