# Hardware-Verification Ledger

What we actually **know** about POD Go behavior vs. what's assumed. Firmware **v2.50**.
Because a preset's viability is only real on the unit (the hardware-test rule — see
[lessons-learned.md](lessons-learned.md)), this page separates confirmed facts from
research and inference so the knowledge base stays honest.

↩ [knowledge index](README.md)

**Legend:** ✅ confirmed on a unit · 🔬 inferred from the hardware-tested preset library
(inductive) · 📖 from Line 6 sources / prior user experience, not independently
re-verified here · ⏳ pending verification.

## ✅ Confirmed on hardware (v2.50)

| Fact | How | Detail |
| --- | --- | --- |
| `meta.name` hard-caps at **16 chars** — POD Go Edit won't type past it; screen shows all 16 | typed `1234567890123456` on the unit | [naming-and-registry.md](../presets/naming-and-registry.md) |
| An over-length `meta.name` is **silently truncated to 16 on import** (not rejected) | hand-edited a longer name, imported | naming-and-registry.md |
| Spaces and symbols (`/ - )` …) can be entered in names on the hardware | entered on the unit | naming-and-registry.md |
| On disk `/` is stored escaped as `\/`; the exported filename sanitizes `/`→`_`; import reads `meta.name` and **ignores the filename** | observed export/import | naming-and-registry.md, [pgp-format.md](../presets/pgp-format.md) |
| **Cab block is single-cab only** — no Helix dual-cab mode | project owner | [reference/block-models.md](../reference/block-models.md) |

## 🔬 Inferred from the tested preset library (inductive)

Working/broken statuses come from presets Clifton built and ran on the unit, so these
patterns are hardware-grounded — but they're generalizations, not exhaustively tested
for every possible combination.

| Pattern | Detail |
| --- | --- |
| `free_blocks = (blockN slots) − built-in blocks present`, base 10 slots | [blocks-and-constraints.md](../presets/blocks-and-constraints.md) |
| Removing **Amp** tends to break; removing **both Amp+Cab** collapses the chain to 8–9 slots and reliably breaks; removing only **Cab** works | blocks-and-constraints.md, [data-quality.md](data-quality.md) |
| Genuine **7 free** requires removing both Volume and FX Loop; otherwise the extra free block is phantom/unassignable | blocks-and-constraints.md |

## 📖 From Line 6 sources or prior experience (not independently re-verified here)

| Claim | Source | Detail |
| --- | --- | --- |
| The 429-model authoritative list and per-category counts | Line 6 manuals / model gallery | [reference/block-models.md](../reference/block-models.md), [resources.md](../reference/resources.md) |
| POD Go omits polyphonic pitch; single fixed FX Loop block (vs. Helix) | Line 6 / community | reference/block-models.md |
| `snapshot0–3`, `footswitch`, `controllers` are rebuilt by the device if deleted | prior user experience | [pgp-format.md](../presets/pgp-format.md) |
| EXP 1 → Wah, EXP 2 → Volume | manual | reference/block-models.md |
| `@type` values (Vol 0, Wah 0, FX Loop 5, EQ 0, Looper 4, Amp 1, Cab 2/0) | factory preset JSON | pgp-format.md |

## ⏳ Pending verification

The [README to-do](../../README.md#to-do) items each need a unit test:

- `5bl_fx_lpr_amp_cab` after re-adding the dropped `block5` — does it become a true 6-free?
- `7bl_eq_amp` — was FX Loop + Looper intended, or is EQ+Amp correct?
- `5bl_vol_fx_eq_lpr_cab` — strip to a blank slate or keep; and does this no-amp config actually work?

Also unverified: that each gap-list block id (amps/cabs/etc.) imports cleanly once captured.

---

_When you confirm or refute something on the unit, move it to the right section and, if a
fact changes, update the source doc + re-run the affected tool (e.g. `tools/coverage.py`)._
