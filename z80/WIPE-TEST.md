# Isolated V9938 wipe test — development only

**Status:** Build + static geometry tests pass; **not yet runtime/visual validated**.
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
`BLOAD "WIPE1.BIN",R` and repeats. This first prototype deliberately
does **not** pace the wipe to video frames, so it may appear nearly
instantaneous and is not visually equivalent to the BASIC animation yet.
It confirms only whether drawing and cleanup work on MSX2.

## Gates before using in full newspaper

1. Check output and screen stability in WebMSX and optionally openMSX.
2. Add deterministic frame pacing, keeping the perceived BASIC duration.
3. Compare completed image and clock/interrupt behaviour against BASIC.
4. Integrate behind an opt-in test switch and expand to effects 2–14.

Never merge this prototype as a finished wipe implementation to `main`.
