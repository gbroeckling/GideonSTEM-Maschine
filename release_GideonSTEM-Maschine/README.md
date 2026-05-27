# GideonSTEM-Maschine — Traktor Pro mapping for Native Instruments Maschine MK2

**A full Traktor Pro STEMS + performance mapping for the Maschine MK2, turning the
controller into a 2‑deck stems mixer, loop/beatjump/remix/key performance pad surface,
transport + browser controller, and a live main‑output VU meter.**

> ## ⚠️ ALPHA RELEASE — read this first
> This mapping is **alpha**. It is in active testing on real hardware. The core
> functions below are confirmed working, but some output/LED features are still being
> validated and behaviour may change between versions. **Back up your existing Traktor
> and Controller Editor settings before importing.** See **Known issues / alpha status**
> at the bottom. Feedback welcome.

---

## Contents
1. What you get
2. Requirements
3. Files in this package
4. Installation (Traktor **and** Controller Editor — both are required)
5. Hardware layout (drawing)
6. Pad pages — the Group A–H buttons
7. Stems display pages — the screen knobs & buttons
8. Transport & browser section
9. The Browse knob (Dial)
10. Stem slot reference
11. Known issues / alpha status
12. Credits
13. Version history

---

## 1. What you get
- **2‑deck STEMS control** (Deck A + Deck B): per‑stem volume, mute, and filter, across
  five different on‑screen layouts.
- **8 performance pad pages** on the Group A–H buttons (16 pads each): stems, loops,
  beatjump, a full remix‑deck grid, key/pitch play, loop‑roll, a **VU meter**, and a
  transport page.
- **Transport + browser** on the lower buttons: play, jump‑to‑start, record, deck‑focus
  toggle, beatjump, **load to Deck A / Deck B**, and browser scrolling.
- **Bidirectional browse** on the Dial (jog) plus the arrow buttons.
- **Full FX control** of all 4 Traktor FX units (on/buttons/dry‑wet/knobs) on the
  Group F/G/H display pages.

This mapping targets a **2‑deck workflow** (Deck A / Deck B) for the stems and transport,
and uses **Deck C** for the remix‑cell grid (Group D).

---

## 2. Requirements
- **Native Instruments Maschine MK2** (full RGB) **or Maschine MK1** (see *Maschine MK1* below).
- **NI Controller Editor** (ships with Maschine software) — used to load the `.ncc`
  controller template so the MK2 sends the correct MIDI.
- **Traktor Pro 4** (developed/tested on Traktor Pro 4; stems require Traktor Pro 3 or newer).
- Tracks must be **Stems (.stem.mp4)** files for the stem controls to do anything.

---

## 3. Files in this package
| File | What it is |
|------|------------|
| `GideonSTEM-Maschine.tsi` | The Traktor mapping. Import this in Traktor → Preferences → Controller Manager. |
| `GideonSTEM-Maschine.ncc` | The NI Controller Editor configuration (all NI controllers; the MK2 section is what matters). Load in Controller Editor. |
| `README.md` | This document. |
| `diagrams/layout_guide.png` | Full labeled guide — control map + all 8 pad-page maps. |
| `diagrams/control_map.png` | The MK2 with every control labeled. |
| `diagrams/pad_A.png … pad_H.png` | One labeled map per Group pad page (A–H). |

> **Both files are required.** The `.tsi` tells Traktor what each MIDI message does; the
> `.ncc` tells the Maschine what MIDI to send. One without the other will not work.

---

## 4. Installation

### A. Load the Controller Editor template (`.ncc`)
1. Open **NI Controller Editor**.
2. **File → Open Configuration…** and select `GideonSTEM-Maschine.ncc`.
   *(This is a full configuration; the Maschine MK2 template inside it is "Template 1".)*
3. Make sure the **Maschine MK2** is selected and the template is active. The MK2 should
   now be in **MIDI mode** and send the CC/note layout this mapping expects.

### B. Import the Traktor mapping (`.tsi`)
1. Traktor → **Preferences → Controller Manager**.
2. **Import** → select `GideonSTEM-Maschine.tsi`.
3. This adds **three devices** (all 100% original):
   - `Maschine MK2 Stems` — stem volume/mute/filter, both decks
   - `Maschine MK2 Performance` — pad pages A–H + transport + browser
   - `Maschine MK2 FX` — FX units 1–4 on display pages F/G/H
4. **Assign a MIDI port to each device.** For every device in the dropdown, set
   **In‑Port** and **Out‑Port** to the **Maschine MK2 Virtual Input/Output** (or your
   MK2 MIDI port). LEDs and the VU meter need the **Out‑Port** set.
5. Click **Close**.

### C. First check
- Turn the Maschine on with the mapping loaded — it should boot showing the **Stems Full
  Mix** screen (see §7).
- Load a stem track to Deck A and move the **display knobs** — stem volumes should move.

---

## 5. Hardware layout (drawing)

```
 ┌───────────────────────────────────────────────────────────────────────┐
 │  [Browse]                  ╔═══════════╗ ╔═══════════╗        ( Volume )│
 │  [Sampling]                ║  LEFT     ║ ║  RIGHT    ║        ( Tempo  )│
 │  [ ... ]                   ║  DISPLAY  ║ ║  DISPLAY  ║        ( Swing  )│
 │                            ╚═══════════╝ ╚═══════════╝         ◎ DIAL   │
 │   DISPLAY BUTTONS  [b1][b2][b3][b4][b5][b6][b7][b8]          (jog/enter)│
 │   DISPLAY KNOBS    (k1)(k2)(k3)(k4)(k5)(k6)(k7)(k8)            [Enter]  │
 │                                                                         │
 │   GROUP BUTTONS                       PADS (4 x 4)                       │
 │     [ A ] [ E ]                 ┌────┬────┬────┬────┐  <- top row =      │
 │     [ B ] [ F ]                 │ 13 │ 14 │ 15 │ 16 │     DECK A         │
 │     [ C ] [ G ]                 ├────┼────┼────┼────┤                    │
 │     [ D ] [ H ]                 │  9 │ 10 │ 11 │ 12 │                    │
 │                                 ├────┼────┼────┼────┤                    │
 │   [Restart][Step◄][Step►]       │  5 │  6 │  7 │  8 │  <- bottom rows =  │
 │   [ Grid ][ Play ][ Rec ]       │  1 │  2 │  3 │  4 │     DECK B         │
 │                                 └────┴────┴────┴────┘                    │
 └───────────────────────────────────────────────────────────────────────┘

 Group buttons A–H switch BOTH the 16 pads AND the on‑screen knob/button layout.
 Pads: top two rows (9–16) act on DECK A, bottom two rows (1–8) act on DECK B.
 (On the remix page, all 16 pads form one 4×4 grid on Deck C.)
```

---

## 6. Pad pages — the Group A–H buttons
Pressing a **Group button (A–H)** switches the 16 pads to a new function *and* changes
the on‑screen layout. In every page, the **top 8 pads (9–16) control Deck A** and the
**bottom 8 pads (1–8) control Deck B** (except Remix, which is one Deck‑C grid).

| Group | Page | What the 16 pads do |
|:-----:|------|---------------------|
| **A** | **Stems Pads** | Per deck: 4 stem **mutes** + 4 stem **filter‑on** toggles (Drums/Bass/Other/Vocals). |
| **B** | **Loops** | Per deck: 8 instant **fixed‑size loops** — **1/8, 1/4, 1/2, 1, 2, 4, 8, 16 beats**. |
| **C** | **Beatjump** | Per deck: **−4, +4, −8, +8, −16, +16, −32, +32 beats**. |
| **D** | **Remix grid** | Full **4×4 Remix Deck** trigger grid on **Deck C** (4 slots × 4 cells). |
| **E** | **Pitch / Key** | Per deck: key shift pads **−4 … +3 semitones**, with a **reset‑to‑original‑key** pad (0). |
| **F** | **Loop Roll** | Per deck: 8 fixed‑size **loop rolls** — **1/16 … 8 beats** (1/16 is the fastest). |
| **G** | **VU Meter** | Live **stereo VU of the main output** (left + right bars, 8 levels each). *Output only — see alpha notes.* |
| **H** | **Transport** | Per deck: **Play, Cue, Sync, Flux** (duplicated to fill 8 pads). |

---

## 7. Display pages — the screen knobs & buttons
The **display knobs (k1–k8)** and **display buttons (b1–b8)** under the screens change
with the Group button. On the stems pages (A–E) the order is always **k1=Drums, k2=Bass,
k3=Other, k4=Vocals** (k5–k8 = the same four stems on the **other deck**).

| Shown on | Page | Knobs (k1–k8) | Buttons (b1–b8) |
|:--------:|------|---------------|-----------------|
| **Group A** | **Stems Full Mix** *(default at startup)* | Full‑range **volume** — Deck A (k1–4) + Deck B (k5–8) | **Mute** per stem (LED) |
| **Group B** | **Stems Encoders** | *Top push‑encoders* turn = **volume**; push = **mute** (LED) | — |
| **Group C** | **Stems Mix Ctrl** | **Filter** amount, both decks | **Mute** per stem (LED) |
| **Group D** | **Stems Fine Vol** | **Fine volume**, both decks | **Mute** per stem (LED) |
| **Group E** | **Stems Filter** | **Filter** sweep, both decks | **Filter on/off** per stem (LED) |
| **Group F** | **FX 1 + 2** | k1–4 = FX1 Dry/Wet + Knob1‑3 · k5–8 = FX2 | b1–4 = FX1 On + Btn1‑3 · b5–8 = FX2 |
| **Group G** | **FX 3 + 4** | k1–4 = FX3 Dry/Wet + Knob1‑3 · k5–8 = FX4 | b1–4 = FX3 On + Btn1‑3 · b5–8 = FX4 |
| **Group H** | **FX All** | k1–4 = FX1‑4 Dry/Wet · k5–8 = FX1‑4 Knob1 | b1–4 = FX1‑4 On · b5–8 = FX1‑4 Btn1 |

> **Why Full Mix is first:** the MK2 always boots to the first display page, so Full Mix
> is placed at index 0 to be the default "home" mixer screen.
>
> Note the Group F/G/H **pads** still do Loop‑roll / VU / Transport (§6) — only the
> **screen knobs/buttons** on those groups are FX.

---

## 8. Transport & browser section (lower‑left buttons)

| Control | Action |
|---------|--------|
| **Play** | Play / Pause the **focused** deck. LED lights (green) while playing. |
| **Restart** | Jump to the **start** of the track — works on **both Deck A and Deck B**. |
| **Rec** | Toggle Traktor's **Audio Recorder** (press = start, press = stop). LED = red while recording. **Off at startup.** |
| **Grid** | **Toggle deck focus** (flip A ↔ B). LED lights when **Deck B** is focused. |
| **Step ◄ / Step ►** | Beatjump **−4 / +4 beats** on the focused deck. |
| **Tempo** | **Load** the selected browser track into **Deck A**. |
| **Enter** | **Load** the selected browser track into **Deck B**. |
| **Dial press (Push)** | **Load** into the focused deck. |
| **Master ◄ / Master ►** | Browser scroll **up / down**. |
| **Browse** | Toggle the browser view/layout. |

---

## 9. The Browse knob (Dial)
- **Turn the Dial** → scroll the browser list **both directions**.
- **Press the Dial** → load the selected track into the focused deck.
- The Dial is configured as a **relative (binary‑offset) encoder** in the `.ncc`. If you
  rebuild the controller template from scratch, keep the Dial in this relative mode or it
  will only scroll one way.

---

## 10. Stem slot reference
Traktor stem slots are fixed in this order (matches standard `.stem.mp4` files):

| Knob / pad column | Stem | Traktor slot |
|:-----------------:|------|:------------:|
| 1 | **Drums** | 0 |
| 2 | **Bass** | 1 |
| 3 | **Other** | 2 |
| 4 | **Vocals** | 3 |

---

## 11. Known issues / alpha status
This is an **alpha**. Confirmed working: stems control (all 5 display pages), pad pages,
loops, beatjump, remix grid, pitch/key, loop‑roll, transport, deck focus toggle,
load‑to‑A/B, browser scroll (Dial + arrows), restart, record‑off‑at‑startup.

Still being validated on hardware (output/LED features depend on the Traktor **Out‑Port**
being assigned):
- **Group G VU meter** movement — the metering output signature is in place; confirm it
  tracks audio once the Out‑Port is assigned.
- **Group A–H button colors** — the buttons currently render the Maschine's **native**
  group colors. Custom per‑group colors require a different (modifier‑based) architecture
  that trades away native page switching; not enabled in this build.
- **Grid / Play LEDs** — should follow deck focus and play state; verify on your unit.
- **FX (Group F/G/H)** — the FX layer was rebuilt from scratch for v0.2 (all original);
  confirm the FX On / Dry‑Wet / Knobs / Buttons respond on your unit.

If something doesn't light or move, first re‑check that **every** imported Traktor device
has both an **In‑Port and Out‑Port** assigned to the MK2.

---

## 11b. Maschine MK1
The **same `.tsi` and `.ncc`** also drive the original **Maschine MK1** — load the `.ncc`
in Controller Editor and select your MK1. The MK1 has the same control layout (16 pads,
8 display knobs/buttons, 8 Group buttons), so pad pages A–H, the stems mixer, FX, and
transport (Play, Record, Grid, Loop=restart, Prev./Next=beatjump, Browse) all work.

**MK1 differences (hardware limits):**
- **Monochrome pads** — the MK1 has no RGB, so pad/VU *colors* don't render (the functions
  still work; the Group G meter lights pads on/off rather than in color).
- **No Dial/jog** — the knob-driven browser scroll and the Dial-push load aren't available
  on the MK1, and it has no Enter/Master buttons. Use Traktor's keyboard/other controls to
  scroll/load, or remap a free MK1 button. (MK1 is **alpha** and untested on hardware so far.)

## 12. Credits
**This build is 100% original** — as of v0.2 it contains **no third‑party mapping data**.
It was developed by reverse‑engineering the Traktor `.tsi` format and studying several
community mappings purely as **format references** (to learn command IDs and byte
encodings — facts, not content). Big thanks to those authors; please support them on
DJ TechTools:

- **DJ Reybans** — the Maschine MK2 mapping that originally inspired this project's
  starting point. *(No Reybans code remains in the current build.)*
- **DJ TechTools community** (maps.djtechtools.com) — the mappings below were studied as
  *format references* for command IDs, encodings and LED formats:
  - *"4 Decks Cue/Fx/Stem MK2 full colour"* — command IDs, LED‑output format, browser
    scroll template, deck encoding.
  - *"Maschine MK2 2.6.1"* — fixed loop‑size and beatjump command templates.
  - *"Traktor + Maschine = Love"* — slicer / tone‑play reference.
  - *MF Twister 4‑deck STEMS mapping* ("TW STMS" / "Twisted Gratification") — the stems
    submix encoding (single Focus device, combined deck+slot field).
  - *Maschine Mikro VU* and *LastResortDJs Mikro* — the moving VU‑meter output signature.
  - *"Maschine ONE"* — the relative (binary‑offset) browse‑encoder recipe + deck focus.
  - *"Native Instruments Maschine MK2 Remix Deck"* — browse / remix reference.
  - *SP1 / Kontrol* mapping — the Key Adjust command template.
- **Open‑source references:** `vxio/traktor-tsi-field-guide` and
  `SuperXtremeMapper/super-xtreme-mapper` (the Traktor command‑ID dictionary) on GitHub.
- **Native Instruments** — Controller Editor and the base configuration template.

*(If you are one of the above authors and want different wording or removal of a credit,
please get in touch and it will be corrected.)*

---

## 13. Version history
- **v0.1‑alpha** — first public alpha. Stems (2‑deck) + 8 pad pages + transport + browser
  + VU. Browse knob bidirectional. Full Mix is the default startup screen.
- **v0.1.1‑alpha** — added labeled layout diagrams to the download.
- **v0.2‑alpha** — FX layer rebuilt as an original `Maschine MK2 FX` device (all 4 FX
  units on Group F/G/H); removed the last third‑party device → **100% original**, and
  cleared the CC003/CC087 mapping conflicts.
- **v0.3‑alpha** — **Maschine MK1 support** from the same `.tsi`/`.ncc` (MK1 pad pages
  re‑channeled to match; transport + stems + FX work). MK1 caveats: monochrome pads, no
  Dial. MK1 untested on hardware.
