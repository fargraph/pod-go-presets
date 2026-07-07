#!/usr/bin/env bash
# Launch the re-signed POD Go Edit copy WITH the libusb interposer, as the sole instance.
# Fixes the "double-clicked / already-running" trap: env vars (DYLD_INSERT_LIBRARIES,
# PODGO_USB_LOG) only apply when the binary is exec'd directly, and the app is single-instance
# — a non-injected copy already running makes the injected launch defer and quit.
# See plans/usb-libusb-intercept/PLAN.md (Step 3).
set -euo pipefail

CAP="${PODGO_CAP:-/Users/clifton.eaton/Desktop/Pod Go Presets/podgo-usb-capture}"
APP_BIN="$CAP/POD Go Edit (RE).app/Contents/MacOS/POD Go Edit"
DYLIB="$CAP/libusb_intercept.dylib"
LOG="$CAP/run-$(date +%Y%m%d-%H%M%S).log"

[ -x "$APP_BIN" ] || { echo "missing re-signed app: $APP_BIN"; exit 1; }
[ -f "$DYLIB" ]   || { echo "missing interposer (run build.sh): $DYLIB"; exit 1; }

# Kill ANY running instance of the RE copy (injected or not) so ours is the sole instance.
# Pattern matches the copy's path (no parens → safe for pkill -f regex).
if pkill -f "podgo-usb-capture/POD Go Edit"; then
  echo "quit a straggler POD Go Edit (RE) instance; waiting for it to release the USB interface"
  sleep 2
fi

echo "log -> $LOG"
echo "launching injected POD Go Edit — connect the unit and drive known operations, then quit."
export DYLD_INSERT_LIBRARIES="$DYLIB"
export PODGO_USB_LOG="$LOG"
exec "$APP_BIN"
