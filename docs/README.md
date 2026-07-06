# POD Go Presets — Documentation

Deep-dive knowledge base for modifying POD Go presets. The root
[README](../README.md) is the user-facing overview (and the source of truth for
the published presets and combination matrix); these are the developer details.

> Firmware target: **POD Go v2.50**. Behavior on other firmware is unverified,
> and the **hardware is always the final authority** (see
> [knowledge/verified.md](knowledge/verified.md)).

## Documentation map

Every doc lives under one of four folders, each with its own index. Nothing is
orphaned — you can reach any page from here.

### 🎛️ [presets/](presets/README.md) — how presets are structured, constrained & named
The `.pgp` file format, the block economy and its constraints, and the naming +
registry conventions. Start here to understand what a preset *is* and how to
build one.

- [presets/pgp-format.md](presets/pgp-format.md) — the `.pgp` JSON structure; how to inspect a preset; editing conventions and serialization gotchas
- [presets/pgp-schema.md](presets/pgp-schema.md) — the **formal JSON Schema** (`registry/pgp.schema.json`, draft 2020-12): the field-by-field envelope, built to validate the base preset
- [presets/blocks-and-constraints.md](presets/blocks-and-constraints.md) — the block chain; free vs built-in blocks; the **free-block rule**; the 7-block ceiling; why removing Amp/Cab breaks; removal taxonomy; the mandatory EQ/Looper block
- [presets/business-rules.md](presets/business-rules.md) — **semantic rules a schema can't express** (validity/naming/editing), each tied to a demonstrator preset with a verified/unverified status (`registry/rules.json`)
- [presets/naming-and-registry.md](presets/naming-and-registry.md) — preset naming; name/filename limits; the `registry/` files; the `tools/`; how to add a preset

### 🔬 [knowledge/](knowledge/README.md) — what hardware testing taught us
The living lab notebook: what's confirmed on a unit, the defects found in the
library, on-device quirks, and the digest of non-obvious findings.

- [knowledge/verified.md](knowledge/verified.md) — **hardware-verification ledger:** what's confirmed on a unit vs inferred vs assumed
- [knowledge/data-quality.md](knowledge/data-quality.md) — discrepancies found in the preset library and their fixes
- [knowledge/troubleshooting.md](knowledge/troubleshooting.md) — on-device quirks: stuck free blocks, footswitch sync, assignments
- [knowledge/lessons-learned.md](knowledge/lessons-learned.md) — digest of non-obvious findings about POD Go, the schema, and the tooling

### 📚 [reference/](reference/README.md) — model catalog, id syntax, generated data & links
The catalog side: what blocks exist, how their internal ids are structured, the
coverage worklist, and external sources.

- [reference/block-models.md](reference/block-models.md) — authoritative POD Go model list by category; POD Go vs. Helix deltas; sources
- [reference/model-id-conventions.md](reference/model-id-conventions.md) — how internal `@model` ids are structured (prefixes, legacy codes, mono/stereo, `EQ_STATIC`)
- [reference/data-coverage.md](reference/data-coverage.md) — **gap worklist:** which block `@model` ids we've captured vs still need (generated)
- [reference/resources.md](reference/resources.md) — external links: Line 6 manuals, model gallery, FAQ, community references

### 🧭 [conventions/](conventions/README.md) — how to work on this project
Code and project conventions, the prescriptive best-practices workflow, and the
rules this documentation follows for itself.

- [conventions/code-conventions.md](conventions/code-conventions.md) — Python (`tools/`) and JSON (`registry/`) style
- [conventions/project-conventions.md](conventions/project-conventions.md) — nested-repo layout; `.pgp` handling; preset organization; git/commit; licensing
- [conventions/best-practices.md](conventions/best-practices.md) — the do/don't workflow: hardware-is-truth, derive-from-content-then-validate, blank slate
- [conventions/documentation.md](conventions/documentation.md) — how this `docs/` tree is organized and maintained (the canonical map)

## Quick facts

- Target firmware: **POD Go v2.50**.
- Free blocks = **`blockN` slots − built-in blocks** (base 10 slots).
- Genuine **7 free** blocks require removing **both** Volume and FX Loop.
- Keep the **Amp** (removing it tends to break); removing only the **Cab** is fine.
- Cab block is **single-cab only** — no dual-cab mode.
- Every preset needs at least one of **EQ or Looper**.
- Knowledge carries a **verified/unverified** status ([verified.md](knowledge/verified.md)); facts are tied to **demonstrator presets** in [`data-presets/demonstrations/`](../data-presets/demonstrations/README.md). Everything is currently **unverified** pending joint hardware confirmation.

## Maintaining these docs

This tree is kept current by the **`document` skill** (invoke `/document`): it
records new knowledge in the right doc, keeps files reasonably sized and
cross-linked, ensures no file is orphaned, and syncs both this index and the
CLAUDE.md documentation index. The rules are written down in
[conventions/documentation.md](conventions/documentation.md).
