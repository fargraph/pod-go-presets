# Lessons Learned & Data Gathered

A digest of the non-obvious things discovered building this knowledge base. Each
points to the doc with the full detail — this page is the "what surprised us" index.

## POD Go behavior (hardware facts)

- **Free blocks = `blockN` slots − built-in blocks present** (base 10 slots). The
  intuitive "7 − Vol − Wah − FX Loop" rule is **wrong** — it only coincidentally works
  for presets that keep EQ+Amp+Cab. [→ blocks-and-constraints.md](blocks-and-constraints.md)
- **Removing the Amp breaks presets; removing only the Cab is fine.** Every working
  no-cab preset works; every no-amp / no-amp-and-cab preset in the library is broken.
  Removing **both** Amp and Cab visibly **collapses the chain to 8–9 slots** (vs the
  healthy 10) — strong evidence the chain destabilizes. [→ blocks-and-constraints.md](blocks-and-constraints.md)
- **The assignable ceiling is 7, and Vol/Wah/FX Loop count against it.** Keeping Volume
  or the FX Loop while having 7 free blocks yields a *phantom* slot the UI shows but
  can't assign — the preset reads as broken. Genuine 7 free needs removing **both**.
- **Cab is single-cab only** — POD Go does **not** have Helix's dual-cab mode. (The
  research draft claimed otherwise; the unit corrected it.) [→ reference/block-models.md](reference/block-models.md)
- **Hardware is the only authority on viability.** Parsing/importing cleanly means
  nothing about whether a combination works. Published research and even Line 6's own
  marketing counts can be wrong; the unit wins. [→ resources.md](resources.md)

## Preset schema

- **`meta.name` caps at 16 chars**, import silently truncates longer, and the on-disk
  `.pgp` filename is decoupled from the stored name (import reads `meta.name`, not the
  filename). Symbols/spaces are allowed; `/` is stored escaped as `\/`.
  [→ naming-and-registry.md](naming-and-registry.md), [pgp-format.md](pgp-format.md)
- **`@model` ids are not display names, and prefixing is inconsistent** (`HD2_` for most,
  but also `VIC_`, `L6…`, and 18 bare-name legacy models). Ids can only be captured by
  dumping a preset — never guessed. [→ reference/model-id-conventions.md](reference/model-id-conventions.md)
- **`EQ_STATIC_*` = the fixed preset-EQ block; `EQ*` (no STATIC) = a free-block EQ
  effect.** The same EQ models exist in both forms. [→ reference/model-id-conventions.md](reference/model-id-conventions.md)
- **Some keys are safe to delete — POD Go rebuilds them** on import/first-assignment:
  `snapshot0–3`, `footswitch`, `controllers`. [→ pgp-format.md](pgp-format.md)
- **`.pgp` is JSON but hand-edits drift from POD Go's serialization:** it tolerates
  trailing commas (strict parsers don't) and escapes `/` as `\/`. Don't reformat.
  [→ pgp-format.md](pgp-format.md)

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
  free-block count, and canonical name from the JSON; `validate_presets.py` fails on any
  mismatch. This auto-fixed the mislabeled files above.
- **Block-coverage matching is deceptively hard.** Naive substring matching of a display
  name inside an id gives both false positives (generic names like `Stereo` match 100+
  ids; `Weeper`→`sweeper`) and false negatives (reordered names like `10 Band Graphic`
  vs id `Graphic10Band`). The fix: **token-subset matching** (split acronyms/camelCase/
  digits, drop stopwords, require the name's token set ⊆ an id's) plus a small curated
  **`name_overrides` crosswalk** for the genuinely ambiguous cases.
  [→ naming-and-registry.md](naming-and-registry.md)
- **Effects were nearly complete from the start; amps/cabs/wah/vol were the gaps.** The
  stock `data-presets/` dumps are effect-category pages, so they captured ~all effects
  but almost no amps/cabs. Filling those means dumping amp/cab presets and re-running
  `tools/refresh.py`. [→ reference/data-coverage.md](reference/data-coverage.md)
