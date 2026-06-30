# Limitations

This document describes the practical constraints of the Kabelkrant system — what it cannot easily do, where it is slow, and why. Understanding the limits helps understand why the design looks the way it does.

---

## Performance

### Text rendering

The biggest performance cost is the proportional text renderer. For each character in a string, `LOOP.SYS` executes:

1. A `MID$` string slice (BASIC string operation)
2. An `ASC()` conversion
3. An integer array lookup for glyph source coordinates
4. A `COPY` command that triggers a VDP hardware blit

Each `COPY` involves the BASIC interpreter calling the MSX BIOS, which programs the V9938 VDP registers and waits for the blit to complete. At 3.58 MHz Z80 speed with the VDP's internal copy rate, a single character takes several milliseconds. A full title line of 20 characters takes measurably longer than a simple screen wipe.

The consequence: **text rendering is the limiting factor on page display speed.** Pages with long bodies (8–10 lines) take noticeably longer to render than short ones. This was acceptable for a slowly-cycling information display but would be inadequate for anything requiring rapid screen updates.

### Wipe transitions

The 14 wipe transitions are implemented as `LINE` and `COPY` loops with step increments. Each frame of a wipe is one or more BASIC statements inside a `FOR` loop — slow by modern standards, but smooth enough at the 1-second-per-wipe pace used in the system.

### No hardware sprites

SCREEN 7 does not support VDP hardware sprites. All moving elements (clock hands, hourglass animation) are redrawn by software — each update erases the old position and redraws the new one using `COPY` from the asset page.

---

## Capacity limits

### Page schedule: 32 pages maximum

`KRANT.PAG` stores exactly 32 page name slots per record, and `N$(0)` to `N$(31)` is the schedule array. The system cannot display more than 32 pages in a single day's schedule without restructuring both the file format and the runtime array.

### Page names: 8 characters maximum

Page names in `KRANT.PAG` are stored as fixed-width 8-character fields. This matches MSX-DOS 8.3 filename limits, but it means page filenames must be 8 characters or fewer (e.g. `MENU0001`, `BEZOEK01`). Longer or more descriptive names are not possible.

### Body text: 10 lines maximum

The `.TXT` page format supports a title (line 2) and up to 10 body lines. Adding more lines would require changing the file format, the reader code, and the screen layout — and would likely cause text to overflow below the visible display area.

### File extension: .TXT only

The 1999 maintenance update changed the extension to `.txt`. The code uses the fixed extension string `EXT$=".txt"`. Mixing pages with different extensions is not supported without source changes.

---

## Memory constraints

`LOOP.SYS` is a large BASIC program (~4 000+ lines) that occupies most of the available BASIC heap. Adding significant new functionality — new page types, additional transitions, extended file formats — would require careful management of:

- Program text size (the interpreter stores every line)
- Array sizes (each `DIM` allocation reduces free heap)
- String space (`CLEAR 2000` sets a fixed pool)

The system has little headroom. The 1999 maintenance update (changing a drive letter on two lines) was exactly the kind of minimal targeted change the codebase can sustain. A major feature addition would risk running out of BASIC memory.

---

## Maintainability

### Line-numbered BASIC

The entire application is written in line-numbered MSX BASIC, which was standard for the platform in 1994. This means:

- There are no named functions or procedures — only numbered `GOSUB` targets
- Global variables serve as both parameters and return values for subroutines
- `GOTO` statements are used for error recovery and loop control
- The relationship between variables is implicit, not declared

Anyone not already familiar with the codebase must trace variable usage across hundreds of lines to understand what a routine expects and what it returns.

### No structured modules within a module

Each `.SYS` file is an independent BASIC program loaded with `RUN`. Within each file, functionality is divided by line-number ranges, not by named constructs. Navigating `LOOP.SYS` requires either a printed listing or careful use of the source line references in [MODULE-REFERENCE.md](MODULE-REFERENCE.md).

### Testing is manual

There is no automated test framework. Any change to the rendering logic, the file reading code, or the schedule management must be verified by running the system on real hardware or an emulator and visually inspecting the output.

### Hardware dependency

The system is tightly coupled to the MSX2 hardware: the V9938 VDP, the specific VRAM layout of SCREEN 7, the keyboard buffer addresses, the MSX-DOS slot structure. None of this is abstracted. Porting to a different platform would require rewriting nearly everything.

---

## What would be difficult to change

| Change | Why difficult |
|---|---|
| More than 32 pages per day | `KRANT.PAG` record format is fixed-width |
| More than 10 body lines | Screen layout and file reader are hardcoded |
| Different screen resolution | All coordinates are absolute SCREEN 7 values |
| New font or different glyph count | `X(190)` metric array is sized to exactly 191 glyphs |
| Adding network/modem capability | Removed in v6.x; no API layer to restore it to |
| Running on non-MSX hardware | Entire display engine is VDP-specific |

These are not defects — they are consequences of a focused, production-stable design that was never expected to grow beyond its original scope.

---

## See also

- [MEMORY-USAGE.md](MEMORY-USAGE.md) — memory layout and BASIC heap constraints
- [RENDERING.md](RENDERING.md) — performance analysis of the rendering pipeline
- [ARCHITECTURE.md](ARCHITECTURE.md) — design decisions and rationale
- [VERSION-HISTORY.md](VERSION-HISTORY.md) — how the system evolved and where it stopped
