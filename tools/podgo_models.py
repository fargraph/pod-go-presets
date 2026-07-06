"""Access POD Go's model catalog, keyed by @model (symbolicID).

Two sources behind one interface:

  - a versioned SNAPSHOT under registry/model-catalog/ (DEFAULT) — portable (no app
    needed), git-diffable across editor/firmware versions. Produced by
    tools/extract_podgo_catalog.py from POD Go Edit's bundled resources.
  - the LIVE POD Go Edit resources — used to *create* snapshots, or as a fallback when no
    snapshot exists. Override the app path with POD_GO_EDIT_RESOURCES.

The snapshot is preferred so day-to-day tooling doesn't depend on POD Go Edit being
installed and always reads the same versioned data. Entries are normalized to:
    {name, category, category_num, dsp_load, cablink?, params, ui_exposed?, image?}
where the key is the `symbolicID` = the project's `@model` (e.g. HD2_AmpCali400Ch1).
"""
import glob
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT_DIR = os.path.join(REPO, "registry", "model-catalog")
DEFAULT_RESOURCES = "/Applications/Line6/POD Go Edit.app/Contents/Resources"


def resources_dir(override=None):
    d = override or os.environ.get("POD_GO_EDIT_RESOURCES") or DEFAULT_RESOURCES
    if not os.path.isdir(d):
        raise FileNotFoundError(
            f"POD Go Edit resources not found at {d!r}. Install POD Go Edit or set "
            f"POD_GO_EDIT_RESOURCES to its Contents/Resources directory.")
    return d


def latest_snapshot(snapshot_dir=SNAPSHOT_DIR):
    snaps = sorted(glob.glob(os.path.join(snapshot_dir, "podgo-edit-*.json")))
    return snaps[-1] if snaps else None


class PodGoCatalog:
    """Read-only view of the POD Go model catalog, keyed by @model id."""

    def __init__(self):
        self.models = {}       # @model -> normalized entry dict
        self.categories = {}   # category id -> metadata
        self.provenance = {}
        self.source = None

    # ---- constructors --------------------------------------------------------
    @classmethod
    def from_snapshot(cls, path):
        self = cls()
        d = json.load(open(path, encoding="utf-8"))
        self.models = d.get("models", {})
        self.categories = d.get("categories", {})
        self.provenance = d.get("provenance", {})
        self.source = path
        return self

    @classmethod
    def from_live(cls, override=None):
        self = cls()
        d = resources_dir(override)
        self.source = d
        for path in sorted(glob.glob(os.path.join(d, "*.models"))):
            token = os.path.basename(path)[:-len(".models")]
            try:
                data = json.load(open(path, encoding="utf-8"))
            except (ValueError, OSError):
                continue
            if not isinstance(data, list):
                continue
            for m in data:
                sid = isinstance(m, dict) and m.get("symbolicID")
                if not sid:
                    continue
                self.models[sid] = {
                    "name": m.get("name"),
                    "category": token,
                    "category_num": m.get("category"),
                    "dsp_load": m.get("load"),
                    "cablink": m.get("cablink"),
                    "params": m.get("params", []),
                }
        cat_path = os.path.join(d, "PGModelCatalog.json")
        if os.path.exists(cat_path):
            try:
                cat = json.load(open(cat_path, encoding="utf-8"))
                for c in cat.get("categories", []):
                    self.categories[str(c.get("id"))] = {"name": c.get("name")}
            except (ValueError, OSError):
                pass
        self.provenance = {"source": "POD Go Edit (live)", "resources_path": d}
        return self

    # ---- lookups -------------------------------------------------------------
    def get(self, model_id):
        return self.models.get(model_id)

    def name(self, model_id):
        m = self.models.get(model_id)
        return m.get("name") if m else None

    def param_names(self, model_id):
        m = self.models.get(model_id)
        return [p.get("name") for p in m.get("params", [])] if m else []

    def by_category(self):
        out = {}
        for sid, m in self.models.items():
            out.setdefault(m.get("category"), []).append(sid)
        return out


_cache = {}


def load(prefer="snapshot", override=None, snapshot_dir=SNAPSHOT_DIR):
    """Load the catalog. prefer='snapshot' (default) uses the newest stored snapshot and
    falls back to the live app; prefer='live' always reads POD Go Edit."""
    key = (prefer, override, snapshot_dir)
    if key in _cache:
        return _cache[key]
    cat = None
    if prefer == "snapshot":
        snap = latest_snapshot(snapshot_dir)
        if snap:
            cat = PodGoCatalog.from_snapshot(snap)
    if cat is None:
        cat = PodGoCatalog.from_live(override)
    _cache[key] = cat
    return cat


if __name__ == "__main__":
    import sys
    cat = load()
    print(f"source: {cat.source}")
    if cat.provenance.get("editor_version"):
        print(f"editor version: {cat.provenance['editor_version']} "
              f"(extracted {cat.provenance.get('extracted')})")
    bc = cat.by_category()
    print(f"{len(cat.models)} models across {len(bc)} categories")
    for model_id in sys.argv[1:]:
        m = cat.get(model_id)
        print(f"\n{model_id}:")
        if not m:
            print("  not found")
            continue
        print(f"  name={m.get('name')!r} category={m.get('category')} "
              f"dsp_load={m.get('dsp_load')}")
        print(f"  params={cat.param_names(model_id)}")
