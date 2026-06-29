# File Formats

## Page text files

File structure:

```text
type-number for the page-icon
title
body line 1
body line 2
...
body line 10
```

Example `BEZOEKTD.TXT`:

```text
1
Bezoektijden
Voor de meeste afdelingen gelden de
volgende bezoektijden: 's middags van
13:30 tot 14:00 uur en 's avonds van
18:00 tot 19:30 uur.

Voor een aantal afdelingen gelden af-
wijkende bezoektijden. Vraag op deze
afdelingen het verplegend personeel
naar de exacte bezoektijden.
```

## `KRANT.PAG`

This file contains which pages should be show in order: 
It contains the file names of the page-files to be shown and is devided in 7 blocks of max 32 pages. (one block per day of the week). 
Thje filenames are stored as 8 bytes and no newline or linefeer, the next file started directly after the 8 bytes.
When all the pages were listed the block was filled with sets of 8 dashes `-` to complete the block.

So the first block (for monday) could look like this:
```
     1	ZZBO1
     2	ZZBO2
     3	TOTAAL
     4	TOTAAL41
     5	ENQUETE
     6	TOTAAL42
     7	OPROEPSY
     8	TOTAAL43
     9	PATSERV
    10	TOTAAL44
    11	POST
    12	TOTAAL45
    13	TELEFOON
    14	BEZOEKTD
    15	TOTAAL46
    16	OECUDIEN
    17	TOTAAL47
    18	GEESZORG
    19	KERK
    20	WANDELEN
    21	MENU01
    22	SYS
    23	--------
    24	--------
    25	--------
    26	--------
    27	--------
    28	--------
    29	--------
    30	--------
    31	--------
    32	--------
```
And then next block immediatly followning this one.

The total `KRAN.PAG` file could look like this:
```
00000000: 5a5a 424f 3120 2020 5a5a 424f 3220 2020  ZZBO1   ZZBO2
00000010: 544f 5441 414c 2020 544f 5441 414c 3431  TOTAAL  TOTAAL41
00000020: 454e 5155 4554 4520 544f 5441 414c 3432  ENQUETE TOTAAL42
00000030: 4f50 524f 4550 5359 544f 5441 414c 3433  OPROEPSYTOTAAL43
00000040: 5041 5453 4552 5620 544f 5441 414c 3434  PATSERV TOTAAL44
00000050: 504f 5354 2020 2020 544f 5441 414c 3435  POST    TOTAAL45
00000060: 5445 4c45 464f 4f4e 4245 5a4f 454b 5444  TELEFOONBEZOEKTD
00000070: 544f 5441 414c 3436 4f45 4355 4449 454e  TOTAAL46OECUDIEN
00000080: 544f 5441 414c 3437 4745 4553 5a4f 5247  TOTAAL47GEESZORG
00000090: 4b45 524b 2020 2020 5741 4e44 454c 454e  KERK    WANDELEN
000000a0: 4d45 4e55 3031 2020 5359 5320 2020 2020  MENU01  SYS
000000b0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000000c0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000000d0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000000e0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000000f0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000100: 5a5a 424f 3120 2020 5a5a 424f 3220 2020  ZZBO1   ZZBO2
00000110: 544f 5441 414c 2020 544f 5441 414c 3431  TOTAAL  TOTAAL41
00000120: 454e 5155 4554 4520 544f 5441 414c 3432  ENQUETE TOTAAL42
00000130: 4f50 524f 4550 5359 544f 5441 414c 3433  OPROEPSYTOTAAL43
00000140: 5041 5453 4552 5620 544f 5441 414c 3434  PATSERV TOTAAL44
00000150: 504f 5354 2020 2020 544f 5441 414c 3435  POST    TOTAAL45
00000160: 5445 4c45 464f 4f4e 4245 5a4f 454b 5444  TELEFOONBEZOEKTD
00000170: 544f 5441 414c 3436 4f45 4355 4449 454e  TOTAAL46OECUDIEN
00000180: 544f 5441 414c 3437 4745 4553 5a4f 5247  TOTAAL47GEESZORG
00000190: 4b45 524b 2020 2020 5741 4e44 454c 454e  KERK    WANDELEN
000001a0: 4d45 4e55 3032 2020 5359 5320 2020 2020  MENU02  SYS
000001b0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000001c0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000001d0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000001e0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000001f0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000200: 5a5a 424f 3120 2020 5a5a 424f 3220 2020  ZZBO1   ZZBO2
00000210: 544f 5441 414c 2020 544f 5441 414c 3431  TOTAAL  TOTAAL41
00000220: 454e 5155 4554 4520 544f 5441 414c 3432  ENQUETE TOTAAL42
00000230: 4f50 524f 4550 5359 544f 5441 414c 3433  OPROEPSYTOTAAL43
00000240: 5041 5453 4552 5620 544f 5441 414c 3434  PATSERV TOTAAL44
00000250: 504f 5354 2020 2020 544f 5441 414c 3435  POST    TOTAAL45
00000260: 5445 4c45 464f 4f4e 4245 5a4f 454b 5444  TELEFOONBEZOEKTD
00000270: 544f 5441 414c 3436 4f45 4355 4449 454e  TOTAAL46OECUDIEN
00000280: 544f 5441 414c 3437 4745 4553 5a4f 5247  TOTAAL47GEESZORG
00000290: 4b45 524b 2020 2020 5741 4e44 454c 454e  KERK    WANDELEN
000002a0: 4d45 4e55 3033 2020 5359 5320 2020 2020  MENU03  SYS
000002b0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000002c0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000002d0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000002e0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000002f0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000300: 5a5a 424f 3120 2020 5a5a 424f 3220 2020  ZZBO1   ZZBO2
00000310: 544f 5441 414c 2020 544f 5441 414c 3431  TOTAAL  TOTAAL41
00000320: 454e 5155 4554 4520 544f 5441 414c 3432  ENQUETE TOTAAL42
00000330: 4f50 524f 4550 5359 544f 5441 414c 3433  OPROEPSYTOTAAL43
00000340: 5041 5453 4552 5620 544f 5441 414c 3434  PATSERV TOTAAL44
00000350: 504f 5354 2020 2020 544f 5441 414c 3435  POST    TOTAAL45
00000360: 5445 4c45 464f 4f4e 4245 5a4f 454b 5444  TELEFOONBEZOEKTD
00000370: 544f 5441 414c 3436 4f45 4355 4449 454e  TOTAAL46OECUDIEN
00000380: 544f 5441 414c 3437 4745 4553 5a4f 5247  TOTAAL47GEESZORG
00000390: 4b45 524b 2020 2020 5741 4e44 454c 454e  KERK    WANDELEN
000003a0: 4d45 4e55 3034 2020 5359 5320 2020 2020  MENU04  SYS
000003b0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000003c0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000003d0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000003e0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000003f0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000400: 5a5a 424f 3120 2020 5a5a 424f 3220 2020  ZZBO1   ZZBO2
00000410: 544f 5441 414c 2020 544f 5441 414c 3431  TOTAAL  TOTAAL41
00000420: 454e 5155 4554 4520 544f 5441 414c 3432  ENQUETE TOTAAL42
00000430: 4f50 524f 4550 5359 544f 5441 414c 3433  OPROEPSYTOTAAL43
00000440: 5041 5453 4552 5620 544f 5441 414c 3434  PATSERV TOTAAL44
00000450: 504f 5354 2020 2020 544f 5441 414c 3435  POST    TOTAAL45
00000460: 5445 4c45 464f 4f4e 4245 5a4f 454b 5444  TELEFOONBEZOEKTD
00000470: 544f 5441 414c 3436 4f45 4355 4449 454e  TOTAAL46OECUDIEN
00000480: 544f 5441 414c 3437 4745 4553 5a4f 5247  TOTAAL47GEESZORG
00000490: 4b45 524b 2020 2020 5741 4e44 454c 454e  KERK    WANDELEN
000004a0: 4d45 4e55 3035 2020 5359 5320 2020 2020  MENU05  SYS
000004b0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000004c0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000004d0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000004e0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000004f0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000500: 5a5a 424f 3120 2020 5a5a 424f 3220 2020  ZZBO1   ZZBO2
00000510: 544f 5441 414c 2020 544f 5441 414c 3431  TOTAAL  TOTAAL41
00000520: 454e 5155 4554 4520 544f 5441 414c 3432  ENQUETE TOTAAL42
00000530: 4f50 524f 4550 5359 544f 5441 414c 3433  OPROEPSYTOTAAL43
00000540: 5041 5453 4552 5620 544f 5441 414c 3434  PATSERV TOTAAL44
00000550: 504f 5354 2020 2020 544f 5441 414c 3435  POST    TOTAAL45
00000560: 5445 4c45 464f 4f4e 4245 5a4f 454b 5444  TELEFOONBEZOEKTD
00000570: 544f 5441 414c 3436 4f45 4355 4449 454e  TOTAAL46OECUDIEN
00000580: 544f 5441 414c 3437 4745 4553 5a4f 5247  TOTAAL47GEESZORG
00000590: 4b45 524b 2020 2020 5741 4e44 454c 454e  KERK    WANDELEN
000005a0: 4d45 4e55 3036 2020 5359 5320 2020 2020  MENU06  SYS
000005b0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000005c0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000005d0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000005e0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000005f0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000600: 5a5a 424f 3120 2020 5a5a 424f 3220 2020  ZZBO1   ZZBO2
00000610: 544f 5441 414c 2020 544f 5441 414c 3431  TOTAAL  TOTAAL41
00000620: 454e 5155 4554 4520 544f 5441 414c 3432  ENQUETE TOTAAL42
00000630: 4f50 524f 4550 5359 544f 5441 414c 3433  OPROEPSYTOTAAL43
00000640: 5041 5453 4552 5620 544f 5441 414c 3434  PATSERV TOTAAL44
00000650: 504f 5354 2020 2020 544f 5441 414c 3435  POST    TOTAAL45
00000660: 5445 4c45 464f 4f4e 4245 5a4f 454b 5444  TELEFOONBEZOEKTD
00000670: 544f 5441 414c 3436 4f45 4355 4449 454e  TOTAAL46OECUDIEN
00000680: 544f 5441 414c 3437 4745 4553 5a4f 5247  TOTAAL47GEESZORG
00000690: 4b45 524b 2020 2020 5741 4e44 454c 454e  KERK    WANDELEN
000006a0: 4d45 4e55 3037 2020 5359 5320 2020 2020  MENU07  SYS
000006b0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000006c0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000006d0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000006e0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000006f0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000700: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000710: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000720: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000730: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000740: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000750: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000760: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000770: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000780: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
00000790: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000007a0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000007b0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000007c0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000007d0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000007e0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
000007f0: 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d 2d2d  ----------------
```


## `.SC7` files

`INTRO.SC7` and `KRANT3.SC7` are SCREEN 7 VRAM dumps. They are loaded by the program as graphics assets.
The INTRO.SC7 contains all elements to render the pages:
![KRANT3.png](imgages/KRANT3.png "KRANT3.SC7")

## Metric files

`X.DAT`, `XK.DAT`, and `YK.DAT` are used as coordinate/metric data for text rendering and clock drawing.

## Binary support files

This is the RamDisk as used store the text pages and to speed upo loading and save the life-time of the floppydrive.
This is 'Ramdisk v2.16, by P. te Bokkel, Modified 24/9/89 by M.J. Vriend'
The `RAMDISK.BIN` is loaded as usual with `BLOAD ...,R` by thhe `AUTOEXEC.BAS` and installs drive `C:`.
