#!/usr/bin/env python3
"""Build single MSX2 RAMDISK + CALL TEXT binary without altering disk-driver code.

RAMDISK.BIN's C000 installer copies a Disk ROM image from C0FB to page1
4000h and initiates a warm reset. We preserve every original byte,
only extend its LDIR copy length and set the empty BASIC statement pointer
at ROM header 4004h. The new CALL handler lives after the existing ROM,
in the same mapper bank, so it can be discovered on the next boot.

WARNING: The original RAMdisk zero-fills 46F4h..7FFEh, erasing the
appended 46F5h handler. This builder is retained ONLY to reproduce the
known-broken experiment. The old DOS/Disk BASIC entry points are
intentionally NOT removed until hardware/emulator integration proves safe.
"""
from pathlib import Path
import argparse
import struct
from msx_basic_ascii import encode_msx_basic

ORG = 0x46F5
ROM_OFFSET = 0xFB
EXPECTED_OLD_COPY_LENGTH = 0x06F4
COPY_PATTERN = bytes.fromhex('21 FB C0 01 F4 06 ED B0')
EXPECTED_ORIGINAL_LEN = 2039
OUT_NAME = 'KBLALL.BIN'


def extension_source(source: str) -> str:
    if source.count('\nCallHandler:\n') != 1 or source.count('\n    ORG 0C804h') != 1:
        raise ValueError('unexpected text-demo ASM structure')
    constants = source[:source.index('\n    ORG 0C804h')]
    body = source[source.index('\nCallHandler:\n') + 1:]
    assert 'INCLUDE \'font_lookup.asm\'' in body
    assert 'INCLUDE \'v9938_lmmm.asm\'' in body
    return (constants + '\n    ORG 046F5h\n'
            'CallHandler:\n'
            '    push hl\n'
            '    ld hl,EmbeddedFonts\n'
            '    call SetFontBase\n'
            '    pop hl\n' +
            body[len('CallHandler:\n'):])


def combine(old: bytes, extension: bytes) -> bytes:
    if len(old) != EXPECTED_ORIGINAL_LEN or old[:7] != bytes.fromhex('FE 00 C0 EF C7 00 C0'):
        raise ValueError('unexpected original RAMDISK.BIN header or length')
    raw = bytearray(old[7:])
    ix = raw.find(COPY_PATTERN)
    if ix < 0 or raw.count(COPY_PATTERN) != 1:
        raise ValueError('RAMDISK installer copy signature not found once')
    if raw[ROM_OFFSET:ROM_OFFSET+4] != b'ABA\x40':
        raise ValueError('unexpected RAM Disk ROM header at C0FB')
    if raw[ROM_OFFSET+4:ROM_OFFSET+6] != b'\0\0':
        raise ValueError('the original ROM statement handler is not empty')
    if not extension:
        raise ValueError('empty Z80 extension')
    assert 0x4000 + len(raw) - ROM_OFFSET == ORG, 'extension ORG mismatch'

    # Patch the one LDIR transfer length (not the disk-driver functions).
    length = len(raw) - ROM_OFFSET + len(extension)
    if length >= 0x4000:
        raise ValueError('extension does not fit a 16KB ROM bank')
    struct.pack_into('<H', raw, ix + 4, length)
    struct.pack_into('<H', raw, ROM_OFFSET + 4, ORG)
    raw.extend(extension)

    if 0xC000 + len(raw) >= 0xF000:
        raise ValueError('BLOAD would overwrite MSX system work RAM')
    header = b'\xFE' + struct.pack('<HHH', 0xC000, 0xC000 + len(raw) - 1, 0xC000)
    return header + raw


def build_programs(root: Path, out: Path) -> None:
    original_boot = (root / 'src/AUTOEXEC.BAS').read_text(encoding='latin1')
    demo = (root / 'z80/asm/ASMTEXT.BAS').read_text(encoding='ascii')
    if 'KBLINIT.SYS' not in original_boot or 'RAMDISK.BIN' not in original_boot:
        raise ValueError('unexpected AUTOEXEC.BAS')
    if '30 CLEAR 300,&HC7FF' not in demo or '70 BLOAD "KBLTXT.BIN",R' not in demo:
        raise ValueError('unexpected demo BASIC')
    boot = original_boot.replace('KBLINIT.SYS', 'COMBTEXT.BAS').replace('RAMDISK.BIN', OUT_NAME)
    demo = demo.replace('30 CLEAR 300,&HC7FF', '30 CLEAR 300').replace(
        '70 BLOAD "KBLTXT.BIN",R', "70 ' CALL extension is inside combined Disk-ROM")
    # The original installer restores page-1 mapper segment 4. The extension
    # ROM lives in segment 2, and its page-1 slot attribute is not registered
    # during the legacy warm-start handoff. Register only for this experiment.
    registration = ("75 OUT &HFD,2:A=PEEK(&HF342):"
                    "POKE &HFCC9+(A AND 3)*16+(A AND 12)+1,32")
    demo = demo.replace('80 CALL KBLVER', registration + '\n80 CALL KBLVER')
    for name, text in [('COMBAUTO.BAS', boot), ('COMBTEXT.BAS', demo)]:
        out.joinpath(name).write_bytes(encode_msx_basic(text.replace('\r\n','\n').encode('ascii')))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, default=Path('.'))
    p.add_argument('--output', type=Path, default=Path('z80/build'))
    p.add_argument('--extension', type=Path, help='Previously assembled 46F5h Z80 ROM extension')
    args = p.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    if args.extension:
        original = (args.root/'src/RAMDISK.BIN').read_bytes()
        extension = args.extension.read_bytes()
        result = combine(original, extension)
        (out/OUT_NAME).write_bytes(result)
        print(f'{out/OUT_NAME}: {len(result)} bytes, original RAMdisk plus ROM CALL TEXT')
        print(f'ROM copy size: {len(original)-7-ROM_OFFSET+len(extension)} bytes')
        build_programs(args.root,out)
    else:
        asm = extension_source((args.root/'z80/asm/basic_text_demo.asm').read_text())
        (args.root/'z80/asm/.generated_combined.asm').write_text(asm)
        print('Generated combined assembly at ROM address 46F5h')
        print('Next assemble .generated_combined.asm into combined_text.raw')


if __name__ == '__main__':
    main()
