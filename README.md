# Pod Go Presets

I created these presets for myself, but I'm willing to share. I have not found a reliable source of information about modifying Pod Go Presets. Most sources may have a few jailbroken preset files available for download, but nothing comprehensive.

If you base your presets off of this collection, I just ask that you include a link to this repository if you choose to redistribute them.

If you are interested in throwing a little monetary support my way, you can buy me a coffee!

<a href="https://www.buymeacoffee.com/cliftoneatf" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

If you find an issue with a preset, or have more information on how to modify the preset JSON files, please feel free to either submit a PR or create an issue. When creating an issue, please provide as much information as you can including screenshots/photos/videos and a detailed description of the problem and what version your software is on.

## Pod Go Version

All presets were made using Pod Go v2.50 and no garantees are made regarding backwards compatability

## Preset Naming

Pod Go Preset names can have up to 14 Characters, but the display behavior is dynamic:

1. In Edit mode, the full preset name can be viewed
2. In Play mode, the preset name is larger and depending on the width of the characters, more or less characters will be displayed. ie. Upper case characters and number characters are larger than lower case characters.
   Presets are named by what they have, not by what has been removed. This allows you to more quickly find the preset type you need. All presets exclude the Wah pedal.

Using the convention, `<Number of free blocks>/Vol/Wah/Fx/Eq/Looper/Amp/Cab`, the default preset would look like `4VWFxEqLpAmCb`.

Consider using `Amp/Cab/Cbo` for amp options?

## Preset Combinations

| Free Blocks | Volume |  Wah   | FX Loop |   EQ   | Looper |  Amp   |  Cab   | File name                   | Notes                   |
| ----------- | :----: | :----: | :-----: | :----: | :----: | :----: | :----: | --------------------------- | ----------------------- |
| 7           |   ❌   |   ❌   |   ❌    |   ✅   |   ❌   |   ✅   |   ✅   | `7bl_Eq_Amp_Cab`            |                         |
| 7           |   ❌   |   ❌   |   ❌    |   ❌   |   ✅   |   ✅   |   ✅   | `7bl_Lpr_Amp_Cab`           |                         |
| 7           |   ❌   |   ❌   |   ❌    |   ✅   |   ✅   |   ✅   |   ❌   | `7bl_Eq_Lpr_Amp`            |                         |
| 5           |   ✅   |   ✅   |   ✅    |   ✅   |   ✅   |   ❌   |   ❌   | `5bl_Vol_Wah_Fx_Eq`         |                         |
| ~~6~~       | ~~✅~~ | ~~❌~~ | ~~✅~~  | ~~✅~~ | ~~✅~~ | ~~❌~~ | ~~✅~~ | ~~`6bl_Vol_Fx_Eq_Cab`~~     | BROKEN                  |
| ~~7~~       | ~~✅~~ | ~~❌~~ | ~~❌~~  | ~~✅~~ | ~~✅~~ | ~~❌~~ | ~~❌~~ | ~~`7bl_Vol_Eq_Lpr`~~        | BROKEN                  |
| ~~7~~       | ~~❌~~ | ~~❌~~ | ~~✅~~  | ~~✅~~ | ~~✅~~ | ~~❌~~ | ~~❌~~ | ~~`7bl_FX_Eq_Lpr`~~         | BROKEN                  |
| 6           |   ❌   |   ❌   |   ✅    |   ✅   |   ❌   |   ✅   |   ✅   | `6bl_Fx_Eq_Amp_Cab`         |                         |
| 6           |   ❌   |   ❌   |   ✅    |   ❌   |   ✅   |   ✅   |   ✅   | `6bl_Fx_Lpr_Amp_Cab`        |                         |
| ~~6~~       | ~~✅~~ | ~~❌~~ | ~~✅~~  | ~~✅~~ | ~~✅~~ | ~~❌~~ | ~~❌~~ | ~~`6bl_Vol_Fx_Eq_Lpr`~~     | BROKEN                  |
| 6           |   ❌   |   ❌   |   ❌    |   ✅   |   ✅   |   ✅   |   ✅   | `6bl_Eq_Lpr_Amp_Cab`        | Use `7bl/Eq`instead     |
| 6           |   ✅   |   ❌   |   ❌    |   ✅   |   ❌   |   ✅   |   ✅   | `6bl_Vol_Eq_Amp_Cab`        |                         |
| 6           |   ✅   |   ❌   |   ❌    |   ❌   |   ✅   |   ✅   |   ✅   | `6bl_Vol_Lpr_Amp_Cab`       |                         |
| ~~5~~       | ~~✅~~ | ~~✅~~ | ~~✅~~  | ~~✅~~ | ~~✅~~ | ~~❌~~ | ~~❌~~ | ~~`5bl_Vol_Wah_Fx_Eq_Lpr`~~ | BROKEN                  |
| 5           |   ✅   |   ❌   |   ✅    |   ✅   |   ❌   |   ✅   |   ✅   | `5bl_Vol_Fx_Eq_Amp_Cab`     |                         |
| 5           |   ✅   |   ❌   |   ✅    |   ❌   |   ✅   |   ✅   |   ✅   | `5bl_Vol_Fx_Lpr_Amp_Cab`    |                         |
| 5           |   ❌   |   ❌   |   ✅    |   ✅   |   ✅   |   ✅   |   ✅   | `5bl_Fx_Eq_Lpr_Amp_Cab`     | Use `6bl/Fx/Eq` instead |

## Notes

-   When selecting what preset to use, consider the following
    -   Start with what pedals you need. Volume, Wah, and Fx Loop cannot be selected for a free block, so they must be chosen at the beginning.
    -   You will need to have at least one mandatory block, choose whether you want the Looper or the Eq.
        -   Looper is a useful tone tweaking and problem solving tool with no workaround.
        -   Eq is also a useful problem solving tool, but it can often be adjusted using an effect or amp's tone stack or in an emergency via the Global EQ.
-   All presets have no footswitch assignments or snapshots. The intent of this library is to provide a blank slate for you to create your own presets. This makes it simpler to work with and maintain the preset files.
-   Reordering blocks seems to also change the block number and `@position` property.
-   The mandatory Eq block can be converted to a looper block
-   The only way to get 7 free user assignable blocks is to remove the Volume pedal and the FX Loop. Keeping either of those effects in the chain will cause the Pod Go to display any free blocks > 6 but they can't be assigned by the user.
-   To get similar functionality with the hardware pedal without needing a Volume block, use a preset that has no volume block, but assign Exp 2 to control the level of an effect in the chain:
    -   Beginning-of-chain use:
        -   Dirt pedal `Gain` control
        -   Amp `Gain` control
    -   Mid chain, post-gain, pre-wet volume control use:
        -   EQ `Level`
        -   Amp `Ch Vol`
        -   Fx Loop `Return` if used before amp for dry effects.
    -   End-of-chain use:
        -   Cab `Level` parameter
        -   Output `Level` parameter
-   When editing a preset the following keys can be deleted:
    -   `snapshot0` through `snapshot3` - Pod Go will rebuild them on import
    -   `footswitch` - Pod Go will rebuild them on first assignment
    -   `controllers` - Pod Go will rebuild them on first assignment
-   Cab and Amp can be removed, but a 7 block limit still exists, and the FX Loop, Volume, Wah all contribute to that limit. That means that even without the FX Loop, Volume, and Wah, presets would be limited to:
    -   EQ
    -   Looper
    -   7 Free
    -   1 Un-assignable (recommend keeping amp model and using a preamp as a drive)
-   In the basic, factory preset, the `@type` properties are assigned as follows:
    | Block | Type |
    | ----- | ---- |
    | Volume | 0 |
    | Wah | 0 |
    | Fx Loop | 5 |
    | Eq | 0 |
    | Looper | 4 |
    | Amp | 1 |
    | Cab | 2,0 |
    | Some Delay and Reverb blocks | 5 |
-   In the basic, factory preset, the free blocks look like this:
    ```
        "block9" : {
          "@position" : 9
        },
    ```

## Troubleshooting

-   Free blocks that seemingly can't be assigned because the top dial won't change effect categories can still be assigned a Looper block. Scroll the top dial even though it seems like nothing is happening. Then scroll the bottom dial, you will see the category change and effect selection will change. You CANNOT select any of these effects though. Make your way blindly to the Looper category using the upper dial. Then use the lower dial to select the Looper you want. The Looper SHOULD be selectable.
-   If a footswitch controlling parameters gets out of sync, for example, a footswitch toggle in a snapshot is reversed compared to other snapshots, try setting
    ```
    "controller" : {
        "dsp0" : {
          "block7" : {
            "Mix" : {
              "@fs_momentary" : false,
              "@min" : 0.24000000953674316,
              "@fs_customcolor" : 6,
              "@max" : 0.45000004768371582,
              "@controller" : 4,
              "@fs_enabled" : false, // <-- Set this to false
              "@fs_ledcolor" : 7077838,
              "@fs_customlabel" : "Delay",
              "@fs_label" : "Mix"
            },
            ...
    ```

### Assignments

-   Parameter assigments seem to use `"@controller" : 3` through `"@controller" : 8`

## Testing

-   [ ] Test each "free" block can be assigned via the on-device selection process.
-   [ ] Run "Clear All Assignments"
