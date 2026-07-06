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

## The DSP budget (second validity factor)

Removal taxonomy and the phantom-slot ceiling are *structural* limits. A
structurally-sound preset can still break for a second, independent reason: it
exceeds POD Go's **DSP budget**. POD Go runs a single DSP path, and every block
consumes a fixed slice of it. The per-model **DSP load** is published in POD Go
Edit's catalog and read by [`tools/podgo_models.py`](../../tools/podgo_models.py)
(see [reference/block-models.md](../reference/block-models.md)).

Approximate per-block loads (firmware v2.50, from the catalog):

| Block | DSP load |
| --- | --- |
| **Amp** | ~24 median, up to 31 — **by far the heaviest** |
| Preamp | ~15 median |
| Reverb ~13 · Delay ~9 | the expensive effects |
| Distortion / Modulation | ~6 median |
| Cab 6.0 · IR 2.5 · Wah ~3.3 · Volume 1.5 | cheap |
| Input + Output | ~22 fixed baseline (always present) |

**What the tested library shows** — summing every block's load across the 23
recorded presets ([`tools/spikes/preset_dsp.py`](../../tools/spikes/preset_dsp.py)):

- Every **working** preset sits at **total DSP ≤ ~80.7** (block-load ≤ 58.7).
- The two heaviest **structurally-sound** (`with-amp-cab`) presets — total **93–94**
  — break on DSP *alone*.
- So a real ceiling sits between ~59 and ~71 block-load; its exact value is **not yet
  pinned** (the library has a gap there). Pinning it with purpose-built boundary
  presets is a deferred task.

This is **derived/analysis knowledge**, cross-checked against the library's recorded
statuses — not itself a new hardware claim. Per-block loads come from Line 6's catalog
(a `source`); the ceiling is `inferred`. See [verified.md](../knowledge/verified.md).

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
