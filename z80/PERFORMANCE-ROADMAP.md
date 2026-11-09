# Z80 performance roadmap — Kabelkrant (after BASIC 6.2b)

Source audit: `src/LOOP.SYS` on `main`. Priorities are hypotheses until
A/B measurements on an MSX2 emulator and (ideally) real NMS 8250 hardware.
Do not change the released `v6.2b` assets.

| Priority | Candidate | BASIC locations | Why | Recommendation |
| --- | --- | --- | --- | --- |
| P0 | Proportional text | `2500–2690` | Per-character BASIC loop, X.DAT lookup, VRAM copies | Finish combined RAMdisk+TEXT CALL interface; compare glyph-by-glyph against BASIC |
| P1 | 14 wipe effects | `3100–3390` | 82–516 BASIC `LINE` operations per transition | Implement `CALL WIPE(n)` / V9938 command batches; benchmark and pace via vblank |
| P2 | Header wipe | `3400–3480` | 43 `COPY` commands per page transition | Add to shared wipe implementation |
| P2 | Full-screen transition | `2000–2080`, `3800–3880` | 213 and 211 BASIC `LINE`/VDP steps respectively | Fold into same graphics engine; maintain vertical-scroll behavior |
| P3 | Intro block pattern | `1500–1640` | Up to 550 BASIC string checks and many `COPY` operations | Optimize only if measured startup delay matters; runs infrequently |
| P3 | Hourglass/progress animation | `3500–3790` | 110 per-iteration `INT`, `COPY`, and delay loops | Possibly issue blits from Z80; keep intentional animation timing |
| P4 | Analog clock | `2900–3050` | 6 short `LINE` operations per update | Leave in BASIC unless contention/latency is measured |
| P4 | Disk and strings | `1400–1490`, `2200–2410` | Mostly RAMdisk reads and BASIC parsing | Keep existing USR uppercase/strip helpers; profile before rewriting |

## Wipe analysis

The 14 wipe effects at `3240–3370` run a total of **82–516**
`LINE` commands each. The current title wipe adds another 43 `COPY`
commands at `3440–3460`. The large number of BASIC loop iterations
and repeated VDP parameter setup make wipes the best next optimization
after text.

Do not merely execute them as quickly as possible: the visible wipe
duration and ordering are part of the user experience. Separate
*rendering work* from *frame pacing*: use the V9938 command-completion
bit (S#2 CE) for correctness, and vblank/frame ticks for animation speed.
Some transitions use outlines rather than fills; implement those using
appropriate VDP commands rather than approximating with rectangles.

SCREEN 7 is 4bpp, so byte-aligned fill commands (HMMV) have constraints.
Use LMMV when pixel-precise edges/colours are needed and benchmark
HMMV for compatible even-pixel rectangles.

## Reproducible testing

1. Isolated A/B for each wipe: identical SCREEN 7 initial image, compare
   resulting pixels and command extent, then time raw work in MSX jiffies.
2. Repeat with matched target frame duration; confirm that animation is
   not visually shortened by the optimization.
3. Run a multi-page Kabelkrant scenario including clock interrupts,
   font-coloured titles, and RAMdisk C: reads.
4. Only then replace the BASIC `GOSUB` calls in a separate release branch.

## Architectural constraint

The combined RAMdisk+TEXT installer is **not yet runtime-proven**.
The two components need only live for the running session, but the
RAMdisk's C: driver and any BASIC CALL dispatch routines must remain
addressable while in use. Do not remove RAMdisk routines or claim saved
mapper banks before call-graph and slot-dispatch validation.
