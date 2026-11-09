# Combined RAMdisk + Z80 TEXT — confirmed memory collision

**Runtime status (2026-11-09): NOT WORKING. Do not release.**

## Confirmed using openMSX 19.1, Philips NMS 8250

At the failing `CALL KBLVER`, a CPU breakpoint **does reach 46F5h**
in slot 3-2 and RAM mapper segment 2. `SLTATR[57]` is 20h and the
Disk-ROM STATEMENT pointer at 4004h reads 46F5h. However the opcode
at 46F5h is 00h rather than expected E5h.

A write-watchpoint recorded **two writes** to physical 46F5h:

- PC **C032h**: installation copies E5h (correct first handler opcode).
- PC **41BFh**: original RAMdisk stores **00h** over it.

The unchanged ROM code at **41B3h** is:

```asm
LD HL,46F4h
LD DE,46F5h
LD BC,390Ah
LD (HL),0
LDIR
```

The RAMdisk deliberately zero-fills **46F4h–7FFEh** in that bank,
using the remaining area as disk/storage workspace. Our appended TEXT
engine at 46F5h is overwritten during normal installation. Enlarging
the initial installer copy length does **not** make the location safe.

Earlier notes claimed BASIC could not reach the handler. That was
incorrect: it reaches the right *address*, but the bytes are erased.

## Proven and unproven

- Standalone `KBLTXT.BIN` (E004h) previously displayed all four fonts,
  colours 15/13 and negative-X alignment under openMSX.
- Combined `KBLALL.BIN` assembles and fits within one 16-KiB mapper
  segment, but its runtime location **collides with RAMdisk storage**.
- A build passing on GitHub Actions is *not* proof that the combined
  executable works.
- The historical driver and the released 6.2b remain untouched.

## Revised design

Preserve the RAMdisk driver, and initialize Z80 TEXT in **separately
protected high RAM** after the RAMdisk warm restart. The original
page-1 ROM header has a tiny reserved space that might accommodate
a dispatch trampoline, but slot/mapper-safe entry, staging order and
BASIC memory allocation require emulator validation.

A single distributed binary with a two-stage loader is possible
in principle, but **not yet proven**. Repeated boot and source-loading
experiments have not passed end-to-end. Two binaries remain a valid
fallback if they preserve BASIC memory and drive C:.

Do not shrink the RAMdisk without first identifying all driver and
storage uses, then passing read/write tests on C:.
