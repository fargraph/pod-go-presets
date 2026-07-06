# Business Rules

The semantic rules a JSON schema can't express — which block combinations are *valid*, how
names and edits must behave — each tied to the preset that demonstrates it and carrying a
verified/unverified status.

↩ [presets index](README.md)

## How to read this

- **Source of truth:** [`registry/rules.json`](../../registry/rules.json). This page renders
  it; edit the JSON, not the prose counts.
- **Status is binary.** ✅ **verified** = jointly confirmed with the project owner **and**
  backed by an accompanying demonstrator preset (for viability facts, hardware-confirmed).
  ⬜ **unverified** = the honest default: presumed/expected, or not yet jointly confirmed.
  See the [verified/unverified ledger](../knowledge/verified.md).
- **Everything is currently ⬜ unverified.** Existing knowledge was reset to `unverified`;
  each item re-earns ✅ only when it's confirmed with a demonstrator. The `demonstrated_by`
  preset is already wired up for most — what's pending is the joint confirmation.
- **Demonstrator** links go to a preset that exhibits the rule; the full catalog with
  "what to observe" is [`data-presets/demonstrations/manifest.json`](../../data-presets/demonstrations/manifest.json).

## Block economy — which combinations are valid

| Status | Rule | Demonstrated by |
| :-: | --- | --- |
| ⬜ | **free-block-formula** — `free_blocks = blockN slots − built-ins present` (base 10 slots); the old "7 − Vol − Wah − FX" rule is wrong. | [base](../../original/New-Preset-2_50_0.pgp) |
| ⬜ | **phantom-slot-ceiling** — assignable ceiling is 7; keeping Volume or FX Loop at 7 free yields a phantom, unassignable slot. | [`7bl_fx_amp_cab_broken`](../../presets/with-amp-cab/7bl_fx_amp_cab_broken.pgp) |
| ⬜ | **genuine-7-free-needs-vol-and-fx-removed** — a real 7 free requires removing *both* Volume and FX Loop. | [`7bl_eq_amp`](../../presets/no-cab/7bl_eq_amp.pgp) |
| ⬜ | **keep-amp** — removing the Amp tends to break; removing only the Cab is fine. | [`6bl_vol_fx_eq_cab_broken`](../../presets/no-amp/6bl_vol_fx_eq_cab_broken.pgp) |
| ⬜ | **no-amp-and-cab-collapses** — removing both Amp and Cab collapses the chain to 8–9 slots and reliably breaks. | [`6bl_fx_eq_lpr_broken`](../../presets/no-amp-and-cab/6bl_fx_eq_lpr_broken.pgp) |
| ⬜ | **eq-or-looper-required** — at least one of EQ or Looper must remain (EQ is convertible to Looper). | _none yet_ |
| ⬜ | **cab-single-only** — single-cab only; no Helix dual-cab mode. | _none yet_ |
| ⬜ | **duplicate-builtin** — a preset can carry a duplicate built-in (two Volume blocks); a plausible break cause. | [`6bl_vol_amp_cab_broken`](../../presets/with-amp-cab/6bl_vol_amp_cab_broken.pgp) |

## Schema — structural facts about the JSON

| Status | Rule | Demonstrated by |
| :-: | --- | --- |
| ⬜ | **empty-free-block-shape** — a free block is exactly `{"@position": N}`; a healthy preset has 10 slots. | [base](../../original/New-Preset-2_50_0.pgp) |
| ⬜ | **dropped-slot-lowers-free** — a missing `blockN` silently lowers the free count. | [`5bl_fx_lpr_amp_cab`](../../presets/with-amp-cab/5bl_fx_lpr_amp_cab.pgp) |
| ⬜ | **block-type-values** — `@type` by role: Vol 0, Wah 0, FX Loop 5, EQ 0, Looper 4, Amp 1, Cab 2. | [base](../../original/New-Preset-2_50_0.pgp) |
| ⬜ | **assignment-sections-shape** — `snapshot0–3` / `footswitch` / `controller` structure (`@controller` 3–8). | [base](../../original/New-Preset-2_50_0.pgp) |
| ⬜ | **eq-static-vs-free-eq** — `HD2_EQ_STATIC_*` is the built-in preset-EQ; `HD2_EQ*` (no `_`) are free effects; they coexist. | [`EQ Page 1`](../../data-presets/EQ%20Page%201.pgp) |

See also the formal envelope in [pgp-schema.md](pgp-schema.md).

## Naming

| Status | Rule | Demonstrated by |
| :-: | --- | --- |
| ⬜ | **name-16-cap** — `meta.name` caps at 16 chars; over-length truncates on import. | [`name-overlength`](../../data-presets/demonstrations/name-overlength.pgp) |
| ⬜ | **name-slash-escape** — `/` in `meta.name` is stored escaped as `\/`; spaces/symbols allowed. | [`name-slash-escape`](../../data-presets/demonstrations/name-slash-escape.pgp) |
| ⬜ | **filename-decoupled-from-name** — export sanitizes `/`→`_` in the filename; import reads `meta.name` and ignores the filename. | _none yet_ |

## Editing

| Status | Rule | Demonstrated by |
| :-: | --- | --- |
| ⬜ | **no-reformat-pgp** — never reformat; preserve `\/` escapes and tolerated trailing commas. | [`name-slash-escape`](../../data-presets/demonstrations/name-slash-escape.pgp), [`7bl_vol_amp_cab_broken`](../../presets/with-amp-cab/7bl_vol_amp_cab_broken.pgp) |
| ⬜ | **trailing-comma-tolerated** — POD Go accepts a trailing comma strict parsers reject; tools recover + flag it. | [`7bl_vol_amp_cab_broken`](../../presets/with-amp-cab/7bl_vol_amp_cab_broken.pgp) |
| ⬜ | **blank-slate-ship** — publish blank: no loaded FX, no footswitch/controller; those keys are safe to delete. | [`7bl_eq_amp_cab`](../../presets/with-amp-cab/7bl_eq_amp_cab.pgp) |

## Flipping an item to ✅ verified

When you and the project owner confirm a rule on the unit (or, for schema facts, jointly
verify the demonstrator), set that rule's `status` to `verified` in
[`registry/rules.json`](../../registry/rules.json), ensure its `demonstrated_by` is
non-empty, and move its row here and in [verified.md](../knowledge/verified.md).
