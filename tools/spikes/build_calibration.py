"""Spike (C) — build a usb_id calibration preset + answer key.

Fills a recorded-working base (6_V--E-_AC: Vol/Amp/EQ/Cab + 6 empty free slots) with 6
distinct, LIGHT, real effect blocks whose PodGoModelDefs indices (= candidate usb_ids)
are known and spread out. Total DSP is kept well under budget so EVERY block loads (no
dropping) and the USB capture shows all of them.

After Clifton loads it and we capture over USB, compare each slot's reported usb_id to the
answer key: if they match the PodGoModelDefs index, the bridge is confirmed (usb_id = index).

Writes data-presets/demonstrations/usb-id-calibration.pgp + .key.json.
"""
import json
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import podgo          # noqa: E402
import podgo_models   # noqa: E402
import podgo_usb_ids  # noqa: E402

REPO = os.path.dirname(TOOLS)
BASE = os.path.join(REPO, "presets/with-amp-cab/6_V--E-_AC.pgp")
OUT = os.path.join(REPO, "data-presets/demonstrations/usb-id-calibration.pgp")
KEY = OUT.replace(".pgp", ".key.json")
cat = podgo_models.load()
ids = podgo_usb_ids.load()
IO = 10.99 * 2

base, _ = podgo.load_pgp(BASE)
b0 = base["data"]["tone"]["dsp0"]

# Pool of distinct real blocks from the library, with load + candidate usb_id (index).
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
        uid = ids.usb_id(m)
        if load is not None and uid is not None and podgo.builtin_of(m) is None:
            pool[m] = {"block": v, "load": load, "usb_id": uid}

# Eligible = light free effects (load <= 5) with a known usb_id; pick 6 spread across
# the id range so a coincidental match is unlikely.
eligible = sorted((x for x in pool.values() if x["load"] <= 5.0),
                  key=lambda x: x["usb_id"])
step = max(1, len(eligible) // 6)
picks = eligible[::step][:6]

empty_slots = [k for k, v in sorted(b0.items())
               if isinstance(v, dict) and not v.get("@model")]

key = {}
for slot_key, pick in zip(empty_slots, picks):
    nb = dict(pick["block"])
    nb["@position"] = b0[slot_key]["@position"]
    nb["@enabled"] = True
    b0[slot_key] = nb
    key[str(nb["@position"])] = {"model": nb["@model"], "expected_usb_id": pick["usb_id"],
                                 "load": pick["load"]}

for k in ("snapshot0", "snapshot1", "snapshot2", "snapshot3", "footswitch",
          "controller", "controllers"):
    base["data"]["tone"].pop(k, None)
base["data"]["meta"]["name"] = "USB ID CAL"

# built-ins are known too (bonus datapoints)
for v in b0.values():
    if isinstance(v, dict) and v.get("@model") and podgo.builtin_of(v["@model"]):
        key[str(v["@position"])] = {"model": v["@model"],
                                    "expected_usb_id": ids.usb_id(v["@model"]),
                                    "load": (cat.get(v["@model"]) or {}).get("dsp_load"),
                                    "builtin": podgo.builtin_of(v["@model"])}

mids = podgo.models(base)
total = sum((cat.get(m) or {}).get("dsp_load", 0) or 0 for m in mids) + IO

print(f"total DSP: {total:.1f}  ({'UNDER budget - all load' if total < 90 else 'TOO HIGH'})")
print("\ncalibration answer key (position -> model -> expected usb_id):")
for pos in sorted(key, key=int):
    e = key[pos]
    tag = e.get("builtin", "free")
    exp = e["expected_usb_id"]
    print(f"  pos {pos:>1}: {e['model']:32} expected_usb_id={exp}  [{tag}]")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(base, f, indent=2)
    f.write("\n")
with open(KEY, "w", encoding="utf-8") as f:
    json.dump(key, f, indent=2)
print(f"\nwrote {os.path.relpath(OUT, REPO)} + {os.path.basename(KEY)}")
