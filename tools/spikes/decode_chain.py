"""Spike 0.3b — decode POD Go block-chain frames from a raw capture.

Reads a capture file (one frame per line, space-separated hex — as produced by the
run_podgo capture hook), and structurally decodes the large per-slot frames: header,
16-bit length, logical channel, and printable payload runs (block @model ids etc.).

Usage:  python3 tools/spikes/decode_chain.py <capture.log> [min_bytes]
"""
import sys
from collections import Counter

CH_BY_TAG = {0xEF: "ch1", 0xF0: "ch2", 0xED: "ch80"}


def load(path):
    frames = []
    for line in open(path, encoding="utf-8", errors="replace"):
        toks = line.split()
        if not toks:
            continue
        try:
            frames.append([int(t, 16) for t in toks])
        except ValueError:
            continue
    return frames


def runs(b, start=12, minlen=3):
    out, cur, cs = [], [], None
    for i in range(start, len(b)):
        if 32 <= b[i] < 127:
            if not cur:
                cs = i
            cur.append(chr(b[i]))
        else:
            if len(cur) >= minlen:
                out.append((cs, "".join(cur)))
            cur = []
    if len(cur) >= minlen:
        out.append((cs, "".join(cur)))
    return out


def hexrows(b):
    rows = []
    for i in range(0, len(b), 16):
        c = b[i:i + 16]
        h = " ".join(f"{x:02x}" for x in c)
        a = "".join(chr(x) if 32 <= x < 127 else "." for x in c)
        rows.append(f"    {i:3d}  {h:<47}  {a}")
    return "\n".join(rows)


def decode_header(b):
    length16 = b[0] | (b[1] << 8)          # 16-bit LE; big frames exceed one byte
    tag = b[4] if len(b) > 6 else 0
    ch = b[6] if len(b) > 6 else 0
    seq = b[9] if len(b) > 9 else 0
    ok = "len+8==actual" if length16 + 8 == len(b) else f"len16={length16}+8 vs {len(b)}"
    return (f"len={len(b):3d}  hdr16=0x{length16:04x} tag=0x{tag:02x} {CH_BY_TAG.get(tag,'?'):<4} "
            f"ch=0x{ch:02x} seq=0x{seq:02x}  [{ok}]")


def main():
    path = sys.argv[1]
    min_bytes = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    frames = load(path)
    big = [b for b in frames if len(b) >= min_bytes]
    print(f"{len(frames)} frames total; {len(big)} with >= {min_bytes} bytes\n")
    print("size histogram:", dict(sorted(Counter(len(b) for b in frames).items())), "\n")

    seen, uniq = set(), []
    for b in big:
        sig = tuple(b[12:])  # ignore volatile header counters
        if sig in seen:
            continue
        seen.add(sig)
        uniq.append(b)
    print(f"{len(uniq)} distinct big-frame payloads (of {len(big)}):\n" + "=" * 68)
    for b in uniq:
        print(decode_header(b))
        r = runs(b)
        if r:
            print("  ascii:", ", ".join(f'@{o}:"{s}"' for o, s in r))
        print(hexrows(b))
        print("-" * 68)


if __name__ == "__main__":
    main()
