# Development context — Z80 Kabelkrant

## Verified release-candidate tests — 12 November 2026

Full **Fedora 43/NMS8250 CI run [43226534570](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43226534570) PASS**: assembly/build, standalone TEXT, integrated page loop, C: read/write/delete, 1395 seconds unattended, editor load/modify/overwrite of existing MENU01.TXT, and return to changing live pages. Guest RTC crossed 23:59:50 to 00:00:00; the separate direct SET TIME initializer also showed real newspaper progression after midnight. The alternative CLOCKCHK.BAS chain produced static frames, a fixture-specific anomaly; it is not the accepted live-loop path.

**25-call-per-mode wipe benchmark**: aggregate original-BASIC/native wipe-body speedup **127.76x**, arithmetic mean per-mode ratio **132.82x**, measured FRE(0)=**13,558 bytes** in the benchmark context. Raw files BENCHRES.CSV and benchmark.json are in the CI artifact; interpretation in docs/Z80-WIPE-BENCHMARK-2026-11-12.md. Not an end-to-end page-loop speedup.

Current minimal release TODO: TODO.md; older testing chronology archived in docs/TEST-HISTORY-2026-11.md. `main` and 6.2b stay unchanged.


> **Private-to-development documentation in a public branch.** This file and
> `AGENTS.md`, `PLAN.md`, `TODO.md`, `BUILD-AND-TEST.md`,
> `HOWTO-TESTING.md` belong to
> `feature/z80-renderer` **only**. Never include them in a PR to `main`.
> Updated 2026-11-10; verify current GitHub Actions results before trusting
> historical status claims.

## Goal and non-goals

Modernize the 1994 MSX2 Kabelkrant incrementally, retaining its look,
functional behavior, historical assets, and MSX2 compatibility. Replace the
expensive BASIC graphics routines with Z80/V9938 routines **only when tested
and measurably beneficial**. The published **v6.2b** is the known stable
BASIC-only maintenance release and must not be overwritten during experiments.

The RAMdisk and Z80 modules may be loaded at each boot. They do **not** need
to survive a reset, but their code/data must remain addressable **while**
BASIC calls them or drive C: uses the RAMdisk.

## Repository map

- `src/LOOP.SYS`: broadcast/pagination logic; proportional text at 2500–2690;
  clock at 2900–3050; 14 wipes at 3100–3390; title wipe at 3400–3480;
  hourglass at 3500–3790.
- `src/KBLINIT.SYS`: video initialization, palettes, RAMdisk handoff and
  three existing string `USR` functions (uppercase, strip, combined).
- `src/AUTOEXEC.BAS`: RAMdisk bootstrap with warm-restart/keyboard-buffer
  continuation. Direct `BLOAD "RAMDISK.BIN",R` mid-test is **not**
  interchangeable with this sequence.
- `src/RAMDISK.BIN`: original binary RAMdisk installer/driver; drive C:.
- `src/KRANT3.SC7`: atlas containing **all four** proportional fonts.
  `KRANT4.SC7` has only three, despite its name.
- `src/X.DAT`: font coordinate data. The original `X(2,20)=18` is a typo;
  runtime/converter uses 158 without mutating the historical source.
- `z80/asm/basic_text_demo.asm`: standalone BASIC `CALL TEXT` extension.
- `z80/asm/font_lookup.asm`, `v9938_lmmm.asm`: font lookup and V9938
  command engine.
- `z80/tools/make_combined_rom.py`: experimental RAMdisk+TEXT image builder.
- `z80/COMBINED-STATUS.md`: latest confirmed integration blocker.
- `z80/PERFORMANCE-ROADMAP.md`: detailed optimization candidates.
- `BUILD-AND-TEST.md`: detailed assembly, disk-image, openMSX and WebMSX test guide.
- `HOWTO-TESTING.md`: project ROM identification, test evidence levels and regression checklist.
- `docs/REUSABLE-MSX-EMULATOR-TESTING.md`: portable openMSX/WebMSX headless testing guide, screenshot pairs, Tcl checkpoint files, CI and proof artifacts.

## Graphics and fonts

SCREEN 7: 512 × 212, 4 bpp; two 64-KiB VRAM pages on a 128-KiB MSX2.
Page 0 is visible; page 1 contains graphics/fonts. `KRANT3.SC7` font
source Y rows are:

| Font | Source row starts |
| --- | --- |
| 1 | 51, 66 |
| 2 | 81, 94 |
| 3 | 107, 124, 142 |
| 4 | 160, 174 |

Do not wipe/copy over font 4 (through approximately Y=188). The
optimized BASIC routine uses page-1 Y=190–207 as scratch. The assembly
colour path uses small scratch rectangles; keep them clear of source glyphs,
VDP sprite/palette tables and any other active VRAM data. Preserve the
`COLOR=RESTORE` palette setup when testing.

Font coordinates are proportional; never assume equal character widths.
The converter audits ASCII 33–127. **Font 3 / ASCII 127 lacks a valid last
coordinate**, so the current lookup safely rejects it; this is not a
completed full-glyph rendering test.

## Verified vs unresolved (do not conflate)

**Verified in separate experiments:** SjASMPlus builds; standalone
`CALL TEXT(...)` with four fonts, white and colour 13, positive and
negative X tested under openMSX/Philips NMS 8250; raw font conversion,
BLOAD format and binary structure unit tests pass.

**Not verified:** the combined RAMdisk+TEXT boot and BASIC `CALL` route.
`KBLALL.BIN` is about 4.2 KB and fits in one 16-KiB mapper bank, but
`KBLCOMB.DSK` currently reaches `Syntax error in 80` at `CALL KBLVER`.
The execution breakpoint at `46F5h` did not fire. The loader/ROM slot
discovery mechanism is the active blocker. Mapper `OUT &HFD,2` in the
demo is only a diagnostic workaround, not a production solution.

The original RAMdisk has **not** been safely reduced or replaced.
A physically small binary is not proof of correct ROM dispatch.

## Test environment and release boundary

- Assemblage: SjASMPlus 1.24.0; Python tests; GitHub Actions
  `.github/workflows/z80-build.yml` (on development branch).
- Emulator: openMSX 19.1, Philips NMS 8250 ROMs; WebMSX with
  `MACHINE=MSX2E` for manual smoke tests.
- Never put external system ROMs in the public repo or workflow artifacts.
- All experimental images belong on the development branch. A successful
  CI build alone is **not** an MSX runtime test.
- Publish only isolated, tested release changes via a clean branch from
  `main`; never merge the whole development branch.

## RAMdisk/TEXT collision — experimentally verified

A runtime breakpoint showed BASIC enters the expected CALL handler
address 46F5h in slot 3-2, but an LDIR at 41B3h in the original
RAMdisk later zero-fills 46F4h–7FFEh. This overwrites the TEXT extension
byte E5h with 00h. The old explanation ('CALL never reaches the ROM')
is superseded. See `z80/COMBINED-STATUS.md` for write-watchpoint evidence.

## Full application alpha milestone

`z80/FULL-TEST.md` documents the **experimental**
`KBLZ80TEST-full-Kabelkrant-EXPERIMENTAL` disk from GitHub Actions.
It uses an unmodified v6.2b disk as the base, a separately loaded
C804h Z80 TEXT module, original RAMdisk, and a smaller LOOP.SYS
that omits the unused BASIC X(4,110) font table to preserve memory.
The historical 6.2b LOOP.SYS is retained on the alpha disk as
`LOOPBAS.SYS`.

Verified in openMSX: RAMdisk boot, Z80 install, multiple CALL TEXT
executions, rendered real news page. **Historical regression:** earlier alpha re-entered the boot sequence after several pages. The zero-length-string `LDIR` corruption and page-loop stack defect were corrected; the user confirmed WebMSX page cycles afterward (see `TODO.md` and `z80/FULL-TEST.md`). This does not yet establish unattended long-run stability.
Do not promote alpha as stable or merge the feature branch wholesale.

## Current integration status (2026-11-10; authoritative recent checkpoint)

- The earlier `KBLCOMB.DSK` ROM-overlay experiment is **known broken** and superseded by separate high-RAM staging; do not mistake its old failure for the working onefile alpha.
- User-confirmed WebMSX: integrated 14 Z80 wipes on `KBLWIPEINT14.DSK`; accepted title-background-copy variant `KBLTITLECOPY.DSK`. These are valid manual smoke results, **not** complete regression evidence.
- [GitHub Actions run 42889296897](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/42889296897): all 72 build-job steps successful, including disk-image tests. Historical ROM-backed NMS8250 job failed before launch due HTTP 405. **Superseded** by successful run 43001359714 using four split ROM URLs with browser User-Agent.
- Automated C: read/write/compare/delete proof, 210s loop captures and image checks are already wired into `.github/workflows/z80-build.yml`, and were **subsequently executed successfully** in run 43001359714 with ephemeral four-ROM downloads. Do not store ROMs in the repository.
- Always read `HOWTO-TESTING.md` for reproducible ROM setup and evidence levels, and `TODO.md` for current next tasks. Never demand exact upstream ROM filenames.

## Verified NMS8250 ROM-backed CI milestone (2026-11-11)

[GitHub Actions run 43001359714](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43001359714), commit `9f3618d`: **build and openMSX runtime job both passed**, using four supplied split ROM URLs fetched with `curl -A "Mozilla/5.0"` into an ephemeral runner ROM pool (no ROM data in repository or artifacts). The openMSX job reports success for standalone Z80 screenshot smoke, independent full Kabelkrant multi-page screenshot/difference regression at 120/165/210/255 emulated seconds on `KBLTITLECOPY.DSK`, and C: write/read/compare/delete proof with `A:KBLPASS.OK` checked via `mcopy` from a disposable copy of `KBLCTESTAUTO.DSK`. Screenshot artifacts are retained by Actions.

Earlier failed runs identified **test harness errors**, not established production regressions: pre-boot screenshot assertions at 25/30s, injected BASIC proof opening file handle #2 (error 52 without `MAXFILES` setting), and missing `mtools` in the separate runtime job. These are corrected; injected proof now reuses closed handle #1. **Still not established:** interactive editor/menu flows, pixel-exact comparison, clock rollover or truly long unattended operation. Keep experimental preview and released v6.2b distinct.

## Verified extended runtime (2026-11-11)

- [GitHub Actions run 43030914435](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43030914435) on commit `693cb2f`: **build PASS**, standalone Z80 openMSX screenshot PASS, multi-page KabelKrant loop PASS, RAMdisk C: write/read/compare/delete **PASS**, and unattended NMS8250 test **PASS** with 0/2/12-second screenshots around 8 intervals covering 120–1392 emulated seconds. Tcl completion was at 1395 seconds. This is evidence of ~23 minutes emulated running on `KBLTITLECOPY.DSK`, not proof of indefinite stability or tests on all experimental disk variants.
- **Editor/menu integration remains FAIL/UNVERIFIED** in this run: the keyboard-driven test reaches menus/editor/save-name prompt but the expected `Z8REG26.TXT` proof file is not found on disposable A:. Do not attribute that to an application regression without further investigation; keyboard injection or a fixture issue remains possible.
- Harness lessons: uniform wipe PNG may be under 1024 bytes and still be valid; validate decoded image dimensions and distinguish content afterward. Schedule Tcl `exit` *after* the final delayed frame (original final +12s screenshot was scheduled after exit). See [docs/REUSABLE-MSX-EMULATOR-TESTING.md](docs/REUSABLE-MSX-EMULATOR-TESTING.md).


## Fedora CI backend / editor integration checkpoint (2026-11-11)

- The Ubuntu hosted runner's DNS failures for `azure.archive.ubuntu.com` motivated using **Fedora 43 userspace containers** for both jobs; GitHub's host remains Ubuntu. [Fedora toolchain probe 43062958577](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43062958577) passed.
- [Run 43065977217](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43065977217) passed build, standalone Z80 screenshot, integrated multi-page loop, C: read/write/delete and 1395-second 24-frame long run on NMS8250. The runtime job's overall conclusion is FAIL **only because** the editor integration does not return to changing pages; do not conflate passing subtests with an overall PASS.
- The editor automation actually loads `MENU01.TXT`, modifies it, and saves `Z8REG26.TXT` on disposable A: (file content verified). Following screenshots remain at `OPSLAAN`; C: save and return path remain unverified. No change to original `TEKST.SYS` or released disk. See portable Fedora CI notes in `docs/REUSABLE-MSX-EMULATOR-TESTING.md`.
