# Resources & Links

External references gathered while building this knowledge base. Firmware target
throughout is **POD Go v2.50** (Helix 3.5-era model set).

## This project

- **Repo:** <https://github.com/fargraph/pod-go-presets>
- **Support the author:** <https://www.buymeacoffee.com/cliftoneatf>

## Line 6 primary sources (authoritative)

- **POD Go model gallery** — <https://line6.com/podgo-models/>
  Official interactive list of every amp/cab/effect with "based on" attributions. The
  most complete *current* model list. (Renders via JS; a plain fetch may not get the
  full table — cross-check against a unit or POD Go Edit.)
- **POD Go 2.50 Owner's Manual** (doc 40-00-0568 Rev G, fw v2.50) — the most
  authoritative text source; verbatim per-category model tables incl. the
  "—Legacy Models—" sub-groups.
  <https://line6.com/data/6/0a00040c018d681e825e1c4b3/application/pdf/POD%20Go%202.50%20Owner's%20Manual%20-%20English%20.pdf>
- **POD Go 2.0 Owner's Manual** (Rev E, fw v2.0) — confirms v2.0 additions.
- **POD Go 1.10 Owner's Manual** (fw v1.10) — baseline model tables with "based on" gear.
- **POD Go 1.40 release notes** — <https://line6.com/support/page/kb/pod/pod-go/pod-go-140-r1037/>
  Confirms which models were added in 1.40.
- **POD Go FAQ / Knowledge Base** — <https://kb.line6.com/pod-go-faq>
  Block structure, fixed vs. free blocks, FX Loop mono/stereo behavior.

## Community / secondary

- **Helix/HX/POD Go model database** — <https://helixhelp.com/models>
  Community cross-reference (loads dynamically). Good for spotting Helix-vs-POD Go deltas.
- **Line 6 Community** — amp-vs-preamp confirmation, and the enumeration of the
  polyphonic-pitch models POD Go omits, came from staff/community threads on
  <https://line6.com/support/>.

## Notes on trusting these

- **Hardware and POD Go Edit beat the docs.** Line 6's marketing counts differ from the
  itemized manual tables, and at least one research claim was wrong (dual-cab — POD Go is
  single-cab only). When a source disagrees with the unit, the unit wins; record the
  correction in [reference-models.json](../registry/reference-models.json) and re-run
  `tools/coverage.py`. See [lessons-learned.md](lessons-learned.md).
- **Internal `@model` ids are never published** by Line 6 — the manuals/gallery give
  display names only. Ids can only be captured by dumping a preset (see
  [reference/model-id-conventions.md](reference/model-id-conventions.md)).
