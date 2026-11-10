#!/usr/bin/env python3
"""Generate a private test-only initializer that runs C: regression post-copy.

The original ROM, RAMdisk, main LOOP, test data and disk are untouched.
Insert one line 235 between the successful C: COPY loop and RUN LOOP.SYS.
"""
from pathlib import Path
import argparse
import sys
from msx_basic_ascii import encode_msx_basic, validate_msx_basic

ROOT=Path(__file__).resolve().parents[2]

def generate(src: bytes)->bytes:
    if not src.endswith(b"\r\n\x1a"):
        raise ValueError("Expected on-disk MSX BASIC ASCII source")
    text=src[:-1].decode("ascii")
    lines=text.split("\r\n")
    program={}
    for line in lines:
        if not line:
            continue
        number,body=line.split(" ",1)
        n=int(number)
        if n in program:
            raise ValueError(f"Duplicate BASIC line: {n}")
        program[n]=body
    if not program.get(195)=="DEFUSR3=&HC806: A=USR3(0)":
        raise ValueError("Expected installed shared Z80 extension")
    if not program.get(230,"").startswith('READ PR$: IF PR$<>"END" THEN COPY "A:"+PR$ TO "C:"'):
        raise ValueError("Expected RAMdisk A: -> C: initialization")
    if program.get(240)!='RUN "LOOP.SYS"':
        raise ValueError("Expected normal broadcast handoff")
    if 235 in program:
        raise ValueError("BASIC line 235 already in use")
    program[235]='RUN "A:CTEST.BAS"'
    out=encode_msx_basic(("\n".join(f"{n} {program[n]}" for n in sorted(program))+"\n").encode("ascii"))
    validate_msx_basic(out)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    ap.add_argument("dest",type=Path)
    a=ap.parse_args()
    data=generate(a.source.read_bytes())
    a.dest.parent.mkdir(parents=True,exist_ok=True)
    a.dest.write_bytes(data)
    print(f"RAMdisk auto-test initializer {len(data)} bytes; test runs after COPY to C:")

if __name__=="__main__":
    main()
