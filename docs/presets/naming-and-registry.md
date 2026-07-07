# Naming & Registry

## Preset naming convention

↩ [presets index](README.md)

Every preset carries **one name** — the same string is the `.pgp` filename stem, the
registry `id`, **and** the on-device `meta.name`. It's derived from the file's actual
contents by `tools/podgo.py` (`canonical_name`) and enforced by `validate_presets.py`,
so the name never lies about the file, and **what you download matches what the unit
shows** — no mental translation between a file and its on-device name.

```
<free>_<V W F E L>_<A C>[_bad][<variant>]
```

- `<free>` — the user-assignable block count. It leads because free blocks are the
  payload of a jailbreak, and it is **not** derivable from the letters alone (slot
  count drops to 8/9 when Amp/Cab are removed).
- **Middle** field `V W F E L` and **rig** field `A C` are *fixed slots* in
  signal-chain order: a **letter = that built-in is present**, a **dash (`-`) = it
  was removed**. `V`=Volume `W`=Wah `F`=FX Loop `E`=EQ `L`=Looper · `A`=Amp `C`=Cab.
- A trailing **`_bad`** field = broken on hardware (`!` was avoided — it triggers shell
  history expansion; status is also authoritative in the registry).
- An optional trailing **digit** (`variant`) disambiguates two identical-content presets.

Examples: `7_---E-_AC` (7 free · EQ · full amp+cab rig), `5_V-FEL_-C` (5 free · no amp,
cab kept), `5_VWFEL_--_bad` (5 free · no amp/cab · broken), `5_VWFEL_--_bad2` (its variant).

Why this shape: it fits the device's **16-char cap** (the whole library is 10–12 chars,
so nothing truncates), the two `_` separators give the eye stable anchors — *how many
free · what's in the chain · what rig* — and the narrow `-` markers let the present-block
letters pop on the device's proportional font. Crucially, `_` separates the fields while
`-` marks removed blocks: two distinct jobs, two distinct glyphs, and **both are legal
filename characters on every OS**, so the filename can be byte-identical to the `meta.name`
(unlike `/`, which is filename-illegal and POD Go stores escaped as `\/`).

> **Status:** confirmed on hardware (v2.50) — the `_` glyph renders and loads fine on the
> unit (owner-tested with a renamed preset), so the scheme's characters (digits, block
> letters, `_`, `-`) are all legible on the device. The `_bad` tag is new and hasn't been
> loaded directly yet, but it's only `_` + letters, both proven. Tracked in
> [verified.md](../knowledge/verified.md).

## Name & filename limits (hardware-verified, v2.50)

POD Go treats three things as independent, and our convention above **deliberately
collapses them into one**. The underlying rules still explain *why* the unified name is
shaped the way it is — keep them straight:

- **Preset name** (`data.meta.name`, what the device stores/shows): **hard cap of 16
  characters.** POD Go Edit will not let you type past 16, and the screen displays all
  16 (verified with `1234567890123456`). Letters, digits, **spaces, and symbols**
  (`/ - )` …) can all be entered directly on the hardware — they are not merely
  JSON-injection artifacts. **On disk, POD Go escapes a forward slash as `\/`** (an
  optional JSON escape that decodes back to `/`): the name `5bl/FxEqLpr/-Amp` is stored
  in the raw `.pgp` as `"5bl\/FxEqLpr\/-Amp"`. To match POD Go's byte-for-byte output
  when hand-editing, write `\/`; a bare `/` parses fine but won't match the device's
  own serialization (see the reformatting gotcha in [pgp-format.md](pgp-format.md)).
  The [unified naming convention](#preset-naming-convention) uses `_` (a filename-safe
  character), so our generated names need no escaping or sanitization at all; this note
  still applies to any legacy or hand-typed name containing a slash.
- **Over-length names on import:** a hand-edited `meta.name` longer than 16 chars is
  **silently truncated to 16 on import** (the preset is not rejected).
- **`.pgp` file name** (on your computer): decoupled from the preset. Export proposes a
  filename derived from `meta.name` but **sanitizes filesystem-illegal characters** — a
  preset named `5bl/FxEqLpr/-Amp` exports as `5bl_FxEqLpr_-Amp.pgp` (each `/` → `_`).
  **Import ignores the filename entirely and reads `meta.name`,** so renaming the file
  on disk has no effect on the loaded preset name. Because our unified names use only
  filename-safe characters, no sanitization occurs — the exported filename equals the
  `meta.name` byte-for-byte, which is the whole point of the shared scheme.

> **Demonstrators:** [`name-overlength.pgp`](../../data-presets/demonstrations/name-overlength.pgp)
> (16-char cap / truncation) and
> [`name-slash-escape.pgp`](../../data-presets/demonstrations/name-slash-escape.pgp)
> (`/` stored as `\/`) — each is the [base preset](../../original/New-Preset-2_50_0.pgp)
> plus one name edit. Rules `name-16-cap`, `name-slash-escape` in
> [business-rules.md](business-rules.md).

## Folders = removal taxonomy

`presets/{with-amp-cab, no-cab, no-amp, no-amp-and-cab}/`. The folder encodes which
of Amp/Cab were removed (the validity-critical axis), **not** working/broken status.
See [blocks-and-constraints.md](blocks-and-constraints.md).

## The registry

Machine-readable source of truth under [`registry/`](../../registry):

- **`combinations.json`** — one entry per preset: `id`, `file`, `status`
  (`working`/`broken`), `taxonomy`, `free_blocks`, `slots`, per-role `blocks`
  flags, `loaded_user_fx`, `duplicate_builtins`, `parse`, `original_file`, `notes`.
  **Status is authoritative here** (the name only mirrors it via the trailing `_bad` tag).
- **`presets.csv`** — the same presets flattened to one filterable table (working
  and broken together, status inline). GitHub renders it with search + column sort.
  Generated from `combinations.json` by `tools/gen_matrix.py`.
- **`blocks.json`** — every distinct `@model` id we've captured, from
  `data-presets/` + `presets/`, with a heuristic category. Generated by
  `tools/harvest_blocks.py`.
- **`reference-models.json`** — the authoritative POD Go model list by category
  (see [reference/block-models.md](../reference/block-models.md)).
- **`pgp.schema.json`** — JSON Schema (draft 2020-12) for a well-formed `.pgp`
  (see [pgp-schema.md](pgp-schema.md)).
- **`rules.json`** — semantic rules + knowledge with a **verified/unverified** status
  and demonstrator linkage (see [business-rules.md](business-rules.md)). **Authoritative
  for rule status.**
- **`model-catalog/podgo-edit-<ver>.json`** — versioned snapshots of POD Go Edit's
  authoritative model catalog (name, category, DSP `load`, param schema, firmware
  provenance, keyed by `@model`), produced by `tools/extract_podgo_catalog.py`. See
  [reference/block-models.md](../reference/block-models.md).
- **`usb-id-map.json`** — partial, hardware-confirmed `usb_id → @model` crosswalk (the small
  integer POD Go reports over USB → the block model). Grown empirically from captures; see
  [reference/usb-id-mapping.md](../reference/usb-id-mapping.md) (encoding, why it's
  device-internal, how to extend it) and rule `usb-id-decode` in `rules.json`.

## Tools

Run from the repo root:

| Command | Does |
| --- | --- |
| `python3 tools/refresh.py` | **After adding data-presets:** harvest + coverage in one step |
| `python3 tools/harvest_blocks.py` | Rebuild `registry/blocks.json` (block ids + per-preset linkage) |
| `python3 tools/coverage.py` | Rebuild `docs/reference/data-coverage.md` gap worklist |
| `python3 tools/validate_presets.py` | Check every preset matches its registry entry & name |
| `python3 tools/validate_examples.py` | Check the knowledge↔preset linkage (`registry/rules.json` + `data-presets/demonstrations/manifest.json`) |
| `python3 tools/gen_matrix.py` | Regenerate `registry/presets.csv` + the clickable preset list in the README |
| `python3 tools/extract_podgo_catalog.py` | Snapshot POD Go Edit's model catalog → `registry/model-catalog/podgo-edit-<ver>.json` |
| `python3 tools/podgo_usb.py <capture.log>` | Decode a raw POD Go USB capture → the live block chain (occupancy, on/off, `usb_id`, `@model`) |

`tools/podgo.py` is the shared library (load/parse, classify, taxonomy, naming).
`tools/podgo_models.py` reads the model-catalog snapshot (name/category/DSP `load`/params by
`@model`; falls back to live POD Go Edit if no snapshot). `tools/podgo_usb.py` decodes a raw
POD Go USB capture into the live block chain (occupancy, on/off, `usb_id`, and `@model` via
[`registry/usb-id-map.json`](../../registry/usb-id-map.json)). `tools/spikes/` holds
**experimental** USB / DSP / calibration reverse-engineering scripts (capture drivers,
calibration-preset builders, frame/DSP analysis) — not part of the validated pipeline.

## Adding a preset

1. Drop the `.pgp` into the correct `presets/<taxonomy>/` folder.
2. Name it by content (or run the classifier to derive the name).
3. Add its entry to `registry/combinations.json`.
4. `python3 tools/refresh.py` (in case it contains newly-seen block ids).
5. `python3 tools/gen_matrix.py` — refresh `registry/presets.csv` + the README list.
6. `python3 tools/validate_presets.py` — must pass.
