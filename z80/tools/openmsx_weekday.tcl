# Automated source-equivalent MSX BASIC Gregorian weekday regression.
# KBLINIT runs A:WDAY.BAS after staging C:; proof is written only on success.
set throttle off
set out [file normalize "z80/build/openmsx-weekday"]
file mkdir $out
proc wd_capture {stamp} {
    global out
    screenshot -raw [file join $out "weekday-$stamp.png"]
}
after time 120 {wd_capture 120}
after time 210 {wd_capture 210}
after time 225 {
    global out
    set f [open [file join $out "weekday.done"] w]
    puts $f "KBL_WEEKDAY_EMULATED_225_SECONDS"
    close $f
    exit
}
