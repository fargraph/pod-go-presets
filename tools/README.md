# tools/

Standard-library-only Python 3 scripts that harvest block data, validate
presets, and regenerate the registry/docs. Run them from the repo root.

| Command | Does |
| --- | --- |
| `python3 tools/refresh.py` | **After adding data-presets:** harvest + coverage in one step |
| `python3 tools/harvest_blocks.py` | Rebuild `registry/blocks.json` (block ids + per-preset linkage) |
| `python3 tools/coverage.py` | Rebuild `docs/reference/data-coverage.md` gap worklist |
| `python3 tools/validate_presets.py` | Check every preset matches its registry entry & name (exit non-zero on error) |
| `python3 tools/gen_matrix.py` | Regenerate `registry/presets.csv` + the clickable preset list in the README |

`podgo.py` is the shared library (load/parse, classify, taxonomy, naming) — the
other scripts import it. Coding style: [`docs/conventions/code-conventions.md`](../docs/conventions/code-conventions.md).
Tool details and the add-a-preset flow: [`docs/presets/naming-and-registry.md`](../docs/presets/naming-and-registry.md).
