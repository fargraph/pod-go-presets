# Lessons Learned & Data Gathered

A digest of the non-obvious things discovered building this knowledge base. Each
points to the doc with the full detail — this page is the "what surprised us" index.

↩ [knowledge index](README.md)

> **Proven by a preset?** Where a finding has a demonstrator, it's catalogued in
> [`data-presets/demonstrations/manifest.json`](../../data-presets/demonstrations/manifest.json)
> and carries a verified/unverified status in [business-rules.md](../presets/business-rules.md) /
> [verified.md](verified.md). Everything is currently **⬜ unverified** pending joint
> hardware confirmation.

## POD Go behavior (hardware facts)

- **Free blocks = `blockN` slots − built-in blocks present** (base 10 slots). The
  intuitive "7 − Vol − Wah − FX Loop" rule is **wrong** — it only coincidentally works
  for presets that keep EQ+Amp+Cab. [→ blocks-and-constraints.md](../presets/blocks-and-constraints.md)
- **Removing the Amp breaks presets; removing only the Cab is fine.** Every working
  no-cab preset works; every no-amp / no-amp-and-cab preset in the library is broken.
  Removing **both** Amp and Cab visibly **collapses the chain to 8–9 slots** (vs the
  healthy 10) — strong evidence the chain destabilizes. [→ blocks-and-constraints.md](../presets/blocks-and-constraints.md)
- **The assignable ceiling is 7, and Vol/Wah/FX Loop count against it.** Keeping Volume
  or the FX Loop while having 7 free blocks yields a *phantom* slot the UI shows but
  can't assign — the preset reads as broken. Genuine 7 free needs removing **both**.
- **Viability has multiple factors: structural rules AND POD Go's import constraints.**
  Beyond the removal taxonomy and the 7-slot ceiling, POD Go enforces a **constraint set
  when it imports a preset** — named in POD Go Edit's own error strings: **max DSP load**, a
  **block-count** cap, **≤ 1 amp/cab/IR**, plus parallel-path rules. Exceed any and POD Go
  **silently drops the trailing blocks** (audio still flows, UI responsive — hardware
  confirmed). Two test presets showed it's *not* purely DSP: a heavy one hit **DSP load**
  (kept 5 of 10), a light one hit the **block-count** cap (kept 7). Caution: the catalog
  `load` field is only a rough *relative* proxy, **not** POD Go's actual DSP % — don't sum it
  into a budget number. [→ blocks-and-constraints.md](../presets/blocks-and-constraints.md)
- **Cab is single-cab only** — POD Go does **not** have Helix's dual-cab mode. (The
  research draft claimed otherwise; the unit corrected it.) [→ reference/block-models.md](../reference/block-models.md)
- **Hardware is the only authority on viability.** Parsing/importing cleanly means
  nothing about whether a combination works. Published research and even Line 6's own
  marketing counts can be wrong; the unit wins. [→ resources.md](../reference/resources.md)

## Preset schema

- **`meta.name` caps at 16 chars**, import silently truncates longer, and the on-disk
  `.pgp` filename is decoupled from the stored name (import reads `meta.name`, not the
  filename). Symbols/spaces are allowed; `/` is stored escaped as `\/`.
  [→ naming-and-registry.md](../presets/naming-and-registry.md), [pgp-format.md](../presets/pgp-format.md)
- **One name, everywhere.** The `.pgp` filename stem, the registry `id`, and the
  on-device `meta.name` are one identical string (`<free>_<VWFEL>_<AC>`). A spelled-out
  filename reads friendlier in a raw file list, but it overruns the 16-char device cap
  and forces you to mentally map a downloaded file to its on-device name. A compact
  fixed-slot scheme fits the cap, and single-letter tokens make "list what's kept" vs
  "list what's removed" a non-choice (both stay short). Key trick: `_` separates the
  fields while `-` marks removed blocks — two jobs, two glyphs, **both filename-safe on
  every OS** — so the file can be byte-identical to the `meta.name` (unlike `/`, which is
  filename-illegal). [→ naming-and-registry.md](../presets/naming-and-registry.md)
- **`@model` ids are not display names, and prefixing is inconsistent** (`HD2_` for most,
  but also `VIC_`, `L6…`, and 18 bare-name legacy models). The full id list now comes from
  **POD Go Edit's bundled catalog** (`registry/model-catalog/`), not preset-dumping.
  [→ reference/model-id-conventions.md](../reference/model-id-conventions.md), [block-models.md](../reference/block-models.md)
- **`EQ_STATIC_*` = the fixed preset-EQ block; `EQ*` (no STATIC) = a free-block EQ
  effect.** The same EQ models exist in both forms. [→ reference/model-id-conventions.md](../reference/model-id-conventions.md)
- **Stock POD Go = 6 built-ins + 4 free in a native 10-slot chain.** POD Go's factory New
  Preset (device-sourced `original/New-Preset-2_50_0.pgp`) contains all ten `block0`–`block9`
  slots — the jailbreak *frees* built-in slots, it doesn't add them. POD Go Edit also bundles a
  `default_preset_p34.hlx` with the same 6+4 economy in a *different* slot arrangement (its
  usage is unconfirmed — per the owner, new presets come from **device firmware**, not the
  editor); together they show built-ins are **not pinned to fixed slot indices** (the amp role
  can even be a `HD2_Preamp…` id). [→ blocks-and-constraints.md](../presets/blocks-and-constraints.md)
- **`@type` is a DSP class, not a built-in or mono/stereo flag.** It buckets blocks by how the
  engine treats them (amp 1, cab 2, looper 4, trails-capable delay/reverb/FX-Loop 5, most else
  0); the clean signal is **`@type=5` ↔ the `@trails` field, 1:1**. There is **no** built-in
  marker at all — a built-in and a user-FX block are byte-shape-identical; role comes from the
  `@model` id. Width is pegged per effect in the `@model` `…Mono/…Stereo` suffix (a Helix
  carryover — path is mono pre-amp, **stereo after the cab**), and Helix's amp+cab pairing
  survives as a per-amp `cablink`, not a combined block.
  [→ pgp-format.md](../presets/pgp-format.md), [reference/model-id-conventions.md](../reference/model-id-conventions.md)
- **Some keys are safe to delete — POD Go rebuilds them** on import/first-assignment:
  `snapshot0–3`, `footswitch`, `controllers`. [→ pgp-format.md](../presets/pgp-format.md)
- **`.pgp` is JSON but hand-edits drift from POD Go's serialization:** it tolerates
  trailing commas (strict parsers don't) and escapes `/` as `\/`. Don't reformat.
  [→ pgp-format.md](../presets/pgp-format.md)

## Data-quality patterns found in the library

Classifying presets by their **contents** (not filenames) surfaced real defects —
filenames frequently lied. Examples: a name claiming FX Loop + Looper when the file had
neither; wrong free-block counts; an omitted Volume block; a **duplicate Volume block**;
a **dropped `block5` slot** silently lowering the free count; a **trailing-comma JSON**
the device tolerates; and a "blank slate" preset that actually shipped a full effect
chain. Lesson: **derive names/status from content and validate, never trust the filename.**
[→ data-quality.md](data-quality.md)

## Tooling / methodology

- **Name and classify from content, then validate.** `tools/podgo.py` derives taxonomy,
  free-block count, and the one canonical name (filename = `id` = `meta.name`) from the
  JSON; `validate_presets.py` fails on any mismatch. This auto-fixed the mislabeled files
  above — including several old names that misreported their free-block count.
  [→ data-quality.md](data-quality.md)
- **Block-coverage matching is deceptively hard.** Naive substring matching of a display
  name inside an id gives both false positives (generic names like `Stereo` match 100+
  ids; `Weeper`→`sweeper`) and false negatives (reordered names like `10 Band Graphic`
  vs id `Graphic10Band`). The fix: **token-subset matching** (split acronyms/camelCase/
  digits, drop stopwords, require the name's token set ⊆ an id's) plus a small curated
  **`name_overrides` crosswalk** for the genuinely ambiguous cases.
  [→ naming-and-registry.md](../presets/naming-and-registry.md)
- **The model-coverage gap is closed by POD Go Edit's catalog.** Preset-mining
  (`data-presets/` dumps) left amps/cabs/wah/vol under-captured and was slow. POD Go Edit
  ships the full authoritative catalog (**574 models** with DSP loads + params +
  firmware provenance) as JSON, so "which models exist" no longer needs harvesting; the
  gap is closed by definition. [→ reference/block-models.md](../reference/block-models.md)
