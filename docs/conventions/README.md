# Conventions — how to work on this project

The rules and habits that keep this repo consistent: how the code is written, how
the repo is organized and committed, the working practices that avoid the traps
we've hit, and how this documentation maintains itself.

↩ [Docs home](../README.md)

## Files in this folder

- [code-conventions.md](code-conventions.md) — Python (`tools/`) and JSON
  (`registry/`) style: stdlib-only, the shared `podgo.py` library, schema tags,
  read-only vs. generator scripts.
- [project-conventions.md](project-conventions.md) — the nested-repo layout,
  `.pgp` file handling, preset organization, git/commit rules, and licensing.
- [best-practices.md](best-practices.md) — the prescriptive do/don't workflow:
  hardware-is-truth, derive-from-content-then-validate, keep-a-blank-slate, and
  more.
- [documentation.md](documentation.md) — the rules this `docs/` tree follows for
  itself (the canonical structure map, indexing invariants, sizing, and the
  maintenance policy the `document` skill enforces).

## Related

- Editing/serialization specifics for `.pgp` files: [pgp-format.md](../presets/pgp-format.md).
- The add-a-preset checklist and tool commands: [naming-and-registry.md](../presets/naming-and-registry.md).
- Why these practices exist (the findings behind them): [lessons-learned.md](../knowledge/lessons-learned.md).
