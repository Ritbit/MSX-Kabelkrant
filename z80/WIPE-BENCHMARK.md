# BASIC versus Z80 wipes — reproducible A/B benchmark

**Branch:** `feature/z80-renderer` only. No `main` changes.

## Generated images (2026-11-10)

- `KBLWIPEINT14.DSK`: accepted integrated newspaper, **original BASIC wipes
  still embedded but bypassed**. Keep as rollback.
- `KBLWIPELEAN.DSK`: same code/data/autoexec and composite machine-code
  payload, but generated LOOP.SYS removes original BASIC wipe bodies
  3240..3370 and unused headings/comments 3150..3230.
  The dispatcher retains 3125, 3130, 3380 and 3390 (interrupts and RETURN).
  The original BASIC `ON A GOTO` selected wipe #1 when A=0 or 15, so the
  new dispatcher explicitly maps those two out-of-range values to #1.
- `KBLWIBENCH.DSK`: exact copy of `KBLWIPELEAN.DSK` **plus**
  `BENCHW.BAS`, a generated MSX BASIC A/B timing harness.

Both disks are actual verified 720-KiB FAT12 images, published as raw
assets on the feature branch. CI checks all existing disk files are
byte-identical to the parent image except the stated LOOP replacement
and added benchmark. The original 14 BASIC wipe bodies in the benchmark
are extracted unchanged from `src/LOOP.SYS`, except their final
`: GOTO 3380` becomes `: RETURN` for GOSUB measurement.

## What has been measured already

| Property | Result |
|---|---|
| Original integrated LOOP.SYS (ASCII on disk) | 12,555 bytes |
| Lean LOOP.SYS (ASCII on disk) | 10,294 bytes |
| Reduction in **ASCII disk file** | **2,261 bytes** |
| Shared TEXT+14 wipes resident Z80 code | 3,775 bytes (unchanged) |
| TEXT-only resident Z80 code | 2,131 bytes |
| Incremental Z80 code for 14 wipes | **1,644 bytes** |
| Safe reserved code region | 4,096 bytes; 321 free |

**Important:** the 2,261-byte ASCII file reduction does *not* equal
free MSX BASIC RAM: BASIC tokenizes program keywords, numbers and line
links on loading. A BASIC `FRE(0)` comparison can quantify the actual
difference in the emulator. The 1,644-byte Z80 increment resides inside
an already reserved 4-KiB region; the memory-mapped reservation still
occupies 4 KiB even though fewer payload bytes are used.

## Run timing benchmark in WebMSX

Open the benchmark image (preserves the production-like intro and
RAMdisk setup):

https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIBENCH.DSK

1. Let Kabelkrant boot so the `CALL WIPE` handler is installed.
2. Use **Ctrl+Stop** to enter BASIC, then `RUN "A:BENCHW.BAS"`.
3. The program initializes SCREEN 7 once, then loops effects 1..14.
   Before *each* timed section it fills X0..511 Y50..211 with colour 14.
   For a given effect it times first the historical BASIC FOR/LINE
   routine and then the resident `CALL WIPE(I)` on the same hardware.
   Both use `TIME` (BIOS JIFFY, typically 50 Hz on European MSX,
   60 Hz on NTSC). The program handles a 16-bit TIME wrap.
4. At completion it displays 14 rows: BASIC jiffies, Z80 jiffies and
   Z80/BASIC ratio. Share or save the screenshot/results.
   A ratio **less than 1** means the full Z80 animation completed faster.

This measures **wall-clock animation duration including deliberate Z80
frame-pacing**, not pure Z80 instruction throughput. The BASIC reference
uses original wipe #14 geometry while the accepted assembly version
recentres the inner rectangles and applies a full final black fill,
so #14 is not strictly equivalent pixelwise.

No benchmark timings are claimed here: the current CI emulator job
skips the actual openMSX run because the required ROM secrets are not
configured. A green Actions run means *build and packaging* passed.

## Measure actual free BASIC RAM

For a controlled comparison of the program memory footprint:

- Boot the accepted integrated original image and stop in BASIC.
  After `LOAD "A:LOOP.SYS"`, record `PRINT FRE(0)`.
- Reset and boot the clean image with the same MSX2 hardware/memory.
  Again `LOAD "A:LOOP.SYS"` and record `PRINT FRE(0)`.

Do **not** use `RUN` for this memory comparison. The loaded programs
must both be at BASIC's prompt, with the same HIMEM setup, and without
other variables. The difference between the two readings is the
effective BASIC free-memory improvement from removing the obsolete
BASIC wipes. This is not a measurement of the 4-KiB machine-code
reservation. If the two images are loaded with different HIMEM or other
environmental state, the readings are not directly comparable.

## Decision rule

Do not drop the verified shared Z80 engine merely because its code
needs 1,644 bytes. Compare measured BASIC free-memory delta, animation
time by effect, page-clock stability and the 321 bytes of remaining
reserved space. If most Z80 effects are no faster, retaining BASIC
may be a better maintenance decision. If smoother/faster, keep the lean
Z80 version and avoid further native ports until memory layout changes.

No changes to the BASIC-only v6.2b release or main branch.

## Auto-start timing disk (preferred)

An additional distinct disk `KBLWIAUTO.DSK` has been built and verified.
It is byte-identical to `KBLWIBENCH.DSK`, except its KBLINIT.SYS
adds line 198: `RUN "A:BENCHW.BAS"` after line 195 installs the
shared Z80 TEXT/WIPE extension. Thus the benchmark runs automatically
on boot, requiring no Ctrl+Stop or BASIC prompt.

WebMSX auto-benchmark:

https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLWIAUTO.DSK

Wait for the final fourteen-row table. Save a screenshot of BASIC ticks,
Z80 ticks and the Z80/BASIC ratios for interpretation. The test includes
deliberate Z80 frame pacing; the original BASIC wipe #14 still uses
its historical misaligned rectangle coordinates. GitHub Actions
verifies code and disk image, but cannot run MSX BASIC without the
optional licensed ROM secrets, so no timing results are claimed yet.
