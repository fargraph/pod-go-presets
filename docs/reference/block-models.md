# POD Go Block / Model Reference

The authoritative list of every block POD Go can load, by category. Firmware
**v2.5x**. Full machine-readable name lists live in
[registry/reference-models.json](../../registry/reference-models.json); coverage
of which internal `@model` ids we've actually captured is in
[data-coverage.md](data-coverage.md).

↩ [reference index](README.md)

> Display names are the human labels shown on-device. Every block's internal `@model`
> id, category, DSP `load`, and parameter schema ship in **POD Go Edit's bundled
> catalog** — see [Authoritative source](#authoritative-source-pod-go-edit-catalog)
> below. (Ids were historically reverse-engineered by dumping presets into
> [`data-presets/`](../../data-presets); the catalog supersedes that as the source of
> truth for *which models exist*.)

## Authoritative source: POD Go Edit catalog

POD Go Edit ships the complete, authoritative model catalog as JSON in its app bundle
(`/Applications/Line6/POD Go Edit.app/Contents/Resources/`): 18 per-category
`*.models` files plus `PGModelCatalog.json`. Together they define **574 model
definitions**, each carrying its `symbolicID` (= the `@model` id), display `name`,
category, **DSP `load`**, full **`params`** schema, and — via a `devices` field —
**which firmware version added it** (428 base + 146 added across updates).

- [`tools/extract_podgo_catalog.py`](../../tools/extract_podgo_catalog.py) snapshots it
  into a versioned, git-diffable file at
  [`registry/model-catalog/`](../../registry/model-catalog/)`podgo-edit-<version>.json`
  (current: **editor v2.50**). Re-run on a new POD Go Edit release → `git diff` shows
  exactly what Line 6 changed.
- [`tools/podgo_models.py`](../../tools/podgo_models.py) reads that snapshot, keyed by
  `@model`, with no dependency on the app being installed.

**Structure of the 574:** 271 are in the general **FX-block picker**; amps (106),
preamps (108), cabs (41) and cab-mic IRs (46) use **dedicated block pickers** and aren't
in `PGModelCatalog.json`. The `devices` field confirms all 574 are genuine POD Go models
(POD Go + POD Go Wireless), not a Helix superset.

This supersedes preset-mining for *knowing which models exist* — that coverage gap is
closed by definition. The hand-curated category counts below predate the catalog and are
being reconciled against it; where they disagree, **the catalog wins**.

## Chain architecture

Fixed order: Input+Gate → **Wah** → **Volume** → **Amp/Preamp** → **Cab/IR** →
**FX Loop** → **Preset EQ** → Output, plus **free effect blocks**. Distortion,
Dynamics and Pitch/Synth are **mono**; EQ, Modulation, Delay, Reverb, Filter are
**stereo**.

## Category summary

| Category | Count (approx) | Notes |
| --- | ---: | --- |
| Amp — guitar | 89 | Each also selectable as a Preamp |
| Amp — bass | 17 | |
| Preamp | 1 standalone | `Studio Tube Pre`; plus every amp in preamp mode |
| Cab — guitar | 40 | **Single cab only** |
| Cab — bass | 11 | |
| Cab — mic | 16 | Chosen per-cab, not a separate block |
| Dynamics | 18 | 11 current + 7 legacy |
| Distortion | 55 | OD / fuzz / boost / bitcrush, incl. 17 legacy |
| EQ | 8 | Preset-EQ block offers a subset |
| Modulation | 55 | chorus/flanger/phaser/trem/rotary/vibe/ring, incl. legacy |
| Delay | 41 | incl. 16 legacy |
| Reverb | 23 | 11 current + 12 legacy |
| Pitch / Synth | 24 | **no polyphonic pitch models** |
| Filter | 15 | 4 current + 11 legacy |
| Wah | 11 | fixed block, EXP 1 |
| Volume / Pan | 4 | Volume Pedal, Gain, Pan, Stereo Width |
| FX Loop | 1 | single fixed send/return block |

See the JSON for the full itemized name lists in each category.

## POD Go vs. Helix (important deltas)

- **Cab block is single-cab only — POD Go does NOT support dual cabs.** (Helix
  does; the initial research draft claimed POD Go had single/dual modes and that
  was **incorrect** — corrected by the project owner.)
- **No polyphonic pitch** (Poly Pitch/Wham/Capo, 12-String, Poly Sustain/Detune).
- **One fixed FX Loop block** instead of Helix's Send/Return category.
- Every amp is also a **Preamp**; the only standalone preamp is `Studio Tube Pre`.
- **Every amp carries a `cablink`** in the catalog — a matched default cab
  (`HD2_AmpUSDoubleNrm → HD2_Cab2x12DoubleC12N`, all 106 amps). This is the vestige of Helix's
  **Amp+Cab** paired block: POD Go keeps Amp (`@type=1`) and Cab (`@type=2`) as **separate**
  blocks but records each amp's factory-matched cab via `cablink`.
- May lack a few of the newest Helix delays/reverbs (e.g. Cosmos Echo) — unverified.

## Sources

Line 6 primary sources, firmware v2.50:

- [line6.com/podgo-models](https://line6.com/podgo-models/) — official interactive
  model gallery (most complete live list).
- **POD Go 2.50 Owner's Manual**, doc 40-00-0568 Rev G — verbatim per-category
  model tables incl. the "—Legacy Models—" sub-groups.
- POD Go 2.0 / 1.10 manuals; 1.40 release notes; [kb.line6.com POD Go FAQ](https://kb.line6.com/pod-go-faq).

## Caveats

- Per-category counts drift ±1–2 by firmware snapshot; for a byte-exact list read
  the names directly off a v2.5x unit or POD Go Edit.
- Any category count here that disagrees with what you see on hardware: **hardware
  wins** — update the JSON and note it, as with the dual-cab correction.
