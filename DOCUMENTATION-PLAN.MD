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

| Status | Document             | Notes |
| ------ | -------------------- | ----- |
| ☑      | README.md            | Rewritten with screenshots, ZZBO context, full docs index |
| ☑      | LICENSE              | |
| ☑      | CONTRIBUTING.md      | |
| ☑      | CHANGELOG.md         | |
| ☑      | SOFTWARE-OVERVIEW.md | |
| ☑      | ARCHITECTURE.md      | Expanded: layers, data flow, startup sequence, design decisions |
| ☑      | VERSION-HISTORY.md   | Documented all three versions: v5.3x, v5.44, v6.2 |

---

# Phase 2 — Historical Documentation

These documents explain the history of the project.

| Status | Document               | Notes |
| ------ | ---------------------- | ----- |
| ☑      | HISTORY.md             | Written as `00-HISTORY.md` — ZZBO, BBS origins, production kiosk |
| ☑      | HARDWARE.md            | Written as `01-HARDWARE.md` — NMS-8250, V9938, MSX.org links |
| ◐      | DEVELOPMENT-HISTORY.md | Covered in `00-HISTORY.md` and `VERSION-HISTORY.md`; standalone doc not yet created |
| ◐      | HOSPITAL-DEPLOYMENT.md | Covered in `00-HISTORY.md`; standalone doc not yet created |

Topics covered:

* Why the project was started — ☑
* Earlier versions (v5.3x BBS, v5.44, v6.2) — ☑
* Philips NMS-8250 hardware — ☑
* Local television network — ☑
* Hardware configuration — ☑
* Operational lifetime and 1999 update — ☑

---

# Phase 3 — Source Code Architecture

Reverse engineer the BASIC source.

| Status | Document            | Notes |
| ------ | ------------------- | ----- |
| ☑      | BOOT.md             | `docs/internal/BOOT.md` |
| ☑      | INITIALISATION.md   | `docs/internal/INITIALISATION.md` |
| ☑      | DISPLAY-LOOP.md     | `docs/internal/DISPLAY-LOOP.md` |
| ☑      | OPERATOR-GUIDE.md   | `docs/12-OPERATOR-GUIDE.md` — with screenshots |
| ☑      | MODULE-REFERENCE.md | `docs/11-MODULE-REFERENCE.md` — all modules with line references |

Delivered:

* sequence diagrams — ☑ (in ARCHITECTURE.md and internal docs)
* module dependencies — ☑ (in ARCHITECTURE.md)
* GOSUB maps — ◐ (partial, in RENDERING.md and DISPLAY-LOOP.md)
* global variables — ◐ (partial, in RENDERING.md)

---

# Phase 4 — Rendering Engine

Document the graphics engine.

| Status | Document         | Notes |
| ------ | ---------------- | ----- |
| ☑      | RENDERING.md     | Complete deep dive: font, metrics, icons, wipes, clock, scratch rendering |
| ☐      | SCREEN-LAYOUT.md | Not yet written |
| ☑      | PAGE-FORMAT.md   | Complete: KRANT.PAG structure with hex dump, .TXT format |

Topics covered:

* SCREEN 7 — ☑
* Proportional font — ☑
* Glyph metrics (X.DAT) — ☑
* Icon rendering — ☑
* Right-aligned scratch rendering — ☑
* Wipe effects — ☑
* Clock drawing — ☑
* Performance notes — ☑

---

# Phase 5 — RAM Disk

| Status | Document        | Notes |
| ------ | --------------- | ----- |
| ◐      | RAMDISK.md      | `docs/08-RAMDISK.md` exists but is thin; `docs/internal/RAMDISK-USAGE.md` also exists |
| ◐      | MEMORY-USAGE.md | `docs/09-MEMORY-USAGE.md` exists but is thin |

---

# Phase 6 — File Formats

| Status | Document        | Notes |
| ------ | --------------- | ----- |
| ☑      | FILE-FORMATS.md | `docs/10-FILE-FORMATS.md` — KRANT.PAG hex dump, .SC7, .TXT, metric files |

---

# Phase 7 — Individual Modules

Reverse engineer every source file.

| Status | Module       | Notes |
| ------ | ------------ | ----- |
| ☑      | AUTOEXEC.BAS | Covered in `docs/internal/BOOT.md` |
| ☑      | KBLINIT.SYS  | Covered in `docs/internal/INITIALISATION.md` |
| ☑      | LOOP.SYS     | Covered in `docs/internal/DISPLAY-LOOP.md` + `docs/RENDERING.md` |
| ☑      | MAIN.SYS     | Covered in `docs/12-OPERATOR-GUIDE.md` |
| ◐      | SYSTEM.SYS   | Covered in `docs/12-OPERATOR-GUIDE.md` (overview only) |
| ◐      | UTILS.SYS    | Covered in `docs/12-OPERATOR-GUIDE.md` (overview only) |
| ◐      | TEKST.SYS    | Covered in `docs/12-OPERATOR-GUIDE.md` (overview only) |
| ◐      | KRANT.SYS    | Covered in `docs/12-OPERATOR-GUIDE.md` (overview only) |
| ☐      | PAPER.SYS    | Not yet documented |
| ☐      | HEADER.SYS   | Not yet documented |

---

# Phase 8 — Visual Documentation

| Status | Item                    | Notes |
| ------ | ----------------------- | ----- |
| ☑      | Boot screenshots        | `startup.png` |
| ☑      | Main menu               | `Hoofd-menu.png` |
| ☑      | Editor                  | `Tekst-invoeren.png` |
| ☑      | Example pages           | `Krant-live.png` |
| ☑      | Asset / font sheet      | `Virtuele-Pagina-bekijken.png` |
| ☑      | All operator menus      | Full set in `docs/images/` |
| ☑      | SCREENSHOTS.md          | Gallery with descriptions for all 20+ images |
| ☐      | Clock close-up          | No dedicated clock screenshot yet |
| ☐      | Wipe animations         | Dynamic; difficult to capture as stills |

---

# Phase 9 — Repository Polish

| Status | Item                          | Notes |
| ------ | ----------------------------- | ----- |
| ☑      | Cross-reference all documents | Done in ARCHITECTURE.md, README.md, and all major docs |
| ☑      | Verify Mermaid diagrams       | Diagrams added/updated in ARCHITECTURE.md, internal docs |
| ☑      | Link screenshots              | SCREENSHOTS.md + 12-OPERATOR-GUIDE.md + README.md |
| ☐      | Proofread                     | Not yet |
| ☐      | Verify technical accuracy     | Not yet |
| ☐      | Final release                 | Not yet |

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

Remaining work in priority order:

1. Expand `docs/08-RAMDISK.md` — the RAM disk binary and BASIC interface deserve more detail
2. Expand `docs/09-MEMORY-USAGE.md` — BASIC memory pressure and the RAM disk trade-off
3. Write `SCREEN-LAYOUT.md` — document the SCREEN 7 page layout coordinates
4. Expand `SYSTEM.SYS`, `UTILS.SYS`, `TEKST.SYS`, `KRANT.SYS` module docs
5. Document `PAPER.SYS` and `HEADER.SYS`
6. Proofread all documents for factual accuracy
