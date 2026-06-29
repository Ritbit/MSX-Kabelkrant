# Memory Usage

The system is constrained by MSX2 memory layout and MSX BASIC limitations.

## Conceptual memory map

```text
0000-3FFF  BIOS / BASIC ROM
4000-7FFF  ROM / mapped area
8000-BFFF  BASIC program/data area
C000-FFFF  RAM/system/resident support area
```

## BASIC memory pressure

The BASIC program uses memory for:

- program text
- variables
- string storage
- arrays
- file buffers
- embedded machine-code helper routines

## VRAM

SCREEN 7 data and graphics assets live in V9938 VRAM. `.SC7` files are loaded as VRAM dumps.

## RAM disk

The RAM disk consumes RAM but reduces disk access. This is a deliberate trade-off: less free memory, but much faster and more predictable page reads.
