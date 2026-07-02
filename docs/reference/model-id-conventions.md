# Internal `@model` ID Conventions

How POD Go names blocks internally in the `.pgp` JSON. Grounded in the 319 ids we've
harvested ([registry/blocks.json](../../registry/blocks.json)). The internal id is
**not** the on-device display name — see [block-models.md](block-models.md) and the
`name_overrides` in [reference-models.json](../../registry/reference-models.json) for
the crosswalk and divergences.

## Prefixes

| Prefix | Count* | Meaning |
| --- | ---: | --- |
| `HD2_` | 289 | The native HX (Helix Gen-2) model set — the vast majority |
| `VIC_` | 10 | A newer batch (e.g. `VIC_ReverbShimmerStereo`, `VIC_DelayGlitchStereo`, `VIC_DynRoomStereo`, `VIC_PitchBoctaverMono`) — later-firmware additions |
| `Victoria_` | 1 | Full-word variant of the same (`Victoria_EuclideanDelayStereo`) |
| `L6…` / `L6SPB_` | 3 | Line 6 legacy (`L6BubbleEcho`, `L6PhazeEko`, `L6SPB_AcousGtrSimStereo`) |
| *(none)* | 18 | Bare legacy names, mostly synth/filter/mod: `Sweeper`, `TapeEater`, `RezSynth`, `SynthLead`, `SeismicSynth`, `KillerZ`, `SampleAndHold`, `Warble_Matic`, `Line6BronzeMaster`, … |

\* in our current harvest; will grow as more data-presets are added.

**Takeaway:** most ids are `HD2_<Name>`, but prefixing is inconsistent — some models
have `VIC_`, some `L6`, and a chunk of legacy models have no prefix at all. Don't assume
`HD2_`; the id must be captured from a real preset, never guessed.

## Legacy stompbox family codes

Embedded in the id (usually right after `HD2_`), these mark the classic Line 6 "4"
modeler families:

| Code | Family | Example |
| --- | --- | --- |
| `DL4` | Delay | `HD2_DL4TapeEchoStereo` |
| `DM4` | Distortion | `HD2_DM4FacialFuzz` |
| `MM4` | Modulation | `HD2_MM4BarberpolePhaser` |
| `FM4` | Filter (& some synth) | `HD2_FM4ObiWah` |
| `M13` / `M1380A` | M-series | `HD2_M13ACFlanger` |

## Mono vs. Stereo suffix

Ids often end in `Mono` or `Stereo`, and it lines up with POD Go's signal-path width:

- **Mono:** Distortion, Dynamics, Pitch/Synth (e.g. `…CompMono`, `…FuzzMono`, `PitchDualPitchMono`)
- **Stereo:** EQ, Modulation, Delay, Reverb, Filter (e.g. `…ParametricStereo`, `ReverbHallStereo`)
- **No suffix:** Amp and Cab (they use their own naming, below), plus many bare legacy models

## Built-in block id prefixes (how the tools detect role)

`tools/podgo.py` classifies the seven built-in blocks by id prefix:

| Role | Prefix |
| --- | --- |
| Volume | `HD2_VolPan…` |
| Wah | `HD2_Wah…` |
| FX Loop | `HD2_FXLoop…` |
| EQ | `HD2_EQ…` |
| Looper | `HD2_Looper…` |
| Amp | `HD2_Amp…` |
| Cab | `HD2_Cab…` |

Everything else is a free-block effect.

## Two special cases worth knowing

- **`EQ_STATIC` vs `EQ`.** The fixed **preset-EQ block** uses `HD2_EQ_STATIC_*`
  (only `Parametric` and `Simple3Band` seen). The **free-block EQ effects** use
  `HD2_EQ*` without `STATIC` (`EQGraphic10BandStereo`, `EQLowCutHighCutStereo`,
  `EQSimpleTiltStereo`, …). The same models (Parametric, Simple 3 Band) exist in
  **both** forms — so a preset can carry an EQ as the mandatory block *and* as a
  free effect, and only the `_STATIC_` one is the dedicated slot.
- **Amp / Cab naming.** Amps are `HD2_Amp<Model>` (`HD2_AmpDelSol300`,
  `HD2_AmpUSDoubleNrm`). Cabs come as `HD2_Cab<spec>` and `HD2_CabMicIr_<spec>`
  (`HD2_Cab2x12DoubleC12N`, `HD2_CabMicIr_2x15Brute`) — `MicIr` = the mic'd-IR engine.

## Capturing an id

The only reliable way to learn a block's id is to dump a preset that uses it (that's
what `data-presets/` is for) and run `python3 tools/refresh.py`. The
[coverage worklist](data-coverage.md) tracks which ids we still need.
