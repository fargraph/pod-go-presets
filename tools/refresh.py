#!/usr/bin/env python3
"""One-shot refresh after adding or editing presets / data-presets.

Rebuilds registry/blocks.json (distinct block ids + per-preset linkage), then
regenerates docs/reference/data-coverage.md (the gap worklist). Run this whenever
you drop new data-presets in to capture more block @model ids.

Usage:  python3 tools/refresh.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harvest_blocks
import coverage

if __name__ == "__main__":
    print("== harvest blocks ==")
    harvest_blocks.main()
    print("\n== coverage ==")
    coverage.main()
