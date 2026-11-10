# HOWTO-TESTING — MSX Kabelkrant Z80

> Development-only documentation for `feature/z80-renderer`. Never merge this file or the development coordination files into `main`. Released BASIC v6.2b is the stable reference. See also `BUILD-AND-TEST.md`, `CONTEXT.md`, `TODO.md`, `PLAN.md`, `z80/FULL-TEST.md` and `.github/workflows/z80-build.yml`.

## Non-negotiable testing rules

1. **Never demand fixed names for downloaded ROM files.** Determine their function from contents, checksums, sizes and the installed openMSX Philips_NMS_8250 machine configuration. Only the *local names used by the openMSX machine definition* must match that definition; the source ZIP/attachment filenames are arbitrary.
2. **Reuse known-working configurations and prior test evidence** before attempting a new ROM acquisition or setup. Do not repeatedly ask the user for files already supplied or available in the current environment.
3. Distinguish: **compiled**, **disk structurally verified**, **emulator booted**, **Z80 code actually executed**, **visually accepted**, **functional regression passed**, and **long-running stable**. Never infer later stages from earlier stages.
4. Prior WebMSX manual successes remain **manual smoke-test evidence**, not automated regression results; do not reset them to "untested."
5. No external system ROMs in commits, public workflows, logs, PRs, disk-image artifacts or releases. Use only legitimately obtained ROMs.
6. Preserve original ROMs, `src/RAMDISK.BIN`, historical assets and stable 6.2b. Never merge the whole Z80 feature branch into `main`.

## Philips NMS8250 ROM identification and configuration

An NMS8250 set may contain a **32 KiB BIOS+BASIC** image plus **16 KiB SUB** and **16 KiB disk** ROMs, or the BIOS and BASIC may be provided as separate **16 KiB** halves. Both packaging styles are possible. Sizes are useful clues **but not definitive identification**.

```sh
find /path/to/roms -type f -print0 |
  while IFS= read -r -d '' file; do
    printf '%8s  ' "$(wc -c < "$file")"
    sha256sum "$file"
  done
```

Check the hashes and ROM layout against the installed `Philips_NMS_8250` machine XML and openMSX's machine test. **Do not concatenate a 32 KiB BIOS+BASIC image again.** If supplied separately and required by the machine config, combine only the *verified* BIOS and BASIC halves in correct order.

```sh
mkdir -p ~/.openMSX/share/systemroms
# Install identified ROMs using the names expected by openMSX machine XML.
openmsx -machine Philips_NMS_8250
# openMSX F10 console: test_machine Philips_NMS_8250
```

Follow actual openMSX error diagnostics for missing or mismatched ROMs. Do not substitute another MSX2 model or C-BIOS as a workaround for the project's Disk BASIC environment.

### GitHub Actions ROM-backed test

The existing workflow has a legacy interface with four **16 KiB** base64 secrets: `MSX_NMS8250_BIOS_B64`, `MSX_NMS8250_BASIC_B64`, `MSX_NMS8250_SUB_B64`, and `MSX_NMS8250_DISK_B64`. If the supplied and *verified* BIOS+BASIC is already 32 KiB, split it into two 16 KiB halves **for this interface**, or explicitly update the workflow to accept a combined file. Treat these as CI interface requirements, not requirements on the original filenames. Recheck the workflow implementation before use. Missing secrets mean the ROM-backed job is skipped, even when other jobs are green.

## Build with SjASMPlus 1.24.0

Run from repository root after `git switch feature/z80-renderer`. Prerequisites: Python 3, SjASMPlus 1.24.0, mtools, openMSX; Linux headless tests need `xvfb`. Installation is documented in `BUILD-AND-TEST.md`.

```sh
mkdir -p z80/build
python3 z80/tools/convert_fonts.py --xdat src/X.DAT --output z80/build/FONTS.DAT
(cd z80/asm && sjasmplus --raw=../build/textdemo.raw \
  --lst=../build/textdemo.lst --sym=../build/textdemo.sym basic_text_demo.asm)
python3 z80/tools/make_bload.py z80/build/textdemo.raw z80/build/KBLTXT.BIN
python3 z80/tools/msx_basic_ascii.py z80/asm/ASMTEXT.BAS z80/build/ASMTEXT.BAS
python3 -m unittest discover -s z80/tests -p 'test_*.py' -v
```

This builds the **standalone TEXT demo**, not the integrated 14-wipe newspaper.

To assemble an isolated demo disk, see the exact `mcopy` recipe in `BUILD-AND-TEST.md`. For **all** integration variants, disk generation and CI validations, run the existing **Z80 build and emulator smoke tests** workflow on `feature/z80-renderer` through GitHub Actions (`workflow_dispatch`) or push relevant source changes. Do not invent a one-line full-build command: use the checked-in workflow as the source of truth. Inspect each build's artifact contents and job summary.

## Run tests

**openMSX (Philips NMS8250):**

```sh
openmsx -machine Philips_NMS_8250 -diska /path/to/test.dsk
```

For the standalone demo only (as defined in `BUILD-AND-TEST.md`), headless smoke capture can use `z80/tools/openmsx_smoke.tcl`:

```sh
timeout 90s xvfb-run -a openmsx -machine Philips_NMS_8250 \
  -diska z80/build/KBLASM.DSK -script z80/tools/openmsx_smoke.tcl
```

A screenshot by itself is not proof of correct execution, correct VRAM pixels or stable runtime. Check console/logs, CPU entry/breakpoints, actual displayed pages and recorded state changes.

**WebMSX (manual smoke):**

- Stable v6.2b: `https://webmsx.org/?MACHINE=MSX2E&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/main/assets/kabelkrant-6.2b.dsk`
- Development variants: load a locally downloaded `.DSK` in WebMSX, or use a verified **raw** public HTTPS disk URL from `feature/z80-renderer` with `MACHINE=MSX2E`. A GitHub Actions artifact download page is not a raw `.DSK` URL.

**Minimum integrated Kabelkrant regression:** confirm RAMdisk boot and drive C: write/read/delete; TEXT and wipe calls; all fourteen integrated wipes and title restoration; intact clock/palette/colours/fonts; page loops over several cycles; operator menu/editor; no error/restart; and comparison with v6.2b. Longer unattended run and benchmark results must be logged separately.

## Existing evidence as of 2026-11-10

- User manually confirmed `KBLWIPEINT14.DSK` runs the newspaper and all 14 integrated Z80 wipes in WebMSX.
- User visually accepted `KBLTITLECOPY.DSK` title restoration, preserving the clock.
- Earlier full Z80 alpha displayed real newspaper pages and executed TEXT in openMSX; a prior page-loop corruption was fixed and manually rechecked in WebMSX.
- **Still open:** exact integrated disk's automated C: I/O, editor/menu and long-run regression; BASIC-versus-Z80 timing data; proof of ROM-backed CI execution. Do not present these as completed until matching logs/results exist.

## Working discipline

Before testing, record: branch + commit SHA, precise disk image + checksum, emulator/machine settings, ROM hashes (never raw ROM bytes), test type, actual observations, and CI run URL if applicable. When a test fails, retain the last-known-good disk and diagnose that failure only; do not recreate previously solved setup problems. Update `TODO.md` with verified status, not assumptions.
