#!/usr/bin/env python3
"""Validate every preset under presets/ against registry/combinations.json and
against its own contents.

Checks, per preset:
  - file parses (or is a known recovered/broken case)
  - it has a registry entry, and vice-versa (no orphans on either side)
  - taxonomy folder matches amp/cab content
  - filename stem matches the content-derived canonical name
  - the '_broken' filename suffix matches the registry status
  - registry's recorded free_blocks / present flags match the file

Exits non-zero if any ERROR is found (WARN does not fail). Run it after editing
presets or the registry.

Usage:  python3 tools/validate_presets.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import podgo

REG = os.path.join(podgo.REPO, "registry", "combinations.json")


def main():
    reg = json.load(open(REG))
    by_file = {e["file"]: e for e in reg["presets"]}
    errors, warns = [], []

    disk = {os.path.relpath(p, podgo.REPO) for p in podgo.preset_paths()}
    for f in by_file.keys() - disk:
        errors.append(f"registry lists missing file: {f}")
    for f in disk - by_file.keys():
        errors.append(f"preset on disk has no registry entry: {f}")

    for rel in sorted(disk & by_file.keys()):
        e = by_file[rel]
        data, status = podgo.load_pgp(os.path.join(podgo.REPO, rel))
        if data is None:
            errors.append(f"{rel}: {status}")
            continue
        if status != "ok" and e.get("parse") == "ok":
            warns.append(f"{rel}: parses as '{status}' but registry says 'ok'")

        c = podgo.classify(data)
        broken = e["status"] == "broken"

        want_folder = podgo.taxonomy(c["present"])
        got_folder = rel.split("/")[1]
        if want_folder != got_folder:
            errors.append(f"{rel}: in '{got_folder}/' but content is '{want_folder}/'")

        want_stem = podgo.canonical_name(c["present"], c["free_blocks"], broken)
        got_stem = os.path.splitext(os.path.basename(rel))[0]
        # allow a disambiguating suffix like _v2 after the canonical stem
        if not (got_stem == want_stem or got_stem.startswith(want_stem + "_")):
            errors.append(f"{rel}: name '{got_stem}' != content name '{want_stem}'")

        if broken != got_stem.endswith("broken") and "_broken" not in got_stem:
            warns.append(f"{rel}: status={e['status']} but filename broken-marker mismatch")
        if e["free_blocks"] != c["free_blocks"]:
            errors.append(f"{rel}: registry free_blocks={e['free_blocks']} != actual {c['free_blocks']}")
        if e["blocks"] != c["present"]:
            errors.append(f"{rel}: registry block flags disagree with file")

    for w in warns:
        print(f"WARN  {w}")
    for er in errors:
        print(f"ERROR {er}")
    ok = len(disk & by_file.keys())
    print(f"\n{ok} presets checked, {len(errors)} errors, {len(warns)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
