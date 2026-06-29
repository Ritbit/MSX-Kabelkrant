# Boot and Startup Flow

This document describes the actual startup flow visible in the published source.

## Entry point

The system starts from:

```text
src/AUTOEXEC.BAS
```

`AUTOEXEC.BAS` is intentionally very small. Its job is not to run the whole program directly, but to prepare BASIC so that the RAM disk binary can be loaded and control can continue into `KBLINIT.SYS`.

## AUTOEXEC.BAS behaviour

The file header identifies it as:

```text
Name      : AUTOEXEC.BAS
Date      : 06-06-1994
Function  : Autostart of kabelkrant
Part of   : Kabelkrant V6.2
Chains to : KBLINIT.SYS
```

Important actions:

1. Sets Ctrl-Stop behaviour by writing to MSX system variable memory.
2. Prepares a BASIC command string that will run `KBLINIT.SYS`.
3. Injects that command into the keyboard/input buffer.
4. Loads `RAMDISK.BIN` with `BLOAD "RAMDISK.BIN",R`.

The important trick is that `AUTOEXEC.BAS` prepares the next BASIC command before loading the binary. After `RAMDISK.BIN` has installed itself, BASIC continues using the prepared command and runs:

```basic
RUN "KBLINIT.SYS"
```

## Startup sequence

```mermaid
sequenceDiagram
    participant BASIC as MSX BASIC
    participant AUTO as AUTOEXEC.BAS
    participant RAM as RAMDISK.BIN
    participant INIT as KBLINIT.SYS
    participant LOOP as LOOP.SYS

    BASIC->>AUTO: boot AUTOEXEC.BAS
    AUTO->>BASIC: prepare keyboard buffer with RUN "KBLINIT.SYS"
    AUTO->>RAM: BLOAD "RAMDISK.BIN",R
    RAM-->>BASIC: returns after installation
    BASIC->>INIT: executes prepared RUN command
    INIT->>LOOP: RUN "LOOP.SYS"
```

## Why this is interesting

This is a very MSX-specific bootstrapping technique. The BASIC program uses the keyboard buffer/system input area as a hand-off mechanism around a binary loader.

That allows the binary RAM disk installer to run first, while still continuing automatically into the BASIC initialisation program afterwards.
