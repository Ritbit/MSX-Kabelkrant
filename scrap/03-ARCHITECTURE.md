# Architecture

The system is split into small BASIC modules. Each module is loaded with `RUN` when needed rather than keeping one large monolithic BASIC program resident.

## Main architectural layers

```mermaid
flowchart TD
    A[Boot layer] --> B[Initialisation layer]
    B --> C[RAM-disk cache layer]
    C --> D[Presentation loop]
    D --> E[Text renderer]
    D --> F[Wipe / transition engine]
    D --> G[Clock]
    D --> H[Operator menu]
    H --> I[Editor]
    H --> J[Page scheduler]
    H --> K[System utilities]
```

## Important design choices

- Use RAM disk drive `C:` to avoid repeated floppy reads during live display.
- Store page content as normal text files.
- Store page schedule separately in `KRANT.PAG`.
- Use SCREEN 7 graphics and `COPY` commands for proportional text and icons.
- Use separate BASIC modules for operator functions.
- Keep the display loop mostly autonomous and return to operator mode only on key/trigger.
