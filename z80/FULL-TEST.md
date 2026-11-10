# Full Kabelkrant Z80 preview test disk

**Status: alpha / development-only. This is not a 6.2b replacement.**

The workflow `.github/workflows/z80-build.yml` publishes
`KBLZ80TEST-full-Kabelkrant-EXPERIMENTAL`, containing `KBLZ80TEST.DSK`.

## Contents

Built from the **published 6.2b** image checked out separately from
`main`. The original RAMdisk, clock, page data, palette and graphics
remain unchanged. Only the generated `KBLINIT.SYS` and `LOOP.SYS`
are substituted; `KBLTXT.BIN` is added.

- `KBLINIT.SYS`: reserve high RAM at `C800h`, then BLOAD/R the Z80
  text engine after the historical RAMdisk warm-start.
- `LOOP.SYS`: replace seven `GOSUB 2500` calls with
  `CALL TEXT(A$,X,Y,LT,K)`; retain the original page/clock logic;
  reserve `C800h` across its second `CLEAR`.
- Remove the **unused** BASIC font drawing subroutine and `X(4,110)`
  double array from the generated test `LOOP.SYS`. Otherwise BASIC
  triggers `ERR=7` (out of memory) at line 1050.
- `LOOPBAS.SYS`: the untouched 6.2b `LOOP.SYS` on the same test disk
  as a source/diagnostic fallback. It is **not** automatically loaded.

No changes have been made to the released 6.2b files or `main`.

## Verified under openMSX (Philips NMS 8250)

Using the exact CI disk image, emulator breakpoints confirmed:

- RAMdisk installation at C000h.
- Text engine initialization at C806h.
- Repeated calls into Z80 text handler C82Ah.
- Real Cablekrant broadcast page with clock, right-aligned coloured
  title and multiple body lines displayed around 130 emulated seconds.

**Known regression:** Around 140–145 emulated seconds, the test machine
returns to the MSX boot/autoexec sequence. This does not happen during
the same interval with the unmodified 6.2b disk. It requires further
runtime trace and is **not considered stable or fully integrated**.

Do not promote the disk to GitHub Releases, change `main`, or claim
long-run stability until the unexpected reset is understood.

## Run it

Download the `KBLZ80TEST-full-Kabelkrant-EXPERIMENTAL` artifact from
the latest successful development-branch GitHub Actions workflow.
Unzip it; the file is named `KBLZ80TEST.DSK`.

Use openMSX:

```sh
openmsx -machine Philips_NMS_8250 -diska KBLZ80TEST.DSK
```

Or use WebMSX, choose `MSX2E`, and insert the **local diskimage** via
its disk menu. A GitHub Actions artifact link is not a raw DSK URL.

The standalone renderer demo `KBLASM.DSK` remains a separate test
and does not exercise the historical RAMdisk/page loop.

## 2026-11-10: potential page-three crash cause

Source review identified a deterministic memory-corruption bug in the Z80
`CALL TEXT` argument copy: `LDIR` was reached when the string length
was zero (`BC=0`). On the Z80, this copies 65,536 bytes, overwriting
RAM instead of doing no work. Valid empty lines in page files can reach
`CALL TEXT("")` (the original BASIC loop skips a single blank space,
but not an empty string). The assembly now skips `LDIR` for zero-length
strings and a regression test checks this guard. This is a **strong
candidate**, not yet an emulator-confirmed explanation for the crash.

Independently, generated test `LOOP.SYS` now enters the non-returning
page cycle with `GOTO 2200` rather than `GOSUB 2200`, preventing a
return-stack leak at each `GOTO 140` cycle restart.

Development-only WebMSX preview (built on CI and published as a raw DSK):

```text
https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLZ80TEST.DSK
```

## Next tests

Identify the reset around 140–145 s with an openMSX trace (PC/stack/
reset vector and current BASIC line), exercise the full cycle,
and benchmark with equal page content against 6.2b.
