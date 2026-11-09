# Agent / contributor rules — development branch only

**Scope:** `feature/z80-renderer` in `Ritbit/MSX-Kabelkrant`.

This file and `CONTEXT.md`, `PLAN.md`, `TODO.md`, `BUILD-AND-TEST.md` are development
coordination files. **Do not merge, cherry-pick, copy, or include these
five files in `main` or any release PR.** They are intentionally absent
from stable branches.

## Read first

1. `CONTEXT.md` for architecture and current verified state.
2. `TODO.md` for the next runnable task.
3. `PLAN.md` for milestones and acceptance criteria.
4. `BUILD-AND-TEST.md` for reproducible build, openMSX and WebMSX steps.
5. `z80/COMBINED-STATUS.md` for the unresolved RAMdisk/CALL integration.

## Working rules

- Work on the feature branch only. Preserve existing `main` and the
  published v6.2b binaries. Never merge this branch wholesale.
- Prefer **small, reproducible experiments** that answer one hypothesis;
  update relevant tests and report exact GitHub Actions run IDs.
- Distinguish **compiled**, **started**, **executed**, **visually correct**,
  **pixel-equivalent**, and **benchmarked**. Never label a build a working
  disk or release until emulator execution supports that statement.
- Test with openMSX/NMS 8250; use WebMSX for optional manual checks.
  Keep MSX BIOS/ROM downloads out of commits, PRs and artifacts.
- Never change original `.SC7`, `X.DAT`, or historical `RAMDISK.BIN`
  merely to make tests pass. Apply corrections in code/converters.
- Preserve display order, colour/palette, transparent glyph copying,
  font metrics, clock interrupts and right-alignment semantics.
- Any candidate RAMdisk trimming needs an annotated call graph plus
  drive C: read/write/startup tests first.
- Provide users only genuine test images when needed for validation,
  not repeated intermediate screenshots by default.
- Use the original bootloader's RAMdisk warm-restart handoff; don't assume
  a plain mid-program `BLOAD ...,R` behaves the same way.
- Validate MSX BASIC files as CRLF-delimited text with bounded line
  lengths; keep source code LF in Git.
- Updating this document should describe **grounded facts**, not infer
  a runtime success from code inspection.

## Release workflow (important)

Create a new branch **from `main`**, then copy/cherry-pick **only the
specific production files and tests intended for release**. Review the
PR's changed-file list before opening it. Never create a release PR by
targeting `main` directly from `feature/z80-renderer`: that would carry
experiments and these coordination files. If any of these five docs
appears in a release diff, stop and remove it from the PR before merge.

The Git branch alone cannot technically enforce "never merge"; enforce
this operationally through release diffs/branch protection.
