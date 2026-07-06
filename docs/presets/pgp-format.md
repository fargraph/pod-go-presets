# The `.pgp` File Format

A `.pgp` preset is a **JSON** file exported by POD Go Edit. Everything in this
library targets **POD Go firmware v2.50**; no backward-compatibility guarantees.

↩ [presets index](README.md)

> This page is the practical "inspect & edit safely" guide. For the formal,
> machine-readable structure see [pgp-schema.md](pgp-schema.md) +
> [`registry/pgp.schema.json`](../../registry/pgp.schema.json). The
> [base preset](../../original/New-Preset-2_50_0.pgp) is the worked example throughout.

## Top-level shape

```
(root)
├── schema          "L6Preset"   — the preset format id (shared with Helix .hlx)
├── version         6            — L6Preset schema version (POD Go fw v2.50)
├── meta            top-level export metadata
└── data
    ├── meta            name (data.meta.name is the on-device name), application, build_sha, …
    ├── device          numeric device id
    ├── device_version
    └── tone
        ├── global      @model, @cursor_group, @pedalstate, @current_snapshot, @tempo
        ├── dsp0        THE SIGNAL CHAIN — blockN slots + input/output
        ├── dsp1        (unused on POD Go, empty)
        ├── snapshot0..3  per-snapshot block on/off + names
        ├── footswitch  (present only once assignments exist)
        └── controller  (present only once assignments exist)
```

> **Format id:** the top-level `schema` = `"L6Preset"`, `version` = `6` (POD Go
> firmware v2.50). The on-device preset name lives at **`data.meta.name`**, not the
> top-level `meta`.

## The chain: `data.tone.dsp0`

Ordered `blockN` slots plus `input` (`P34_AppDSPFlowInput`) and `output`
(`P34_AppDSPFlowOutput`). See [blocks-and-constraints.md](blocks-and-constraints.md)
for what the slots mean.

- Empty free block: `{ "@position": 9 }`
- Occupied block: `@model`, `@type`, `@position`, `@enabled`, plus params.
- `@type` — the block's **DSP class**, not a built-in flag and not the mono/stereo flag.
  See [The `@type` field](#the-type-field) below.
- Reordering blocks changes both the `blockN` index and `@position`.

> **See it:** the [base preset](../../original/New-Preset-2_50_0.pgp) shows the empty-block
> shape (`block2/3/8/9`), every `@type` value, and the full assignment sections — rules
> `empty-free-block-shape`, `block-type-values`, `assignment-sections-shape` in
> [business-rules.md](business-rules.md).

### The `@type` field

`@type` is a coarse **DSP/structural class** for a block — how POD Go's engine treats it —
**not** a built-in marker and **not** the mono/stereo flag (width lives in the `@model`
suffix; see [model-id-conventions.md](../reference/model-id-conventions.md#mono-vs-stereo-suffix)).
Observed across the whole library:

| `@type` | Class | Members |
| --- | --- | --- |
| 0 | generic series/insert effect | comp, dist, EQ, mod, filter, wah, volume, gate, pitch, **cab-mic-IR**, and *non-trails* delays |
| 1 | Amp | |
| 2 | Cab | the speaker/impulse engine (distinct from cab-mic-IR, which is type 0) |
| 4 | Looper | |
| 5 | **trails-capable** time-based / send-return | almost all delays, **all** reverbs, the FX Loop |
| 6 | pitch/synth subtype | |

The one reliable signal is **`@type=5` ↔ the `@trails` field, 1:1** — every type-5 block
carries `@trails` (spillover tails). The only delays that *aren't* type 5 are the three where
tails make no sense — `DelayDoubleDouble`, `VIC_DelayRatchet`, `VIC_DelayStutterEdit` — and
they drop to type 0 with no `@trails`.

> **No built-in flag exists.** A user-assigned FX block and a factory built-in are
> **structurally identical** — same fields (`@model`, `@type`, `@position`, `@enabled`,
> `@no_snapshot_bypass`, params). Nothing in the JSON marks a block as built-in; the role is
> inferred from the **`@model` id alone** (its prefix — see
> [model-id-conventions.md](../reference/model-id-conventions.md#built-in-block-id-prefixes-how-the-tools-detect-role)).
> `@type` only *partially* leaks role: values 1/2/4 uniquely imply amp/cab/looper, but 0 and 5
> are shared with ordinary user effects.

## Inspecting a preset

Don't eyeball JSON — parse it. The `tools/` scripts do this; quick one-liner:

```bash
python3 -c "import json,sys; d=json.load(open(sys.argv[1]))['data']['tone']['dsp0']; \
[print(k, v.get('@model','(free)')) for k,v in sorted(d.items()) if isinstance(v,dict)]" \
presets/with-amp-cab/7_---E-_AC.pgp
```

## Editing conventions

Intended published state is a **blank slate**: no user effects loaded in free
blocks, no footswitch assignments, no snapshots. When cleaning a preset, these
keys are safe to delete — POD Go rebuilds them:

- `snapshot0`–`snapshot3` — rebuilt on import
- `footswitch` — rebuilt on first assignment
- `controllers` / `controller` — rebuilt on first assignment

## Gotchas

- **Don't reformat `.pgp` files.** They're in `.prettierignore` (`*.pgp`);
  reformatting creates noisy, meaningless diffs. Note POD Go escapes forward slashes
  in strings as `\/` (e.g. `meta.name` `"5bl\/FxEqLpr\/-Amp"`) — a JSON re-serializer
  normalizes `\/` → `/`, changing bytes without changing meaning. Exactly the noise the
  ignore rule prevents. When hand-editing, preserve the `\/` form.
- **Trailing commas.** At least one hand-edited preset has a trailing comma that
  makes it invalid JSON; POD Go tolerates it but strict parsers don't. Our tools
  recover from it and flag it (`parse: recovered-trailing-comma`). Demonstrator:
  [`7_V----_AC_bad.pgp`](../../presets/with-amp-cab/7_V----_AC_bad.pgp).
- **`meta.name` is capped at 16 chars.** Hand-editing a longer name is pointless —
  POD Go truncates it to 16 on import. Symbols/spaces are allowed; `/` is stored as
  `\/`. See name/filename limits in [naming-and-registry.md](naming-and-registry.md).
  Demonstrators: [`name-overlength.pgp`](../../data-presets/demonstrations/name-overlength.pgp),
  [`name-slash-escape.pgp`](../../data-presets/demonstrations/name-slash-escape.pgp).
- **Dropped slots.** A preset can end up with fewer than 10 `blockN` entries if a
  free slot was accidentally removed during editing (see
  [data-quality.md](../knowledge/data-quality.md)). That silently lowers the free-block count.
  Demonstrator: [`5_--F-L_AC.pgp`](../../presets/with-amp-cab/5_--F-L_AC.pgp).
