"""Shared helpers for reading Line 6 POD Go .pgp preset files.

A .pgp is JSON exported by POD Go Edit. The signal chain lives at
data.tone.dsp0, whose blockN entries are the ordered chain slots. An empty
(user-assignable / "free") block is just {"@position": N}; an occupied block
also carries an "@model" identifier and its params.

Nothing here mutates files. Import this from the other tools/ scripts.
"""
import json
import re
import glob
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Built-in (non-free) blocks, matched by the prefix of their @model id.
# Order matters: it is the canonical signal-chain order used for preset names.
BUILTIN_PATTERNS = [
    ("volume",  r"HD2_VolPan"),
    ("wah",     r"HD2_Wah"),
    ("fx_loop", r"HD2_FXLoop"),
    ("eq",      r"HD2_EQ_"),
    ("looper",  r"HD2_Looper"),
    ("amp",     r"HD2_Amp"),
    ("cab",     r"HD2_Cab"),
]
# short token used in filenames for each built-in
TOKENS = {"volume": "vol", "wah": "wah", "fx_loop": "fx", "eq": "eq",
          "looper": "lpr", "amp": "amp", "cab": "cab"}

TOTAL_SLOTS_BASE = 10  # a healthy jailbroken preset exposes 10 blockN slots


def load_pgp(path):
    """Return (data, parse_status). parse_status is 'ok', 'recovered-trailing-comma',
    or an error string (with data=None) if the file cannot be parsed at all."""
    raw = open(path, encoding="utf-8").read()
    try:
        return json.loads(raw), "ok"
    except json.JSONDecodeError as e:
        cleaned = re.sub(r",(\s*[}\]])", r"\1", raw)  # tolerate hand-edit trailing commas
        try:
            return json.loads(cleaned), "recovered-trailing-comma"
        except json.JSONDecodeError as e2:
            return None, f"unparseable: {e2}"


def chain_blocks(data):
    """Ordered list of (key, dict) for every blockN slot in dsp0 (skips input/output)."""
    dsp0 = data["data"]["tone"]["dsp0"]
    return [(k, v) for k, v in dsp0.items()
            if k.startswith("block") and isinstance(v, dict)]


def models(data):
    """List of @model ids present in the chain (occupied blocks only)."""
    return [v["@model"] for _, v in chain_blocks(data) if "@model" in v]


def builtin_of(model):
    """Return the built-in name for a model id, or None if it's a free-block effect."""
    for name, pat in BUILTIN_PATTERNS:
        if re.search(pat, model):
            return name
    return None


def classify(data):
    """Structural summary of a preset. free_blocks = total slots minus built-in
    blocks; it counts user-assignable slots whether currently empty or filled."""
    blocks = chain_blocks(data)
    present = {name: False for name, _ in BUILTIN_PATTERNS}
    counts = {name: 0 for name, _ in BUILTIN_PATTERNS}
    loaded_user_fx = []
    for _, v in blocks:
        m = v.get("@model")
        if not m:
            continue
        b = builtin_of(m)
        if b:
            present[b] = True
            counts[b] += 1
        else:
            loaded_user_fx.append(m)
    n_builtin = sum(counts.values())
    return {
        "slots": len(blocks),
        "free_blocks": len(blocks) - n_builtin,
        "present": present,
        "duplicate_builtins": {k: c for k, c in counts.items() if c > 1},
        "loaded_user_fx": loaded_user_fx,
    }


def taxonomy(present):
    """Removal-category folder for a preset, from amp/cab presence."""
    a, c = present["amp"], present["cab"]
    if a and c:
        return "with-amp-cab"
    if a:
        return "no-cab"
    if c:
        return "no-amp"
    return "no-amp-and-cab"


def canonical_name(present, free_blocks, broken=False):
    """Content-derived filename stem, e.g. '7bl_eq_amp_cab' (+ '_broken')."""
    toks = [TOKENS[name] for name, _ in BUILTIN_PATTERNS if present[name]]
    stem = f"{free_blocks}bl_" + "_".join(toks)
    return stem + ("_broken" if broken else "")


def preset_paths():
    return sorted(glob.glob(os.path.join(REPO, "presets", "**", "*.pgp"), recursive=True))


def data_preset_paths():
    return sorted(glob.glob(os.path.join(REPO, "data-presets", "*.pgp")))
