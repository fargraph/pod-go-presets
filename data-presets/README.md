# data-presets/

Stock Pod Go preset dumps kept purely for **data retrieval** — harvesting the
exact internal `@model` id strings for every factory block, organized by the
device's category/page layout (e.g. "Reverb Page 1a", "Dist Page 5").

These are **not** usable/curated presets. Internal `@model` ids are never
published by Line 6; the only way to learn one is to dump a preset that uses the
block, which is what these files are for. `tools/harvest_blocks.py` (via
`tools/refresh.py`) reads them into [`registry/blocks.json`](../registry/blocks.json),
and [`docs/reference/data-coverage.md`](../docs/reference/data-coverage.md) tracks
which ids are still missing.

Background: [`docs/reference/model-id-conventions.md`](../docs/reference/model-id-conventions.md).
