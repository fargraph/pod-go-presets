# Internal `@model` ID Conventions

How POD Go names blocks internally in the `.pgp` JSON. Grounded in the 319 ids we've
harvested ([registry/blocks.json](../../registry/blocks.json)). The internal id is
**not** the on-device display name — see [block-models.md](block-models.md) and the
`name_overrides` in [reference-models.json](../../registry/reference-models.json) for
the crosswalk and divergences.

↩ [reference index](README.md)

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
`HD2_`; the id can't be inferred from a display name — look it up in POD Go Edit's catalog
(see [block-models.md](block-models.md)).

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

**POD Go pegs each effect to one width — a Helix carryover.** Helix offers many effects in
both a mono and a stereo version; POD Go ships only one. In POD Go Edit's catalog, of the
effects that carry a width suffix **119 are Stereo-only and 57 are Mono-only** — the **Looper**
is the sole model shipping both (`HD2_Looper` / `HD2_LooperOneSwitch`). So the suffix is fixed
per model, not a user choice.

The split follows the **signal path**: POD Go runs **mono up through the amp and cab, then
stereo after the cab** (owner-confirmed on hardware, v2.50). Pre-amp effects (dirt, dynamics,
pitch) are the **Mono** variants; time-based effects that sit post-cab (delay, reverb) are the
**Stereo** variants — which is why "delays and reverbs are stereo after the cab." Width lives
in the `@model` suffix, **not** the block's `@type` (`@type=0` holds both mono and stereo
effects — see [pgp-format.md](../presets/pgp-format.md#the-type-field)).

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

> **Caveat — Amp vs. Preamp id.** The amp built-in is matched by the `HD2_Amp` prefix, but
> POD Go also has **preamp** models whose id is `HD2_Preamp…` (POD Go Edit's own
> `default_preset_p34.hlx` puts `HD2_PreampTweedBluesBrt` in the amp slot). `HD2_Preamp…`
> does **not** match `HD2_Amp`, so a preamp placed in the amp role would currently be
> classified as a *free* block. This is a **latent gap** — no preset in the library uses a
> preamp, so nothing is misclassified today, but a future preamp-in-amp-slot preset would
> miscount. Flagged for the tools, not yet fixed.

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

## Where the ids come from

The authoritative source for every `@model` id is **POD Go Edit's bundled catalog**
(`*.models`; see [block-models.md](block-models.md)), read by
[`tools/podgo_models.py`](../../tools/podgo_models.py) — so ids no longer need to be
harvested from presets. Dumping a preset into `data-presets/` and running
`python3 tools/refresh.py` still works and is how [`registry/blocks.json`](../../registry/blocks.json)
was built (it records which ids appear in *our* presets), but it is no longer the only way
to *learn* an id.

## The USB device id (`usb_id`) → `@model` — encoding cracked, crosswalk empirical

Over USB, POD Go refers to a block by a **small integer** (`usb_id`), not by its `@model`
string. **The encoding is cracked** (hardware-confirmed on two independent captures, firmware
v2.50): in each occupied slot section of the preset stream, the `usb_id` is a **MessagePack
uint** stored right after the constant `c2 19` prefix, immediately before the `1aff09` marker
(fixint `< 0x80`, `0xcc` = uint8, `0xcd` = uint16 BE). **Amps and cabs use the same encoding.**
Decoded by [`tools/podgo_usb.py`](../../tools/podgo_usb.py).
Confirmation: Vol `224`, Amp `289`, EQ `472` re-read identically across two different presets.

The **id → `@model` map is a device-internal enumeration** we cannot derive from the app data:
`usb_id` is **not** the `PodGoModelDefs.bin` array index (refuted with real numbers — the
Deluxe Comp is `99`, not its array index `193`), not the community `helix_usb` "modules" table,
and no catalog ordering reproduces it. So the crosswalk must be built **empirically** from
captures of known presets; a partial one (10/574, hardware-read pairs) lives in
[`registry/usb-id-map.json`](../../registry/usb-id-map.json). Full coverage would need many
more captures or the device's own model table. See
[resources.md](resources.md) for the POD Go Edit on-disk resources.
