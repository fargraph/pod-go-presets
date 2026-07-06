"""Spike (C2) — build a SECOND usb_id calibration preset for decode-rule validation.

Capture 1 ('USB ID CAL') cracked the encoding: usb_id = a MessagePack uint after the
'c2 19' prefix in each occupied slot (7/7). This preset validates that the rule
GENERALIZES on independent data and expands the crosswalk, while staying at 6 blocks so
NOTHING drops (the block-count cap kept 7/10 last time).

Base 6_V--E-_AC.pgp contributes 4 built-ins:
  Vol=HD2_VolPanVolStereo (CROSS-CHECK, expect 224), Amp=HD2_AmpDelSol300 (CROSS-CHECK,
  expect 289), EQ=HD2_EQ_STATIC_ParametricStereo (CROSS-CHECK, expect 472),
  Cab=HD2_CabMicIr_2x15Brute (NEW — it dropped in capture 1, so its id is unknown; also
  tests whether cabs use the same c2-19 encoding).
Plus 2 NEW light free effects -> 6 occupied blocks total.

Writes data-presets/demonstrations/usb-id-calibration-2.pgp + .key.json (no expected ids;
the capture REVEALS them).
"""
import json
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import podgo          # noqa: E402
import podgo_models   # noqa: E402

REPO = os.path.dirname(TOOLS)
BASE = os.path.join(REPO, "presets/with-amp-cab/6_V--E-_AC.pgp")
OUT = os.path.join(REPO, "data-presets/demonstrations/usb-id-calibration-2.pgp")
KEY = OUT.replace(".pgp", ".key.json")

# Two NEW, light, distinct free effects to add (verified present in the library pool).
NEW_EFFECTS = ["HD2_TremoloTremoloStereo", "HD2_CompressorAutoSwellMono"]

cat = podgo_models.load()
xwalk = json.load(open(os.path.join(REPO, "registry", "usb-id-map.json")))["map"]
known_models = set(xwalk.values())

# Grab valid block JSON for each new effect from any library preset that contains it.
def find_block(model):
    for path in podgo.preset_paths() + podgo.data_preset_paths():
        try:
            data, _ = podgo.load_pgp(path)
        except (OSError, ValueError):
            continue
        for v in data["data"]["tone"]["dsp0"].values():
            if isinstance(v, dict) and v.get("@model") == model:
                return dict(v)
    return None

base, _ = podgo.load_pgp(BASE)
b0 = base["data"]["tone"]["dsp0"]
empty = [k for k, v in sorted(b0.items())
         if isinstance(v, dict) and not v.get("@model")]

for model, slot_key in zip(NEW_EFFECTS, empty):
    blk = find_block(model)
    if blk is None:
        sys.exit(f"ERROR: no library block found for {model}")
    blk["@position"] = b0[slot_key]["@position"]
    blk["@enabled"] = True
    b0[slot_key] = blk

for k in ("snapshot0", "snapshot1", "snapshot2", "snapshot3", "footswitch",
          "controller", "controllers"):
    base["data"]["tone"].pop(k, None)
base["data"]["meta"]["name"] = "USBIDCAL2"

# Answer key: every occupied blockN slot, flagged cross-check (in crosswalk) vs new.
key = {}
occ_blocks = [v for k, v in b0.items()
              if k.startswith("block") and isinstance(v, dict) and v.get("@model")]
for v in sorted(occ_blocks, key=lambda x: x["@position"]):
    m = v["@model"]
    exp = None
    for uid, mm in xwalk.items():
        if mm == m:
            exp = int(uid)
    key[str(v["@position"])] = {
        "model": m,
        "role": podgo.builtin_of(m) or "free",
        "check": "CROSS-CHECK" if m in known_models else "new",
        "expect_usb_id": exp,
        "load": (cat.get(m) or {}).get("dsp_load"),
    }

mids = podgo.models(base)
total = sum((cat.get(m) or {}).get("dsp_load", 0) or 0 for m in mids) + 10.99 * 2
occ = sum(1 for v in b0.values() if isinstance(v, dict) and v.get("@model"))
print(f"occupied blocks: {occ}  (target 6, well under the ~7 count cap)")
print(f"total DSP est:   {total:.1f}  (light -> all should load)\n")
print("answer key (position -> model -> expect):")
for pos in sorted(key, key=int):
    e = key[pos]
    exp = f"expect {e['expect_usb_id']}" if e["expect_usb_id"] else "REVEALS new id"
    print(f"  pos {pos}: {e['model']:34} [{e['role']:4}] {e['check']:11} {exp}")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(base, f, indent=2)
    f.write("\n")
with open(KEY, "w", encoding="utf-8") as f:
    json.dump(key, f, indent=2)
    f.write("\n")
print(f"\nwrote {os.path.relpath(OUT, REPO)} + {os.path.basename(KEY)}")
