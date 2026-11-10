#!/usr/bin/env python3
"""Generate opt-in rectangle-enabled 14-wipe resident code.

Never replaces the accepted full/lean builds. The one-argument syntax
is delegated unchanged to WipeSharedRun.
"""
from pathlib import Path
import argparse
from make_wipe_integration import make_asm

ROOT=Path(__file__).resolve().parents[2]

PARSER="""WipeCommand:
    xor a
    ld (RectUsed),a
    call GetChar
    cp '('
    jp nz,SyntaxError
    inc hl
    ld ix,GETBYT
    call CALBAS
    ld (WipeRequested),a
    call GetChar
    cp ')'
    jr z,.closed
    cp ','
    jp nz,SyntaxError
    ld a,(WipeRequested)
    cp 1
    jp nz,IllegalFunction
    ; Four FRMQNT signed 16-bit coordinates; each comma required.
    call ExpectComma
    ld ix,FRMQNT
    call CALBAS
    ld (RectX1),de
    call ExpectComma
    ld ix,FRMQNT
    call CALBAS
    ld (RectY1),de
    call ExpectComma
    ld ix,FRMQNT
    call CALBAS
    ld (RectX2),de
    call ExpectComma
    ld ix,FRMQNT
    call CALBAS
    ld (RectY2),de
    call GetChar
    cp ')'
    jp nz,SyntaxError
    ld a,1
    ld (RectUsed),a
.closed:
    inc hl
    ld a,(WipeRequested)
    cp 1
    jp c,IllegalFunction
    cp 15
    jp nc,IllegalFunction
    ld a,(RectUsed)
    or a
    jr z,.legacy
    call WipeRectValidate
    jp c,IllegalFunction
    push hl
    call WipeRectRun
    pop hl
    ret
.legacy:
    ld a,(WipeRequested)
    push hl
    call WipeSharedRun
    pop hl
    ret

WipeRequested: db 0
RectUsed: db 0

GetChar:
"""

def make_rectangle_asm(baseline: str)->str:
    # Starting with the full 14-wipe variant preserves the released
    # extension setup and all previous 14 modes.
    full=make_asm(baseline,full=True)
    start=full.index("WipeCommand:\n")
    stop=full.index("GetChar:\n",start)+len("GetChar:\n")
    if full[start:stop].count("WipeRequested: db 0")!=1:
        raise ValueError("Unexpected wipe parser")
    full=full[:start]+PARSER+full[stop:]
    marker="    INCLUDE 'wipe_shared.asm'\nEmbeddedFonts:"
    if full.count(marker)!=1:
        raise ValueError("Shared engine insertion point changed")
    full=full.replace(marker,"    INCLUDE 'wipe_shared.asm'\n    INCLUDE 'wipe_rect_one.asm'\nEmbeddedFonts:")
    return full

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--output",type=Path,required=True)
    opts=arg.parse_args()
    from make_wipe_integration import SOURCE
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(make_rectangle_asm(SOURCE.read_text()))
    print(f"Generated rectangle-enabled 14-wipe extension: {opts.output}")

if __name__=="__main__":
    main()
