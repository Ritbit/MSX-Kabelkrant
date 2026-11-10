; Kabelkrant SCREEN 7 wipe effects #3/#4: horizontal 2-pixel strips.
; Wipe #3 x=0,2,...510. Wipe #4 x=510,508,...0.
; Geometry: x=0..511, y=50..211 (visible rows only).
; Standalone BLOAD/R demo, never loaded by KBLONEFILE.DSK.
; Direction selected with numeric WIPE_RIGHT_TO_LEFT (0/1).
; Pace one BIOS JIFFY per four completed strips (64 frames/transition).
    ORG 0C804h
    dw WipeHorizontal
JIFFY EQU 0FC9Eh

WipeHorizontal:
    push af
    push bc
    push de
    push hl

    IF WIPE_RIGHT_TO_LEFT
    ld hl,510              ; final visible pair is 510..511
    ELSE
    ld hl,0
    ENDIF
    ld (LmDX),hl
    ld hl,50
    ld (LmDY),hl
    ld hl,2
    ld (LmNX),hl
    ld hl,162
    ld (LmNY),hl
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h               ; LMMV/IMP black fill, not LINE outline
    ld (LmCMD),a
    ld a,4
    ld (WipePaceCounter),a
.next_strip:
    call LmmmLaunch
    call HorizontalWaitIdle

    ld hl,WipePaceCounter
    dec (hl)
    jr nz,.advance
    ld (hl),4
    call HorizontalWaitFrame

.advance:
    ld hl,(LmDX)
    IF WIPE_RIGHT_TO_LEFT
    ld a,h
    or l
    jr z,.done              ; x=0 was the last strip
    dec hl
    dec hl
    ELSE
    ld de,510
    or a
    sbc hl,de
    jr z,.done              ; x=510 was the last strip
    ld hl,(LmDX)
    inc hl
    inc hl
    ENDIF
    ld (LmDX),hl
    jr .next_strip
.done:
    ; VDP command completed before returning to BASIC.
    pop hl
    pop de
    pop bc
    pop af
    ret

; Wait for VDP S#2 CE bit 0 to clear; do not leave interrupts disabled.
; Restore the previous IFF2 state rather than blindly EI.
HorizontalWaitIdle:
    push af
    push de
    ld a,i
    jp po,.off
    ld a,1
    jr .saved
.off:
    xor a
.saved:
    ld (HorizontalIFF),a
.wait:
    di
    ld a,2
    out (099h),a
    ld a,08Fh
    out (099h),a
    in a,(099h)
    ld d,a
    xor a
    out (099h),a
    ld a,08Fh
    out (099h),a
    ld a,d
    and 1
    jr z,.done
    ld a,(HorizontalIFF)
    or a
    jr z,.wait
    ei
    jr .wait
.done:
    ld a,(HorizontalIFF)
    or a
    jr z,.restore
    ei
.restore:
    pop de
    pop af
    ret

HorizontalWaitFrame:
    push af
    push hl
    ld a,i
    jp po,.done
    ld hl,JIFFY
    ld a,(hl)
.wait:
    cp (hl)
    jr z,.wait
.done:
    pop hl
    pop af
    ret

WipePaceCounter: db 4
HorizontalIFF:    db 0
    INCLUDE 'v9938_lmmm.asm'
