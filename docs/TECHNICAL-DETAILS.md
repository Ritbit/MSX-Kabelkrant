# Technical Details

This document describes four implementation techniques in Kabelkrant-MSX2 that go beyond ordinary MSX BASIC programming: the keyboard-buffer boot bootstrap, the embedded Z80 machine-code routines, the scratch-area rendering trick, and interval-timer management.

---

## Keyboard/input-buffer bootstrap

`AUTOEXEC.BAS` faces a problem: it needs to load `RAMDISK.BIN` using `BLOAD ... ,R` (which transfers control to the Z80 binary and does not return to BASIC normally), and then continue into `KBLINIT.SYS`. A simple `RUN "KBLINIT.SYS"` after the `BLOAD` would never execute.

The solution is to pre-load the next command into the **MSX keyboard input buffer** before triggering the binary:

```basic
110 COLOR 0,0,0: A$=CHR$(13)+"COLOR 0,0,0:Run"+CHR$(34)+"KBLINIT.SYS"+CHR$(34)+CHR$(13)
120 POKE &HF3FA,&H00F0: POKE &HF3FB,&H00FB  ' set buffer start/end pointers
130 FOR I=1 TO LEN(A$): POKE &HFBF0+I-1,ASC(MID$(A$,I,1)): NEXT
140 WR%=&HFBF0+LEN(A$): POKE &HF3F8,WR% AND 255: POKE &HF3F9,((WR% AND &HFF00)/256) AND 255
150 BLOAD "RAMDISK.BIN",R
```

The string `A$` contains a `RETURN`, followed by `COLOR 0,0,0:RUN"KBLINIT.SYS"`, followed by another `RETURN`. This is written character by character into the keyboard buffer at `&HFBF0`, and the buffer write pointer is updated at `&HF3F8/F3F9`.

When `RAMDISK.BIN` finishes installing the RAM disk and returns to BASIC (at the BASIC warm-start vector), BASIC finds characters waiting in the keyboard buffer and executes them as if the operator had typed the command. The system boots into `KBLINIT.SYS` with the RAM disk already in place.

This technique is standard practice in MSX BASIC for chaining through machine-code loaders. It requires no operating system support — just knowledge of three memory-mapped I/O addresses.

---

## Embedded Z80 machine-code routines (USR0, USR1, USR2)

`KBLINIT.SYS` embeds 167 bytes of Z80 machine code in two `DATA` lines and installs them as three MSX BASIC `USR` functions:

```basic
210 RESTORE 270: AD=&HF975
    FOR I=0 TO 166: READ A$: POKE AD+I,VAL("&H"+A$): NEXT
    DEFUSR=AD: DEFUSR2=AD+11: DEFUSR1=AD+25
```

### What the routines do

The comment at line 270 states:

```text
Code for 3 USR functions, 0 = Upcase, 1 = strip spaces, 2 = 0 + 1
```

| USR | Address | Offset | Function |
|---|---|---|---|
| `USR0` | `&HF975` | 0 | Convert string to uppercase |
| `USR2` | `&HF980` | +11 | Apply USR0 then USR1 (uppercase + strip spaces) |
| `USR1` | `&HF98E` | +25 | Strip leading/trailing spaces from string |

### How they are called

MSX BASIC `USR` functions accept a single string argument and return a string:

```basic
A$ = USR1(R$)    ' strip spaces from text read from page file
A$ = USR0(A$)    ' convert to uppercase
```

In `LOOP.SYS`, `USR1` is applied to each line read from a `.TXT` page file before rendering, ensuring that accidental leading or trailing spaces in the page content files do not affect the displayed position or width of the text.

### Why Z80 rather than BASIC

MSX BASIC has no built-in `TRIM$` or `UCASE$` function. Implementing these in BASIC requires a character-by-character loop with `MID$`, `ASC`, and `CHR$` — expensive in both code size and execution time when called for every line of every page. A 167-byte machine-code block covers all three combinations with negligible overhead.

### Installation mechanism

The DATA-to-POKE installation pattern is a well-established MSX BASIC technique. The bytes are stored as two-character hex strings in `DATA` statements, read one at a time with `READ`, converted to numeric values with `VAL("&H"+A$)`, and written into high RAM with `POKE`. This embeds the Z80 binary directly in the BASIC source without requiring a separate binary file.

The installation target address `&HF975` is in the high-RAM area between the top of the BASIC stack and the keyboard buffer area. This region is stable across the runtime of the display loop because no other BASIC operation writes there.

### The raw bytes

```text
Offset 0x00 (USR0 — uppercase):
FE 03 C0 CD B3 F9 C8 CD BE F9 C9

Offset 0x0B (USR2 — uppercase + strip):
FE 03 C0 D5 CD B3 F9 D1 C8 CD BE F9 18 09

Offset 0x19 (USR1 — strip spaces):
FE 03 C0 D5 CD B3 F9 D1 C8 D5 E5 CD E2 F9 E1 D1
12 B7 C8 47 E5 CD D2 F9 E1 12 B7 C8 47 D5 CD F7
F9 D1 12 B7 C9 ...  (continues to offset 0xA6)
```

The entry point pattern `FE 03 C0` is shared by all three routines: `CP 3` checks that the argument is a BASIC string type (type code 3). `RET NZ` returns immediately if the argument is not a string — standard MSX BASIC USR calling convention defensive check.

---

## Hidden-page scratch rendering

The proportional text renderer in `LOOP.SYS` needs to support right-aligned and centred text, but the total pixel width of a proportional string is not known until after all glyphs have been drawn. There is no way to pre-calculate width without first rendering.

The solution is a **scratch area at Y=190 on VRAM page 1** (the hidden page that also holds the font assets). When the destination X coordinate is negative (a sentinel value), the renderer writes glyphs into this scratch strip instead of the visible page. Once the full string is rendered and its width `XX` is known, the scratch strip is copied to the correct position on the visible page:

```basic
2680 IF X<0 THEN X=ABS(X)-XX: COPY (0,190)-(XX-1,209),1 TO (X,Y),0,TPSET
```

The scratch strip occupies rows 190–209 (20 rows × 512 pixels), safely below the visible display area (rows 0–211) on the hidden page. The visible page (page 0) is never written to until the final positioned copy.

This technique makes proportional right-alignment possible in BASIC without any lookahead or two-pass algorithm.

See [RENDERING.md](RENDERING.md) for the full renderer analysis.

---

## Interval timer and interrupt management

`LOOP.SYS` uses MSX BASIC's `INTERVAL` statement to drive the analog clock update without blocking the main display loop:

```basic
INTERVAL ON,36      ' fire every ~0.5 s (36 × 1/60 s timer ticks)
ON INTERVAL GOSUB clock_routine
```

The clock routine redraws the clock hands at the current time. Because this fires asynchronously — interrupting whatever the main loop is currently executing — it can corrupt VRAM operations that span multiple BASIC statements.

The solution is to bracket sensitive operations with `INTERVAL OFF` / `INTERVAL ON`:

```basic
INTERVAL OFF
' ... multi-statement VDP COPY sequence ...
INTERVAL ON
```

This appears around the text renderer and wipe transitions — operations that depend on page 1 remaining stable while a sequence of `COPY` commands runs. The clock interrupt is brief, but if it fired between two `COPY` calls in a wipe sequence, it could draw clock hands over partially-wiped page content.

Disabling the interval only for critical sections (not for the entire display loop) keeps the clock as responsive as possible while protecting the renderer.

---

## See also

- [BOOT-PROCESS.md](BOOT-PROCESS.md) — boot sequence with keyboard-buffer bootstrap
- [internal/BOOT.md](internal/BOOT.md) — annotated AUTOEXEC.BAS source
- [MEMORY-USAGE.md](MEMORY-USAGE.md) — USR routine memory location
- [RENDERING.md](RENDERING.md) — full rendering pipeline with scratch area detail
- [internal/TEXT-ENGINE.md](internal/TEXT-ENGINE.md) — text renderer source analysis
