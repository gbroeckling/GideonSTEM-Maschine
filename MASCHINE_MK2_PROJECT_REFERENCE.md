# Maschine MK2 + Traktor Pro 4 Stems Project — Technical Reference (v2)

> ⚠️ **Maintainers: `HANDOFF.md` is the current source of truth for project state.** Trust
> this file's TSI binary-format, enum, and TID sections. **Ignore its "current state" /
> roadmap and any modifier-paging plan** — they predate the shipped channel-based build.

> Persistent reference document. Contains every identifier, byte offset, control ID, MIDI mapping, and structural detail discovered during the build. Read this first when resuming work.

> **Note**: This is the v2 reference. It supersedes `MASCHINE_MK1_PROJECT_REFERENCE.md`. Garry has both MK1 and MK2 controllers but the project is now on the MK2. Most info applies to both since they share MIDI implementations, but RGB pad features are MK2-only.

---

## 1. PROJECT GOAL

Add comprehensive stem-deck control to a Native Instruments **Maschine MK2** hardware controller running alongside the existing **Frickhold Deluxe** TSI mapping in **Traktor Pro 4**. The MK2 stays in its existing role (pads for performance modes, transport, etc.) while:
- Top 8 knobs gain dedicated stem control with push-to-mute
- Pad grid acts as VU display: top half **red** for Deck A, bottom half **blue** for Deck B, brightness reflects stem volume

Long-term: full performance suite — stems + filter + FX send + pitch bend + beatjump + key shift + loops, all on the MK2, with the existing pad pages preserved (or replaced where appropriate).

---

## 2. HARDWARE TARGET

### Maschine MK2 (current target)
- **16 multicolor RGB pads** in 4×4 grid, velocity + aftertouch sensitive
- **8 push-encoder rotary knobs** (top row) — turn = CC, push = note, higher-than-MIDI resolution internally
- **2 LCD displays** (64×256 monochrome each)
- **8 display knobs** above displays (4 left, 4 right) — separate from top 8 knobs
- **16 display buttons** (8 left, 8 right) under displays
- **8 Group buttons (A–H)** — RGB on MK2, page switchers
- **47 backlit buttons** total (RGB-capable)
- **1 endless encoder** (30 steps) in master section + push
- **Master section**: encoder + Volume/Tempo/Swing buttons (no longer 3 separate knobs like MK1)
- **Transport buttons**: Play, Rec, Restart, Stop, Erase, Tap, Grid, Browse, Sampling
- **F1, F2, F3 buttons**
- **Modifier buttons**: Shift, Note Repeat, Step, Pad Mode, Keyboard, Scene, Pattern, Auto/Lock
- **Arrow buttons**: Lower L/R, Upper L/R, Master L/R
- **Rear**: USB 2.0, 5-pin MIDI In/Out, Kensington lock
- Dimensions: 320 × 295 × 60 mm
- Weight: 4.6 lb / 2.1 kg (slightly heavier than MK1)

### Maschine MK1 (legacy reference, also owned)
- Same 4×4 pad layout, 16 pads
- **Mono red/orange LEDs only**, brightness control only — no color
- Same 8 top knobs, displays, buttons
- 41 buttons total (vs 47 on MK2)
- Master section has 3 separate knobs (Volume, Tempo, Swing) instead of encoder
- Driver caveat: needs **X1Mk1_usb2midi bridge** (ko-fi) on macOS post-Mojave 10.14.6
- The .ncm template format differs from MK2's

### MK2 RGB pad protocol
The MK2 pads support **4 LED modes** in Controller Editor:
1. **1-Color**: Single fixed color, MIDI value drives brightness
2. **2-Color**: Two preset colors, MIDI value picks between them + brightness
3. **HSB**: Three separate MIDI CCs control Hue (color wheel), Saturation, Brightness independently — full dynamic color
4. **Indexed**: Single MIDI value looks up a color from a fixed palette

For our VU display we use **1-Color mode** (red on top half, blue on bottom half) since color is static per pad, only brightness varies.

### Software stack
- **Native Instruments Controller Editor** — manages MK2 → MIDI mapping (.ncm template files, binary, NOT public spec)
- **Traktor Pro 4** — receives MIDI, applies via Controller Manager (.tsi files, partly reverse-engineered)

---

## 3. EXISTING FRICKHOLD DELUXE TSI — FULL ANALYSIS

### File: `frickhold_maschine_deluxe.tsi`
- 2,299,094 bytes XML
- Single base64-encoded blob in `<Entry Name="DeviceIO.Config.Controller">`
- Decoded binary: 1,665,360 bytes
- 4 device entries inside:

| Offset    | Length  | Device Name                       |
|-----------|---------|-----------------------------------|
| 32        | 565,748 | `MF_FX 4Banks [A]` (Midi Fighter) |
| 565,788   | 556,784 | `MF_FX 4Banks [B]` (Midi Fighter) |
| 1,122,580 | 528,926 | `MASCHINE FRICKHOLD DELUXE$$$`    |
| 1,651,514 | 13,838  | (unnamed - small)                 |

### Maschine device structure (the one we care about)
- DDIF target: `0` = Focus (follows whichever deck has focus)
- DDIV version: `2.6.1 Dev` (revision 0x1c1 = 449)
- DDPT ports: "All Ports" / "All Ports"
- DDCI: 4,113 input MIDI definitions
- DDCO: 4,112 output MIDI definitions (LED feedback)
- DDCB: 71,938 bytes
  - CMAS: 383 CMAI mappings
  - DCBM: 383 binding labels

### Frickhold's MIDI footprint (130 unique inputs)

**Channel 1 CCs in use** (knobs, buttons, modifiers):
```
3, 7, 9, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
85, 86, 87, 88, 89, 90,
104, 105, 106, 107, 108, 109, 110, 111, 112,
115, 116, 117, 118, 119
```

**Channel 1 CCs FREE** (64 of them):
```
1, 2, 4, 5, 6, 8, 10, 11, 12, 13,
30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45,
62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84,
91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103,
113, 114, 120, 121, 122, 123, 124, 125, 126, 127
```

**Channel 8 CCs in use** (modifier-shifted layer, mostly free):
```
20, 46, 47, 48, 49, 50, 51, 52, 53
```
Channel 8 has **110 free CCs** out of 119.

**Channel 15** (currently free, now used for VU output): Notes 48-63 (C3-D#4)

**Channel 16** (originally free): now used for stem control inputs (CCs 20-27 + Notes C1-G1)

**Pad allocation by channel** (frickhold's architectural trick for A-H mode switching):
- Ch01: 16 pads (one mode, e.g., Group A)
- Ch02: 16 pads (alternate mode, e.g., Group C)
- Ch04: 14 pads (third mode, 2 notes mysteriously unmapped)
- Ch05: 16 pads (fourth mode)
- Ch08: 4 pads (modifier shift layer)

The Group A-H buttons cycle the pad page in Controller Editor, which sends pads on different MIDI channels. Traktor sees each channel's pads as separate inputs and binds them to different commands. Effectively gives 4-8 "modes" without using Traktor modifiers.

**FX-dedicated CCs that can be freed/repurposed**: Ch01 CCs 85-90 (FX engage/select in original).

### Frickhold's TraktorControlIds (73 unique)

| TID  | Type | Mode    | Deck | Example MIDI         | Likely meaning                       |
|------|------|---------|------|----------------------|--------------------------------------|
| 29   | Knob | Direct  | 0    | Ch01.CC.003          | Master volume / global               |
| 100  | Btn  | Toggle  | 0    | Ch01.CC.109          | Play (5x — multi-deck)               |
| 123  | Btn  | Inc     | 1    | Ch04.Note.D#4        | Beatjump or Inc-style command        |
| 125  | Btn  | Hold    | 0    | Ch01.CC.087          | Cue / Hold-style                     |
| 202  | Btn  | Toggle  | 0    | Ch02.Note.C#3        | Loop active / similar                |
| 204  | Btn  | Hold    | 0    | (CUP)                | Cue Up                               |
| 206  | Btn  | Hold    | 0    | (CUE)                | Cue                                  |
| 232  | Knob | Direct  | -    | Ch08.Note.D#1        | **Slot FX Amount** (Submix)          |
| 233  | Btn  | ?       | 2    | Ch08.Note.C1         |                                      |
| 239  | Btn  | Toggle  | -    | Ch01.Note.C#2        | **Slot FX On/Off** (Submix)          |
| 249  | Knob | Direct  | -    | Ch08.Note.C1         | **Slot Filter Amount** (Submix)      |
| 250  | Btn  | Toggle  | -    | Ch01.Note.X          | **Slot Filter On/Off** (Submix)      |
| 251  | Knob | Direct  | -    | (NEW in our TSI)     | **Slot Volume** (Submix) ⭐          |
| 258  | Btn  | Hold    | 8    | Ch08.CC.046          | Remix Slot mute (24x)                |
| 259  | Btn  | Toggle  | -    | (NEW in our TSI)     | **Slot Mute** (Submix) ⭐            |
| 265  | Btn  | Inc     | 8    | Ch05.Note.C#1        | Remix slot inc (16x)                 |
| 320  | Btn  | Direct  | 0    | Ch01.CC.111          |                                      |
| 321  | Btn  | Toggle  | 0    | Ch01.Note.C#2        | FX 1 enable                          |
| 322  | Btn  | Toggle  | 0    | Ch01.Note.A1         | FX 2 enable                          |
| 338  | Btn  | Toggle  | 0    | Ch01.Note.F1         |                                      |
| 339  | Btn  | Toggle  | 0    | Ch01.Note.C#1        |                                      |
| 362  | Knob | Direct  | 0    | Ch01.CC.015          | FX param                             |
| 363  | Knob | Direct  | 3    | Ch01.CC.028          | FX param                             |
| 364  | Knob | Direct  | 3    | Ch01.CC.029          | FX param                             |
| 365  | Knob | Direct  | 0    | Ch01.CC.014          | FX dry/wet                           |
| 366  | Knob | Direct  | 0    | Ch01.CC.015          | FX param 1                           |
| 367  | Knob | Direct  | 0    | Ch01.CC.016          | FX param 2                           |
| 368  | Knob | Direct  | 0    | Ch01.CC.017          | FX param 3                           |
| 369  | Btn  | Toggle  | 0    | Ch01.CC.046          | FX btn 1                             |
| 370  | Btn  | Toggle  | 0    | Ch01.CC.047          | FX btn 2                             |
| 371  | Btn  | Toggle  | 0    | Ch01.CC.048          | FX btn 3                             |
| 372  | Btn  | Toggle  | 0    | Ch01.CC.049          | FX btn 4                             |
| 400  | Btn  | Toggle  | 0    | Ch01.Note.C1         | (Hotcue something)                   |
| 402  | Knob | Direct  | 1    | Ch01.CC.009          |                                      |
| 406  | Btn  | Hold    | 1    | Ch04.Note.B3         |                                      |
| 733  | Btn  | Dec     | 2    | Ch08.Note.C#1        |                                      |
| 2056 | Btn  | Toggle  | 0    | Ch01.CC.109          |                                      |
| 2176 | Btn  | ?       | 1    | Ch01.CC.086          | Possibly Stem Mode modifier-style    |
| 2192 | Btn  | Hold    | 0    | (LOOP)               | Loop                                 |
| 2196 | Enc  | Rel     | 0    | (SIZE)               | Loop Size                            |
| 2240 | Btn  | ?       | 0    | (SYNC shifted)       |                                      |
| 2248 | Btn  | ?       | 0    | Ch01.Note.C2         |                                      |
| 2258 | Btn  | ?       | 0    | Ch04.Note.C#4        |                                      |
| 2259 | Btn  | ?       | 0    | Ch04.Note.C4         |                                      |
| 2293 | Btn  | ?       | 0    | (FX 1 shifted)       |                                      |
| 2298 | Btn  | Direct  | 0    | Ch02.Note.C2         | (12x — important)                    |
| 2301 | Btn  | Inc     | 0    | Ch01.CC.046          |                                      |
| 2302 | Btn  | Inc     | 0    | Ch01.CC.104          | **Stem Mode toggle** (frickhold)     |
| 2306 | Btn  | Inc     | 0    | (CUP shifted)        |                                      |
| 2311 | Btn  | Toggle  | 0    | Ch01.CC.089          |                                      |
| 2313 | Btn  | Toggle  | 0    | Ch01.CC.090          |                                      |
| 2317 | Btn  | Direct  | 0    | Ch02.Note.C3         |                                      |
| 2328 | Btn  | Hold    | 0    | Ch01.Note.C2 (16x)   | (Hotcue 1 hold?)                     |
| 2331 | Btn  | Hold    | 0    | Ch01.Note.C2 (16x)   | (Hotcue shifted?)                    |
| 2333-2340 | LED | Out  | 0    | Ch01.Note.X          | LED feedback for hotcue states       |
| 2350 | Btn  | Toggle  | 0    | Ch01.CC.108          |                                      |
| 2351 | Btn  | Dec     | 0    | Ch02.Note.E2         |                                      |
| 2372 | Btn  | Dec     | 0    | Ch02.Note.C2         |                                      |
| 2391 | Btn  | Direct  | 0    | Ch01.Note.D#2        | (BEAT something)                     |
| 2392 | Btn  | ?       | 0    | (IN modifier)        | Loop In (shifted)                    |
| 2393 | Btn  | ?       | 0    | (OUT modifier)       | Loop Out (shifted)                   |
| 2401 | Btn  | ?       | 1    | Ch01.CC.106          |                                      |
| 2402 | Btn  | ?       | 0    | Ch01.CC.105          |                                      |
| 2548-2553 | Btn | Direct/Hold | 0 | Ch01.CC.111-119  | Loop / IN / OUT system               |
| 2552 | Btn  | Direct  | 0    | (Shift+Play)         | **Stem Mode toggle** (X1's modifier) |
| 2553 | Btn  | Direct  | 0    | (Shift+Play right)   | Stem Mode Deck B                     |
| 2694-2703 | LED | Out  | 0    | Ch01.CC.X            | LED feedback                         |
| 3076 | Btn  | ?       | 1    | Ch01.CC.106          | Load                                 |
| 3200 | Btn  | Dec     | 0    | Ch01.CC.117          |                                      |
| 3456 | Btn  | Inc     | 0    | Ch01.CC.117          |                                      |
| 4162 | Btn  | Direct  | 0    | Ch01.CC.115          |                                      |
| 4209 | Btn  | Toggle  | 0    | Ch01.CC.116          | (Load shifted?)                      |
| 5129 | Btn  | Direct  | 0    | Ch01.CC.109          |                                      |
| 5144 | Btn  | ?       | 1    | Ch01.CC.107          |                                      |
| 5154 | Btn  | ?       | 1    | Ch04.Note.D#3        |                                      |

---

## 4. TRAKTOR TSI BINARY FORMAT (REVERSE-ENGINEERED)

Source: https://github.com/ivanz/TraktorMappingFileFormat (Ivan Zlatev, 2014, GPL)
Companion editor: https://github.com/TakTraum/cmdr (Michael Rahier, then Pedro Estrela)
Commercial editor (newer, uses ivanz spec): Super Xtreme Mapping (`superxtrememapper.github.io`)

### Wire format
- Big-endian throughout
- Strings: 4-byte char count (UTF-16-BE codepoints), then UTF-16-BE bytes
- Frame header: 4-byte ASCII tag + 4-byte big-endian length + payload

### Tag hierarchy

```
DIOM (root)
├── DIOI [4]          (always 0x00000001)
└── DEVS              (devices list)
    ├── int           NumberOfDevices
    └── DEVI[]        (one per device)
        └── DDAT      (device data)
            ├── DDIF [4]    DeviceTarget enum (0=Focus, 1=DeckA, 2=DeckB, 3=DeckC, 4=DeckD)
            ├── DDIV        VersionInfo: string + int revision
            ├── DDIC        Comment / Device display name (THIS is what shows in Controller Manager)
            ├── DDPT        DevicePorts: in_port_name + out_port_name (UTF-16 strings)
            ├── DDDC
            │   ├── DDCI    MidiInDefinitions: int count + DCDT[]
            │   └── DDCO    MidiOutDefinitions: int count + DCDT[]
            ├── DDCB
            │   ├── CMAS    MappingsList: int count + CMAI[]
            │   └── DCBM    MidiNoteBindingList: int count + DCBM[]
            └── DVST        unknown trailer (12 bytes empty in our generated TSI)
```

### Enums

```c
enum DeviceTarget {
    Focus = 0, DeckA = 1, DeckB = 2, DeckC = 3, DeckD = 4
};

enum MappingType { In = 0, Out = 1 };

enum MappingControllerType {
    Button = 0, FaderOrKnob = 1, Encoder = 2, LED = 65535 (0xFFFF)
};

enum MappingInteractionMode {
    Toggle = 1, Hold = 2, Direct = 3, Relative = 4,
    Increment = 5, Decrement = 6, Reset = 7, Output = 8
};

enum MappingTargetDeck {
    DeviceTargetDeck = -1,         // use device's DDIF
    AorFX1orRemixDeck1Slot1OrGlobal = 0,
    BorFX2orRemixDeck1Slot2 = 1,
    CorFX3orRemixDeck1Slot3 = 2,
    DorFX4orRemixDeck1Slot4 = 3,
    RemixDeck2Slot1 = 4, ..., RemixDeck2Slot4 = 7,
    RemixDeck3Slot1 = 8, ..., RemixDeck3Slot4 = 11,
    RemixDeck4Slot1 = 12, ..., RemixDeck4Slot4 = 15
};

enum MidiEncoderMode {
    _3Fh_41h = 0, _7Fh_01h = 1
};

// Resolution stored as IEEE-754 float bytes:
enum MappingResolution {
    Fine    = 0x3C800000,
    Min     = 0x3D800000,  // also DEFAULT
    Default = 0x3D800000,
    Coarse  = 0x3E000000,
    Switch  = 0x3F000000
};
```

### DCDT (MIDI Definition) — 46-52 bytes typical
```
[4-byte midi label length N]
[N*2 bytes UTF-16-BE midi label]   e.g. "Ch16.CC.020"
[4 bytes Unknown1] = 0
[4 bytes Unknown2] = 0
[4 bytes float Velocity] = 127.0 (0x42FE0000)
[4 bytes int EncoderMode] = 0
[4 bytes int ControlId] = 0xFFFFFFFF for non-NI controllers
```

### DCBM (Binding Label) — variable
```
[4 bytes int BindingId]
[4 bytes int LabelLength N]
[N*2 bytes UTF-16-BE label]   e.g. "Ch16.CC.020"
```

### CMAI (Mapping Instance) — 140 bytes typical
```
[4 bytes int MidiNoteBindingId]   ← matches a DCBM record's BindingId
[4 bytes int MappingType]          ← 0=In, 1=Out
[4 bytes int TraktorControlId]     ← which Traktor function (e.g., 251 = Slot Volume)
[CMAD frame]                       ← 8-byte header + 120-byte payload
```

### CMAD (Mapping Settings) — 120 bytes payload
```
Offset  Size  Type   Field
0       4     int    Unknown1 (always 4)
4       4     int    ControllerType (Button=0, Knob=1, Encoder=2, LED=65535)
8       4     int    InteractionMode (1=Toggle, 2=Hold, 3=Direct, 4=Rel, 5=Inc, 6=Dec, 7=Reset, 8=Output)
12      4     int    Deck/Slot (signed; -1=DeviceTarget, 0-3=A/B/C/D OR Slot 1-4 for Submix)
16      4     int    AutoRepeat (0/1)
20      4     int    Invert (0/1)
24      4     int    SoftTakeover (0/1)
28      4     float  RotarySensitivity (5.0 typical, 1% UI = 0.5f, 300%=15f for Direct)
32      4     float  RotaryAcceleration (0.0 typical)
36      4     -      Unknown10 (00000000 typical)
40      4     -      Unknown11 (00000001 or 00000002, varies)
44      4     float  SetValueTo (0.0 or 1.0 typical)
48      4     int    CommentLength N
52      N*2   utf16  Comment (UTF-16-BE)  ← variable length!
52+N*2  4     int    ModifierOneId (0 = no modifier; else Traktor control ID of modifier)
+4      4     -      Unknown15
+8      4     int    ModifierOneValue (modifier state required to fire)
+12     4     int    ModifierTwoId
+16     4     -      Unknown18
+20     4     int    ModifierTwoValue
+24     4     -      Unknown20
+28     4     float  LedMinControllerRange (0.0 typical)
+32     4     -      Unknown22
+36     4     float  LedMaxControllerRange (1.0 typical)
+40     4     int    LedMinMidiRange (0)
+44     4     int    LedMaxMidiRange (127)
+48     4     int    LedInvert (0/1)
+52     4     int    LedBlend (0=threshold, 1=linear interpolation)
+56     4     -      Unknown29
+60     4     enum   Resolution (0x3D800000 = Default for knobs, 0x00000001 for buttons)
+64     4     -      Unknown30 (00000000)
                                         total = 120 bytes
```

**Critical**: The Comment field is dynamically sized — fields after it shift accordingly. Use `48+CommentLength*2` to find ModifierOneId.

---

## 5. KEY TRAKTOR CONTROL IDS (extracted from real mappings)

### Submix / Stem Deck commands (TP 2.9+)
Discovered via NI Kontrol X1 STEMS TSI by parsing CMAIs with comment "Stem Mode Deck A":

| TraktorControlId | Function           | ControllerType | InteractionMode | Notes                       |
|------------------|--------------------|----------------|-----------------|-----------------------------|
| **251**          | Slot Volume        | Knob (1)       | Direct (3)      | Slot in CMAD deck field 0-3 |
| **259**          | Slot Mute          | Button (0)     | Toggle (1)      | Slot in CMAD deck field 0-3 |
| **249**          | Slot Filter Amount | Knob (1)       | Direct (3)      | Slot in deck field          |
| **250**          | Slot Filter On/Off | Button (0)     | Toggle (1)      | Slot in deck field          |
| **232**          | Slot FX Amount     | Knob (1)       | Direct (3)      | Slot in deck field          |
| **239**          | Slot FX On/Off     | Button (0)     | Toggle (1)      | Slot in deck field          |

**Note**: These are "Deck Common > Submix" commands per NI's own documentation. They work on both Stem Decks AND Remix Decks (same controls cover both).

The X1 Stems mapping uses a "Stem Mode" modifier (TID 2552) that cycles through 3 values (1=Vol/Mute, 2=Filter, 3=FX), all on the same physical knobs — the modifier conditions in CMAD select which TID is active. Our generated TSI doesn't use this modifier — knobs are dedicated to volume.

### TID 251 verified usage as Out (LED) mapping — IMPORTANT
TID 251 is normally an Input (knob → volume). For our VU display, we use it as an Output:
- ControllerType = 65535 (LED)
- InteractionMode = 8 (Output)
- LedMinControllerRange/LedMaxControllerRange threshold the volume range (0.0-1.0)
- LedMinMidiRange/LedMaxMidiRange (0-127) define the MIDI value range
- LedBlend = 1 for linear interpolation (smooth fade), 0 for threshold (binary on/off)

**Status**: Structurally valid per spec. **Not yet verified that Traktor actually emits volume change events for stem slots.** If the pads don't light, fallback is TID 259 (mute state) for binary feedback only.

### Common Track Deck IDs (observed)
- 100 = Play
- 125 = Sync (or related)
- 103 = Cue Reset
- 204 = CUP (Cue Up)
- 206 = Cue
- 2306 = (CUP shifted, increment-style)

### Loop IDs (observed in X1)
- 2192 = Loop Active
- 2196 = Loop Size (encoder, relative)
- 202 = Loop something (toggle)
- 2548-2553 = Loop In/Out system
- 2391 = "<BEAT" (beat indicator/sync target)
- 2351 = Beatjump or similar (Dec)
- 2372 = Beatjump (Dec, deck=0)

### FX IDs (observed)
- 321 = FX 1 enable
- 322 = FX 2 enable
- 2293 = FX 1 (shifted)
- 2311, 2313 = FX selectors (toggle)
- 365-368 = FX D/W and params 1-3
- 369-372 = FX buttons 1-4

### Hotcue IDs (observed)
- 400 = Hotcue 1
- 2328 = Hotcue 1 hold
- 2331 = Hotcue 1 (shifted/direct)
- 2333-2340 = Hotcue LED states

### Browser/Load IDs (observed)
- 3076 = Load
- 3200 = (CC 117 dec)
- 3456 = (CC 117 inc)
- 4209 = Load (shifted)

### Modifier Control IDs (used for layered mappings)
- 2548-2553 = Various transient modifier triggers
- 2552 = Stem Mode (X1 STEMS TSI)
- 2553 = Stem Mode Deck B (X1 STEMS CD TSI)
- 2301, 2302 = FX/Stem mode toggles (frickhold)
- 513 = Beat Phase (continuous output, range 0.0-0.5, used for "<BEAT" indicator)

### Beat/Phase IDs
- 513 = Beat Phase output (rotating beat indicator, range 0.0-0.5 cycles per beat)
- 850 = (related to BEAT ←/→, less continuous)

---

## 6. CURRENT GENERATED TSIs

### v1: `Maschine_MK1_Stems.tsi` (legacy filename, works on MK2)
- 6,103 bytes XML, 4,444 byte binary blob
- 2 devices: Deck A and Deck B
- 8 inputs each (4 stem volumes + 4 mutes), no outputs
- Uses Generic MIDI device type (no NI driver dependency)

### v2: `Maschine_MK2_Stems_VU.tsi` (current focus)
- 11,359 bytes XML, 8,388 byte binary blob
- 2 devices: Deck A and Deck B
- 8 inputs + 8 outputs each = 16 mappings per device
- Outputs drive pad LED brightness based on slot volume
- Color is set in Controller Editor (red top half, blue bottom half) — not in TSI

### v2 Full mapping table

**Device 1: "Maschine MK2 Stems+VU (Deck A)"** — DDIF=DeckA (1)

Inputs:
| Knob | Action | MIDI                  | TID | Slot | Maps to                |
|------|--------|-----------------------|-----|------|------------------------|
| 1    | turn   | Ch16 CC 20            | 251 | 0    | Deck A Stem 1 Volume   |
| 1    | push   | Ch16 Note C1 (note 36)| 259 | 0    | Deck A Stem 1 Mute     |
| 2    | turn   | Ch16 CC 21            | 251 | 1    | Deck A Stem 2 Volume   |
| 2    | push   | Ch16 Note C#1 (note 37)|259 | 1    | Deck A Stem 2 Mute     |
| 3    | turn   | Ch16 CC 22            | 251 | 2    | Deck A Stem 3 Volume   |
| 3    | push   | Ch16 Note D1 (note 38)| 259 | 2    | Deck A Stem 3 Mute     |
| 4    | turn   | Ch16 CC 23            | 251 | 3    | Deck A Stem 4 Volume   |
| 4    | push   | Ch16 Note D#1 (note 39)|259 | 3    | Deck A Stem 4 Mute     |

Outputs (top half = pads 9-16, RED):
| Pad | Position | Output MIDI               | Slot | VU range  | Maps to                          |
|-----|----------|---------------------------|------|-----------|----------------------------------|
| 9   | row 3    | Ch15 Note G#3 (56)        | 0    | 0.0-0.5   | Deck A Stem 1 Volume (low band)  |
| 10  | row 3    | Ch15 Note A3 (57)         | 1    | 0.0-0.5   | Deck A Stem 2 Volume (low band)  |
| 11  | row 3    | Ch15 Note A#3 (58)        | 2    | 0.0-0.5   | Deck A Stem 3 Volume (low band)  |
| 12  | row 3    | Ch15 Note B3 (59)         | 3    | 0.0-0.5   | Deck A Stem 4 Volume (low band)  |
| 13  | top row  | Ch15 Note C4 (60)         | 0    | 0.5-1.0   | Deck A Stem 1 Volume (high band) |
| 14  | top row  | Ch15 Note C#4 (61)        | 1    | 0.5-1.0   | Deck A Stem 2 Volume (high band) |
| 15  | top row  | Ch15 Note D4 (62)         | 2    | 0.5-1.0   | Deck A Stem 3 Volume (high band) |
| 16  | top row  | Ch15 Note D#4 (63)        | 3    | 0.5-1.0   | Deck A Stem 4 Volume (high band) |

**Device 2: "Maschine MK2 Stems+VU (Deck B)"** — DDIF=DeckB (2)

Inputs:
| Knob | Action | MIDI                  | TID | Slot | Maps to                |
|------|--------|-----------------------|-----|------|------------------------|
| 5    | turn   | Ch16 CC 24            | 251 | 0    | Deck B Stem 1 Volume   |
| 5    | push   | Ch16 Note E1 (note 40)| 259 | 0    | Deck B Stem 1 Mute     |
| 6    | turn   | Ch16 CC 25            | 251 | 1    | Deck B Stem 2 Volume   |
| 6    | push   | Ch16 Note F1 (note 41)| 259 | 1    | Deck B Stem 2 Mute     |
| 7    | turn   | Ch16 CC 26            | 251 | 2    | Deck B Stem 3 Volume   |
| 7    | push   | Ch16 Note F#1 (note 42)|259 | 2    | Deck B Stem 3 Mute     |
| 8    | turn   | Ch16 CC 27            | 251 | 3    | Deck B Stem 4 Volume   |
| 8    | push   | Ch16 Note G1 (note 43)| 259 | 3    | Deck B Stem 4 Mute     |

Outputs (bottom half = pads 1-8, BLUE):
| Pad | Position  | Output MIDI               | Slot | VU range  | Maps to                          |
|-----|-----------|---------------------------|------|-----------|----------------------------------|
| 1   | bottom    | Ch15 Note C3 (48)         | 0    | 0.0-0.5   | Deck B Stem 1 Volume (low band)  |
| 2   | bottom    | Ch15 Note C#3 (49)        | 1    | 0.0-0.5   | Deck B Stem 2 Volume (low band)  |
| 3   | bottom    | Ch15 Note D3 (50)         | 2    | 0.0-0.5   | Deck B Stem 3 Volume (low band)  |
| 4   | bottom    | Ch15 Note D#3 (51)        | 3    | 0.0-0.5   | Deck B Stem 4 Volume (low band)  |
| 5   | row 2     | Ch15 Note E3 (52)         | 0    | 0.5-1.0   | Deck B Stem 1 Volume (high band) |
| 6   | row 2     | Ch15 Note F3 (53)         | 1    | 0.5-1.0   | Deck B Stem 2 Volume (high band) |
| 7   | row 2     | Ch15 Note F#3 (54)        | 2    | 0.5-1.0   | Deck B Stem 3 Volume (high band) |
| 8   | row 2     | Ch15 Note G3 (55)         | 3    | 0.5-1.0   | Deck B Stem 4 Volume (high band) |

### NI Stem default order (drums/bass/other/vocals)
- Slot 1 (deck=0) = Drums (red color)
- Slot 2 (deck=1) = Bass (orange)
- Slot 3 (deck=2) = Other / Melody (blue)
- Slot 4 (deck=3) = Vocals (green)

### Visual layout reminder

```
   ┌──────┬──────┬──────┬──────┐
   │ 🟥13 │ 🟥14 │ 🟥15 │ 🟥16 │  Deck A — high zone (vol 50-100%)
   ├──────┼──────┼──────┼──────┤
   │ 🟥 9 │ 🟥10 │ 🟥11 │ 🟥12 │  Deck A — low zone  (vol  0-50%)
   ├──────┼──────┼──────┼──────┤
   │ 🟦 5 │ 🟦 6 │ 🟦 7 │ 🟦 8 │  Deck B — high zone (vol 50-100%)
   ├──────┼──────┼──────┼──────┤
   │ 🟦 1 │ 🟦 2 │ 🟦 3 │ 🟦 4 │  Deck B — low zone  (vol  0-50%)
   └──────┴──────┴──────┴──────┘
     S1     S2     S3     S4
   Drums  Bass  Other  Vocals
```

### CMAD differences from X1 reference (validated)
v1 vs X1 reference: only 2 fields differ:
- **ModifierOneId**: ours = 0 (no modifier), X1 = 2552 (stem mode)
- **ModifierOneValue**: ours = 0, X1 = 1

All other 28 CMAD fields match byte-for-byte.

v2 adds Out CMADs which use different field values:
- ControllerType = 65535 (LED) instead of 1 (Knob)
- InteractionMode = 8 (Output) instead of 3 (Direct)
- LedMinControllerRange/LedMaxControllerRange thresholds set per pad
- Mapping_type = 1 (Out) at CMAI level instead of 0 (In)

### Build script
File: `build_tsi_v2.py` (in `/home/claude/tsi_build/`)
- Pure Python 3, stdlib only (struct, base64)
- Functions: `build_cmad_volume(slot)`, `build_cmad_mute(slot)`, `build_cmad_vu(slot, vu_min, vu_max)`, `build_cmai()`, `build_dcbm_record()`, `build_dcdt()`, `build_device(name, deck, in_mappings, out_mappings)`
- Reusable for generating new variants — change input/output lists, regenerate

---

## 7. NCM (CONTROLLER EDITOR) FORMAT — UNKNOWN

The Maschine MK2 template format `.ncm` is a **proprietary NI binary format with no public spec**. Cannot generate. Manual config in Controller Editor required for the MK2 → MIDI side.

### What's needed in CE for the v2 stems+VU layer

**Top 8 knobs (input):**
- Type=Control Change, Channel=16, CC#=20-27, Mode=Absolute, Range 0-127

**Top 8 knob pushes (input):**
- Type=Note, Channel=16, Note#=36-43, Mode=Gate, Velocity Min/Max=127

**Pads 9-16 LED output (Deck A, RED):**
- LED mode = **1-Color**
- Color preset: **Red** (or any deep red)
- MIDI input notes for LED: Channel 15, Notes 56-63 (G#3, A3, A#3, B3, C4, C#4, D4, D#4)
- The pad's input note (what it sends when pressed) is unrelated and stays as whatever frickhold's mapping uses

**Pads 1-8 LED output (Deck B, BLUE):**
- LED mode = **1-Color**
- Color preset: **Blue**
- MIDI input notes for LED: Channel 15, Notes 48-55 (C3, C#3, D3, D#3, E3, F3, F#3, G3)

### MK2 RGB color reference (1-Color mode presets)

In Controller Editor, common color choices for the 1-Color preset:
- White, Light grey, Dark grey, Black
- Pink, Red, Orange, Light orange, Warm yellow, Yellow
- Lime, Green, Mint, Cyan, Turquoise, Blue
- Plum, Violet, Magenta

For our use:
- Top half = "Red"
- Bottom half = "Blue"

For HSB mode (future): Hue 0=red, 32=yellow, 64=green, 96=blue, 112=magenta. Saturation 127=full color, 0=white. Brightness 0-127.

---

## 8. THE MISSING BASE MAPPING (FROM OLD MACHINE)

User has a free MK1 community mapping he used previously, characterized by:
- Free, MK1-native (not MK2 port)
- A-H Group buttons each switch full pad keypad to a different mode
- 8 pads per deck split per mode (top 8 = Deck A, bottom 8 = Deck B, OR similar)
- Modes are performance-focused: pitch shift, step sequencer, slicer prominent
- Possibly hotcues somewhere; explicitly NO loops mode
- Mapping description listed each Group A-H mode by name (rare)

Mappings ruled out so far:
- DJTT #6426 (Traktor+Maschine=Love) — MK2 only, author confirmed
- DJTT #1237 (Paulz Ultimate) — has both MK1+MK2 but A-D = cues+loops, E-H = FX presets
- DJTT #448 (Beaubryte Remix Fighter) — MK1 native but FX-heavy
- DJTT #5331 (Mario Costa Cue Slicer/Key) — DJTT page 500-erroring, hardware unconfirmed
- DJ Rafik's Maschine Mapping — MK2 only, has the right A-H-mode structure with Pitch Cue on E/F

Garry will dig out original files from old machine. When found:
- Drop .ncm + .tsi into chat
- Parse the .tsi for additional CC/Note/TID info
- Possibly merge into our generated stems TSI for one unified file

---

## 9. ROADMAP — DETAILED

### Immediate next steps (testing phase)
1. **Test v1 first** — import `Maschine_MK1_Stems.tsi`, verify knob inputs work
2. **Then test v2** — import `Maschine_MK2_Stems_VU.tsi`, verify pads light when stem volumes change
3. **Configure Controller Editor**:
   - Top 8 knobs CC + Note assignments (per Section 6 input table)
   - Pads 9-16 set to red 1-Color, listening on Ch15 Notes 56-63
   - Pads 1-8 set to blue 1-Color, listening on Ch15 Notes 48-55
4. Watch for behavior:
   - Knobs control stems? ✓
   - Pad pushes mute stems? ✓
   - Pads light up red/blue based on slot volume? ⚠️ (untested)
   - If pads don't respond: Traktor doesn't emit Slot Volume change events, fallback to TID 259 for binary mute feedback
5. **If TSI fails to load**: check Traktor's log file (`~/Documents/Native Instruments/Traktor X.X/Logs`)

### Phase 2 — LED feedback for binary mute state (fallback if v2 VU doesn't work)
- Add 8 entries to DDCO using TID 259 (Slot Mute) as Out
- Same MIDI Notes as the In mappings (knob push notes)
- LedBlend=0 (binary), LedMaxMidiRange=127 (full bright when muted)
- Result: knob LED on the push button = mute state indicator (not VU)

### Phase 3 — Stem Filter knobs
- Use 8 of the **display knobs** (CC 22-29 currently used by frickhold for FX) — REPURPOSE
- TIDs: 249 (filter amount knob), 250 (filter on/off button)
- Display knobs left bank (CC 22-25) = Deck A stem filters 1-4
- Display knobs right bank (CC 26-29) = Deck B stem filters 1-4
- Filter on/off via display buttons under the knobs (CC 46-53 left, 54-61 right)

### Phase 4 — Stem FX Send
- TIDs: 232 (FX amount knob), 239 (FX on/off button)
- Could share display knobs with Filter via a modifier toggle
- Or assign to other freed CCs

### Phase 5 — Performance tools (repurposing freed FX area)
Free CCs to use: Ch01 85-90 + nearly all of Ch08

Suggested tools (per `performance_tools_setup.md`):
- **Pitch Bend**: 2 display knobs (Tempo Bend, relative encoder mode, sensitivity 0.5)
- **Beatjump**: F1/F2/F3 + extras (1, 4, 8 beats, fwd/back, both decks)
- **Key Shift**: display buttons L1-L3, R1-R3 (semitone ±, reset)
- **Loop In/Out**: display buttons L4-L6, R4-R6
- **Loop Size**: display buttons L7-L8, R7-R8

### Phase 6 — Stem Solo (modifier-shifted)
- Hold Shift + push knob = solo that stem (mute all OTHER stems on that deck)
- Need TID for "Slot Solo" — not yet discovered (search future TSIs)
- Or implement as macro: shift+knob_push triggers 3 mute commands on the OTHER 3 slots

### Phase 7 — Document complete Controller Editor MK2 template
- Map every MK2 control to exact CE assignment
- Print/save as PDF reference card
- Include color settings per pad/button
- Could regenerate the .ncm if format ever gets reverse-engineered

### Long-term ideas
- **Python TSI generator library**: the `build_tsi.py` / `build_tsi_v2.py` scripts could become a real library, taking declarative YAML/JSON input → outputting valid TSIs
- **TSI merger utility**: combine frickhold's existing TSI + our stems TSI into a single import (currently 3 separate device entries)
- **Visualize TSI structure**: tree view of all CMAIs with comments + MIDI bindings, faster than navigating Traktor's UI
- **Auto-port between MK1 / MK2 / MK3 / Mikro / Jam**: same Traktor side, regenerate Controller Editor templates per device
- **Build the missing "modes" mapping from scratch**: given user's A-H performance-mode preference, produce a complete MK2 mapping with pitch/step/slice on Groups A-H
- **Full HSB output mode**: dynamic color per pad based on multiple parameters (e.g., color shifts red→yellow→green as volume rises, 3-CC HSB output)
- **Beat-synced pad animation**: use TID 513 (Beat Phase) to animate pads in time with the beat grid (would require careful LED Out mapping with phase-based threshold)
- **Use Maschine Jam alongside MK2**: 8×8 grid would give 64 pads = full waveform visualization on one of frickhold's freed channels. Garry has both controllers.

---

## 10. EXTERNAL RESOURCES

### TSI format docs
- ivanz spec: https://github.com/ivanz/TraktorMappingFileFormat
- C# implementation: https://github.com/ivanz/Traktor.Mapping
- CMDR editor source: https://github.com/TakTraum/cmdr
- Super Xtreme Mapping (commercial): https://superxtrememapper.github.io/super-xtreme-mapper/

### NI documentation
- Stem control how-to: https://support.native-instruments.com/hc/en-us/articles/210295045
- Building Maschine→Traktor mappings: https://blog.native-instruments.com/how-to-make-a-maschine-mapping-for-traktor-part-1/
- Controller Editor Manual: https://www.native-instruments.com/fileadmin/ni_media/downloads/manuals/CONTROLLER_EDITOR_Manual_English.pdf
- MASCHINE MK2 Hardware Reference: https://www.native-instruments.com/fileadmin/ni_media/downloads/manuals/maschine/MASCHINE_2.0_MK2_Hardware_Control_Reference_English.pdf

### MK2 reverse-engineering / hacks (HID protocol, not MIDI)
- shaduzlabs `cabl` library (formerly maschinIO): http://www.shaduzlabs.com/blog/19/maschinio-is-dead-long-live-maschinio.html
- Vincenzo Pacella (shaduzlabs) GitHub: https://github.com/shaduzlabs
- terminar/rebellion: https://github.com/terminar/rebellion (basic MK1 support, MK3 + Komplete Kontrol focus)
- biappi/Macchina (MK1 from 2012)
- fzero/maschine-mk1 (MK1 Linux reverse-engineering)
- These tools bypass MIDI entirely and speak NI's NHL/HID protocol — NOT useful for our Traktor-driven approach but exist as a fallback for full custom display control

### Reference TSIs (parsed during this project)
- `frickhold_maschine_deluxe.tsi` — base mapping (4 devices, 1.6MB binary)
- `Kontrol X1 STEMS (AB).tsi` — NI's stem mapping reference (1 device "STEMS", 89KB binary, 394 mappings)
- `Kontrol X1 STEMS (CD).tsi` — same structure for decks C/D

### Stems-related mappings to consider extracting more TIDs from
- DJTT #7332 — Stewe MF Twister 4-Deck Stems (has Filter, FX, VU layers)
- DJTT #4745 — MF Twister 4-Deck Stems AB-CD-FX
- Community S4 MK3 stem remap (red_nick) — `stem-remap-v1.tsi`, `s4mk3-stem-control-v2.tsi`
- Pioneer DDJ-FLX4 Stems (traktormaps.com) — has Stem Solo + Stem FX Solo
- Kontrol F1 Traktor Pro 4 (traktormaps.com) — combines Pattern Player + Stems with full LED feedback

### Useful tools
- **010 Editor** (commercial) + the ivanz `.bt` template — visual binary structure browser
- **Python struct module** — sufficient for parsing/generating, no special tools needed
- **MIDI Monitor** (Snoize) — for spying on MIDI traffic when debugging
- **Wireshark** with `usbaudio.midi.event` filter — for USB-level MIDI capture (Mixxx wiki has detailed guide)

---

## 11. ENVIRONMENT NOTES

### Build location (for future Claude sessions)
- TSI build scripts: `/home/claude/tsi_build/build_tsi.py` (v1), `build_tsi_v2.py` (v2 with VU)
- Reference X1 TSI binary: parse `/mnt/user-data/uploads/Kontrol_X1_STEMS_1_0.zip` → Kontrol X1 STEMS (AB).tsi
- Frickhold TSI: `/mnt/user-data/uploads/frickhold_maschine_deluxe.tsi`
- Final outputs: `/mnt/user-data/outputs/Maschine_MK1_Stems_for_Frickhold.zip` (v1), `Maschine_MK2_Stems_VU.zip` (v2)

### Quick parser snippet (reusable across sessions)
```python
import re, base64, struct

def parse_tsi(path):
    with open(path, 'r') as f:
        content = f.read()
    m = re.search(r'<Entry Name="DeviceIO\.Config\.Controller"[^>]*Value="([^"]*)"', content)
    return base64.b64decode(m.group(1))

def find_tag(data, tag, start=0):
    pos = data.find(tag.encode(), start)
    if pos < 0: return None
    length = struct.unpack('>I', data[pos+4:pos+8])[0]
    return pos, length, data[pos+8:pos+8+length]

def parse_cmai(body):
    return {
        'binding_id': struct.unpack('>I', body[0:4])[0],
        'type': 'In' if struct.unpack('>I', body[4:8])[0] == 0 else 'Out',
        'tid': struct.unpack('>I', body[8:12])[0],
        'cmad': body[20:],  # 120 bytes
    }

def parse_cmad(cmad):
    base = {
        'controller_type': struct.unpack('>I', cmad[4:8])[0],
        'interaction_mode': struct.unpack('>I', cmad[8:12])[0],
        'deck': struct.unpack('>i', cmad[12:16])[0],
        'set_value_to': struct.unpack('>f', cmad[44:48])[0],
        'comment_length': struct.unpack('>I', cmad[48:52])[0],
    }
    pos = 52 + base['comment_length']*2
    base['mod1_id'] = struct.unpack('>I', cmad[pos:pos+4])[0]
    base['mod1_val'] = struct.unpack('>I', cmad[pos+8:pos+12])[0]
    base['mod2_id'] = struct.unpack('>I', cmad[pos+12:pos+16])[0]
    base['mod2_val'] = struct.unpack('>I', cmad[pos+20:pos+24])[0]
    # LED-related fields
    base['led_min_ctrl'] = struct.unpack('>f', cmad[pos+28:pos+32])[0]
    base['led_max_ctrl'] = struct.unpack('>f', cmad[pos+36:pos+40])[0]
    base['led_min_midi'] = struct.unpack('>I', cmad[pos+40:pos+44])[0]
    base['led_max_midi'] = struct.unpack('>I', cmad[pos+44:pos+48])[0]
    base['led_blend'] = struct.unpack('>I', cmad[pos+52:pos+56])[0]
    return base
```

### Quick TSI builder snippet (for one-off generation)
```python
import struct, base64

def utf16be_str(s):
    return struct.pack('>I', len(s)) + s.encode('utf-16-be')

def frame(tag, payload):
    return tag.encode() + struct.pack('>I', len(payload)) + payload

# See build_tsi_v2.py for full builders. Key functions:
# - build_cmad_volume(slot) -> 120 bytes for input volume knob
# - build_cmad_mute(slot) -> 120 bytes for input mute toggle
# - build_cmad_vu(slot, vu_min, vu_max) -> 120 bytes for output LED VU
# - build_cmai(binding_id, type, tid, cmad) -> CMAI frame
# - build_device(name, target_deck, in_mappings, out_mappings) -> DEVI frame
```

---

## 12. UNRESOLVED QUESTIONS / FUTURE WORK

- [ ] **Critical**: Does Traktor actually send Slot Volume change events as Output? If yes, our v2 VU works. If no, fall back to mute-state-only feedback.
- [ ] Stem Solo TraktorControlId — not yet observed in any TSI we've parsed. Likely a TID near 232/239/249/250/259 range. Pioneer DDJ-FLX4 Stems mapping mentions "Stem Solo" + "Stem FX Solo" — buy/parse that mapping.
- [ ] Stem Filter Type select (Z-iso vs LP/HP) — TP4 may have multiple filter modes per stem
- [ ] LED state TIDs for stem mute/filter/fx — partially known, need a TSI with LED feedback already wired (Kontrol F1 TP4 mapping likely has it)
- [ ] How frickhold actually used pad pages A-H — would need to map all 16 pads × 4 channels × modifier states to deduce the mode layout. ~250 CMAIs worth of analysis.
- [ ] Whether DDIF=Focus + slot field works as well as DDIF=DeckA explicit — could simplify to one device
- [ ] Whether NI Stem Decks support different track stems orderings (drums/bass/melody/vox is convention but per-track encoded)
- [ ] MK2 RGB color value for "Red" and "Blue" presets in 1-Color mode — need to check Controller Editor's color picker, may have specific MIDI values that work better than others
- [ ] HSB output protocol exact CC mapping for Maschine MK2 pads — Pioneer F1 thread says CH1=Hue, CH2=Sat, CH3=Brightness on the same CC. Need to verify MK2 follows same convention.
- [ ] Whether Traktor can drive multiple Out CMAIs in the same clock cycle (16 stem volume outputs all updating simultaneously could cause MIDI flood)

---

## 13. FILES PRODUCED THIS PROJECT

1. `/mnt/user-data/outputs/stem_mapping_setup.md` — manual setup guide (initial)
2. `/mnt/user-data/outputs/performance_tools_setup.md` — repurposing guide for FX area
3. `/mnt/user-data/outputs/Maschine_MK1_Stems_for_Frickhold.zip` — v1: input-only stem control
   - Contains: TSI file, README, build script, this reference doc (v1)
4. `/mnt/user-data/outputs/Maschine_MK2_Stems_VU.zip` — v2: stems + VU pad output
   - Contains: TSI file, README, build script v2, this reference doc (v2)

---

## 14. SESSION NOTES & GOTCHAS

### MK1 vs MK2 distinction
- User initially said "MK1" — actually has MK2 (RGB pads). Both files were generated assuming MK2. The v1 filename says "MK1" but works on either.
- User has BOTH controllers, currently focused on MK2.
- Maschine Jam (8×8 grid) is also potentially in user's setup — could be used as visualization surface in future phases.

### Traktor Pro 4 specifics
- Uses TSI format identical to TP3 (binary spec is the same)
- Stem decks introduced in TP 2.9
- TP4 added native stem separation (AI-driven, in-app)
- DDIV version field can be older (e.g., "2.6.1 Dev") and TP4 still loads it fine

### Critical gotchas
1. **Comment field is variable-length** in CMAD — fields after it (modifiers, LED ranges) are at offset `52 + commentLength*2`, not fixed.
2. **TraktorControlId is at CMAI level**, not CMAD. CMAI is `binding_id(4) + type(4) + tid(4) + CMAD_frame`.
3. **Slot encoding**: For Submix commands, the deck field in CMAD encodes the slot number (0-3), and the device's DDIF encodes which deck (A/B/C/D). So same TID = different slot per CMAI.
4. **LedBlend matters**: `0` = hard threshold (binary on/off when LedMin/Max crossed), `1` = linear interpolation (smooth fade between LedMinMidi and LedMaxMidi).
5. **In/Out can share TID** — TID 251 is used for input (Volume knob) AND output (Volume state for VU). Distinguished by mapping_type field (0/1).
6. **Pad LED color is set in Controller Editor, not TSI**. The TSI just sends MIDI values 0-127; CE decides what color to show. To change pad colors, edit the .ncm template, not regenerate the TSI.

### Future Claude sessions: how to resume
- User says "Maschine project" → search past chats with conversation_search tool
- Or user uploads `MASCHINE_MK2_PROJECT_REFERENCE.md` (this doc) → instant full context restoration
- Build environment in `/home/claude/tsi_build/` is wiped between sessions; recreate from `build_tsi_v2.py` if needed (the script is in the output zip)

---

*End of v2 technical reference. When resuming this project, search past chats for "Maschine MK2 stems Frickhold" or upload this file to bring full context back.*
