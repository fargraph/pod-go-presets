# The `.pgp` JSON Schema

The formal, machine-readable structure of a POD Go preset, as a JSON Schema. This is the
field-by-field companion to [`registry/pgp.schema.json`](../../registry/pgp.schema.json);
for how to *inspect and safely edit* a preset, see [pgp-format.md](pgp-format.md).

↩ [presets index](README.md)

## What it is (and isn't)

[`registry/pgp.schema.json`](../../registry/pgp.schema.json) is a **JSON Schema (draft
2020-12)** that describes a well-formed `.pgp` (firmware v2.50, `schema: "L6Preset"`,
`version: 6`). It is **advisory** — deliberately *not* wired into the tools — because two
real-world quirks live outside JSON Schema's reach:

1. **Trailing commas.** POD Go tolerates a trailing comma that makes the file invalid
   JSON. Recover it first (`tools/podgo.py` `load_pgp` does) before validating.
2. **Escaped slashes.** A `/` in a string is stored escaped as `\/` — a valid, optional
   JSON escape. The schema validates the decoded value; byte-fidelity is a separate rule
   ([`no-reformat-pgp`](business-rules.md)).

The schema is built to **validate the known-good base**
[`original/New-Preset-2_50_0.pgp`](../../original/New-Preset-2_50_0.pgp) and the entire
[`presets/`](../../presets) library (24 files, 0 failures). The over-length-name
demonstrator is the one file it *rejects* — on purpose (see below).

## Top-level envelope

The real top level is wider than the chain-focused view in [pgp-format.md](pgp-format.md):

```
{
  "data":    { … },          // meta, device, tone, device_version
  "meta":    { "original", "pbn", "premium" },   // top-level, NOT the same as data.meta
  "schema":  "L6Preset",
  "version": 6
}
```

| Path | Type | Notes |
| --- | --- | --- |
| `schema` | const `"L6Preset"` | preset format tag |
| `version` | integer | `6` on v2.50 |
| `meta` (top level) | object | `original` / `pbn` / `premium` flags — distinct from `data.meta` |
| `data.meta` | object | **`name` (`maxLength` 16)**, `application`, `build_sha`, `modifieddate`, `appversion` |
| `data.device` / `data.device_version` | integer | device id / firmware id |
| `data.tone` | object | the tone — see below |

## `data.tone`

Requires `global` and `dsp0`; the rest are optional and rebuilt by the device if absent:

- `global` — `@model` const `@global_params`, plus `@cursor_group`, `@pedalstate`,
  `@current_snapshot`, `@tempo`.
- `dsp0` — **the signal chain** (below).
- `dsp1` — empty object (unused on POD Go).
- `snapshot0`–`snapshot3` — `@valid`, `blocks.dsp0.{block0..9: bool}`, `@name`, `@tempo`,
  `@pedalstate`, `@ledcolor`, optional `controllers`.
- `footswitch` / `controller` — present only once assignments exist; `@controller` uses
  `3`–`8` for parameter assignments. See [troubleshooting.md](../knowledge/troubleshooting.md).

## `data.tone.dsp0` — the chain

Requires `input` (`@model` const `P34_AppDSPFlowInput`) and `output`
(`P34_AppDSPFlowOutput`), plus `block0`–`block9`:

- **Free / empty block** — exactly `{ "@position": N }` (`@position` 0–9).
- **Occupied block** — adds `@model` (+ `@type`, `@enabled`, `@no_snapshot_bypass`, and
  model-specific params). Built-in role is read from the `@model` prefix
  (`HD2_VolPan`/`Wah`/`FXLoop`/`EQ_`/`Looper`/`Amp`/`Cab`); everything else is a
  free-block effect. Param objects are open (`additionalProperties: true`).

The block-economy rules that decide which combinations are *valid* (not just well-formed)
are not expressible here — they live in [business-rules.md](business-rules.md) and
[blocks-and-constraints.md](blocks-and-constraints.md).

## Demonstrated by

| Fact | Preset |
| --- | --- |
| The full well-formed envelope, empty-block shape, `@type` values, assignment sections | [`original/New-Preset-2_50_0.pgp`](../../original/New-Preset-2_50_0.pgp) |
| `EQ_STATIC_*` (built-in) vs free `HD2_EQ*` effects coexisting | [`data-presets/EQ Page 1.pgp`](../../data-presets/EQ%20Page%201.pgp) |
| `/` stored as `\/` in `meta.name` | [`data-presets/demonstrations/name-slash-escape.pgp`](../../data-presets/demonstrations/name-slash-escape.pgp) |
| `meta.name` `maxLength` 16 (schema **rejects** the over-length name) | [`data-presets/demonstrations/name-overlength.pgp`](../../data-presets/demonstrations/name-overlength.pgp) |

Full catalog: [`data-presets/demonstrations/manifest.json`](../../data-presets/demonstrations/manifest.json).

## Validating (optional)

The schema is not required to work on the repo, but you can check a preset against it with
any draft-2020-12 validator (e.g. Python `jsonschema`), recovering trailing commas first:

```python
import json, jsonschema, tools.podgo as podgo   # from repo root
schema = json.load(open("registry/pgp.schema.json"))
data, _ = podgo.load_pgp("original/New-Preset-2_50_0.pgp")
jsonschema.Draft202012Validator(schema).validate(data)   # passes
```
