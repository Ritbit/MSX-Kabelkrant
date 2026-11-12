# Gregorian weekday regression — Z80/BASIC shared LOOP.SYS

The fixed source expression for line 1330 of `src/LOOP.SYS` is:

```basic
1330 DG=((Y\12+Y MOD 12+(Y MOD 12)\4+C(M)+(Y MOD 4=0 AND M<3 AND Y>0)+D+(Y<90)+(Y=0 AND M<3)) MOD 7)
```

Why: the original 1900-century weekday arithmetic omitted the **2000-century shift**. With the pre-existing year pivot (Y 90–99 means 1990–99; Y 00–89 means 2000–89), MSX BASIC boolean TRUE=-1 provides the needed subtraction in `(Y<90)`. January/February of **2000** require one more subtraction because the original formula excludes the year-00 leap boundary. Existing leap-year logic for 2004, 2008, ... already applies separately. `DG` retains 0=Saturday...6=Friday; `WK=((DG+5)MOD 7)+1` remains unchanged.

The compact 21-byte line extension was selected because the original 6.2b FAT12 `LOOP.SYS` has **14 fixed 1024-byte clusters**, with only **39 bytes** free before this change. The updated DOS source fits with **18 bytes** free; no changes to original FAT allocation.

## Regression gates

- `python3 tools/test_weekday.py`: checks the precise source formula and 36,525 valid dates from 1990-01-01 through 2089-12-31 against Python's Gregorian `datetime.date`.
- `z80/tools/make_weekday_proof.py`: creates a **disposable** BASIC test program with **217 cases** including century boundary, leap days, 2026-11-12 and 2026-11-13. It extracts the actual line 1330 from `src/LOOP.SYS`, compares its MSX BASIC output with independently generated expected values, and writes `A:WDAY.OK` only if all match.
- `z80/tools/openmsx_weekday.tcl`: NMS8250 ROM-backed execution; CI reads the FAT12 proof file using `mcopy`. No edits to production `KBLINIT.SYS` or released disk files.
- Build and runtime tests are opt-in for NMS8250 ROM acquisition via a commit message containing `[nms8250-rom-test]`.

Main BASIC 6.2b packaging [run 43237807415](https://github.com/Ritbit/MSX-Kabelkrant/actions/runs/43237807415) passed source tests, rebuilt the 720-KiB DSK and ZIP and updated the existing v6.2b release assets. The original v6.2 disk remains unchanged.
