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
- [x] User confirmed **KBLWIPEINT14.DSK runs the Kabelkrant and all fourteen integrated Z80 wipes in WebMSX** (2026-11-10). This is a manual functional smoke test; not yet C: or editor regression approval.
- [ ] Validate editor/menu paths, longer unattended cycles and clock rollover on **the exact integrated 14-wipe disk**; C: read/write/delete and 255s multi-page loop already passed on the accepted title-integrated test variant (run 43001359714). Preserve rollback preview.
- [x] Build special title Z80 wipe (`CALL WIPE(15)`) in isolated `KBLTITLE.DSK`; initial black-fill version rejected by user screenshot (destroyed title background and left old text). Fixed using opaque VRAM LMMM template copy X0..9/Y0..48 -> X0..434/Y0..48 while preserving clock X435..511. CI passes at **3879/4096 bytes**, leaving **217 bytes**.
- [x] User visually approved `KBLTITLECOPY.DSK` in WebMSX (2026-11-10): title backgrounds and lines restore correctly, old title clears and clock is preserved. Keep `KBLWIPELEAN.DSK` as rollback.
- [ ] Treat the five-argument rectangular wipe proposal as independent experimental development; **do not** use for title bars.
- [x] Generate lean 14-Z80-wipe test disk removing obsolete BASIC wipes; ASCII LOOP.SYS shrank 2,261 bytes (12,555 to 10,294), **not yet measured in tokenized BASIC RAM**.
- [x] Generate paired BASIC-versus-Z80 timing benchmark disk (`KBLWIBENCH.DSK`) with all 14 exact original BASIC loops and 14 shared native modes; CI verified disk/source parity.
- [ ] Run `BENCHW.BAS` on WebMSX/openMSX with ROMs; collect 14 measured BASIC/Z80 JIFFY pairs and compare actual RAM using `FRE(0)`. CI cannot execute MSX BASIC without ROMs.
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

## NMS8250 automated regression (2026-11-10)
- [x] Prepare disposable 14-wipe+title disk C: test that writes an A: proof marker **only** after writing, reading, comparing, and deleting a temporary C: file.
- [x] Add time-separated openMSX captures over 210 emulated seconds and a comparison script that rejects blank/stationary output.
- [x] CI builds and tests the proof disk and accepted title-wipe image without modifying release or main.
- [x] Support three private NMS8250 ROMs (32KiB BIOS+BASIC + 16KiB SUB + 16KiB disk); no ROMs committed or attached to artifacts.
- [x] Execute core ROM-backed NMS8250 emulator suite and inspect screenshot artifacts; **resolved 2026-11-11** using `curl -A "Mozilla/5.0"` on the four split ROM URLs; build, standalone, loop and C: proof all passed in run 43001359714. Prior HTTP 405 was source User-Agent filtering. ROM binaries provided by the user did not mount in the conversation/container.
- [ ] Verify editor/menu, clock rollover and longer cycle reliability after C: proof is successful.


## Latest CI inspection (2026-11-10)
- [x] Inspected [run 42889296897](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/42889296897): **build success**, **openMSX failed before launch** (HTTP 405). No new C:, loop, screenshot or editor runtime result.
- [x] Linked `HOWTO-TESTING.md` from `AGENTS.md` and `CONTEXT.md` for cross-session continuity.
- [x] Run NMS8250 integration smoke with ephemeral ROM URLs, C: proof marker and image-difference summaries (run 43001359714).

## ROM URL regression follow-up (2026-11-11)
- [x] [Run 42983952510](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/42983952510): all build steps passed. First of four new split Philips ROM URLs (`nms8250-bios.rom`) returned HTTP 405 from GitHub Actions; remaining three were not attempted because the step stopped at the first error. No emulator run or C: runtime test occurred.
- [ ] Resume automated NMS8250 C:/loop tests with verified ROM files in a private runner pool or private Actions secrets, not ROM bytes committed to Git. Do not retry these blocked public URLs without changed circumstances.

## Verified NMS8250 ROM-backed CI milestone (2026-11-11)

[GitHub Actions run 43001359714](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43001359714), commit `9f3618d`: **build and openMSX runtime job both passed**, using four supplied split ROM URLs fetched with `curl -A "Mozilla/5.0"` into an ephemeral runner ROM pool (no ROM data in repository or artifacts). The openMSX job reports success for standalone Z80 screenshot smoke, independent full Kabelkrant multi-page screenshot/difference regression at 120/165/210/255 emulated seconds on `KBLTITLECOPY.DSK`, and C: write/read/compare/delete proof with `A:KBLPASS.OK` checked via `mcopy` from a disposable copy of `KBLCTESTAUTO.DSK`. Screenshot artifacts are retained by Actions.

Earlier failed runs identified **test harness errors**, not established production regressions: pre-boot screenshot assertions at 25/30s, injected BASIC proof opening file handle #2 (error 52 without `MAXFILES` setting), and missing `mtools` in the separate runtime job. These are corrected; injected proof now reuses closed handle #1. **Still not established:** interactive editor/menu flows, pixel-exact comparison, clock rollover or truly long unattended operation. Keep experimental preview and released v6.2b distinct.

## Operator/editor integration smoke (2026-11-11)

- [x] Reviewed unchanged `MAIN.SYS`, `TEKST.SYS`, `LOOP.SYS`: the test must exercise memory coexistence and the real menu -> editor -> A:/C: save -> return-to-LOOP path, not unrelated menu functionality.
- [x] Added keyboard-driven disposable-disk openMSX test (`z80/tools/openmsx_editor_smoke.tcl`) plus independent A: `Z8REG26.TXT` content verification and screenshot comparison (`z80/tools/check_editor_smoke.py`). No production BASIC or released disk is changed.
- [x] First automated [run 43022043857](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43022043857) reached the main menu, TEKST menu and editor, but did **not** reach the save/return state: synthetic keystrokes overlapped screen transitions. The existing standalone, full newspaper loop and C: proof tests stayed green. This is a **test sequencing failure**, not demonstrated editor corruption.
- [ ] Confirm final spaced-input test on [run 43022652650](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43022652650): it was pending when last inspected, behind older in-progress run 43022629964. Only check off after the A: file proof and resumed live page captures pass. Inspect preserved `openmsx-NMS8250-editor-smoke` screenshots if it fails.
- [ ] Following a successful editor test, perform separate longer unattended NMS8250 page-cycle and clock stability checks with explicit artifacts.

## Reusable emulator test guide and extended regression (2026-11-11)

- [x] Added [docs/REUSABLE-MSX-EMULATOR-TESTING.md](docs/REUSABLE-MSX-EMULATOR-TESTING.md), cross-referenced from AGENTS.md, CONTEXT.md, HOWTO-TESTING.md and BUILD-AND-TEST.md. General-purpose openMSX/CI Tcl screenshots, keyboard injections, test images, ROM handling, WebMSX limitations and proof-file patterns are separated from Kabelkrant-specific instructions.
- [x] Run [43028765015](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43028765015) produced 23-minute emulated NMS8250 captures with different real pages, but the **long-run validator failed** because its >1 KiB PNG threshold rejects highly compressed blank wipe frames; at 660 and 662 seconds both frames are blank. Do **not** falsely report an application crash: later captures at 840 and 1200 seconds contain real pages. The short loop and C: runtime proofs passed in this run.
- [x] Extended long-run capture to 0/2/12-second triplets at eight intervals; validator now requires a populated frame in each triplet and substantial changes across intervals. Yet to verify with CI.
- [ ] The editor/menu test still reaches save-name prompt but does not produce the A: proof file. Next trial uses `type_via_keybuf` for the long BASIC input strings, keeping menu commands via simulated keyboard matrix; capture screenshots and inspect proof before declaring PASS.
- [ ] Inspect results of [run 43029861418](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43029861418) and mark independent PASS/FAIL for long-run and editor test.

## Verified extended runtime (2026-11-11)

- [GitHub Actions run 43030914435](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43030914435) on commit `693cb2f`: **build PASS**, standalone Z80 openMSX screenshot PASS, multi-page KabelKrant loop PASS, RAMdisk C: write/read/compare/delete **PASS**, and unattended NMS8250 test **PASS** with 0/2/12-second screenshots around 8 intervals covering 120–1392 emulated seconds. Tcl completion was at 1395 seconds. This is evidence of ~23 minutes emulated running on `KBLTITLECOPY.DSK`, not proof of indefinite stability or tests on all experimental disk variants.
- **Editor/menu integration remains FAIL/UNVERIFIED** in this run: the keyboard-driven test reaches menus/editor/save-name prompt but the expected `Z8REG26.TXT` proof file is not found on disposable A:. Do not attribute that to an application regression without further investigation; keyboard injection or a fixture issue remains possible.
- Harness lessons: uniform wipe PNG may be under 1024 bytes and still be valid; validate decoded image dimensions and distinguish content afterward. Schedule Tcl `exit` *after* the final delayed frame (original final +12s screenshot was scheduled after exit). See [docs/REUSABLE-MSX-EMULATOR-TESTING.md](docs/REUSABLE-MSX-EMULATOR-TESTING.md).

## Existing page editor fixture follow-up (2026-11-11)
- [x] Inspected the actual FAT12 root of the built `KBLTITLECOPY.DSK`; `RECEPT1.TXT` used by the previous keyboard test is absent. Confirmed present: `MENU01.TXT` through `MENU07.TXT`, `ZZBO1.TXT`, `ZZBO2.TXT`, etc. The editor's 'Bestaat niet' was expected, not a Z80 regression.
- [x] Changed disposable operator smoke to load `MENU01.TXT`, modify it and save to distinct `Z8REG26.TXT`. The original BASIC editor and disk images remain unchanged.
- [ ] Inspect [GitHub Actions run 43032437487](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43032437487) for test result; build passed, but ROM-backed runtime job was still in its 'Install headless emulator' step when last checked. Never mark this editor scenario passed until the new A: file proof and resumed-loop screenshots have been verified.
