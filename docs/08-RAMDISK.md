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

## Refresh strategy

When the relevant date/week state changes, `LOOP.SYS` refreshes the active text files from drive `A:` into drive `C:`.

```mermaid
flowchart LR
    A[Drive A:] -->|copy *.PAG / *.TXT| C[Drive C: RAM disk]
    C --> L[LOOP.SYS]
    L --> S[Screen]
```

## Scope

This document describes RAM disk usage from BASIC. It does not document the internal Z80 implementation.
