"""Spike 0.3 — offline decode of POD Go response framing.

Parses the captured helix_usb run log (device->host frames logged as "Unexpected
message"), and structurally decodes each distinct frame: header fields, logical
channel, and printable payload runs (preset names etc.). No hardware, no third-party
imports — pure offline analysis of already-captured bytes, the first step toward a
POD Go preset/slot parser.

Usage:  python3 tools/spikes/analyze_frames.py <path-to-run log>
"""
import sys
import re

# device->host header (observed): [len, 0x0, 0x0, 0x18, TAG, 0x3, CH, 0x10, 0x0, SEQ, 0x0, SUBLEN, ...]
# our outgoing had (CH,0x10,TAG,0x3) — inbound swaps to (TAG,0x3,CH,0x10).
CH_BY_TAG = {0xEF: "ch1 (x1x10)", 0xF0: "ch2 (x2x10)", 0xED: "ch80 (x80x10)"}

BYTE_RE = re.compile(r"0x([0-9a-fA-F]+)")


def parse_frames(path):
    frames = []
    for line in open(path, encoding="utf-8", errors="replace"):
        if "Unexpected message" not in line:
            continue
        # take only the hex list after the colon
        payload = line.split(":", 1)[-1]
        b = [int(h, 16) for h in BYTE_RE.findall(payload)]
        if len(b) >= 12:
            frames.append(b)
    return frames


def printable_runs(b, start=12, minlen=3):
    runs, cur, cur_start = [], [], None
    for i in range(start, len(b)):
        c = b[i]
        if 32 <= c < 127:
            if not cur:
                cur_start = i
            cur.append(chr(c))
        else:
            if len(cur) >= minlen:
                runs.append((cur_start, "".join(cur)))
            cur = []
    if len(cur) >= minlen:
        runs.append((cur_start, "".join(cur)))
    return runs


def decode(b):
    length = b[0]
    tag = b[4]
    ch = b[6]
    seq = b[9]
    sublen = b[11]
    match = "len==framelen" if length == len(b) else f"len byte={length} vs actual={len(b)}"
    return (f"  header: len_byte=0x{length:02x}  type=0x{b[3]:02x}  "
            f"tag=0x{tag:02x} {CH_BY_TAG.get(tag,'?'):<12} ch=0x{ch:02x}  "
            f"seq=0x{seq:02x}  sublen=0x{sublen:02x}   [{match}]")


def hexrows(b, start=0):
    rows = []
    for i in range(start, len(b), 16):
        chunk = b[i:i + 16]
        hexs = " ".join(f"{x:02x}" for x in chunk)
        asci = "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)
        rows.append(f"    {i:3d}  {hexs:<47}  {asci}")
    return "\n".join(rows)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "run_podgo.log"
    frames = parse_frames(path)
    print(f"parsed {len(frames)} device->host frames from {path}\n")

    # dedupe by (length, tag, payload-shape) keeping first of each distinct signature
    seen, uniq = set(), []
    for b in frames:
        sig = (len(b), b[4], tuple(b[12:]))  # ignore volatile seq/counter bytes
        if sig in seen:
            continue
        seen.add(sig)
        uniq.append(b)

    print(f"{len(uniq)} distinct frame signatures:\n" + "=" * 66)
    for b in uniq:
        runs = printable_runs(b)
        print(decode(b))
        if runs:
            print("  ascii runs:", ", ".join(f'@{o}:"{s}"' for o, s in runs))
        print(hexrows(b))
        print("-" * 66)


if __name__ == "__main__":
    main()
