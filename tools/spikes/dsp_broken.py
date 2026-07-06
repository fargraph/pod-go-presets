"""Spike — for every BROKEN registry preset, show its block-by-block DSP and classify
the failure as structural (amp removed) vs DSP (structurally sound but over budget)."""
import json
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import podgo          # noqa: E402
import podgo_models   # noqa: E402

REPO = os.path.dirname(TOOLS)
cat = podgo_models.load()
IO = 10.99 * 2
STRUCTURAL_TAX = {"no-amp", "no-amp-and-cab"}

combos = json.load(open(os.path.join(REPO, "registry", "combinations.json"),
                       encoding="utf-8"))["presets"]

for p in combos:
    if p["status"] != "broken":
        continue
    data, _ = podgo.load_pgp(os.path.join(REPO, p["file"]))
    parts = []
    for mid in podgo.models(data):
        m = cat.get(mid)
        parts.append(((m or {}).get("dsp_load") or 0.0, podgo.builtin_of(mid) or "free",
                      (m or {}).get("name", "?"), mid))
    total = sum(x[0] for x in parts) + IO
    structural = p["taxonomy"] in STRUCTURAL_TAX
    verdict = "STRUCTURAL (amp removed)" if structural else \
              ("DSP-OVER-BUDGET" if total > 82 else "sound+low-DSP (other cause)")
    print(f"\n{p['id']}  [{p['taxonomy']}] free={p['free_blocks']} "
          f"total_dsp={total:5.1f}  -> {verdict}")
    for load, tag, name, _mid in sorted(parts, reverse=True):
        print(f"     {load:5.1f}  {tag:8} {name}")
