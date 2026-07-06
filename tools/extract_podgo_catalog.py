"""Extract a versioned snapshot of POD Go Edit's model catalog into the repo.

Reads the canonical POD Go Edit resources and writes a normalized, diff-friendly,
browser-ready JSON snapshot tagged by editor version. Run it again when a new POD Go Edit
version is installed; `git diff` then shows exactly what Line 6 changed (new models,
DSP-load tweaks, param changes).

The snapshot merges the per-category `*.models` defs (symbolicID/@model, name, category,
DSP `load`, `params`, plus `devices` = per-model firmware provenance) with
`PGModelCatalog.json` (the FX-block picker: image, display order, which models the general
FX block exposes). Amps/cabs/preamps/IRs are NOT in PGModelCatalog — they have dedicated
pickers — so `in_fx_picker` is False for them (they're still selectable via their block).

Usage:  python3 tools/extract_podgo_catalog.py [--out DIR] [--resources DIR]
"""
import datetime
import glob
import json
import os
import plistlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import podgo_models  # noqa: E402  (reused only for resources_dir path resolution)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(REPO, "registry", "model-catalog")

PARAM_KEYS = ("name", "symbolicID", "min", "max", "default", "valueType",
              "displayType", "assign")
# raw model fields worth preserving verbatim beyond the normalized ones
EXTRA_KEYS = ("cablink", "ircablink", "devices")


def editor_info(resources_dir):
    info = os.path.join(os.path.dirname(resources_dir), "Info.plist")
    try:
        d = plistlib.load(open(info, "rb"))
        return (d.get("CFBundleShortVersionString"), d.get("CFBundleVersion"),
                d.get("CFBundleIdentifier"))
    except (OSError, ValueError):
        return None, None, None


def build_snapshot(resources_override=None):
    rdir = podgo_models.resources_dir(resources_override)
    short, build, bid = editor_info(rdir)

    # FX-block picker: category metadata + per-model image / display order.
    fx_ui, cat_meta = {}, {}
    try:
        pg = json.load(open(os.path.join(rdir, "PGModelCatalog.json"), encoding="utf-8"))
        for c in pg.get("categories", []):
            cat_meta[str(c.get("id"))] = {"name": c.get("name"),
                                          "shortName": c.get("shortName"),
                                          "color": c.get("color"),
                                          "image": c.get("image"),
                                          "count": len(c.get("models", []))}
            for order, m in enumerate(c.get("models", [])):
                fx_ui[m.get("id")] = {"image": m.get("image"), "ui_order": order}
    except (OSError, ValueError):
        pass

    models, with_devices = {}, 0
    for path in sorted(glob.glob(os.path.join(rdir, "*.models"))):
        token = os.path.basename(path)[:-len(".models")]
        try:
            data = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, list):
            continue
        for m in data:
            sid = isinstance(m, dict) and m.get("symbolicID")
            if not sid:
                continue
            entry = {"name": m.get("name"),
                     "category": token,               # block type from the .models file
                     "category_num": m.get("category"),
                     "dsp_load": m.get("load"),
                     "in_fx_picker": sid in fx_ui}
            for k in EXTRA_KEYS:
                if m.get(k) is not None:
                    entry[k] = m[k]
            if "devices" in entry:
                with_devices += 1
            if sid in fx_ui:
                entry["image"] = fx_ui[sid]["image"]
                entry["ui_order"] = fx_ui[sid]["ui_order"]
            entry["params"] = [{k: p.get(k) for k in PARAM_KEYS}
                               for p in m.get("params", []) if isinstance(p, dict)]
            models[sid] = entry

    return {
        "provenance": {
            "source": "POD Go Edit",
            "editor_version": short,
            "editor_build": build,
            "bundle_id": bid,
            "resources_path": rdir,
            "extracted": datetime.date.today().isoformat(),
            "tool": "tools/extract_podgo_catalog.py",
        },
        "counts": {
            "models": len(models),
            "in_fx_picker": sum(1 for m in models.values() if m["in_fx_picker"]),
            "with_firmware_provenance": with_devices,
            "categories": len(cat_meta),
        },
        "categories": cat_meta,     # FX-picker category metadata (id -> name/count/...)
        "models": dict(sorted(models.items())),
    }, short


def main():
    out_dir, resources = DEFAULT_OUT, None
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--out" and i + 1 < len(args):
            out_dir = args[i + 1]
        elif a == "--resources" and i + 1 < len(args):
            resources = args[i + 1]

    snap, ver = build_snapshot(resources)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"podgo-edit-{ver}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2, ensure_ascii=False)
        f.write("\n")

    c = snap["counts"]
    print(f"wrote {path}")
    print(f"  editor {snap['provenance']['editor_version']} "
          f"(build {snap['provenance']['editor_build']})")
    print(f"  {c['models']} models | {c['in_fx_picker']} in FX picker | "
          f"{c['with_firmware_provenance']} carry firmware provenance | "
          f"{c['categories']} FX categories")


if __name__ == "__main__":
    main()
