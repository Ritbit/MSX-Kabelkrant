# Changelog

This changelog records the public archive history, not every original 1990s development change.

## 6.2b — 2026 maintenance release

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
