# BUILD-AND-TEST — Kabelkrant Z80 development

> **Development branch only:** `feature/z80-renderer`. Never merge this
> file, `CONTEXT.md`, `AGENTS.md`, `PLAN.md` or `TODO.md` into `main`.
> Use clean release branches created from `main` for production changes.
>
> Commands below describe the existing repository's build pipeline,
> not a claim that the **combined RAMdisk+TEXT** prototype works at runtime.

## 1. Prerequisites (Linux / Ubuntu 24.04 example)

- Python 3.10+, `git`, `cmake`, a C++ toolchain, `mtools`.
- [SjASMPlus 1.24.0](https://github.com/z00m128/sjasmplus) for assembly.
- [openMSX](https://openmsx.org/) for MSX2 emulator tests; `xvfb` for
  headless captures in environments without a display.
- A **locally installed** Philips NMS 8250 BIOS, BASIC, MSX2 sub-ROM and
  disk ROM. ROM files are not committed, uploaded, or bundled with artifacts.

```sh
sudo apt-get update
sudo apt-get install -y git cmake build-essential python3 mtools openmsx openmsx-data xvfb
git clone --recursive --depth 1 --branch v1.24.0 https://github.com/z00m128/sjasmplus.git /tmp/sjasmplus
cmake -S /tmp/sjasmplus -B /tmp/sjasmplus-build -DCMAKE_BUILD_TYPE=Release -DENABLE_LUA=OFF
cmake --build /tmp/sjasmplus-build --parallel 2
# Alternatively, use the packaged sjasmplus if it is compatible.
sudo cmake --install /tmp/sjasmplus-build
```

Check out the development branch and run commands from the repository
root, unless a subshell specifies otherwise:

```sh
git switch feature/z80-renderer
mkdir -p z80/build
```

## 2. Build the standalone Z80 BASIC CALL module

```sh
python3 z80/tools/convert_fonts.py --xdat src/X.DAT --output z80/build/FONTS.DAT
(cd z80/asm && sjasmplus --raw=../build/textdemo.raw \
  --lst=../build/textdemo.lst --sym=../build/textdemo.sym basic_text_demo.asm)
python3 z80/tools/make_bload.py z80/build/textdemo.raw z80/build/KBLTXT.BIN
python3 z80/tools/msx_basic_ascii.py z80/asm/ASMTEXT.BAS z80/build/ASMTEXT.BAS
python3 -m unittest discover -s z80/tests -p 'test_*.py' -v
```

`KBLTXT.BIN` is the **standalone**, independently tested BASIC
`CALL TEXT` module. Its BLOAD payload starts at E004h and requires
`CLEAR 300,&HDFFF`. The extension's dispatch pointer is installed at
C004h, so do not load the historical RAMdisk in this standalone test.
The ROM/image experiments below have different memory/slot requirements.

**Do not BLOAD `kernel.raw`:** it is not a BASIC-loadable binary.

## 3. Build a bootable standalone MSX2 disk image

```sh
cp assets/kabelkrant-6.2.dsk z80/build/KBLASM.DSK
printf '10 SCREEN 0:WIDTH 80:COLOR 15,4,4\r\n20 PRINT "KABELKRANT Z80 CALL TEXT TEST"\r\n30 RUN "ASMTEXT.BAS"\r\n' > z80/build/AUTOEXEC.BAS
mcopy -o -i z80/build/KBLASM.DSK z80/build/AUTOEXEC.BAS ::AUTOEXEC.BAS
mcopy -o -i z80/build/KBLASM.DSK z80/build/ASMTEXT.BAS ::ASMTEXT.BAS
mcopy -o -i z80/build/KBLASM.DSK z80/build/KBLTXT.BIN ::KBLTXT.BIN
mdir -i z80/build/KBLASM.DSK ::
test "$(stat -c %s z80/build/KBLASM.DSK)" -eq 737280
```

This copies the *original* 6.2 image and replaces files in the copy.
It does not modify assets in Git. The disk uses `KRANT3.SC7` for all
four fonts, and tests white/colour-13 text plus right alignment.

`ASMTEXT.BAS` must be encoded as MSX Disk BASIC ASCII
(CRLF line endings plus terminal Ctrl-Z), using the converter above.
Never feed the LF-only Git source straight to MSX BASIC; that caused an
actual `Direct statement in file` regression.

## 4. Build the combined RAMdisk + TEXT *experimental* image

The combined prototype retains the historical RAMdisk's Disk ROM code,
appends the BASIC CALL handler at 46F5h, and extends the ROM copy size:

```sh
python3 z80/tools/make_combined_rom.py --root . --output z80/build
(cd z80/asm && sjasmplus --raw=../build/combined_text.raw \
  --lst=../build/combined_text.lst --sym=../build/combined_text.sym .generated_combined.asm)
python3 z80/tools/make_combined_rom.py --root . --output z80/build \
  --extension z80/build/combined_text.raw
cp assets/kabelkrant-6.2.dsk z80/build/KBLCOMB.DSK
mcopy -o -i z80/build/KBLCOMB.DSK z80/build/COMBAUTO.BAS ::AUTOEXEC.BAS
mcopy -o -i z80/build/KBLCOMB.DSK z80/build/COMBTEXT.BAS ::COMBTEXT.BAS
mcopy -o -i z80/build/KBLCOMB.DSK z80/build/KBLALL.BIN ::KBLALL.BIN
```

**Known failure:** This image builds and boots but `CALL KBLVER` still
produces `Syntax error in 80`; ROM/slot dispatch does not reach 46F5h.
Do **not** use it as a working Kabelkrant disk. Details and evidence:
[`z80/COMBINED-STATUS.md`](z80/COMBINED-STATUS.md).
A successful compile or artifact upload is **not** an emulator-pass.

## 5. openMSX — NMS 8250 setup and interactive test

Put legally obtained system ROMs in the user system-ROM file pool:

```sh
mkdir -p ~/.openMSX/share/systemroms
# If supplied as two 16 KiB files, the NMS 8250 requires BIOS+BASIC
# concatenated in that order into a 32 KiB image:
cat /path/to/nms8250-bios.rom /path/to/nms8250-basic.rom \
  > ~/.openMSX/share/systemroms/nms8250_basic-bios2.rom
# Also place the nms8250_msx2sub.rom and nms8250_disk.rom there.
```

Check the machine in openMSX: **Machine → Test MSX hardware**,
or open the F10 console and issue `test_machine Philips_NMS_8250`.
ROM file checksums and configuration matter; use the openMSX error
message if a ROM is missing. C-BIOS alone cannot stand in for the
required Disk BASIC environment.

Start the standalone test image:

```sh
openmsx -machine Philips_NMS_8250 -diska z80/build/KBLASM.DSK
```

Observe that `CALL KBLVER` and the four-font text display execute,
not merely that the machine boots. Check text, transparency, palette,
colour 13, negative X alignment, and BASIC errors. The current source
safely skips font 3 / ASCII 127 due to an invalid last coordinate.

To test the **known-broken combined prototype**, use
`-diska z80/build/KBLCOMB.DSK` *and expect the documented failure*.

### Headless screenshot / smoke capture

An included Tcl script captures a PNG after 25 **emulated** seconds:

```sh
mkdir -p z80/build
timeout 90s xvfb-run -a openmsx \
  -machine Philips_NMS_8250 \
  -diska z80/build/KBLASM.DSK \
  -script z80/tools/openmsx_smoke.tcl
test -s z80/build/openmsx-smoke.png
```

The screenshot is a **smoke artifact**, not proof of correct graphics.
Inspect it or compare against known-good output; check emulator errors.
Use openMSX's F10 console for `screenshot -raw`, `test_machine`
and debugging/breakpoints. For deterministic regression tests,
validate expected CPU/memory/VRAM conditions in addition to a PNG.

Official references:
[openMSX setup](https://openmsx.org/manual/setup.html),
[console commands](https://openmsx.org/manual/commands.html).

## 6. WebMSX — manual browser tests

The published stable 6.2b (no experimental Z80 code):

```text
https://webmsx.org/?MACHINE=MSX2E&DISK=https://raw.githubusercontent.com/Ritbit/MSX-Kabelkrant/main/assets/kabelkrant-6.2b.dsk
```

WebMSX recognizes `MACHINE=MSX2E` and `DISK=` (also `DISKA_URL=`).
For a Z80 development image, either **upload the local DSK through
WebMSX's disk UI**, or first put it at an accessible **public raw HTTPS
URL** and substitute that URL into `DISK=`. GitHub Actions artifact
download pages are **not** equivalent to directly accessible raw
`.dsk` URLs, and `z80/build/` is intentionally ignored by Git.

See the [WebMSX URL parameters](https://github.com/ppeccin/WebMSX/blob/master/doc/README.md).
WebMSX is a separate manual validation route, not the evidence source
for an openMSX/Tcl test.

## 7. CI and acceptance criteria

Workflow:
[`.github/workflows/z80-build.yml`](.github/workflows/z80-build.yml)
runs automatically on changes in `z80/**` and related build files.
It compiles SjASMPlus, runs Python tests, and uploads named artifacts:

| Artifact | Meaning |
| --- | --- |
| `KBLASM-experimental-MSX2-testdisk` | Standalone candidate; run in emulator |
| `KBLCOMB-RAMdisk-TEXT-EXPERIMENTAL` | Builds, **runtime CALL remains broken** |
| `KBLBASE-original-BASIC-four-font-testdisk` | BASIC reference |
| `KBLBENCH-original-vs-optimized-BASIC` | BASIC A/B timing baseline |
| `z80-prototype-NOT-BOOTABLE` | Raw build/listing and font data; not a disk |

Before calling a stage **working**, verify: assembly completes, BASIC
files are valid, disk image boots under NMS 8250, the expected `CALL`
actually executes, rendered pixels/palette are acceptable, and
regressions are absent. Benchmark on equal work with MSX-jiffy times.
Never publish an untested combined image as a release.

When updating test procedures, update this file and the relevant
workflow together. All this documentation remains on the development
branch only.
