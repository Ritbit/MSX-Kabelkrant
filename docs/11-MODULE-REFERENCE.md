# Module Reference

| File | Role from source header | Numbered lines |
|------|-------------------------|----------------|
| `AUTOEXEC.BAS` | Autostart of kabelkrant | 15 |
| `HEADER.SYS` |  | 9 |
| `KBLINIT.SYS` | initializes the ram/vram areas of Kabelkrant and setups system | 45 |
| `KRANT.SYS` | Process system funtions | 243 |
| `LOOP.SYS` | Generates kabelkrant    1999:Changed line 3940 to EXT$=".txt" | 338 |
| `MAIN.SYS` | Process system funtions | 60 |
| `PAPER.SYS` | Make a paper for Kabelkrant V6.0 | 10 |
| `SYSTEM.SYS` | Change system setup. | 92 |
| `TEKST.SYS` | Tekst-editor. | 241 |
| `UTILS.SYS` | Utillities for Kabelkrant V6.2 | 110 |


## `AUTOEXEC.BAS`

Header metadata:

```json
{
  "name": "AUTOEXEC.BAS",
  "date": "06-06-1994",
  "function": "Autostart of kabelkrant",
  "part of": "Kabelkrant V6.2",
  "chains to": "KBLINIT.SYS",
  "options": "None"
}
```

Numbered BASIC lines: **15**

Notable operations:

- line 10: `' Name     : AUTOEXEC.BAS`
- line 150: `BLOAD "RAMDISK.BIN",R`

## `KBLINIT.SYS`

Header metadata:

```json
{
  "name": "KBLINIT.SYS",
  "date": "08-07-1994       1999:Changed line 230 to A: drive",
  "function": "initializes the ram/vram areas of Kabelkrant and setups system",
  "part of": "Kabelkrant V6.2",
  "chains to": "LOOP.SYS, which contains routines for showing the paper",
  "options": "None",
  "print": ""
}
```

Numbered BASIC lines: **45**

Notable operations:

- line 10: `' Name     : KBLINIT.SYS`
- line 100: `COLOR 0,0,0: ON ERROR GOTO 330: VDP(9)=VDP(9) OR 2:' Zet sprites uit`
- line 110: `SCREEN 0: WIDTH 80: KEY OFF: DEFINT A-Z: KEY 10,"run 4100"+CHR$(13)`
- line 115: `SCREEN 7: COLOR 15,0,0: COLOR=(0,1,1,3):CLS`
- line 120: `SETPAGE 0,1: CLS: BLOAD "intro.SC7",S: COLOR=(0,1,1,3): COLOR=RESTORE: SETPAGE 0,0`
- line 124: `COPY (0,0)-(512,212),1 TO (0,0),0`
- line 140: `'   COPY (X,0)-(X,212),1 TO (X,0),0`
- line 150: `'   COPY (257-X,0)-(257-X,212),1 TO (257-X,0),0`
- line 160: `'   COPY (255+X,0)-(255+X,212),1 TO (255+X,0),0`
- line 170: `'   COPY (512-X,0)-(512-X,212),1 TO (512-X,0),0`
- line 185: `COPY (0,0)-(512,44) TO (0,212)`
- line 190: `SETPAGE 0,1: CLS: BLOAD "KRANT4.SC7",S: SETPAGE 0,0: CLEAR 2000`
- line 200: `IF PEEK(&HF347)>3 THEN SCREEN 1: WIDTH 32: COLOR 15,0,0: PRINT "WARNING: reboot system with CTRLkey pressed to disconnect some  diskdrives, because else an     error may `
- line 210: `RESTORE 270: AD=&HF975: FOR I=0 TO 166: READ A$: POKE AD+I,VAL("&H"+A$): NEXT: DEFUSR=AD:DEFUSR2=AD+11: DEFUSR1=AD+25`
- line 220: `ON ERROR GOTO 250`
- line 230: `READ PR$: IF PR$<>"END" THEN COPY "A:"+PR$ TO "C:":GOTO 230`
- line 240: `RUN "LOOP.SYS"`
- line 250: `IF ERR=53 THEN RESUME NEXT ELSE ON ERROR GOTO 320`
- line 330: `SCREEN 1: COLOR 15,0,0: ON ERROR GOTO 0`

## `LOOP.SYS`

Header metadata:

```json
{
  "name": "LOOP.SYS",
  "date": "08-07-1994              1999:Changed line 3960 to A: Drive",
  "function": "Generates kabelkrant    1999:Changed line 3940 to EXT$=\".txt\"",
  "part of": "Kabelkrant V6.2",
  "chains to": "MAIN.SYS",
  "options": "Chains by pressing space-bar.",
  "note": "This version uses fast text rendering via assembly"
}
```

Numbered BASIC lines: **338**

Notable operations:

- line 10: `' Name     : LOOP.SYS`
- line 120: `ON ERROR GOTO 4050: ON INTERVAL=50 GOSUB 2900: INTERVAL OFF`
- line 1130: `COPY "XK.dat" TO XK: COPY "YK.DAT" TO YK: COPY "X.DAT" TO X`
- line 1240: `GET DATE DT$`
- line 1430: `OPEN "C:KRANT.PAG" AS #1 LEN=256`
- line 1440: `FIELD #1,128 AS D$,128 AS E$:GET #1,WK: CLOSE`
- line 1610: `COPY(109,44)-(118,51),1 TO (X,Y)`
- line 1690: `COPY "INTRO2.DAT" TO "C:INTRO2.DAT"`
- line 1700: `OPEN "C:INTRO2.DAT" FOR INPUT AS #1`
- line 1720: `LINE INPUT #1,A$`
- line 1780: `COPY (119,44)-(128,50),1 TO (20+X*0.14,(Y*0.13)-10),0,TPSET`
- line 1820: `KILL "C:INTRO2.DAT"`
- line 2060: `COPY(435,0)-(511,44),1 TO (435,0),0,TPSET: INTERVAL ON`
- line 2250: `INTERVAL OFF`
- line 2270: `INTERVAL ON`
- line 2310: `ON ERROR GOTO 2470`
- line 2320: `OPEN "C:"+N$(PG)+".TXT" FOR INPUT AS #1`
- line 2330: `ON ERROR GOTO 0`
- line 2340: `LINE INPUT #1,R$: PL=VAL(R$): GOSUB 3500: 'Zandloper en pictogram plaatsen`
- line 2350: `LINE INPUT #1,R$: A$=USR1(R$): X=-425: Y=30: LT=3: K=13: GOSUB 2500`
- line 2380: `LINE INPUT #1,A$: IF A$=" " OR A$=STRING$(10,8) THEN 2400`
- line 2480: `ON ERROR GOTO 0: RESUME`
- line 2530: `INTERVAL OFF: SETPAGE 0,1`
- line 2540: `LINE(0,164)-(512,212),0,BF:IF LT=1 THEN COPY(0,51)-(512,80) TO (0,164)`
- line 2550: `LINE(0,164)-(512,212),K,BF,AND: SETPAGE 0,0: INTERVAL ON`
- line 2640: `IF X<0 THEN COPY(X1,Y1)-(X2,Y2),1 TO (XX,190),1`
- line 2650: `IF X>=0 THEN COPY(X1,Y1)-(X2,Y2),1 TO (X+XX,Y),0,TPSET`
- line 2675: `IF LT=3 THEN INTERVAL OFF:SETPAGE 0,1:LINE(0,164)-(512,212),K,BF,AND:SETPAGE 0,0:INTERVAL ON`
- line 2680: `IF X<0 THEN X=ABS(X)-XX: COPY (0,190)-(XX-1,209),1 TO (X,Y),0,TPSET`
- line 2930: `GET TIME T$`

## `MAIN.SYS`

Header metadata:

```json
{
  "name": "MAIN.SYS",
  "date": "03-01-1994",
  "function": "Process system funtions",
  "part of": "Kabelkrant V6.2",
  "chains to": "UTILS.SYS/SYSTEM.SYS/KRANT.SYS/TEKST.SYS",
  "options": "Save text and papers, alter system setup, run utillities."
}
```

Numbered BASIC lines: **60**

Notable operations:

- line 10: `' Name     : MAIN.SYS`
- line 60: `' options  : Save text and papers, alter system setup, run utillities.`
- line 100: `MAXFILES=2: CLEAR 5000: DEFINT A-Z: KEY OFF`
- line 120: `ON ERROR GOTO 1000`
- line 330: `A$=INPUT$(1): A=VAL(A$): IF A=0 THEN 330`
- line 870: `LOCATE30,11:PRINT"Stoppen ? [j/N] ";:IN$=INPUT$(1)`
- line 890: `SCREEN 7:COLOR 15,0,0:SETPAGE 0,1: COLOR=RESTORE: COLOR=(0,1,1,3)`
- line 895: `SETPAGE 0,0:CLS:COPY (0,0)-(512,44) TO (0,212)`
- line 900: `RUN "LOOP.SYS"`

## `KRANT.SYS`

Header metadata:

```json
{
  "name": "KRANT.SYS",
  "date": "03-01-1994",
  "function": "Process system funtions",
  "part of": "Kabelkrant V6.2",
  "chains to": "MAIN.SYS",
  "options": "Save papers.",
  "cls": "IF WK=0 OR WK>7 THEN RETURN 170",
  "print": "SV=1"
}
```

Numbered BASIC lines: **243**

Notable operations:

- line 10: `' Name     : KRANT.SYS`
- line 120: `'ON ERROR GOTO 50120`
- line 140: `'WK=1:GOSUB 1840:GOSUB 1890' open KRANT.NPG`
- line 310: `A$=INPUT$(1): A=VAL(A$): IFA=0 THEN 310`
- line 370: `IF SV=0 THEN CLOSE: RUN "MAIN.SYS"`
- line 430: `IN$=INPUT$(1): IN$=USR(IN$): PRINTA$;`
- line 600: `GOSUB 1700: IF F=0 THEN PRINT"Geen pagina's aanwezig.": PRINT"Druk op een toets.": A$=INPUT$(1): RETURN 170`
- line 930: `GOSUB 1700: IF F=0 THEN PRINT"Geen pagina's aanwezig.": PRINT"Druk op een toets." : A$=INPUT$(1): SV=0: RETURN 170`
- line 1280: `PRINT"Zeker weten (J/N) :" :IN$=INPUT$(1): IN$=USR(IN$): IF IN$<>"J"THEN RETURN 170`
- line 1310: `ON ERROR GOTO 1430`
- line 1360: `OPEN N$(PG)+".txt" FOR INPUT AS#2`
- line 1370: `LINEINPUT #2,KP$:PRINT" Kop: "+KP$`
- line 1410: `PRINT"Druk een toets..": A$=INPUT$(1)`
- line 1420: `CLOSE: ON ERROR GOTO 2270: RETURN 170`
- line 1450: `ON ERROR GOTO 2270: RESUME`
- line 1480: `' Line input routine #1, see #2, but also given length`
- line 1530: `'Line input routine #2, performs BS and CR, no DEL accepted`
- line 1560: `A$=INPUT$(1): IF A$=CHR$(127) THEN A$=CHR$(8)`
- line 1660: `GET TIME TI$: GET DATE D$: A$=MID$("0000000"+BIN$(PEEK(&H002B)),6,2)`
- line 1870: `CLOSE: OPEN "KRANT.PAG" AS #1 LEN=256`
- line 1880: `FIELD #1,128 AS D$,128 AS E$`
- line 1890: `GET #1,WK`
- line 2210: `PUT 1,WK: SV=0`
- line 2260: `LOCATE,,0: PRINT: PRINT"Don't forget signals!!"+STRING$(5,7): LOCATE,,LO: CLOSE: END`

## `TEKST.SYS`

Header metadata:

```json
{
  "name": "TEKST.SYS",
  "date": "03-01-1994",
  "function": "Tekst-editor.",
  "part of": "KabelKrant V6.2",
  "chains to": "MAIN.SYS",
  "options": "Save text"
}
```

Numbered BASIC lines: **241**

Notable operations:

- line 10: `' Name     : TEKST.SYS`
- line 100: `MAXFILES=2: CLEAR 5000: DEFINT A-Z`
- line 130: `ON ERROR GOTO 6000`
- line 300: `A$=INPUT$(1): A=VAL(A$): IF A=0 THEN 300`
- line 400: `IF SV=0 THEN RUN "MAIN.SYS"`
- line 460: `IN$=INPUT$(1): IN$=USR(IN$): PRINTIN$;`
- line 670: `A$=INPUT$(1): IF A$<>CHR$(27) THEN SV=-1`
- line 1500: `LOCATE 30,23: PRINT"Uw keuze: ";: A$=INPUT$(1)`
- line 1780: `FILES"*.txt": PRINT: PRINT`
- line 1810: `ON ERROR GOTO 1890`
- line 1820: `OPEN IN$+".TXT" FOR OUTPUT AS#1`
- line 1840: `OPEN "c:"+IN$+".TXT" FOR OUTPUT AS#1`
- line 1860: `ON ERROR GOTO 2300`
- line 1880: `A$=INPUT$(1): RETURN 190`
- line 1900: `ON ERROR GOTO 2300`
- line 2000: `FILES"*.txt": PRINT: PRINT`
- line 2030: `ON ERROR GOTO 2090`
- line 2040: `OPEN IN$+".TXT" FOR INPUTAS#1`
- line 2060: `ON ERROR GOTO 2300`
- line 2080: `A$=INPUT$(1): T=1: RETURN 190`
- line 2110: `ON ERROR GOTO 2300`
- line 2150: `A$=INPUT$(1): IN$=USR(A$)`
- line 2290: `A$=INPUT$(1): IF A$=CHR$(127) THEN A$=CHR$(8)`

## `SYSTEM.SYS`

Header metadata:

```json
{
  "name": "SYSTEM.SYS",
  "date": "04-05-1994",
  "function": "Change system setup.",
  "part of": "Kabelkrant V6.2",
  "chains to": "MAIN.SYS",
  "options": "None",
  "cls": "PRINTID$"
}
```

Numbered BASIC lines: **92**

Notable operations:

- line 10: `' Name     : SYSTEM.SYS`
- line 100: `CLEAR 1000:DEFINTA-Z:MAXFILES=2`
- line 115: `ON ERROR GOTO 65000`
- line 1170: `A$=INPUT$(1): A=VAL(A$): IF A=0 THEN 1160`
- line 2300: `A$=INPUT$(1): IF USR(A$)="N" THEN 1000 ELSE IF USR(A$)="J" THEN ELSE 2300`
- line 2320: `ON ERROR GOTO 2340`
- line 2330: `SET TIME IN$:GOTO 1000`
- line 2350: `ON ERROR GOTO 0`
- line 2470: `GET DATE DA$`
- line 2500: `A$=INPUT$(1): IF USR(A$)="N" THEN 1000 ELSE IF USR(A$)="J" THEN ELSE 2500`
- line 2520: `ON ERROR GOTO 2540`
- line 2530: `SET DATE IN$: GOTO 1000`
- line 2550: `ON ERROR GOTO 0`
- line 20010: `' Input routine`
- line 21010: `'Line input routine, performs BS and CR, no DEL accepted`
- line 21040: `A$=INPUT$(1): IF A$=CHR$(127) THEN A$=CHR$(8)`
- line 21210: `' Get date and time in DA$ and TI$`
- line 21230: `GET TIME TI$: GET DATE D$: DF=(PEEK(&H002B) AND &H30)\16`

## `UTILS.SYS`

Header metadata:

```json
{
  "name": "UTILS.SYS",
  "date": "13-06-1994",
  "function": "Utillities for Kabelkrant V6.2",
  "part of": "Kabelkrant V6.2",
  "chains to": "MAIN.SYS",
  "options": "Run 'Storing' page",
  "cls": "PRINTID$",
  "print": "LOCATE 30: PRINT\"Druk op een toets.\": A$=INPUT$(1)"
}
```

Numbered BASIC lines: **110**

Notable operations:

- line 10: `' Name     : UTILS.SYS`
- line 60: `' Options  : Run 'Storing' page`
- line 100: `CLEAR 1000:DEFINTA-Z:MAXFILES=2`
- line 115: `ON ERROR GOTO 65000: ON STRIG GOSUB 2000: STRIG(0) OFF`
- line 1170: `A$=INPUT$(1): A=VAL(A$): IF A=0 THEN 1160`
- line 1660: `PRINT: ON ERROR GOTO 1720`
- line 1670: `FILES"*.TXT"`
- line 1700: `A$=INPUT$(1)`
- line 1705: `ON ERROR GOTO 65000`
- line 1740: `ON ERROR GOTO 65000`
- line 1860: `PRINT: ON ERROR GOTO 1920`
- line 1870: `FILES"*.TXT"`
- line 1901: `A$=USR(INPUT$(1)): IF A$<>"J" THEN PRINT"N": GOTO 1904`
- line 1903: `KILL IN$`
- line 1904: `PRINT: LOCATE 30: PRINT"Druk op een toets.": A$=INPUT$(1)`
- line 1905: `ON ERROR GOTO 65000`
- line 1940: `ON ERROR GOTO 65000`
- line 2000: `STRIG(0) OFF: SETPAGE 0,0: SCREEN 0: GOTO 1000`
- line 2630: `SCREEN 7: BLOAD"storing.sc7",S: COLOR=RESTORE: COLOR=(0,1,1,3):STRIG(0) ON`
- line 2730: `SCREEN 7: SETPAGE 1,1: COLOR=RESTORE`
- line 20010: `' Input routine`
- line 21010: `'Line input routine, performs BS and CR, no DEL accepted`
- line 21040: `A$=INPUT$(1): IF A$=CHR$(127) THEN A$=CHR$(8)`
- line 21210: `' Get date and time in DA$ and TI$`
- line 21230: `GET TIME TI$: GET DATE D$: A$=MID$("0000000"+BIN$(PEEK(&H002B)),6,2)`

## `PAPER.SYS`

Header metadata:

```json
{
  "name": "PAPER.SYS",
  "date": "31-06-1994",
  "function": "Make a paper for Kabelkrant V6.0",
  "part of": "Kabelkrant V6.2",
  "chains to": "MAIN.SYS",
  "options": "Save and load papers"
}
```

Numbered BASIC lines: **10**

Notable operations:

- line 10: `' Name     : PAPER.SYS`

## `HEADER.SYS`

Header metadata:

```json
{
  "name": "",
  "date": "",
  "function": "",
  "part of": "Kabelkrant V6.2",
  "chains to": "",
  "options": ""
}
```

Numbered BASIC lines: **9**

Notable operations:

- line 10: `' Name     :`
