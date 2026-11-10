# Full Kabelkrant Z80 preview test disk

**Status: alpha / development-only. This is not a 6.2b replacement.**

The workflow `.github/workflows/z80-build.yml` publishes
`KBLZ80TEST-full-Kabelkrant-EXPERIMENTAL`, containing `KBLZ80TEST.DSK`,
and commits the raw test disk to `assets/KBLZ80TEST.DSK` on this
feature branch for direct WebMSX loading. The CI build tests the actual
FAT12 image against the current 6.2b baseline before publishing.

## Contents

Built from the **published 6.2b** image checked out separately from
`main`. The original RAMdisk, clock, page data, palette and graphics
remain unchanged. Only the generated `KBLINIT.SYS` and `LOOP.SYS`
are substituted; `KBLTXT.BIN` is added.

- `KBLINIT.SYS`: reserve high RAM at `C800h`, then BLOAD/R the Z80
  text engine after the historical RAMdisk warm-start.
- `LOOP.SYS`: replace seven `GOSUB 2500` calls with
  `CALL TEXT(A$,X,Y,LT,K)`; retain the original page/clock logic;
  reserve `C800h` across its second `CLEAR`.
- Remove the **unused** BASIC font drawing subroutine and `X(4,110)`
  double array from the generated test `LOOP.SYS`. Otherwise BASIC
  triggers `ERR=7` (out of memory) at line 1050.
- `LOOPBAS.SYS`: the untouched 6.2b `LOOP.SYS` on the same test disk
  as a source/diagnostic fallback. It is **not** automatically loaded.

No changes have been made to the released 6.2b files or `main`.

## Verified under openMSX (Philips NMS 8250)

Using the exact CI disk image, emulator breakpoints confirmed:

- RAMdisk installation at C000h.
- Text engine initialization at C806h.
- Repeated calls into Z80 text handler C82Ah.
- Real Cablekrant broadcast page with clock, right-aligned coloured
  title and multiple body lines displayed around 130 emulated seconds.

**Prior regression (now resolved in manual WebMSX testing):** The alpha
previously restarted after approximately three pages. Source review found
that `LDIR` was executed for empty strings (`BC=0` copies 64 KiB),
corrupting memory. The guard and the page-loop `GOTO` fix are now included.
On 2026-11-10 the user confirmed that the crash no longer occurs and
that the coloured heading outlines are correct. Longer unattended runs,
operator functions and drive C: regressions still need independent testing.

Do not promote the disk to GitHub Releases, change `main`, or claim
long-run stability until the unexpected reset is understood.

## Run it

Use the directly published raw `assets/KBLZ80TEST.DSK` from
`feature/z80-renderer`, or download and unpack the
`KBLZ80TEST-full-Kabelkrant-EXPERIMENTAL` Actions artifact.

Use openMSX:

```sh
openmsx -machine Philips_NMS_8250 -diska KBLZ80TEST.DSK
```

Or use the WebMSX URL below to load the public raw DSK automatically.
A GitHub Actions artifact ZIP URL itself is not a raw disk URL.

The standalone renderer demo `KBLASM.DSK` remains a separate test
and does not exercise the historical RAMdisk/page loop.

## 2026-11-10: potential page-three crash cause

Source review identified a deterministic memory-corruption bug in the Z80
`CALL TEXT` argument copy: `LDIR` was reached when the string length
was zero (`BC=0`). On the Z80, this copies 65,536 bytes, overwriting
RAM instead of doing no work. Valid empty lines in page files can reach
`CALL TEXT("")` (the original BASIC loop skips a single blank space,
but not an empty string). The assembly now skips `LDIR` for zero-length
strings and a regression test checks this guard. This is a **confirmed memory-corruption bug** fixed at the assembly level;
the user confirmed that WebMSX no longer crashes after page three, but
no independent memory trace has established it as the sole original cause.

Independently, generated test `LOOP.SYS` now enters the non-returning
page cycle with `GOTO 2200` rather than `GOSUB 2200`, preventing a
return-stack leak at each `GOTO 140` cycle restart.

Development-only WebMSX preview (built on CI and published as a raw DSK):

```text
https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLZ80TEST.DSK
```

## Experimental single-BLOAD alternative (2026-11-10)

A **separate** `KBLONEFILE.DSK` is generated on the feature branch
without replacing the known-working `KBLZ80TEST.DSK`. On 2026-11-10 the
user confirmed it **boots and displays the newspaper without any error
codes** after moving `CLEAR 2000,&HC7FF` ahead of the intro. This is a
successful WebMSX smoke test, NOT proof of long-run stability:

- `z80/tools/make_onefile_preview.py` copies the exact historical
  `RAMDISK.BIN` C000–C7EF payload unchanged, pads to C804 and appends
  the separately assembled TEXT payload, while keeping BLOAD's original
  C000 entry.
- The boot `AUTOEXEC.BAS` remains unchanged and runs the composite
  as `RAMDISK.BIN`. Generated `KBLINIT.SYS` substitutes
  `195 DEFUSR3=&HC806: A=USR3(0)` for the second BLOAD.
- Unit tests check binary layout/preservation. GitHub Actions builds
  and publishes the experimental disk separately.
- The staged C806 entry survives warmstart, early `CLEAR`, intro and
  the later `CLEAR` in the observed WebMSX run. The onefile BASIC code
  invokes `USR3` to install TEXT and the newspaper displays normally.
  Drive C: read/write integrity, repeated page cycles and operator/editor
  flows are not yet independently checked.

Manual WebMSX experiment (do not confuse with the working alpha):

```text
https://webmsx.org/?MACHINE=MSX2E&RAMMAPPER_SIZE=256&AUTO_START=true&FAST_BOOT=1&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/feature/z80-renderer/assets/KBLONEFILE.DSK
```

### Onefile symptom and diagnostic checkpoints

The first single-BLOAD build hung at the logo; the diagnostic build
reported `E2`, revealing loss of C806 during the intro. Reserving
`HIMEM=&HC7FF` with `CLEAR 2000,&HC7FF` **before** SCREEN 7 and the intro
removed this failure in the user's WebMSX test. The onefile experiment
still contains explicit C806 opcode probes:

- `E1`: the TEXT payload is absent by early KBLINIT, after RAMdisk warmstart.
- `E1B`: the payload is overwritten by the early HIMEM `CLEAR`.
- `E2`: the payload was present at E1 but disappeared during intro drawing.
- `E3`: the payload survived the intro but not the BASIC `CLEAR`.

The probes look for the assembly install entry's expected first opcode
`21h` (`LD HL,CallHandler`). A pass only rules out this simple overwrite;
it does **not** prove that the full module, mapper state, stack and
`USR3` ABI are correct. An apparent freeze without E1/E2/E3 needs
an openMSX CPU trace at C806 and the BASIC error/handler path.

Only the **experimental onefile** version gets these checks; the working
two-file preview remains untouched.

If later regressions occur, trace C806 and C004 under openMSX before
changing any historical RAMdisk bytes. The onefile user-visible boot
result is positive but a complete C: regression remains required.

## Next tests

Run a multi-cycle unattended openMSX trace and explicit drive C:
read/write and operator/editor tests; compare pixels and benchmark
identical page text against the refreshed 6.2b BASIC release.
