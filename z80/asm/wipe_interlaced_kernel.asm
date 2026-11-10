; Wipes #11/#12, original BASIC 3340/3350: alternating interlaced strokes.
; Wipe #11: top down plus mirrored bottom up, 2 scanlines per stroke.
; Wipe #12: alternating even left/right odd X columns, 1 pixel per stroke.
; V9938 SCREEN 7: visible X 0..511, Y 50..211. No title-bar overwrites.
; Numeric WIPE_VERTICAL 1 for #11, 0 for #12. Isolated BLOAD/R.
    ORG 0C804h
    dw WipeInterlaced
JIFFY EQU 0FC9Eh

WipeInterlaced:
    push af
    push bc
    push de
    push hl
    IF WIPE_VERTICAL
    ld hl,50
    ld (StrokeNear),hl      ; first top-down band starts Y=50
    ld hl,207
    ld (StrokeFar),hl       ; mirrored BASIC 257-A starts at 207
    ld hl,0
    ld (LmDX),hl
    ld hl,512
    ld (LmNX),hl
    ld hl,2
    ld (LmNY),hl
    ld a,81
    ld (StrokeRemaining),a
    ld a,1                  ; frame per completed pair (81 frames)
    ELSE
    ld hl,0
    ld (StrokeNear),hl      ; even x=0,2,4,...510
    ld hl,511
    ld (StrokeFar),hl       ; odd x=511,509,507,...1
    ld hl,50
    ld (LmDY),hl
    ld hl,1
    ld (LmNX),hl
    ld hl,162
    ld (LmNY),hl
    ld a,0                  ; 256 iterations as 8-bit wrapping counter
    ld (StrokeRemaining),a
    ld a,4                  ; frame per four pairs (64 frames)
    ENDIF
    ld (StrokePace),a
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h
    ld (LmCMD),a

.next_pair:
    ld hl,(StrokeNear)
    IF WIPE_VERTICAL
    ld (LmDY),hl
    ELSE
    ld (LmDX),hl
    ENDIF
    call LmmmLaunch

    ld hl,(StrokeFar)
    IF WIPE_VERTICAL
    ; Mirrored bottom-up band may reach title-bar rows at end:
    ; BASIC starts 207,205,...47; explicitly clip rather than corrupt.
    ld a,h
    or a
    jr nz,.no_far
    ld a,l
    cp 50
    jr c,.no_far
    ld (LmDY),hl
    call LmmmLaunch
    jr .after_far
.no_far:
    ; No second stroke after y falls below 50.
    ELSE
    ld (LmDX),hl
    call LmmmLaunch
    ENDIF
.after_far:
    call WipeWaitIdle

    ld hl,StrokePace
    dec (hl)
    jr nz,.advance
    IF WIPE_VERTICAL
    ld (hl),1
    ELSE
    ld (hl),4
    ENDIF
    call WipeWaitFrame

.advance:
    ld a,(StrokeRemaining)
    dec a
    ld (StrokeRemaining),a
    jr z,.done

    ld hl,(StrokeNear)
    inc hl
    inc hl
    ld (StrokeNear),hl
    ld hl,(StrokeFar)
    dec hl
    dec hl
    ld (StrokeFar),hl
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


StrokeNear:      dw 0
StrokeFar:       dw 0
StrokeRemaining: db 0
StrokePace:      db 0
WipeSavedIFF:    db 0
    INCLUDE 'v9938_lmmm.asm'
