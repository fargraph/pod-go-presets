#!/usr/bin/env python3
"""
frame_decode.py — parse POD Go USB command frames from a libusb_intercept capture.

Frame model (hypothesis under test; validated by --check across a whole capture):
    [ payload_len : u16 LE ][ 0x00 ][ flag : u8 ][ channel : 4 bytes ][ payload : payload_len ][ pad -> 4B ]
  - channel examples: 8010ed03, 0110ef03, 0210f003 (three service channels)
  - request vs response: the IN channel is the OUT channel's two u16 halves swapped
    (e.g. OUT 0110ef03  <->  IN ef030110)
  - flag: 0x18 (normal/data) or 0x28 (seen on read-requests); more TBD

Usage:
    python3 frame_decode.py [capture.log] --check      # validate the model over every frame
    python3 frame_decode.py [capture.log] --grep 01ae  # decode frames whose payload contains hex
"""
import os, re, sys, glob
from collections import Counter

def newest_log():
    cap = os.environ.get("PODGO_CAP",
        "/Users/clifton.eaton/Desktop/Pod Go Presets/podgo-usb-capture")
    logs = sorted(glob.glob(os.path.join(cap, "run-*.log")), key=os.path.getmtime)
    return logs[-1] if logs else None

REC = re.compile(r"^(\d+) t=(\S+) (\S+) ep=(\S+) dir=(\S+).* data=([0-9a-f]+)$")

def frames(path):
    """Yield (idx, dir, raw_bytes) for records carrying real data on the bulk endpoints."""
    for line in open(path):
        m = REC.match(line)
        if not m:
            continue
        idx, _t, _tag, ep, d, data = m.groups()
        if ep not in ("0x01", "0x81"):
            continue
        yield int(idx), d, bytes.fromhex(data)

def parse(b):
    if len(b) < 8:
        return None
    ln = b[0] | (b[1] << 8)
    total = 8 + ln
    padded = (total + 3) & ~3
    return dict(plen=ln, byte2=b[2], flag=b[3], chan=b[4:8].hex(),
                payload=b[8:8 + ln], framelen=len(b), ok=(padded == len(b) and b[2] == 0))

def check(path):
    n = ok = 0
    bad = []
    chans, flags = Counter(), Counter()
    for idx, d, b in frames(path):
        p = parse(b)
        if not p:
            continue
        n += 1
        chans[p["chan"]] += 1
        flags[p["flag"]] += 1
        if p["ok"]:
            ok += 1
        elif len(bad) < 8:
            bad.append((idx, b.hex()))
    print(f"frames parsed: {n}   header-model holds (8+len, 4B-aligned, byte2=0): {ok} "
          f"({100*ok//max(n,1)}%)")
    print(f"channels: {dict(chans.most_common())}")
    print(f"flags:    { {hex(k): v for k, v in flags.most_common()} }")
    if bad:
        print("frames NOT matching the model (first few):")
        for idx, h in bad:
            print(f"  idx={idx} {h}")

def show(b, idx=None, dir=None):
    p = parse(b)
    if not p:
        print(f"  idx={idx} <short frame> {b.hex()}"); return
    print(f"  idx={idx} dir={dir} chan={p['chan']} flag=0x{p['flag']:02x} plen={p['plen']} "
          f"framelen={p['framelen']} ok={p['ok']}")
    print(f"      payload={p['payload'].hex()}")

def grep(path, needle):
    for idx, d, b in frames(path):
        if needle in b.hex():
            show(b, idx, d)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = [a for a in sys.argv[1:] if a.startswith("--")]
    path = args[0] if args else newest_log()
    if not path:
        sys.exit("no capture log (pass one or set PODGO_CAP)")
    if "--check" in opts or not opts:
        check(path)
    for o in opts:
        if o.startswith("--grep"):
            needle = o.split("=", 1)[1] if "=" in o else (args[1] if len(args) > 1 else "")
            print(f"\nframes containing '{needle}':")
            grep(path, needle)

if __name__ == "__main__":
    main()
