# Reusable MSX emulator testing — openMSX, WebMSX and GitHub Actions

> **Portable how-to**. This file deliberately uses generic names and examples so it can be copied into other MSX projects. It is development documentation, not part of the KabelKrant release. The project-specific configuration and proven results live in [HOWTO-TESTING.md](../HOWTO-TESTING.md). Last updated: 2026-11-11.

## 1. Test levels and evidence

Do not conflate **build**, **image validated**, **ROMs loaded**, **MSX booted**, **target program executed**, **functional evidence**, **human visual approval**, **long-running regression**, and **release quality**. Keep the exact emulator/machine, ROM hashes (never ROM bytes), Git SHA, disk checksum, elapsed *emulated* time, scripts, artifacts and CI run URL.

A screenshot is evidence of a moment in time, **not** proof that a particular machine-code handler ran. For disk operations, check output files/markers written by the emulated machine, not only on-screen 'PASS' text. For pixel-exact tests, compare measured display pixels or VRAM against a known-good reference and control palette/render settings.

## 2. ROM provisioning in CI (never commit ROM binaries)

- Use ROM files you are allowed to use. Keep them outside Git commits, CI logs, screenshots, release images and public artifacts.
- Identify required ROMs by machine configuration, size and checksum. Upstream filenames are not fixed requirements; local names may need to match the emulator's machine definition.
- A configured GitHub secret can provide a private ROM; another option is an explicitly approved download endpoint at runtime. Avoid uploading ROMs as ordinary artifacts.
- The KabelKrant Philips NMS8250 ROM host responded HTTP **405** to default `curl`, but worked with **`-A "Mozilla/5.0"`** (verified Actions run [43001359714](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43001359714)). This is **host-specific**, not a universal requirement or permission to bypass a site's restrictions.
- Verify exact lengths and where possible expected SHA256 before launching openMSX, and remove temporary ROM files in an `if: always()` cleanup step.

Example of an approved download, **substitute your own authorized URL**:

```bash
set -euo pipefail
umask 077
mkdir -p "$RUNNER_TEMP/msx-roms"
curl --fail --location --silent --show-error --retry 0 \
  --connect-timeout 10 --max-time 60 -A 'Mozilla/5.0' \
  "$APPROVED_ROM_URL" -o "$RUNNER_TEMP/msx-roms/rom.bin"
test "$(stat -c %s "$RUNNER_TEMP/msx-roms/rom.bin")" -eq "$EXPECTED_BYTES"
sha256sum "$RUNNER_TEMP/msx-roms/rom.bin" # record hash only
```

If a machine uses a 32 KiB concatenated BIOS+BASIC image, combine only individually **verified** 16 KiB halves in the correct order; do not duplicate/concatenate an existing 32 KiB image. Adapt local openMSX ROM paths/names to the installed machine XML.

## 3. Headless openMSX in GitHub Actions

Ubuntu 24.04 example:

```bash
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
  openmsx openmsx-data xvfb python3-pil mtools
mkdir -p test-output
timeout 240s xvfb-run -a openmsx \
  -machine Philips_NMS_8250 \
  -diska "$RUNNER_TEMP/test-runtime.dsk" \
  -script tests/openmsx_smoke.tcl \
  > test-output/openmsx.log 2>&1
```

`timeout` limits **wall clock**, while `after time 120` inside openMSX Tcl schedules based on **emulated time**. The KabelKrant runner uses `set throttle off` for accelerated tests; nevertheless, preserve a sufficient wall-clock timeout. A missing ALSA sequencer is often harmless in a headless runner; check that the emulator actually reaches checkpoints rather than treating every audio warning as fatal.

**Always copy** the input `.dsk` to a disposable runtime image before tests that write to A:. The original test disk stays unchanged. Install `mtools` in the **runtime job**, even if the separate build job already has it.

## 4. Reusable Tcl screenshot and completion checkpoints

Example `tests/openmsx_smoke.tcl`:

```tcl
set throttle off
set out [file normalize "test-output"]
file mkdir $out

proc capture {stamp} {
    global out
    screenshot -raw [file join $out "frame-$stamp.png"]
    set f [open [file join $out "frame-$stamp.done"] w]
    puts $f "CAPTURE:$stamp"
    close $f
}

after time 120 {capture 120}
after time 122 {capture 122}
after time 132 {capture 132}
after time 300 {
    capture 300
    set f [open [file join $out "test.done"] w]
    puts $f "EMULATOR_COMPLETED"
    close $f
    exit
}
```

On headless runners, an openMSX `puts` may not appear in the shell log as expected. **Write a checkpoint file from Tcl** and assert its contents in CI; rely on actual screenshot files and functional proofs, not stdout alone.

```bash
grep -q '^EMULATOR_COMPLETED$' test-output/test.done
test -s test-output/frame-120.png
test -s test-output/frame-122.png
```

Determine the real cold-boot time empirically. A first screenshot at 25 or 30 emulated seconds was an empty boot screen in this project. Do not alter the application to make a premature test capture pass.

## 5. Capture screenshot **pairs** around transitions

A wipe/clear animation can produce a temporarily all-black or uniform frame. **Take two screenshots 1–2 emulated seconds apart** at each observation point and treat the pair together. **A two-second pair is not a definitive freeze detector**: on the KabelKrant NMS8250 23-minute capture, both images at 660/662 seconds were uniform during an apparent display transition, while later captures again showed newspaper pages. Preserve these as diagnostic evidence rather than automatically classifying the program as frozen. For a suspicious pair, add a third capture 10–15 emulated seconds after the first (or a suitable delay for that application's longest expected transition). Compare pages **across** distant intervals to establish ongoing progression. The evidence across the full run is more important than declaring every individual low-colour frame a failure. A static image pair may also mean the page is intentionally displayed for several seconds.

```tcl
foreach t {120 300 480 660 840 1020 1200 1380} {
    after time $t [list capture [format "%04d" $t]]
    after time [expr {$t+2}] [list capture [format "%04d" [expr {$t+2}]]]
    # Optional follow-up to distinguish a slower wipe from a hang:
    after time [expr {$t+12}] [list capture [format "%04d" [expr {$t+12}]]]
}
```

Beware false positives: a moving clock, cursor, screen border or incidental animation alone does not prove the news pages change. Use a body-region crop, difference statistics, and where feasible page IDs or actual VRAM/state checks. A long test is not stable merely because the scheduled checkpoint exists.

Project reference: `z80/tools/openmsx_regression.tcl` and `z80/tools/check_openmsx_regression.py`.

## 6. Keyboard-driven integration testing

Drive actual MSX keyboard input rather than changing BASIC variables or faking data files:

```tcl
proc send {s} { type -release -freq 3 $s }
after time 140 {send " "}
after time 200 {capture menu}
after time 205 {send "2"}
```

This `type` technique and `keymatrixdown`/`keymatrixup` are available in openMSX scripting. For software that uses the **standard BIOS keyboard buffer**, `type_via_keybuf "text"` is an alternative for longer strings: it injects input via that buffer and **does not** test physical keyboard-matrix scanning. Confirm that the application uses compatible BIOS input. To test the hardware keyboard path, retain `type -release -freq N` or matrix calls. See the [openMSX command reference](https://openmsx.org/manual/commands.html). **The example is not a complete editor test**: menu/input readiness must be verified. Short inter-event delays can drop or misroute keypresses; `INPUT$(1)` in MSX BASIC is not a host-side event queue. Prefer state/screen checkpoints or deterministic waits and send text and ENTER as separate actions. **Known open issue (2026-11-11):** the keyboard-driven KabelKrant editor scenario reaches menu, editor and save-name prompt, but does not yet produce the expected disk proof. The screenshots show the prompt stuck; the script must not be advertised as an accepted end-to-end test until the actual file has been verified. Confirm the expected menu before entering the next key, and fail with diagnostics rather than claiming success.

For a save/read/delete test, use a unique disposable filename (8.3), verify it with `mcopy` *from the emulator-mutated disk*, and check contents. A proof file created after successful operations is stronger than a text screenshot:

```bash
mcopy -i "$RUNNER_TEMP/test-runtime.dsk" ::PROOF.OK - |
  grep -q '^PASS TEST'
```

Do not accidentally open BASIC file handle `#2` when `MAXFILES` only supports `#1`. In this project a `Bad file number` (error 52) occurred in the *test fixture*, not in the core RAMdisk; the fixture was corrected by reusing already-closed `#1`.

## 7. CI structuring and failure evidence

- Split build/static tests from real ROM-backed emulator jobs. **Skipped** emulator tests must be reported as skipped, not silently folded into a green build.
- Keep independent smoke, page-loop, C: proof and UI tests separate; use `if: always()` when tests should continue after earlier independent failures.
- Upload PNGs, JSON results, Tcl checkpoint files and sanitized logs **even on failure**. Use `if: always()` and `if-no-files-found: warn` for diagnostic artifact steps.
- Avoid auto-publishing disk images on every debugging commit unless intentional; record the precise artifact and checksum tested.
- Avoid using a commit-message substring as the only ROM-test activation mechanism for a reusable pipeline. Prefer an explicit `workflow_dispatch` input or a clearly defined job configuration; this project's existing workflow still has a historical `[nms8250-rom-test]` opt-in path.
- Don't loosen a validator only to make CI green. Inspect screenshot artifacts first; fix unsound timing/assumptions while preserving meaningful functional assertions.
- Distinguish infrastructure error, harness error, application regression and incomplete evidence in the job summary.

## 8. WebMSX — what is and isn't automated

WebMSX is useful for independent **manual visual validation** in a browser. For example:

```text
https://webmsx.org/?MACHINE=MSX2E&DISK=https://example.org/path/test.dsk
```

Use a **direct publicly fetchable raw HTTPS disk URL**, or load a local `.dsk` through WebMSX's UI. A GitHub Actions artifact *web page* is not a raw `.dsk` endpoint. An openMSX Tcl `-script` test **does not execute inside WebMSX**. Don't assert browser automation if only openMSX ran.

To automate WebMSX in the future, use a real browser-testing setup (e.g. Playwright) to load the page, deliver keyboard input and capture browser screenshots. That pipeline must manage cross-origin disk loading, the browser's audio/user-gesture policies, input focus and state synchronization, and compare outputs to accepted references. This project has **not yet established** an automated WebMSX browser regression run; existing WebMSX evidence is user-confirmed manual testing.

References: [openMSX manual](https://openmsx.org/manual/), [WebMSX source/docs](https://github.com/ppeccin/WebMSX), and the development branch's workflow and scripts.

## 9. Minimal reusable checklist

1. Select an exact build/disk SHA, tested machine/ROM hashes, and disposable write targets.
2. Boot the emulator and verify execution with state checkpoints, file proofs or validated graphics.
3. Capture **paired** screenshots at transitions plus separated later samples, retain logs on failures.
4. Record PASS/FAIL/SKIPPED with *what was actually measured*. Store outputs, never system ROM bytes.
