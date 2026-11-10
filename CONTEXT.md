# Development context — Z80 Kabelkrant

> **Private-to-development documentation in a public branch.** This file and
> `AGENTS.md`, `PLAN.md`, `TODO.md`, `BUILD-AND-TEST.md`,
> `HOWTO-TESTING.md` belong to
> `feature/z80-renderer` **only**. Never include them in a PR to `main`.
> Updated 2026-11-09; verify current GitHub Actions results before trusting
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
- `HOWTO-TESTING.md`: canonical ROM identification rules, test evidence levels and regression checklist.

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
executions, rendered real news page. **Known regression:** machine
re-enters the boot sequence at roughly 140–145 emulated seconds.
Do not promote alpha as stable or merge the feature branch wholesale.
