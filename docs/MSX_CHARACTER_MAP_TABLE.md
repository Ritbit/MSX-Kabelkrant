# MSX Standard Character Font & Screen Control Codes

The default European MSX character map uses a derivation of the standard ASCII table, modified to include specific international language characters and specialized mathematical graphical blocks.

## ⌨️ Screen Layout Control Strings
When using the MSX BASIC `PRINT` command or passing characters through the MSX-DOS string router (`call 0005h`, function `02h`/`09h`), sending these specific hex bytes will trigger immediate structural terminal display changes instead of printing text:

| Hex Byte | Dec Byte | Control Character | Description / Result |
| :--- | :--- | :--- | :--- |
| `0x01` | `1` | `Extended Graphics` | **Graphic prefix**: the immediately following byte (`0x40`–`0x5F`) is rendered using its alternate extended graphic glyph (font slots `0x00`–`0x1F`) instead of its normal ASCII form. Only effective on **European / International and Russian MSX**. See the **Extended Graphic Characters** section below. |
| `0x07` | `7` | `BEEP` | Fires a brief, physical hardware system audio bell alert. |
| `0x08` | `8` | `BackSpace` | Steps the visual text entry cursor left by one space. |
| `0x09` | `9` | `TAB` | Jumps the text entry cursor forward by 8 character blocks. |
| `0x0A` | `10` | `LineFeed` | Moves the tracking cursor directly down to the next text row. |
| `0x0C` | `12` | `CLS` / FormFeed | **Clear Screen**: Instantly wipes the entire text screen area. |
| `0x0D` | `13` | `CarriageReturn`| Moves the cursor back to the far left column of the row. |
| `0x1B` | `27` | `ESCAPE` | Starts an ANSI/VT52 terminal display cursor sequence. |
| `0x1F` | `31` | `HOME` | Returns the text cursor back to coordinates `0, 0` (top-left). |

---

## 🖼️ Extended Graphic Characters (`0x01` Prefix)

On **European (International) and Russian MSX**, characters `0x40`–`0x5F` have an alternate graphic glyph stored in font slots `0x00`–`0x1F`. Prepending byte `0x01` switches the next character to its graphic form.

The offset rule: `0x01 0x40` → font slot `0x00`, `0x01 0x41` → font slot `0x01`, …, `0x01 0x5F` → font slot `0x1F`.

> **Not available on Japanese, Arabic, or other non-European MSX variants.**  
> Reference: [MSX font](https://www.msx.org/wiki/MSX_font) · [MSX Characters and Control Codes](https://www.msx.org/wiki/MSX_Characters_and_Control_Codes)

In MSX BASIC: `PRINT CHR$(1)+"V"` prints a vertical bar `│`.  
In assembly: `DB 01h, 56h`

### Box-Drawing Characters (confirmed)

These glyphs are used by the KabelKrant BASIC source to draw UI frames:

| Sequence (BASIC) | Char | Bytes | Glyph | Description |
| :--- | :--- | :--- | :--- | :--- |
| `CHR$(1)+"S"` | `S` | `0x01 0x53` | `┤` | Right T-junction (separator line end) |
| `CHR$(1)+"T"` | `T` | `0x01 0x54` | `├` | Left T-junction (separator line start) |
| `CHR$(1)+"V"` | `V` | `0x01 0x56` | `│` | Vertical bar (left/right border) |
| `CHR$(1)+"W"` | `W` | `0x01 0x57` | `─` | Horizontal bar (top/bottom/separator fill) |
| `CHR$(1)+"X"` | `X` | `0x01 0x58` | `┌` | Top-left corner |
| `CHR$(1)+"Y"` | `Y` | `0x01 0x59` | `┐` | Top-right corner |
| `CHR$(1)+"Z"` | `Z` | `0x01 0x5A` | `└` | Bottom-left corner |
| `CHR$(1)+"["` | `[` | `0x01 0x5B` | `┘` | Bottom-right corner |

### Full Extended Graphic Range

The complete set spans `0x40`–`0x5F` (32 characters). Slots `0x40`–`0x52` map to font glyphs `0x00`–`0x12`, which contain block-fill and half-block graphic shapes. Slots `0x55`, `0x5C`–`0x5F` are additional line/block glyphs.

| Char | Bytes | Font slot | Notes |
| :--- | :--- | :--- | :--- |
| `@` | `0x01 0x40` | `0x00` | Block graphic (see MSX font) |
| `A`–`R` | `0x01 0x41`–`0x01 0x52` | `0x01`–`0x12` | Block graphic glyphs |
| `S` | `0x01 0x53` | `0x13` | `┤` Right T-junction |
| `T` | `0x01 0x54` | `0x14` | `├` Left T-junction |
| `U` | `0x01 0x55` | `0x15` | Cross / center junction |
| `V` | `0x01 0x56` | `0x16` | `│` Vertical bar |
| `W` | `0x01 0x57` | `0x17` | `─` Horizontal bar |
| `X` | `0x01 0x58` | `0x18` | `┌` Top-left corner |
| `Y` | `0x01 0x59` | `0x19` | `┐` Top-right corner |
| `Z` | `0x01 0x5A` | `0x1A` | `└` Bottom-left corner |
| `[` | `0x01 0x5B` | `0x1B` | `┘` Bottom-right corner |
| `\` | `0x01 0x5C` | `0x1C` | Top T-junction `┬` |
| `]` | `0x01 0x5D` | `0x1D` | Bottom T-junction `┴` |
| `^` | `0x01 0x5E` | `0x1E` | Block graphic glyph |
| `_` | `0x01 0x5F` | `0x1F` | Block graphic glyph |

---

## 🎨 Hex-to-Character Mapping Blocks

### 1. Control & Standard Numbers (`0x20 - 0x3F`)
* `0x20`: Spacebar canvas block
* `0x21 - 0x2F`: Math expressions and symbols (`! " # $ % & ' ( ) * + , - . /`)
* `0x30 - 0x39`: Numerical character blocks (`0 1 2 3 4 5 6 7 8 9`)
* `0x3A - 0x3F`: Layout syntax tags (`: ; < = > ?`)

### 2. Standard Uppercase Alphabet (`0x40 - 0x5F`)
* `0x40`: `@` symbol
* `0x41 - 0x5A`: Uppercase characters (`A` through `Z`)
* `0x5B - 0x5F`: Layout structural symbols (`[ \ ] ^ _`)

### 3. Standard Lowercase Alphabet (`0x60 - 0x7F`)
* `0x60`: `` ` `` Backtick character block
* `0x61 - 0x7A`: Lowercase characters (`a` through `z`)
* `0x7B - 0x7F`: Graphic boundary tokens (`{ | } ~ Δ`)

### 4. Extended Graphics & Accented Letters (`0x80 - 0xFF`)
The upper half of the MSX font engine contains European accented characters (`ç`, `é`, `ù`, etc.) alongside vintage 8-bit text-mode block elements used to create geometric layouts, borders, and custom progress bars without using bitmap graphics screen configurations.

#### Useful Text-Mode Frame Building Characters:
* **Vertical Line (`│`)**: Byte `0xBA`
* **Horizontal Line (`─`)**: Byte `0xCD`
* **Top-Left Corner (`┌`)**: Byte `0xC9`
* **Top-Right Corner (`┐`)**: Byte `0xBB`
* **Bottom-Left Corner (`└`)**: Byte `0xC8`
* **Bottom-Right Corner (`┘`)**: Byte `0xBC`
* **Solid Block Box (`█`)**: Byte `0xFF`

## 💬 Code Implementation for Agents

### Printing a Block Frame in Assembly (MSX-DOS string termination):
Unlike C strings which terminate in a zero byte (`0x00`), **MSX-DOS string subroutines terminate exclusively in a dollar sign (`$`)**. 
```assembly
PrintBoxHeader:
    LD   DE, FrameString
    LD   C, 09h             ; MSX-DOS service ID to write a string buffer
    CALL 0005h              ; Route to system call handler vector
    RET

FrameString: 
    ; Prints a Top-Left corner, 5 horizontal bars, a Top-Right corner, and a LineFeed
    DB   0C9h, 0CDh, 0CDh, 0CDh, 0CDh, 0CDh, 0BBh, 0Ah, 0Dh, "\$"
```
