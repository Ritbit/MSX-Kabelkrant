10 ' Name     : AUTOEXEC.BAS
20 ' Date     : 06-06-1994
30 ' Function : Autostart of kabelkrant
40 ' Part of  : Kabelkrant V6.2
50 ' Chains to: KBLINIT.SYS
60 ' Options  : None
70 '
80 ' Kabelkrant (c) 1994 Bas van Ritbergen / RitBit
90 '
100 POKE &HFBB1,0: ' 0 = Zet Crtl-Stop aan; 1 = Zet Ctrl-Stop uit!!
110 COLOR 0,0,0: A$=CHR$(13)+"COLOR 0,0,0:Run"+CHR$(34)+"KBLINIT.SYS"+CHR$(34)+CHR$(13)
120 POKE &HF3FA,&H00F0: POKE &HF3FB,&H00FB : FOR I=1 TO LEN(A$)
130 POKE &HFBF0+I-1,ASC(MID$(A$,I,1)): NEXT: WR%=&HFBF0+LEN(A$)
140 POKE &HF3F8,WR% AND 255: POKE &HF3F9,((WR% AND &HFF00)/256) AND 255
150 BLOAD "RAMDISK.BIN",R
