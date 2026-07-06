"""Spike — characterize POD Go's per-model DSP loads from the catalog snapshot, as the
basis for deriving the DSP/free-block rules. Reads the versioned snapshot (no app needed).
"""
import json
import os
import statistics
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNAP = os.path.join(REPO, "registry", "model-catalog", "podgo-edit-2.50.json")

ms = json.load(open(SNAP, encoding="utf-8"))["models"]
loads = {sid: m for sid, m in ms.items() if m.get("dsp_load") is not None}

bycat = defaultdict(list)
for sid, m in loads.items():
    bycat[m["category"]].append(m["dsp_load"])

print("=== DSP load per block type (POD Go 2.50) ===")
print(f"{'block type':14}{'n':>4}{'min':>7}{'median':>8}{'max':>7}")
for c in sorted(bycat):
    v = bycat[c]
    print(f"{c:14}{len(v):>4}{min(v):>7.2f}{statistics.median(v):>8.2f}{max(v):>7.2f}")

allv = [m["dsp_load"] for m in loads.values()]
print(f"\nglobal: n={len(allv)}  min={min(allv)}  max={max(allv)}")

print("\n=== 'fixed' category (candidate built-in blocks) ===")
for m in sorted((m for m in loads.values() if m["category"] == "fixed"),
                key=lambda x: x["name"]):
    print(f"  {m['name']:22} load={m['dsp_load']:6}  ({len(m['params'])} params)")

print("\n=== 'io' category ===")
for m in (m for m in ms.values() if m["category"] == "io"):
    print(f"  {m['name']:22} load={m.get('dsp_load')}")

print("\n=== heaviest 12 blocks ===")
for m in sorted(loads.values(), key=lambda x: x["dsp_load"], reverse=True)[:12]:
    print(f"  {m['dsp_load']:6.2f}  {m['category']:10} {m['name']}")

print("\n=== lightest 8 blocks ===")
for m in sorted(loads.values(), key=lambda x: x["dsp_load"])[:8]:
    print(f"  {m['dsp_load']:6.2f}  {m['category']:10} {m['name']}")
