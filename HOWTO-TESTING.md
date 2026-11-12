# HOWTO-TESTING — MSX Kabelkrant Z80

## Accepted Fedora runtime regression — 12 November 2026

[Run 43226534570](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43226534570): both jobs PASS. On the NMS8250: standalone TEXT, 14-wipe/title integrated newspaper loop, C: read/write/delete proof, 1,395 seconds unattended with 24 PNG frames, operator editor existing-file overwrite and return to changing live pages. The ROMs are downloaded ephemerally and never committed or uploaded.

For benchmark figures, guest-produced BENCHRES.CSV and benchmark.json are retained in the `openmsx-NMS8250-benchmark-and-clock` Actions artifact. The accepted benchmark now repeats each Z80 wipe **25 times** and averages the guest jiffies; see [docs/Z80-WIPE-BENCHMARK-2026-11-12.md](docs/Z80-WIPE-BENCHMARK-2026-11-12.md) for all 14 measured pairs and interpretation.

RTC: the test-only CLOCKCHK.BAS recorded 23:59:50 -> 00:00:00 and FRE(0)=15,605 in A:CLOCK.OK; **separately**, direct inline SET TIME before the normal LOOP.SYS produced changing newspaper pages after midnight, and that test is a mandatory CI gate. The chained CLOCKCHK -> LOOP fixture itself showed static frames and is not treated as production evidence.

For ROM acquisition, Fedora/DNF packages, headless openMSX, 25-call timing and clock fixture design, see [docs/REUSABLE-MSX-EMULATOR-TESTING.md](docs/REUSABLE-MSX-EMULATOR-TESTING.md). The short current TODO.md lists release packaging and independent nonblocking issues; the long historic test log is in docs/TEST-HISTORY-2026-11.md.


**Copyable methods for other MSX projects:** [docs/REUSABLE-MSX-EMULATOR-TESTING.md](docs/REUSABLE-MSX-EMULATOR-TESTING.md). This document is the **project-specific** reference for ROM URLs and current evidence.

> Development-only documentation for `feature/z80-renderer`. Never merge this file or the development coordination files into `main`. Released BASIC v6.2b is the stable reference. See also `BUILD-AND-TEST.md`, `CONTEXT.md`, `TODO.md`, `PLAN.md`, `z80/FULL-TEST.md` and `.github/workflows/z80-build.yml`.

## Non-negotiable testing rules

1. **Never demand fixed names for downloaded ROM files.** Determine their function from contents, checksums, sizes and the installed openMSX Philips_NMS_8250 machine configuration. Only the *local names used by the openMSX machine definition* must match that definition; the source ZIP/attachment filenames are arbitrary.
2. **Reuse known-working configurations and prior test evidence** before attempting a new ROM acquisition or setup. Do not repeatedly ask the user for files already supplied or available in the current environment.
3. Distinguish: **compiled**, **disk structurally verified**, **emulator booted**, **Z80 code actually executed**, **visually accepted**, **functional regression passed**, and **long-running stable**. Never infer later stages from earlier stages.
4. Prior WebMSX manual successes remain **manual smoke-test evidence**, not automated regression results; do not reset them to "untested."
5. No external system ROMs in commits, public workflows, logs, PRs, disk-image artifacts or releases. Use only legitimately obtained ROMs.
6. Preserve original ROMs, `src/RAMDISK.BIN`, historical assets and stable 6.2b. Never merge the whole Z80 feature branch into `main`.

## NMS8250 ROM download references (links only)

The following four URLs were supplied by the project maintainer. **Store these source URLs in documentation, not the ROM binary data in Git.** The remote source filenames are illustrative, not a requirement for identifying ROM images: verify actual ROM size, hash and suitability for the openMSX machine configuration.

| Purpose | Source URL | Expected size | Optional GitHub Actions secret |
| --- | --- | --- | --- |
| MSX BIOS | https://download.file-hunter.com/System%20ROMs/machines/philips/nms8250-bios.rom | 16 KiB | `MSX_NMS8250_BIOS_B64` |
| MSX BASIC | https://download.file-hunter.com/System%20ROMs/machines/philips/nms8250-basic.rom | 16 KiB | `MSX_NMS8250_BASIC_B64` |
| MSX2 SUB-ROM | https://download.file-hunter.com/System%20ROMs/machines/philips/nms8250_msx2sub.rom | 16 KiB | `MSX_NMS8250_SUB_B64` |
| MSX Disk ROM | https://download.file-hunter.com/System%20ROMs/machines/philips/nms8250_disk.rom | 16 KiB | `MSX_NMS8250_DISK_B64` |

**2026-11-11 CI resolution:** [run 42983952510](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/42983952510) initially got HTTP 405 without browser User-Agent. Adding `curl -A "Mozilla/5.0"` to all four split-ROM downloads resolved access. [Run 43001359714](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43001359714) successfully executed the NMS8250 standalone, multi-page loop and C: proof tests; ROMs remained temporary and private to the runner. The earlier direct combined-ROM and ZIP URLs returned HTTP 405 in run 42889296897; test these four *distinct* links separately before relying on direct CI downloads. Do not silently substitute downloads from an unverified mirror, and respect the source's access rules. GitHub Actions secrets are an optional alternative for private runtime provision, not ROM files in the repository. Keep ROM bytes outside commits, artifacts, and logs; consult the applicable distribution rights.

## Philips NMS8250 ROM identification and configuration

The reusable ROM acquisition/security technique is documented in the portable guide linked above. An NMS8250 set may contain a **32 KiB BIOS+BASIC** image plus **16 KiB SUB** and **16 KiB disk** ROMs, or the BIOS and BASIC may be provided as separate **16 KiB** halves. Both packaging styles are possible. Sizes are useful clues **but not definitive identification**.

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

The current workflow accepts **two private-secret layouts** (the names below are CI input interfaces, not source-file naming requirements):

- Preferred three-file set: `MSX_NMS8250_MAIN32_B64` (32 KiB BIOS+BASIC), `MSX_NMS8250_SUB16_B64` (16 KiB), `MSX_NMS8250_DISK16_B64` (16 KiB).
- Legacy four-file set: `MSX_NMS8250_BIOS_B64`, `MSX_NMS8250_BASIC_B64`, `MSX_NMS8250_SUB_B64`, `MSX_NMS8250_DISK_B64` (each 16 KiB). The workflow joins BIOS and BASIC in this case.

Do **not** split an already verified 32 KiB image merely because a previous guide asked for four files. Keep ROM contents private. No secrets means the emulator tests are skipped (other build steps may still pass).

**Actual result, 2026-11-10:** [GitHub Actions run 42889296897](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/42889296897) completed all 72 build-job steps successfully. The separate NMS8250 job failed during ROM acquisition: both explicit user-provided direct and ZIP endpoints returned HTTP 405 from the runner. No NMS8250 emulator test executed in that run; its failure is infrastructure/ROM availability, **not a Kabelkrant runtime regression**. Avoid repeating these URLs without new evidence they work. The runtime job already defines loop captures and a C: read/write/delete proof, so resume those tests once private, verified ROMs are accessible.

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

## Verified NMS8250 ROM-backed CI milestone (2026-11-11)

[GitHub Actions run 43001359714](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43001359714), commit `9f3618d`: **build and openMSX runtime job both passed**, using four supplied split ROM URLs fetched with `curl -A "Mozilla/5.0"` into an ephemeral runner ROM pool (no ROM data in repository or artifacts). The openMSX job reports success for standalone Z80 screenshot smoke, independent full Kabelkrant multi-page screenshot/difference regression at 120/165/210/255 emulated seconds on `KBLTITLECOPY.DSK`, and C: write/read/compare/delete proof with `A:KBLPASS.OK` checked via `mcopy` from a disposable copy of `KBLCTESTAUTO.DSK`. Screenshot artifacts are retained by Actions.

Earlier failed runs identified **test harness errors**, not established production regressions: pre-boot screenshot assertions at 25/30s, injected BASIC proof opening file handle #2 (error 52 without `MAXFILES` setting), and missing `mtools` in the separate runtime job. These are corrected; injected proof now reuses closed handle #1. **Still not established:** interactive editor/menu flows, pixel-exact comparison, clock rollover or truly long unattended operation. Keep experimental preview and released v6.2b distinct.

## Verified extended runtime (2026-11-11)

- [GitHub Actions run 43030914435](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43030914435) on commit `693cb2f`: **build PASS**, standalone Z80 openMSX screenshot PASS, multi-page KabelKrant loop PASS, RAMdisk C: write/read/compare/delete **PASS**, and unattended NMS8250 test **PASS** with 0/2/12-second screenshots around 8 intervals covering 120–1392 emulated seconds. Tcl completion was at 1395 seconds. This is evidence of ~23 minutes emulated running on `KBLTITLECOPY.DSK`, not proof of indefinite stability or tests on all experimental disk variants.
- **Editor/menu integration remains FAIL/UNVERIFIED** in this run: the keyboard-driven test reaches menus/editor/save-name prompt but the expected `Z8REG26.TXT` proof file is not found on disposable A:. Do not attribute that to an application regression without further investigation; keyboard injection or a fixture issue remains possible.
- Harness lessons: uniform wipe PNG may be under 1024 bytes and still be valid; validate decoded image dimensions and distinguish content afterward. Schedule Tcl `exit` *after* the final delayed frame (original final +12s screenshot was scheduled after exit). See [docs/REUSABLE-MSX-EMULATOR-TESTING.md](docs/REUSABLE-MSX-EMULATOR-TESTING.md).


## Current Fedora 43 CI backend (2026-11-11)

The development workflow `.github/workflows/z80-build.yml` was migrated from Ubuntu package installation to **Fedora 43 container jobs**. The managed GitHub VM host is still Ubuntu, but `dnf`, SjASMPlus compilation, `mtools`, openMSX and Python runtime tests run inside Fedora; no Ubuntu `apt-get` is required. See [docs/REUSABLE-MSX-EMULATOR-TESTING.md](docs/REUSABLE-MSX-EMULATOR-TESTING.md) for the portable setup, Git checkout ownership pitfall, and package list.

Evidence: [Fedora dependency probe 43062958577](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43062958577) passed. [Fedora full CI run 43065977217](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43065977217): **build PASS**, standalone NMS8250 renderer PASS, multi-page loop PASS, disposable C: write/read/delete PASS, 24-frame / ~23-minute emulated unattended regression PASS. The editor case made it through menu, loaded existing `MENU01.TXT`, edited and saved `Z8REG26.TXT` to A: (verified by `mcopy`), but the automated checker **did not observe resumed page changes**, so overall runtime job is FAIL. Do not mark the end-to-end editor return as accepted. No original program source, ROM binaries, `main`, or v6.2b release was modified for this migration.
