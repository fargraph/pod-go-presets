# The USB block id (`usb_id`) ↔ `@model`

Over USB, POD Go refers to a block by a **small integer** (`usb_id`), not by its `@model`
string. This page covers the wire **encoding** (hardware-confirmed), why the **id → `@model`
map is device-internal** (confirmed by decompiling POD Go Edit — it is *not* in the app), and
the one structural regularity that *does* hold and how to exploit it to grow the crosswalk.

↩ [reference index](README.md)

## Encoding — how a `usb_id` is stored on the wire (verified, v2.50)

In each occupied slot section of the preset stream, the `usb_id` is a **MessagePack uint**
stored right after the constant `c2 19` prefix, immediately before the `1aff09` marker:

- fixint (`< 0x80`, 1 byte), `0xcc` = uint8, `0xcd` = uint16 **big-endian**.
- **Amps and cabs use the same encoding.** The **Looper** is the exception: it carries its
  id as `84 08 <uint> 09` (not `c2 19 … 1aff09`), so a plain `c2 19` scan misses it.

Hardware-confirmed on two independent captures (Vol `224`, Amp `289`, EQ `472` re-read
identically across two presets). This is the project's first ✅ verified rule
([`usb-id-decode`](../../registry/rules.json)); decoded by
[`tools/podgo_usb.py`](../../tools/podgo_usb.py). See
[knowledge/verified.md](../knowledge/verified.md) for the ledger entry and demonstrators.

The editor **sends** these ids too (host→device): a set-model frame carries
`… c2 19 cd 01 1e …` = uint16 `0x011E` = `286` (Line 6 Litigator); an add-block carries
`c2 19 5c` = `92` (Minitaur). So the mapping is used in **both** directions.

## The `usb_id → @model` map is device-internal — confirmed by decompilation

POD Go Edit's Mac binary (`POD Go Edit.app/Contents/MacOS/POD Go Edit`, v2.50) is an
**x86-64 Mach-O, unstripped, ~45,600 C++ symbols**, which made the internals fully
navigable. The mapping is **not present as extractable static data** anywhere in the app —
verified several independent ways (decompilation analysis, **not** a hardware fact):

- **No catalog field.** [`PodGoModelDefs.bin`](resources.md) (MessagePack, the 574-model
  array) has only `params · symbolicID · name · load · category · cablink · capEdge ·
  devices · ircablink · meter*`. **No usb_id.** Same for `PGModelCatalog.bin/json`, the
  per-category `*.models`, `PGControls.json`, and `PodGo.sym` (which is a `symbol → param-name`
  list). `main.imb` is a zlib PNG atlas.
- **No static id array**, in *any* model order (defs order, catalog-traversal order,
  per-category order), at any width (u16/u32, LE/BE), contiguous or strided ≤256 B. Litigator
  `286` and Del Sol `289` are **adjacent** in the defs array, yet the pair `286,289` occurs
  nowhere as adjacent values.
- **No string- or hash-keyed table.** The executable contains **zero `HD2_…` symbolicID
  strings**. `ModelIDHash()` is just **FNV-1a** (basis `0x811c9dc5`, prime `0x01000193`) for
  the `L6HashTable<L6String, ModelDef*>` buckets — and none of those hashes appear in the
  binary either. `L6EdLibModelDefs::ModelDef` exposes only `getAttr(name)` over the `.bin`
  dict; it has **no numeric-id accessor**.
- **The editor keeps blocks as numeric ids at runtime.** In the HelixCore codec,
  `L6VariantToHCPModel()` reads the model as a plain `int` straight into the
  `HelixCore_Preset_Model` struct (blocks live in a `RedBlackTree<unsigned int,
  HelixCore_Preset_Model>` keyed by the id). So the id is *already* a number by the time it
  reaches the wire; the `symbolicID → id` conversion happens once, upstream, and is **not**
  backed by app data.
- **The device never sends symbolicID strings, nor a bulk model manifest.** Across the
  captures the largest device→host transfer is ~20 B; no `HD2_` strings appear inbound.

**Conclusion:** the numbers come from the **device**, not from POD Go Edit's shipped data.
This is why no amount of catalog re-ordering reproduces them, and why the crosswalk must be
built empirically (or pulled from the device).

> Earlier note said "not the `PodGoModelDefs` array index (Deluxe Comp is `99`, not index
> `193`), not the community `helix_usb` modules table, no catalog ordering reproduces it."
> The decompilation **confirms and explains** that: it isn't a re-ordering of app data at all.

## The one regularity: monotonic within a category

Cross-referencing the hardware-confirmed pairs against `PodGoModelDefs.bin`, `usb_id` is
**strictly increasing with defs-order *within* each category** — but **not** globally, and
categories are **not** contiguous in id-space (they interleave):

| Category | defs-order examples (defidx → usb_id) |
| --- | --- |
| Amp | 55→**286**, 56→**289**, 86→**527** |
| Compressor | 193→**99**, 195→**101**, 196→**304** |
| Distortion | 258→**93**, 263→**98**, 289→**434** |
| Cab | 127→**551**, 165→**552** |
| Modulation | 363→**249**, 372→**387** |
| EQ | 312→**445**, 317→**472** |

That signature says `usb_id` is the **Helix/HX platform's global model id, assigned in
historical / firmware-introduction order.** POD Go's model set is a subset of the HX universe
that preserves *relative order within a category* but not the cross-category interleaving — so
the interleaving simply isn't recoverable from POD Go Edit's local data. *(Inference from the
23 known pairs; treat the generalization to all 574 as unverified.)*

**Why it's useful anyway:** monotonicity is a hard **validation constraint** — any newly
captured pair must not invert its category's known order — and it lets you **bound** an unknown
id between its known category neighbors.

## Growing the crosswalk (10→574)

The partial, hardware-read map lives in
[`registry/usb-id-map.json`](../../registry/usb-id-map.json). Two ways to extend it:

1. **Empirical captures (current method).** Load a preset with known blocks, capture the
   stream, decode with [`tools/podgo_usb.py`](../../tools/podgo_usb.py), and record each
   slot's `usb_id` against the block you know is there. Slow but reliable; validate new pairs
   against the monotonic-within-category constraint above.
2. **Per-category model-list fetch (proposed, untested).** The device appears to hand the
   editor per-category numeric id lists aligned to its catalog order (that alignment is what
   makes the ids monotonic). Capturing the editor *opening the model picker for each block
   type once* — connected to the unit — should yield a numeric list per category that aligns
   1:1 with that category's `.models` order, giving the whole table in one session. The
   existing captures only touched a few blocks, so they don't contain it.

A runtime (lldb) dump of the editor's block-id map with the unit connected is a third,
heavier option. **All routes require the hardware** — the app alone cannot produce the ids.

## Related

- Wire framing, opcodes, and the command envelope: `tools/usb-intercept/protocol.md`
  (working spec, outside `docs/`).
- POD Go Edit's on-disk resources and the model catalog:
  [block-models.md](block-models.md), [resources.md](resources.md).
- `@model` *string* anatomy (a different id system): [model-id-conventions.md](model-id-conventions.md).
