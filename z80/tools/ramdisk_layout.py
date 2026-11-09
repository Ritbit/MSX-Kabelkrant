#!/usr/bin/env python3
"""Static audit of RAMDISK.BIN's destructive mapper-bank zero-fill."""
from pathlib import Path

ROM_OFFSET = 0xFB
ROM_BASE = 0x4000
FILL_INSTRUCTIONS = bytes.fromhex("21 F4 46 11 F5 46 01 0A 39 36 00 ED B0")
FILL_FIRST = 0x46F4
FILL_DST = 0x46F5
FILL_LENGTH = 0x390A
FORMER_TEXT_ENTRY = 0x46F5


def validate_ramdisk(data: bytes) -> None:
    if len(data) != 2039 or data[:7] != bytes.fromhex("FE 00 C0 EF C7 00 C0"):
        raise ValueError("Unexpected historical RAMDISK.BIN format")
    rom = data[7+ROM_OFFSET:]
    if rom[:4] != b"ABA\x40":
        raise ValueError("Unexpected ROM signature or init pointer")
    if rom.count(FILL_INSTRUCTIONS) != 1 or rom.index(FILL_INSTRUCTIONS) != 0x1B3:
        raise ValueError("Original RAMdisk zero-fill routine changed")
    if ROM_BASE + len(rom) != FORMER_TEXT_ENTRY:
        raise ValueError("Expected end of original Disk-ROM has changed")


def first_overlap(start: int, length: int) -> int | None:
    if not 0 < length < 65536:
        raise ValueError("Invalid extension length")
    end = start + length - 1
    fill_end = FILL_DST + FILL_LENGTH - 1
    if start <= fill_end and end >= FILL_FIRST:
        return max(start, FILL_FIRST)
    return None


if __name__ == "__main__":
    validate_ramdisk(Path("src/RAMDISK.BIN").read_bytes())
    assert first_overlap(FORMER_TEXT_ENTRY, 2048) == FORMER_TEXT_ENTRY
    print("RAMdisk destroys 46F4h..7FFEh; former TEXT entry 46F5h is unsafe")
