# Hardware

## Deployment machine

The known deployment target was a **Philips NMS-8250** MSX2 computer.

Relevant characteristics:

- MSX2 architecture
- Z80 CPU
- V9938 video display processor
- SCREEN 7 graphics support
- floppy-based storage
- typical 128 KB class RAM configuration
- suitable video output for connection to a local television system

## System role

The MSX2 was not used as an interactive desktop machine during normal operation. It acted as an unattended information appliance: boot, load the bulletin system, cache data into RAM disk, then cycle through pages on the TV output.

```mermaid
flowchart LR
    A[Philips NMS-8250] --> B[MSX2 video output]
    B --> C[Local TV distribution]
    C --> D[Hospital rooms / public displays]
```
