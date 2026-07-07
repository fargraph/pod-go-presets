"""decode_model_list — recover the full usb_id ↔ @model table from a capture where
POD Go Edit fetched the device's model list(s).

SUPERSEDED (kept for reference): the usb_id ↔ @model map turned out to be derivable directly
from POD Go Edit's PodGo.sym (usb_id == a symbolicID's index in that file) — use
tools/gen_usb_id_map.py, no capture needed. Hardware then showed opening a model picker sends
NO device traffic (the picker is rendered from the local catalog), so the "browse to capture
the list" premise below never fires anyway. See docs/reference/usb-id-mapping.md.

Motivation (see docs/reference/usb-id-mapping.md): the `usb_id → @model` map is NOT in
POD Go Edit's shipped data — the app decompiles clean of any static table, keeps blocks as
numeric ids, and gets those ids from the unit. But `usb_id` is strictly MONOTONIC with the
`PodGoModelDefs.bin` array order *within each category*, which means the device hands the
editor its model ids in an order aligned to that canonical catalog order. So if we capture the
editor pulling the model list (browse every block's model picker once, connected), the response
is a numeric array we can align 1:1 to the catalog and read the whole table off.

This tool does NOT assume the exact wire encoding. It uses the ~23 hardware-confirmed pairs in
registry/usb-id-map.json as ANCHORS: it searches the device→host stream for an integer run
(uint16 LE/BE, or a MessagePack uint array) whose values land on the known usb_ids at the
positions the catalog predicts. Two+ anchors hitting simultaneously is statistically decisive,
so a match is self-validating — and any decoded value that contradicts a known pair rejects the
alignment. It tries the whole 574-model catalog first (≈20 anchors — very strong), then each
numeric category separately (the fallback if the device sends per-category lists).

Canonical order comes straight from PodGoModelDefs.bin (the reordered registry snapshot does
NOT preserve it), so this needs POD Go Edit installed (or POD_GO_EDIT_RESOURCES set), like the
other catalog tools.

Usage:
    python3 tools/decode_model_list.py <capture.log>     # decode a real capture
    python3 tools/decode_model_list.py --selftest        # prove the decoder on synthetic data
    python3 tools/decode_model_list.py <capture.log> --out newmap.json   # write merged crosswalk

Capture recipe (to produce <capture.log>): connect the unit, launch the libusb-intercepted
POD Go Edit (tools/usb-intercept/capture.sh), then open the model picker for EACH block type
once (amp, cab, every FX category, wah, volume, EQ, looper) so the editor fetches each list,
then quit. Feed the resulting run-*.log here.
"""
import json
import os
import re
import struct
import sys

# --- catalog (canonical PodGoModelDefs.bin order) --------------------------------------

def _resources_dir():
    d = os.environ.get("POD_GO_EDIT_RESOURCES") or \
        "/Applications/Line6/POD Go Edit.app/Contents/Resources"
    if not os.path.isdir(d):
        sys.exit(f"POD Go Edit resources not found at {d!r}. Install POD Go Edit or set "
                 f"POD_GO_EDIT_RESOURCES to its Contents/Resources directory.")
    return d


def _clean(o):
    if isinstance(o, bytes):
        return o.rstrip(b"\x00").decode("utf-8", "replace")
    if isinstance(o, list):
        return [_clean(x) for x in o]
    if isinstance(o, dict):
        return {_clean(k): _clean(v) for k, v in o.items()}
    return o


def load_catalog_order():
    """Return (flat, by_cat): flat = [symbolicID…] in PodGoModelDefs.bin array order;
    by_cat = {category_num: [symbolicID…]} preserving that order within each category."""
    import msgpack
    raw = open(os.path.join(_resources_dir(), "PodGoModelDefs.bin"), "rb").read()
    defs = _clean(msgpack.unpackb(raw, raw=True, strict_map_key=False))
    flat, by_cat = [], {}
    for m in defs:
        sid = m.get("symbolicID")
        flat.append(sid)
        by_cat.setdefault(m.get("category"), []).append(sid)
    return flat, by_cat


def load_known():
    """usb_id(int) -> symbolicID, from registry/usb-id-map.json's 'map' (the hardware pairs)."""
    p = os.path.join(os.path.dirname(__file__), "..", "registry", "usb-id-map.json")
    try:
        return {int(k): v for k, v in json.load(open(p))["map"].items()}
    except Exception:
        return {}


# --- capture → device→host byte blob ---------------------------------------------------

_LIBUSB_IN = re.compile(r"\bdir=IN\b.*\bdata=([0-9a-f]+)")


def inbound_blob(path):
    """Concatenate all device→host payload bytes, so an array that straddles two 512-byte
    reads still parses. Accepts the libusb_intercept log format (dir=IN … data=<hex>) and,
    as a fallback, a plain 'space-separated hex per line' dump."""
    hexchunks, saw_libusb = [], False
    for line in open(path, encoding="utf-8", errors="replace"):
        if "dir=IN" in line:
            saw_libusb = True
            m = _LIBUSB_IN.search(line)
            if m and m.group(1):
                hexchunks.append(m.group(1))
    if not saw_libusb:                      # plain hex dump: take every parseable line
        for line in open(path, encoding="utf-8", errors="replace"):
            toks = line.split()
            try:
                hexchunks.append(bytes(int(t, 16) for t in toks).hex())
            except ValueError:
                continue
    return bytes.fromhex("".join(hexchunks))


# --- integer views over the blob -------------------------------------------------------

def _mp_uint(b, i):
    """MessagePack unsigned int at b[i] → (value, next_index), or (None, i) if not a uint."""
    if i >= len(b):
        return None, i
    t = b[i]
    if t < 0x80:                                   return t, i + 1
    if t == 0xcc and i + 1 < len(b):               return b[i + 1], i + 2
    if t == 0xcd and i + 2 < len(b):               return (b[i + 1] << 8) | b[i + 2], i + 3
    if t == 0xce and i + 4 < len(b):               return int.from_bytes(b[i + 1:i + 5], "big"), i + 5
    return None, i


def msgpack_int_arrays(blob):
    """Yield (start, [ints]) for every MessagePack array-of-uints in the blob (fixarray
    0x9X, array16 0xdc, array32 0xdd). Only arrays whose every element is a uint are kept."""
    n = len(blob)
    i = 0
    while i < n:
        t = blob[i]
        count = start = None
        if 0x90 <= t <= 0x9f:
            count, start = t & 0x0f, i + 1
        elif t == 0xdc and i + 2 < n:
            count, start = (blob[i + 1] << 8) | blob[i + 2], i + 3
        elif t == 0xdd and i + 4 < n:
            count, start = int.from_bytes(blob[i + 1:i + 5], "big"), i + 5
        if count and 2 <= count <= 4096:
            vals, j, ok = [], start, True
            for _ in range(count):
                v, j = _mp_uint(blob, j)
                if v is None:
                    ok = False
                    break
                vals.append(v)
            if ok:
                yield i, vals
        i += 1


# --- anchor alignment ------------------------------------------------------------------

def _anchors_for(order_sublist, known):
    """(index_in_sublist -> usb_id) for models in order_sublist that we already know."""
    sid_to_usb = {sid: uid for uid, sid in known.items()}
    return {i: sid_to_usb[sid] for i, sid in enumerate(order_sublist) if sid in sid_to_usb}


def _decode_from_values(seq, order_sublist, anchors, min_anchors):
    """Given a decoded integer sequence `seq` and a catalog `order_sublist` with `anchors`
    (idx_in_sublist -> usb_id), slide the sublist over seq. Accept an offset only if ≥
    min_anchors anchors match AND none contradict. Return {symbolicID: usb_id} or None."""
    if len(anchors) < min_anchors:
        return None
    L = len(order_sublist)
    for off in range(0, len(seq) - L + 1):
        good = True
        for idx, usb in anchors.items():
            if seq[off + idx] != usb:
                good = False
                break
        if good:
            return {order_sublist[i]: seq[off + i] for i in range(L)}
    return None


def _u16_views(blob):
    """(label, list-of-ints) for the two uint16 fixed-width views of the blob."""
    n = len(blob) - (len(blob) % 2)
    le = list(struct.unpack_from("<%dH" % (n // 2), blob, 0)) if n else []
    be = list(struct.unpack_from(">%dH" % (n // 2), blob, 0)) if n else []
    return [("u16le", le), ("u16be", be)]


def align_group(order_sublist, known, blob, min_anchors=2):
    """Try to recover {symbolicID: usb_id} for one catalog group from the blob, across all
    encodings. Returns (mapping, how) or (None, None)."""
    anchors = _anchors_for(order_sublist, known)
    if len(anchors) < min_anchors:
        return None, None
    # 1) MessagePack array-of-uints (the wire is msgpack; most likely shape)
    for _start, vals in msgpack_int_arrays(blob):
        got = _decode_from_values(vals, order_sublist, anchors, min_anchors)
        if got:
            return got, "msgpack-array"
    # 2) fixed-width uint16 run (LE then BE)
    for label, seq in _u16_views(blob):
        got = _decode_from_values(seq, order_sublist, anchors, min_anchors)
        if got:
            return got, label
    return None, None


def _monotonic_ok(by_cat, mapping):
    """Every category's decoded usb_ids must be strictly increasing in catalog order
    (the invariant from docs/reference/usb-id-mapping.md). Returns list of violations."""
    bad = []
    for cat, sids in by_cat.items():
        seq = [(sid, mapping[sid]) for sid in sids if sid in mapping]
        for (s0, u0), (s1, u1) in zip(seq, seq[1:]):
            if u1 <= u0:
                bad.append((cat, s0, u0, s1, u1))
    return bad


# --- driver ----------------------------------------------------------------------------

def decode(blob, flat, by_cat, known):
    """Return (mapping, notes). Tries the whole catalog first, then per numeric category."""
    notes = []
    mapping = {}

    whole, how = align_group(flat, known, blob, min_anchors=3)
    if whole:
        mapping.update(whole)
        notes.append(f"full 574-model list aligned from one array (encoding={how})")
    else:
        notes.append("no single full-catalog list found; trying per-category")
        for cat, sids in sorted(by_cat.items(), key=lambda kv: (kv[0] is None, kv[0])):
            got, how = align_group(sids, known, blob, min_anchors=2)
            if got:
                mapping.update(got)
                notes.append(f"category {cat}: {len(got)} models (encoding={how})")

    # validation: decoded values must agree with every known pair they cover
    contradictions = [(sid, mapping[sid], uid)
                      for uid, sid in known.items()
                      if sid in mapping and mapping[sid] != uid]
    return mapping, notes, contradictions


def merged_crosswalk(mapping, known):
    """usb_id -> symbolicID, known pairs first (authoritative), then newly decoded ones."""
    out = dict(known)                              # hardware pairs win on conflict
    for sid, uid in mapping.items():
        out.setdefault(uid, sid)
    return {k: out[k] for k in sorted(out)}


def report(mapping, notes, contradictions, flat, by_cat, known, out_path=None):
    total = len(flat)
    print(f"catalog: {total} models across {len(by_cat)} categories")
    print(f"anchors (hardware pairs): {len(known)}\n")
    for ln in notes:
        print(f"  - {ln}")
    print(f"\ndecoded pairs: {len(mapping)} / {total}")
    new = {s: u for s, u in mapping.items() if u not in known}
    print(f"  new (not already in usb-id-map.json): {len(new)}")
    if contradictions:
        print("\n  !! CONTRADICTIONS with known pairs (alignment suspect — do NOT trust):")
        for sid, got, want in contradictions:
            print(f"     {sid}: decoded {got}, hardware says {want}")
    mono_bad = _monotonic_ok(by_cat, mapping)
    if mono_bad:
        print(f"\n  !! monotonic-within-category violations: {len(mono_bad)} (alignment suspect)")
        for cat, s0, u0, s1, u1 in mono_bad[:8]:
            print(f"     cat {cat}: {s0}={u0} then {s1}={u1}")
    else:
        print("  monotonic-within-category: OK")

    if mapping and not contradictions and not mono_bad:
        cross = merged_crosswalk(mapping, known)
        if out_path:
            json.dump({"_comment": "usb_id -> @model, merged from decode_model_list.py; "
                                   "verify a sample on hardware before promoting to usb-id-map.json.",
                       "map": {str(k): v for k, v in cross.items()}},
                      open(out_path, "w"), indent=2)
            print(f"\n  wrote merged crosswalk ({len(cross)} ids) -> {out_path}")
        else:
            print(f"\n  merged crosswalk would carry {len(cross)} ids "
                  f"(pass --out FILE to write it)")
    elif not mapping:
        print("\n  nothing decoded — this capture has no model-list array. Re-capture while "
              "browsing every block's model picker (see the module docstring's recipe).")


# --- self-test (proves the decoder without a real capture) -----------------------------

def selftest():
    """Synthesize a device response from the catalog + a plausible per-model usb_id, then
    confirm the decoder recovers the whole table from each supported encoding."""
    flat, by_cat = load_catalog_order()
    # Purely SYNTHETIC ground truth (strictly increasing per category by construction) and
    # synthetic anchors — self-contained, independent of registry/usb-id-map.json so this test
    # keeps passing regardless of what the real map holds.
    truth, base = {}, 40
    for cat, sids in by_cat.items():
        for sid in sids:
            truth[sid] = base
            base += 3
    known = {}                                     # a few anchors per multi-model category
    for cat, sids in by_cat.items():
        if len(sids) >= 2:
            for sid in (sids[0], sids[-1]):
                known[truth[sid]] = sid

    def mp_array(vals):
        b = bytearray()
        n = len(vals)
        b += (bytes([0x90 | n]) if n < 16 else
              b"\xdc" + struct.pack(">H", n) if n < 65536 else
              b"\xdd" + struct.pack(">I", n))
        for v in vals:
            if v < 0x80:      b += bytes([v])
            elif v < 0x100:   b += bytes([0xcc, v])
            else:             b += b"\xcd" + struct.pack(">H", v)
        return bytes(b)

    ok = True
    # (a) one full-catalog msgpack array, with noise on both sides
    blob = b"\x01\x02\x03" + mp_array([truth[s] for s in flat]) + b"\xff\xff"
    mapping, notes, contra = decode(blob, flat, by_cat, known)
    full_ok = (not contra and all(mapping.get(s) == truth[s] for s in flat)
               and len(mapping) == len(flat))
    print(f"selftest full-catalog msgpack array: {'PASS' if full_ok else 'FAIL'} "
          f"({len(mapping)}/{len(flat)} recovered)")
    ok &= full_ok
    # (b) per-category uint16-LE arrays (no full list present).
    blob = b""
    for cat, sids in by_cat.items():
        blob += b"\x00\x00" + b"".join(struct.pack("<H", truth[s]) for s in sids) + b"\x00\x00"
    mapping, notes, contra = decode(blob, flat, by_cat, known)
    aligned_cats = [c for c, sids in by_cat.items()
                    if len(_anchors_for(sids, known)) >= 2]
    covered = [s for c in aligned_cats for s in by_cat[c]]
    percat_ok = (not contra and covered
                 and all(mapping.get(s) == truth[s] for s in covered))
    print(f"selftest per-category uint16 arrays: {'PASS' if percat_ok else 'FAIL'} "
          f"({len(mapping)} models across {len(aligned_cats)} anchorable categories, "
          f"synthetic anchors)")
    ok &= percat_ok
    print("\nSELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = sys.argv[1:]
    if "--selftest" in opts:
        sys.exit(selftest())
    if not args:
        sys.exit(__doc__)
    out_path = None
    if "--out" in opts:
        i = opts.index("--out")
        out_path = opts[i + 1] if i + 1 < len(opts) else None
    flat, by_cat = load_catalog_order()
    known = load_known()
    blob = inbound_blob(args[0])
    print(f"capture: {args[0]}")
    print(f"device→host bytes: {len(blob)}\n")
    mapping, notes, contradictions = decode(blob, flat, by_cat, known)
    report(mapping, notes, contradictions, flat, by_cat, known, out_path)


if __name__ == "__main__":
    main()
