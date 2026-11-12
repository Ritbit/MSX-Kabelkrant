#!/usr/bin/env python3
"""Build MSX BASIC weekday proof on disposable disk (no production modifications).

The BASIC expression comes literally from src/LOOP.SYS line 1330; test cases
and expected weekday codes come independently from Python's datetime.date.
"""
import argparse
from datetime import date
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from msx_basic_ascii import encode_msx_basic, validate_msx_basic

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "LOOP.SYS"

YEARS = (1990, 1992, 1999, 2000, 2001, 2004, 2024, 2025, 2026,
         2028, 2040, 2050, 2088, 2089)
MONTHS = (1, 2, 3, 11, 12)


def make_cases():
    dates = set()
    for y in YEARS:
        for m in MONTHS:
            for d in (1, 13, 28):
                dates.add(date(y, m, d))
    for y in (1992, 2000, 2004, 2024, 2028, 2040, 2088):
        dates.add(date(y, 2, 29))
    return sorted(dates)


def build_test() -> tuple[bytes, int]:
    lines = SOURCE.read_text(encoding="utf-8", errors="replace").splitlines()
    formula = [s for s in lines if re.match(r"^1330 DG=", s)]
    months = [s for s in lines if s.startswith("1090 DATA ")]
    if len(formula) != 1 or len(months) != 1:
        raise ValueError("Missing date formula or month offset table")
    from test_weekday import EXPECTED, MONTH_OFFSETS
    if formula[0] != EXPECTED:
        raise ValueError("Unapproved or mismatched weekday source formula")
    if months[0] != "1090 DATA " + ",".join(map(str, MONTH_OFFSETS)):
        raise ValueError("Month table changed")
    cases = make_cases()
    p = {
        10: "DEFINT A-Z",
        20: "DIM C(12)",
        30: "RESTORE 1000:FOR M=1 TO 12:READ C(M):NEXT",
        40: "RESTORE 1100",
        50: f"FOR I=1 TO {len(cases)}",
        60: "READ YR,M,D,EX",
        70: 'Y=YR MOD 100:JA$="19":IF YR>=2000 THEN JA$="20"',
        80: formula[0].split(" ", 1)[1],
        90: 'IF DG<>EX THEN PRINT "BAD WEEKDAY";YR;M;D;DG;EX:END',
        100: "NEXT I",
        110: 'OPEN "A:WDAY.OK" FOR OUTPUT AS #1',
        120: f'PRINT #1,"PASS {len(cases)} WEEKDAYS"',
        130: "CLOSE #1",
        140: 'RUN "LOOP.SYS"',
        1000: "DATA " + ",".join(map(str, MONTH_OFFSETS)),
    }
    pairs = [(v.year, v.month, v.day, (v.weekday() + 2) % 7)
             for v in cases]
    for index in range(0, len(pairs), 5):
        number = 1100 + (index // 5) * 10
        p[number] = "DATA " + ",".join(
            str(item) for record in pairs[index:index + 5] for item in record
        )
    basic = "\n".join(f"{num} {p[num]}" for num in sorted(p)) + "\n"
    result = encode_msx_basic(basic.encode("ascii"))
    validate_msx_basic(result)
    return result, len(cases)


def build_initializer(original: bytes) -> bytes:
    if not original.endswith(b"\r\n\x1a"):
        raise ValueError("Expected MSX ASCII BASIC initializer")
    lines = {}
    for line in original[:-1].decode("ascii").split("\r\n"):
        if not line:
            continue
        n, body = line.split(" ", 1)
        lines[int(n)] = body
    if not lines.get(230, "").startswith(
        'READ PR$: IF PR$<>"END" THEN COPY "A:"+PR$ TO "C:"'
    ) or lines.get(240) != 'RUN "LOOP.SYS"' or 235 in lines:
        raise ValueError("Expected original KBLINIT RAMdisk copy/LOOP handoff")
    lines[235] = 'RUN "A:WDAY.BAS"'
    out = encode_msx_basic(
        ("\n".join(f"{num} {lines[num]}" for num in sorted(lines)) + "\n"
         ).encode("ascii")
    )
    validate_msx_basic(out)
    return out


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("source_init", type=Path)
    arg.add_argument("test_init", type=Path)
    arg.add_argument("test_basic", type=Path)
    args = arg.parse_args()
    test, count = build_test()
    init = build_initializer(args.source_init.read_bytes())
    args.test_init.parent.mkdir(parents=True, exist_ok=True)
    args.test_basic.parent.mkdir(parents=True, exist_ok=True)
    args.test_init.write_bytes(init)
    args.test_basic.write_bytes(test)
    print(f"MSX BASIC weekday test: {count} dates, {len(test)} bytes")


if __name__ == "__main__":
    main()
