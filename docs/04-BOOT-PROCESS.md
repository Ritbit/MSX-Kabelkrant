# Boot Process

The system starts in `AUTOEXEC.BAS`.

Detected startup-relevant lines:

- line 50: `' Chains to: KBLINIT.SYS`
- line 100: `POKE &HFBB1,0: ' 0 = Zet Crtl-Stop aan; 1 = Zet Ctrl-Stop uit!!`
- line 110: `COLOR 0,0,0: A$=CHR$(13)+"COLOR 0,0,0:Run"+CHR$(34)+"KBLINIT.SYS"+CHR$(34)+CHR$(13)`
- line 120: `POKE &HF3FA,&H00F0: POKE &HF3FB,&H00FB : FOR I=1 TO LEN(A$)`
- line 130: `POKE &HFBF0+I-1,ASC(MID$(A$,I,1)): NEXT: WR%=&HFBF0+LEN(A$)`
- line 140: `POKE &HF3F8,WR% AND 255: POKE &HF3F9,((WR% AND &HFF00)/256) AND 255`
- line 150: `BLOAD "RAMDISK.BIN",R`

## Boot sequence

```mermaid
sequenceDiagram
    participant BASIC as MSX BASIC
    participant AUTO as AUTOEXEC.BAS
    participant RAM as RAMDISK.BIN
    participant INIT as KBLINIT.SYS
    participant LOOP as LOOP.SYS

    BASIC->>AUTO: Run AUTOEXEC.BAS
    AUTO->>BASIC: Prepare continuation into KBLINIT.SYS
    AUTO->>RAM: BLOAD RAMDISK.BIN,R
    RAM-->>BASIC: RAM disk installed
    BASIC->>INIT: Run KBLINIT.SYS
    INIT->>LOOP: Start LOOP.SYS
```

## Key idea

`AUTOEXEC.BAS` exists mainly to bootstrap the binary RAM disk and then continue into BASIC initialisation.

The unusual part is the keyboard-buffer injection on lines 110–140. `AUTOEXEC.BAS` cannot simply `RUN "KBLINIT.SYS"` after `BLOAD` because `BLOAD ... ,R` transfers control to machine code and does not return normally. Instead, the program pre-loads the `RUN` command into the MSX keyboard input buffer *before* triggering the binary. When `RAMDISK.BIN` finishes and returns to BASIC, BASIC reads the buffer and executes the waiting command automatically.

---

## See also

- [internal/BOOT.md](internal/BOOT.md) — full annotated source analysis of the boot sequence
- [internal/INITIALISATION.md](internal/INITIALISATION.md) — what KBLINIT.SYS does after boot
- [ARCHITECTURE.md](ARCHITECTURE.md) — startup sequence diagram
