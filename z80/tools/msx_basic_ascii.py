#!/usr/bin/env python3
"""Create MSX Disk BASIC ASCII program: CRLF line endings and DOS EOF ^Z.

The source file is kept as normal LF text in Git. This script strictly
validates the BASIC line numbers and limits before preparing disk bytes.
"""
import argparse
from pathlib import Path
import re

MAX_LINE_LENGTH = 240
LINE = re.compile(rb"^([0-9]{1,5})(?:[ \t]|$)")

def encode_msx_basic(source: bytes) -> bytes:
    # Source may be LF or CRLF in the repository.
    source = source.replace(b"\r\n", b"\n")
    if b"\r" in source or b"\x1a" in source or b"\x00" in source:
        raise ValueError("unexpected CR/NUL/EOF in text source")
    if not source.endswith(b"\n"):
        raise ValueError("BASIC source must end in a newline")
    lines = source[:-1].split(b"\n")
    last_num = -1
    if not lines or not all(lines):
        raise ValueError("empty BASIC program line")
    for line in lines:
        if any(ch > 0x7F or (ch < 0x20 and ch != 9) for ch in line):
            raise ValueError("BASIC program must be ASCII")
        m = LINE.match(line)
        if not m:
            raise ValueError(f"unnumbered BASIC line: {line[:40]!r}")
        n = int(m.group(1))
        if not 0 <= n <= 65529 or n <= last_num:
            raise ValueError("line numbers must be ascending and unique")
        last_num = n
        if len(line) > MAX_LINE_LENGTH:
            raise ValueError(f"BASIC line {n} exceeds {MAX_LINE_LENGTH} characters")
    return b"\r\n".join(lines) + b"\r\n\x1a"

def validate_msx_basic(content: bytes) -> None:
    if not content.endswith(b"\r\n\x1a"):
        raise ValueError("MSX BASIC file must end in CRLF + CTRL-Z")
    source = content[:-1].replace(b"\r\n", b"\n")
    if b"\r" in source or source.count(b"\n") == 0:
        raise ValueError("stray CR or missing CRLF")
    if encode_msx_basic(source) != content:
        raise ValueError("invalid MSX BASIC formatting")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = encode_msx_basic(args.source.read_bytes())
    validate_msx_basic(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)
    print(f"{args.output}: {len(result)} bytes, CRLF + DOS EOF")
