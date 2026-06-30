# RAM Disk

The RAM disk is installed by `RAMDISK.BIN` and used as drive `C:`.

## Purpose

The RAM disk reduces floppy I/O during continuous display.

## Startup

`AUTOEXEC.BAS` loads the binary:

```basic
BLOAD "RAMDISK.BIN",R
```

`KBLINIT.SYS` then copies page schedule and text files into drive `C:`.

## Runtime reads

The display loop reads from `C:`:

```text
C:KRANT.PAG
C:<page>.TXT
```

## Initial population

`KBLINIT.SYS` copies selected files from drive `A:` to drive `C:` before the display loop starts:

```text
*.PAG   (page schedule files)
*.TXT   (page content files)
```

Missing files are tolerated — the copy is wrapped in an error handler so a missing file does not abort startup.

## Refresh strategy

When the relevant date/week state changes, `LOOP.SYS` refreshes the active text files from drive `A:` to drive `C:`:

```text
A:<page>.txt  →  C:<page>.txt
```

This refresh happens automatically when the system detects a day or week change. The schedule file `KRANT.PAG` itself is not refreshed at runtime — it was loaded at startup and remains in RAM.

```mermaid
flowchart LR
    A[Floppy / drive A:] -->|startup copy| C[RAM disk / drive C:]
    A -->|day-change refresh| C
    C --> L[LOOP.SYS]
    L --> S[Screen output]
```

## BASIC interface

The RAM disk appears to BASIC as a normal MSX-DOS drive. All standard BASIC file operations work:

```basic
OPEN "C:KRANT.PAG" AS #1 LEN=256   ' random file access
OPEN "C:"+N$(PG)+".TXT" FOR INPUT AS #1  ' sequential read
COPY "A:"+N$(A)+EXT$ TO "C:"+N$(A)+".txt"  ' file copy
KILL "C:*.txt"                       ' delete files
```

This keeps the BASIC code simple — no special RAM disk API, just normal MSX-DOS path syntax with `C:` as the drive letter.

## Scope

This document describes RAM disk usage from BASIC. The internal Z80 implementation of `RAMDISK.BIN` is not documented here.

---

## See also

- [internal/RAMDISK-USAGE.md](internal/RAMDISK-USAGE.md) — detailed source analysis with BASIC code references
- [04-BOOT-PROCESS.md](04-BOOT-PROCESS.md) — how RAMDISK.BIN is installed at boot
- [09-MEMORY-USAGE.md](09-MEMORY-USAGE.md) — RAM trade-off between BASIC and the RAM disk
- [ARCHITECTURE.md](ARCHITECTURE.md) — data flow diagram showing the A: → C: → display pipeline
