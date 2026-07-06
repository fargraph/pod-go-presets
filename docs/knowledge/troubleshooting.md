# Troubleshooting

## Assigning a "stuck" free block

↩ [knowledge index](README.md)

Free blocks that seem unassignable (the top dial won't change effect categories)
can still take a **Looper**. Scroll the top dial even though nothing appears to
happen, then scroll the bottom dial — the category/selection will change but you
**cannot** select any of these effects. Blindly work the upper dial to the
**Looper** category, then use the lower dial to pick the Looper. The Looper should
select.

> If a preset has more than the assignable ceiling of free blocks (e.g. 7 free
> while keeping Volume or the FX Loop), the extra slot is a phantom and can't be
> assigned at all. That's a design limit, not a bug — see
> [blocks-and-constraints.md](../presets/blocks-and-constraints.md).

## Footswitch / snapshot out of sync

If a footswitch that controls parameters gets out of sync (e.g. a toggle is
reversed in one snapshot vs others), edit the controller entry and set
`@fs_enabled` to `false`:

```jsonc
"controller": {
  "dsp0": {
    "block7": {
      "Mix": {
        "@fs_momentary": false,
        "@controller": 4,
        "@fs_enabled": false,   // <-- set this to false
        "@fs_customlabel": "Delay",
        "@fs_label": "Mix"
      }
    }
  }
}
```

## Parameter assignments

Parameter assignments use `"@controller": 3` through `"@controller": 8`.

## Preset reads as broken or "off" — schema-level causes

These are the recurring, file-level problems, each with a preset that demonstrates it (open
it and compare against the base). Full catalog:
[`data-presets/demonstrations/manifest.json`](../../data-presets/demonstrations/manifest.json).

- **Fewer free blocks than expected → a dropped slot.** If a preset shows one fewer free
  block than intended, a `blockN` slot was likely deleted during editing (9 slots, not 10).
  Add the missing `"blockN": { "@position": N }` back to `dsp0`. Demonstrator:
  [`5_--F-L_AC.pgp`](../../presets/with-amp-cab/5_--F-L_AC.pgp) (missing
  `block5`). See [data-quality.md](data-quality.md).
- **A 7th free block won't assign → the phantom-slot ceiling.** If Volume or the FX Loop is
  still present, the 7th free slot is a phantom the UI shows but can't assign — remove
  *both* Volume and FX Loop for a genuine 7. Demonstrator:
  [`7_--F--_AC_bad.pgp`](../../presets/with-amp-cab/7_--F--_AC_bad.pgp).
- **A duplicate built-in block.** Two of the same built-in (e.g. two Volume blocks) can
  break a preset. Demonstrator:
  [`6_V----_AC_bad.pgp`](../../presets/with-amp-cab/6_V----_AC_bad.pgp).
- **Fewer blocks than authored → an import constraint was hit.** A preset that exceeds one
  of POD Go's import (“translation”) constraints still imports, but the unit **fills blocks
  from the input and silently drops the trailing ones** — leaving empty slots, audio still
  passing, UI responsive (graceful, not a crash). The two that bite in practice: **max DSP
  load** (heavy chains) and a **block-count** cap (even light chains); plus the ≤ 1
  **amp/cab/IR** caps. Fix by lightening the chain and/or using fewer blocks. Note **catalog
  `load` is only a rough proxy for the DSP %**, not an exact budget. Demonstrators:
  [`dsp-over-budget-test.pgp`](../../data-presets/demonstrations/dsp-over-budget-test.pgp)
  (DSP load) and
  [`usb-id-calibration.pgp`](../../data-presets/demonstrations/usb-id-calibration.pgp)
  (block count). See [blocks-and-constraints.md](../presets/blocks-and-constraints.md) ·
  *Import-translation constraints*.
- **Name shows truncated after import.** `meta.name` caps at 16 characters; a longer name
  is silently cut to the first 16 on import — not rejected. Demonstrator:
  [`name-overlength.pgp`](../../data-presets/demonstrations/name-overlength.pgp).

## A `.pgp` won't parse in a strict tool (but POD Go loads it)

POD Go tolerates a **trailing comma** that strict JSON parsers reject; our tools recover
and flag it (`parse: recovered-trailing-comma`). Don't "fix" it by reformatting the file —
that changes bytes device-wide (it also normalizes `\/` → `/`). Demonstrator:
[`7_V----_AC_bad.pgp`](../../presets/with-amp-cab/7_V----_AC_bad.pgp). See
[pgp-format.md](../presets/pgp-format.md) and the `no-reformat-pgp` rule in
[business-rules.md](../presets/business-rules.md).

## Reporting a problem

Open an issue with as much detail as possible: screenshots/photos/video, a clear
description of the problem and expected behavior, and your **firmware version**.
