#!/usr/bin/env python3
"""Validate the knowledge-to-preset linkage: registry/rules.json and
data-presets/demonstrations/manifest.json.

Checks:
  - rules.json / manifest.json parse; rule ids are unique
  - every rule 'kind' and 'status' is from the declared vocabulary
  - every manifest 'rule' id exists in rules.json
  - every demonstrator file (manifest 'file' and every rule 'demonstrated_by') exists and
    parses (a recovered trailing comma is allowed and reported as a WARN)
  - status==verified requires a non-empty demonstrated_by (verified is earned by a preset)
  - WARN if a manifest entry's status disagrees with its rule's status

Exits non-zero on any ERROR (WARN does not fail). Run after editing rules.json, the
manifest, or the demonstrator presets.

Usage:  python3 tools/validate_examples.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import podgo

RULES = os.path.join(podgo.REPO, "registry", "rules.json")
MANIFEST = os.path.join(podgo.REPO, "data-presets", "demonstrations", "manifest.json")


def check_file(rel, errors, warns, label):
    """A demonstrator path must exist and parse (recovered trailing comma is a WARN)."""
    path = os.path.join(podgo.REPO, rel)
    if not os.path.exists(path):
        errors.append(f"{label}: file does not exist: {rel}")
        return
    data, status = podgo.load_pgp(path)
    if data is None:
        errors.append(f"{label}: {rel}: {status}")
    elif status != "ok":
        warns.append(f"{label}: {rel}: parses as '{status}'")


def main():
    errors, warns = [], []
    rules_doc = json.load(open(RULES))
    manifest = json.load(open(MANIFEST))

    rules = rules_doc["rules"]
    kinds = set(rules_doc.get("kinds", []))
    statuses = set(rules_doc.get("status_model", {}).keys())

    by_id = {}
    for r in rules:
        rid = r["id"]
        if rid in by_id:
            errors.append(f"rules.json: duplicate rule id: {rid}")
        by_id[rid] = r
        if kinds and r.get("kind") not in kinds:
            errors.append(f"rules.json: {rid}: kind '{r.get('kind')}' not in {sorted(kinds)}")
        if statuses and r.get("status") not in statuses:
            errors.append(f"rules.json: {rid}: status '{r.get('status')}' not in {sorted(statuses)}")
        if r.get("status") == "verified" and not r.get("demonstrated_by"):
            errors.append(f"rules.json: {rid}: status=verified but demonstrated_by is empty")
        for p in r.get("demonstrated_by", []):
            check_file(p, errors, warns, f"rules.json:{rid}")

    for d in manifest["demonstrations"]:
        rid = d.get("rule")
        if rid not in by_id:
            errors.append(f"manifest: demonstration '{rid}' has no matching rule in rules.json")
        check_file(d["file"], errors, warns, f"manifest:{rid}")
        if rid in by_id and d.get("status") and d["status"] != by_id[rid].get("status"):
            warns.append(f"manifest:{rid}: status '{d['status']}' != rule status "
                         f"'{by_id[rid].get('status')}'")

    for w in warns:
        print(f"WARN  {w}")
    for er in errors:
        print(f"ERROR {er}")
    print(f"\n{len(rules)} rules, {len(manifest['demonstrations'])} demonstrations checked, "
          f"{len(errors)} errors, {len(warns)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
