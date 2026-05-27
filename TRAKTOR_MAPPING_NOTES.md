# Traktor / Controller Mapping — Reusable Build Notes

> ⚠️ **Maintainers: see `HANDOFF.md` for current project state.** This file is good for
> format/TID detail, but **§9b "pad paging = modifiers" is the ABANDONED approach** — the
> shipped build uses **channel-based** paging. HANDOFF.md is the source of truth.

Working knowledge base for building Traktor (and later Serato) controller mappings,
especially Native Instruments Maschine MK2. Built up while fixing the MK2 stems +
A–H performance mapping. Keep updated.

> **Golden rule (learned the hard way):** Do NOT guess Traktor command IDs or field
> encodings. Get GROUND TRUTH — parse a real working mapping, or have the user export
> a 1-control seed from Traktor's GUI and diff it. Local structural validity ≠ Traktor
> acceptance. (Source: vxio/traktor-tsi-field-guide on GitHub.)

---

## 1. File formats

- **.tsi** (Traktor mapping): XML wrapper. Controller binary is base64 in
  `Entry Name="DeviceIO.Config.Controller"`. Big-endian frames: 4-char tag + 4-byte
  length (excludes the 8-byte header) + payload.
- **.ncc** (NI Controller Editor *Configuration*): XML, fully editable. Contains every
  NI controller's templates. This is what we patch.
- **.ncm / .ncm2** (single Controller Editor template): proprietary binary — do NOT
  rely on editing these; work in the .ncc instead.

## 2. TSI binary structure
```
DIOM (root) > DIOI[=1] + DEVS(int nDevices + DEVI[])
DEVI = utf16("Generic MIDI") + DDAT
DDAT = DDIF(int target) + DDIV(ver) + DDIC(device name) + DDPT(ports)
       + DDDC(DDCI + DDCO  = MIDI in/out defs, the DCDT palette)
       + DDCB(CMAS + DCBM) + DVST
CMAS = int count + CMAI[]
CMAI@q: tag,size, bindingId u32(q+8), type u32(q+12) [0=In,1=Out],
        tid u32(q+16), CMAD frame @ q+20 (payload @ q+28)
```
- **DDIF (device target):** 0=Focus, 1=DeckA, 2=DeckB, 3=C, 4=D.
- **MIDI palette (DDCI/DDCO):** full set = 16ch × (128 CC + 128 Note + 1 PitchBend) =
  **4112** entries. (Our generator uses 4096, omitting PitchBend — harmless.)
- **CMAD payload (120 bytes):** ctrlType@4 (0=Button,1=Knob,2=Enc,65535=LED),
  interaction@8 (1=Toggle,2=Hold,3=Direct,4=Rel,5=Inc,6=Dec,7=Reset,8=Output),
  deck/slot@12 (signed), setValueTo@44(float), commentLen@48 then UTF16-BE comment;
  after comment: mod1Id, mod1Val, mod2Id, mod2Val, LED ranges, Resolution(0x3d800000
  knob / 0x1 button). LED-out = ctrlType 65535 + interaction 8.

## 3. Deck / slot targeting (CRITICAL, differs by command family)
- **Normal deck commands** (cue, fx, flux, hotcue, play, loop, beatjump…): CMAD deck
  field = 0=A, 1=B, 2=C, 3=D. Device can be DDIF=Focus(0).
- **Submix / STEM commands** (vol/mute/filter/fx-send): the deck field is an ABSOLUTE
  combined deck+slot value **0–15**: DeckA stems=0-3, DeckB=4-7, DeckC=8-11, DeckD=12-15.
  Use ONE device with DDIF=0 (Focus). Do NOT split into per-deck DDIF devices — that
  conflicts with the absolute field and breaks everything. (This was the stems bug.)

## 4. Verified Traktor command IDs (TIDs)
Source: github SuperXtremeMapper/super-xtreme-mapper → XtremeMapping/Models/TSI/
TraktorCommands.swift (420 commands; saved locally as TraktorCommands.swift).
```
Play/Pause 100   Play 101                 Cue 206   CUP 204   Cue/Set+Store 209
Sync On 125   Beat Sync 126   Tempo Sync 122   Phase Sync 124
Hotcue 1-8 = 214-221   Select/Set+Store 2328   Delete 2331   State 2329
   Hotcue N Type (LED out used by #917) = 2333-2340
Loops: Loop In 200  Loop Out 201  Loop Active On 202  Reloop 203
   Loop Set 2192  Loop Size 2193  Size +1 2194  Size -1 2195  Size Selector 2196
   Loop Active 2316  Size Select+Set 2317  Current Loop Size 2319
Beatjump 2380  Beatjump Forward 2381  Beatjump Backward 2382
   Move 2351  Move Fwd 2352  Move Back 2353  Move Size Selector 2372
Tempo Bend 406  Tempo Bend Stepless 404  Tempo Adjust 123
Key: Reset 401  Adjust 402  Match 403  Keylock On 405
Filter 320  Filter On 319
FX: on 369  dry/wet 365  knob1-3 366/367/368  button1-3 370/371/372
   FX unit deck-select 321(1) 322(2) 338(3) 339(4)
Flux Mode On 2350
Slicer/Freeze: Freeze Mode On 803  Slice Trigger 1-8 = 810-817
Browser: scroll 3200  layout 4209
STEM submix (verified working): Slot Volume 251  Slot Mute 259
   Slot Filter Adjust 249  Slot Filter On 250  Slot FX Send 232  Slot FX On 239
```

## 5. Maschine MK2 .ncc layout
- `<controller type="Maschine Controller MK2">` section.
- `<pages>` → 8 `<page>` = the DISPLAY section (top: encoders, display knobs+buttons).
  Our generator writes these (stems on encoders + perf). Knobs/buttons send CC.
- `<groups>` → 8 `<group name="Pad Page A..H" color-index="N">` = the PAD pages,
  switched by the Group A–H buttons. Each holds 16 `<pad subtype="trigger">` inputs
  (note + channel, gate/ondown) + `<led>` outputs (3 per pad: …B/H/S states) carrying
  `<unit color-type color-mode color-on-index color-off-index>` = the per-pad colors.
- Pad note layout (Reybans original, OVERLAPPING — must re-note for distinct pages):
  A 12-27, B 24-39, C 36-51, D 48-63, E 60-75, F 72-87, G 84-99, H 96-111, all Ch01.
  Plan: re-note non-overlapping A=0-15 … H=112-127 (notes don't clash with CC controls).
- Colors = indexed palette via color-on-index/color-off-index (and group color-index).

## 6. Current working setup (MK2)
- Build script: `build_reybans_stems.py`. Outputs `Reybans_MK2_Stems.tsi` +
  `Reybans_Stems_Performance.ncc`, auto-copied to `F:/`.
- STEMS: WORKING (user-confirmed). One device "Maschine MK2 Stems", DDIF=0, deck/slot
  0-7 (A=0-3,B=4-7), TIDs 251/259/249/250, stems controls on Ch02.
- Performance "bottom": being rebuilt — A–H pad pages = Hotcues / Loops / Beatjump /
  Pitch-Key / FX / Loop-Roll / Slicer / Transport. Volume-only stems on encoders.

## 7. Reference mappings on disk (ground truth, keep)
- `ref_TW_stems_Main_CABD_edit.tsi` — DJTT MF Twister 4-deck STEMS (proved stems
  encoding: 1 Focus device, 0-15 field). 
- #917 "4Decks Cue/Fx/Stem MK2 full colour" — best-commented; source of cue/fx/flux/
  hotcue/transport TIDs + deck encoding + LED-out format.
- #1237 Maschine MK2 2.6.1 — has loops/beat-roll (uncommented).
- #6426 Traktor+Maschine=Love — slicer + tone-play(pitch) (Spanish comments).
- `TraktorCommands.swift` — full TID dictionary.

## 8. How to get a mapping from DJ TechTools (maps.djtechtools.com)
Login is required to download. Account: garry@bcmail.net (password in engram).
Flow (devise): GET my.djtechtools.com/users/sign_in → grab form authenticity_token →
POST login (user[email],user[password],authenticity_token,commit) keeping the session
cookie → GET the mapping page → the download is a POST form `#new_mapping_download` to
`maps.djtechtools.com/mapping_downloads` with `mapping_download[mapping_version_id]` +
that page's authenticity_token. Downloads are ZIPs. (PowerShell Invoke-WebRequest with
-SessionVariable works; raw curl had no connectivity here; `gh api` works for GitHub.)

## 9. Parser snippet (Python, validated)
```python
import re,base64,struct
def blob(path):
    raw=open(path,'rb').read().decode('utf-8','replace')
    return base64.b64decode(re.search(r'DeviceIO\.Config\.Controller"[^>]*Value="([A-Za-z0-9+/=]+)"',raw).group(1))
def u32(d,p): return struct.unpack('>I',d[p:p+4])[0]
def i32(d,p): return struct.unpack('>i',d[p:p+4])[0]
# walk: q=d.find(b'CMAI'); type=u32(q+12); tid=u32(q+16); cmad payload @ q+28
#   ctrlType=u32(c+4) interaction=u32(c+8) deck=i32(c+12) commentLen=u32(c+48)
```

## 9b. Pad pages, COLORS & fixed-size loops (A–H build learnings)

### Colors — where they live
- **Color is NOT in the .tsi.** The TSI only carries the command + LED on/off MIDI ranges.
  The actual pad COLOR is 100% a Controller Editor thing.
- **.ncm2 files ARE XML** (not binary — they start `<?xml`). Readable. They contain the
  color data as `<unit color-type="1" color-mode="M" color-on-index="N" color-off-index="O"/>`.
- **No file contains a palette legend.** Files store color *indices*; the index→actual-color
  map lives in the Controller Editor app/firmware (NI's own forum: indexed mode "does not
  match the manual"). To learn actual colors: (a) read a mapping's template IMAGE (e.g.
  #1237 ships TemplateMk2MASCHINE.jpg), or (b) calibrate on hardware (paint pads with
  indices 1..16, look at the unit).
- **color-mode matters A LOT:** `color-mode="0"` renders everything BLUE (it's a fixed/1-color
  mode — index does not set hue). **`color-mode="1"` gives real distinct hues.** #917/#1237 use 1/2.
- **VERIFIED mode-1 palette (read off MK2 hardware):**
  `color-on-index` 1=red, 2=orange, 3=yellow, 4=green, 5=cyan, 6=blue, 7=purple, 8=pink (rainbow).
  So to set a pad/button to a specific colour: `color-mode="1"` + the index above.
  (Group A-H buttons use mode 1, indices 1-8 = full rainbow, A=red..H=pink.)
- Our .ncc attribute order: `color-type color-mode color-on-index color-off-index`.
  #917/#1237 order differs (alphabetical) — match the actual order when regexing.
- #1237 template-image group colors (visual ground truth): A=purple B=green C=orange
  D=blue E=pink F=yellow G=cyan H=mint.
- Deck-distinct colors: set top pads (Pad9-16=Deck A) and bottom (Pad1-8=Deck B) to
  different color-on/off-index. We used Deck A=idx11, Deck B=idx2 (both render as real
  colors; confirm exact hue on hardware).

### NCC pad-page editing gotchas
- The .ncc has MANY `<controller type="...">` sections (MK1, MK2, MK3, Mikro, Jam, Komplete
  Kontrol...). Several reuse `<group name="Pad Page A..H">`. **ALWAYS scope a find() to the
  MK2 section** (`content.find('<controller type="Maschine Controller MK2">')`) or you patch
  the wrong controller. (This bit us — colors silently went to the MK1 page.)
- MK2 pad pages = `<groups>` → `<group name="Pad Page A..H" [color-index=N]>`; each has 16
  `<pad subtype="trigger">` (note,channel,gate/ondown) + per-pad `<led>` ×3 (id PadNB/H/S on
  channels 2/0/1) carrying the color `<unit>`.
- **Do NOT page the pads by re-channeling them across Ch03-Ch10.** A Group button can't both
  send MIDI (for Traktor) AND switch the hardware pad page, so re-channeled notes never reach
  Traktor. This was the fundamental flaw that broke 7 of 8 pad pages. Use modifiers (below).

### 9b. Pad paging = Traktor MODIFIERS, on ONE channel (verified vs DJTT #917)
Real working MK2 mappings keep all 16 pads on ONE channel/note set and page them with a
Traktor modifier — #917 = 1 Focus device, 563 mappings, 558 modifier-gated.
- **Modifier command TID = 2547 + N** (Modifier #1 = 2548 … #8 = 2555).
- **Group button → SET modifier:** CMAI TID = 2548 (Mod#1); CMAD = Button(0)/Direct(3); the
  target value is an **INT at offset 44**; conditions zeroed. Make the NCC group button `gate`
  so each press sets the page. (Radio-button paging: A→0, B→1, … H→7.)
- **Each pad command → GATE by modifier:** in the CMAD (commentLen=0 ⇒ condition at offset 52):
  `@52 ModId (2548)`, `@56 cmp (0=equals)`, `@60 Val (page index)`; `@64/@68/@72` = 2nd slot.
  Helper: `_gate(cmad, val)` writes those 3 words. Works on every 120-byte CMAD we build.
- **Modifiers are PER-DEVICE.** Keep the group setters AND the gated pads in the SAME Traktor
  device, so its Mod#1 is self-contained and doesn't clash with the kept Reybans device's
  Mod#1-#6 (which it uses for its own FX paging).
- Clean 120-byte setter template (patch INT @44): see `_SETMOD_TEMPLATE` in build script.

### 9c. Pad LED color — color-mode matters
- `color-mode="0"` ⇒ MK2 forces **fixed blue** regardless of index (this was the "all blue"
  bug — the patch had only changed the color index, never the mode).
- `color-mode="1"` ⇒ real hue palette (verified on Group buttons): 1=red 2=orange 3=yellow
  4=green 5=cyan 6=blue 7=purple 8=pink. Set on==off index for a static page hue.
- #917 uses `color-mode="2"` for pads (off/on state colors); mode 1 is right for fixed hues.
- Group A-H button CCs (this Reybans .ncc): A=80 B=81 C=82 D=83 E=91 F=92 G=93 H=94 (Ch01).
  Pads: PadN = note 11+N → notes 12-27 (Pad1-8 = bottom = Deck B; Pad9-16 = top = Deck A).

### Fixed-size loops (the intuitive pad layout)
- Use **TID 2317 "Loop Size Select+Set", interaction=Direct(3)**. The loop SIZE is an INTEGER
  index at **CMAD offset 44** (the field normally read as SetValueTo float — here it's an int):
  `0=1/32 1=1/16 2=1/8 3=1/4 4=1/2 5=1 6=2 7=4 8=8 9=16 10=32` beats. Selector range fields
  at offset 80 (=0xffffffff) and 88 (=0x0a=10) are specific to this command — **clone the
  whole 120-byte CMAD from a working map (#1237) and patch only offset 12 (deck) + 44 (size)**.
- Don't use "Loop Size +1/-1" (2194/2195) as standalone pads — they only resize an ALREADY
  ACTIVE loop, so they look dead otherwise.

### 9d. VU / level meters (why a meter shows "no movement")
Level-meter command TIDs (Output only): **2704/2705 = Main Level L/R**, 2688-2703 = deck
pre/post-fader L/R, 2706-2714 = booth/monitor/mic/FX levels.
- A meter LED-output CMAD is NOT the same as a button on/off LED output. The "moving meter"
  signature (verified from working Maschine VU #10371): **CtrlType=65535, Inter=8(Output),
  @40=2, range-type fields (u20/u22/u29)=2, LedBlend=1 (fade), Resolution=0x3d800000 (0.0625
  float).** A button LED uses Blend=0 + Reso=0x00000001 ("Switch") + range-type=1 → Traktor
  treats it as binary on/off ⇒ **no movement**. That was our VU bug.
- Each bar segment = one output mapping with its own band: **MinCtrl@80 = lower edge,
  MaxCtrl@88 = upper edge** (e.g. segment k of 8 = [(k-1)/8, k/8]); MinMidi=0/MaxMidi=127.
  Cumulative fill = each segment fades in across its band and clamps full above.
- #10371 drives color via two mappings per pad: PadNH (Ch01) gets a FIXED velocity = color
  code (40/12/127 = Maschine pad colors), PadNB (Ch03) gets proportional 0-127 = brightness.
  Our simpler approach: one output per pad on Ch01 (PadNH) + NCC `color-mode=1` static hue
  (on=hue, off=0) so the pad lights its preset color as the level crosses its band.
- Template: see `_VU_TEMPLATE` in build script (cloned from #10371, patch only @80/@88).

## 10. For SERATO (future)
Serato uses a different mapping system (no .tsi). Serato MIDI mappings are stored in
its own format; the MIDI side (what the Maschine sends via Controller Editor .ncc) is
REUSABLE — same pad notes / CC layout. So: keep the .ncc pad/encoder layout, and build
the Serato side separately (Serato MIDI learn / its config). Investigate Serato's
mapping file format when starting that project; reuse sections 5 + the .ncc here.
