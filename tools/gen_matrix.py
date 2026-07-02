#!/usr/bin/env python3
"""Generate the preset tables from registry/combinations.json:

  1. registry/presets.csv — one flat, filterable table (GitHub renders it with
     search + column sort). Best for filtering to a block combination.
  2. The clickable preset list in README.md, injected between the
     <!-- PRESETS:START --> / <!-- PRESETS:END --> markers. Working and broken are
     listed together, grouped by removal taxonomy, with status inline and each name
     linking to the file (open on GitHub -> Download raw file).

Both regenerate from the registry, so re-run this after editing combinations.json.

Usage:  python3 tools/gen_matrix.py
"""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import podgo

COLS = ["volume", "wah", "fx_loop", "eq", "looper", "amp", "cab"]
CSV_HEADER = ["free_blocks", "vol", "wah", "fx", "eq", "lpr", "amp", "cab",
              "status", "taxonomy", "slots", "file", "notes"]
TAXONOMY_ORDER = ["with-amp-cab", "no-cab", "no-amp", "no-amp-and-cab"]
MARKERS = re.compile(r"(<!-- PRESETS:START[^>]*-->).*?(<!-- PRESETS:END -->)", re.S)


def write_csv(rows, dest):
    with open(dest, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_HEADER)
        for e in rows:
            b = e["blocks"]
            w.writerow([e["free_blocks"]] + [1 if b[k] else 0 for k in COLS] +
                       [e["status"], e["taxonomy"], e["slots"], e["file"],
                        " ; ".join(e.get("notes", []))])


def index_block(rows):
    """Markdown list injected into README (links are repo-root-relative)."""
    lines = []
    for tax in TAXONOMY_ORDER:
        group = sorted((e for e in rows if e["taxonomy"] == tax),
                       key=lambda e: (-e["free_blocks"], e["id"]))
        if not group:
            continue
        lines.append(f"### {tax}")
        for e in group:
            status = "✅ working" if e["status"] == "working" else "❌ broken"
            note = ""
            if e.get("notes"):
                n = e["notes"][0]
                note = " ⚠️ " + (n[:70].rstrip() + "…" if len(n) > 70 else n)
            lines.append(f"- [`{e['id']}`]({e['file']}) — {e['free_blocks']} free · {status}{note}")
        lines.append("")
    return "\n".join(lines).rstrip()


def inject_readme(block, path):
    text = open(path, encoding="utf-8").read()
    if not MARKERS.search(text):
        raise SystemExit("README.md is missing the <!-- PRESETS:START/END --> markers")
    new = MARKERS.sub(lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}", text)
    open(path, "w", encoding="utf-8").write(new)


def main():
    reg = json.load(open(os.path.join(podgo.REPO, "registry", "combinations.json")))
    rows = sorted(reg["presets"], key=lambda e: (e["taxonomy"], -e["free_blocks"], e["id"]))
    write_csv(rows, os.path.join(podgo.REPO, "registry", "presets.csv"))
    inject_readme(index_block(rows), os.path.join(podgo.REPO, "README.md"))
    n_work = sum(e["status"] == "working" for e in rows)
    print(f"Wrote registry/presets.csv + injected README list: {len(rows)} presets "
          f"({n_work} working, {len(rows) - n_work} broken)")


if __name__ == "__main__":
    main()
