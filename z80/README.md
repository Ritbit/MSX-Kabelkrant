# Kabelkrant Z80 work-in-progress

This branch is an **assembly build prototype**, not a working MSX driver.
Do not use `kernel.raw` with `BLOAD`: it lacks a BASIC-extension handler,
installer, and safe resident-memory allocation. The original Kabelkrant
and assets are left untouched.

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

The original `KRANT4.SC7` graphic asset contains fonts **1, 3 and 4**
but **no font 2**. The original metadata for font 4 (Y=160,174) points
into empty space in `KRANT4.SC7`; actual rows are Y=134,149.

`KRANT3.SC7` contains all four fonts at rows:
1: (51,66), 2: (81,94), 3: (107,124,142), 4: (160,174).
The original `LOOP.SYS` indiscriminately clears rows 164..212, which
wipes the source for font 4 in that atlas.

The isolated `FONTBAS.BAS` baseline deliberately uses `KRANT3.SC7`,
draws font 4 before font 1, changes font 3's row metadata back to
(107,124,142), and prepares scratch rows only for font 1. It uses
K=15, so omitting the original AND recolour operation is safe here.
These are **test-harness-only** changes: `src/LOOP.SYS`, `X.DAT`,
`KRANT3.SC7` and `KRANT4.SC7` remain unchanged.
