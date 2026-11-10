#!/usr/bin/env python3
"""Experimental single-BLOAD RAMDISK+TEXT image for MSX2 Kabelkrant.

Preserve original RAMDISK.BIN bytes from C000..C7EF *exactly*. Append
the separately assembled TEXT module at C804, with the loader still
executing the original C000 entry point. After the historic warm start,
KBLINIT can explicitly invoke C806 to install CALL TEXT (if the payload
survives the mapper/slot restart).

This intentionally does NOT put TEXT inside RAMdisk's 46F4..7FFE
zero-filled storage. The combined image is unproven at runtime.
"""
from pathlib import Path
import argparse
import struct

RAM_START = 0xC000
RAM_END = 0xC7EF
TEXT_START = 0xC804
TEXT_ENTRY = 0xC806
TEXT_LIMIT = 0xD804


def parse_bload(data: bytes) -> tuple[int, int, int, bytes]:
    if len(data) < 8 or data[0] != 0xFE:
        raise ValueError("not an MSX BLOAD binary")
    start, end, entry = struct.unpack_from("<HHH", data, 1)
    payload = data[7:]
    if end < start or end - start + 1 != len(payload):
        raise ValueError("invalid BLOAD start/end/payload length")
    return start, end, entry, payload


def combine(ramdisk: bytes, text: bytes) -> bytes:
    rs, re, rx, rp = parse_bload(ramdisk)
    ts, te, tx, tp = parse_bload(text)
    if (rs, re, rx) != (RAM_START, RAM_END, RAM_START):
        raise ValueError("unexpected RAMdisk memory layout or entry")
    if ts != TEXT_START or tx != TEXT_ENTRY or te + 1 > TEXT_LIMIT:
        raise ValueError("unexpected Z80 TEXT load range")
    gap = TEXT_START - (re + 1)
    if gap < 0:
        raise ValueError("TEXT overlaps historical RAMdisk installer")
    merged = rp + bytes(gap) + tp
    end = RAM_START + len(merged) - 1
    assert merged[:len(rp)] == rp
    assert merged[TEXT_START - RAM_START:] == tp
    return b"\xfe" + struct.pack("<HHH", RAM_START, end, RAM_START) + merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ramdisk", type=Path, default=Path("src/RAMDISK.BIN"))
    ap.add_argument("--text", type=Path, default=Path("z80/build/KBLTXT.BIN"))
    ap.add_argument("--output", type=Path, default=Path("z80/build/KBLRAMTX.BIN"))
    args = ap.parse_args()
    merged = combine(args.ramdisk.read_bytes(), args.text.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(merged)
    _, end, entry, _ = parse_bload(merged)
    print(f"EXPERIMENTAL combined loader: {len(merged)} bytes, C000..{end:04X}, entry {entry:04X}")


if __name__ == "__main__":
    main()
