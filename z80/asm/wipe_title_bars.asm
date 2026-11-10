; Fixed-geometry title wipe: copy an untouched left-hand template.
; The original BASIC used COPY(0,0)-(10,48) TO (A,0), A=0..420 STEP10.
; A black LMMV fill is WRONG here: it destroys green/grey backgrounds
; and leaves part of the right-aligned titles untouched.
;
; This variant uses the V9938 LMMM IMP VRAM->VRAM operation:
;   source X=0..9, Y=0..48 on page 0 (clean background/template);
;   destination X=0..434 in 10-pixel bands, last band 5 pixels.
; Title borders and original palette colours are copied from source.
; The clock at X=435..511 is never written. Preserve the screenshot's
; original bands (including 8,23,29,44), not just their interiors.
; Only the opt-in CALL WIPE(15) image includes this routine.
WipeTitleBars:
    push af
    push bc
    push de
    push hl

    ld hl,0
    ld (LmSX),hl
    ld (LmSY),hl
    ld (LmDX),hl
    ld (LmDY),hl
    ld (TitleX),hl
    ld hl,10
    ld (LmNX),hl
    ld hl,49
    ld (LmNY),hl
    xor a
    ld (LmARG),a         ; left-to-right, top-to-bottom
    ld a,090h
    ld (LmCMD),a         ; LMMM IMP (opaque VRAM->VRAM copy)
    ld b,44              ; 43 x 10px + final 5px = X0..434
.loop:
    ld a,b
    cp 1
    jr nz,.full
    ld hl,5
    ld (LmNX),hl         ; protect clock X435 onwards
.full:
    ld hl,(TitleX)
    ld (LmDX),hl
    push bc
    call LmmmLaunch
    call WipeSharedIdle
    pop bc
    ld hl,(TitleX)
    ld de,10
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
