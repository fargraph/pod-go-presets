# data-presets/demonstrations/

Presets that **demonstrate** a documented POD Go fact — the evidence layer that ties the
knowledge base to something you can open, import, and see. This is distinct from the flat
dumps one level up (`data-presets/*.pgp`), whose only job is to harvest `@model` ids.

- **Source of truth:** [`manifest.json`](manifest.json) — one entry per fact, mapping a
  rule id (see [`registry/rules.json`](../../registry/rules.json)) to the preset that
  proves it, with what to observe and the file's provenance.
- **Anchored on the known-good base.** Where possible a demonstrator is the factory base
  preset [`original/New-Preset-2_50_0.pgp`](../../original/New-Preset-2_50_0.pgp) plus one
  minimal, byte-preserving edit, so its proof is a one-line diff. Facts a static file
  can't isolate point instead at a real export already in the repo.
- **These are NOT published presets.** The curated collection lives in
  [`presets/`](../../presets); nothing here asserts hardware viability of a block
  combination. Files here are reference/teaching artifacts and are **not** harvested into
  `registry/blocks.json` (the harvest glob is flat).

## Status

Every demonstration is **`unverified`** until the fact is jointly confirmed on hardware
with the project owner *and* has an accompanying preset here — see the verified/unverified
model in [`docs/knowledge/verified.md`](../../docs/knowledge/verified.md).

## New files here (base + one edit)

| File | Proves | Edit vs base |
| --- | --- | --- |
| `name-slash-escape.pgp` | `/` in `meta.name` is stored escaped as `\/` | name → `In\/Out` |
| `name-overlength.pgp` | `meta.name` 16-char cap; import truncates | name → `0123456789ABCDEFGHIJ` (20 ch) |

All other demonstrations reference real exports already in the repo (`original/`,
`data-presets/*.pgp`, `presets/`) — see `manifest.json`.

Authoritative docs: [pgp-schema.md](../../docs/presets/pgp-schema.md) ·
[business-rules.md](../../docs/presets/business-rules.md) ·
[naming-and-registry.md](../../docs/presets/naming-and-registry.md) ·
[pgp-format.md](../../docs/presets/pgp-format.md)
