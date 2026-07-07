# Reference — model catalog, id syntax, generated data & links

The catalog side of the knowledge base: the authoritative Pod Go model list, how
internal `@model` ids are structured, the auto-generated worklist of which ids
we've captured, and the external sources everything traces back to. The
machine-readable data lives in [`registry/`](../../registry/).

↩ [Docs home](../README.md)

## Files in this folder

- [block-models.md](block-models.md) — the authoritative list of every block Pod
  Go can load, by category; the chain architecture; Pod Go vs. Helix deltas; and
  the Line 6 sources. Machine-readable list:
  [`registry/reference-models.json`](../../registry/reference-models.json).
- [model-id-conventions.md](model-id-conventions.md) — how Pod Go names blocks
  internally in the JSON: prefixes (`HD2_`, `VIC_`, bare legacy), legacy stompbox
  family codes, mono/stereo suffixes, and `EQ_STATIC` vs. `EQ`.
- [usb-id-mapping.md](usb-id-mapping.md) — the separate **`usb_id`** id system: the
  hardware-cracked wire encoding, why the `usb_id → @model` map is device-internal
  (confirmed by decompiling POD Go Edit — it's not in the app), the
  monotonic-within-category constraint, and how to grow the empirical crosswalk.
- [usb-control-protocol.md](usb-control-protocol.md) — the **USB control protocol**: how POD Go
  Edit drives the unit (transport, channels, frame format, session mechanics) and the decoded
  **command dictionary** (bypass/set-model/set-param/add/remove/load/save/rename), plus the libusb
  capture method. Orientation + status (⬜ decoded, not replay-verified); byte-level spec in
  [`tools/usb-intercept/protocol.md`](../../tools/usb-intercept/protocol.md).
- [data-coverage.md](data-coverage.md) — **generated** gap worklist: which block
  `@model` ids we've captured vs. still need. Written by
  [`tools/coverage.py`](../../tools/coverage.py); **do not hand-edit.**
- [resources.md](resources.md) — external links: Line 6 manuals, the model
  gallery, the FAQ/knowledge base, and community references, plus notes on how far
  to trust each.

## Related

- What the `registry/*.json` files are and how ids get harvested:
  [../presets/naming-and-registry.md](../presets/naming-and-registry.md).
