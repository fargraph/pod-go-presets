# Blocks & Constraints

How POD Go's block chain works, and the rules that decide which preset
combinations are possible. This is the conceptual core of the project.

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
| `7bl_eq_amp_cab` | eq, amp, cab (3) | 10 | 7 |
| `6bl_fx_eq_amp_cab` | fx, eq, amp, cab (4) | 10 | 6 |
| `5bl_vol_fx_eq_amp_cab` | vol, fx, eq, amp, cab (5) | 10 | 5 |

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
   [data-quality.md](data-quality.md) and the registry), presets that remove the
   **Amp** tend to break, and removing **both Amp and Cab** collapses the chain to
   8–9 slots and reliably breaks. Removing only the **Cab** while keeping the Amp
   is fine. This is why the taxonomy below matters.

## Removal taxonomy (folder layout)

Presets are grouped by which of Amp/Cab they remove — the axis that most affects
validity:

| Folder | Amp | Cab | Observed |
| --- | :-: | :-: | --- |
| `with-amp-cab` | ✅ | ✅ | Safe |
| `no-cab` | ✅ | ❌ | Works |
| `no-amp` | ❌ | ✅ | Suspect — verify on hardware |
| `no-amp-and-cab` | ❌ | ❌ | Breaks (all known examples broken) |

Working/broken status is **not** encoded by folder — it lives in
[registry/combinations.json](../registry/combinations.json) and in a `_broken`
filename suffix. A folder just says which built-ins were removed.

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
