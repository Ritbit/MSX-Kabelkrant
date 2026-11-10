#!/usr/bin/env python3
"""Re-use validated boot initializer to auto-run RECTDEMO.BAS after Z80 install."""
from pathlib import Path
import sys
from make_auto_wipe_benchmark import generate

def rectangle_init(original: bytes)->bytes:
    out=generate(original)
    old=b'198 RUN "A:BENCHW.BAS"'
    if out.count(old)!=1:
        raise ValueError("Unexpected auto-run initializer")
    return out.replace(old,b'198 RUN "A:RECTDEMO.BAS"')

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: make_rect_demo_init.py INPUT OUTPUT")
    source,target=map(Path,sys.argv[1:])
    result=rectangle_init(source.read_bytes())
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(result)
    print(f"Generated dedicated rectangle demo initializer ({len(result)} bytes)")
