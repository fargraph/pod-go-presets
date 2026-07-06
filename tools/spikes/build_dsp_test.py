"""Spike (B) — construct a structurally-valid, over-DSP-budget test preset.

Takes a recorded-WORKING with-amp-cab base (6_V--E-_AC: Volume/Amp/EQ/Cab + 6 empty free
slots) and fills those 6 slots with real heavy effect blocks copied verbatim (valid
params) from an existing preset. The result is byte-for-byte the same STRUCTURE as a
working preset — same built-ins, same free-block count, no duplicates, no phantom-7 — so
the ONLY variable vs. the working base is DSP load. If it breaks on hardware, DSP is
isolated as the cause.

Writes data-presets/demonstrations/dsp-over-budget-test.pgp. UNTESTED until hardware.
"""
import json
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import podgo          # noqa: E402
import podgo_models   # noqa: E402

REPO = os.path.dirname(TOOLS)
BASE = os.path.join(REPO, "presets/with-amp-cab/6_V--E-_AC.pgp")
SRC = os.path.join(REPO, "presets/with-amp-cab/6_V----_AC_bad.pgp")
OUT = os.path.join(REPO, "data-presets/demonstrations/dsp-over-budget-test.pgp")
cat = podgo_models.load()
IO = 10.99 * 2

base, _ = podgo.load_pgp(BASE)
b0 = base["data"]["tone"]["dsp0"]

# Build a pool of DISTINCT real blocks (valid params) from the whole library, keyed by
# @model, tagged with DSP load + built-in role. Distinct = no repeats -> no confound.
pool = {}
for path in podgo.preset_paths() + podgo.data_preset_paths():
    try:
        data, _ = podgo.load_pgp(path)
    except (OSError, ValueError):
        continue
    for v in data["data"]["tone"]["dsp0"].values():
        m = isinstance(v, dict) and v.get("@model")
        if not m or m in pool or m.startswith("P34_"):
            continue
        load = (cat.get(m) or {}).get("dsp_load")
        if load is not None:
            pool[m] = (load, v, podgo.builtin_of(m))

# Heaviest distinct free effect PER CATEGORY (diverse mix -> a break can only be DSP,
# not e.g. a per-category count limit).
_by_cat = {}
for load, block, role in pool.values():
    if role is not None:
        continue
    c = (cat.get(block["@model"]) or {}).get("category")
    if c and (c not in _by_cat or load > _by_cat[c][0]):
        _by_cat[c] = (load, block, role)
heavy_free = sorted(_by_cat.values(), key=lambda x: -x[0])
heavy_amp = sorted((x for x in pool.values() if x[2] == "amp"), key=lambda x: -x[0])

# Swap the base amp (block5) for the heaviest amp block available.
for k, v in b0.items():
    if isinstance(v, dict) and podgo.builtin_of(v.get("@model", "")) == "amp":
        nb = dict(heavy_amp[0][1])
        nb["@position"] = v["@position"]
        nb["@type"] = v.get("@type", 1)
        b0[k] = nb
        print(f"amp: {v['@model']} -> {nb['@model']} (load {heavy_amp[0][0]})")
        break

# Fill the empty free slots with the heaviest distinct free effects.
empty_slots = [k for k, v in sorted(b0.items())
               if isinstance(v, dict) and not v.get("@model")]
print(f"filling {len(empty_slots)} free slots with heaviest distinct effects:")
for slot_key, (load, block, _) in zip(empty_slots, heavy_free):
    nb = dict(block)
    nb["@position"] = b0[slot_key]["@position"]
    b0[slot_key] = nb
    print(f"  {slot_key}: {nb['@model']} (load {load})")

# Let POD Go rebuild snapshots/footswitch/controllers (safe to drop per pgp-format).
for k in ("snapshot0", "snapshot1", "snapshot2", "snapshot3", "footswitch",
          "controller", "controllers"):
    base["data"]["tone"].pop(k, None)

base["data"]["meta"]["name"] = "DSP OVER TEST"

# --- validate structure + compute DSP ---
info = podgo.classify(base)
mids = podgo.models(base)
total = sum((cat.get(m) or {}).get("dsp_load", 0) or 0 for m in mids) + IO

print("\n=== constructed preset ===")
print("built-ins present:", {k: v for k, v in info["present"].items() if v}
      if "present" in info else info)
print("free_blocks:", info.get("free_blocks"), " taxonomy:", info.get("taxonomy"))
print("occupied blocks:", len(mids))
print(f"total DSP: {total:.1f}  (working ceiling ~80.7  ->  "
      f"{'OVER budget' if total > 82 else 'NOT over budget!'})")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(base, f, indent=2)
    f.write("\n")
print(f"\nwrote {os.path.relpath(OUT, REPO)}")
