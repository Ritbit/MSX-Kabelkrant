# Fixed two-title-bar wipe prototype

**Status:** feature-branch-only experimental Z80 alpha; integrated WebMSX
visual acceptance pending.

## Decision

The existing newspaper uses 14 Z80 page wipes. The title bars do not
need the same five-argument rectangular engine. The historical BASIC
title effect at LOOP.SYS lines 3430..3480 copies an 11x49-pixel
background strip left-to-right over the top header, which can also
touch borders and time graphics.

A dedicated **fixed-geometry** Z80 command `CALL WIPE(15)` replaces
that BASIC routine **only** in the separate generated
`KBLTITLE.DSK` disk. It never changes the random page-wipe selection
or the existing `CALL WIPE(1..14)` semantics.

## Exact drawn area

- Top title-band interior: X=0..434, Y=9..22.
- Lower title-band interior: X=0..434, Y=30..43.
- Retains border rows Y=8,23,29,44 and the space between title bars.
- **Retains right-hand clock overlay X=435..511.**
- 54 passes of 8px and a final 3px pass cover precisely 435 columns.
- Each pass executes two V9938 LMMV IMP colour-0 commands,
  one for each 14px-high strip, and waits for VDP idle.
- Frame pacing is 1 JIFFY tick per two passes (around 27 ticks of
  pacing; VDP command execution adds time).

The normal page wipes still use their original fixed newspaper area
X=0..511, Y=50..211. No extra coordinate parameters, clipping rules,
or scaling tables are needed for these two title bars.

## Integration and test

- `z80/asm/wipe_title_bars.asm` implements the dedicated routine.
- `z80/asm/wipe_shared.asm` includes it only under
  `WIPE_TITLE EQU 1`.
- `z80/tools/make_title_wipe.py` generates the isolated assembly
  and LOOP.SYS from the known 14-wipe alpha. Every other branch build
  uses `WIPE_TITLE EQU 0`.
- Generated BASIC retains `GOSUB 3400` and the original INTERVAL
  OFF/ON semantics, but no longer executes the old COPY loop at 3440.
- The published test disk is `assets/KBLTITLE.DSK` once CI succeeds.
  Before publication CI checks the compiled code fits C804..D803
  (4KiB maximum), original RAMdisk machine bytes, and the exact
  disk payload. It checks all other files equal the clean 14-wipe
  regression image.

Preview, after CI publication:

https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLTITLE.DSK

**Do not mark it visually approved until tested.** The accepted
`KBLWIPELEAN.DSK` and `KBLWIPEINT14.DSK` are rollback baselines.

## Separate generic rectangle engine

`CALL WIPE(effect,x1,y1,x2,y2)` remains a *separate experimental
proposal* for other screen areas. It is intentionally **not used**
for title bars; do not add its parser/geometry overhead to the
working 14-wipe resident build without demonstrating a useful case
and proving the memory budget.
