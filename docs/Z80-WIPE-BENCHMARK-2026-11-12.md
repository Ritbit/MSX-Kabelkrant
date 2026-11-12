# Measured BASIC vs Z80 wipe performance — NMS8250 (12 November 2026)

**Verified Fedora/openMSX CI:** [run 43226534570](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43226534570) on `feature/z80-renderer` (full build and runtime job PASS).

The auto-start test disk `KBLWIAUTO.DSK` tests the **original 14 BASIC wipe bodies** against the 14 integrated Z80 `CALL WIPE(I)` effects on the **same emulated Philips NMS8250**. The guest's `TIME` variable measures emulated jiffies. For the native code, the refined benchmark runs **25 sequential calls per mode** before reading `TIME`, reducing 1-jiffy quantization error. Guest BASIC writes `BENCHRES.CSV` to a temporary A: disk; CI parses it to `benchmark.json`. Both files are retained in the run's `openmsx-NMS8250-benchmark-and-clock` artifact.

## Refined 25-call measurements

| Wipe | BASIC, 1 call (jiffies) | Z80, 25 calls (jiffies) | Mean Z80, 1 call (jiffies) | Speedup |
|---:|---:|---:|---:|---:|
| 1 | 56 | 30 | 1.20 | 46.67× |
| 2 | 55 | 28 | 1.12 | 49.11× |
| 3 | 130 | 25 | 1.00 | 130.00× |
| 4 | 129 | 41 | 1.64 | 78.66× |
| 5 | 58 | 28 | 1.12 | 51.79× |
| 6 | 130 | 34 | 1.36 | 95.59× |
| 7 | 58 | 25 | 1.00 | 58.00× |
| 8 | 130 | 33 | 1.32 | 98.48× |
| 9 | 420 | 30 | 1.20 | 350.00× |
| 10 | 420 | 25 | 1.00 | 420.00× |
| 11 | 112 | 33 | 1.32 | 84.85× |
| 12 | 193 | 31 | 1.24 | 155.65× |
| 13 | 193 | 48 | 1.92 | 100.52× |
| 14 | 185 | 33 | 1.32 | 140.15× |
| **Total** | **2,269** | **444** | **17.76** | **127.76×** |

The **aggregate speedup** is `2269 / (444 / 25) = 127.76×`; the unweighted mean of individual speedup ratios is **132.82×**. The average Z80 call per mode measures approximately **1.00–1.92 jiffies** (20–38 ms at 50 Hz), while the original BASIC wipes take 55–420 jiffies (1.10–8.40 seconds). Guest `FRE(0)` measured **13,558 bytes** before running the benchmark.

These numbers supersede the preliminary one-call-only benchmark from [run 43223383149](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43223383149), where quantization yielded an inflated aggregate ratio of 141.75×. The refined run measures 25 native calls, not just one.

## Scope and limitations

- **This is a wipe-body CALL timing comparison**, not total elapsed time for a complete KabelKrant page (BASIC logic, file I/O, text rendering, page transitions and title/clock updates).
- These are MSX `TIME` jiffies on the NMS8250, *not* host wall-clock timings; `set throttle off` only speeds up the host execution of the emulator.
- BASIC #14 and corrected native #14 intentionally differ in final geometric behavior; the comparison is functional, not pixel-exact.
- Even 25-call averaging cannot prove visual equivalence or animation pacing; those have separate user-reviewed WebMSX and integrated openMSX captures. No inference about frame rendering should be made from a lone `CALL` duration.
- The free BASIC memory value depends on the loaded BASIC program and runtime state; this is not a universal limit after all menus/editor paths.

## Editor, clock and stable runtime in same run

- Editor/menu: loaded `MENU01.TXT`, modified and overwrote it on a disposable A: disk, verified text contents and returned to changing broadcast pages. This uses the existing-file path; writing a brand-new extra file on a nearly full C: RAMdisk is **not** thereby proven.
- RAMdisk read/write/delete proof, standalone renderer and 1,395-second (23-minute) multi-page loop passed.
- RTC test-only program independently recorded `23:59:50 → 00:00:00` and `FRE(0)=15,605` in `A:CLOCK.OK`.
- In a **separate direct-initializer test** the real `LOOP.SYS` continued displaying distinct pages after an inline `SET TIME "23:59:50"`, with RGB differences **28.718, 21.748, 9.7 and 26.485** across five screenshots at 120–300 emulated seconds. Unlike this direct case, the separate `CLOCKCHK.BAS`-then-`RUN LOOP.SYS` fixture showed a static screen after writing its proof. Do not treat that fixture's static screen as evidence of a production freeze; why that extra program affects the subsequent render remains uninvestigated.
- The live clock screenshots show a **pre-existing weekday-name discrepancy** for 2026 dates (e.g. Friday 13 Nov 2026 rendered as Saturday). This is separate from Z80 rendering and RTC rollover.

All changed BASIC files for these tests are written to **disposable test images only**. No system ROM binaries, original 6.2b release binaries or `main` are modified.
