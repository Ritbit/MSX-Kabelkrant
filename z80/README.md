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
