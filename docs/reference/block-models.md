# POD Go Block / Model Reference

The authoritative list of every block POD Go can load, by category. Firmware
**v2.5x**. Full machine-readable name lists live in
[registry/reference-models.json](../../registry/reference-models.json); coverage
of which internal `@model` ids we've actually captured is in
[data-coverage.md](data-coverage.md).

↩ [reference index](README.md)

> Display names are the human labels shown on-device. The internal `@model` id
> (e.g. `HD2_AmpDelSol300`) is **not** published by Line 6 — the only way to learn
> it is to dump a preset that uses the block. That is the purpose of
> [`data-presets/`](../../data-presets) and the coverage worklist.

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
