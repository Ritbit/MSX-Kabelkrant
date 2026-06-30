# Memory Usage

The Kabelkrant system operates within the tight memory constraints of the MSX2 architecture. Every major resource — the BASIC interpreter, the program, string data, arrays, the RAM disk, and the graphics assets — competes for a limited address space.

---

## Z80 address space

The Z80 CPU addresses 64 KB of memory. On the MSX2, this space is mapped via a slot system:

```text
0000–3FFF   Slot 0: BIOS ROM (MSX system)
4000–7FFF   Slot 1: MSX-BASIC ROM (interpreter)
8000–BFFF   Slot 3-2: Main RAM (BASIC program + data)
C000–FFFF   Slot 3-2: Main RAM (stack, system vars, USR routines)
```

The exact mapping depends on the machine configuration; on the NMS-8250 the 64 KB RAM is in slot 3-2 and is paged in behind the ROMs for the upper sections.

---

## BASIC memory layout

Within the RAM pages, MSX BASIC organises memory as follows at runtime:

```text
Low RAM
  ├── System variables and work area    (~&H8000–&HF3xx)
  ├── BASIC program text                (grows upward from ~&H8001)
  ├── Variables and arrays              (follows program end)
  ├── String space (heap)               (grows downward from CLEAR limit)
  └── Stack                             (~&HF380 downward)

High RAM
  ├── &HF975–&HFxx  USR machine-code routines (installed by KBLINIT.SYS)
  └── &HFBF0–...    Keyboard buffer injection area (used by AUTOEXEC.BAS)
```

### The CLEAR statement

`KBLINIT.SYS` line 190 contains:

```basic
CLEAR 2000
```

`CLEAR n` sets the string heap size to `n` bytes and resets all variables. 2 000 bytes is a moderate allocation: enough for the page titles, body lines, and filename strings that `LOOP.SYS` manipulates at runtime, but deliberately conservative to leave room for the program text and arrays.

Increasing this number would give more string space but push the string heap lower in memory, potentially conflicting with large arrays or the embedded USR routines at `&HF975`.

### Arrays

`LOOP.SYS` allocates several numeric arrays for the font metric system:

```basic
DIM X(190), XK(190), YK(190)   ' glyph metric arrays
DIM N$(31)                       ' page schedule (32 entries)
```

The metric arrays hold one entry per possible glyph index. At 2 bytes each (integer arrays via `DEFINT A-Z`), that is approximately 1 140 bytes for the three arrays together. The page name array adds another 32 × (string overhead + ~8 chars) = roughly 400–500 bytes.

---

## The RAM disk trade-off

The RAM disk driver (`RAMDISK.BIN`) is installed into the MSX memory mapper as an additional RAM segment — effectively it borrows one or more 16 KB mapper pages from the available RAM pool.

The trade-off is deliberate:

| Without RAM disk | With RAM disk |
|---|---|
| More BASIC heap space | Less BASIC heap space |
| Every page read hits the floppy | All reads serve from RAM |
| ~1–3 s floppy seek per page | ~0 ms RAM read per page |
| Reliable only if floppy is fast | Completely predictable timing |

For a continuously cycling display system, predictable timing matters more than maximum heap size. A slow or noisy floppy seek would cause a visible hesitation between pages — unacceptable in a broadcast context.

---

## VRAM

The V9938 VDP has **128 KB of dedicated VRAM**, entirely separate from the Z80 address space. The MSX2 SCREEN 7 mode uses this as follows:

```text
VRAM page 0 (display page)   0x00000–0x1FFFF   (128 KB total)
  ├── Page 0: active display output
  │     0x00000  Pixel data: 512×212 pixels × 4 bits = ~54 KB
  │     0x00000–0x0D5FF  Visible display area
  ├── Page 1: hidden working page
  │     0x10000  Loaded graphics: KRANT4.SC7 (font glyphs, icons, hourglass frames)
  │     Also used for the Y=190 scratch rendering area
  └── Palette registers (not in pixel memory)
```

`KBLINIT.SYS` loads `KRANT4.SC7` onto page 1 (`SETPAGE 0,1: BLOAD "KRANT4.SC7",S`) and the intro splash onto page 0 from `intro.SC7`. During the display loop, `SETPAGE 0,0` makes page 0 the active display while page 1 remains loaded with the font and icon assets, always ready for `COPY` operations.

The consequence: **VRAM is not a constraint**. All graphical assets fit comfortably in 128 KB. The constraint is purely in the Z80 address space — the BASIC program and its data.

---

## Summary

| Resource | Location | Approximate size |
|---|---|---|
| BASIC program text (LOOP.SYS) | RAM ~&H8001 upward | ~25–30 KB |
| Integer variables + arrays | RAM, above program | ~2–3 KB |
| String heap (CLEAR 2000) | RAM, grows downward | 2 KB |
| USR machine-code routines | RAM &HF975–&HFFFF | ~167 bytes |
| Font + icon assets (KRANT4.SC7) | VRAM page 1 | ~54 KB |
| Intro splash (intro.SC7) | VRAM page 0 (startup) | ~54 KB |
| RAM disk (C: drive) | Mapped RAM page | ~16–32 KB |

---

## See also

- [RAMDISK.md](RAMDISK.md) — RAM disk usage from BASIC
- [TECHNICAL-DETAILS.md](TECHNICAL-DETAILS.md) — USR machine-code routines
- [ARCHITECTURE.md](ARCHITECTURE.md) — overall system design
- [HARDWARE.md](HARDWARE.md) — V9938 VDP and hardware specs
