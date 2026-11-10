#!/usr/bin/env python3
"""Generate a separate 14-page-wipes + dedicated two-title-bars-wipe alpha.

Existing user-accepted 14-wipe resident image is not modified.
Title wipe is selected by CALL WIPE(15) only inside generated LOOP.
"""
from pathlib import Path
import argparse
import sys

from make_wipe_integration import make_asm, SOURCE
from make_wipe_benchmark import clean_loop, split_program
from msx_basic_ascii import encode_msx_basic, validate_msx_basic


def title_asm(original: str) -> str:
    full = make_asm(original, full=True)
    if full.count("WIPE_TITLE EQU 0") != 1:
        raise ValueError("Missing opt-in feature gate")
    full = full.replace("WIPE_TITLE EQU 0", "WIPE_TITLE EQU 1", 1)
    old = "    cp 15\n    jp nc,IllegalFunction"
    if full.count(old) != 1:
        raise ValueError("Missing original fourteen-effect range guard")
    return full.replace(old, "    cp 16\n    jp nc,IllegalFunction", 1)


def title_loop(original_lean: str) -> str:
    lines = split_program(original_lean)
    expected = {
        3430: "INTERVAL OFF",
        3440: "FOR A=0 TO 420 STEP 10",
        3450: "   COPY(0,0)-(10,48),0 TO (A,0),0",
        3460: "NEXT A",
        3470: "INTERVAL ON",
        3480: "RETURN",
    }
    for num, body in expected.items():
        # Repository preserves leading spaces on the COPY line.
        if lines.get(num, "").strip() != body.strip():
            raise ValueError(f"Unexpected old title-wipe line {num}: {lines.get(num)!r}")
    lines[3430] = "INTERVAL OFF:CALL WIPE(15):INTERVAL ON"
    for num in (3440, 3450, 3460, 3470):
        del lines[num]
    assert lines[3480] == "RETURN"
    assert lines[3141] == "CALL WIPE(A):GOTO 3380"
    return "\n".join(f"{n} {lines[n]}" for n in sorted(lines)) + "\n"


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--lean-loop", type=Path, required=True)
    parser.add_argument("--output-loop", type=Path, required=True)
    args=parser.parse_args()
    data=args.lean_loop.read_bytes()
    if not data.endswith(b"\r\n\x1a"):
        raise ValueError("Expected encoded MSX BASIC ASCII input")
    original=data[:-1].decode("ascii").replace("\r\n","\n")
    loop=encode_msx_basic(title_loop(original).encode("ascii"))
    validate_msx_basic(loop)
    args.asm.parent.mkdir(parents=True, exist_ok=True)
    args.output_loop.parent.mkdir(parents=True, exist_ok=True)
    args.asm.write_text(title_asm(SOURCE.read_text()))
    args.output_loop.write_bytes(loop)
    print(f"Title-only special wipe generated; LOOP.SYS {len(data)} -> {len(loop)} bytes")


if __name__=="__main__":
    main()
