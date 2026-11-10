# Isolated V9938 wipe test — development only

**Status (2026-11-10):** The user confirmed isolated effect #1 appears to work in WebMSX. The current updated build adds frame pacing and isolated effect #2; neither paced version has yet been visually validated.
This disk is separate from the user-confirmed working `KBLONEFILE.DSK`
and does not change the newspaper's current BASIC wipes.

## Effect #1: top to bottom

Original BASIC `src/LOOP.SYS` line 3240:

```basic
3240 FOR A = 50 TO 212 STEP 2: LINE(0,A)-(512,A+1),0,BF: NEXT: GOTO 3380
```

`z80/asm/wipe_kernel.asm` uses V9938 SCREEN 7 LMMV fill, black,
x=0..511, two scanlines at a time, y=50..211 (81 visible bands).
The original BASIC final band starts at y=212, beyond visible SCREEN 7.

**Development-only WebMSX test:**

https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE.DSK

The standalone disk `KBLWIPE.DSK` fills a rectangle, calls
`BLOAD "WIPE1.BIN",R` and repeats. The 2026-11-10 updated kernel
waits for command completion and then one MSX BIOS JIFFY tick per
2-scanline band (81 bands). At 50 Hz the wait component alone takes
approximately 1.62 s; at 60 Hz approximately 1.35 s. This is deliberate
frame pacing, but not yet calibrated to the historical BASIC duration.

## Effect #2: bottom to top

Uses the same V9938 fill kernel with the Y sequence reversed:
210,208,...,50; the bottommost visible pair is y=210..211.
This is compiled separately as `WIPE2.BIN` and placed on
`KBLWIPE2.DSK`.

https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-KabelKrant/feature/z80-renderer/assets/KBLWIPE2.DSK

Neither demo is used by the working `KBLONEFILE.DSK` newspaper.

## Gates before using in full newspaper

1. Check output and screen stability in WebMSX and optionally openMSX.
2. Calibrate the JIFFY-based pacing against the perceived BASIC duration.
3. Compare completed image and clock/interrupt behaviour against BASIC.
4. Integrate behind an opt-in test switch and expand to effects 2–14.

Never merge this prototype as a finished wipe implementation to `main`.

### 2026-11-10: wipe #2 assembled as wipe #1 (regression corrected)

Manual WebMSX test showed wipe #2 actually went **top-to-bottom**.
The first machine-code regression test demonstrated that `WIPE1.BIN`
and `WIPE2.BIN` were byte-for-byte identical: the old `IFDEF`
assembly test did not select the `WIPE_REVERSE EQU 1` branch.
The assembly now uses numeric `IF WIPE_REVERSE`, with explicit
forward/reverse wrapper files. GitHub CI validates the **compiled**
start-Y immediate (50 vs 210), rejects identical binaries and checks
that `KBLWIPE2.DSK` contains the actual reverse binary.

A separate cache-safe preview is published as `KBLWIPE2FIX.DSK`:

https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE2FIX.DSK

Runtime direction still requires visual confirmation of this corrected build.

## Effects #3 and #4: horizontal wipes (2026-11-10)

The isolated V9938 LMMV kernel in `wipe_horizontal_kernel.asm` fills
two-pixel-wide columns over y=50..211 (162 scanlines), black, SCREEN 7:

- Wipe #3: x=0,2,...510 (left to right); original BASIC line 3260
- Wipe #4: x=510,508,...0 (right to left); original BASIC line 3270

Each effect runs 256 strips. JIFFY pacing occurs after every four
completed strips: approximately 64 video frames of deliberate delay,
or 1.28 s at 50 Hz before VDP overhead. The final visible pixel
is x=511; the original BASIC coordinate x=512 is beyond SCREEN 7.

The direction is set through explicit numerical assembly constants, not
`IFDEF`. CI verifies **actual BLOAD machine-code bytes** for each first
X coordinate, rejects identical binaries, opens both built FAT12 disk
images, and verifies their embedded WIPE3/4 binaries and AUTOEXEC content.

**Test only these isolated previews, not the live newspaper:**

- Wipe #3, left to right:
  https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE3.DSK
- Wipe #4, right to left:
  https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE4.DSK

The CI binary/disk verification has passed; **visual direction and
animation pacing still require WebMSX confirmation**. Do not yet replace
the original BASIC transitions.

## Effects #5 and #6: two edges toward centre (2026-11-10)

The user confirmed both isolated wipes #3 and #4 work correctly in WebMSX.

The new `wipe_centre_kernel.asm` builds two different **standalone**
BLOAD/R binaries. Geometry is based on visible SCREEN 7 pixels, with
clipped original BASIC boundary coordinates:

- **Wipe #5 (BASIC line 3280):** top and bottom simultaneously toward
  centre; 41 pairs of 2-scanline black fills. Near Y starts at 50,
  far Y starts at 210, and both converge at 130. Covers Y=50..211.
  One JIFFY wait per pair (about 0.82 s at 50 Hz, plus VDP overhead).
- **Wipe #6 (BASIC line 3290):** left and right simultaneously toward
  centre; 128 pairs of 2-pixel columns. Near X starts at 0, far X starts
  at 510, converging at 254 and 256 respectively. Covers X=0..511.
  One JIFFY wait per two pairs (about 1.28 s at 50 Hz plus overhead).

Both drawing commands finish before the next pair is issued. The
CI gates publishing on checks of the actual **compiled BLOAD binaries**,
the precise coverage of the visible rectangle and the exact binary and
AUTOEXEC embedded inside each FAT12 image. CI passed; the user confirmed **both wipes #5 and #6** work correctly in WebMSX on 2026-11-10.

**Isolated WebMSX tests:**

- Wipe #5, top/bottom to centre:
  https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE5.DSK
- Wipe #6, left/right to centre:
  https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE6.DSK

The full newspaper `KBLONEFILE.DSK` still uses original BASIC wipes.

## Effects #7 and #8: centre outward (2026-11-10)

New isolated binaries in `wipe_outward_kernel.asm`, driven by numeric
`WIPE_FROM_SIDES` constants, reverse the geometry of wipes #5/#6.
Both use black V9938 LMMV two-pixel bands and JIFFY pacing.

- **Wipe #7:** centre toward top and bottom, source BASIC line 3300;
  starts on Y=130 and extends to top Y=50 and bottom Y=210.
  Covers Y=50..211; deliberately clips the historical Y=49 endpoint
  to preserve the title area. 41 pairs, one tick per pair.
- **Wipe #8:** centre toward left and right, source BASIC line 3310;
  starts on X=254 and X=256, ends on X=0 and X=510.
  Covers X=0..511; 128 pairs, one tick every two pairs.

After detecting and correcting an assembly entry-symbol error and a
false-positive binary assertion, the full CI build passed. The build
checks actual BLOAD bytes (including distinct starting coordinates and
pair counts), full visible pixel coverage, and FAT12 image contents.

**WebMSX isolated tests (visual confirmation still needed):**

- #7: https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE7.DSK
- #8: https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE8.DSK

No change to the working one-file newspaper or BASIC 6.2b release.

## Effects #9 and #10: rectangular outlines (2026-11-10)

The user visually confirmed effects **#7 and #8** in WebMSX. All
eight preceding wipes are now confirmed.

The original BASIC lines 3320 and 3330 draw two nested box **outlines**
per iteration (`LINE ...,B`, *not* `BF`). These experimental Z80
approximations draw each two-pixel contour using four V9938 LMMV fills
(two horizontal and two vertical border bands), preserving the interior
until subsequent passes. To avoid out-of-range coordinates, the
precomputed `wipe_rect_table.asm` stores 128 visible rectangles,
x=0..254 in steps of two, y=floor(x*75/256).

- **#9:** outside toward centre (ascending table order), 128 boxes.
- **#10:** centre toward outside (descending table order), 128 boxes.

Frame pacing: one JIFFY wait per two completed outlines (64 waits).
Both binaries are standalone and do not alter the working newspaper.

The CI checks original BASIC line semantics, every table row's bounds,
four border drawing commands, the compiled first table pointer for each
direction and the exact binary stored in each FAT12 disk. Build passed;
**pixel-perfect BASIC parity is not claimed**, and visual WebMSX
confirmation is still needed.

- #9: https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE9.DSK
- #10: https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE10.DSK

## Effects #11–#14 (2026-11-10)

The user confirmed that both #11 (vertical interlaced) and #12
(horizontal interlaced) work in WebMSX. Consequently **wipes #1–#12
are visually confirmed**, including the corrected #2.

The final two wipes are isolated experimental binaries:

- **#13** (original `LOOP.SYS` 3360): four moving vertical 1-pixel
  lines per iteration at x=A, 512-A, 257+A, 257-A, A=0..256 STEP 2.
  A 129-row lookup table preserves this order, using 0FFFFh for
  off-screen coordinates; V9938 LMMV draws only visible columns
  over y=50..211. One JIFFY tick per two iterations.
- **#14** (original `LOOP.SYS` 3370): four different unfilled
  rectangular outlines per iteration, 39 iterations Y=0..76 STEP 2.
  Each original rectangle is converted into four one-pixel V9938
  border strips. A table of 156 records specifies clipped coordinates,
  including the source's inward/outward overlapping rectangle motion.
  One JIFFY tick per four complete outlines.

**Build gates:** CI validates all the precomputed geometry against
independently computed BASIC expressions, loaded BLOAD entry addresses,
the exact data tables in the assembled binaries and the exact FAT12
payloads and AUTOEXEC labels. The CI build passed. Visual parity
of #13/#14 must still be confirmed.

- Wipe #13: https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE13.DSK
- Wipe #14: https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE14.DSK

Neither preview modifies the working one-BLOAD Kabelkrant or BASIC v6.2b.

## Wipe #14 alignment correction (2026-11-10)

The user visually accepted **wipe #13** but identified that the two
nested rectangle systems in #14 were misaligned, just as in BASIC
v6.2b. A geometric audit confirmed the reason:

- Outer rectangles: top=50+Y, bottom=212-Y, centre Y=131.
- Original BASIC inner rectangles: top=120-Y, bottom=119+Y,
  centre Y=119.5. They were shifted **11.5 pixels upward**.
- Experimental Z80 fix: inner top=131-Y, bottom=131+Y,
  centre Y=131, for all 39 steps. Horizontal centre stays X=256.

At the SCREEN 7 bottom boundary the first outer rectangle's bottom
Y=212 is clipped to 211; this one-pixel boundary difference is
intentional. The original BASIC source on main is **not** changed.
The CI tests now assert both geometries share vertical centre Y=131
after clipping allowances, inspect every one of 156 table records,
verify the compiled data table and the embedded FAT12 WIPE14.BIN.

Full CI build succeeded. The corrected preview is provided under a
new cache-safe name (same bytes as the newly built KBLWIPE14.DSK):

https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE14FIX.DSK

**Visual confirmation of this corrected version is still pending.**

## Wipe #14 incomplete clear fix (2026-11-10)

A WebMSX screenshot from the user showed that the alignment-corrected
wipe #14 left un-erased white rectangular outlines. The contour-only
strategy does not mathematically cover every pixel: although the visual
transition is correct, the display was not guaranteed black at return.

The experimental Z80 `wipe14.asm` now adds an **unconditional final
V9938 LMMV colour-0 fill** covering exactly X=0..511 and Y=50..211,
after all 156 outline records have been drawn. It waits for the VDP CE
bit to clear before returning control to BASIC. No title-bar pixels
are modified. The test verifies drawing order, full-rectangle
coordinates in source and compiled opcodes, and embedded FAT12 payload.

The CI build succeeded and a separate browser-cache-safe disk is
published. Runtime appearance of the **new** build still needs visual
confirmation:

https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIPE14FIX2.DSK

This change is **only** to the isolated wipe #14 demo; the working
Kabelkrant onefile and BASIC-only 6.2b have not been modified.
