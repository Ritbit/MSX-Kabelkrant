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
