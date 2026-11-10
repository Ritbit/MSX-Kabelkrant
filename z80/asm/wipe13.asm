; Wipe #13: four interlaced vertical lines (BASIC line 3360).
; Each BASIC iteration A=0..256 STEP 2 produces four single-pixel lines
; at x=A,512-A,257+A,257-A. Outside x=0..511 is skipped.
; V9938 SCREEN 7 y=50..211, avoiding title-bar and y=212.
    ORG 0C804h
    dw WipeFourColumns
JIFFY EQU 0FC9Eh

WipeFourColumns:
    push af
    push bc
    push de
    push hl
    ld hl,ColumnTable
    ld (ColumnPtr),hl
    ld a,129
    ld (ColumnIterations),a
    ld a,2
    ld (ColumnPace),a
    ld hl,50
    ld (LmDY),hl
    ld hl,1
    ld (LmNX),hl
    ld hl,162
    ld (LmNY),hl
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h
    ld (LmCMD),a

.next_step:
    ld hl,(ColumnPtr)
    ld de,8
    add hl,de
    ld (ColumnPtr),hl        ; next row's address
    or a
    sbc hl,de
    ld b,4
.next_column:
    push bc
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    push hl
    ld a,d
    cp 0FFh
    jr z,.skip
    ld (LmDX),de
    call LmmmLaunch
.skip:
    pop hl
    pop bc
    djnz .next_column
    call WipeWaitIdle
    ld hl,ColumnPace
    dec (hl)
    jr nz,.advance
    ld (hl),2
    call WipeWaitFrame
.advance:
    ld a,(ColumnIterations)
    dec a
    ld (ColumnIterations),a
    jr nz,.next_step
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



ColumnPtr:        dw 0
ColumnIterations: db 0
ColumnPace:       db 0
WipeSavedIFF:     db 0
    INCLUDE 'v9938_lmmm.asm'
    INCLUDE 'wipe13_columns.asm'
