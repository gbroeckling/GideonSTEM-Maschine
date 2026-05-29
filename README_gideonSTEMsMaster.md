# GideonSTEM-Maschine — Traktor Pro mapping for Native Instruments Maschine MK2

**A full Traktor Pro STEMS + performance mapping for the Maschine MK2, turning the
controller into a 2-deck stems mixer, a 24-page performance pad surface (loops, beatjump,
remix, key, tone-play, loop-roll, drum Pattern Player, FX), a transport + browser
controller, and a 4-unit FX command surface — all from a single Python build.**

> ## ⚠️ ALPHA RELEASE — read this first
> This mapping is **alpha**. It is in active testing on real hardware. The core
> functions below are confirmed working, but some features (notably the **FX-select
> pads** — see Known Issues) and most LED/VU outputs are still being validated, and
> behaviour may change between versions. **Back up your existing Traktor and Controller
> Editor settings before importing.** Feedback welcome.

---

## Contents
1. What you get
2. Requirements
3. Files in this package
4. Installation (Traktor **and** Controller Editor — both are required)
5. Hardware layout (drawing)
6. **The layer system — Scene & Pattern buttons** *(new in v0.4)*
7. Pad pages — **Base layer** (Group A–H)
8. Pad pages — **Scene layer** (A2–H2)
9. Pad pages — **Pattern layer** (A3–H3, drum Pattern Player)
10. Display pages — the screen knobs & buttons
11. Transport, layer & utility buttons
12. The Browse knob (Dial)
13. Stem slot reference
14. Known issues / alpha status
15. Maschine MK1
16. Credits
17. Version history

---

## 1. What you get
- **2-deck STEMS control** (Deck A + Deck B): per-stem volume, mute, and filter, across
  five different on-screen layouts.
- **24 performance pad pages** — the 8 Group buttons (A–H) × **3 layers** (Base, Scene,
  Pattern). 16 pads each. Stems, loops, beatjump, a full remix grid, key/pitch, tone-play,
  loop-roll, phrase-jump, loop recorder, an FX selector, transport for all four decks, and
  a complete **drum Pattern Player** on FX3/FX4.
- **8 screen pages** — the display knobs/buttons under the screens change with the Group:
  five stems layouts (volume / encoders / mix / fine / filter) and three FX layouts (FX1+2,
  FX3+4, all four units).
- **Full FX control** of all 4 Traktor FX units (on, buttons, dry/wet, knobs).
- **Transport + browser**: play, jump-to-start, record, deck-focus toggle, beatjump,
  load-to-A/B, browser scroll, plus **Scene / Pattern / Solo / Mute / Volume** utility keys.
- **Bidirectional browse** on the Dial (jog) plus the arrow buttons.

This mapping targets a **2-deck workflow** (Deck A / Deck B) for stems and transport, uses
**Deck C** for the remix grid (Group D) and loop-station recall, and uses **FX Units 3 & 4**
as the two voices of the drum Pattern Player (Pattern layer).

---

## 2. Requirements
- **Native Instruments Maschine MK2** (full RGB) **or Maschine MK1** (see *Maschine MK1* below).
- **NI Controller Editor** (ships with Maschine software) — loads the `.ncc` controller
  template so the MK2 sends the correct MIDI.
- **Traktor Pro 4** (developed/tested on Traktor Pro 4; stems require Traktor Pro 3 or newer;
  the drum **Pattern Player** requires Traktor Pro 4).
- Tracks must be **Stems (.stem.mp4)** files for the stem controls to do anything.

---

## 3. Files in this package
| File | What it is |
|------|------------|
| `GideonSTEM-Maschine.tsi` | The Traktor mapping. Import in Traktor → Preferences → Controller Manager. |
| `GideonSTEM-Maschine.ncc` | The NI Controller Editor configuration. Load in Controller Editor. |
| `README.md` | This document. |
| `TID_catalog_public.xlsx` | A sanitized reference of the Traktor command IDs (TIDs) this mapping uses — control type, interaction, value ranges, hardware-test status. Facts only; no third-party content. |
| `diagrams/control_map.png` | The MK2 with every control labeled. |
| `diagrams/layout_guide.png` | **Everything in one image** — control map + all 24 pad pages (3 layers) + all 8 screen pages. |
| `diagrams/cheatsheet_base.png` | The 8 Base-layer pad maps. |
| `diagrams/cheatsheet_scene.png` | The 8 Scene-layer pad maps. |
| `diagrams/cheatsheet_pattern.png` | The 8 Pattern-layer pad maps. |
| `diagrams/cheatsheet_screens.png` | The 8 display (knob/button) maps. |
| `diagrams/pad_A.png … pad_H.png` | Base-layer pad maps, one per Group. |
| `diagrams/pad_A2.png … pad_H2.png` | Scene-layer pad maps. |
| `diagrams/pad_A3.png … pad_H3.png` | Pattern-layer pad maps. |
| `diagrams/screen_A.png … screen_H.png` | The screen (knob/button) map per Group. |

> **Both controller files are required.** The `.tsi` tells Traktor what each MIDI message
> does; the `.ncc` tells the Maschine what MIDI to send. One without the other will not work.

---

## 4. Installation

### A. Load the Controller Editor template (`.ncc`)
1. Open **NI Controller Editor**.
2. **File → Open Configuration…** and select `GideonSTEM-Maschine.ncc`.
3. Make sure the **Maschine MK2** is selected and the template is active. The MK2 should
   now be in **MIDI mode** and send the CC/note layout this mapping expects.

### B. Import the Traktor mapping (`.tsi`)
1. Traktor → **Preferences → Controller Manager**.
2. **Import** → select `GideonSTEM-Maschine.tsi`.
3. This adds **three devices** (all 100% original):
   - `Maschine MK2 Stems` — stem volume/mute/filter, both decks
   - `Maschine MK2 Performance` — the 24 pad pages + transport + browser + utility keys
   - `Maschine MK2 FX` — FX units 1–4 on the screen pages
4. **Assign a MIDI port to each device.** For every device, set **In-Port** and **Out-Port**
   to the **Maschine MK2 Virtual Input/Output** (or your MK2 MIDI port). LEDs need the Out-Port.
5. Click **Close**.

### C. FX Pre-Selection (needed for the FX-select pads, Group G)
The Group G pads load effects by **position in your Traktor FX Pre-Selection list**. The
labels in the diagrams assume Traktor's **default Effect-Selector order**. If you have
reordered your FX Pre-Selection list, the Group G pads will load whatever sits at those
positions instead. *(See Known Issues — the FX-select pads are not working reliably yet.)*

### D. First check
- Boot the Maschine with the mapping loaded — it should show the **Stems Full Mix** screen.
- Load a stem track to Deck A and move the **display knobs** — stem volumes should move.

---

## 5. Hardware layout (drawing)

```
 ┌───────────────────────────────────────────────────────────────────────┐
 │  [Browse]                  ╔═══════════╗ ╔═══════════╗        ( Volume )│
 │  [Sampling]                ║  LEFT     ║ ║  RIGHT    ║        ( Tempo  )│
 │                            ║  DISPLAY  ║ ║  DISPLAY  ║        ( Swing  )│
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
 │   [Scene][Pattern][Solo]        └────┴────┴────┴────┘                    │
 │   [Mute][Volume][Note Repeat]                                           │
 └───────────────────────────────────────────────────────────────────────┘

 Group A–H pick the PAGE.  Scene / Pattern pick the LAYER (see §6).
 Pads: top two rows (9–16) = DECK A, bottom two rows (1–8) = DECK B.
 (Remix & FX-selector pages use all 16 pads as one block — see each page.)
```

---

## 6. The layer system — Scene & Pattern buttons *(new in v0.4)*

Each Group button (A–H) now has **three layers**, selected by the **Scene** and **Pattern**
buttons. This triples the pad surface from 8 pages to **24**.

| Layer | How to reach it | Pages |
|-------|-----------------|-------|
| **Base** | Scene **off**, Pattern **off** | A – H |
| **Scene** | Press **Scene** (light on) | A2 – H2 |
| **Pattern** | Press **Pattern** (light on) | A3 – H3 |

- The layers are **mutually exclusive** — only one is active at a time.
- The Group button still picks **which** page within the active layer, and it still changes
  the on-screen layout (the screen pages, §10, are shared across all three layers).
- The **Pattern** layer is a complete **drum Pattern Player** built on **FX Units 3 & 4**
  (load a Pattern Player effect into FX3 and FX4 first). Pressing Pattern also **auto-arms**
  the drum bus: it routes Deck D into FX3/FX4 and switches both units on, so the drums are
  audible as soon as you trigger a pattern.

---

## 7. Pad pages — Base layer (Group A–H)
Top 8 pads (9–16) = **Deck A**, bottom 8 (1–8) = **Deck B**, except where noted.

| Group | Page | What the 16 pads do |
|:-----:|------|---------------------|
| **A** | **Stems Pads** | Per deck: 4 stem **mutes** + 4 stem **filter-on** toggles (Drums/Bass/Other/Vocals). |
| **B** | **Loops** | Per deck: 8 instant **fixed-size loops** — 1/8, 1/4, 1/2, 1, 2, 4, 8, 16 beats. |
| **C** | **Beatjump** | Per deck: −4, +4, −8, +8, −16, +16, −32, +32 beats. |
| **D** | **Remix grid** | Full **4×4 Remix Deck** trigger grid on **Deck C** (slots 1–4 × cells 1–4). One block, not split by deck. |
| **E** | **Pitch / Key** | Per deck: key shift −4 … +3 semitones, with a **reset-to-original-key** pad (0). |
| **F** | **Loop Station** | Pads 1–4 = **silent Capture** of Deck A/B/C/D's current loop into the remix deck; pads 5–16 = **recall** 12 captured cells (Deck C). Capture is silent — nothing jumps or plays while you set it up. |
| **G** | **FX1 Select** | 16 effects loaded into **FX Unit 1**; the wet swells while the pad is held and returns to dry on release. *(Alpha: not working reliably yet — see Known Issues.)* |
| **H** | **Transport** | Per deck: **Play, Cue, Sync, Flux** (duplicated to fill 8 pads). |

---

## 8. Pad pages — Scene layer (A2–H2)
Reached with the **Scene** light on. Same Group buttons, different jobs.

| Group | Page | What the 16 pads do |
|:-----:|------|---------------------|
| **A2** | **Stem FX Send** | Per deck: 4 pads route the deck to **FX1/FX2/FX3/FX4**; 4 pads toggle the per-stem **FX send** (Drums/Bass/Other/Vocals). |
| **B2** | **Loop Roll** | Per deck: 8 momentary **loop rolls** — 1/16, 1/8, 1/4, 1/2, 1, 2, 4, 8 beats. |
| **C2** | **Phrase Jump** | Per deck: big jumps — ±16, ±32, ±64, ±128 beats. |
| **D2** | **Remix grid 5–8** | Deck C remix cells **5–8** per slot — extends the page-D grid. |
| **E2** | **Tone Play** | Per deck: play one stem chromatically — RESET (0) + 1 … +7 semitones. (Mute the other stems on page A to play one melodically.) |
| **F2** | **Loop Recorder** | Traktor's global Loop Recorder — **Rec/Play, Size −, Size +, Undo**, repeated on all four rows for two-hand reach. *(Experimental.)* |
| **G2** | **FX1 Select (hard)** | Same 16 effects as Group G, with harder/wetter parameter settings. *(Alpha: see Known Issues.)* |
| **H2** | **Transport C/D** | Play/Cue/Sync/Flux for **Deck C** (top) and **Deck D** (bottom). |

---

## 9. Pad pages — Pattern layer (A3–H3, drum Pattern Player)
Reached with the **Pattern** light on. This layer drives a two-voice drum Pattern Player on
**FX Unit 3** and **FX Unit 4** (load a Pattern Player into each first). Pressing Pattern
auto-routes Deck D into FX3/FX4 and turns both on.

| Group | Page | What the 16 pads do |
|:-----:|------|---------------------|
| **A3** | **FX3 Control Room** | Voice 1 (FX3): On · Play/Mute · Next/Prev Sample · patterns 1/3/5/7 · volume 25/50/75/100% · pitch −12/0/+7/+12. |
| **B3** | **FX4 Control Room** | Voice 2 (FX4): same 16-pad layout as A3, for FX4. |
| **C3** | **Drum Mixer** | Route Deck A/B/C/D → FX3 and → FX4 · FX3/FX4 Play & On · FX3/FX4 volume low/high. |
| **D3** | **Tone-Play Drums** | Play the drum voices chromatically — FX3 pitch +0…+7 (bottom), FX4 pitch +0…+7 (top). |
| **E3** | **Sound Design** | Per voice: Next/Prev sample, reset pitch, Play/Mute, and a 4-step **Decay** sweep (min → max). |
| **F3** | **Gate & Volume** | Per voice: two momentary **mute-gate** pads (stutter the drums), Play, reset pitch, and a 4-step **volume** ramp (duck → full). |
| **G3** | **Macros** | One-tap combos across both voices: **DROP** (mute both), **BUILD** (busy pattern), **FILL** (max pattern), **CLEAR** (pattern 1 + reset pitch); FX3/FX4 quick patterns; FX3/FX4 play + volume-full. |
| **H3** | **Pattern Picker** | FX3 patterns 1–8 (bottom), FX4 patterns 1–8 (top). Patterns run **sparse → busy**, so stepping up the pads intensifies the groove. |

---

## 10. Display pages — the screen knobs & buttons
The **display knobs (k1–k8)** and **buttons (b1–b8)** change with the Group button. On the
stems pages (A–E) the order is always **k1=Drums, k2=Bass, k3=Other, k4=Vocals** (k5–k8 =
the same four stems on the **other deck**). The screen layout is the same in all three
layers — only the pads change when you switch Scene/Pattern.

| Shown on | Page | Knobs (k1–k8) | Buttons (b1–b8) |
|:--------:|------|---------------|-----------------|
| **A** | **Stems Full Mix** *(boot screen)* | Full-range **volume** — Deck A (k1–4) + Deck B (k5–8) | **Mute** per stem (LED) |
| **B** | **Stems Encoders** | Top push-encoders turn = **volume**; push = **mute** | — |
| **C** | **Stems Mix Ctrl** | **Filter** amount, both decks | **Mute** per stem (LED) |
| **D** | **Stems Fine Vol** | **Fine volume**, both decks | **Mute** per stem (LED) |
| **E** | **Stems Filter** | **Filter** sweep, both decks | **Filter on/off** per stem (LED) |
| **F** | **FX 1 + 2** | k1–4 = FX1 Dry/Wet + Knob1-3 · k5–8 = FX2 | b1–4 = FX1 On + Btn1-3 · b5–8 = FX2 |
| **G** | **FX 3 + 4** | k1–4 = FX3 Dry/Wet + Knob1-3 · k5–8 = FX4 | b1–4 = FX3 On + Btn1-3 · b5–8 = FX4 |
| **H** | **FX All** | k1–4 = FX1-4 Dry/Wet · k5–8 = FX1-4 Knob1 | b1–4 = FX1-4 On · b5–8 = FX1-4 Btn1 |

> **Why Full Mix is first:** the MK2 always boots to the first display page, so Full Mix is
> placed at index 0 to be the default "home" mixer screen.

---

## 11. Transport, layer & utility buttons (lower buttons)

| Control | Action |
|---------|--------|
| **Play** | Play / Pause the **focused** deck. LED green while the focused deck plays. |
| **Restart** | Jump to the **start** of the track — fires on **both Deck A and Deck B**. |
| **Rec** | Toggle Traktor's **Audio Recorder** (press = start, press = stop). LED red while recording. Off at startup. |
| **Grid** | **Toggle deck focus** (flip A ↔ B). LED follows focus. |
| **Step ◄ / Step ►** | Beatjump −4 / +4 beats on the focused deck. |
| **Scene** | Engage the **Scene layer** (pages A2–H2). Press again to return to Base. |
| **Pattern** | Engage the **Pattern layer** (pages A3–H3) and auto-arm the FX3/FX4 drum bus. |
| **Solo** | **FX1 engage** — routes Deck A + B into FX1 and switches FX1 on (the arm for the Group G FX-select pads). |
| **Mute** | Toggle-mute **all stem slots** of decks A–D at once (level-preserving). LED follows mute state. |
| **Volume** | **Volume mode** — while latched, the **Dial** drives the focused deck's channel volume. |
| **Note Repeat** | Toggle **Cruise / Auto-DJ**. |
| **Tempo** | **Load** the selected browser track into **Deck A**. |
| **Enter** | **Load** the selected browser track into **Deck B**. |
| **Dial press (Push)** | **Load** into the focused deck. |
| **Master ◄ / Master ►** | Browser **tree** select (navigate folders). |
| **Browse** | Toggle the browser view/layout. |

---

## 12. The Browse knob (Dial)
- **Turn the Dial** → scroll the browser list **both directions** (when not in Volume mode).
- **Press the Dial** → load the selected track into the focused deck.
- On the **Pattern** layer the Dial drives **Deck D** channel volume; with **Volume mode**
  latched it drives the **focused** deck's volume.
- The Dial is a **relative (binary-offset) encoder** in the `.ncc`. If you rebuild the
  controller template from scratch, keep it in this relative mode or it will only scroll one way.

---

## 13. Stem slot reference
Traktor stem slots are fixed in this order (matches standard `.stem.mp4` files):

| Knob / pad column | Stem | Traktor slot |
|:-----------------:|------|:------------:|
| 1 | **Drums** | 0 |
| 2 | **Bass** | 1 |
| 3 | **Other** | 2 |
| 4 | **Vocals** | 3 |

---

## 14. Known issues / alpha status
This is an **alpha**. **Confirmed working on hardware:** stems control (all 5 display pages),
the base pad pages (stems, loops, beatjump, remix, pitch/key, transport), the Scene-layer
loop-roll and tone-play, the Pattern-layer drum routing, deck-focus toggle, load-to-A/B,
browser scroll (Dial + arrows), restart, mute-all, and record-off-at-startup.

**Not working yet / still being validated:**

- **FX-select pads (Group G / G2) — NOT working yet.** Pressing a Group G pad is meant to
  load the effect into FX Unit 1, switch it on, route it to the decks, and swell the wet.
  In the current build the effect-select and on/route do not fire reliably together — this
  is the top item being fixed. The **Solo** button (FX1 engage) and the **FX screen pages**
  (Group F/G/H, §10) are the working way to drive FX for now. *(Fix in progress.)*
- **Drum Pattern Player (A3–H3)** — routing is in place and the drums should be audible once
  a Pattern Player is loaded into FX3/FX4; the per-pad pattern/volume/pitch values are built
  from the verified FX-unit controls but want a full hardware pass.
- **Loop Recorder (F2)** — experimental; the transport TIDs are sparsely documented.
- **Group A–H button colors** — the buttons render the Maschine's **native** group colors.
  Custom per-group colors require a different architecture that trades away native page
  switching; not enabled in this build.
- **Grid / Play LEDs and metering outputs** — should follow focus / play / level; verify on
  your unit. Output features need the Traktor **Out-Port** assigned.

If something doesn't light or move, first re-check that **every** imported Traktor device has
both an **In-Port and Out-Port** assigned to the MK2.

---

## 15. Maschine MK1
The **same `.tsi` and `.ncc`** also drive the original **Maschine MK1** — load the `.ncc` in
Controller Editor and select your MK1. The MK1 has the same control layout (16 pads, 8
display knobs/buttons, 8 Group buttons), so the pad pages, stems mixer, FX, and transport
all work.

**MK1 differences (hardware limits):**
- **Monochrome pads** — no RGB, so pad colors don't render (the functions still work).
- **No Dial/jog** — knob-driven browser scroll and Dial-push load aren't available, and there
  is no Enter/Master button. Use Traktor's keyboard/other controls to scroll/load, or remap a
  free MK1 button. (MK1 is **alpha** and untested on hardware so far.)

---

## 16. Credits
**This build is 100% original** — it contains **no third-party mapping data**. It was
developed by reverse-engineering the Traktor `.tsi` format and studying several community
mappings purely as **format references** (to learn command IDs and byte encodings — facts,
not content). Big thanks to those authors; please support them on DJ TechTools:

- **DJ Reybans** — the Maschine MK2 mapping that originally inspired this project's starting
  point. *(No Reybans code remains in the current build.)*
- **DJ TechTools community** (maps.djtechtools.com) — mappings studied as *format references*
  for command IDs, encodings and LED formats:
  - *"4 Decks Cue/Fx/Stem MK2 full colour"* — command IDs, LED-output format, browser scroll
    template, deck encoding.
  - *"Maschine MK2 2.6.1"* — fixed loop-size and beatjump command templates.
  - *"Traktor + Maschine = Love"* — slicer / tone-play reference.
  - *MF Twister 4-deck STEMS mapping* ("TW STMS" / "Twisted Gratification") — the stems submix
    encoding (single Focus device, combined deck+slot field).
  - *Maschine Mikro VU* and *LastResortDJs Mikro* — metering-output signature.
  - *"Maschine ONE"* — the relative (binary-offset) browse-encoder recipe + deck focus.
  - *"Native Instruments Maschine MK2 Remix Deck"* — browse / remix reference.
  - *SP1 / Kontrol* mapping — the Key Adjust command template.
  - *Xone:K2* and *Kontrol S4 "Instant JogFX"* — FX float-parameter encoding.
- **Open-source references:** `vxio/traktor-tsi-field-guide` and
  `SuperXtremeMapper/super-xtreme-mapper` (the Traktor command-ID dictionary) on GitHub.
- **Native Instruments** — Controller Editor and the base configuration template.

*(If you are one of the above authors and want different wording or removal of a credit,
please get in touch and it will be corrected.)*

---

## 17. Version history
- **v0.1-alpha** — first public alpha. Stems (2-deck) + 8 pad pages + transport + browser +
  VU. Browse knob bidirectional. Full Mix is the default startup screen.
- **v0.1.1-alpha** — added labeled layout diagrams to the download.
- **v0.2-alpha** — FX layer rebuilt as an original `Maschine MK2 FX` device (all 4 FX units
  on the screen pages); removed the last third-party device → **100% original**, and cleared
  the CC003/CC087 mapping conflicts.
- **v0.3-alpha** — **Maschine MK1 support** from the same `.tsi`/`.ncc`.
- **v0.4-alpha** — **the big layer update.** Adds the **Scene** and **Pattern** layers,
  taking the pad surface from 8 pages to **24** (3 layers × 8 groups):
  - **Scene layer (A2–H2):** stem FX-send + deck→FX routing, loop-roll, phrase-jump, remix
    cells 5–8, chromatic tone-play, the global Loop Recorder, a second (harder) FX bank, and
    transport for Decks C/D.
  - **Pattern layer (A3–H3):** a full two-voice **drum Pattern Player** on FX3/FX4 — control
    rooms, drum mixer/routing, tone-play, sound design, gate & volume, one-tap macros, and a
    sparse→busy pattern picker.
  - New **utility keys:** Scene, Pattern, Solo (FX1 engage), Mute-all-stems, Volume mode,
    Note Repeat (Cruise/Auto-DJ).
  - Group **F** is now a silent **Loop Station** (capture + recall); Group **G** is an **FX1
    selector** (replaces the old VU page).
  - Rebuilt, layer-aware **diagrams** (control map, 24 pad maps, 8 screen maps, per-layer
    cheatsheets) and a sanitized **TID reference** spreadsheet.
  - **Known alpha gap:** the Group G FX-select pads are not firing reliably yet (fix in progress).
