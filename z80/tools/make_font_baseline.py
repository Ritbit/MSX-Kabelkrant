#!/usr/bin/env python3
"""Generate four-font baseline from original LOOP.SYS using KRANT3.SC7.

KRANT4.SC7 omits font 2 and moves font 4 from Y=160/174 to 134/149.
KRANT3.SC7 contains all four fonts, but the original routine clears its
font-4 glyphs at Y>=164. We preserve every original draw/copy command,
only omit the destructive preparation for fonts 2/3/4 when K=15 (white).
KRANT3 font 3 has its original Y positions (107,124,142).
No original source or graphical assets are modified.
"""
import argparse
from pathlib import Path
import re
from msx_basic_ascii import encode_msx_basic, validate_msx_basic

HEADER = [
    "10 ' ORIGINAL LOOP.SYS BASIC RENDERER REFERENCE - NO Z80 TEXT",
    "20 DEFINT A-W,Z:DEFDBL X,Y",
    "30 SCREEN 7:COLOR 15,0,0:COLOR=(0,1,1,3):CLS",
    '40 SETPAGE 0,1:CLS:BLOAD "KRANT3.SC7",S:COLOR=RESTORE:SETPAGE 0,0:CLS',
    "50 DIM X(4,110),L1(4),L2(4),L3(4),Y1(4),Y2(4),Y3(4),H(4)",
    '60 COPY "X.DAT" TO X',
    "70 GOSUB 2700:K=15",
    '80 A$="ABCDEFGHIJKLMNOPQRSTUVWXYZ"',
    "90 LT=4:X=20:Y=5:GOSUB 2500",
    "100 LT=2:X=20:Y=55:GOSUB 2500",
    "110 LT=3:X=20:Y=105:GOSUB 2500",
    "120 LT=1:X=20:Y=155:GOSUB 2500",
    "130 GOTO 130",
]

# Minimal white-only demo changes to prevent corrupting source pixels.
# Font 1 uses the same source->scratch COPY as the original BASIC routine.
REFERENCE_OVERRIDES = {
    2530: "2530 INTERVAL OFF:SETPAGE 0,1",
    2540: "2540 IF LT=1 THEN LINE(0,164)-(512,212),0,BF:COPY(0,51)-(512,80) TO (0,164)",
    2550: "2550 SETPAGE 0,0:INTERVAL ON",
    2675: "2675 'NO SCRATCH COLOUR RESTORE IN WHITE-ONLY TEST",
    2830: "2830 DATA 43,83,96,107,124,142,16",
}

def extract_original(source: str) -> list[str]:
    selected = []
    for line in source.splitlines():
        m = re.match(r"^([0-9]+)(?:[ \t]|$)", line)
        if not m:
            continue
        num = int(m.group(1))
        if (2500 <= num <= 2690) or (2700 <= num <= 2840):
            selected.append(REFERENCE_OVERRIDES.get(num, line))
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
    print(f"{a.output}: {len(output)} bytes, four fonts from original BASIC with documented scratch fixes")
