# Editor

The application contains an operator/editor mode for maintaining the displayed information.

Typical editing workflow:

```mermaid
flowchart LR
    Edit[Operator edits page]
    Edit --> Save[Save page]
    Save --> Disk[Disk files]
    Disk --> RAM[RAM disk refresh]
    RAM --> Display[Display loop]
```

The editor is intended for local maintenance of the information pages rather than general-purpose text editing.
