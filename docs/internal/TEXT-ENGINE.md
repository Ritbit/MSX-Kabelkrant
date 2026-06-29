# Text Engine

The original text renderer is implemented in BASIC inside `LOOP.SYS`.

## Entry point

The renderer starts at:

```text
GOSUB 2500
```

It expects several global variables to be set before entry:

| Variable | Meaning |
|----------|---------|
| `A$` | text string to draw |
| `X` | destination X coordinate; negative means aligned scratch render |
| `Y` | destination Y coordinate |
| `LT` | font/letter type selector |
| `K` | colour/mask value |

## Font assets

The renderer uses graphics already loaded into VRAM from:

```text
KRANT4.SC7
```

It also uses glyph metrics loaded earlier:

```basic
COPY "X.DAT" TO X
```

and font row metadata defined in DATA lines inside `LOOP.SYS`.

## Font metadata

`LOOP.SYS` reads per-font metadata into:

```basic
L1(LT), L2(LT), L3(LT)
Y1(LT), Y2(LT), Y3(LT)
H(LT)
```

These values define glyph group thresholds, source Y positions and glyph heights.

## Render algorithm

For each character:

1. Convert ASCII to an internal glyph index using `ASC(...) - 33`.
2. Select the correct source row using `L1/L2/L3`.
3. Look up source X range from the `X()` table.
4. Copy the glyph from hidden/source page 1.
5. Either draw directly to page 0, or draw to a scratch area on page 1 if alignment is needed.
6. Advance the output width counter.

## Direct rendering

When `X >= 0`, glyphs are copied directly to the visible page:

```basic
COPY(X1,Y1)-(X2,Y2),1 TO (X+XX,Y),0,TPSET
```

## Scratch/aligned rendering

When `X < 0`, glyphs are first drawn into a scratch area around Y=190 on page 1. After the total width is known, the routine copies the line to the visible page using:

```basic
X = ABS(X) - XX
COPY (0,190)-(XX-1,209),1 TO (X,Y),0,TPSET
```

This makes it possible to position text based on its final measured width.

## Interrupt handling

The routine disables the clock interval around rendering-sensitive operations:

```basic
INTERVAL OFF
...
INTERVAL ON
```

This prevents the clock routine from drawing while the text routine is modifying VRAM/scratch areas.

## Why it is slow

The renderer is elegant but expensive because each character requires BASIC string operations, conditionals, table lookups and a VDP `COPY` command.
