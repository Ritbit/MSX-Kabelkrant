#!/usr/bin/env python3
"""Generate test-only MSX BASIC init and clock probe; never alter released BASIC.

Run after KBLINIT's C: disk copy, before standard LOOP.SYS. The test program
moves the *emulated RTC* to 23:59:50 and waits for midnight, writes a proof
to disposable A:, records FRE(0), and chains to the original broadcast loop.
"""
from pathlib import Path
import argparse
from msx_basic_ascii import encode_msx_basic, validate_msx_basic

CLOCK_PROBE = """10 DEFINT A-Z:SET TIME "23:59:50"
20 GET TIME B$:IF LEFT$(B$,2)<>"23" THEN 990
30 GET TIME A$
40 IF LEFT$(A$,2)="23" THEN 30
50 IF LEFT$(A$,2)<>"00" THEN 990
60 OPEN "A:CLOCK.OK" FOR OUTPUT AS #1
70 PRINT #1,"PASS RTC,";B$;",";A$
80 PRINT #1,"FRE0,";FRE(0)
90 CLOSE #1
100 RUN "LOOP.SYS"
990 PRINT "CLOCK TEST FAILED":END
"""

def make_initializer(original: bytes) -> bytes:
    if not original.endswith(b"\r\n\x1a"):
        raise ValueError("Expected MSX BASIC ASCII initializer")
    rows = {}
    for raw in original[:-1].decode("ascii").split("\r\n"):
        if not raw:
            continue
        n, body = raw.split(" ", 1)
        rows[int(n)] = body
    if not rows.get(230, "").startswith('READ PR$: IF PR$<>"END" THEN COPY "A:"+PR$ TO "C:"'):
        raise ValueError("Expected completed RAMdisk file-copy initializer")
    if rows.get(240) != 'RUN "LOOP.SYS"' or 235 in rows:
        raise ValueError("Unexpected post-copy original flow")
    rows[235] = 'RUN "A:CLOCKCHK.BAS"'
    result = encode_msx_basic(("\n".join(f"{n} {rows[n]}" for n in sorted(rows))+"\n").encode("ascii"))
    validate_msx_basic(result)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("initializer", type=Path)
    parser.add_argument("clock_basic", type=Path)
    args = parser.parse_args()
    args.initializer.parent.mkdir(parents=True, exist_ok=True)
    args.clock_basic.parent.mkdir(parents=True, exist_ok=True)
    args.initializer.write_bytes(make_initializer(args.source.read_bytes()))
    data = encode_msx_basic(CLOCK_PROBE.encode("ascii"))
    validate_msx_basic(data)
    args.clock_basic.write_bytes(data)
    print(f"Clock rollover: {len(data)} MSX BASIC bytes; original KBLINIT unmodified")

if __name__=="__main__":
    main()
