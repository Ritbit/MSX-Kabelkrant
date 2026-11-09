# Kabelkrant Z80 work-in-progress

**Build and emulator tests:** [`BUILD-AND-TEST.md`](../BUILD-AND-TEST.md) (SjASMPlus, FAT12 disk images, openMSX/NMS 8250, WebMSX).

This branch is an **assembly build prototype**, not a working MSX driver.
Do not use `kernel.raw` with `BLOAD`: it lacks a BASIC-extension handler,
installer, and safe resident-memory allocation. The original graphical assets remain untouched; only the development-branch
BASIC sources have been repaired.

- `asm/font_lookup.asm`: KBF1 font lookup (unfinished runtime integration).
- `asm/v9938_lmmm.asm`: V9938 LMMM command issuer (not yet emulator-tested).
- `asm/kernel.asm`: prototype translation unit.
- `tools/convert_fonts.py`: converts original `src/X.DAT` without modifying it.
- `tests/test_conversion.py`: verifies font binary layout against the original.

## Build locally

Requires SjASMPlus 1.24.0 and Python 3.10+:

```sh
python3 z80/tools/convert_fonts.py --xdat src/X.DAT --output z80/build/FONTS.DAT
python3 -m unittest discover -s z80/tests -p 'test_conversion.py' -v
(cd z80/asm && sjasmplus --raw=../build/kernel.raw --lst=../build/kernel.lst --sym=../build/kernel.sym kernel.asm)
```

On `feature/z80-renderer`, GitHub Actions runs these steps and publishes a
non-bootable reference artifact. A real MSX emulator-test disk follows only
after the BASIC calling interface, colour handling and memory placement work.

## Four-font reference baseline

## Four-font BASIC renderer (production source on this branch)

`src/KBLINIT.SYS` now loads `KRANT3.SC7`, the atlas containing all four
fonts. `src/LOOP.SYS` reads their original Y positions:

| Font | Y starts |
| --- | --- |
| 1 | 51, 66 |
| 2 | 81, 94 |
| 3 | 107, 124, 142 |
| 4 | 160, 174 |

**Fast path:** For K=15 and X>=0, each glyph is copied directly from
page 1 to page 0 using `TPSET`. No scratch clear/recolour is needed.
For other colours or X<0 (right alignment), the whole line is assembled
on page 1 at Y=190..207, colour-masked once, and copied to page 0.
The source atlas extends through Y=188, so neither path erases font 4.

Original `src/X.DAT` is unchanged. Its font-2 X(2,20) coordinate is
erroneously 18 between 148 and 166; BASIC fixes this to 158 when loading
the table, and the assembly `FONTS.DAT` converter applies the same
correction.

The `KBLBASE.DSK` Actions artifact includes `FONTBAS.BAS` (white,
positive X) and `FONTCOL.BAS` (K=13, negative X) as regression programs.
They run the *production* GOSUB 2500 routine, not a separate drawing
implementation. Tested locally under openMSX with Philips NMS 8250 ROMs.

The branch is development-only. The `kernel.raw` Z80 prototype still
must not be loaded with `BLOAD`. `ASMTEXT.BAS` is an independent
assembly experiment and is **not** a replacement for the BASIC routine.
