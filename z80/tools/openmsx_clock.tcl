# Midnight rollover fixture: KBLINIT runs a disposable test-only BASIC
# program which SET TIME 23:59:50, waits for 00:00:xx, writes A:CLOCK.OK
# with GET TIME before/after and FRE(0), then runs original LOOP.SYS.
# Set emulated RTC time progression so throttle-off remains deterministic.
set rtcmode EmuTime
set throttle off
set out [file normalize "z80/build/openmsx-clock"]
file mkdir $out
proc clk_capture {stamp} {
    global out
    screenshot -raw [file join $out "clock-$stamp.png"]
}
foreach stamp {150 190 250 310} {
    after time $stamp [list clk_capture $stamp]
}
after time 315 {
    global out
    set f [open [file join $out "clock.done"] w]
    puts $f "KBL_CLOCK_EMULATED_315_SECONDS"
    close $f
    exit
}
