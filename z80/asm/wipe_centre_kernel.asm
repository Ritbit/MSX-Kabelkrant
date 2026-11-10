; Wipes 5/6 toward centre. SCREEN 7 visible (x=0..511, y=50..211).
; Two simultaneous edges, each 2 pixels/scanlines thick.
; WIPE_FROM_SIDES numeric 0: top+bottom toward vertical centre.
; WIPE_FROM_SIDES numeric 1: left+right toward horizontal centre.
; These are ISOLATED test binaries and do not alter the working newspaper.
    ORG 0C804h
    dw WipeTowardCentre
JIFFY EQU 0FC9Eh

WipeTowardCentre:
    push af
    push bc
    push de
    push hl

    IF WIPE_FROM_SIDES
    ld hl,0
    ld (WipeNear),hl        ; left edge starts at X=0
    ld hl,510
    ld (WipeFar),hl         ; right edge starts at X=510
    ld hl,50
    ld (LmDY),hl
    ld hl,2
    ld (LmNX),hl
    ld hl,162
    ld (LmNY),hl
    ld a,128               ; 128 pairs of 2-pixel columns
    ld (WipeRemaining),a
    ld a,2                 ; one frame per 2 pairs (~64 frames)
    ELSE
    ld hl,50
    ld (WipeNear),hl        ; top starts at Y=50
    ld hl,210
    ld (WipeFar),hl         ; bottom starts at Y=210
    ld hl,0
    ld (LmDX),hl
    ld hl,512
    ld (LmNX),hl
    ld hl,2
    ld (LmNY),hl
    ld a,41                ; 41 pairs, last pair overlaps centre row
    ld (WipeRemaining),a
    ld a,1                 ; one frame per pair (~41 frames)
    ENDIF
    ld (WipePaceCounter),a
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h              ; V9938 LMMV/IMP black fill
    ld (LmCMD),a

.next_pair:
    ld hl,(WipeNear)
    IF WIPE_FROM_SIDES
    ld (LmDX),hl
    ELSE
    ld (LmDY),hl
    ENDIF
    call LmmmLaunch

    ld hl,(WipeFar)
    IF WIPE_FROM_SIDES
    ld (LmDX),hl
    ELSE
    ld (LmDY),hl
    ENDIF
    call LmmmLaunch
    call WipeWaitIdle      ; complete BOTH VDP commands before pacing

    ld hl,WipePaceCounter
    dec (hl)
    jr nz,.advance
    IF WIPE_FROM_SIDES
    ld (hl),2
    ELSE
    ld (hl),1
    ENDIF
    call WipeWaitFrame
.advance:
    ld a,(WipeRemaining)
    dec a
    ld (WipeRemaining),a
    jr z,.done

    ld hl,(WipeNear)
    inc hl
    inc hl
    ld (WipeNear),hl
    ld hl,(WipeFar)
    dec hl
    dec hl
    ld (WipeFar),hl
    jr .next_pair

.done:
    pop hl
    pop de
    pop bc
    pop af
    ret

; Poll V9938 status S#2 command-execution bit (CE=bit0).
; Restore original interrupt state before returning.
WipeWaitIdle:
    push af
    push de
    ld a,i
    jp po,.off
    ld a,1
    jr .saved
.off:
    xor a
.saved:
    ld (WipeSavedIFF),a
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
    ld a,(WipeSavedIFF)
    or a
    jr z,.wait
    ei
    jr .wait
.done:
    ld a,(WipeSavedIFF)
    or a
    jr z,.restore
    ei
.restore:
    pop de
    pop af
    ret

WipeWaitFrame:
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

WipeNear:        dw 0
WipeFar:         dw 0
WipeRemaining:   db 0
WipePaceCounter: db 0
WipeSavedIFF:    db 0
    INCLUDE 'v9938_lmmm.asm'
