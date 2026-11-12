# Working TODO — KabelKrant Z80 (12 November 2026)

**Development branch:** `feature/z80-renderer`. Do not merge this coordination document or `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, `HOWTO-TESTING.md`, `BUILD-AND-TEST.md` to `main`. The detailed older run log has been preserved in [docs/TEST-HISTORY-2026-11.md](docs/TEST-HISTORY-2026-11.md).

## Core acceptance — DONE

- [x] BASIC 6.2b maintenance weekday fix merged to `main` (2026-11-12); release DSK and ZIP rebuilt with 27 other original files preserved.
- [x] Combined RAMdisk+Z80 TEXT engine boots and runs; all four fonts, 14 Z80 wipes and the corrected title wipe were previously accepted in WebMSX.
- [x] Fedora 43 container for both build and openMSX jobs; no Ubuntu APT dependency.
- [x] Repeatable [NMS8250 full CI run 43226534570](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43226534570): build/assembly/tests, standalone renderer, integrated multi-page loop, RAMdisk C: read/write/delete, **1,395 seconds** unattended, editor/menu load-edit-save-to-existing-A:-file and return to broadcast **all PASS**.
- [x] Guest RTC midnight rollover `23:59:50 -> 00:00:00` confirmed via `A:CLOCK.OK`; independent direct-init `SET TIME` test confirms live `LOOP.SYS` continues changing pages after midnight. Both steps now gate CI.
- [x] `FRE(0)` measured (13,558 B in benchmark; 15,605 B in independent RTC probe). This is program-state-specific, not a general all-workflows memory guarantee.
- [x] 14 BASIC vs Z80 wipe benchmarks measured in MSX `TIME` jiffies. **25 consecutive Z80 calls per wipe** reduce timing quantization: aggregate wipe-body time improvement **127.76×**, arithmetic mean individual ratio **132.82×**. See [docs/Z80-WIPE-BENCHMARK-2026-11-12.md](docs/Z80-WIPE-BENCHMARK-2026-11-12.md), [CI run 43226534570](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43226534570) and `openmsx-NMS8250-benchmark-and-clock` artifact.
- [x] Reusable test guidance in [docs/REUSABLE-MSX-EMULATOR-TESTING.md](docs/REUSABLE-MSX-EMULATOR-TESTING.md).

## Remaining before any release

- [ ] Prepare a **clean release branch from `main`**, selecting only approved production changes and relevant tests; exclude experimental alphas, machine ROMs and all development coordination docs.
- [ ] Verify final release candidate file set and exact disk checksum; perform one final ROM-backed CI run and optional manual WebMSX visual check on that exact image.
- [ ] Open/review a narrowly scoped release PR, check changed files before merging; ask for explicit release approval. **No merge or release requested yet.**

## Independent follow-ups, not core Z80 blockers

- [x] Fixed original 19xx weekday arithmetic for the supported 1990–2089 range (2026-11-13 now Friday). 36,525 dates validated on both branches; 217 cases additionally executed in real NMS8250 BASIC with `A:WDAY.OK`. `main` BASIC 6.2b rebuilt/released; see `z80/WEEKDAY-REGRESSION.md`.
- [ ] Test creation of **additional new** editor C: files with RAMdisk nearly full. Overwriting an existing page is now verified A: and return-to-loop; prior extra-file `Z8REG26.TXT` attempt wrote A: but stalled in the C: save path. Avoid claiming arbitrary free capacity.
- [ ] Optional: edge-font ASCII 127, pixel-exact 6.2b renderer parity, full end-to-end page timing (vs wipe bodies), and five-argument rectangular wipe experiment. None was part of the accepted 14-wipe engine test scope.
- [ ] Diagnostic only: explain why the extra test-only `CLOCKCHK.BAS` program that independently proves RTC rollover leaves a static subsequent screen whereas direct inline `SET TIME` + original `LOOP.SYS` progresses normally. The CI release gate uses the **direct** route.
- [ ] Consider a self-hosted Oracle Linux/CentOS Stream runner later only if needed; current Fedora container CI is operational.

**Read for reproducibility:** `HOWTO-TESTING.md`, `docs/REUSABLE-MSX-EMULATOR-TESTING.md`, `docs/Z80-WIPE-BENCHMARK-2026-11-12.md`. Historical test failures/lessons are in `docs/TEST-HISTORY-2026-11.md`.
