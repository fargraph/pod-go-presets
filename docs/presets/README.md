# Presets — structure, constraints & naming

How a Pod Go preset is built: the `.pgp` file format, the block economy and the
rules that decide which combinations are possible, and how presets are named and
tracked in the registry. Start here to understand and create presets.

↩ [Docs home](../README.md)

## Files in this folder

- [pgp-format.md](pgp-format.md) — the `.pgp` JSON structure (top-level shape, the
  `data.tone.dsp0` signal chain, block fields), how to inspect a preset, the safe-
  to-delete keys, and the serialization gotchas (`\/` escapes, trailing commas,
  never reformat).
- [blocks-and-constraints.md](blocks-and-constraints.md) — the conceptual core:
  free vs. built-in blocks, the **free-block rule** (`slots − built-ins`), the
  7-assignable ceiling, the removal taxonomy, and the mandatory EQ/Looper block.
- [naming-and-registry.md](naming-and-registry.md) — the content-derived naming
  convention, hardware name/filename limits, the `registry/*` files, the `tools/`
  commands, and the add-a-preset checklist.

## Related

- What the block ids mean and the catalog of models:
  [../reference/](../reference/README.md).
- Defects these rules caught in the real library:
  [../knowledge/data-quality.md](../knowledge/data-quality.md).
- Conventions for editing presets safely:
  [../conventions/best-practices.md](../conventions/best-practices.md).
