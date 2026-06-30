# The System in Use

This document describes the Kabelkrant from the perspective of the people who used it: the patients and visitors who watched it, the operators who maintained it, and the ZZBO staff who broadcast it.

---

## What viewers saw

A patient in a hospital room in the Zaanstreek, sometime in the early 1990s, might have found a few channels on the bedside television. One of them was the ZZBO cable channel.

Most of the time — between programmes, or when no live content was scheduled — the channel showed the **Kabelkrant**: a quietly cycling sequence of information screens, visible to anyone with the TV on that channel.

The screen looked like this:

![Live page](images/Krant-live.png)

Each page occupied the full screen in a crisp graphical style. The layout was consistent across all pages:

- A **header banner** at the top carried the ZZBO identity and the current day of the week.
- A small **pictogram** in the top-left corner identified the page category at a glance — a fork and knife for meal times, an arrow for general notices, a house icon for ward information, a heart for care-related content.
- A **page title** in large, clear proportional text dominated the upper portion.
- Up to **ten lines of body text** appeared below in a smaller font — enough for a daily menu, a list of visiting hours per department, or a short announcement.
- An **analog clock** with moving hands sat in the top-right corner, giving the current time even when no programme was airing.
- A small **hourglass animation** in the bottom-left ticked down the seconds until the page changed.
- A **page counter** in the top area showed the viewer's position in the day's schedule — for example, `3/12`.

Every 15 to 30 seconds, a **wipe transition** swept the current page away and replaced it with the next. The transitions varied — horizontal sweeps, vertical rolls, dissolves — giving the system a polished broadcast feel.

There was no interaction. The viewer simply watched. Pages changed on their own, the clock moved, the hourglass filled and emptied. The system ran continuously, day after day, without anyone touching the keyboard.

---

## A typical broadcast day

The system displayed a different page schedule for each day of the week. The operator had pre-configured which pages would appear on Mondays, Tuesdays, and so on, and in what order.

A typical day's schedule might include:

1. A welcome/general information page
2. Visiting hours — general
3. Visiting hours — specific wards with different rules
4. Today's lunch menu
5. Today's dinner menu
6. Notice about an upcoming event
7. Pharmacy hours
8. General ward information
9. A departmental announcement
10. Contact and reception information
11. ZZBO programme schedule
12. Closing/general information page

The system would loop through this list continuously, cycling back to page 1 after page 12, and repeating throughout the day until the channel switched to live programming or was turned off for the evening.

At midnight, or when the day changed, the system automatically switched to the next day's schedule — the next 7-day block in `KRANT.PAG` — and refreshed the text files from the floppy disk. An operator who had set up next week's schedules in advance could leave the system running without touching it for days.

If a page had no content assigned, the system silently skipped it. If the schedule was exhausted, it looped from the beginning.

---

## The operator's workflow

The system was designed to be maintained by non-technical staff — an administrator or receptionist at the care facility, or a member of the ZZBO team.

The operator had physical access to the MSX2 computer. It sat in a technical room or broadcast area, connected by cable to the ZZBO distribution system and with a small monitor for maintenance work.

### Starting a session

To enter the operator menus, the operator pressed the **space bar** during the live display. The graphical broadcast display was replaced by a simple 80-column text menu:

![Main menu](images/Hoofd-menu.png)

From here the operator could update text, change the schedule, adjust the clock, or show the maintenance screen.

### Updating a page

![Text editor](images/Tekst-invoeren.png)

The editor shows the page type number at the top (which selects the icon), the title on line 2, and up to 10 body lines below. The operator types the new content directly, using the MSX keyboard.

1. Select **Teksten** (texts) from the main menu.
2. Choose **Laden** (load) and type the filename of the page to edit.
3. The text editor opens with the current content.
4. Choose **Bewaren** (save) to write the updated file back to the floppy disk.

### Changing the schedule

![Page schedule editor](images/Krant-samenstellen.png)

The schedule editor shows the 32 page slots for the current day. The operator assigns page files to slots by typing the file number from the list shown in the lower panel.

1. Select **Krant** (newspaper) from the main menu.
2. Choose **Samenstellen** (compose).
3. Save the day's schedule when done.

### Time and date

The **Systeem instellingen** menu allows the operator to set the clock and date using the MSX BASIC `SET TIME` and `SET DATE` commands. Summer/winter time adjustment is a single menu option.

![System settings](images/Systeem-Instellingen-Menu.png)

### Returning to broadcast

When editing is complete, the operator selects **Stoppen** from the main menu. The system switches back to SCREEN 7 graphics mode and resumes the live display loop from `LOOP.SYS`.

The updated content and schedule take effect immediately — or at the next startup, if files were changed on the floppy without restarting.

---

## The fault screen

If the system needed to be taken off-air for maintenance — a hardware problem, a content error, or a planned interruption — the operator could display a static maintenance screen from the utilities menu:

![Fault screen](images/Storing.png)

The `STORING.SC7` screen (storing = Dutch for fault/breakdown) replaced the live display with a polite message. This was the operator's way of telling viewers that the service was temporarily unavailable.

---

## The physical installation

The Kabelkrant MSX2 sat in the ZZBO broadcast infrastructure alongside other cable TV equipment. The connection was straightforward:

```text
Philips NMS-8250
      │
      │ RGB / composite video out
      ▼
RF modulator / cable headend
      │
      │ cable TV distribution
      ▼
Hospital room televisions
```

The MSX produced a composite or RGB video signal. A modulator converted this to an RF channel that could be distributed over the existing coaxial cable TV infrastructure already installed in the building. No special hardware was required between the computer and the distribution system.

A second connection led to a maintenance monitor — a small television or monitor in the technical room that allowed the operator to see the live display without having to enter a patient area.

The floppy disk drive on the NMS-8250 contained the software and all the page content. To update the system, the operator could either use the built-in text editor (while the system was running) or swap the floppy with a pre-prepared disk containing updated content.

---

## What made it work

For the viewers, the Kabelkrant was simply a useful channel to watch — a reliable source of the information they needed during a stay in a care facility.

For the operators, it was a low-maintenance system. Once the week's schedules were configured, the system ran itself. Updating a single page took a few minutes. The operator did not need to understand the software in any depth.

For ZZBO, it was a way to extend the value of the cable TV infrastructure they were already running. The same cable that carried television programmes could carry a live, updatable information service — at the cost of one home computer, one floppy disk, and a modest amount of operator time per week.

The engineering challenge — running a professional-looking broadcast-quality graphical display on a Z80 home computer in MSX BASIC — is what this repository documents.

---

## See also

- [00-HISTORY.md](00-HISTORY.md) — full historical background of ZZBO and the project
- [12-OPERATOR-GUIDE.md](12-OPERATOR-GUIDE.md) — operator menus reference with screenshots
- [SCREENSHOTS.md](SCREENSHOTS.md) — full screenshot gallery
- [RENDERING.md](RENDERING.md) — how the graphical display was actually produced
- [ARCHITECTURE.md](ARCHITECTURE.md) — system architecture and data flow
