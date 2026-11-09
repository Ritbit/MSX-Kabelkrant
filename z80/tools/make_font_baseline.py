#!/usr/bin/env python3
"""Generate baseline font demo using byte-for-byte original BASIC renderer.

Extract the original graphics and font-data routines from src/LOOP.SYS,
so reference output is *not* a reinterpretation of their behavior.
"""
import argparse
from pathlib import Path
import re
from msx_basic_ascii import encode_msx_basic, validate_msx_basic

HEADER = [
    "10 ' ORIGINAL LOOP.SYS BASIC RENDERER REFERENCE - NO Z80 TEXT",
    "20 DEFINT A-W,Z:DEFDBL X,Y",
    "30 SCREEN 7:COLOR 15,0,0:COLOR=(0,1,1,3):CLS",
    '40 SETPAGE 0,1:CLS:BLOAD "KRANT4.SC7",S:COLOR=RESTORE:SETPAGE 0,0:CLS',
    "50 DIM X(4,110),L1(4),L2(4),L3(4),Y1(4),Y2(4),Y3(4),H(4)",
    '60 COPY "X.DAT" TO X',
    "70 GOSUB 2700:K=15",
    '80 A$="ABCDEFGHIJKLMNOPQRSTUVWXYZ"',
    "90 LT=1:X=20:Y=25:GOSUB 2500",
    "100 LT=2:X=20:Y=75:GOSUB 2500",
    "110 LT=3:X=20:Y=125:GOSUB 2500",
    "120 LT=4:X=20:Y=175:GOSUB 2500",
    "130 GOTO 130",
]

def extract_original(source: str) -> list[str]:
    selected = []
    for line in source.splitlines():
        m = re.match(r"^([0-9]+)(?:[ \t]|$)", line)
        if not m:
            continue
        num = int(m.group(1))
        if (2500 <= num <= 2690) or (2700 <= num <= 2840):
            selected.append(line)
    ids = {int(line.split()[0]) for line in selected}
    required = {2530,2540,2550,2555,2560,2580,2590,2600,2610,2620,2630,2640,2650,2660,2670,2675,2680,2690,2730,2740,2750,2760,2770,2810,2820,2830,2840}
    if not required.issubset(ids):
        raise ValueError(f"missing original BASIC lines: {sorted(required-ids)}")
    return selected

def make_program(source: str) -> bytes:
    basic = ("\n".join(HEADER + extract_original(source)) + "\n").encode("ascii")
    result = encode_msx_basic(basic)
    validate_msx_basic(result)
    return result

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=Path("src/LOOP.SYS"))
    p.add_argument("--output",type=Path,default=Path("z80/build/FONTBAS.BAS"))
    a=p.parse_args()
    output=make_program(a.source.read_text(encoding="latin-1"))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(output)
    print(f"{a.output}: {len(output)} bytes, four fonts, original BASIC renderer")
