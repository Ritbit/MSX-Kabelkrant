; V9938 SCREEN 7 LMMM/TPSET command prototype. Not emulator tested.
; R#32-R#46 are populated at LmmmParams. NOT reentrant.
VDPCTRL EQU 099h
VDPIND  EQU 09Bh

LmmmLaunch:
    push af
    push bc
    push de
    push hl
    ld a,i
    jr po,.irq_off
    ld a,1
    jr .irq_saved
.irq_off:
    xor a
.irq_saved:
    ld (LmmmSavedIFF),a
.wait_idle:
    di
    ld a,2
    out (VDPCTRL),a
    ld a,08Fh
    out (VDPCTRL),a
    in a,(VDPCTRL)
    ld d,a
    xor a
    out (VDPCTRL),a
    ld a,08Fh
    out (VDPCTRL),a
    ld a,d
    and 1
    jr z,.issue
    ld a,(LmmmSavedIFF)
    or a
    jr z,.wait_idle
    ei
    jr .wait_idle
.issue:
    ld a,32
    out (VDPCTRL),a
    ld a,091h
    out (VDPCTRL),a
    ld hl,LmmmParams
    ld b,15
    ld c,VDPIND
    otir
    ld a,(LmmmSavedIFF)
    or a
    jr z,.done
    ei
.done:
    pop hl
    pop de
    pop bc
    pop af
    ret

LmmmSavedIFF: db 0
LmmmParams:
LmSX:  dw 0
LmSY:  dw 0
LmDX:  dw 0
LmDY:  dw 0
LmNX:  dw 0
LmNY:  dw 0
LmCLR: db 0
LmARG: db 0
LmCMD: db 098h
