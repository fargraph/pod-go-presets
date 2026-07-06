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
data
├── meta            name, application, build_sha, modifieddate, appversion
├── device          numeric device id
└── tone
    ├── global      @model, @cursor_group, @pedalstate, @current_snapshot, @tempo
    ├── dsp0        THE SIGNAL CHAIN — blockN slots + input/output
    ├── dsp1        (unused on POD Go, empty)
    ├── snapshot0..3  per-snapshot block on/off + names
    ├── footswitch  (present only once assignments exist)
    └── controller  (present only once assignments exist)
```

## The chain: `data.tone.dsp0`

Ordered `blockN` slots plus `input` (`P34_AppDSPFlowInput`) and `output`
(`P34_AppDSPFlowOutput`). See [blocks-and-constraints.md](blocks-and-constraints.md)
for what the slots mean.

- Empty free block: `{ "@position": 9 }`
- Occupied block: `@model`, `@type`, `@position`, `@enabled`, plus params.
- `@type` by role (factory): Volume 0, Wah 0, FX Loop 5, EQ 0, Looper 4, Amp 1,
  Cab 2/0. Some Delay/Reverb blocks are type 5.
- Reordering blocks changes both the `blockN` index and `@position`.

> **See it:** the [base preset](../../original/New-Preset-2_50_0.pgp) shows the empty-block
> shape (`block2/3/8/9`), every `@type` value, and the full assignment sections — rules
> `empty-free-block-shape`, `block-type-values`, `assignment-sections-shape` in
> [business-rules.md](business-rules.md).

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
