# Data-Quality Findings

Issues surfaced by the classifier (`tools/`) when the library was reorganized.
Files were renamed to match their **actual contents**; the discrepancies below are
recorded here and in [registry/combinations.json](../../registry/combinations.json)
(`notes` + `original_file`). Items marked **verify** likely warrant an on-device
check or fix by the author.

↩ [knowledge index](README.md)

> Several of these defects double as **demonstrators** — they're the evidence for
> schema/economy rules. The dropped slot, duplicate built-in, trailing comma, and phantom
> slot are catalogued in
> [`data-presets/demonstrations/manifest.json`](../../data-presets/demonstrations/manifest.json)
> and cross-referenced from [business-rules.md](../presets/business-rules.md).

## Working presets

- **`no-cab/7_---E-_A-.pgp`** (was `7bl_Eq_Fx_loopr_Amp.pgp`) — **verify.** The old
  name claimed an FX Loop and a Looper, but the file contains **neither** (only
  EQ + Amp, 7 free blocks). Renamed to match content. If FX Loop + Looper were
  intended, re-export a corrected preset.

- **`no-amp/5_V-FEL_-C.pgp`** (was `5bl_Fx_Eq_Lpr_Cab.pgp`) — **verify.**
  Two issues: (1) the old name omitted a **Volume** block that is present; (2) it is
  **not a blank slate** — it ships with a full loaded chain (Comp / Dist / Chorus /
  Delay / Reverb). Also a no-amp config, which is otherwise unproven. Decide whether
  to clear the effects (blank-slate intent) or keep it as a demo.

- **`with-amp-cab/5_--F-L_AC.pgp`** (was `6bl_Fx_Lpr_Amp_Cab.pgp`) —
  **verify / fixable.** The file is missing slot **`block5`**, so it exposes only
  **5** free blocks despite the original `6bl` name. Almost certainly an accidental
  drop. To restore the intended 6th free block, add `"block5": { "@position": 5 }`
  to `dsp0` (its free count then becomes 6, so it should be renamed to `6_--F-L_AC`).

## Broken presets

- **`with-amp-cab/6_V----_AC_bad.pgp`** (was `6bl_Vol_Fx_Amp_Cab BROKEN`) —
  contains **two Volume blocks** (duplicate) and no FX Loop despite the old name.
  The duplicate built-in is a plausible cause of breakage.

- **`with-amp-cab/7_V----_AC_bad.pgp`** (was `7bl_Vol_Amp_Cab BROKEN`) —
  **malformed JSON**: a trailing comma makes it invalid to strict parsers (POD Go
  tolerates it; our tools recover and flag `parse: recovered-trailing-comma`).

- **`with-amp-cab/7_--F--_AC_bad.pgp`** — 7 free blocks while the FX Loop is
  present; per the assignable-block ceiling the 7th free slot can't be assigned.

- **`no-amp-and-cab/*`** — every "no amp and cab" experiment is broken, and several
  have **collapsed to 8–9 `blockN` slots** (vs the healthy 10). Strong evidence that
  removing both Amp and Cab destabilizes the chain. See
  [blocks-and-constraints.md](../presets/blocks-and-constraints.md).

## Names regenerated to the unified scheme

All 23 presets were renamed to the [unified naming
scheme](../presets/naming-and-registry.md#preset-naming-convention)
(`<free>_<V W F E L>_<A C>`) — the same string is now the filename, the registry `id`,
and the `meta.name`.

Regenerating the `meta.name` from contents surfaced the **same class of lie the
filenames carried**: several old device names reported the wrong free-block count or
phantom blocks. Examples (old `meta.name`, before the rewrite):

| Preset | Old `meta.name` | Claimed | Actual |
| --- | --- | --- | --- |
| `no-amp-and-cab/4_VWFE-_--_bad` | `6/VWFxEq` | 6 free | 4 free |
| `no-amp-and-cab/5_V--EL_--_bad` | `7/VolEqLpr` | 7 free | 5 free |
| `no-amp-and-cab/5_V-FEL_--_bad` | `6/VolFxEqLpr` | 6 free | 5 free |
| `no-amp-and-cab/6_--FEL_--_bad` | `7/FxEqLpr` | 7 free | 6 free |
| `with-amp-cab/6_V----_AC_bad` | `6bl/Fx/Vol` | an FX Loop | vol only, no FX Loop |

The inflated free-counts cluster on the `no-amp-and-cab` experiments — consistent
with the author naming them from the pre-collapse 10-slot assumption before the
chain dropped to 8–9 slots (see [blocks-and-constraints.md](../presets/blocks-and-constraints.md)).
Fixed by generating the name from contents via `podgo.canonical_name`;
`validate_presets.py` now asserts the filename stem, the registry `id`, and the
`meta.name` are all that one canonical name (≤16 chars), so a stale name can no longer
slip in on any of the three.

## Re-checking

Run `python3 tools/validate_presets.py` after any edit — it re-derives each
preset's taxonomy, free-block count, name, and on-device `meta.name` from contents
and fails on mismatch. It currently passes with 0 errors.
