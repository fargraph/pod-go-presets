# POD Go Presets

I created these presets for myself, but I'm willing to share. I have not found a
reliable source of information about modifying POD Go presets — most sources have a
few jailbroken files to download, but nothing comprehensive. This repo aims to be
that: a catalog of every viable combination of removable built-in blocks, plus a
[knowledge base](docs/) documenting how POD Go presets actually work.

If you base your presets off this collection, I just ask that you include a link to
this repository if you redistribute them.

If you'd like to throw a little support my way, you can buy me a coffee!

<a href="https://www.buymeacoffee.com/cliftoneatf" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

Found a problem with a preset, or have more info on modifying the JSON? Please open
an issue or PR. For issues, include as much detail as you can — screenshots/photos/
video, a clear description, and your firmware version.

## POD Go version

All presets were made on **POD Go v2.50**. No guarantees about backward compatibility.

## How it's organized

```
presets/           the presets, grouped by which built-in blocks were removed
  with-amp-cab/    no-cab/    no-amp/    no-amp-and-cab/
docs/              knowledge base — start at docs/README.md
registry/          machine-readable data (combinations, block ids, model reference)
data-presets/      stock preset dumps, used only to harvest block ids
tools/             small Python scripts (classify / validate / harvest / coverage)
```

Presets are named by **what they contain**, not what was removed — e.g.
`7bl_eq_amp_cab` = 7 free blocks + EQ + Amp + Cab. Details:
[docs/naming-and-registry.md](docs/naming-and-registry.md).

## To-do

Preset viability can only be confirmed on a real POD Go unit — every item below needs a
**hardware test** before it's done. Background: [docs/data-quality.md](docs/data-quality.md).

- [ ] **`5bl_fx_lpr_amp_cab`** is missing slot `block5`, so it exposes only 5 free
  blocks instead of the intended 6. Re-add `"block5": { "@position": 5 }` to `dsp0`,
  rename back to `6bl_fx_lpr_amp_cab`, and hardware-test.
- [ ] **`7bl_eq_amp`** contains neither an FX Loop nor a Looper despite its old name
  (`7bl_Eq_Fx_loopr_Amp`). Confirm the intent — add them back or keep as EQ+Amp — then
  hardware-test.
- [ ] **`5bl_vol_fx_eq_lpr_cab`** ships with a loaded effect chain (not a blank slate)
  and is a no-amp config. Decide whether to strip it to a blank slate or keep it as a
  demo, then hardware-test.

## Documentation

The [docs/](docs/README.md) folder is the deep dive. Highlights:

- **[Blocks & constraints](docs/blocks-and-constraints.md)** — how the chain works,
  the free-block rule, why removing Amp/Cab breaks things.
- **[The `.pgp` format](docs/pgp-format.md)** — file structure and safe edits.
- **[Block/model reference](docs/reference/block-models.md)** — every POD Go model
  by category, and the [data-coverage worklist](docs/reference/data-coverage.md).
- **[Troubleshooting](docs/troubleshooting.md)** — on-device quirks.

## Preset combinations

**The full, filterable list of every preset — working and broken together — is
[registry/presets.csv](registry/presets.csv).** GitHub renders it as a sortable,
searchable table: click a column header to sort, or use the search box to filter
(type e.g. `amp`, `no-amp`, `broken`, or a file name). Each row has the free-block
count, a `1`/`0` flag per built-in block (vol / wah / fx / eq / lpr / amp / cab),
the working/broken **status**, taxonomy, slot count, file link, and notes — so you
can pick the block combination you want and see whether it's viable in the same row.

It's generated from [registry/combinations.json](registry/combinations.json) by
`python3 tools/gen_matrix.py`. Currently **13 working, 10 broken** across
with-amp-cab / no-cab / no-amp / no-amp-and-cab; see
[docs/data-quality.md](docs/data-quality.md) for why the broken ones fail.

Free-block count = `blockN` slots − built-in blocks present (base 10 slots). Genuine
**7 free** blocks require removing **both** Volume and FX Loop. Every preset keeps at
least one of **EQ or Looper**.

## Notes on choosing a preset

- Start with the pedals you need. **Volume, Wah, and FX Loop can't go in a free
  block**, so they must be chosen up front (and each costs a free block).
- Keep at least one mandatory block — **Looper or EQ**. The Looper is a unique
  tone-tweaking/problem-solving tool; EQ is often replaceable via an effect/amp tone
  stack or the Global EQ.
- Presets ship as a **blank slate**: no footswitch assignments or snapshots, so you
  start clean. (One preset currently breaks that intent — see data-quality.md.)
- To ride volume without a Volume block, assign EXP 2 to a level parameter — details
  in [docs/blocks-and-constraints.md](docs/blocks-and-constraints.md).

For the full mechanics (the free-block rule, the 7-block ceiling, the `@type` table,
removing Amp/Cab), see [docs/blocks-and-constraints.md](docs/blocks-and-constraints.md)
and [docs/pgp-format.md](docs/pgp-format.md).
