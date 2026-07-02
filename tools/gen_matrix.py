#!/usr/bin/env python3
"""Generate registry/presets.csv from registry/combinations.json — ONE unified,
filterable table of every preset (working and broken together, status inline).

GitHub renders a .csv as a table with a search box and click-to-sort columns, so
you find a block combination first (sort/search) and read its working/broken
status in the same row. Regenerate whenever you edit the registry.

Columns: free_blocks, vol wah fx eq lpr amp cab (1/0 per built-in block),
status, taxonomy, slots, file, notes.

Usage:  python3 tools/gen_matrix.py
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import podgo

COLS = ["volume", "wah", "fx_loop", "eq", "looper", "amp", "cab"]
HEADER = ["free_blocks", "vol", "wah", "fx", "eq", "lpr", "amp", "cab",
          "status", "taxonomy", "slots", "file", "notes"]


def main():
    reg = json.load(open(os.path.join(podgo.REPO, "registry", "combinations.json")))
    rows = sorted(reg["presets"], key=lambda e: (e["taxonomy"], -e["free_blocks"], e["id"]))
    dest = os.path.join(podgo.REPO, "registry", "presets.csv")
    with open(dest, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for e in rows:
            b = e["blocks"]
            w.writerow([e["free_blocks"]] + [1 if b[k] else 0 for k in COLS] +
                       [e["status"], e["taxonomy"], e["slots"], e["file"],
                        " ; ".join(e.get("notes", []))])
    n_work = sum(e["status"] == "working" for e in rows)
    print(f"Wrote {os.path.relpath(dest, podgo.REPO)}: {len(rows)} presets "
          f"({n_work} working, {len(rows) - n_work} broken)")


if __name__ == "__main__":
    main()
