# data-presets/

**Reference** presets — not the published collection (that's [`presets/`](../presets)).
Two kinds live here:

## 1. Stock dumps (flat, this folder)

The `*.pgp` files at this level are stock POD Go preset dumps kept purely for **data
retrieval** — harvesting the exact internal `@model` id strings for every factory block,
organized by the device's category/page layout (e.g. "Reverb Page 1a", "Dist Page 5").

Internal `@model` ids are never published by Line 6; the only way to learn one is to dump a
preset that uses the block. `tools/harvest_blocks.py` (via `tools/refresh.py`) reads these
flat files into [`registry/blocks.json`](../registry/blocks.json), and
[`docs/reference/data-coverage.md`](../docs/reference/data-coverage.md) tracks which ids are
still missing. Background:
[`docs/reference/model-id-conventions.md`](../docs/reference/model-id-conventions.md).

## 2. Demonstrations ([`demonstrations/`](demonstrations/README.md))

Presets that **prove** a documented POD Go fact — the evidence layer for the knowledge
base. Where possible each is the known-good
[base preset](../original/New-Preset-2_50_0.pgp) plus one minimal, byte-preserving edit.
Catalog + "what to observe":
[`demonstrations/manifest.json`](demonstrations/manifest.json); status per fact:
[`docs/presets/business-rules.md`](../docs/presets/business-rules.md).

> The harvest glob is **flat** (`data-presets/*.pgp`), so the `demonstrations/` subfolder is
> intentionally **not** harvested into `blocks.json` — it's tracked by its own manifest.

Related: [`docs/presets/pgp-schema.md`](../docs/presets/pgp-schema.md) (the `.pgp` schema).
