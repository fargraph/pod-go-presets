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

## Command envelope (on channel 8010ed03)
Inside the payload, after an inner sub-header (partially decoded — carries 2 rolling counters +
a u32-LE inner length), the operation is a **msgpack-ish** blob:
```
83 66  cd <seq:u16>  64  <OPCODE>  65 <8Y>  <fields…>
```
- `cd <seq>` — per-command **sequence counter** (~1000+, increments). Plus two more counters in the
  inner sub-header (request-id / offset, TBD). Replay must reproduce whichever the device validates.
- `<OPCODE>` — the byte after `64`. `<8Y>` — msgpack map size (81/82/85 = 1/2/5 fields).

### Opcode table (decoded)
| opcode | operation | field tail | example |
| --- | --- | --- | --- |
| `0x14` | **load preset** | `6b 01 6c <preset_index>` | 13A→`6c 30`, 12A→`6c 2c` |
| `0x1c` | **remove block** *(tentative)* | `65 81 62 <pos>` | remove @pos 3 → `1c 65 81 62 03` |
| `0x1e` | **set param** | `65 85 62 <pos> 1d c3 1a 00 1c <param> 77 ca <f32>` | Mid→0.5 |
| `0x27` | **add block** | `65 82 62 <pos> 63 82… c2 19 <usb_id> 1a ff 09 …defaults` | add Minitaur@3 |
| `0x28` | **set model** | `65 82 62 <pos> 64 8317 c2 19 <usb_id> 1a ff` | amp→Litigator |
| `0x29` | **set bypass** | `65 82 62 <pos> 3b <c2=off\|c3=on>` | amp off/on |
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

## Confidence
Load-preset & param-addressing: **high** (exact index math + sequential param ids). Set-model,
bypass, add: **high** (matched labeled stimulus). Remove: **tentative** (one example). Inner-header
counters: **partial**. None **replay-verified** yet — that is plan Step 5.

## Coverage vs POD Go Edit (editing)
Decoded: load preset · set model · add/remove block · set bypass · set param · read chain (usb_ids).
Not yet: move block · save/rename preset · globals/I/O · snapshots/footswitch · tuner/tap · block
position (pre/post) · read commands (fetch chain/preset-list). → next capture batches + Step 5 client.
