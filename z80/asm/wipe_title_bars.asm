; Special fixed-size title-bar wipe, no rectangular parameter parser.
; Calls WIPE(15) to erase ONLY title bar interiors, x0..511:
;  top y9..22  (14 rows), bottom y30..43 (14 rows).
; Borders at 8,23,29,44 and the clock graphics remain untouched.
; Two V9938 LMMV commands per 8px column; frame every two columns.
; No VDP changes until CALL WIPE(15), and always wait for VDP idle.
WipeTitleBars:
    push af
    push bc
    push de
    push hl
    ld hl,0
    ld (TitleX),hl
    ld b,64
    ld hl,8
    ld (LmNX),hl
    ld hl,14
    ld (LmNY),hl
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h
    ld (LmCMD),a
.loop:
    ld hl,(TitleX)
    ld (LmDX),hl
    ld hl,9
    ld (LmDY),hl
    push bc
    call LmmmLaunch
    ld hl,30
    ld (LmDY),hl
    call LmmmLaunch
    call WipeSharedIdle
    pop bc
    ld hl,(TitleX)
    ld de,8
    add hl,de
    ld (TitleX),hl
    ld a,b
    and 1
    jr nz,.next
    push bc
    call WipeSharedFrame
    pop bc
.next:
    djnz .loop
    pop hl
    pop de
    pop bc
    pop af
    ret
TitleX: dw 0
