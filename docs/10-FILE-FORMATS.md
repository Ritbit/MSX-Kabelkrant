# File Formats

## Page text files

Observed structure:

```text
type-number
title
body line 1
body line 2
...
```

Example `BEZOEKTD.TXT`:

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

## Menu text files

### MENU01.TXT
```text
6
Het menu
MAANDAG 25 APRIL:

Heldere champignonsoep

Varkenscarree
Spinazie
Gekookte aardappelen
Bleekselderiesla

Yoghurt met aardbeien
```

### MENU02.TXT
```text
6
Het menu
DINSDAG 26 APIRL:

Gebonden kerriesoep

Runderlapje
Bietjes
Gekookte aardappelen
Koolrabiesalade

Peer met saus
```

### MENU03.TXT
```text
6
Het menu
WOENSDAG 27 APRIL:

Heldere groentesoep

Gevulde paprika
Sperziebonen
Rijst
Taugeesalade

Bananenvla
```

### MENU04.TXT
```text
6
Het menu
DONDERDAG 28 APRIL:

Linzensoep

Kippebout
Macedoine
Gebakken krieltjes
IJsbergsla

Meloen
```

### MENU05.TXT
```text
6
Het menu
VRIJDAG 29 APRIL:

Heldere selderijsoep

Kaasomelet met tomatensaus
Snijboontjes
Aardappelpuree
Gemengde salade

Vlaflip
```

## `KRANT.PAG`

Binary/random-access page schedule file.

Size: 2048 bytes
SHA256: 2b0c91a98fa8b3369ce27da7dc0b117a6a6588fda98843fe3f5e609176f57d21
First 256 bytes (hex):
```
5a 5a 42 4f 31 20 20 20 5a 5a 42 4f 32 20 20 20 54 4f 54 41 41 4c 20 20 54 4f 54 41 41 4c 34 31 45 4e 51 55 45 54 45 20 54 4f 54 41 41 4c 34 32 4f 50 52 4f 45 50 53 59 54 4f 54 41 41 4c 34 33 50 41 54 53 45 52 56 20 54 4f 54 41 41 4c 34 34 50 4f 53 54 20 20 20 20 54 4f 54 41 41 4c 34 35 54 45 4c 45 46 4f 4f 4e 42 45 5a 4f 45 4b 54 44 54 4f 54 41 41 4c 34 36 4f 45 43 55 44 49 45 4e 54 4f 54 41 41 4c 34 37 47 45 45 53 5a 4f 52 47 4b 45 52 4b 20 20 20 20 57 41 4e 44 45 4c 45 4e 4d 45 4e 55 30 31 20 20 53 59 53 20 20 20 20 20 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d 2d
```

## `.SC7` files

`INTRO.SC7`, `KRANT3.SC7`, and `KRANT4.SC7` are SCREEN 7 VRAM dumps. They are loaded by BASIC as graphics assets.

## Metric files

`X.DAT`, `XK.DAT`, and `YK.DAT` are used as coordinate/metric data for text rendering and clock drawing.

## Binary support files

`RAMDISK.BIN` is loaded with `BLOAD ...,R` and installs drive `C:`.
