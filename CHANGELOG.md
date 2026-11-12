# Changelog

This changelog records the public archive history, not every original 1990s development change.

## 6.2b — 2026 maintenance release

- 2026-11-12 maintenance re-spin: correct `LOOP.SYS` line 1330 weekday calculation for 2000–2089 (including the leap-year 2000 boundary), retaining the original 1990–2089 two-digit-year pivot and weekday/week-record numbering. Validate all 36,525 dates; rebuild the BASIC disk image and ZIP without changing the historical 6.2 disk or the other 27 files. [CI build](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43237807415).

- 2026-11-10 maintenance re-spin: replace `GOSUB 2200` with `GOTO 2200` at line 190 in `LOOP.SYS`. The page loop restarts using `GOTO 140` without returning, so the original entry could accumulate BASIC return frames. All historical and other 6.2b files remain unchanged.


- Rebuilt the bootable MSX2 disk image and readable ZIP from the corrected BASIC sources.
- Load `KRANT3.SC7` instead of `KRANT4.SC7`, enabling all four proportional fonts.
- Correct font-1/font-3 atlas Y coordinates and the typo at `X(2,20)` (18 → 158), without modifying `X.DAT`.
- Optimize SCREEN 7 BASIC text drawing: direct VRAM copies for white, positive-X text and a dedicated scratch line for coloured/right-aligned text.
- Keep the historical 6.2 release files alongside the new 6.2b files.
- Benchmark (openMSX, NMS 8250): approximately 20–21% faster for white text, with smaller gains for coloured or right-aligned text; not a full-system benchmark.
- No experimental Z80 text engine is included in this release.

## 2026

- Source prepared for publication as a historical GitHub archive.
- Initial documentation added.
- GPLv3-or-later license selected.

## 1990s

- Version 6 of the MSX2 Kabelkrant system was used on the internal television system of a local hospital.
- The system evolved from earlier versions developed in previous years.

More detailed historical version information can be reconstructed later.
