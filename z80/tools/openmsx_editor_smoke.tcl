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
# The initial 120 seconds cover the NMS8250 boot and intro.
after time 140 {send " "}
after time 149 {capture main}
after time 153 {send "2"}
after time 162 {capture textmenu}
after time 165 {send "2"}
after time 174 {capture editor}
after time 177 {send "Z80EDITORTEST"}
after time 185 {press_esc}
after time 191 {capture escape}
after time 194 {send "3"}
after time 201 {capture returnmenu}
after time 204 {send "3"}
after time 212 {capture save}
after time 215 {send "Z8REG26\r"}
after time 224 {capture saved}
after time 227 {send " "}
after time 235 {send "1"}
after time 245 {capture mainagain}
after time 250 {send "1"}
after time 257 {send "j"}
after time 310 {capture resumed}
after time 355 {capture resumed2; puts "KBL_EDITOR_TRACE_DONE"; set f [open [file join $out "editor.done"] w]; puts $f "KBL_EDITOR_TRACE_DONE"; close $f; exit}
