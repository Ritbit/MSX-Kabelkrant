# Boot Sequence

```mermaid
sequenceDiagram
    participant User
    participant BASIC
    participant Init
    participant RAM
    participant Loop

    User->>BASIC: Power on
    BASIC->>Init: AUTOEXEC.BAS
    Init->>RAM: Prepare RAM disk
    Init->>Loop: Start main loop
    Loop->>Loop: Display pages continuously
```

The startup procedure is intentionally simple to maximise unattended reliability.
