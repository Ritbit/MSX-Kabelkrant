#!/usr/bin/env python3
"""Generate a clean 14-Z80-wipe LOOP and a same-machine BASIC/Z80 benchmark.

No released BASIC files are edited. The benchmark preserves the exact
original BASIC effect bodies, except replacing GOTO 3380 with RETURN
to execute each effect as a timed subroutine. Wipe 14 retains its
historical misaligned geometry in the BASIC control.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

from msx_basic_ascii import encode_msx_basic, validate_msx_basic

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "LOOP.SYS"
ORIGINAL_EFFECT_LINES = tuple(range(3240, 3380, 10))


def split_program(program: str) -> dict[int, str]:
    result: dict[int, str] = {}
    for line in program.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"(\d+) (.*)", line)
        if not match:
            raise ValueError(f"Unnumbered BASIC line: {line!r}")
        number = int(match.group(1))
        if number in result:
            raise ValueError(f"Duplicate BASIC line {number}")
        result[number] = match.group(2)
    return result


def clean_loop(loop: str) -> str:
    source = split_program(loop)
    expected = "IF A>=1 AND A<=14 THEN CALL WIPE(A):GOTO 3380"
    if source.get(3140) != expected:
        raise ValueError("Not the validated full 14-wipe integration LOOP")
    if not source.get(3141, "").startswith("ON A GOTO 3240,3250,"):
        raise ValueError("Original fallback 3141 not present")
    if not all("GOTO 3380" in source.get(n, "") for n in ORIGINAL_EFFECT_LINES):
        raise ValueError("One or more original BASIC wipe bodies missing")
    if source.get(3125) is None or source.get(3130) is None or source.get(3380) is None:
        raise ValueError("Wipe prologue or interrupt restoration missing")
    source[3140] = "IF A<1 OR A>14 THEN A=1"
    source[3141] = "CALL WIPE(A):GOTO 3380"
    # The original ON A GOTO falls through to the first FOR loop for
    # indices 0 and 15; retain that behaviour by mapping them to #1.
    for number in list(source):
        if 3150 <= number <= 3370:
            del source[number]
    if any(n in source for n in ORIGINAL_EFFECT_LINES):
        raise AssertionError("Obsolete BASIC wipes still in clean LOOP")
    if source[3380] != "INTERVAL ON" or source[3390] != "RETURN":
        raise ValueError("Wipe exit changed unexpectedly")
    return "\n".join(f"{n} {source[n]}" for n in sorted(source)) + "\n"


def make_benchmark(original: str) -> str:
    source = split_program(original)
    for number in ORIGINAL_EFFECT_LINES:
        if source.get(number) is None:
            raise ValueError(f"Missing original BASIC wipe #{number}")
    dispatch = ",".join(str(1000 + 10 * i) for i in range(14))
    lines = [
        '10 REM KBL A/B WIPE TIMING - ORIG BASIC VS SHARED Z80',
        '20 DEFINT A-Z:DEFDBL X,Y',
        '30 DIM B(14),Z(14)',
        '35 F#=FRE(0)',
        '40 INTERVAL OFF:SCREEN 7:COLOR 15,0,0',
        '50 FOR I=1 TO 14',
        '60 LINE(0,50)-(511,211),14,BF',
        '70 T#=TIME',
        f'80 ON I GOSUB {dispatch}',
        '90 U#=TIME:D#=U#-T#:IF D#<0 THEN D#=D#+65536',
        '100 B(I)=D#',
        '110 LINE(0,50)-(511,211),14,BF',
        '120 T#=TIME',
        '125 FOR J=1 TO 25',
        '130 CALL WIPE(I)',
        '135 NEXT J',
        '140 U#=TIME:D#=U#-T#:IF D#<0 THEN D#=D#+65536',
        '150 Z(I)=D#',
        '160 NEXT I',
        '170 SCREEN 0:WIDTH 80:COLOR 15,4,4:CLS',
        '180 PRINT "KABELKRANT BASIC / Z80 WIPE BENCHMARK"',
        '190 PRINT "50Hz/60Hz jiffies: smaller = faster"',
        '200 PRINT "Effect BASIC   Z80/25calls  avgZ80/BASIC"',
        '210 FOR I=1 TO 14',
        '220 PRINT USING "##";I;',
        '230 PRINT USING "    #####   #####";B(I);Z(I);',
        '240 IF B(I)=0 THEN PRINT "    n/a" ELSE PRINT USING "     ###.##";Z(I)/(25*B(I))',
        '250 NEXT I',
        '260 PRINT "Wipe 14 BASIC geometry differs (known bug)."',
        '270 PRINT "Z80 animation includes frame pacing."',
        '280 PRINT "Record results; RESET to restart newspaper."',
        '281 OPEN "A:BENCHRES.CSV" FOR OUTPUT AS #1',
        '282 PRINT #1,"effect,basic_jiffies,z80_25calls_jiffies"',
        '283 FOR I=1 TO 14:PRINT #1,STR$(I)+","+STR$(B(I))+","+STR$(Z(I)):NEXT I',
        '284 PRINT #1,"FRE0,";F#',
        '285 CLOSE #1',
        '290 END',
    ]
    for index, original_number in enumerate(ORIGINAL_EFFECT_LINES):
        body = source[original_number]
        suffix = ": GOTO 3380"
        if not body.endswith(suffix):
            raise ValueError(f"Unexpected BASIC wipe tail at {original_number}")
        converted = body[: -len(suffix)] + ": RETURN"
        lines.append(f"{1000 + index*10} {converted}")
    result = "\n".join(lines) + "\n"
    validate_msx_basic(encode_msx_basic(result.encode("ascii")))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-loop", type=Path, required=True)
    parser.add_argument("--clean-loop", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    args = parser.parse_args()
    old = args.full_loop.read_bytes()
    if not old.endswith(b"\x1a"):
        raise ValueError("Full integration LOOP not in ASCII MSX BASIC format")
    old_text = old[:-1].decode("ascii").replace("\r\n", "\n")
    clean_text = clean_loop(old_text)
    benchmark_text = make_benchmark(SOURCE.read_text(encoding="utf-8"))
    clean = encode_msx_basic(clean_text.encode("ascii"))
    benchmark = encode_msx_basic(benchmark_text.encode("ascii"))
    for path, payload in ((args.clean_loop, clean),(args.benchmark,benchmark)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    print(f"Clean LOOP ASCII-disk delta: {len(clean)-len(old):+d} bytes "
          f"({len(old)} -> {len(clean)}); this is NOT tokenized BASIC RAM")
    print(f"Benchmark BASIC: {len(benchmark)} disk bytes, 14 BASIC timings + 25 Z80 calls per effect")


if __name__ == "__main__":
    main()
