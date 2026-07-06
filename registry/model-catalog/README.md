# registry/model-catalog

Versioned snapshots of POD Go Edit's authoritative model catalog — one JSON per editor
version (`podgo-edit-<version>.json`), produced by
[`tools/extract_podgo_catalog.py`](../../tools/extract_podgo_catalog.py) and read by
[`tools/podgo_models.py`](../../tools/podgo_models.py).

Each snapshot lists every POD Go model keyed by `@model` (`symbolicID`) with its display
name, category, DSP `load`, parameter schema, and firmware provenance (which firmware
version added it). Re-run the extractor on a new POD Go Edit release; `git diff` shows
exactly what Line 6 changed between versions.

Full explanation: [docs/reference/block-models.md](../../docs/reference/block-models.md).
