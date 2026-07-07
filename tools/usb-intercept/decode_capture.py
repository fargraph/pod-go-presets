#!/usr/bin/env python3
"""
decode_capture.py — turn a libusb_intercept capture log into a POD Go block chain.

Reads a capture written by libusb_intercept.dylib (see plans/usb-libusb-intercept/PLAN.md),
concatenates the inbound (device->host) payloads, and extracts the per-slot usb_id using the
rule the sibling plan (plans/podgo-usb-control) cracked:

    each occupied slot carries  c2 19 <msgpack-uint usb_id> 1a ff ...

msgpack uint widths handled: fixint (0x00-0x7f, 1 byte), 0xcc+u8, 0xcd+u16(big-endian).

Usage:
    python3 decode_capture.py [capture.log]         # defaults to newest run-*.log in $CAP
    PODGO_CAP=/path python3 decode_capture.py

Output: the ordered usb_id chain, each mapped to a model name when known. Unknown ids are
candidates to name by reading the block off the POD Go Edit UI for the loaded preset.
"""
import os, re, sys, glob, json

# Fallback seed if usb_id_crosswalk.json (next to this script) is missing.
SEED = {224: "Volume/Pan", 289: "Amp", 472: "EQ", 99: "Compressor", 84: "Delay",
        98: "Distortion", 117: "Filter", 249: "Tremolo", 304: "Compressor (AutoSwell)",
        552: "2x15 Brute"}

def load_crosswalk():
    """usb_id(int) -> 'name (category)' from usb_id_crosswalk.json; falls back to SEED."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usb_id_crosswalk.json")
    try:
        pairs = json.load(open(path))["pairs"]
        return {int(k): f"{v['name']} ({v['category']})" for k, v in pairs.items()}
    except Exception:
        return dict(SEED)

def newest_log():
    cap = os.environ.get("PODGO_CAP",
        "/Users/clifton.eaton/Desktop/Pod Go Presets/podgo-usb-capture")
    logs = sorted(glob.glob(os.path.join(cap, "run-*.log")), key=os.path.getmtime)
    return logs[-1] if logs else None

def inbound_blob(path):
    """Concatenate all IN (device->host) payloads in log order, so slot markers that straddle
    two 512-byte reads still parse."""
    hexchunks = []
    rx = re.compile(r"\bdir=IN\b.*\bdata=([0-9a-f]+)")
    with open(path) as f:
        for line in f:
            if "dir=IN" not in line:
                continue
            m = rx.search(line)
            if m:
                hexchunks.append(m.group(1))
    return bytes.fromhex("".join(hexchunks))

def decode_slots(blob):
    """Find every  c2 19 <usb_id> 1a  marker; return list of (offset, usb_id, ok_trailer)."""
    out, i, n = [], 0, len(blob)
    while True:
        j = blob.find(b"\xc2\x19", i)
        if j < 0:
            break
        k = j + 2
        if k >= n:
            break
        b0 = blob[k]
        if b0 == 0xcc and k + 1 < n:
            val, end = blob[k + 1], k + 2
        elif b0 == 0xcd and k + 2 < n:
            val, end = (blob[k + 1] << 8) | blob[k + 2], k + 3
        elif b0 < 0x80:
            val, end = b0, k + 1
        else:
            i = k
            continue
        trailer_ok = end < n and blob[end] == 0x1a   # expected 1a ff 09 marker after the id
        out.append((j, val, trailer_ok))
        i = end
    return out

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else newest_log()
    if not path or not os.path.exists(path):
        sys.exit("no capture log found (pass one, or set PODGO_CAP)")
    names = load_crosswalk()
    blob = inbound_blob(path)
    slots = decode_slots(blob)
    # keep only well-formed markers (trailing 1a); collapse an immediately-repeated full scan
    good = [(o, v) for (o, v, ok) in slots if ok]
    print(f"capture: {path}")
    print(f"inbound bytes: {len(blob)}   slot-markers (c2 19 …1a): {len(good)}\n")
    seen_order, seen = [], set()
    for off, uid in good:
        key = (off, uid)
        if key in seen:
            continue
        seen.add(key); seen_order.append(uid)
    print("chain (in capture order; repeats across re-reads collapsed by offset):")
    for idx, uid in enumerate(seen_order):
        name = names.get(uid, "??? — read this slot's block off POD Go Edit to name it")
        print(f"  slot {idx:>2}  usb_id={uid:<5} {name}")
    unknown = sorted({u for u in seen_order if u not in names})
    if unknown:
        print(f"\nNEW usb_ids to name (not in seed crosswalk): {unknown}")

if __name__ == "__main__":
    main()
