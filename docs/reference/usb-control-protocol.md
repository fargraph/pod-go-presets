# POD Go USB control protocol & capture

How POD Go Edit drives the unit over USB, how we capture that traffic, and the command
dictionary reverse-engineered so far. The byte-level working spec is
[`tools/usb-intercept/protocol.md`](../../tools/usb-intercept/protocol.md) (a still-evolving
working doc, kept with its tools); **this page is the orientation + honest status.**

> **Status: ⬜ unverified.** Everything here is **decoded** from captures and cross-checked
> against known actions, but **no command has yet been issued *by us* and confirmed on the unit**
> (a replay). Per the project's rule, decoded ≠ verified — see
> [knowledge/verified.md](../knowledge/verified.md). This work lives in
> `plans/podgo-protocol-re/PLAN.md` (Step 5 = build the client + hardware-verify).

↩ [reference index](README.md)

## How we see the wire (capture method)

POD Go Edit talks to the unit through a bundled **libusb**. We capture at the app's libusb API
boundary with a **DYLD interposer** ([`tools/usb-intercept/`](../../tools/usb-intercept/)) — on
**macOS, SIP left on, one machine, no hardware analyzer**:

- The shipped app is hardened-runtime + library-validation, so we run a **re-signed local copy**
  (`capture.sh`) with `DYLD_INSERT_LIBRARIES=libusb_intercept.dylib`; the dylib logs every bulk
  transfer's full payload (async-callback trampoline — the app is async-first).
- Decode offline: `frame_decode.py` (framing), `decode_capture.py` (chain, via the crosswalk).
  The re-signed app copy + capture logs live **outside the repo** (parent working dir).
- Rejected alternative: Wireshark's macOS USB capture needs SIP **off** *and* hits an
  Apple-Silicon all-zero-payload bug — the app-level interposer avoids both.

## Transport & framing

- Bulk **OUT ep `0x01`** / **IN ep `0x81`** (512-byte reads). Each libusb bulk submit = one frame.
- **Frame** (validated across 100% of captured frames — no checksum, every byte accounted for):
  `[ payload_len : u16 LE ][ 0x00 ][ flag ][ channel : 4 bytes ][ payload ][ pad → 4-byte align ]`.
- **Three service channels**; a response uses the request channel with its two u16 halves swapped:
  - `8010ed03` ↔ `ed038010` — **editor / block edits** (id 6)
  - `0110ef03` ↔ `ef030110` — **preset & device state + rename** (id 5)
  - `0210f003` ↔ `f0030210` — third service (id 4)
- Idle = ~**1.0 s heartbeat per channel** (a keepalive).

## Session mechanics

- **Deterministic handshake:** per channel, OPEN → INIT → POLL. Every fresh connect walks the
  counters to the **same** state — the first command is always `seq=1000` — so a client reaches
  it with no guessing.
- **No checksum/CRC anywhere;** the counter fields (`seq` +1/command, plus two inner counters)
  are strictly monotonic.
- **ACKs echo the command's `seq`** (with a `64`→`67` marker) and return the resulting state — so
  a client confirms a write by matching `seq`. A **preset load** streams the whole preset back,
  fragmented, containing block/param/enum **names** as strings.

## Command dictionary (decoded)

All addressed by physical slot `62 <pos>`; model via the `c2 19 <usb_id> 1a ff` envelope
(see [usb-id-mapping.md](usb-id-mapping.md)); param values are IEEE-754 float32 (`ca <f32>`, 0–1),
enum params carry a string label; preset index `6c <(bank-1)*4 + slot>`; names are
null-terminated msgpack fixstr.

| opcode | operation | channel |
| --- | --- | --- |
| `0x29` | set bypass (`3b` c2=off / c3=on) | ed03 |
| `0x28` | set model | ed03 |
| `0x1e` | set parameter | ed03 |
| `0x27` / `0x1c` | add / remove block | ed03 |
| `0x14` / `0x47` | load / save preset | ed03 |
| `0x16` `0x17` `0x18` | reads / state polls | ed03 |
| `0x06` / `0x01` | rename preset / select | **ef03** |

Full byte templates, field offsets, and examples:
[`tools/usb-intercept/protocol.md`](../../tools/usb-intercept/protocol.md).

## Related

- The `usb_id ↔ @model` system these commands use: [usb-id-mapping.md](usb-id-mapping.md)
  (+ decoder `tools/podgo_usb.py`, map `registry/usb-id-map.json`).
- `@model` *string* id anatomy (a different id system): [model-id-conventions.md](model-id-conventions.md).
- POD Go Edit's on-disk resources / model catalog: [block-models.md](block-models.md).
