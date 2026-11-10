#!/usr/bin/env python3
"""Audit the page-3 combined TEXT/wipe memory budget from real BLOAD bytes.

This tool is intentionally *read-only*. It must not relocate the original
RAMdisk, increase HIMEM, or silently concatenate independent wipe kernels.
"""
from pathlib import Path
import struct

START=0xC804
LIMIT=0xD804  # exclusive; onefile loader's current verified upper bound

def bload(path):
    data=Path(path).read_bytes()
    if len(data)<8 or data[0]!=0xFE:
        raise ValueError(f"{path}: invalid MSX BLOAD header")
    start,end,entry=struct.unpack_from("<HHH",data,1)
    if end-start+1!=len(data)-7:
        raise ValueError(f"{path}: payload length mismatch")
    return start,end,entry,len(data)-7

def main():
    root=Path(__file__).resolve().parents[1]/"build"
    text=root/"KBLTXT.BIN"
    start,end,entry,used=bload(text)
    if (start,entry)!=(START,START+2):
        raise ValueError("TEXT entry moved; break with RAMdisk risk")
    remaining=LIMIT-(end+1)
    if remaining<0:
        raise ValueError(f"TEXT spills beyond current safe limit: {end:04X}")
    print(f"TEXT at {start:04X}..{end:04X}: {used} bytes, "
          f"remaining in current 4KiB slot: {remaining} bytes")
    sizes=[]
    for n in range(1,15):
        p=root/f"WIPE{n}.BIN"
        wstart,wend,wentry,length=bload(p)
        if (wstart,wentry)!=(START,START+2):
            raise ValueError(f"WIPE{n}: unexpected standalone entry")
        sizes.append(length)
    print("Individual standalone wipe payloads:")
    for n,sz in enumerate(sizes,1):
        print(f"  {n:02}: {sz:5} bytes")
    print(f"Naive sum (TEXT + all standalones): {used+sum(sizes)} bytes "
          f"against {LIMIT-START} bytes")
    print("Standalone binaries each contain their own command engine and "
          "data; this is NOT a prediction of a deduplicated common engine.")
    if used+sum(sizes)>LIMIT-START:
        print("A naive append cannot fit. Shared engine, compact geometry "
              "tables and/or a separately validated memory region are required.")


if __name__=="__main__":
    main()
