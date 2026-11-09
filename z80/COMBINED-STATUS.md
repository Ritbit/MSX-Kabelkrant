# Combined RAMdisk + Z80 TEXT experimental integration

Status: **build works, runtime integration does not yet work** (2026-11-09).
Do **not** merge into main or distribute as a working image.

## Construction

`z80/tools/make_combined_rom.py` preserves the original `src/RAMDISK.BIN`
installer and disk-driver bytes except for (1) the existing LDIR copy size
and (2) the previously empty STATEMENT pointer in the copied ROM header.
The assembly text handler is appended at mapper-bank address `46F5h`.
The resulting `KBLALL.BIN` is approximately 4.2 KB and fits inside the
existing 16 KB mapper bank. The historical 6.2b assets are unchanged.

## Verified

- SjASMPlus assembly succeeds on GitHub Actions.
- Unit tests check the original RAMdisk image, the modifications to its
  relocation code and ROM header, and payload size/bounds.
- A combined `KBLCOMB.DSK` is built and boots in openMSX 19.1 with
  the Philips NMS 8250 ROMs, using the original warm-restart sequence.
- The combined Disk-ROM is present in the mapper's physical segment 2.
  At the point of failure, the original installer has reset mapper page 1
  to segment 4; the demo explicitly selects segment 2.
- The test registers BASIC's page-1 CALL slot attribute (RAMAD1=8Bh,
  SLTATR[57]) and calls `CALL KBLVER`.

## Unresolved

The emulator still reports `Syntax error in 80` at `CALL KBLVER`.
A conditional CPU breakpoint at `46F5h` with opcode `E5h` (the actual
compiled entry) **never fires**. The earlier unqualified breakpoints at
`46F5h` were false positives from other slots, not proof of extension
execution.

Next: investigate the firmware's CALL slot-scan / inter-slot dispatch
path and make the ROM's STATEMENT handler selectable without hardcoded
mapper writes in BASIC. The current `OUT &HFD,2` in the test script is a
diagnostic workaround, **not a production-safe solution**.

## Trimming the original RAMdisk

Not recommended yet. Driver routines at `4000h..46F4h` service MSX Disk
BASIC/DOS entrypoints; removing any without call-graph analysis may break
drive C:. The 4.2 KB combined image fits in the *same* 16 KB mapper
segment, so byte trimming alone does not save a segment of RAM. ROM error
messages can be considered only after the combined loader works and the
disk-driver code has been reverse engineered and regression tested.
