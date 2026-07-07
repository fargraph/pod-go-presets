#!/usr/bin/env bash
# Build + ad-hoc-sign the libusb interposer into the out-of-repo scratch dir.
# See plans/usb-libusb-intercept/PLAN.md. Run from anywhere.
set -euo pipefail

# Scratch dir (parent working dir, one level above the repo; not checked in).
CAP="${PODGO_CAP:-/Users/clifton.eaton/Desktop/Pod Go Presets/podgo-usb-capture}"
SRC="$(cd "$(dirname "$0")" && pwd)/libusb_intercept.c"
OUT="$CAP/libusb_intercept.dylib"

mkdir -p "$CAP"
echo "building $OUT (x86_64, to match the Rosetta app)"
clang -arch x86_64 -dynamiclib -O2 -Wall \
      -Wl,-undefined,dynamic_lookup \
      -o "$OUT" "$SRC"

echo "ad-hoc signing (Apple Silicon requires a signature even for x86_64)"
codesign --force --sign - "$OUT"

echo "done. verify with:  otool -l \"$OUT\" | grep -A3 __interpose ; codesign -dv \"$OUT\""
echo
echo "capture (quit the real POD Go Edit + any pyusb spikes first):"
echo "  DYLD_INSERT_LIBRARIES=\"$OUT\" \\"
echo "  PODGO_USB_LOG=\"$CAP/run1.log\" \\"
echo "    \"$CAP/POD Go Edit (RE).app/Contents/MacOS/POD Go Edit\""
