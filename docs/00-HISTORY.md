# History

## The broadcaster: ZZBO

The **ZZBO** — *Zaanse Zieken en Bejaarden Omroep* (Zaans Sick and Elderly Broadcasting) — was a local cable television broadcaster in the **Zaanstreek** region of the Netherlands. Since 1965 it produced radio and, later, television programs for the sick and elderly care facilities in the area: hospitals, nursing homes, and residential care centres.

The broadcaster operated on the internal cable television network shared by these facilities. Patients and residents could watch the ZZBO channel on the television sets in their rooms and in public areas, alongside regular broadcast programming.

In addition to programming, ZZBO wanted to use the cable channel as a practical information medium — a continuously running electronic bulletin board visible to anyone watching. This became the **ZZBO Kabelkrant** (cable newspaper).

---

## The problem

Care facilities have a constant flow of information that needs to reach patients, visitors, and staff:

- daily menus
- visiting hours per department
- announcements and notices
- local news and events
- service information

Printing and distributing paper notices is slow, labour-intensive, and quickly goes out of date. A television channel that could be updated from one central point and viewed anywhere in the building was a natural solution — if the technology existed at an affordable price.

---

## Why MSX?

In the Netherlands, the **MSX** home computer standard remained popular well into the late 1980s and early 1990s, longer than in most other Western countries. **Philips** was one of the main MSX manufacturers in Europe and sold its machines through consumer electronics retailers — making them affordable and accessible outside the professional computing market.

The critical capability was video output. The MSX2 video processor, the **Yamaha V9938**, produced a composite/RGB signal directly suitable for connection to a television set or to a local cable distribution system. No scan conversion or expensive interface hardware was needed.

The **Philips NMS-8250** — a dual-floppy MSX2 — was well suited to the role:

- It could run unattended, boot automatically from floppy, and loop indefinitely.
- Its video output could be fed directly into the cable TV system.
- It was affordable compared to dedicated broadcast equipment.
- MSX BASIC was sufficient to build a practical information display system.

A home computer became a broadcast appliance.

---

## Development history

### Version 5.3x — the dial-up BBS era (c. 1990)

The earliest preserved version of the software dates to around **1990**, when the copyright line reads *"KabelKrant (c) 1990 by RitBit Software Inc."*

In this version, the system was not a standalone kiosk. It was a **dial-up BBS** (bulletin board system): editors and staff could telephone in over a modem to read and update the kabelkrant content remotely. The software included:

- `LOGIN.SYS` / `LOGOFF.SYS` — user authentication with username and password
- `MDMBASIC.BIN` — a modem support binary
- `TEKST-M.SYS` / `TEKST-T.SYS` — two separate text-handling modules
- `USER.DTA` — user account data
- `REQUEST.DTA` / `COMMENTS.DTA` — request and comment data files
- `LOG.DTA` — session logging

The main menu offered options including *"Grafisch (nog niet mogenlijk)"* (graphical — not yet possible) and *"VHS programma (nog niet mogenlijk)"* (VHS program — not yet possible), showing planned features that were never fully implemented.

This version connected the world of 1990s Dutch BBS culture with a local TV broadcast use case.

### Version 5.44 — the transition

An intermediate version removed the BBS and modem infrastructure entirely. Authentication, modems, and session logging disappeared. The focus shifted to the local display-only kiosk model. The graphical assets were still stored as a single `MAINPAGE.SC7`, and the operator utilities were not yet separated into dedicated modules.

### Version 6.2 — the production kiosk (1994)

By **1994**, the software had evolved into a mature, purpose-built display system. The source file headers are dated between January and July 1994, with version numbers reading *"Kabelkrant V6.2"*.

Key changes from earlier versions:

- The modem and BBS code was fully removed.
- The display system became entirely graphical, using dedicated asset sheets (`KRANT3.SC7`, `KRANT4.SC7`).
- A custom proportional font system replaced any text-mode output during live display.
- A graphical fault screen (`STORING.SC7`) was added.
- New utility modules (`UTILS.SYS`, `PAPER.SYS`) were introduced.
- The RAM disk caching strategy was refined.
- The system gained 14 animated wipe transitions between pages.

A note in the source comments records a small update in **1999**: drive references were changed from `B:` to `A:`, suggesting the system was still running and maintained five years after the original release.

---

## In production

The system ran on an MSX2 in the broadcast environment, connected to the cable TV distribution system. It cycled through information pages during whatever hours the channel ran informational content rather than active programming.

Operators — ZZBO staff or facility employees — could interrupt the live display by pressing the space bar, enter the operator menus, update page text or the daily page schedule, and return to the broadcast loop.

The system was practical and low-maintenance. Once configured for a given week, it ran entirely unattended.

---

## Preservation

The original floppy disks were preserved and the source extracted for archiving. The code was published to GitHub in 2026, more than 30 years after the last major development.

The repository contains:

- the version 6.2 source in `src/`
- the version 5.3x source in `archive/5.3x/`
- the version 5.44 source in `archive/5.44/`

See [VERSION-HISTORY.md](VERSION-HISTORY.md) for a detailed comparison of the versions.
See [01-HARDWARE.md](01-HARDWARE.md) for the hardware platform details.
