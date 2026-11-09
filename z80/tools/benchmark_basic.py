#!/usr/bin/env python3
"""Reproducible original-vs-optimized BASIC renderer benchmark.

Uses the original LOOP.SYS from the v6.2 FAT12 floppy image and the
optimized LOOP.SYS on this branch. The two GOSUB routines run side-by-side
under identical font, colour and X settings. Times are MSX TIME jiffies.
"""
import argparse
import math
from pathlib import Path
import re
from msx_basic_ascii import encode_msx_basic, validate_msx_basic


def disk_file(image: bytes, filename: str) -> bytes:
    bps = int.from_bytes(image[11:13], "little")
    spc = image[13]
    reserved = int.from_bytes(image[14:16], "little")
    nfats = image[16]
    nroot = int.from_bytes(image[17:19], "little")
    spf = int.from_bytes(image[22:24], "little")
    if not (bps == 512 and spc > 0 and nfats == 2):
        raise ValueError("unexpected original FAT12 format")
    fat = image[reserved*bps:(reserved+spf)*bps]
    root = (reserved+nfats*spf)*bps
    data = root+math.ceil(nroot*32/bps)*bps
    stem, ext = filename.upper().split(".")
    key = (stem.ljust(8)+ext.ljust(3)).encode("ascii")
    for index in range(nroot):
        e = image[root+32*index:root+32*(index+1)]
        if e[0] == 0:
            break
        if e[:11] != key:
            continue
        cluster = int.from_bytes(e[26:28], "little")
        count = int.from_bytes(e[28:32], "little")
        content = bytearray()
        visited = set()
        while 2 <= cluster < 0xff8 and cluster not in visited:
            visited.add(cluster)
            start = data+(cluster-2)*bps*spc
            content += image[start:start+bps*spc]
            offset = cluster+cluster//2
            value = int.from_bytes(fat[offset:offset+2], "little")
            cluster = (value >> 4) if (cluster & 1) else value & 0xfff
        if len(content) < count:
            raise ValueError("corrupt FAT12 chain")
        return bytes(content[:count])
    raise FileNotFoundError(filename)


def lines_in(source: str, start: int, end: int) -> list[str]:
    result = []
    for line in source.splitlines():
        m = re.match(r"^([0-9]+)\s", line)
        if m and start <= int(m[1]) <= end:
            result.append(line)
    return result


def program(old: str, new: str, font: int, repeats: int = 5) -> bytes:
    if font not in (1, 3) or not 1 <= repeats <= 20:
        raise ValueError("unsupported benchmark settings")
    original = lines_in(old, 2500, 2690)
    optimized = lines_in(new, 2500, 2690)
    metadata = lines_in(new, 2700, 2840)
    if len(original) < 18 or len(optimized) < 18 or len(metadata) < 8:
        raise ValueError("renderer or metadata missing")
    original = [
        re.sub(r"\b(25\d\d|26\d\d)\b", lambda m: str(int(m[0])+1000), line)
        for line in original
    ]
    lines = [
        '10 REM KABELKRANT ORIGINAL VS OPTIMIZED BASIC BENCHMARK',
        '20 DEFINT A-W,Z:DEFDBL X,Y',
        '30 SCREEN 7:COLOR 15,0,0:COLOR=(0,1,1,3):CLS',
        '40 SETPAGE 0,1:CLS:BLOAD "KRANT3.SC7",S:COLOR=RESTORE:SETPAGE 0,0:CLS',
        '50 DIM X(4,110),L1(4),L2(4),L3(4),Y1(4),Y2(4),Y3(4),H(4),O(4),P(4)',
        '60 COPY "X.DAT" TO X',
        '65 X(2,20)=158',
        '70 GOSUB 2700',
        '80 A$="KABELKRANT 2026 ABCDEFGHIJKLMNOP"',
        f'85 N={repeats}:LT={font}',
        '90 FOR Q=1 TO 4',
        '100 IF Q=1 THEN K=15:X=20:Y=60',
        '110 IF Q=2 THEN K=13:X=20:Y=60',
        '120 IF Q=3 THEN K=15:X=-500:Y=60',
        '130 IF Q=4 THEN K=13:X=-500:Y=60',
        '140 TIME=0:FOR I=1 TO N:IF Q>2 THEN X=-500',
        '145 GOSUB 3500:NEXT I:O(Q)=TIME',
        '150 TIME=0:FOR I=1 TO N:IF Q>2 THEN X=-500',
        '155 GOSUB 2500:NEXT I:P(Q)=TIME',
        '160 NEXT Q',
        '170 SCREEN 0:WIDTH 40:COLOR 15,4,4:CLS',
        '180 PRINT "KABELKRANT BASIC A/B BENCHMARK"',
        '190 PRINT "MSX2 NMS8250, FONT";LT;", N=";N',
        '200 PRINT "MSX JIFFIES (50 PER SECOND)"',
        '210 PRINT "MODE          ORIGINAL OPTIMIZED"',
        '220 RESTORE 260:FOR Q=1 TO 4',
        '230 READ M$',
        '240 PRINT M$;TAB(19);O(Q);TAB(29);P(Q)',
        '250 NEXT Q',
        '260 DATA WHITE +X,COLOR +X,WHITE -X,COLOR -X',
        '265 PRINT "COMPLETE"',
        '266 GOTO 266',
    ] + optimized + metadata + original
    numbers = [int(line.split(" ", 1)[0]) for line in lines]
    if numbers != sorted(numbers) or len(numbers) != len(set(numbers)):
        raise ValueError("duplicate/out-of-order BASIC line number")
    output = encode_msx_basic(("\n".join(lines)+"\n").encode("ascii"))
    validate_msx_basic(output)
    return output


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disk", type=Path, default=Path("assets/kabelkrant-6.2.dsk"))
    ap.add_argument("--optimized", type=Path, default=Path("src/LOOP.SYS"))
    ap.add_argument("--output", type=Path, default=Path("z80/build"))
    args = ap.parse_args()
    old = disk_file(args.disk.read_bytes(), "LOOP.SYS").decode("latin-1")
    new = args.optimized.read_text(encoding="latin-1")
    args.output.mkdir(parents=True, exist_ok=True)
    for font in (1, 3):
        target = args.output/f"BENCH{font}.BAS"
        target.write_bytes(program(old, new, font))
        print(f"{target}: {target.stat().st_size} bytes")


if __name__ == "__main__":
    main()
