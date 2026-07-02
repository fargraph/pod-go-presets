# Knowledge — what hardware testing taught us

The living lab notebook. Because a preset's viability is only real on the unit,
this is where confirmed facts, discovered defects, on-device quirks, and the
digest of non-obvious findings live — kept honest about what's verified vs.
inferred.

↩ [Docs home](../README.md)

## Files in this folder

- [verified.md](verified.md) — the **hardware-verification ledger**: every claim
  slotted by confidence tier (✅ confirmed on a unit · 🔬 inferred from the tested
  library · 📖 from Line 6 sources · ⏳ pending). Consult this before trusting any
  "fact".
- [data-quality.md](data-quality.md) — concrete defects found in the preset
  library (wrong names, duplicate/missing blocks, dropped slots, malformed JSON)
  and their fixes.
- [troubleshooting.md](troubleshooting.md) — on-device quirks and workarounds:
  assigning a "stuck" free block, footswitch/snapshot sync, parameter assignments.
- [lessons-learned.md](lessons-learned.md) — a digest of the non-obvious things
  discovered building this knowledge base; each entry links to the detail doc.

## Related

- The rules these findings validate or correct:
  [../presets/blocks-and-constraints.md](../presets/blocks-and-constraints.md).
- The prescriptive practices derived from them:
  [../conventions/best-practices.md](../conventions/best-practices.md).
