# Z80 development plan

**Development branch only — never merge this document to `main`.**

## Milestone 1 — RAMdisk and TEXT integration (current)

Goal: one startup binary that preserves drive C: and makes the Z80
`CALL TEXT`/version handler reachable from MSX BASIC.

1. Reproduce the original `RAMDISK.BIN` warm-restart handoff and
   document slot/mapper state before and after initialization.
2. Trace BIOS/BASIC extension scan and inter-slot dispatch. Resolve the
   current `CALL KBLVER` error before making larger changes.
3. Validate drive C: read/write behaviour and reload after warm boot.
4. Validate all four fonts; colours 13/15, left and right alignment;
   glyph width, clipping and unsupported ASCII edge cases.
5. Compare actual output and MSX-jiffy performance with BASIC v6.2b.
6. Only then remove demonstrably unused RAMdisk functions if useful.

**Exit:** combined disk boots, C: works, every supported `CALL` works,
original font pixels/colour behaviour match within stated exceptions,
and timing numbers are reproducible.

## Milestone 2 — 14 wipe effects

Implement `CALL WIPE(n)` with V9938 command batching. Reproduce
effects 1–14 from `src/LOOP.SYS` lines 3100–3390, including direction
and outlines. Decouple drawing speed from frame pacing.

**Exit:** each effect matches the BASIC reference visually/pixelwise at
equivalent animation duration, and measured work time improves.

## Milestone 3 — title-bar and screen transitions

Port lines 3400–3480 and, if measurements justify it, the full-screen
transitions around 2000–2080 and 3800–3880. Respect page boundaries,
palette and clock interrupts.

**Exit:** identical output and no clock/interrupt regressions.

## Milestone 4 — lower-priority candidates

Profile and possibly port intro block drawing and hourglass animation.
Keep the analogue clock, file parsing and string handling in BASIC unless
measurements show a worthwhile improvement. Existing uppercase/strip
`USR` helpers should be preserved or integrated only after their ABI is
verified.

## Milestone 5 — integration and release

- Full unattended multi-page run on NMS 8250 emulator; test menu/editing
  flows, drive C:, palette recovery and malformed page content.
- Benchmark representative workloads against **published v6.2b**.
- Create a **new clean release branch off main** containing only reviewed
  production modifications. Never include `CONTEXT.md`, `AGENTS.md`,
  `PLAN.md`, `TODO.md` or unrelated experimental artifacts.
- Build/review a release disk, ZIP and release notes separately.
