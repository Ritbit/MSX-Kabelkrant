#!/usr/bin/env python3
"""Convert unchanged Kabelkrant src/X.DAT (MSX BASIC MBF doubles) into KBF1.

KBF1: 8-byte file header, then four font records. Each record is 11 bytes
(ID, height, L1/L2/L3, Y1/Y2/Y3, reserved, uint16 count) followed by
signed little-endian int16 coordinates. No new font/artwork assets are made.
"""
from pathlib import Path
import argparse
import struct

FONT_META = {
    1: (14, (52, 96, 0), (51, 66, 0)),
    2: (12, (56, 96, 0), (81, 94, 0)),
    3: (16, (43, 83, 96), (107, 124, 142)),
    4: (14, (49, 96, 0), (160, 174, 0)),
}


def decode_number(data: bytes) -> int:
    """Decode an integral 8-byte MSX BASIC decimal double (packed BCD)."""
    if len(data) != 8:
        raise ValueError('expected 8-byte double')
    if data == b'\0' * 8:
        return 0
    n = (data[0] & 0x7f) - 0x40
    digits = ''.join(f'{byte >> 4}{byte & 15}' for byte in data[1:])
    if any(byte >> 4 > 9 or (byte & 15) > 9 for byte in data[1:]):
        raise ValueError('invalid BCD coordinate')
    from decimal import Decimal
    value = Decimal(int(digits)) * Decimal(10) ** (n - 14)
    if value != int(value):
        raise ValueError(f'non-integral coordinate {value}')
    return -int(value) if data[0] & 0x80 else int(value)


def convert(raw: bytes) -> bytes:
    if len(raw) != 5 * 111 * 8:
        raise ValueError('src/X.DAT must contain exactly 555 BASIC doubles')
    values = [decode_number(raw[i:i + 8]) for i in range(0, len(raw), 8)]
    # X.DAT: font 2 X(2,20)=18 is an original typo between 148 and 166.
    # Correct the generated descriptor while preserving the raw source file.
    k = 20 * 5 + 2
    if values[k] == 18 and values[k-5] == 148 and values[k+5] == 166:
        values[k] = 158
    if values[k] != 158:
        raise ValueError("unexpected font 2 coordinate at X(2,20)")
    output = bytearray(b'KBF1' + bytes([1, 4, 0, 0]))
    for font, (height, limits, ys) in FONT_META.items():
        coords = [values[index * 5 + font] for index in range(111)]
        # All four original tables end in a -1 sentinel and trailing zero slots.
        while coords and coords[-1] == 0:
            coords.pop()
        if not coords or coords[-1] != -1:
            raise ValueError(f'font {font} missing -1 terminator')
        if not all(-32768 <= n <= 32767 for n in coords):
            raise ValueError('coordinate outside int16 range')
        output += struct.pack('<9BH', font, height, *limits, *ys, 0, len(coords))
        output += struct.pack('<' + 'h' * len(coords), *coords)
    return bytes(output)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--xdat', type=Path, default=Path('src/X.DAT'))
    p.add_argument('--output', type=Path, default=Path('z80/build/FONTS.DAT'))
    args = p.parse_args()
    data = convert(args.xdat.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f'{args.output}: {len(data)} bytes, four fonts')


if __name__ == '__main__':
    main()
