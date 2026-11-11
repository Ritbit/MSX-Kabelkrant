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
    type -release -freq 3 $string
}
proc send_text {string} {
    # MSX BASIC INPUT$ uses the BIOS keyboard buffer. Avoid dropped long
    # typed strings seen with slow matrix injection in headless CI.
    type_via_keybuf $string
}
# Open the existing MSX editor, load a known original TXT page, change it,
# save as a NEW 8.3 filename on a disposable disk, and resume the newspaper.
# Avoid the historical empty-buffer editor branch (LEN(R$(Y))=1).
after time 140 {send " "}
after time 200 {capture main}
after time 205 {send "2"}
after time 250 {capture textmenu}
after time 255 {send "4"}
after time 300 {capture loadprompt}
after time 305 {send_text "MENU01"}
after time 350 {send_text "\r"}
after time 400 {capture loaded}
after time 405 {send " "}
after time 450 {capture afterload}
after time 455 {send "2"}
after time 500 {capture editor}
after time 505 {send_text "Z80EDITORTEST"}
after time 550 {capture edited}
after time 555 {press_esc}
after time 600 {capture escape}
after time 605 {send "3"}
after time 650 {capture returnmenu}
after time 655 {send "3"}
after time 700 {capture save}
after time 705 {send_text "Z8REG26"}
after time 750 {send "\r"}
after time 800 {capture saved}
after time 805 {send " "}
after time 850 {capture aftersave}
after time 855 {send "1"}
after time 900 {capture mainagain}
after time 905 {send "1"}
after time 950 {capture confirmation}
after time 955 {send "j"}
after time 1040 {capture resumed}
after time 1120 {capture resumed2; set f [open [file join $out "editor.done"] w]; puts $f "KBL_EDITOR_TRACE_DONE"; close $f; exit}
