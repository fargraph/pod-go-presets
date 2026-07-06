# Blocks & Constraints

How POD Go's block chain works, and the rules that decide which preset
combinations are possible. This is the conceptual core of the project.

↩ [presets index](README.md)

## The chain

A preset's signal chain lives at `data.tone.dsp0` in the `.pgp` JSON. It is an
ordered set of `blockN` slots plus fixed `input` / `output` endpoints. A healthy
jailbroken preset exposes **10 `blockN` slots** (`block0`–`block9`).

Each slot is one of:

- **Empty / free** — `{ "@position": N }` only. User-assignable to any HX effect.
- **Occupied** — has an `@model` id (e.g. `HD2_AmpDelSol300`) plus params. This is
  either a *built-in* block or a user effect placed in a free slot.

> **The 10 slots are native, not created by the jailbreak.** POD Go's factory **New Preset**
> (firmware v2.50) already contains all ten `block0`–`block9`, with **6 built-ins** present
> (Volume, Wah, FX Loop, Amp, Cab, and the mandatory EQ *or* Looper) and **4 free slots** — so
> stock POD Go = **4 free blocks** (`10 − 6`). The jailbreak *removes built-ins* to free their
> slots (see [the free-block rule](#the-free-block-rule-corrected)); it does not add slots.
> (`@position` values in the JSON are slot indices, not necessarily signal-chain order.)

**Concrete factory layout (v2.50).** POD Go's factory New Preset — the repo's device-sourced
[`New-Preset-2_50_0.pgp`](../../original/New-Preset-2_50_0.pgp) (`schema:"L6Preset"` v6) —
fills the ten slots like this; note the **slot index is not signal-chain order**:

| Slot | `@model` | Role |
| --- | --- | --- |
| `block0` | `HD2_VolPanVolStereo` | Volume |
| `block1` | `HD2_WahFasselStereo` | Wah |
| `block2`–`block3` | *(empty)* | free ×2 |
| `block4` | `HD2_FXLoopMono1` | FX Loop |
| `block5` | `HD2_AmpUSDoubleNrm` | Amp |
| `block6` | `HD2_Cab2x12DoubleC12N` | Cab |
| `block7` | `HD2_EQ_STATIC_ParametricStereo` | EQ (mandatory) |
| `block8`–`block9` | *(empty)* | free ×2 |

That's **6 built-ins + 4 free = 4 stock free blocks.**

> **Aside — POD Go Edit bundles a *different* default.** The editor app ships a
> `default_preset_p34.hlx` (also `schema:"L6Preset"` v6, name `New Preset`) with the same 6+4
> economy but a **different slot arrangement** (EQ `block0`, Wah `block1`, FX Loop `block2`,
> Preamp `block3`, Cab `block7`, Volume `block9`; free at 4–6, 8) — and it uses a *Preamp*
> (`HD2_Preamp…`) in the amp role. **How the editor uses that file is unconfirmed;** per the
> project owner, POD Go populates a new preset from the **device firmware**, not from POD Go
> Edit (there's no known "new preset" or "revert to default" action in the editor). So the two
> files together establish only the **structural economy** — 10 slots, 6 built-ins + 4 free,
> built-ins *not* pinned to fixed slot indices — and the **device's own New Preset is the
> authority** on the actual factory layout.

## Built-in vs. free blocks

Seven block roles are "built-in" (dedicated, not freely-typed). We detect each by
the prefix of its `@model` id:

| Role | `@model` prefix | Free? | Notes |
| --- | --- | --- | --- |
| Volume | `HD2_VolPan` | no | Fixed block, EXP 2 |
| Wah | `HD2_Wah` | no | Fixed block, EXP 1 |
| FX Loop | `HD2_FXLoop` | no | Single fixed send/return |
| EQ | `HD2_EQ_` | no | "Preset EQ"; convertible to Looper |
| Looper | `HD2_Looper` | no | Mandatory-slot alternative to EQ |
| Amp | `HD2_Amp` | no | One amp block |
| Cab | `HD2_Cab` | no | One cab/IR block |

Everything else (Dist, Delay, Reverb, Mod, Filter, Pitch/Synth, Dynamics, and EQ
when used as an extra) is a **free-block effect**.

## The free-block rule (corrected)

> **free_blocks = (number of `blockN` slots) − (number of built-in blocks present)**

Base slot count is **10**. So each built-in you *keep* costs one potential free
block; each you *remove* frees one — **as long as the preset stays valid** (see
below). Worked examples (all verified against the working library):

| Preset | Built-ins present | Slots | Free |
| --- | --- | --- | --- |
| `7_---E-_AC` | eq, amp, cab (3) | 10 | 7 |
| `6_--FE-_AC` | fx, eq, amp, cab (4) | 10 | 6 |
| `5_V-FE-_AC` | vol, fx, eq, amp, cab (5) | 10 | 5 |

> **Note:** an earlier rule of thumb — "free = 7 − Vol − Wah − FX Loop" — is
> *wrong*. It happens to match presets that keep EQ+Amp+Cab, but it fails whenever
> you keep both EQ and Looper, or drop Amp/Cab. Count slots minus built-ins.

## The validity ceiling (why "more free" isn't free)

Removing built-ins *should* give more free blocks, but two hard limits bite:

1. **The 7 assignable-block ceiling.** POD Go will *display* free blocks beyond 7
   but won't let you assign them. Keeping **Volume** or the **FX Loop** while
   also having 7 free blocks produces an unassignable phantom slot — the preset
   reads as broken. The only way to a genuine 7 free is to remove **both**
   Volume and FX Loop (Wah too counts against the budget).

2. **Removing Amp/Cab destabilizes the chain.** Empirically (see
   [data-quality.md](../knowledge/data-quality.md) and the registry), presets that remove the
   **Amp** tend to break, and removing **both Amp and Cab** collapses the chain to
   8–9 slots and reliably breaks. Removing only the **Cab** while keeping the Amp
   is fine. This is why the taxonomy below matters.

## Removal taxonomy (folder layout)

Presets are grouped by which of Amp/Cab they remove — the axis that most affects
validity:

| Folder | Amp | Cab | Observed (library status counts) |
| --- | :-: | :-: | --- |
| `with-amp-cab` | ✅ | ✅ | Safe — 11 working / 2 broken (the 2 fail on DSP or the free-7 edge, *not* the amp/cab axis) |
| `no-cab` | ✅ | ❌ | Works — 2 / 0 |
| `no-amp` | ❌ | ✅ | Risky — 1 working / 1 broken |
| `no-amp-and-cab` | ❌ | ❌ | Breaks — 0 working / 6 broken |

Working/broken status is **not** encoded by folder — it lives in
[registry/combinations.json](../../registry/combinations.json) and in a `_bad`
tag in the preset name. A folder just says which built-ins were removed.

> **Demonstrated by** (see [business-rules.md](business-rules.md) for status, and the
> [manifest](../../data-presets/demonstrations/manifest.json) for what to observe):
> free-block formula → [base](../../original/New-Preset-2_50_0.pgp);
> phantom 7th slot → [`7_--F--_AC_bad`](../../presets/with-amp-cab/7_--F--_AC_bad.pgp);
> genuine 7 free → [`7_---E-_A-`](../../presets/no-cab/7_---E-_A-.pgp);
> removing both Amp+Cab collapses → [`6_--FEL_--_bad`](../../presets/no-amp-and-cab/6_--FEL_--_bad.pgp).
> All still **⬜ unverified** pending joint hardware confirmation.

## Import-translation constraints (why blocks drop)

Removal taxonomy and the phantom-slot ceiling are *structural* limits. Beyond those, POD Go
enforces a **set of constraints when it imports (“translates”) a preset**. If the preset
exceeds any of them, POD Go **silently drops blocks** (trailing-first) rather than refusing
the preset — audio still flows through the blocks that fit and the UI stays responsive
(graceful degradation, hardware-confirmed, firmware v2.50).

The constraint **names come from POD Go Edit's own error strings**
(`appErrorStrings_eng.json` — app-authoritative, not our inference; see
[resources.md](../reference/resources.md)):

| Constraint (Line 6's wording) | Meaning |
| --- | --- |
| `max dsp processing load exceeded` | the **DSP load** budget |
| `dsp block constraint exceeded` | a **block-count** cap (separate from load) |
| `too many amps` / `too many cabs` / `too many IRs` | **≤ 1 each** — the single-amp / single-cab rules |
| `too many parallel dsp paths`, `path block constraint`, split/join rules | parallel-path limits (POD Go is single-path → mostly N/A) |
| `incompatible model` | a model not valid for this device/slot |
| `Invalid or bad block location specified` | placement validity |

**Two of these trip the drop, whichever comes first** — observed on hardware with two
purpose-built test presets (same recorded-working structure; only the block weight/count
varied):

- A **heavy** over-budget preset
  ([`build_dsp_test.py`](../../tools/spikes/build_dsp_test.py), 10 heavy blocks) hit the
  **max DSP load** limit — POD Go kept the first **5** blocks and dropped the rest.
- A **light** 10-block preset
  ([`build_calibration.py`](../../tools/spikes/build_calibration.py)) was well under any load
  estimate yet still dropped 3 blocks — it hit the **block-count** constraint, keeping **7**.

So block-dropping is **not purely DSP load**; it's this constraint set.

### On the DSP-load numbers — a caution

Per-block **DSP load** values exist in POD Go Edit's catalog and are read by
[`tools/podgo_models.py`](../../tools/podgo_models.py) (amps heaviest ~24–31; reverb/delay
next; cab/wah/volume cheap). They're useful for *relative* comparison, **but they are only a
rough proxy — they do NOT sum to POD Go's actual DSP %.** (A preset that looked light by
catalog-load still hit a constraint, so any specific “total DSP budget” number from summing
`load` is unreliable — an earlier draft of this doc claimed ~98–129 and that was wrong-scale.)
The real numeric limits (max block count, max DSP %) are **compiled into the POD Go Edit
executable**, not in any readable data file; they can be pinned empirically by bisection.
Current hardware bounds: a *light* preset fits ~7 blocks, a *heavy* one ~5. See
[verified.md](../knowledge/verified.md) and [troubleshooting.md](../knowledge/troubleshooting.md).

### Keeping the Amp is a signal-path rule, not a DSP one

The amp is the single biggest DSP consumer (~24), so removing it *frees* the most
budget — a `no-amp` preset can carry more/heavier effects. The library's
highest-DSP **working** preset (10 blocks, total 80.7) is in fact a `no-amp` preset.
So "keep the amp" is about signal-path stability, not DSP headroom; when a no-amp
preset does work, it enables the fullest chains.

### free = 7 is a slot edge, independent of DSP

The phantom-slot ceiling is orthogonal to the budget: a `with-amp-cab` preset with
**free = 7** (both Volume and FX Loop removed) broke at a *low* DSP load (~29.5) — it
failed the slot/routing limit, not the budget.

## Mandatory block: EQ or Looper

At least one of **EQ** or **Looper** must remain. The mandatory EQ block can be
converted into a Looper. Trade-off:

- **Looper** — tone-tweaking/problem-solving tool with no workaround.
- **EQ** — also useful, but often replaceable via an effect/amp tone stack or the
  Global EQ in a pinch.

## Getting a volume-pedal feel without a Volume block

To free the Volume slot but still ride level with EXP 2, assign it to:
- Beginning of chain: Dirt `Gain`, Amp `Gain`
- Mid chain (post-gain, pre-wet): EQ `Level`, Amp `Ch Vol`, FX Loop `Return` (if
  pre-amp for dry effects)
- End of chain: Cab `Level`, Output `Level`
