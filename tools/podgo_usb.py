"""podgo_usb — reassemble + decode a POD Go preset chain from a raw USB capture.

Turns a raw USB capture (one read per line, space-separated hex) into the ordered POD Go
slot list, with each occupied block's on/off state, decoded usb_id, and @model name.

- Reassembly: accumulate data_in[16:] of every ed/80 data frame; split the blob on 8213;
  slot_type 06=occupied / 0814c0=empty(No-Slot) / 07=Looper.
- usb_id decode (hardware-confirmed, two captures): a MessagePack uint right after the
  constant 'c2 19' prefix, before the '1aff09' marker, in each occupied slot. See rule
  'usb-id-decode' in registry/rules.json and docs/reference/model-id-conventions.md.
- Names come from the partial crosswalk registry/usb-id-map.json (empirical, grown by
  capturing known presets; see tools/spikes/build_calibration2.py).

First-party code, informed by kempline/helix_usb. Capture production currently uses the
(external, to-be-vendored/upstreamed) patched helix_usb driver; this tool decodes the log.

Usage:  python3 tools/podgo_usb.py <capture.log>
"""
import sys

# POD Go is a SINGLE-PATH device: input(00) + N user slots + output(01). Unlike the
# Helix dual-path 20-slot model, so we detect the chain dynamically between 00 and 01.
SLOT_TYPE = {0x00: "input", 0x01: "output", 0x02: "input-lower",
             0x03: "output-lower", 0x06: "occupied", 0x07: "LOOPER",
             0x08: "empty(No-Slot)"}


def split_frames(read):
    """A single USB read may concatenate several protocol frames. Split by the
    16-bit LE length rule (frame_len = (b0 | b1<<8) + 8)."""
    frames, i = [], 0
    while i + 12 <= len(read):
        flen = (read[i] | (read[i + 1] << 8)) + 8
        if flen < 12 or i + flen > len(read):
            break
        frames.append(read[i:i + flen])
        i += flen
    return frames


def is_preset_data_frame(f):
    # ed/80 channel, payload-bearing (len > 16). Matches request_preset.py's pattern.
    return (len(f) > 16 and f[3] == 0x18 and f[4] == 0xED
            and f[5] == 0x03 and f[6] == 0x80 and f[7] == 0x10)


def reassemble(path):
    blob = bytearray()
    for line in open(path, encoding="utf-8", errors="replace"):
        toks = line.split()
        try:
            read = bytes(int(t, 16) for t in toks)
        except ValueError:
            continue
        for f in split_frames(read):
            if is_preset_data_frame(f):
                blob.extend(f[16:])          # accumulate payload, per request_preset.py
    return blob.hex()


def slot_sections(hexblob):
    """Bound the chain at the 8215 preset boundary, then split on 0x8X 0x13 slot
    headers (any child count) — mirrors helix_usb.extract_slot_sections."""
    b = hexblob.find("8215")
    if b < 0:
        return []
    region = bytes.fromhex(hexblob[b + 14:])   # skip 8215 + 5 more bytes (7 total)
    bounds = [i for i in range(len(region) - 1)
              if (region[i] & 0xF0) == 0x80 and region[i + 1] == 0x13]
    out = []
    for j, s in enumerate(bounds):
        e = bounds[j + 1] if j + 1 < len(bounds) else len(region)
        sec = region[s:e]
        if len(sec) >= 3:
            out.append(sec)      # sec[0]=0x8X header, sec[1]=0x13, sec[2]=slot_type
    return out


def read_msgpack_uint(b, i):
    """Decode a MessagePack unsigned int at b[i]; return (value, next_index)."""
    t = b[i]
    if t < 0x80:  return t, i + 1                                       # positive fixint
    if t == 0xcc: return b[i + 1], i + 2                                # uint8
    if t == 0xcd: return (b[i + 1] << 8) | b[i + 2], i + 3               # uint16 BE
    if t == 0xce: return int.from_bytes(b[i + 1:i + 5], "big"), i + 5    # uint32 BE
    return None, i


def extract_standard_module(sec):
    """For an occupied ('06') slot, return (usb_id, on_off).

    CRACKED (2026-07-06, one hardware capture): a block's usb_id is a MessagePack uint
    stored right after the constant 'c2 19' prefix, immediately before the '1aff09' marker
    — NOT the fixed byte slice the old code read (which grabbed wrong/constant bytes).
    Verified 7/7 against the 'USB ID CAL' calibration preset; width markers (fixint / cc /
    cd) match value magnitudes. on/off is the c2(false)/c3(true) bool just after 1aff09."""
    h = sec.hex()
    m = sec.find(b"\x1a\xff\x09")
    if m < 0:
        return None, None                       # non-standard layout
    usb_id = None
    c = h.find("c219")                           # the constant prefix before the id
    if 0 <= c // 2 < m:
        usb_id, _ = read_msgpack_uint(sec, c // 2 + 2)
    onoff = "?"
    for k in range(m + 3, min(m + 8, len(sec) - 1)):
        if sec[k] == 0x0a and sec[k + 1] in (0xc2, 0xc3):
            onoff = "on" if sec[k + 1] == 0xc3 else "off"
            break
    return usb_id, onoff


def load_crosswalk():
    """Partial usb_id -> @model crosswalk (registry/usb-id-map.json)."""
    import json
    import os
    p = os.path.join(os.path.dirname(__file__), "..", "registry", "usb-id-map.json")
    try:
        return {int(k): v for k, v in json.load(open(p))["map"].items()}
    except Exception:
        return {}


def main():
    path = sys.argv[1]
    hexblob = reassemble(path)
    print(f"reassembled blob: {len(hexblob)//2} bytes  (8215={'8215' in hexblob})\n")

    secs = slot_sections(hexblob)
    types = [s[2] for s in secs]
    print(f"{len(secs)} slot sections; slot_type sequence: "
          f"{[hex(t) for t in types]}\n")

    # single-path chain: the user slots are everything up to the output(0x01) marker.
    # (input 0x00 sits just before the 8215-bounded region, so it isn't a section here.)
    i1 = types.index(0x01) if 0x01 in types else len(secs)
    user = secs[:i1]
    occ = 0
    xwalk = load_crosswalk()
    print(f"POD Go chain: {len(user)} user slots + output(01)\n")
    print(f"  {'slot':4} {'state':14} {'on/off':6} {'usb_id':8} "
          f"@model (partial crosswalk)")
    for n, sec in enumerate(user, 1):
        t = sec[2]
        kind = SLOT_TYPE.get(t, f"?0x{t:02x}")
        if t == 0x06:
            occ += 1
            uid, onoff = extract_standard_module(sec)
            name = xwalk.get(uid, "?") if uid is not None else "-"
            print(f"  {n:<4} {kind:14} {str(onoff):6} {str(uid):8} {name}")
        else:
            print(f"  {n:<4} {kind:14}")
    print(f"\noccupied blocks: {occ}    empty: {sum(1 for s in user if s[2]==0x08)}"
          f"    looper: {sum(1 for s in user if s[2]==0x07)}")


if __name__ == "__main__":
    main()
