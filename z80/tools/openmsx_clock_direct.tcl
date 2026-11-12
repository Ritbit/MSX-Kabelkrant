# Diagnostic: do not run CLOCKCHK.BAS between RAMdisk setup and LOOP.
# Instead KBLINIT invokes SET TIME directly then original LOOP.SYS.
set rtcmode EmuTime
set throttle off
set out [file normalize "z80/build/openmsx-clock-direct"]
file mkdir $out
proc sample {stamp} {
    global out
    screenshot -raw [file join $out "direct-$stamp.png"]
    set f [open [file join $out "machine-state.txt"] a]
    puts $f "emulated_seconds=$stamp pc=[reg PC] runtime=[machine_info time]"
    close $f
}
foreach stamp {120 165 210 255 300} {
    after time $stamp [list sample $stamp]
}
after time 305 {
    global out
    set f [open [file join $out "direct.done"] w]
    puts $f "KBL_CLOCK_DIRECT_DONE"
    close $f
    exit
}
