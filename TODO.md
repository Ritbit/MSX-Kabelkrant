# Working TODO — Z80 Kabelkrant

**Branch:** `feature/z80-renderer`. Development-only; never merge this
file or the other three coordination docs to `main`.

## Now — make combined ROM dispatch work

- [ ] Determine why BASIC's CALL scan does not reach `46F5h` even with
      mapper segment 2 visible and page-1 slot attribute set.
- [ ] Trace ROM slot-selection / inter-slot dispatch before trying more
      vector patches; capture actual PC, slot and mapper state.
- [ ] Make `CALL KBLVER` succeed in `KBLCOMB.DSK` under openMSX.
- [ ] Verify original drive C: startup and a basic file read/write after
      integrating the new handler.
- [ ] Remove temporary hardcoded `OUT &HFD,2` diagnostic workaround
      when a correct installed handler is available.

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
