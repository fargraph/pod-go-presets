# Project Conventions

How the repository is organized, handled, and committed. Firmware target
throughout: **Pod Go v2.50**.

↩ [conventions index](README.md)

## The nested-repo layout (read this first)

There are **two** directories that look like "the project":

```
Pod Go Presets/            ← working root. NOT a git repo. Holds Claude's CLAUDE.md.
└── pod-go-presets/        ← THE git repo → github.com/fargraph/pod-go-presets
    ├── README.md          user-facing overview + preset list (source of truth)
    ├── docs/              this developer knowledge base
    ├── presets/           the published presets, by removal taxonomy
    ├── data-presets/      stock-preset dumps used only to harvest @model ids
    ├── registry/          machine-readable source of truth (JSON + CSV)
    ├── tools/             Python scripts (harvest, coverage, validate, matrix)
    ├── original/          untouched factory preset(s) for diffing
    └── LICENSE.md         MIT — Elevate Life Media LLC
```

- **Run all `git` commands from inside `pod-go-presets/`,** not the working root.
- `CLAUDE.md` deliberately lives *above* the repo so it is never committed.

## `.pgp` file handling

`.pgp` files are JSON but are treated as **opaque, byte-sensitive** artifacts:

- **Never reformat them.** They are Prettier-ignored (`.prettierignore` = `*.pgp`).
  Pod Go escapes `/` as `\/` and tolerates trailing commas a strict serializer
  would "fix" — reformatting produces meaningless, noisy diffs. Preserve the exact
  bytes. Details: [pgp-format.md](../presets/pgp-format.md).
- **Don't trust filenames — derive from content.** Names and status are computed
  from the JSON by `tools/podgo.py`; the filename mirrors the content, never the
  reverse. See [naming-and-registry.md](../presets/naming-and-registry.md) and the
  defects this caught in [data-quality.md](../knowledge/data-quality.md).
- **Published presets are a blank slate:** no loaded effects in free blocks, no
  footswitch assignments, no snapshots.

## Preset organization

- Presets live in `presets/<taxonomy>/` where taxonomy is one of
  `with-amp-cab`, `no-cab`, `no-amp`, `no-amp-and-cab` (which of Amp/Cab were
  removed — the validity-critical axis, **not** working/broken status). See
  [blocks-and-constraints.md](../presets/blocks-and-constraints.md).
- **Working/broken status is authoritative in
  [`registry/combinations.json`](../../registry/combinations.json)** and mirrored
  by a `_broken` filename suffix.
- The full add-a-preset checklist and tool commands are in
  [naming-and-registry.md](../presets/naming-and-registry.md).

## Git & commits

- **Commit only when the user asks,** and only from inside `pod-go-presets/`.
- Commit messages: **short, lowercase** (see `git log` — e.g. `update readme`,
  `formatted`, `cleanup readme`).
- The user-facing README uses ✅/❌ tables for the combination matrix; keep it and
  `registry/presets.csv` in sync via `tools/gen_matrix.py`.
- After any preset/registry edit, `tools/validate_presets.py` must pass.

## Licensing & attribution

- **MIT License**, © Elevate Life Media LLC (see
  [`LICENSE.md`](../../LICENSE.md)).
- If you redistribute presets based on this collection, include a link back to
  the repo (the author's only request).

## Firmware

Everything here targets **Pod Go v2.50**. When behavior may be
version-specific, say so and record the firmware — and remember that **the
hardware is the final authority** (see [best-practices.md](best-practices.md) and
the [verified.md](../knowledge/verified.md) ledger).
