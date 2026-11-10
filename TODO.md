# Working TODO — Z80 Kabelkrant

**Branch:** `feature/z80-renderer`. Development-only; never merge this
file or the other three coordination docs to `main`.

## Now — one-file loader boots in WebMSX (2026-11-10)

- [x] Trace BASIC CALL into slot 3-2/segment 2; it reaches 46F5h.
- [x] Find destructive zero-fill at 41B3h (PC 41BFh writes 00h).
- [x] Stage one-file TEXT at C804 and reserve HIMEM before intro; user confirms the newspaper works with no E1/E1B/E2/E3 errors in WebMSX.
- [ ] Validate CALL dispatch, drive C: read/write and BASIC memory limits.
- [x] Build separate one-file alpha while retaining working two-file fallback.
- [x] User confirmed several complete newspaper page cycles with one-file alpha and no observed issues (2026-11-10).
- [ ] Validate RAMdisk C: read/write and editor paths for one-file alpha before removing fallback.
- [x] CI gates the built single-BLOAD disk by verifying embedded RAMdisk/TEXT byte ranges, exact BASIC files and all 6.2b baseline files.
- [ ] Remove diagnostic mapper pokes from any production candidate.

## Full Kabelkrant Z80 alpha (WebMSX smoke passed; not release-stable)

- [x] Load original RAMdisk first and Z80 TEXT at C804h after warmstart.
- [x] Remove unused BASIC font array and renderer from *test* LOOP.SYS;
      include original LOOPBAS.SYS in the testdisk.
- [x] Boot full application, draw a news page and verify Z80 CALL handler
      repeatedly invoked in openMSX NMS 8250.
- [x] Fix the deterministic `LDIR`/`BC=0` RAM corruption; WebMSX user confirmed broadcast continues past page 3 (2026-11-10).
- [ ] Run automated multi-page / editor / clock / C: I/O regressions with
      this exact full disk image before claiming runtime stability.

- [x] Add CI checks for the built FAT12 preview, text binary/load address, the BASIC page loop and unmodified baseline files.

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

- [x] Build isolated Z80/V9938 wipe #1 (top-down) drawing kernel; compile and geometry-check under CI, without changing the live newspaper.
- [x] User confirmed isolated wipes #1–#13 work in WebMSX, including corrected wipe #2.
- [x] User accepts wipe #14 with known residual diagonal artifacts after alignment + terminal black clear; functional, not pixel-perfect.
- [x] User visually confirmed wipe #13.
- [x] Validate corrected #14 terminal black fill in WebMSX; user accepts remaining diagonal artifacts.
- [x] Add compiled wipe+TEXT memory-budget audit and dedicated integration design (`z80/WIPE-INTEGRATION.md`).
- [x] Implement shared `CALL WIPE(n)` engine for all 14 in a **separate** opt-in onefile image (`KBLWIPEINT14.DSK`): 3775 bytes within 4096-byte reserved area; retain 1..8 and 1..12 fallback alphas.
- [ ] Run new integrated full newspaper through WebMSX/openMSX (rom-backed); validate wipe directions, text, clock, C: I/O, editor, repeated cycles. CI build alone is not runtime approval.
- [ ] Port title-bar wipe if benchmarks warrant it.
- [ ] Benchmark screen transitions, intro and hourglass before porting.
- [ ] Full Kabelkrant multi-page integration tests and clean release PR.

## Completion log

- [x] BASIC-only v6.2b independently released on `main`.
- [x] Standalone assembly `CALL TEXT`: four fonts, white/13 and
      positive/negative-X tested in openMSX.
- [x] Build first combined `KBLALL.BIN`; stays within one 16-KiB bank.
- [x] Diagnose old `KBLALL.BIN` collision with RAMdisk storage; do not promote that unsafe binary. New *distinct* one-file `KBLRAMTX.BIN` stages TEXT above C800 and boots in WebMSX.

Keep this list short and current: move resolved technical detail to
`z80/COMBINED-STATUS.md`, not into an ever-growing TODO.
