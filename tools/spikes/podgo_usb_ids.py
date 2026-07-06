"""Candidate usb_id <-> @model bridge, decoded from POD Go Edit's PodGoModelDefs.bin.

PodGoModelDefs.bin is a MessagePack array of 574 model definitions (same data as the
.models JSON). It carries NO explicit device id, so the HYPOTHESIS is that a model's
INDEX in this array IS the integer id the device/USB protocol reports (usb_id). This is
UNVERIFIED pending a hardware calibration capture (see build_calibration.py).

Requires: pip install msgpack
"""
import os

DEFAULT_BIN = ("/Applications/Line6/POD Go Edit.app/Contents/Resources/"
               "PodGoModelDefs.bin")


def _clean(s):
    return s.rstrip("\x00") if isinstance(s, str) else s


class UsbIdMap:
    def __init__(self, path=DEFAULT_BIN):
        import msgpack
        d = msgpack.unpack(open(path, "rb"), raw=False, strict_map_key=False)
        self.by_index = []          # index (candidate usb_id) -> symbolicID
        self.by_model = {}          # symbolicID (@model) -> index
        for i, m in enumerate(d):
            sid = next((_clean(v) for k, v in m.items()
                        if _clean(k) == "symbolicID"), None)
            self.by_index.append(sid)
            if sid:
                self.by_model[sid] = i

    def usb_id(self, model):
        """Candidate usb_id (array index) for an @model, or None."""
        return self.by_model.get(model)

    def model(self, usb_id):
        """@model at a given usb_id (array index), or None."""
        return self.by_index[usb_id] if 0 <= usb_id < len(self.by_index) else None


def load(path=DEFAULT_BIN):
    return UsbIdMap(path)


if __name__ == "__main__":
    import sys
    m = load()
    print(f"{len(m.by_index)} models in PodGoModelDefs.bin")
    for a in sys.argv[1:]:
        if a.isdigit():
            print(f"  usb_id {a} -> {m.model(int(a))}")
        else:
            print(f"  {a} -> candidate usb_id {m.usb_id(a)}")
