# POD Go USB control protocol — working spec

Reverse-engineered from libusb captures of POD Go Edit (`tools/usb-intercept/`). **Working
artifact, not verified** — commands are decoded + cross-checked against known stimulus, but
"verified" (per CLAUDE.md) requires a hardware replay (plan Step 5). See
`plans/podgo-protocol-re/PLAN.md`. Firmware v2.50, device `0e41:424b`.

## Transport
- Bulk **OUT ep `0x01`**, **IN ep `0x81`** (512-byte reads). Each libusb bulk submit = one frame.
- App uses libusb async (`submit_transfer` + callbacks); `control_transfer` carries no protocol data.

## Frame (validated: 100% of 16,332 frames)
```
[ payload_len : u16 LE ] [ 0x00 ] [ flag : u8 ] [ channel : 4 bytes ] [ payload ] [ pad → 4-byte align ]
```
- **channels** (OUT → IN is the two u16 halves swapped = request/response pairing):
  `8010ed03`↔`ed038010`, `0110ef03`↔`ef030110`, `0210f003`↔`f0030210`. Editor commands ride **`8010ed03`**.
- **flag**: `0x18` normal, `0x28` rare read-request. Idle = ~16-byte heartbeats on all 3 channels.

## Session (handshake · channels · heartbeat)
- **Channel ids** (1 byte): `ef03`=5, **`ed03`=6 (editor — all edits ride here)**, `f003`=4.
  OUT→IN swaps the two u16 halves. `ef03` also carries device/preset state; `f003` minimal.
- **Handshake** (per channel, on connect) — 3 fixed frames:
  1. OPEN `0c 0000 28 <chan> 00000002 00010021 00100000` (payload identical on all channels)
  2. INIT `11 0000 18 <chan> 00020004 00100000 0100 <id> 00 01000000 <id>000000`  (id = 4/5/6)
  3. POLL `08 0000 18 <chan> 0003 …`
  Order: `ef03` first (~+3.5 s after device open), then `ed03` + `f003` (~+7.3 s). The INIT reply
  carries device/preset state (e.g. the current preset name).
- **Heartbeat:** ~**1.0 s per channel** at idle (16-byte poll frames) — likely a required keepalive.

## Command envelope (channel ed03)
Payload = a 16-byte **inner record**, then the msgpack command, then 4-byte padding:
```
[ AAAA:u16 ][ f2:u16 ][ BBBB:u32 LE ][ 01 00 <chan_id> 00 ][ inner_len:u32 LE ]  <msgpack>  [pad→4B]
   counter    (type?)    counter       channel id (ed03=06)   = len(msgpack)
```
msgpack command:
```
83 66  cd <seq:u16>   64  <OPCODE>   65 <8Y>   <fields…>
```
**No checksum / CRC anywhere** — verified across 100% of frames: every byte is
header/counter/const/length/msgpack/pad, and `inner_len == len(msgpack)` always. The counters are all
strictly **monotonic**, so replay just advances them like the app: **`seq` starts 1000, +1 per command**
(echoed in the ACK → correlation key); `AAAA` = per-channel message index; `BBBB` = cumulative tick.
- `<OPCODE>` = byte after `64`; `<8Y>` = msgpack map size (81/82/85 = 1/2/5 fields).

### Responses / ACKs
Every command gets a reply on the swapped channel (`ed038010`) that **echoes the same `seq`**, with a
`67` marker where the request had `64`, plus the resulting state (set-param echoes the param + clamped
value; set-model returns the block's full new param set). → the client confirms success by matching
`seq`. Reads/polls use opcodes `0x16/0x17/0x18` on ed03 (frequent block/param state queries).

### Reads · preset-load response · enums · fragmentation (Track 2b, run-20260707-114718)
- **Preset load** (`0x14`, `6c <(bank-1)*4+slot>`; confirmed 12A/13A/02A) makes the unit **stream the
  ENTIRE preset back** as a large fragmented multi-frame response on `ed038010` (continuation frames
  share the `BBBB` counter; reassemble by concatenation like `decode_capture.py`).
- The stream is **self-describing**: it carries block NAMES, param NAMES, and enum value labels as
  msgpack strings (`Mix`, `Delay Feedback`, `Time`, `Dotted 1/8`, `Amp Drive`, `Crunch`, …) alongside
  the `c2 19 <usb_id> 1a ff` model markers and `ca <f32>` values. → readable preset contents over USB;
  a potential auto-source for the usb_id crosswalk (names ↔ ids in one response).
- **Enum / list params** (e.g. tempo note-division) carry a string label + index, distinct from
  continuous float knobs — so param encoding is type-dependent (float32 vs enum).
- **On-unit changes** (knob/footswitch on the hardware): appear to surface via the app's normal state
  polls rather than an obviously distinct push — **tentative**; a dedicated on-unit-only capture with
  long idle gaps would pin the exact frame. Not needed to issue writes.

### Opcode table (decoded)
| opcode | operation | field tail | example |
| --- | --- | --- | --- |
| `0x14` | **load preset** | `6b 01 6c <preset_index>` | 13A→`6c 30`, 12A→`6c 2c` |
| `0x1c` | **remove block** *(tentative)* | `65 81 62 <pos>` | remove @pos 3 → `1c 65 81 62 03` |
| `0x1e` | **set param** | `65 85 62 <pos> 1d c3 1a 00 1c <param> 77 ca <f32>` | Mid→0.5 |
| `0x27` | **add block** | `65 82 62 <pos> 63 82… c2 19 <usb_id> 1a ff 09 …defaults` | add Minitaur@3 |
| `0x28` | **set model** | `65 82 62 <pos> 64 8317 c2 19 <usb_id> 1a ff` | amp→Litigator |
| `0x29` | **set bypass** | `65 82 62 <pos> 3b <c2=off\|c3=on>` | amp off/on |
| `0x47` | **save preset** (ed03) | `65 83 6b 01 6c <slot> 6d <str> <name\0>` | 02A→14A "WT:Main" |
| `0x06` | **rename preset** (on **ef03**) | `65 83 6b 01 6c <slot> 6d <str> <name\0>` | 14A→"RenameTest" |
| `0x4e` | focus/select block (UI state) | `65 81 62 <pos>` | precedes adds |

### Field encodings
- **block position** `62 <pos>` — 1-based physical slot (amp=6, delay=8, etc.). Uniform across ops.
- **usb_id (model)** `c2 19 <msgpack-uint> 1a ff` (chain-read/write); **looper** uses `84 08 <id> 09`.
  msgpack uint: fixint `<0x80`, `cc`+u8, `cd`+u16 BE. Crosswalk in `usb_id_crosswalk.json`.
- **param value** `ca <IEEE-754 float32 BE>` — normalized 0.0 (min) … 1.0 (max); knob 0–10 maps linearly.
- **param index** the byte after `1c` in set-param: amp Drive/Gain=0, Bass=1, Mid=2, Treble=3
  (sequential knob order; likely per-model).
- **preset index** `6c <u8>` = `(bank−1)×4 + slot` where A=0,B=1,C=2,D=3 (13A=48=`0x30`).
- turning a knob **streams** intermediate values (a float sweep); replay sends only the final value.
- **strings (preset names)** — null-terminated msgpack fixstr `a<len>` (e.g. "RenameTest\0" =
  `ab 52656e616d6554657374 00`; "WT:Main\0" = `a8 …`).
- **two command scopes / channels:** block-level edits (bypass/model/param/add/remove) ride **`ed03`**;
  preset-level ops — **rename `0x06`** and a preset-context select `0x01` — ride **`ef03`**. (Save `0x47`
  addresses the slot but was seen on `ed03`.)

## Confidence
Frame / handshake / channels / counters: **solid** — no checksum (verified across 100% of frames),
all counters monotonic, handshake fully templated, ACKs echo `seq`. Load-preset & param-addressing:
**high** (exact index math + sequential param ids). Set-model, bypass, add: **high** (matched labeled
stimulus). Remove: **tentative** (one example). Still open before the first write: `seq` START value on
a *fresh* connect (seen 1000 here — confirm it's the session start); whether the device validates the
counters; large-transfer fragmentation; event / NAK formats. None **replay-verified** yet — plan Step 5.

## Coverage vs POD Go Edit (editing)
Decoded: load preset · set model · add/remove block · set bypass · set param · read chain (usb_ids).
Not yet: move block · save/rename preset · globals/I/O · snapshots/footswitch · tuner/tap · block
position (pre/post) · read commands (fetch chain/preset-list). → next capture batches + Step 5 client.
