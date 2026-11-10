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

## Corrected method: restore background from a left-hand VRAM template

WebMSX screenshot showed that the first revision's two black LMMV fills
removed the coloured title-bar backgrounds and borders, while bits of
right-aligned text remained visible. This behaviour is **not accepted**.

The corrected dedicated routine uses a V9938 **LMMM IMP VRAM-to-VRAM
copy**, matching the idea of original BASIC
`COPY(0,0)-(10,48),0 TO(A,0),0`, rather than drawing black:

- Source: immutable clean template at **X=0..9, Y=0..48**.
- Destination: **X=0..434, Y=0..48**, in **43 passes of 10px**
  followed by **1 pass of 5px**.
- Original per-row colours, horizontal lines, gaps and outlines are
  copied from the template.
- No writes to **X=435..511** (clock and right-hand graphics).
- Calls `LmmmLaunch`, then `WipeSharedIdle`, with deliberate
  JIFFY pacing every two passes.
- Keeps `CALL WIPE(1..14)` and existing newspaper loop unchanged.
- New live visual confirmation is required. Do not claim a successful
  visual test simply because the assembly and disk checks pass.

The first implementation of `wipe_title_bars.asm` has been replaced.
The previously published `KBLTITLE.DSK` will be replaced only if CI
passes and a new cache-safe filename is published for this correction.
No five-argument generic geometry/parser overhead is introduced.

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
