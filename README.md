# Kabelkrant

## Building a Digital Hospital Information System on an MSX2

This repository preserves the source code for a digital news and information bulletin system written for an **MSX2 home computer** in the early 90's.

The software was used on the internal television system of a local hospital. It displayed information pages such as announcements, menus, visiting hours, service notices and other local news. The version published here is from the **sixth edition** of the system; earlier versions existed before this release.

The system is mostly written in **MSX BASIC**, with a small supporting RAM disk binary written in Z80 assembly to speed up page loading. It was designed for real-world unattended use and ran in production for several years.

> This repository is intended as a historical and educational archive of the original BASIC project.

## Why this is interesting

Kabelkrant-MSX2 is a small example of a practical 1990s information system built with very limited hardware:

- MSX2 computer
- MSX BASIC
- V9938 video hardware
- 128 KB RAM class machine
- custom RAM disk for faster page access
- screen graphics and text rendering in SCREEN 7
- local TV distribution as output

Although modest by modern standards, it solved a real communication problem using consumer home-computer hardware.

## Repository layout

```text
.
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SOFTWARE-OVERVIEW.md
│   └── VERSION-HISTORY.md
├── src/              # Original BASIC/source files
├── assets/           # Screen images, font/page data, SC7 assets
└── archive/          # Older versions, if available
```

The exact layout may evolve while the archive is being cleaned up.

## Screenshots and video

Screenshots and video captures can be generated using an MSX emulator such as openMSX or WebMSX.

Suggested future media:

```text
docs/images/boot.png
docs/images/main-page.png
docs/images/editor.png
docs/images/page-rendering.png
docs/video/demo.mp4
```

## Documentation

Start here:

- [Software overview](docs/SOFTWARE-OVERVIEW.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Version history](docs/VERSION-HISTORY.md)

More technical documentation can be added later for file formats, RAM disk internals, rendering, memory usage and emulator setup.

## Status

This is a historical archive. The code is published for preservation, curiosity and retro-computing interest.

It may not run unmodified on every MSX2 emulator or hardware configuration without reconstructing the original disk layout.

## License

This project is released under the **GNU General Public License v3.0 or later**.

See [LICENSE](LICENSE).
