# Best Practices

The prescriptive do/don't for working on Pod Go presets and this repo. These are
the *rules to follow*; the *findings that justify them* are in
[lessons-learned.md](../knowledge/lessons-learned.md).

↩ [conventions index](README.md)

## Truth & verification

- **The hardware is the only authority on viability.** A preset importing or
  parsing cleanly says nothing about whether it works. Never upgrade "imports
  cleanly" to "works" — only a test on a unit does that.
- **Record confidence honestly.** Slot every hardware claim into the right tier of
  the [verified.md](../knowledge/verified.md) ledger: ✅ confirmed on a unit · 🔬 inferred
  from the tested library · 📖 from Line 6 sources · ⏳ pending. Don't let an
  inference read as a confirmed fact.
- **When a source disagrees with the unit, the unit wins.** Record the correction
  in [`registry/reference-models.json`](../../registry/reference-models.json) and
  re-run `tools/coverage.py` (the dual-cab correction is the cautionary tale — see
  [block-models.md](../reference/block-models.md)).

## Deriving, not trusting

- **Derive names and status from content, then validate.** Let `tools/podgo.py`
  compute taxonomy, free-block count, and canonical name from the JSON; run
  [`tools/validate_presets.py`](../../tools/validate_presets.py) and require 0
  errors. Filenames have lied before ([data-quality.md](../knowledge/data-quality.md)).
- **Capture `@model` ids from real dumps — never guess them.** Prefixing is
  inconsistent (`HD2_`, `VIC_`, bare legacy names). Dump a preset that uses the
  block and run `tools/refresh.py`. See
  [model-id-conventions.md](../reference/model-id-conventions.md).

## Editing presets safely

- **Don't reformat `.pgp` files;** preserve Pod Go's exact bytes (the `\/`
  escapes, tolerated trailing commas). See [pgp-format.md](../presets/pgp-format.md).
- **Ship a blank slate:** strip loaded effects, footswitch assignments, and
  snapshots (`snapshot0–3`, `footswitch`, `controllers` are safe to delete — Pod
  Go rebuilds them).
- **Keep at least one of EQ or Looper** (the mandatory block) and respect the
  7-assignable ceiling — see [blocks-and-constraints.md](../presets/blocks-and-constraints.md).

## Keeping the repo consistent (run the tools)

Standard loops (from the repo root):

- **Added stock `data-presets/` dumps →** `python3 tools/refresh.py` (harvest +
  coverage).
- **Added/changed a preset or the registry →** `python3 tools/gen_matrix.py`
  (refresh `presets.csv` + the README list), then
  `python3 tools/validate_presets.py` (must pass).
- Full command reference: [naming-and-registry.md](../presets/naming-and-registry.md).

## Keeping knowledge current

- **When you learn something, document it** — invoke the `document` skill so it
  lands in the right doc, gets indexed, and both indexes stay in sync. Don't let
  findings live only in a commit message or your memory.
- **Prefer editing an existing doc** over adding a new one; link instead of
  duplicating (single source of truth).
- **Retire resolved unknowns:** move a solved ⏳-pending item or a fixed quirk to
  its proper home so the docs don't accumulate stale caveats.
