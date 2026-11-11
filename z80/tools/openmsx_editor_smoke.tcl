# Disposable end-to-end operator UI smoke, Philips NMS 8250 / KBLTITLECOPY.DSK.
# Input is normal matrix keyboard input; do not patch BASIC or RAM directly.
# Screenshots are diagnostics. Success requires an A: file proof AND resumed pages.
set throttle off
set out [file normalize "z80/build/openmsx-editor"]
file mkdir $out
proc capture {name} {
    global out
    set path [file join $out "${name}.png"]
    screenshot -raw $path
    set file [open [file join $out "${name}.done"] w]
    puts $file $name
    close $file
}
proc press_esc {} {
    # MSX invariant keyboard matrix: ESC row 7, bit 2.
    keymatrixdown 7 0x04
    after time 0.20 {keymatrixup 7 0x04}
}
proc send {string} {
    type -release -freq 12 $string
}
# Generous simulated-time spacing prevents keypresses crossing menu transitions.
# NMS8250 takes >120 emulated seconds for its graphical cold start.
after time 140 {send " "}
after time 200 {capture main}
after time 205 {send "2"}
after time 250 {capture textmenu}
after time 255 {send "2"}
after time 300 {capture editor}
after time 305 {send "Z80EDITORTEST"}
after time 350 {capture edited}
after time 355 {press_esc}
after time 400 {capture escape}
after time 405 {send "3"}
after time 450 {capture returnmenu}
after time 455 {send "3"}
after time 500 {capture save}
after time 505 {send "Z8REG26\\r"}
after time 560 {capture saved}
after time 565 {send " "}
after time 610 {capture aftersave}
after time 615 {send "1"}
after time 660 {capture mainagain}
after time 665 {send "1"}
after time 710 {capture confirmation}
after time 715 {send "j"}
after time 790 {capture resumed}
after time 835 {capture resumed2; set f [open [file join $out "editor.done"] w]; puts $f "KBL_EDITOR_TRACE_DONE"; close $f; exit}
