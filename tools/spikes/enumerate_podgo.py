"""Spike 0.1 — POD Go USB enumeration (READ-ONLY).

Feasibility probe for the POD Go USB-control MCP server (see
EXECPLAN-podgo-mcp-usb.md, Spike 0.1). Answers risk R1: does the POD Go expose a
vendor-specific control interface (like the HX Stomp's interface 0), and what are
its endpoints?

This script is strictly passive: it reads USB *descriptors* only. It never claims
an interface, sets a configuration, or writes a single byte to the device, so it
cannot change device state or interfere with POD Go Edit. String-descriptor reads
(manufacturer/product/serial) do briefly open the device for a control-IN transfer;
those are wrapped in try/except and skipped if the OS/permissions disallow them.

Prereqs:  brew install libusb  &&  pip install pyusb
Run:      python3 tools/spikes/enumerate_podgo.py
"""
import sys

LINE6_VID = 0x0E41  # Line 6, Inc. (shared across POD/Helix/HX family)

# USB transfer-type codes -> label (bmAttributes & 0x3)
XFER = {0: "control", 1: "iso", 2: "bulk", 3: "interrupt"}
# A few USB base-class codes we expect to see on this device.
CLASS = {0x00: "(per-interface)", 0x01: "audio", 0x03: "HID",
         0xFF: "vendor-specific"}


def dir_label(addr):
    return "IN " if addr & 0x80 else "OUT"


def describe_endpoint(ep):
    xfer = XFER.get(ep.bmAttributes & 0x3, "?")
    return (f"      ep 0x{ep.bEndpointAddress:02x} {dir_label(ep.bEndpointAddress)}"
            f"  {xfer:<9} maxpkt={ep.wMaxPacketSize}")


def try_string(dev, index):
    """Best-effort string-descriptor read; returns '' if unavailable."""
    if not index:
        return ""
    try:
        import usb.util
        return usb.util.get_string(dev, index) or ""
    except Exception as e:  # noqa: BLE001 - any failure is non-fatal here
        return f"<unreadable: {type(e).__name__}>"


def describe_device(dev):
    """Print the full descriptor tree for one device. Returns True if any
    vendor-specific (class 0xFF) interface with bulk endpoints was found."""
    print(f"\nDevice  {dev.idVendor:04x}:{dev.idProduct:04x}  "
          f"(bus {dev.bus}, addr {dev.address})")
    print(f"  Manufacturer : {try_string(dev, dev.iManufacturer)}")
    print(f"  Product      : {try_string(dev, dev.iProduct)}")
    print(f"  Serial       : {try_string(dev, dev.iSerialNumber)}")
    print(f"  Device class : 0x{dev.bDeviceClass:02x} "
          f"{CLASS.get(dev.bDeviceClass, '')}")

    found_vendor_bulk = False
    for cfg in dev:
        print(f"  Configuration {cfg.bConfigurationValue} "
              f"({cfg.bNumInterfaces} interfaces)")
        for intf in cfg:
            cls = intf.bInterfaceClass
            print(f"    Interface {intf.bInterfaceNumber} "
                  f"alt {intf.bAlternateSetting}  "
                  f"class 0x{cls:02x} {CLASS.get(cls, '')}")
            has_bulk = False
            for ep in intf:
                print(describe_endpoint(ep))
                if (ep.bmAttributes & 0x3) == 2:  # bulk
                    has_bulk = True
            if cls == 0xFF and has_bulk:
                found_vendor_bulk = True
    return found_vendor_bulk


def main():
    try:
        import usb.core
    except ImportError:
        print("ERROR: pyusb not installed.  ->  pip install pyusb", file=sys.stderr)
        return 2

    try:
        devices = list(usb.core.find(find_all=True, idVendor=LINE6_VID))
    except usb.core.NoBackendError:
        print("ERROR: no USB backend (libusb) found.  ->  brew install libusb",
              file=sys.stderr)
        return 2

    if not devices:
        print(f"No Line 6 device (VID {LINE6_VID:04x}) found.")
        print("Checklist: POD Go powered on & USB-connected, POD Go Edit CLOSED.")
        print("\nAll USB devices currently visible (VID:PID):")
        for d in usb.core.find(find_all=True):
            print(f"  {d.idVendor:04x}:{d.idProduct:04x}")
        return 1

    gate_pass = False
    for dev in devices:
        if describe_device(dev):
            gate_pass = True

    print("\n" + "=" * 60)
    print("SPIKE 0.1 GATE (R1): vendor-specific control interface present?")
    if gate_pass:
        print("  RESULT: YES — found a class 0xFF interface with bulk endpoints.")
        print("  -> Proceed to Spike 0.2 (passive connect + dump 0x81).")
    else:
        print("  RESULT: NO — no vendor-specific bulk interface seen.")
        print("  -> Control likely MIDI-only; consider fallback path C.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
