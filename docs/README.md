# POD Go Presets — Documentation

Deep-dive knowledge base for modifying POD Go presets. The root
[README](../README.md) is the user-facing overview; these are the details.

## Contents

| Doc | What's in it |
| --- | --- |
| [blocks-and-constraints.md](blocks-and-constraints.md) | How the block chain works; free vs built-in blocks; the **free-block rule**; the 7-block ceiling; why removing Amp/Cab breaks; removal taxonomy |
| [pgp-format.md](pgp-format.md) | The `.pgp` JSON structure; how to inspect a preset; editing conventions and gotchas |
| [naming-and-registry.md](naming-and-registry.md) | Preset naming convention; the `registry/` files; the `tools/`; how to add a preset |
| [reference/block-models.md](reference/block-models.md) | Authoritative POD Go model list by category; POD Go vs. Helix deltas; sources |
| [reference/data-coverage.md](reference/data-coverage.md) | **Gap worklist** — which block `@model` ids we've captured vs still need (generated) |
| [data-quality.md](data-quality.md) | Discrepancies found in the preset library and their fixes |
| [troubleshooting.md](troubleshooting.md) | On-device quirks: stuck free blocks, footswitch sync, assignments |

## Quick facts

- Target firmware: **POD Go v2.50**.
- Free blocks = **`blockN` slots − built-in blocks** (base 10 slots).
- Genuine **7 free** blocks require removing **both** Volume and FX Loop.
- Keep the **Amp** (removing it tends to break); removing only the **Cab** is fine.
- Cab block is **single-cab only** — no dual-cab mode.
- Every preset needs at least one of **EQ or Looper**.
