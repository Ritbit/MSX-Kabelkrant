#!/usr/bin/env python3
"""Generate an *opt-in* onefile build with CALL WIPE(1..8).

The trusted BASIC v6.2b and normal Z80 TEXT source remain untouched.
Only the new demonstration disk uses this generated assembler source.
"""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "z80" / "asm" / "basic_text_demo.asm"


def once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"Expected exactly one marker: {old!r}, got {source.count(old)}")
    return source.replace(old, new, 1)


def make_asm(source: str, extra: bool = False, full: bool = False) -> str:
    extra = extra or full
    source = ('WIPE_EXTRA EQU 1\n' if extra else 'WIPE_EXTRA EQU 0\n') + ('WIPE_FULL EQU 1\n' if full else 'WIPE_FULL EQU 0\n') + source
    source = once(
        source,
        "    ld de,VerName\n    call CompareName\n    jr z,.ver",
        "    ld de,WipeName\n    call CompareName\n    jr z,.wipe\n"
        "    ld de,VerName\n    call CompareName\n    jr z,.ver",
    )
    source = once(
        source,
        ".ver:\n    pop hl\n    call VersionCommand",
        ".wipe:\n    pop hl\n    call WipeCommand\n    or a\n    ret\n"
        ".ver:\n    pop hl\n    call VersionCommand",
    )
    source = once(source, "VerName:  db 'KBLVER',0",
                  "VerName:  db 'KBLVER',0\nWipeName: db 'WIPE',0")
    source = once(
        source, "GetChar:\n",
        """WipeCommand:
    call GetChar
    cp '('
    jp nz,SyntaxError
    inc hl
    ld ix,GETBYT
    call CALBAS
    ld (WipeRequested),a
    call GetChar
    cp ')'
    jp nz,SyntaxError
    inc hl
    ld a,(WipeRequested)
    cp 1
    jp c,IllegalFunction
    cp 9
    jp nc,IllegalFunction
    push hl
    call WipeSharedRun
    pop hl
    ret

WipeRequested: db 0

GetChar:
""",
    )
    if extra:
        source = once(source, "    cp 9\n    jp nc,IllegalFunction",
                      "    cp 15\n    jp nc,IllegalFunction" if full else
                      "    cp 13\n    jp nc,IllegalFunction")
    source = once(source, "EmbeddedFonts:\n",
                  "    INCLUDE 'wipe_shared.asm'\nEmbeddedFonts:\n")
    return source


def make_loop(loop: str, extra: bool = False, full: bool = False) -> str:
    line = next((l for l in loop.splitlines() if l.startswith("3140 ")), None)
    if not line or "ON A GOTO 3240,3250," not in line:
        raise ValueError("Unexpected BASIC wipe dispatcher")
    if any(l.startswith("3141 ") for l in loop.splitlines()):
        raise ValueError("3141 already exists")
    return once(loop, line + "\n",
                ("3140 IF A>=1 AND A<=14 THEN CALL WIPE(A):GOTO 3380\n" if full
                 else "3140 IF A>=1 AND A<=12 THEN CALL WIPE(A):GOTO 3380\n" if extra
                 else "3140 IF A>=1 AND A<=8 THEN CALL WIPE(A):GOTO 3380\n")
                + "3141 " + line[5:] + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asm", type=Path,
                        default=ROOT/"z80"/"asm"/".generated_wipe_text.asm")
    parser.add_argument("--loop", type=Path,
                        default=ROOT/"z80"/"build"/"wipe_integration"/"LOOP.SYS")
    parser.add_argument("--extra", action="store_true", help="Build shared 1..12 wipe engine")
    parser.add_argument("--full", action="store_true", help="Build experimental shared 1..14 wipe engine")
    args = parser.parse_args()
    from make_full_z80_test import transform
    from msx_basic_ascii import encode_msx_basic, validate_msx_basic
    init = (ROOT/"src"/"KBLINIT.SYS").read_text(encoding="utf-8")
    loop = (ROOT/"src"/"LOOP.SYS").read_text(encoding="utf-8")
    _, textloop, _ = transform(init,loop,one_file=True)
    textloop=make_loop(textloop,extra=args.extra,full=args.full)
    encoded=encode_msx_basic(textloop.encode("ascii"))
    validate_msx_basic(encoded)
    args.asm.parent.mkdir(parents=True,exist_ok=True)
    args.loop.parent.mkdir(parents=True,exist_ok=True)
    args.asm.write_text(make_asm(SOURCE.read_text(),extra=args.extra,full=args.full))
    args.loop.write_bytes(encoded)
    print(f"Generated opt-in wipe1..{14 if args.full else 12 if args.extra else 8}: {args.asm}, {args.loop}")


if __name__=="__main__":
    main()
