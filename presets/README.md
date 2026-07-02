# presets/

The published, "jailbroken" presets, grouped into subfolders by **removal
taxonomy** — which of Amp/Cab each preset removes (the validity-critical axis).
The folder does **not** encode working/broken status; that lives in
[`registry/combinations.json`](../registry/combinations.json) and is mirrored by a
`_broken` filename suffix.

| Folder | Amp | Cab | Observed |
| --- | :-: | :-: | --- |
| `with-amp-cab/` | ✅ | ✅ | Safe |
| `no-cab/` | ✅ | ❌ | Works |
| `no-amp/` | ❌ | ✅ | Suspect — verify on hardware |
| `no-amp-and-cab/` | ❌ | ❌ | Breaks (all known examples broken) |

Presets are named by **what they contain** (`<free>bl_<built-ins>[_broken]`), a
name derived from the file's actual contents. See
[`docs/presets/blocks-and-constraints.md`](../docs/presets/blocks-and-constraints.md) for the
block economy and [`docs/presets/naming-and-registry.md`](../docs/presets/naming-and-registry.md)
for naming and the add-a-preset checklist. User-facing download list:
[the repo README](../README.md#presets).
