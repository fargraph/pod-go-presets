#!/usr/bin/env python3
"""Harvest every distinct @model id we have data for, from data-presets/ and
presets/, into registry/blocks.json.

The internal @model strings (e.g. HD2_AmpDelSol300) can ONLY be learned by
dumping a real preset that uses that block -- Line 6 never publishes them. So
this file is our growing record of "which blocks we have captured the id for."
Category is a best-effort heuristic; the authoritative taxonomy lives in
docs/reference/block-models.md.

Usage:  python3 tools/harvest_blocks.py   (writes registry/blocks.json)
"""
import json
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import podgo

# Ordered (regex, category) -- first match wins, so list specifics first.
CATEGORY_RULES = [
    (r"AppDSPFlow", "io"),
    (r"HD2_Cab", "cab"),
    (r"HD2_Amp", "amp"),
    (r"HD2_VolPan", "volume-pan"),
    (r"HD2_Wah", "wah"),
    (r"HD2_FXLoop", "fx-loop"),
    (r"HD2_Looper", "looper"),
    (r"HD2_EQ|CaliQStereo|AcousGtrSim", "eq"),
    (r"DM4.*Comp|Compressor|Gate|Autoswell|VettaJuice|VettaComp|BoostComp|RedComp|BlueComp|TubeComp", "dynamics"),
    (r"Dist|Fuzz|Overdrive|Drive|Screamer|Boost|Bitcrusher|Megaphone|Scrambler|Minotaur|Teemah|Pillars|Obsidian|Hedgehog|Stupor|BronzeMaster|KillerZ|KWB|DM4", "distortion"),
    (r"Delay|DL4|Echo|Eko|Euclidean", "delay"),
    (r"Reverb|DynPlate|DynRoom|Plateaux|Ganymede|Searchlights|Shimmer|Glitz|DoubleTank|Particle", "reverb"),
    (r"Pitch|Synth|Harmony|Octaver|Boctaver|Wham|Saturn5|RezSynth|Seismic|BuzzWave|DoubleBass|Growler", "pitch-synth"),
    (r"Filter|FM4|Tron|Seeker|Throbber|ObiWah|VoiceBox|SpinCycle|SlowFilter|CometTrails|Mutant|Myster|Asheville", "filter"),
    (r"MM4|M13|M138|Chorus|Flanger|Phaser|Tremolo|Trem|Rotary|Vibe|Vibrato|Ring|Panner|Panned|Dimension|Sweeper|Matic|RetroReel|DoubleTake|Barberpole|FrequencyShift|SampleAndHold|Warble|TapeEater|ScriptPhase", "modulation"),
]


def category_of(model):
    for pat, cat in CATEGORY_RULES:
        if re.search(pat, model):
            return cat
    return "unknown"


def friendly(model):
    """Rough human name from the id (for eyeballing only)."""
    s = re.sub(r"^(HD2_|VIC_)", "", model)
    s = re.sub(r"(Mono|Stereo)$", "", s)
    s = re.sub(r"(?<=[a-z])(?=[A-Z0-9])", " ", s)
    return s.strip()


def main():
    seen = collections.OrderedDict()

    def scan(paths):
        for p in paths:
            data, status = podgo.load_pgp(p)
            if data is None:
                continue
            rel = os.path.relpath(p, podgo.REPO)
            for m in podgo.models(data):
                e = seen.setdefault(m, {"category": category_of(m), "name": friendly(m),
                                        "occurrences": 0, "presets": set()})
                e["occurrences"] += 1      # counts repeats within a file too
                e["presets"].add(rel)      # distinct preset files this block appears in

    # order matters only for display; every file is scanned regardless
    scan(podgo.data_preset_paths())
    scan(podgo.preset_paths())

    by_cat = collections.Counter(e["category"] for e in seen.values())
    out = {
        "schema": "podgo-blocks/v2",
        "note": "Distinct @model ids we have captured, with the exact preset files each "
                "appears in ('presets'). Regenerate anytime to refresh the linkage. "
                "Category is heuristic; see docs/reference/block-models.md for the authoritative list.",
        "distinct_models": len(seen),
        "counts_by_category": dict(sorted(by_cat.items())),
        "models": {m: {"category": e["category"], "name": e["name"],
                       "occurrences": e["occurrences"], "in_presets": len(e["presets"]),
                       "presets": sorted(e["presets"])}
                   for m, e in sorted(seen.items(), key=lambda kv: (kv[1]["category"], kv[0]))},
    }
    dest = os.path.join(podgo.REPO, "registry", "blocks.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    json.dump(out, open(dest, "w"), indent=2)
    print(f"Wrote {os.path.relpath(dest, podgo.REPO)}: {len(seen)} distinct models")
    for cat, n in sorted(by_cat.items()):
        print(f"  {cat:14} {n}")


if __name__ == "__main__":
    main()
