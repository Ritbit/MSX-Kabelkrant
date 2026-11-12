# NMS8250 BASIC-versus-Z80 wipe benchmark — 12 November 2026

**Verified ROM-backed openMSX result:** [GitHub Actions run 43223383149](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43223383149), `feature/z80-renderer`. Test disk `KBLWIAUTO.DSK` generated from the accepted 14-wipe integrated variant. The benchmark runs both original BASIC wipe bodies and the new native `CALL WIPE(I)` on the **same** emulated Philips NMS8250, writing `BENCHRES.CSV` on a disposable A: disk. See CI artifact `openmsx-NMS8250-benchmark-and-clock`.

## Measured one-call jiffies

| Effect | BASIC jiffies | Z80 jiffies | Basic / Z80 |
|---:|---:|---:|---:|
| 1 | 56 | 1 | 56.0× |
| 2 | 56 | 1 | 56.0× |
| 3 | 130 | 1 | 130.0× |
| 4 | 129 | 2 | 64.5× |
| 5 | 58 | 1 | 58.0× |
| 6 | 130 | 2 | 65.0× |
| 7 | 59 | 1 | 59.0× |
| 8 | 130 | 1 | 130.0× |
| 9 | 419 | 1 | 419.0× |
| 10 | 419 | 1 | 419.0× |
| 11 | 112 | 1 | 112.0× |
| 12 | 194 | 1 | 194.0× |
| 13 | 192 | 1 | 192.0× |
| 14 | 184 | 1 | 184.0× |
| **Sum** | **2,268** | **16** | **141.75×** |

On this PAL MSX emulator, a jiffy is approximately 20 ms. BASIC single-wipe call timings ranged from 1.12–8.38 seconds; Z80 returned in 1–2 jiffies per invocation. The arithmetic mean of the **individual** ratios is 152.75×; the ratio of the **summed** timings is 141.75×. `FRE(0)` before the benchmark was **13,601 bytes**.

## How to interpret these results

- The benchmark measures elapsed MSX BASIC `TIME` around the two **wipe call bodies**, not a complete newspaper page (title rendering, file I/O, main loop and clock continue outside this scope).
- The Z80 result has **very coarse resolution** (one or two 20 ms jiffies). Ratios such as 419× are sensitive to quantisation and should not be advertised as precise visual animation speedups. Repeated-call averaging would improve confidence.
- The original BASIC wipe #14 and corrected native #14 have known different geometry.
- Headless openMSX with `set throttle off` accelerates wall-clock execution but MSX `TIME` is an emulated-jiffy measurement.
- MSX BASIC memory figure `FRE(0)` depends on the currently loaded program/strings; it is **not** a proof of free RAM after every possible operator workflow.

## Other runtime evidence from same run

- Editor: existing `MENU01.TXT` loaded, modified and overwritten on disposable A:; contents verified; returned to changing newspaper pages. The earlier extra-file save to `Z8REG26.TXT` had stuck at `OPSLAAN`; overwriting avoids extra RAMdisk allocation.
- Clock: test-only BASIC wrote `A:CLOCK.OK` with `PASS RTC,23:59:50,00:00:00` and `FRE0, 15605`. However, the four 150–310-second screenshots of the subsequent broadcast were identical; **ongoing page progression across the forced midnight event is not yet proven**. A separate direct-initializer diagnostic follows.
- Build, 14-wipe page loop, C: read/write/delete and 1,395s unattended multi-page regression passed.

The benchmark and midnight test alter only *disposable test disks*, not stable v6.2b or the accepted Z80 release candidate. No system ROM binaries are committed.
