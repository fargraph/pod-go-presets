# Troubleshooting

## Assigning a "stuck" free block

Free blocks that seem unassignable (the top dial won't change effect categories)
can still take a **Looper**. Scroll the top dial even though nothing appears to
happen, then scroll the bottom dial — the category/selection will change but you
**cannot** select any of these effects. Blindly work the upper dial to the
**Looper** category, then use the lower dial to pick the Looper. The Looper should
select.

> If a preset has more than the assignable ceiling of free blocks (e.g. 7 free
> while keeping Volume or the FX Loop), the extra slot is a phantom and can't be
> assigned at all. That's a design limit, not a bug — see
> [blocks-and-constraints.md](blocks-and-constraints.md).

## Footswitch / snapshot out of sync

If a footswitch that controls parameters gets out of sync (e.g. a toggle is
reversed in one snapshot vs others), edit the controller entry and set
`@fs_enabled` to `false`:

```jsonc
"controller": {
  "dsp0": {
    "block7": {
      "Mix": {
        "@fs_momentary": false,
        "@controller": 4,
        "@fs_enabled": false,   // <-- set this to false
        "@fs_customlabel": "Delay",
        "@fs_label": "Mix"
      }
    }
  }
}
```

## Parameter assignments

Parameter assignments use `"@controller": 3` through `"@controller": 8`.

## Reporting a problem

Open an issue with as much detail as possible: screenshots/photos/video, a clear
description of the problem and expected behavior, and your **firmware version**.
