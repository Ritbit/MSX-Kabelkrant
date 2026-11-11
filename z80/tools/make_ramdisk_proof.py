#!/usr/bin/env python3
"""Build an emulator-only C: test which writes PASS proof to its A: test disk.

Never modify the original CTEST.BAS or any accepted alpha image.
The marker is written only after all C: writes, reads, compares and
deletion completed successfully. Copy DSK to a temporary location
before running openMSX because this intentionally writes to A:.
"""
from pathlib import Path
import sys
from msx_basic_ascii import encode_msx_basic,validate_msx_basic

def generate(basic_text: str)->bytes:
    rows={}
    for line in basic_text.splitlines():
        n,body=line.split(" ",1)
        n=int(n)
        if n in rows: raise ValueError(f"Repeated line {n}")
        rows[n]=body
    if rows.get(210)!='KILL F$' or rows.get(220)!='PRINT "PASS: WRITE/READ/DELETE ON C:"':
        raise ValueError("Diagnostic changed; refusing to patch")
    if any(i in rows for i in (212,214,216,218)):
        raise ValueError("Line numbers reserved for marker are in use")
    rows.update({
        212:'OPEN "A:KBLPASS.OK" FOR OUTPUT AS #1',
        214:'PRINT #1,"PASS C: RW DELETE"',
        216:'CLOSE #1',
        218:'PRINT "C: VERIFIED: DISK PROOF SAVED"',
    })
    out=encode_msx_basic(("\n".join(f"{n} {rows[n]}" for n in sorted(rows))+"\n").encode("ascii"))
    validate_msx_basic(out)
    return out

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: make_ramdisk_proof.py CTEST-SOURCE output")
    inp,out=map(Path,sys.argv[1:])
    data=generate(inp.read_text())
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(data)
    print(f"Generated MSX C: read/write/delete proof program: {len(data)} bytes")
