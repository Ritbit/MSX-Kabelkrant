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
