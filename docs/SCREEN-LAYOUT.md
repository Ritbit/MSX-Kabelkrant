# Screen Layout

This document maps the coordinate zones of the Kabelkrant display in SCREEN 7 (512×212 pixels).

All coordinates are absolute pixel values as used in `LOOP.SYS`. X ranges 0–511 (left–right), Y ranges 0–211 (top–bottom).

---

## Display zones

```text
  X:  0                                                       511
  Y:  ┌────────────────────────────────────────────────────────┐
  0   │  HEADER BANNER                             │  CLOCK    │
      │  Day-of-week / ZZBO identity               │  top-right│
 44   ├──────────────┬─────────────────────────────┴───────────┤
      │  ICON        │  TITLE  (large font, Y≈51–65)           │
      │  top-left    ├─────────────────────────────────────────┤
      │  Y=50–90     │  BODY TEXT                              │
      │              │  Lines 1–10, Y=51+(R-1)*16              │
      │  HOURGLASS   │  each line ~16 px tall                  │
      │  Y=90–130    │                                         │
212   └──────────────┴─────────────────────────────────────────┘
```

---

## Zone details

### Header banner — rows 0–43

The 44-row header is loaded from the `KRANT4.SC7` asset page and is never redrawn between pages. During wipe transitions the header is preserved by backing it up to row 212:

```basic
COPY (0,0)-(512,44) TO (0,212)   ' backup header below visible area
```

The day-of-week element and clock within the header are the only parts that update during live display.

### Icon area — top-left, destination (5, 50)

A pictogram chosen by the page type number (line 1 of the `.TXT` file) is copied from `KRANT4.SC7` on VRAM page 1. Source positions and meanings:

| Type | Source on page 1 | Icon |
|---|---|---|
| 0 | `(0,0)–(27,15)` | Arrow / pointer |
| 1 | `(28,0)–(57,15)` | Television |
| 2 | `(58,0)–(87,15)` | Radio |
| 3 | `(88,0)–(117,15)` | House |
| 4 | `(118,0)–(147,15)` | Envelope |
| 5 | `(148,0)–(177,15)` | Fork and knife |
| 6 | `(178,0)–(207,15)` | Exclamation mark |
| 7 | `(208,0)–(237,15)` | Heart |
| 8 | `(238,0)–(267,15)` | Scissors and comb |
| 9 | `(268,0)–(297,15)` | Flowers / plants |

All icons are copied to destination `(5, 50)` on the visible page.

### Hourglass — destination (10, 90)

The hourglass animation sits below the icon. It advances one frame per display cycle using a counter `A` (0–99):

```basic
COPY (INT(A/10)*26, 17)-(INT(A/10)*26+25, 43), 1 TO (10,90), 0
```

When the counter reaches 100, a separate fill/empty animation plays before resetting.

### Clock — top-right corner, rows 0–43

The analog clock is updated by the `INTERVAL` timer handler (approximately every 0.5 s). Clock hands are drawn with `LINE` commands over the clock face graphic within the header area on VRAM page 1.

### Title — Y≈51, font type LT=3

The page title (line 2 of `.TXT`) is rendered in the large font:

```basic
X=50: Y=51: LT=3: K=15: GOSUB 2500
```

Large font glyphs are ~14–16 px tall, occupying rows 51–66 approximately.

### Body text — Y=51+(R-1)*16, font type LT=1

Body lines are rendered in the smaller body font with a 16-pixel line pitch:

```basic
X=50: Y=51+((R-1)*16): LT=1: K=15: GOSUB 2500
```

| Line (R) | Y position |
|---|---|
| 1 | 51 |
| 2 | 67 |
| 3 | 83 |
| 4 | 99 |
| 5 | 115 |
| 6 | 131 |
| 7 | 147 |
| 8 | 163 |
| 9 | 179 |
| 10 | 195 |

Line 10 at Y=195 uses the last ~16 rows before the display bottom (Y=211).

### Page counter — right-aligned in header

The `3/12` counter is rendered with a negative-X sentinel (right-aligned):

```basic
A$=STR$(PG+1)+"/"+PT$: X=-425: Y=9: LT=3: K=13: GOSUB 2500
```

`X=-425` means: render into scratch, then place so the right edge lands at pixel 425 — to the left of the clock area.

---

## Hidden VRAM page 1 layout

VRAM page 1 is loaded with `KRANT4.SC7` and is never displayed. It is the permanent source for all `COPY` blits:

```text
KRANT4.SC7 on VRAM page 1 (512×212 pixels):
  Y   0– 44   Large font glyph strip (LT=3)
  Y  45– 95   Medium font glyph strip (LT=2)
  Y  96–160   Small / body font glyph strip (LT=1)
  Y 160–189   Icons, hourglass frames, UI decorations
  Y 190–209   *** SCRATCH ZONE — written at runtime by text renderer ***
```

The scratch zone (Y=190–209) is used by the right-alignment renderer:

```basic
' render glyphs to scratch first, then reposition
IF X<0 THEN COPY(X1,Y1)-(X2,Y2),1 TO (XX,190),1
...
IF X<0 THEN X=ABS(X)-XX: COPY (0,190)-(XX-1,209),1 TO (X,Y),0,TPSET
```

This area is written and overwritten for every right-aligned string render. The KRANT4.SC7 assets in this row band are either not needed after initial use, or are accessed before the scratch operation within the same render call.

---

## Wipe transition zone

Wipe transitions operate on the full body area, rows 44–212:

```basic
'Wipes moeten lopen van line 48 tot 212 en 0 tot 512 (256*512)
```

The header (rows 0–43) is excluded from wipes — it remains static. After a wipe clears the body area, the new page content is rendered into the cleared zone before the next wipe.

---

## See also

- [RENDERING.md](RENDERING.md) — complete rendering pipeline with glyph metrics
- [internal/TEXT-ENGINE.md](internal/TEXT-ENGINE.md) — text renderer source analysis
- [10-FILE-FORMATS.md](10-FILE-FORMATS.md) — page type numbers and .TXT format
- [SCREENSHOTS.md](SCREENSHOTS.md) — annotated screenshots showing all zones
