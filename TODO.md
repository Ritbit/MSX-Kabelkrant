# Working TODO — Z80 Kabelkrant

**Branch:** `feature/z80-renderer`. Development-only; never merge this
file or the other three coordination docs to `main`.

## Now — confirmed RAMdisk memory collision

- [x] Trace BASIC CALL into slot 3-2/segment 2; it reaches 46F5h.
- [x] Find destructive zero-fill at 41B3h (PC 41BFh writes 00h).
- [ ] Safely stage TEXT in protected page-3 RAM after RAMdisk restart.
- [ ] Validate CALL dispatch, drive C: read/write and BASIC memory limits.
- [ ] Decide on one-file two-stage loader or a proven two-file fallback.
- [ ] Remove diagnostic mapper pokes from any production candidate.

## Next — functional and performance parity

- [ ] Exercise all ASCII 33–127 per font; define a deliberate fallback
      for font 3 / ASCII 127 instead of reading the sentinel.
- [ ] Compare font pixels, colour 13/15, transparency, clipping and
      negative-X alignment against the BASIC v6.2b renderer.
- [ ] Benchmark both renderers with identical strings on the same NMS 8250
      environment; record MSX jiffies and test limitations.
- [ ] Decide whether any RAMdisk functionality is genuinely unused
      **after** call graph + C: regression tests.

## Later — acceleration roadmap

- [ ] Implement and test `CALL WIPE(n)`, n=1..14; preserve frame pacing.
- [ ] Port title-bar wipe if benchmarks warrant it.
- [ ] Benchmark screen transitions, intro and hourglass before porting.
- [ ] Full Kabelkrant multi-page integration tests and clean release PR.

## Completion log

- [x] BASIC-only v6.2b independently released on `main`.
- [x] Standalone assembly `CALL TEXT`: four fonts, white/13 and
      positive/negative-X tested in openMSX.
- [x] Build first combined `KBLALL.BIN`; stays within one 16-KiB bank.
- [x] Confirm combined `CALL KBLVER` still fails at BASIC line 80:
      do not promote the binary as production-ready.

Keep this list short and current: move resolved technical detail to
`z80/COMBINED-STATUS.md`, not into an ever-growing TODO.
