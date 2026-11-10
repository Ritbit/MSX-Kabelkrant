# Integrating 14 wipe effects into the single-BLOAD Z80 Kabelkrant

**Status:** design/memory audit, not yet loaded into the live newspaper.
**Branch:** `feature/z80-renderer`; never modify v6.2b on main.

## Validated baseline

- Original RAMdisk loader: C000..C7EF, BLOAD entry C000. Keep unchanged.
- Z80 TEXT: C804 entry C806, extension installed via `DEFUSR3`.
- Current `make_onefile_preview.py` enforces exclusive end D804: just
  **4096 bytes** for the complete appendage.
- Successful CI built TEXT binary `KBLTXT.BIN` at 2138 total BLOAD
  bytes, i.e. **2131 bytes of payload**. Remaining space within the
  current 4KiB budget is **1965 bytes**.
- The CI audit measured **12,263 bytes** for TEXT plus all fourteen
  standalone payloads versus **4,096 bytes** of currently reserved space.
  This naive total includes duplicate helper code and is not the final
  expected size of a shared engine; nevertheless blind concatenation
  demonstrably cannot fit.
- Original 14 standalone wipes are not composable by concatenation:
  they start at the same C804 address, each has its own BLOAD vector,
  LMMV/CE/JIFFY helper, and the box/column effects embed hundreds of
  geometry records. Standalone runtime verification does *not* prove
  they will safely coexist with TEXT or RAMdisk.

Run `python3 z80/tools/audit_wipe_memory.py` after compiling TEXT and
all 14 standalones to see actual measured payload sizes. CI now runs
this automatically.

## Safe staged implementation

1. First create a *new optional test image*, not a replacement for
   `KBLONEFILE.DSK`. Add a single shared V9938 command/wait module
   and `CALL WIPE(n)` dispatch to the TEXT extension without altering
   the original RAMdisk or the existing text renderer.
2. Minimize footprint by using a **common wipe engine** and
   parameterized strategies for horizontal/vertical bands, paired
   movements, interlaced columns, and contours. Encode compact geometry
   or generate coordinates rather than including 14 complete copies
   of the V9938 command helper and full rectangle tables.
3. Enforce linker addresses and size strictly: C804..D803 unless a
   *separately proved* larger resident-memory layout is implemented.
   Any overrun fails CI. Do not raise `HIMEM` or assume extra mapper
   pages can be used without checking the RAMdisk and BASIC.
4. Preserve the original BASIC wipe selection behind an opt-in switch;
   on the test disk only, replace it with `CALL WIPE(n)` after
   validating each effect and the complete page loop, RAMdisk C: I/O,
   editor and screen persistence. Check return semantics and timing.
5. Only promote to normal development alpha after multiple page
   cycles and regression tests. Keep v6.2b unchanged.

## Wipe #14 known limitation

User accepted `KBLWIPE14FIX2.DSK` as sufficiently improved but
reported residual diagonal lines during the transition. The inner
rectangles have been recentered at Y=131 and a final black LMMV fill
covers X=0..511, Y=50..211. This guarantees terminal **drawn** black
state in source/compiled command sequence; the visually remaining
diagonal artifacts are **not** claimed fixed. Track as a low-priority
visual artifact. Do not describe #14 as pixel-perfect parity.

## Release boundary

No changes to `main`, no merge of branch-only coordination documents.
The existing working `KBLONEFILE.DSK` remains the rollback baseline.
