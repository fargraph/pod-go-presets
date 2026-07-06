"""Spike 0.2 — POD Go connect handshake + dump (NO state changes).

Feasibility probe (see EXECPLAN-podgo-mcp-usb.md, Spike 0.2). Answers:
  R2 — does the POD Go respond on 0x81 when we send the proper Connect initiation?
  R5 — can we claim vendor interface 0 on macOS?  (already answered PASS in v1)

v2 change: the helix_usb protocol is a stateful handshake, not a passive stream. It
begins with a Connect "start" packet; the device only talks back after that. v1 sent
only keepalives (heartbeats) and got silence — expected. This version sends the Connect
start packet first, then a heartbeat each second to hold the session, and dumps every
inbound packet on 0x81 so we can see whether the POD Go engages.

Packets ported verbatim from kempline/helix_usb (HX Stomp). We do NOT (yet) implement
the full scripted response state machine — this is just: initiate + heartbeat + observe.

SAFETY: writes only the Connect-initiation + keepalive packets (same class of traffic
POD Go Edit sends on connect/idle). No preset load, no block toggle, no settings write.

PREREQ: POD Go on & connected, **POD Go Edit fully closed**.
Run:  python3 tools/spikes/connect_dump_podgo.py
"""
import sys
import time
import threading

VID, PID = 0x0E41, 0x424B
EP_OUT, EP_IN = 0x01, 0x81
RUN_SECONDS = 10
READ_TIMEOUT_MS = 500

# Connect mode start() packet — the session initiation (verbatim from modes/connect.py).
CONNECT_START = bytes([0xc, 0x0, 0x0, 0x28, 0x1, 0x10, 0xef, 0x3, 0x0, 0x0, 0x0,
                       0x2, 0x0, 0x1, 0x0, 0x21, 0x0, 0x10, 0x0, 0x0])

# Heartbeats (byte 9 = per-type counter starting 0x2, wraps 0xFF->0).
def x1x10(c):
    return bytes([0x8, 0x0, 0x0, 0x18, 0x1, 0x10, 0xef, 0x3, 0x0, c, 0x0, 0x8,
                  0x72, 0x1e, 0x0, 0x0])
def x2x10(c):
    return bytes([0x8, 0x0, 0x0, 0x18, 0x2, 0x10, 0xf0, 0x3, 0x0, c, 0x0, 0x10,
                  0x9, 0x10, 0x0, 0x0])
def x80x10(c):
    return bytes([0x8, 0x0, 0x0, 0x18, 0x80, 0x10, 0xed, 0x3, 0x0, c, 0x0, 0x10,
                  0x0, 0x0, 0x0, 0x0])


def hexdump(data):
    b = bytes(data)
    rows = []
    for i in range(0, len(b), 16):
        chunk = b[i:i + 16]
        hexs = " ".join(f"{x:02x}" for x in chunk)
        asci = "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)
        rows.append(f"    {i:04x}  {hexs:<47}  {asci}")
    return "\n".join(rows)


def main():
    try:
        import usb.core
        import usb.util
    except ImportError:
        print("ERROR: pyusb not installed.  ->  pip install pyusb", file=sys.stderr)
        return 2

    try:
        dev = usb.core.find(idVendor=VID, idProduct=PID)
    except usb.core.NoBackendError:
        print("ERROR: no libusb backend.  ->  brew install libusb", file=sys.stderr)
        return 2
    if dev is None:
        print(f"POD Go ({VID:04x}:{PID:04x}) not found. On & connected?")
        return 1
    print(f"Found POD Go {VID:04x}:{PID:04x}")

    try:
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
    except (NotImplementedError, usb.core.USBError):
        pass

    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]
    try:
        usb.util.claim_interface(dev, intf)
        print("Claimed interface 0 (R5: PASS)")
    except usb.core.USBError as e:
        print(f"FAILED to claim interface 0: {e}  (is POD Go Edit open?)")
        return 1
    for ep in (EP_OUT, EP_IN):
        try:
            dev.clear_halt(ep)
        except usb.core.USBError:
            pass

    received = []
    stop = threading.Event()
    t0 = time.monotonic()

    def reader():
        while not stop.is_set():
            try:
                data = dev.read(EP_IN, 512, timeout=READ_TIMEOUT_MS)
                t = time.monotonic() - t0
                received.append((t, bytes(data)))
                print(f"\n[IN  +{t:5.2f}s] {len(data)} bytes on 0x81:")
                print(hexdump(data))
            except usb.core.USBTimeoutError:
                continue
            except usb.core.USBError as e:
                print(f"[reader] USBError: {e}")
                break

    th = threading.Thread(target=reader, daemon=True)
    th.start()

    def send(name, pkt):
        try:
            dev.write(EP_OUT, pkt, timeout=1000)
            print(f"[OUT +{time.monotonic()-t0:5.2f}s] {name} ({len(pkt)}B)")
        except usb.core.USBError as e:
            print(f"[OUT] {name} failed: {e}")

    # Phase 1: the session initiation the device is actually waiting for.
    print("\n-- Phase 1: Connect start packet --")
    send("CONNECT_START", CONNECT_START)

    # Phase 2: heartbeat once/sec to hold the session while we listen.
    print("-- Phase 2: heartbeat + listen --")
    c = 0x2
    for _ in range(RUN_SECONDS):
        for name, pkt in (("x1x10", x1x10(c)), ("x2x10", x2x10(c)),
                          ("x80x10", x80x10(c))):
            send(name, pkt)
        c = (c + 1) if c < 0xFF else 0x0
        time.sleep(1.0)

    stop.set()
    th.join(timeout=2)
    try:
        usb.util.release_interface(dev, intf)
        usb.util.dispose_resources(dev)
    except usb.core.USBError:
        pass

    total = sum(len(d) for _, d in received)
    print("\n" + "=" * 62)
    print(f"SPIKE 0.2 SUMMARY: received {len(received)} inbound reads / {total} bytes.")
    print("  R5 (claim iface 0 on macOS): PASS")
    if received:
        print("  R2 (device engages on Connect handshake): PASS — POD Go responded!")
        print("  -> Big signal. Next: port the modes/ state machine (Spike 0.3 prep).")
    else:
        print("  R2: still no response even to Connect start.")
        print("  -> Handshake likely differs on POD Go. Next: get raw modes/ source for")
        print("     a faithful full port, or Spike 0.5 (capture real POD Go Edit traffic).")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
