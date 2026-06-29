# Documentation Roadmap

## Purpose

This roadmap describes the work required to fully document the original **MSX-Kabelkrant** project.

The goal is **not** to rewrite or modernise the software.

The goal is to preserve both the software **and the engineering knowledge** behind it.

Each document should be based on the original source code whenever possible.

---

# Status Legend

| Status | Meaning                                 |
| ------ | --------------------------------------- |
| ☐      | Not started                             |
| ◐      | In progress                             |
| ☑      | Completed                               |
| ⚠      | Needs review                            |
| 📷     | Waiting for screenshots                 |
| 🔍     | Requires additional reverse engineering |

---

# Phase 1 — Repository

These documents describe the project as a whole.

| Status | Document             |
| ------ | -------------------- |
| ☑      | README.md            |
| ☑      | LICENSE              |
| ☑      | CONTRIBUTING.md      |
| ☑      | CHANGELOG.md         |
| ☑      | SOFTWARE-OVERVIEW.md |
| ◐      | ARCHITECTURE.md      |
| ◐      | VERSION-HISTORY.md   |

---

# Phase 2 — Historical Documentation

These documents explain the history of the project.

| Status | Document               |
| ------ | ---------------------- |
| ☐      | HISTORY.md             |
| ☐      | HARDWARE.md            |
| ☐      | DEVELOPMENT-HISTORY.md |
| ☐      | HOSPITAL-DEPLOYMENT.md |

Topics include:

* Why the project was started
* Earlier versions
* Philips NMS-8250
* Local television network
* Hardware configuration
* Operational lifetime

---

# Phase 3 — Source Code Architecture

Reverse engineer the BASIC source.

| Status | Document            |
| ------ | ------------------- |
| ☐      | BOOT.md             |
| ☐      | INITIALISATION.md   |
| ☐      | DISPLAY-LOOP.md     |
| ☐      | OPERATOR-GUIDE.md   |
| ☐      | MODULE-REFERENCE.md |

Deliverables:

* call graphs
* sequence diagrams
* module dependencies
* global variables
* GOSUB maps

---

# Phase 4 — Rendering Engine

Document the graphics engine.

| Status | Document         |
| ------ | ---------------- |
| ☐      | RENDERING.md     |
| ☐      | SCREEN-LAYOUT.md |
| ☐      | PAGE-FORMAT.md   |

Topics:

* SCREEN 7
* proportional font
* glyph metrics
* icon rendering
* alignment
* hidden page rendering
* wipe effects
* clock drawing
* performance

---

# Phase 5 — RAM Disk

| Status | Document        |
| ------ | --------------- |
| ☐      | RAMDISK.md      |
| ☐      | MEMORY-USAGE.md |

Topics:

* installation
* BASIC interface
* startup
* update strategy
* runtime behaviour
* mapper usage
* interaction with LOOP.SYS

---

# Phase 6 — File Formats

| Status | Document        |
| ------ | --------------- |
| ☐      | FILE-FORMATS.md |

Document:

* KRANT.PAG
* *.TXT
* X.DAT
* XK.DAT
* YK.DAT
* *.SC7
* RAMDISK.BIN

---

# Phase 7 — Individual Modules

Reverse engineer every source file.

| Status | Module       |
| ------ | ------------ |
| ☐      | AUTOEXEC.BAS |
| ☐      | KBLINIT.SYS  |
| ☐      | LOOP.SYS     |
| ☐      | MAIN.SYS     |
| ☐      | SYSTEM.SYS   |
| ☐      | UTILS.SYS    |
| ☐      | TEKST.SYS    |
| ☐      | KRANT.SYS    |
| ☐      | PAPER.SYS    |
| ☐      | HEADER.SYS   |

For every module document:

* purpose
* entry points
* GOSUB layout
* variables
* files used
* routines
* implementation notes
* historical remarks

---

# Phase 8 — Visual Documentation

| Status | Item                    |
| ------ | ----------------------- |
| 📷     | Boot screenshots        |
| 📷     | Main menu               |
| 📷     | Editor                  |
| 📷     | Example pages           |
| 📷     | Clock                   |
| 📷     | Wipe animations         |
| 📷     | System overview diagram |

---

# Phase 9 — Repository Polish

| Status | Item                          |
| ------ | ----------------------------- |
| ☐      | Cross-reference all documents |
| ☐      | Verify Mermaid diagrams       |
| ☐      | Link screenshots              |
| ☐      | Proofread                     |
| ☐      | Verify technical accuracy     |
| ☐      | Final release                 |

---

# Documentation Rules

Every document should:

* be based on the source code whenever possible
* distinguish facts from assumptions
* include diagrams where useful
* explain *why* the software works the way it does
* preserve the historical implementation
* avoid unnecessary modernisation

---

# Current Priority

1. Finish ARCHITECTURE.md
2. Reverse engineer LOOP.SYS
3. Write RENDERING.md
4. Write PAGE-FORMAT.md
5. Write MODULE-REFERENCE.md

These five documents provide the largest increase in understanding of the project.
