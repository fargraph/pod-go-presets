"""Spike 0.4 — inspect POD Go Edit's bundled model catalog (PGModelCatalog.json).

Explores the catalog's structure and whether it carries the identifiers we need:
the USB module ids we read off the device (e.g. 77, cd0121) and/or the @model strings
used in .pgp presets. If it does, it is the complete usb_id/@model <-> name map with no
harvesting required.

Usage:  python3 tools/spikes/inspect_catalog.py <PGModelCatalog.json>
"""
import json
import sys

path = sys.argv[1]
raw = open(path, encoding="utf-8", errors="replace").read()
d = json.loads(raw)

print(f"file size: {len(raw):,} bytes")
print(f"top-level type: {type(d).__name__}")
if isinstance(d, dict):
    print(f"top-level keys: {list(d.keys())}")


def find_entry_lists(obj, path="$", out=None, depth=0):
    """Locate lists of dict 'model entries' and record where they live."""
    if out is None:
        out = []
    if depth > 6:
        return out
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        out.append((path, len(obj), obj[0]))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            find_entry_lists(v, f"{path}.{k}", out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):
            find_entry_lists(v, f"{path}[{i}]", out, depth + 1)
    return out


lists = find_entry_lists(d)
print(f"\nfound {len(lists)} list-of-dict locations:")
for p, n, sample in lists[:12]:
    print(f"  {p}  ({n} entries)  keys={list(sample.keys())[:12]}")

# Show one full sample entry from the largest list
if lists:
    biggest = max(lists, key=lambda x: x[1])
    print(f"\nsample entry from {biggest[0]} ({biggest[1]} entries):")
    print(json.dumps(biggest[2], indent=2)[:900])

# Do the identifiers we care about appear anywhere in the raw text?
print("\n--- identifier presence in raw catalog text ---")
for tok in ["cd0121", "cd01d8", "cd0228", "HD2_", "@model", "usbId", "dsp_id",
            "modelId", "moduleId"]:
    print(f'  "{tok}": {tok in raw}')
