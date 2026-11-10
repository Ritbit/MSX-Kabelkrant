; Optional WIPE 9..12 engine. Shares LmmmLaunch/WaitIdle/WaitFrame
; and memory-only VDP parameters with the resident TEXT renderer.
; Not included by the 1..8 integration alpha.
WipeExtraRun:
    cp 11
    jp nc,WipeExtraInterlace
    jp WipeExtraBoxes

; WIPE 9: outer to inner boxes; WIPE 10: reverse.
; Two-byte geometry table replaces 12-byte standalone records.
WipeExtraBoxes:
    push af
    push bc
    push de
    push hl
    ld (ExtraMode),a
    ld hl,WipeCompactBoxTable
    cp 10
    jr nz,.forward
    ld de,254
    add hl,de
.forward:
    ld (ExtraPtr),hl
    ld a,128
    ld (ExtraRemain),a
    ld a,2
    ld (ExtraPace),a
    call ExtraInitBlack

.next:
    ld hl,(ExtraPtr)
    ld a,(hl)
    ld (ExtraX),a
    inc hl
    ld a,(hl)
    ld (ExtraY),a

    ; Box X left/right, width, all clipped to visible 0..511.
    ld a,(ExtraX)
    ld l,a
    ld h,0
    ld (ExtraLeft),hl
    ld e,a
    ld d,0
    ld hl,510
    or a
    sbc hl,de
    ld (ExtraRight),hl
    sla e
    rl d
    ld hl,512
    or a
    sbc hl,de
    ld (ExtraWidth),hl

    ; Box top/bottom/height from 8-bit y.
    ld a,(ExtraY)
    ld e,a
    ld d,0
    ld hl,50
    add hl,de
    ld (ExtraTop),hl
    ld hl,210
    or a
    sbc hl,de
    ld (ExtraBottom),hl
    sla e
    rl d
    ld hl,162
    or a
    sbc hl,de
    ld (ExtraHeight),hl

    call ExtraDrawBox
    ld hl,ExtraPace
    dec (hl)
    jr nz,.advance
    ld (hl),2
    call WipeSharedFrame
.advance:
    ld hl,ExtraRemain
    dec (hl)
    jr z,.done
    ld hl,(ExtraPtr)
    ld de,2
    ld a,(ExtraMode)
    cp 10
    jr z,.backward
    add hl,de
    jr .set
.backward:
    or a
    sbc hl,de
.set:
    ld (ExtraPtr),hl
    jp .next
.done:
    pop hl
    pop de
    pop bc
    pop af
    ret

; Four 2px contour bands, shares one LMMV parameter block.
ExtraDrawBox:
    ld hl,(ExtraLeft)
    ld (LmDX),hl
    ld hl,(ExtraTop)
    ld (LmDY),hl
    ld hl,(ExtraWidth)
    ld (LmNX),hl
    ld hl,2
    ld (LmNY),hl
    call LmmmLaunch
    ld hl,(ExtraBottom)
    ld (LmDY),hl
    call LmmmLaunch
    ld hl,(ExtraTop)
    ld (LmDY),hl
    ld hl,(ExtraHeight)
    ld (LmNY),hl
    ld hl,2
    ld (LmNX),hl
    call LmmmLaunch
    ld hl,(ExtraRight)
    ld (LmDX),hl
    call LmmmLaunch
    jp WipeSharedIdle

; WIPE 11: alternating top+bottom scanline bands.
; WIPE 12: even left columns plus mirrored odd right columns.
WipeExtraInterlace:
    push af
    push bc
    push de
    push hl
    ld (ExtraMode),a
    cp 11
    jr z,.vertical
    ld hl,0
    ld (WipeNear),hl
    ld hl,511
    ld (WipeFar),hl
    ld hl,50
    ld (LmDY),hl
    ld hl,1
    ld (LmNX),hl
    ld hl,162
    ld (LmNY),hl
    xor a                       ; 256 iterations by wrapping counter
    ld (ExtraRemain),a
    ld a,4
    jr .pacing
.vertical:
    ld hl,50
    ld (WipeNear),hl
    ld hl,207
    ld (WipeFar),hl
    ld hl,0
    ld (LmDX),hl
    ld hl,512
    ld (LmNX),hl
    ld hl,2
    ld (LmNY),hl
    ld a,81
    ld (ExtraRemain),a
    ld a,1
.pacing:
    ld (ExtraPace),a
    call ExtraInitBlack
.loop:
    ld hl,(WipeNear)
    call ExtraSetAxis
    call LmmmLaunch
    ld hl,(WipeFar)
    ld a,(ExtraMode)
    cp 11
    jr nz,.draw_far
    ld a,h
    or a
    jr nz,.skip_far
    ld a,l
    cp 50
    jr c,.skip_far
.draw_far:
    call ExtraSetAxis
    call LmmmLaunch
.skip_far:
    call WipeSharedIdle
    ld hl,ExtraPace
    dec (hl)
    jr nz,.continue
    ld a,(ExtraMode)
    cp 11
    ld (hl),1
    jr z,.wait
    ld (hl),4
.wait:
    call WipeSharedFrame
.continue:
    ld hl,ExtraRemain
    dec (hl)
    jr z,.finish
    ld hl,(WipeNear)
    inc hl
    inc hl
    ld (WipeNear),hl
    ld hl,(WipeFar)
    dec hl
    dec hl
    ld (WipeFar),hl
    jp .loop
.finish:
    pop hl
    pop de
    pop bc
    pop af
    ret

ExtraSetAxis:
    push af
    ld a,(ExtraMode)
    cp 11
    jr nz,.x
    ld (LmDY),hl
    pop af
    ret
.x:
    ld (LmDX),hl
    pop af
    ret

ExtraInitBlack:
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h
    ld (LmCMD),a
    ret

ExtraMode: db 0
ExtraPtr: dw 0
ExtraX: db 0
ExtraY: db 0
ExtraRemain: db 0
ExtraPace: db 0
ExtraLeft: dw 0
ExtraRight: dw 0
ExtraTop: dw 0
ExtraBottom: dw 0
ExtraWidth: dw 0
ExtraHeight: dw 0
    INCLUDE 'wipe_compact_table.asm'
