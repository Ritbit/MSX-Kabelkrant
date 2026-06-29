# System Overview

The software is an MSX BASIC application with a small Z80 RAM-disk binary.

It cycles through information pages built from simple `.TXT` files and schedule data. Graphics and font data are stored as MSX2 SCREEN 7 VRAM dumps.

## Runtime overview

```mermaid
flowchart TD
    A[AUTOEXEC.BAS] --> B[RAMDISK.BIN]
    B --> C[KBLINIT.SYS]
    C --> D[Load SC7 graphics]
    C --> E[Copy PAG/TXT files to C:]
    E --> F[LOOP.SYS]
    F --> G[Read KRANT.PAG]
    G --> H[Open page TXT file]
    H --> I[Render title/body/icon]
    I --> J[Wait / clock / animation]
    J --> K[Wipe transition]
    K --> H
    F --> L[MAIN.SYS operator menu]
```

## Example page file

`BEZOEKTD.TXT` demonstrates the page content structure:

```text
1
Bezoektijden
Voor de meeste afdelingen gelden de
volgende bezoektijden: 's middags van
13:30 tot 14:00 uur en 's avonds van
18:00 tot 19:30 uur.

Voor een aantal afdelingen gelden af-
wijkende bezoektijden. Vraag op deze
afdelingen het verplegend personeel
naar de exacte bezoektijden.
```
