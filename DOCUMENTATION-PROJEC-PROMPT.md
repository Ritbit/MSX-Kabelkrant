# MSX-Kabelkrant Documentation Project

## Context

You are joining an existing documentation effort for the **MSX-Kabelkrant** project.

The repository already contains substantial documentation. **Do not redesign the repository structure.**

The documentation structure is considered stable.

Your job is to **improve** the documentation, not reorganize it.

---

# Project

MSX-Kabelkrant is a real hospital information system written in **MSX BASIC** for the **Philips NMS-8250 MSX2**.

The current version in the repository is **version 6.2 (1994)**, although earlier versions (5.x and older) may be added later.

The software was used in production inside a hospital to display continuously rotating information pages on televisions.

The project is preserved primarily for historical and educational purposes.

---

# Repository

The Git repository is the **single source of truth**.

Never create duplicate documentation.

Never create "v2", "new", "fixed", "copy", or similar files.

Always edit the existing documents.

---

# Documentation philosophy

The repository should eventually become the technical manual that should have accompanied the software in 1994.

The documentation has three audiences:

* retro-computing enthusiasts
* MSX developers
* software engineers interested in historical software engineering

The goal is to explain:

* what the system does
* how it works
* why it was implemented this way

---

# General rules

1. Never invent behaviour.

If something is uncertain:

* inspect the source code
* inspect the data files
* inspect emulator output

If it still cannot be determined:

state clearly that the behaviour is currently unknown.

Never present guesses as facts.

---

2. The BASIC source is authoritative.

Whenever documentation contradicts source code, the source code wins.

---

3. Avoid duplication.

Every topic has exactly one "home".

Example:

* Rendering algorithms belong in `RENDERING.md`
* File structures belong in `FILE-FORMATS.md`
* Module internals belong in `MODULE-REFERENCE.md`
* System overview belongs in `ARCHITECTURE.md`

Other documents should reference these instead of repeating them.

---

4. Explain engineering decisions.

Do not merely describe what happens.

Also explain why it is implemented that way.

Examples:

* Why use SCREEN 7?
* Why proportional fonts?
* Why a RAM disk?
* Why random-access files?
* Why fixed-width filenames?
* Why render to a scratch area for right alignment?

---

5. Preserve history.

This repository documents an original 1994 implementation.

Do not modernize terminology or rewrite historical implementation decisions.

---

# Existing documentation

Before editing anything:

Read every document under:

docs/

Understand what is already documented.

Update existing documents rather than creating new ones.

---

# Documentation plan

The file:

DOCUMENTATION-PLAN.md

is the master checklist.

Always follow that plan.

When a document is completed:

* mark it complete in DOCUMENTATION-PLAN.md
* do not invent new phases
* do not redesign the roadmap

---

# Current priority

Work strictly in this order unless instructed otherwise:

1. RENDERING.md
2. PAGE-FORMAT.md
3. RAMDISK.md
4. MEMORY-USAGE.md
5. MODULE-REFERENCE.md
6. ARCHITECTURE.md
7. VERSION-HISTORY.md

---

# Expected quality

Every document should be source-driven.

For example, RENDERING.md should contain:

* complete rendering pipeline
* SCREEN 7 usage
* proportional font system
* glyph lookup
* X.DAT usage
* page layout
* title rendering
* body rendering
* pictograms
* clock
* wipe effects
* performance analysis
* implementation tricks

with Mermaid diagrams where appropriate.

---

# Reverse engineering

Treat the project like software archaeology.

Read the source carefully.

Build an understanding of the implementation.

Document that understanding.

Do not merely describe BASIC statements.

Explain the design.

---

# Source code documentation

When documenting modules:

Describe:

* purpose
* entry points
* global variables
* arrays
* files used
* routines
* call graph
* data flow
* implementation notes

Avoid line-by-line commentary unless it contributes to understanding.

---

# File formats

Document:

* KRANT.PAG
* *.TXT
* X.DAT
* XK.DAT
* YK.DAT
* *.SC7 (only as VRAM dumps)
* RAMDISK.BIN interface (not necessarily the assembly internals)

Use diagrams where helpful.

---

# Diagrams

Use Mermaid extensively.

Prefer diagrams over long textual descriptions.

Useful diagrams include:

* sequence diagrams
* flowcharts
* dependency graphs
* memory maps
* rendering pipelines
* boot sequence
* page lifecycle

---

# Historical accuracy

Whenever possible:

Verify documentation by:

* reading source
* examining assets
* running the emulator

Do not rely on assumptions.

---

# Working style

You have direct filesystem access.

Use it.

Read the existing documentation first.

Then improve it incrementally.

Never regenerate everything.

Never overwrite good documentation with shorter documentation.

Always leave the repository in a better state than you found it.

---

# Final objective

The completed repository should become one of the best documented historical MSX software projects available on GitHub.

A developer unfamiliar with MSX should be able to understand the complete architecture without first reading thousands of lines of BASIC source code.
