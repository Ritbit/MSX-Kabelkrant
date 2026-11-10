; Experimental compact resident implementations of wipes 13 and 14.
; These share the TEXT renderer's VDP command block and idle/frame wait.
; Explicitly enabled only by WIPE_FULL EQU 1. No standalone tables.

WipeIntegrated13:
    push af
    push bc
    push de
    push hl
    ld hl,0
    ld (ExtraCounter),hl
    ld hl,50
    ld (LmDY),hl
    ld hl,1
    ld (LmNX),hl
    ld hl,162
    ld (LmNY),hl
    ld a,129
    ld (ExtraRemain),a
    ld a,2
    ld (ExtraPace),a
    call ExtraInitBlack
.loop:
    ld de,(ExtraCounter)
    ex de,hl
    call ExtraDrawColumn
    ld de,(ExtraCounter)
    ld hl,512
    or a
    sbc hl,de
    call ExtraDrawColumn
    ld de,(ExtraCounter)
    ld hl,257
    add hl,de
    call ExtraDrawColumn
    ld de,(ExtraCounter)
    ld hl,257
    or a
    sbc hl,de
    call ExtraDrawColumn
    call WipeSharedIdle
    ld hl,ExtraPace
    dec (hl)
    jr nz,.advance
    ld (hl),2
    call WipeSharedFrame
.advance:
    ld hl,ExtraRemain
    dec (hl)
    jr z,.done
    ld hl,(ExtraCounter)
    inc hl
    inc hl
    ld (ExtraCounter),hl
    jp .loop
.done:
    pop hl
    pop de
    pop bc
    pop af
    ret

ExtraDrawColumn:
    ld a,h
    cp 2                  ; x >= 512 is outside SCREEN7
    ret nc
    ld (LmDX),hl
    jp LmmmLaunch

; Four 1px box outlines for y=0,2,...76. Inner pair shares centre
; y=131 with the outer pair (fixes the original BASIC offset).
WipeIntegrated14:
    push af
    push bc
    push de
    push hl
    xor a
    ld (ExtraY),a
    ld a,39
    ld (ExtraRemain),a
    ld a,1
    ld (ExtraStroke),a
    call ExtraInitBlack

.loop:
    ld a,(ExtraY)
    add a,a
    ld (ExtraX),a
    ld l,a
    ld h,0
    ld (ExtraLeft),hl
    ld e,a
    ld d,0
    ld hl,512
    or a
    sbc hl,de
    ld a,h
    cp 2
    jr nz,.right_ok
    dec hl                 ; clip original x=512 to visible x=511
.right_ok:
    ld (ExtraRight),hl
    ld a,(ExtraY)
    ld e,a
    ld d,0
    ld hl,50
    add hl,de
    ld (ExtraTop),hl
    ld hl,212
    or a
    sbc hl,de
    ld a,h
    or a
    jr nz,.bottom_ok
    ld a,l
    cp 212
    jr nz,.bottom_ok
    dec hl                 ; clip y=212 to last visible y=211
.bottom_ok:
    ld (ExtraBottom),hl
    call ExtraDrawRect
    ld hl,(ExtraLeft)
    inc hl
    ld (ExtraLeft),hl
    ld hl,(ExtraRight)
    dec hl
    ld (ExtraRight),hl
    call ExtraDrawRect

    ld a,(ExtraX)
    ld e,a
    ld d,0
    ld hl,182
    or a
    sbc hl,de
    ld (ExtraLeft),hl
    ld hl,330
    add hl,de
    ld (ExtraRight),hl
    ld a,(ExtraY)
    ld e,a
    ld d,0
    ld hl,131
    or a
    sbc hl,de
    ld (ExtraTop),hl
    ld hl,131
    add hl,de
    ld (ExtraBottom),hl
    call ExtraDrawRect
    ld hl,(ExtraLeft)
    inc hl
    ld (ExtraLeft),hl
    ld hl,(ExtraRight)
    dec hl
    ld (ExtraRight),hl
    call ExtraDrawRect
    call WipeSharedFrame

    ld hl,ExtraRemain
    dec (hl)
    jr z,.final
    ld a,(ExtraY)
    add a,2
    ld (ExtraY),a
    jp .loop

.final:
    ; Contour tracks cannot cover all pixels: enforce black terminal
    ; state over newspaper only, no title-bar modifications.
    ld hl,0
    ld (LmDX),hl
    ld hl,50
    ld (LmDY),hl
    ld hl,512
    ld (LmNX),hl
    ld hl,162
    ld (LmNY),hl
    call ExtraInitBlack
    call LmmmLaunch
    call WipeSharedIdle
    pop hl
    pop de
    pop bc
    pop af
    ret

; Convert inclusive bounds to width/height before shared box drawer.
ExtraDrawRect:
    ld hl,(ExtraRight)
    ld de,(ExtraLeft)
    or a
    sbc hl,de
    inc hl
    ld (ExtraWidth),hl
    ld hl,(ExtraBottom)
    ld de,(ExtraTop)
    or a
    sbc hl,de
    inc hl
    ld (ExtraHeight),hl
    jp ExtraDrawBox

ExtraCounter: dw 0
