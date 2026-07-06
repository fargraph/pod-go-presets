# Verified / Unverified Ledger

What we actually **know** on hardware vs. what's presumed. Firmware **v2.50**. Because a
preset's viability is only real on the unit, this page separates confirmed facts from
everything else so the knowledge base stays honest.

↩ [knowledge index](README.md)

## The model

Status is **binary**, and it mirrors [`registry/rules.json`](../../registry/rules.json):

- ✅ **Verified** — jointly confirmed with the project owner **and** backed by an
  accompanying demonstrator preset. For viability facts the demonstrator must be
  hardware-confirmed. **Never** set from analysis, a clean parse, or a clean import.
- ⬜ **Unverified** — the honest default: presumed/expected from research, inference, or
  Line 6 sources, or simply not yet jointly confirmed. Carries a *basis* note recording
  how we currently believe it (`hardware` · `factory-preset` · `inferred` · `source`).

> **Everything below is currently ⬜ Unverified.** The prior four-tier ledger (✅/🔬/📖/⏳)
> was collapsed into this binary split and **all entries were reset to Unverified** — a
> fact re-earns ✅ only when it is confirmed with a demonstrator, not inherited from old
> notes. Most items already have a `demonstrated_by` preset wired up
> ([manifest](../../data-presets/demonstrations/manifest.json)); what remains is the joint
> confirmation.

## ✅ Verified

_None yet._ Items land here as they're confirmed on the unit with an accompanying
demonstrator. To promote one: set its `status` to `verified` in
[`registry/rules.json`](../../registry/rules.json) (with a non-empty `demonstrated_by`),
then move its row here.

## ⬜ Unverified (with current basis)

Basis `hardware` = previously observed on a unit but reset pending re-confirmation;
`factory-preset` = read from factory JSON; `inferred` = generalized from the tested
library; `source` = Line 6 / community.

| Fact | Basis | Detail |
| --- | --- | --- |
| `meta.name` hard-caps at 16 chars; over-length truncates on import | hardware | [naming-and-registry.md](../presets/naming-and-registry.md) · rule `name-16-cap` |
| Spaces/symbols allowed in names; `/` stored escaped as `\/`; import reads `meta.name`, ignores the filename | hardware | [naming-and-registry.md](../presets/naming-and-registry.md) · rules `name-slash-escape`, `filename-decoupled-from-name` |
| Cab block is single-cab only — no Helix dual-cab mode | source | [reference/block-models.md](../reference/block-models.md) · rule `cab-single-only` |
| `free_blocks = (blockN slots) − built-ins present`, base 10 slots | inferred | [blocks-and-constraints.md](../presets/blocks-and-constraints.md) · rule `free-block-formula` |
| Removing Amp tends to break; removing both Amp+Cab collapses to 8–9 slots and breaks; removing only Cab works | inferred | [blocks-and-constraints.md](../presets/blocks-and-constraints.md) · rules `keep-amp`, `no-amp-and-cab-collapses` |
| Genuine 7 free requires removing both Volume and FX Loop; else the extra slot is phantom | inferred | [blocks-and-constraints.md](../presets/blocks-and-constraints.md) · rules `genuine-7-free-needs-vol-and-fx-removed`, `phantom-slot-ceiling` |
| At least one of EQ or Looper must remain | inferred | rule `eq-or-looper-required` |
| `@type` per role (Vol 0, Wah 0, FX Loop 5, EQ 0, Looper 4, Amp 1, Cab 2) | factory-preset | [pgp-format.md](../presets/pgp-format.md) · rule `block-type-values` |
| `EQ_STATIC_*` is the built-in preset-EQ; `EQ*` (no `_`) are free effects | factory-preset | [model-id-conventions.md](../reference/model-id-conventions.md) · rule `eq-static-vs-free-eq` |
| `snapshot0–3`, `footswitch`, `controllers` are rebuilt by the device if deleted | source | [pgp-format.md](../presets/pgp-format.md) · rule `blank-slate-ship` |
| POD Go tolerates a trailing comma strict parsers reject | inferred | [data-quality.md](data-quality.md) · rule `trailing-comma-tolerated` |
| A dropped `blockN` slot silently lowers the free-block count | inferred | [data-quality.md](data-quality.md) · rule `dropped-slot-lowers-free` |
| The 429-model list, per-category counts, EXP 1→Wah / EXP 2→Volume | source | [reference/block-models.md](../reference/block-models.md) |

## Pending a demonstrator or a unit test

The [README to-do](../../README.md#to-do) items each need a unit test, and these rules have
no demonstrator yet: `eq-or-looper-required`, `cab-single-only`,
`filename-decoupled-from-name`. Also unverified: that each gap-list block id imports cleanly
once captured. Note the [unified naming scheme](../presets/naming-and-registry.md#preset-naming-convention)
now used by every preset (filename = `id` = `meta.name`): its **`_` glyph is confirmed on
hardware (v2.50)** — the owner loaded a renamed preset and it displays and loads fine, so the
scheme is proven legible on the unit. (The new `_bad` broken tag is `_` + letters, both proven,
but hasn't been loaded directly yet. A formal ✅ ledger row would still want a rule + demonstrator.)

---

_When you confirm or refute something on the unit, update
[`registry/rules.json`](../../registry/rules.json), move the row between ✅/⬜ here and in
[business-rules.md](../presets/business-rules.md), fix the source doc, and re-run any
affected tool (e.g. `tools/coverage.py`)._
