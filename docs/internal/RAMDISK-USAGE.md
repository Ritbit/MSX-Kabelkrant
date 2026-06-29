# RAM Disk Usage

This document describes how the BASIC code uses the RAM disk. It does not document the internal Z80 implementation of `RAMDISK.BIN`.

## Purpose

The RAM disk is used as drive `C:`.

The goal is to reduce disk I/O during the live display loop.

## Boot installation

`AUTOEXEC.BAS` loads:

```basic
BLOAD "RAMDISK.BIN",R
```

This installs the RAM disk before `KBLINIT.SYS` runs.

## Initial population

`KBLINIT.SYS` copies selected files from drive `A:` to drive `C:`. The visible filename patterns are:

```text
*.PAG
*.TXT
```

Missing files are tolerated.

## Runtime refresh

`LOOP.SYS` periodically copies the active page text files from `A:` to `C:`:

```text
A:<page>.txt  ->  C:<page>.txt
```

This happens when the detected week/day state changes.

## Runtime reads

During page display, `LOOP.SYS` reads from:

```text
C:KRANT.PAG
C:<page>.TXT
```

## Data flow

```mermaid
flowchart LR
    A[Floppy / drive A:] -->|startup copy| B[RAM disk / drive C:]
    A -->|page refresh| B
    B --> C[LOOP.SYS]
    C --> D[Screen output]
```

## Notes

The RAM disk is treated as a normal MSX-DOS-style drive from BASIC. This keeps the BASIC code simple: normal `COPY`, `OPEN`, `KILL` and file path syntax can be used.
