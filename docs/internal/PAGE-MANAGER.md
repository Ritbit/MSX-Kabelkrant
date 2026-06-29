# Page Management

Page scheduling and composition are split between `LOOP.SYS` and `KRANT.SYS`.

## Runtime page schedule

At runtime, `LOOP.SYS` loads the schedule from:

```text
C:KRANT.PAG
```

The file is opened as a random file with record size 256:

```basic
OPEN "C:KRANT.PAG" AS #1 LEN=256
FIELD #1,128 AS D$,128 AS E$
GET #1,WK
```

Each 256-byte record contains 32 page names:

- first 128 bytes: 16 page names
- second 128 bytes: 16 page names
- each page name: 8 characters

This maps directly into the runtime array:

```basic
N$(0) ... N$(31)
```

## End marker

A slot is considered empty/end-of-newspaper when:

```text
--------
```

or when the entry begins with a space.

## Page text files

Each page entry refers to a text file:

```text
<name>.TXT
```

During display, pages are opened from the RAM disk:

```text
C:<name>.TXT
```

During refresh, files are copied from drive `A:` to drive `C:`.

## KRANT.SYS

`KRANT.SYS` is the newspaper/page schedule editor.

It provides menu options for:

- composing a newspaper
- changing an existing newspaper
- saving
- loading
- reading/checking the newspaper

It maintains a 32-entry `N$()` page list and writes it back into `KRANT.PAG`.

## KRANT.PAG save format

When saving, `KRANT.SYS` concatenates the first 16 page names into one 128-byte field and the next 16 page names into another 128-byte field:

```basic
D1$ = N$(0)  + ... + N$(15)
E1$ = N$(16) + ... + N$(31)
RSET D$ = D1$
RSET E$ = E1$
PUT 1,WK
```

## Relationship between editor and runtime

```mermaid
flowchart LR
    A[KRANT.SYS editor] --> B[KRANT.PAG]
    B --> C[KBLINIT copies to RAM disk]
    C --> D[C:KRANT.PAG]
    D --> E[LOOP.SYS]
    E --> F[Display pages]
```

## Notes

The page manager uses fixed-width 8-character names, which fits well with MSX-DOS 8.3 naming limits and makes the `KRANT.PAG` record format simple.
