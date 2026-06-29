# Limitations

The system reflects practical MSX2 constraints.

## Performance

The slowest areas are graphical text rendering and wipe transitions. Disk I/O is partly mitigated by the RAM disk.

## Memory

MSX BASIC memory is limited. The RAM disk improves I/O performance but consumes memory.

## Storage

Filenames and page references follow MSX-DOS style limitations. The page schedule uses fixed-width names.

## Maintainability

The program uses global variables and line-numbered BASIC. This was normal for the environment but makes later maintenance harder.
