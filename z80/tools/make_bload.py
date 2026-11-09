#!/usr/bin/env python3
"""Wrap SjASMPlus raw E004h payload in an MSX BASIC BLOAD/R header."""
from pathlib import Path
import argparse
import struct

def convert(payload: bytes, load: int = 0xE004, entry: int = 0xE006) -> bytes:
    if not payload or load < 0xE004 or load + len(payload) > 0xF000:
        raise ValueError("unsafe BLOAD payload")
    return b"\xFE" + struct.pack("<HHH",load,load+len(payload)-1,entry) + payload

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("output",type=Path)
    a=ap.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(convert(a.input.read_bytes()))
    print(a.output,a.output.stat().st_size)
