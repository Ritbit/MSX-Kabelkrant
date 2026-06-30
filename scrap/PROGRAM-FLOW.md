# Program Flow

The Kabelkrant software is organised as a collection of BASIC modules loaded as required.

## High-level execution

```mermaid
flowchart TD
    A[AUTOEXEC.BAS] --> B[KBLINIT.SYS]
    B --> C[System initialisation]
    C --> D[Load graphics]
    C --> E[Prepare RAM disk]
    D --> F[Start LOOP.SYS]
    E --> F
    F --> G[Select page]
    G --> H[Render page]
    H --> I[Display transition]
    I --> G
    F --> J[Operator functions]
    J --> F
```

## Startup responsibilities

AUTOEXEC.BAS prepares the runtime environment and transfers control to the initialisation code.

KBLINIT.SYS prepares graphics, memory, data files and the runtime environment before entering the main display loop.

The display loop repeatedly selects, renders and presents information pages.
