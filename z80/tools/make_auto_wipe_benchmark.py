#!/usr/bin/env python3
"""Generate auto-start benchmark KBLINIT without changing the working alpha."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from make_wipe_benchmark import split_program
from msx_basic_ascii import encode_msx_basic,validate_msx_basic


def generate(original: bytes) -> bytes:
    if not original.endswith(b"\r\n\x1a"):
        raise ValueError("Expected MSX BASIC ASCII initialization file")
    program=split_program(original[:-1].decode("ascii").replace("\r\n","\n"))
    if program.get(195)!="DEFUSR3=&HC806: A=USR3(0)":
        raise ValueError("Expected original integrated single-file extension setup")
    if 198 in program or 196 in program or 197 in program:
        raise ValueError("198 is not a free transition line")
    if 200 not in program:
        raise ValueError("Expected original program flow after installer")
    program[198]='RUN "A:BENCHW.BAS"'
    result=encode_msx_basic(("\n".join(f"{n} {program[n]}" for n in sorted(program))+"\n").encode("ascii"))
    validate_msx_basic(result)
    return result

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: make_auto_wipe_benchmark.py INIT.SYS OUTPUT.SYS")
    inp,out=map(Path,sys.argv[1:])
    data=generate(inp.read_bytes())
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(data)
    print(f"Auto benchmark init {len(data)} bytes; inserted BASIC 198")
