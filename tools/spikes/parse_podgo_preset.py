"""Spike 0.3c — reassemble + parse a POD Go preset chain from a raw capture.

Turns a raw USB capture (one read per line, space-separated hex) into the ordered POD Go
slot list. Reassembly + slot model mirror helix_usb's request_preset.py (accumulate
data_in[16:] of every ed/80 data frame; split the blob on 8213; slots [1-8,11-18] are the
assignable chain positions, 06=occupied / 0814c0=empty(No-Slot) / 07=Looper).

This is first-party code (the beginning of our POD Go parser), informed by helix_usb.

Usage:  python3 tools/spikes/parse_podgo_preset.py <capture.log>
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


def extract_standard_module(sec):
    """For an occupied ('06') slot, extract (module_id, on_off) using
    helix_usb.parse_standard_module_slot's logic: strip the 0x8X13 header, find the
    '1aff09' marker, module_id = hexchars[16:idx], on/off = char at idx+11 ('3'=on)."""
    s = sec.hex()[4:]                     # drop the 2-byte 0x8X 0x13 slot header
    idx = s.find("1aff09")
    if idx < 0:
        return None, None                # not a standard module (amp/cab use other tags)
    module_id = s[16:idx]
    onoff = s[idx + 11] if idx + 11 < len(s) else "?"
    return module_id, {"3": "on", "2": "off"}.get(onoff, f"?({onoff})")


def load_helix_table():
    """helix_usb's Helix model table — used ONLY as an unverified hypothesis for POD Go
    (the whole point of the harvester is to replace this with a POD-Go-native crosswalk)."""
    p = ("/private/tmp/claude-502/-Users-clifton-eaton-Desktop-Pod-Go-Presets/"
         "d5b1660f-8129-48f9-993a-9ec400854059/scratchpad/helix_usb/modules.py")
    try:
        ns = {}
        exec(open(p).read(), ns)
        return ns.get("modules", {})
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
    helix = load_helix_table()
    print(f"POD Go chain: {len(user)} user slots + output(01)\n")
    print(f"  {'slot':4} {'state':14} {'on/off':6} {'usb_id':8} "
          f"helix-table guess (UNVERIFIED for POD Go)")
    for n, sec in enumerate(user, 1):
        t = sec[2]
        kind = SLOT_TYPE.get(t, f"?0x{t:02x}")
        if t == 0x06:
            occ += 1
            mid, onoff = extract_standard_module(sec)
            guess = " / ".join(helix.get(mid, ["?", "not in table"])) if mid else "-"
            print(f"  {n:<4} {kind:14} {str(onoff):6} {str(mid):8} {guess}")
        else:
            print(f"  {n:<4} {kind:14}")
    print(f"\noccupied blocks: {occ}    empty: {sum(1 for s in user if s[2]==0x08)}"
          f"    looper: {sum(1 for s in user if s[2]==0x07)}")


if __name__ == "__main__":
    main()
