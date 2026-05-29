"""
build_reybans_stems.py  (v4)

Merges DJ Reybans Maschine MK2 mapping with comprehensive Stems control.

HARDWARE LAYOUT (Maschine MK2 default MIDI, Ch01):
  Page B — Top 8 push-encoders:
    Turn  CC22-29   (knobs 1-8, L-R)
    Push  CC54-61   (same 8 knobs pushed)
  Page A — Display section (switches with Group A-H):
    Display knobs    CC14-21
    Display buttons  CC46-53

STEMS PAGES (knob1=Drums, knob2=Bass, knob3=Other, knob4=Vocals):
  Page A  "Stems Filter"    Display knobs CC14-21  = filter amount  A+B
                            Display btns  CC46-53  = filter on/off  A+B  [LED out]
  Page B  "Stems Encoders"  Enc turns     CC22-29  = volume         A+B
                            Enc pushes    CC54-61  = mute           A+B  [LED out]
  Page C  "Stems Mix Ctrl"  Display knobs CC62-69  = filter amount  A+B
                            Display btns  CC70-77  = mute           A+B  [LED out]
  Page D  "Stems Fine Vol"  Display knobs CC91-98  = volume (fine)  A+B
                            Display btns  CC99-102 = mute Deck A    [LED out]
                                          CC120-123= mute Deck B    [LED out]
  Page E  "Stems Full Mix"  Display knobs CC78-81  = volume Deck A
                                          CC82-84,103 = volume Deck B
                            Display btns  CC99-102 = mute Deck A    [LED out, shared D]
                                          CC120-123= mute Deck B    [LED out, shared D]

STEM LABELS (standard slot order: slot 0=Drums, 1=Bass, 2=Other, 3=Vocals):
  Knob 1 = Drums   (Traktor stem slot 0)
  Knob 2 = Bass    (Traktor stem slot 1)
  Knob 3 = Other   (Traktor stem slot 2)
  Knob 4 = Vocals  (Traktor stem slot 3)

DECK / SLOT (verified against working DJTT MF Twister 4-deck stems mapping):
  ONE stems device, DDIF=0 (Focus). Deck AND slot are encoded together in the CMAD
  deck field as 0-15: Deck A stems = 0-3, Deck B stems = 4-7 (C=8-11, D=12-15).
  After importing TSI, assign all 3 devices a port in Traktor Controller Manager.

TRAKTOR TIDs (Stem Slot controls):
  249 = Slot Filter Amount    250 = Slot Filter On/Off
  251 = Slot Volume           259 = Slot Mute
  232 = Slot FX Send Amount   239 = Slot FX On/Off  (NOT USED — no FX in stems pages)

CC RANGES USED (MIDI Ch02 — free from performance and hardware conflicts):
  Stems pages A-E send Ch02 CCs. Traktor stems devices listen on Ch02.
  MK2 hardware controls (GroupA-H = CC80-94, transport = CC98-119) send Ch01 only.
  Performance Device 1 listens on Ch01 only. Zero overlap possible.
  14-29, 46-61  (pages A+B)
  62-77         (page C: filter + mute)
  78-84, 103    (page E vol)
  91-98         (page D fine vol)
  99-103, 120-123 (page D+E mute)
"""

import struct, base64, re, shutil, os

REYBANS_TSI = "Reybans_Maschine_MK2_reference.tsi"   # upstream source we derive device blobs from
INPUT_NCC   = "gideonSTEMsMaster.ncc"
OUTPUT_TSI  = "gideonSTEMsMaster.tsi"
OUTPUT_NCC  = "gideonSTEMsMaster.ncc"   # patched in place

# Stems use MIDI Ch02 in both NCC (ch=1) and TSI labels ("Ch02.CC.XXX").
# Device 1 (performance) uses Ch01 from the original Reybans TSI.
# No CC stripping or remapping needed — different channels = zero overlap.


# ---------------------------------------------------------------------------
# Binary helpers
# ---------------------------------------------------------------------------

def utf16be_str(s):
    return struct.pack('>I', len(s)) + s.encode('utf-16-be')

def frame(tag, payload):
    return tag.encode() + struct.pack('>I', len(payload)) + payload

def read_utf16(d, p):
    n = struct.unpack('>I', d[p:p+4])[0]
    s = d[p+4:p+4+n*2].decode('utf-16-be', errors='replace')
    return s, p+4+n*2


# ---------------------------------------------------------------------------
# Full 4096-entry MIDI palette (required by Traktor)
# ---------------------------------------------------------------------------

_NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

def _build_dcdt(midi_label):
    payload  = utf16be_str(midi_label)
    payload += struct.pack('>II', 0, 0)
    payload += struct.pack('>f', 127.0)
    payload += struct.pack('>I', 0)
    payload += struct.pack('>i', -1)
    return frame('DCDT', payload)

def _all_dcdt_entries():
    entries = []
    for ch in range(1, 17):
        for cc in range(128):
            entries.append(_build_dcdt(f"Ch{ch:02d}.CC.{cc:03d}"))
        for note in range(128):
            octave = note // 12 - 1
            name = _NOTE_NAMES[note % 12]
            entries.append(_build_dcdt(f"Ch{ch:02d}.Note.{name}{octave}"))
    return entries


# ---------------------------------------------------------------------------
# CMAD builders — 120-byte payloads
# ---------------------------------------------------------------------------

def _cmad_volume(slot):
    """Knob turn -> Slot Volume (TID 251), Direct."""
    p  = struct.pack('>I', 4)
    p += struct.pack('>I', 1)            # ControllerType: Knob
    p += struct.pack('>I', 3)            # InteractionMode: Direct
    p += struct.pack('>i', slot)
    p += struct.pack('>I', 0)            # AutoRepeat
    p += struct.pack('>I', 0)            # Invert
    p += struct.pack('>I', 0)            # SoftTakeover
    p += struct.pack('>f', 5.0)          # RotarySensitivity
    p += struct.pack('>f', 0.0)          # RotaryAcceleration
    p += b'\x00\x00\x00\x00'
    p += b'\x00\x00\x00\x02'
    p += struct.pack('>f', 1.0)          # SetValueTo
    p += struct.pack('>I', 0)            # CommentLength
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += b'\x00\x00\x00\x02'
    p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x02'
    p += struct.pack('>f', 1.0)
    p += struct.pack('>I', 0); p += struct.pack('>I', 127)
    p += struct.pack('>I', 0); p += struct.pack('>I', 1)
    p += b'\x00\x00\x00\x02'
    p += b'\x3d\x80\x00\x00'             # Resolution: Default
    p += b'\x00\x00\x00\x00'
    assert len(p) == 120
    return p

def _cmad_mute(slot):
    """Button push -> Slot Mute (TID 259), Toggle.
    NCC buttons now use gate mode (127 on press, 0 on release).
    Traktor Toggle(1) only acts on values >= threshold, ignores the 0 release.
    Result: each physical press toggles mute once (clean 2-press cycle).
    """
    p  = struct.pack('>I', 4)
    p += struct.pack('>I', 0)            # ControllerType: Button
    p += struct.pack('>I', 1)            # InteractionMode: Toggle
    p += struct.pack('>i', slot)
    p += struct.pack('>I', 0); p += struct.pack('>I', 0); p += struct.pack('>I', 0)
    p += struct.pack('>f', 5.0); p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x00'; p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 0.0)
    p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 1.0)
    p += struct.pack('>I', 0); p += struct.pack('>I', 127)
    p += struct.pack('>I', 0); p += struct.pack('>I', 0)
    p += b'\x00\x00\x00\x01'
    p += b'\x00\x00\x00\x01'
    p += b'\x00\x00\x00\x00'
    assert len(p) == 120
    return p

def _cmad_filter(slot):
    """Knob -> Slot Filter Amount (TID 249), Direct."""
    p  = struct.pack('>I', 4)
    p += struct.pack('>I', 1)            # Knob
    p += struct.pack('>I', 3)            # Direct
    p += struct.pack('>i', slot)
    p += struct.pack('>I', 0); p += struct.pack('>I', 0); p += struct.pack('>I', 0)
    p += struct.pack('>f', 5.0); p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x00'; p += b'\x00\x00\x00\x02'
    p += struct.pack('>f', 1.0)
    p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += b'\x00\x00\x00\x02'
    p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x02'
    p += struct.pack('>f', 1.0)
    p += struct.pack('>I', 0); p += struct.pack('>I', 127)
    p += struct.pack('>I', 0); p += struct.pack('>I', 1)
    p += b'\x00\x00\x00\x02'
    p += b'\x3d\x80\x00\x00'
    p += b'\x00\x00\x00\x00'
    assert len(p) == 120
    return p

def _cmad_filter_on(slot):
    """Button -> Slot Filter On/Off (TID 250), Toggle (same logic as mute)."""
    p  = struct.pack('>I', 4)
    p += struct.pack('>I', 0)            # Button
    p += struct.pack('>I', 1)            # Toggle
    p += struct.pack('>i', slot)
    p += struct.pack('>I', 0); p += struct.pack('>I', 0); p += struct.pack('>I', 0)
    p += struct.pack('>f', 5.0); p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x00'; p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 0.0)
    p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 1.0)
    p += struct.pack('>I', 0); p += struct.pack('>I', 127)
    p += struct.pack('>I', 0); p += struct.pack('>I', 0)
    p += b'\x00\x00\x00\x01'
    p += b'\x00\x00\x00\x01'
    p += b'\x00\x00\x00\x00'
    assert len(p) == 120
    return p

def _cmad_led_out(slot):
    """LED Output — sends Traktor state back to button LED."""
    p  = struct.pack('>I', 4)
    p += struct.pack('>I', 65535)        # ControllerType: LED (0xFFFF)
    p += struct.pack('>I', 8)            # InteractionMode: Output
    p += struct.pack('>i', slot)
    p += struct.pack('>I', 0); p += struct.pack('>I', 0); p += struct.pack('>I', 0)
    p += struct.pack('>f', 5.0); p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x00'; p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 0.0)
    p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 1.0)
    p += struct.pack('>I', 0); p += struct.pack('>I', 127)
    p += struct.pack('>I', 0); p += struct.pack('>I', 0)  # LedBlend: threshold
    p += b'\x00\x00\x00\x01'
    p += b'\x00\x00\x00\x01'            # Resolution: Switch
    p += b'\x00\x00\x00\x00'
    assert len(p) == 120
    return p


# ---------------------------------------------------------------------------
# Performance pad mappings (A-H pages). Normal deck commands: deck field 0=A,1=B
# (verified in working mapping #917). Button CMAD modeled on validated _cmad_mute.
# ---------------------------------------------------------------------------

def _cmad_btn(deck, interaction):
    """Button -> command (TID set at CMAI level). interaction: 1=Toggle,2=Hold,3=Direct."""
    p  = struct.pack('>I', 4)
    p += struct.pack('>I', 0)            # ControllerType: Button
    p += struct.pack('>I', interaction)  # InteractionMode
    p += struct.pack('>i', deck)         # deck: 0=A,1=B
    p += struct.pack('>I', 0); p += struct.pack('>I', 0); p += struct.pack('>I', 0)
    p += struct.pack('>f', 5.0); p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x00'; p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 0.0)
    p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += struct.pack('>I', 0); p += b'\x00\x00\x00\x00'; p += struct.pack('>I', 0)
    p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 0.0)
    p += b'\x00\x00\x00\x01'
    p += struct.pack('>f', 1.0)
    p += struct.pack('>I', 0); p += struct.pack('>I', 127)
    p += struct.pack('>I', 0); p += struct.pack('>I', 0)
    p += b'\x00\x00\x00\x01'
    p += b'\x00\x00\x00\x01'
    p += b'\x00\x00\x00\x00'
    assert len(p) == 120
    return p

def _note_label(n):
    return f"Ch01.Note.{_NOTE_NAMES[n % 12]}{n // 12 - 1}"

# FIXED-SIZE loop pads. TID 2317 "Loop Size Select+Set", Direct. Cloned byte-for-byte
# from a verified working #1237 CMAD; only deck (offset 12) and size index (offset 44)
# are patched. Offsets 80/88 (ffffffff / 0x0a) are selector-range fields specific to
# this command — that's why we clone instead of hand-building.
# Size index (Traktor loop selector): 0=1/32 1=1/16 2=1/8 3=1/4 4=1/2 5=1 6=2 7=4 8=8 9=16 10=32 beats.
_LOOP2317_TEMPLATE = bytes.fromhex(
    '0000000400000000000000030000000000000000000000000000000040a00000000000000000000100000001000000030000000000000000000000000000000000000000000000000000000000000001ffffffff000000010000000a000000000000007f0000000000000001000000010000000100000000')

# Group B: Pad1-8 = notes 24-31 (bottom half = Deck B, field 1),
#          Pad9-16 = notes 32-39 (top half = Deck A, field 0).
# 8 sizes per deck, in pad order: 1/8,1/4,1/2,1,2,4,8,16 beats -> indices 2..9.
_LOOP_SIZES = [2, 3, 4, 5, 6, 7, 8, 9]

def _cmad_loop_size(deck, size_index):
    b = bytearray(_LOOP2317_TEMPLATE)
    b[12:16] = struct.pack('>i', deck)
    b[44:48] = struct.pack('>I', size_index)
    assert len(b) == 120
    return bytes(b)

def _loops_mappings():
    """Group B fixed-size Loops page. Ch01 notes 24-39. Each pad = instant loop of a set size."""
    m = []
    for base, deck in ((24, 1), (32, 0)):     # bottom=Deck B(field 1), top=Deck A(field 0)
        for i, size in enumerate(_LOOP_SIZES):
            m.append((_note_label(base + i), 0, 2317, _cmad_loop_size(deck, size)))
    return m

def _note_lbl(note, ch):
    """MIDI note label on an arbitrary channel (ch is 0-based; ch=0 -> Ch01)."""
    return f"Ch{ch + 1:02d}.Note.{_NOTE_NAMES[note % 12]}{note // 12 - 1}"

# --- Beatjump page (Group C, MIDI Ch04 = ch index 3) ---
# TID 2380 Beatjump, Hold(2). Jump amount = SIGNED size-index at offset 44
# (index 5=1,6=2,7=4,8=8,9=16,10=32 beats; negative=backward). Cloned from #1237.
_BEATJUMP_TEMPLATE = bytes.fromhex('000000040000000000000002ffffffff00000000000000000000000040a00000000000000000000100000001fffffff800000000000009f5000000000000000000000064ffffffff0000000100000001fffffff3000000010000000d000000000000007f0000000000000001000000010000000100000000')

def _cmad_beatjump(deck, amount_index):
    b = bytearray(_BEATJUMP_TEMPLATE)
    b[12:16] = struct.pack('>i', deck)
    b[44:48] = struct.pack('>i', amount_index)
    b[52:56] = struct.pack('>I', 0)                   # zero modifier (2549) -> fire unconditionally
    assert len(b) == 120
    return bytes(b)

# 8 pads/deck (pad order): -4 +4 -8 +8 -16 +16 -32 +32 beats -> indices -7 7 -8 8 -9 9 -10 10
_BEATJUMP_AMTS = [-7, 7, -8, 8, -9, 9, -10, 10]

def _beatjump_mappings():
    """Group C. MIDI Ch04 notes 36-51. bottom half=Deck B, top half=Deck A."""
    m = []
    for half_base, deck in ((36, 1), (44, 0)):   # Group C notes 36-51
        for i, amt in enumerate(_BEATJUMP_AMTS):
            m.append((_note_lbl(half_base + i, 3), 0, 2380, _cmad_beatjump(deck, amt)))
    return m

def _cmad_bend(deck, down):
    """Tempo Bend (TID 406 at CMAI). Hold; Invert (offset 20)=1 -> bend down, 0 -> up."""
    b = bytearray(_cmad_btn(deck, 2))
    b[20:24] = struct.pack('>I', 1 if down else 0)
    return bytes(b)

def _stems_pad_mappings():
    """Group A (Ch03, notes 12-27). Per deck: 4 stem mutes + 4 stem filter-on.
    Submix slot encoding: Deck A stems = slots 0-3, Deck B = slots 4-7."""
    m = []
    for base, slot0 in ((12, 4), (20, 0)):   # bottom=Deck B (slots 4-7), top=Deck A (slots 0-3)
        for i in range(4):
            m.append((_note_lbl(base + i, 2),     0, 259, _cmad_mute(slot0 + i)))       # mute
        for i in range(4):
            m.append((_note_lbl(base + 4 + i, 2), 0, 250, _cmad_filter_on(slot0 + i)))  # filter-on
    return m

# --- Group D: Remix Cell control on DECK C, FULL 4x4 (16 cells = 4 slots x 4 cells) ---
# Slot N Cell M Trigger: Slot1=600.., Slot2=616.., Slot3=632.., Slot4=648.. Deck field 2 = Deck C.
_REMIX_CELLS = [600, 601, 602, 603, 616, 617, 618, 619, 632, 633, 634, 635, 648, 649, 650, 651]
def _remixcell_mappings():
    """Group D (Ch05, notes 48-63). FULL 4x4 = Deck C remix grid (slots 1-4 x cells 1-4)."""
    return [(_note_lbl(48 + i, 4), 0, tid, _cmad_btn(2, 2)) for i, tid in enumerate(_REMIX_CELLS)]

# --- Group E: Pitch Play. Key Adjust 402 Direct, float at offset 44 = semitones/12 ---
_KEY_SEMIS = [-4, -3, -2, -1, 0, 1, 2, 3]   # per deck (8 pads); 0 = reset to original key
# Real Key Adjust (402) Direct CMAD cloned from SP1 (#9481); patch deck@12 + key float@44.
_KEY402_TEMPLATE = bytes.fromhex('0000000400000000000000030000000000000000000000000000000040a00000000000000000000100000002beaa7efa00000000000009f4000000000000000000000000000000000000000000000002bf800000000000023f800000000000000000007f0000000000000001000000023e2aaaab00000000')
def _cmad_keyplay(deck, semis):
    b = bytearray(_KEY402_TEMPLATE)
    b[12:16] = struct.pack('>i', deck)
    b[44:48] = struct.pack('>f', semis / 12.0)        # key offset = semitone/12 (verified)
    b[52:56] = struct.pack('>I', 0)                   # zero SP1's modifier (2548) -> fire unconditionally
    assert len(b) == 120
    return bytes(b)
def _pitchplay_mappings():
    """Group E (Ch06, notes 60-75). Per deck: 8 key-shift pads (-4..+4 semitones, with keylock)."""
    m = []
    for base, deck in ((60, 1), (68, 0)):
        for i, s in enumerate(_KEY_SEMIS):
            m.append((_note_lbl(base + i, 5), 0, 402, _cmad_keyplay(deck, s)))
    return m

def _looproll_mappings():
    """Group F (Ch07, notes 72-87). Fixed-size loop roll, sizes 1/16..8 (indices 1-8).
    Shifted up one notch from 1/32..4 — fastest is now 1/16 (1/32 was too fast).
    NOTE: round-1 moved this OFF page F (F is now loop+memories); destined for B2 in round 2."""
    m = []
    for base, deck in ((72, 1), (80, 0)):
        for i in range(8):
            m.append((_note_lbl(base + i, 6), 0, 2317, _cmad_loop_size(deck, i + 1)))
    return m


def _gate(cmad, modid, val):
    """Gate a CMAD by a Traktor modifier — fires only when modifier == val. Condition slot
    (commentLen=0 CMAD): @52 = ModId (2547+N, e.g. Mod#2 = 2549), @56 = cmp (0 = equals),
    @60 = Val. Confirmed against djtt references (hundreds of uses: @52=2547+N, @56=0, @60=val)."""
    b = bytearray(cmad)
    b[52:56] = struct.pack('>I', modid)
    b[56:60] = struct.pack('>I', 0)
    b[60:64] = struct.pack('>I', val)
    return bytes(b)

# Round 2 Scene-shift foundation -------------------------------------------------
# A latching Scene button (CC112, NCC behavior="toggle") drives Traktor Modifier #2:
# light off -> Mod#2 = 0 (layer 1), light on -> Mod#2 = 1 (layer 2). Layer-1 pad mappings
# are gated Mod#2==0, layer-2 (A2-H2) gated Mod#2==1, so the same physical pads do two jobs.
MOD2 = 2549   # Traktor Modifier #2 (ModId 2547+2)

# Set-Modifier-#2 command (TID 2549), cloned byte-for-byte from a djtt reference. We patch
# @8 = interaction and @44 = value. Driven by the NCC Scene button (CC112, behavior="toggle"),
# with Hold (2) interaction — this is the pairing the user confirmed WORKING on hardware (B2
# toggled). (An earlier attempt to "fix" it with gate+Toggle broke a working setup — reverted.)
_SETMOD2_TEMPLATE = bytes.fromhex('0000000400000000000000030000000000000000000000000000000040a00000000000000000000100000001000000000000000000000000000000000000000000000000000000000000000000000001000000000000000100000007000000000000007f0000000000000001000000010000000100000000')

def _cmad_setmod2(value, interaction=2):
    b = bytearray(_SETMOD2_TEMPLATE)
    b[8:12]  = struct.pack('>I', interaction)
    b[44:48] = struct.pack('>I', value)
    assert len(b) == 120
    return bytes(b)

def _gate_list(mappings, modid, val):
    """Apply a modifier gate to every (label, type, tid, cmad) tuple in a mapping list."""
    return [(lbl, typ, tid, _gate(cmad, modid, val)) for (lbl, typ, tid, cmad) in mappings]

def _looproll_b2_mappings():
    """B2 — the Scene-shifted layer of page B (Ch01 notes 24-39, the SAME pads as the B loops
    layer). Fixed-size loop ROLL, sizes 1/16..8 beats (indices 1-8); bottom half Deck B, top
    Deck A. Gated to Mod#2==1 by the caller so it only fires when the Scene light is on.
    TODO (Garry): B (set loops) and B2 (loop roll) are too similar — make them more distinct in a
    future rev (e.g. B = set-and-hold loops, B2 = momentary loop rolls, or a different size set)."""
    m = []
    for base, deck in ((24, 1), (32, 0)):
        for i in range(8):
            m.append((_note_label(base + i), 0, 2317, _cmad_loop_size(deck, i + 1)))
    return m


def _cmad_hotcue(deck, idx):
    """Select/Set+Store Hotcue (TID 2328), Hold, with the hotcue INDEX in SetValue@44 — the
    PROVEN dedicated-slot recipe from DJTT #2224. Empty slot + active loop -> stores the loop;
    filled slot -> recalls (jump + loop)."""
    b = bytearray(_cmad_btn(deck, 2))      # Hold interaction (proven for 2328)
    b[44:48] = struct.pack('>i', idx)      # hotcue index 0-3 carried in SetValue
    return bytes(b)

def _loopmem_mappings():
    """Group F (Ch07, notes 72-87): silent CAPTURE + recall, built ENTIRELY from VERIFIED djtt
    commands. 'Capture deck X' (TID 2002, Direct — labeled 'Capture deck A/B/C/D' in references,
    with LED feedback) grabs that deck's current loop into the remix deck SILENTLY: no playhead
    jump, nothing heard while setting it up. Recall = remix cell triggers (600+, the proven
    page-D recipe) play a captured loop later, OVER whatever is playing — no jump back.
    (Traktor's Loop Recorder transport is in NO djtt reference, so it cannot be built
    verified-only; this capture->remix path is the verifiable equivalent of your 'silent record,
    save, use later'. Captures land in the FOCUSED remix deck — keep Deck C focused as the target.)
      Pad1-4 (72-75): Capture Deck A / B / C / D  (2002, Direct)
      Pad5-16 (76-87): remix cell triggers, slots 1-3 x cells 1-4 (recall captured loops, Deck C)"""
    m = []
    for i in range(4):                                  # Capture deck A/B/C/D (silent grab -> remix)
        m.append((_note_lbl(72 + i, 6), 0, 2002, _cmad_btn(i, 3)))
    recall = [600, 601, 602, 603, 616, 617, 618, 619, 632, 633, 634, 635]
    for i, tid in enumerate(recall):                    # recall: trigger captured remix cells (Deck C)
        m.append((_note_lbl(76 + i, 6), 0, tid, _cmad_btn(2, 2)))
    return m


# Verified TID 362 "Effect 1 Selector" CMAD (commentLen=0): Direct (@8=3) + HasValueUI (@36=1) +
# ValueUIType combobox (@40=1) + LedMinRange (@84=0) + LedMaxRange (@88=43 = FX-list count) + Midi 0-127.
# Parsed from cmdr's EnumInCommand and confirmed byte-identical across 6 controller families (Kontrol S4,
# CNTRL:R, MIDI Fighter Spectra, Maschine Jam, Xone:K2, Maschine). Past failures: plain Direct button
# (HasValueUI=0) -> Traktor increments/cycles; loop-size clone (LedMin=-1, range 40) -> intermittent.
_FX362_TEMPLATE = bytes.fromhex(
    '0000000400000000000000030000000000000000000000000000000040a0000000000000'
    '000000010000000100000005000000000000000000000000000000000000000000000000'
    '000000000000000100000000000000010000002b000000000000007f00000000000000'
    '00000000010000000100000000')

def _cmad_fxselect(pos):
    """Effect 1 Selector (TID 362) -> load the effect at FX Pre-Selection position `pos` into FX1.
    Clone the verified _FX362_TEMPLATE and patch the unit (@12) and position (@44). @44 is the 1-based
    slot in the user's Traktor FX Pre-Selection list (default order: Beatmasher=1, Gater=5, Delay=6 ...)."""
    b = bytearray(_FX362_TEMPLATE)
    b[12:16] = struct.pack('>i', 0)        # FX Unit 1
    b[44:48] = struct.pack('>I', pos)      # effect list position (1-based, FX Pre-Selection)
    assert len(b) == 120
    return bytes(b)


# Per-effect quick-use presets: (effect list-position, Knob1/366, Knob2/367, Knob3/368, button TID).
# Params are good-sounding values decoded from reference macros (catalog Normalized sheet); None = leave
# default. button = the effect's engage button (370/371/372) for button-type effects, else None.
# NOTE: list-position assumes Traktor's default Effect-Selector order (see README pad->effect map).
FX_PRESETS_G = [   # page G (layer 0) — musical bank
    (1,  0.9,  None, None, 370),   # Beatmasher  (1/4-bar mash; Btn1 = gate)
    (5,  0.5,  0.5,  None, 371),   # Gater       (half rate;   Btn2 = gate on)
    (6,  0.6,  0.42, 0.5,  None),  # Delay
    (29, 0.5,  None, None, None),  # Tape Delay
    (19, 0.24, 0.77, 0.72, None),  # Iceverb     (reference reverb tone)
    (14, 0.5,  None, None, None),  # Phaser
    (16, None, 0.0,  None, None),  # Phaser Flux
    (32, 0.75, 0.85, None, 371),   # Bouncer     (Btn2 = on)
    (11, 0.75, None, None, 370),   # Oscillator  (Btn1 = on)
    (40, 0.4,  None, None, 370),   # Zzzurp      (Btn1 = on)
    (43, None, None, 0.5,  None),  # Strrretch
    (8,  0.5,  None, None, None),  # Filter LFO
    (37, 0.5,  None, None, None),  # Bass-o-Matic
    (7,  0.6,  None, None, None),  # Delay T3
    (15, 0.5,  None, None, None),  # Phaser Pulse
    (6,  0.8,  0.6,  0.5,  None),  # Delay (dub: more feedback)
]
FX_PRESETS_G2 = [  # page G2 (layer 1, Scene) — same effects, harder/wetter bank
    (1,  1.0,  None, None, 370),   # Beatmasher  (1/8-bar, fastest)
    (5,  0.5,  0.75, None, 371),   # Gater       (faster rate)
    (6,  0.8,  0.42, 0.5,  None),  # Delay       (more feedback)
    (29, 0.7,  None, None, None),  # Tape Delay
    (19, 0.5,  0.9,  0.8,  None),  # Iceverb     (bigger)
    (14, 0.8,  None, None, None),  # Phaser      (deeper)
    (16, None, 0.5,  None, None),  # Phaser Flux
    (32, 0.9,  0.9,  None, 371),   # Bouncer     (1/32)
    (11, 0.9,  None, None, 370),   # Oscillator  (higher)
    (40, 0.8,  None, None, 370),   # Zzzurp      (more)
    (43, None, None, 0.8,  None),  # Strrretch
    (8,  0.75, None, None, None),  # Filter LFO
    (37, 0.75, None, None, None),  # Bass-o-Matic
    (7,  1.0,  None, None, None),  # Delay T3
    (15, 0.75, None, None, None),  # Phaser Pulse
    (6,  1.0,  0.6,  0.5,  None),  # Delay (max)
]

def _fxselect_mappings(layer):
    """Group G (layer 0) / G2 (layer 1, Scene), Ch08 notes 84-99 — 16-effect FX1 selector, PLAN B:
    each pad ONLY chooses the effect (362) + sets its params + drives the wet. The route (321), unit-on
    (369) and effect on/off buttons (370/371/372) do NOT fire from the pad — they're pre-armed once
    (Solo engage, or FX1 left on+routed in Traktor) so the select can never collide with the on (that
    race was the intermittency). Press = effect chosen + wet full; RELEASE = wet 0 = off. The activator
    is the wet (a value, Hold), held only on the pressed pad — no 16-pad conflict."""
    presets = FX_PRESETS_G if layer == 0 else FX_PRESETS_G2
    m = []
    for i, (pos, k1, k2, k3, btn) in enumerate(presets):
        note = _note_lbl(84 + i, 7)
        m.append((note, 0, 362, _gate(_cmad_fxselect(pos), MOD2, layer)))           # choose effect
        for tid, val in ((366, k1), (367, k2), (368, k3)):                          # set its params (floats)
            if val is not None:
                m.append((note, 0, tid, _gate(_cmad_fxval(0, val), MOD2, layer)))
        m.append((note, 0, 365, _gate(_cmad_wet_gate(), MOD2, layer)))              # activator: wet full held, 0 on release
    return m

# --- Group G: stereo VU of MAIN OUTPUT (replaces Mixer FX) ---
# 8-level bar per channel. Left = Main Level L (2704), Right = Main Level R (2705).
# LED output to the pad B-LED on Ch03 (ch2), pad notes 84-99. Cumulative bar: level k lights
# when Main level >= k/8. Pad fill order (user spec):
#   L = pads 2,6,10,14,1,5,9,13 (levels 1..8);  R mirrored = 3,7,11,15,4,8,12,16.
_VU_LEFT  = [2, 6, 10, 14, 1, 5, 9, 13]
_VU_RIGHT = [3, 7, 11, 15, 4, 8, 12, 16]
_VU_LEVEL_COLOR = {1: 4, 2: 5, 3: 6, 4: 3, 5: 2, 6: 7, 7: 1, 8: 1}  # mode1: 1-6 varied non-red, 7-8 red

# Metering LED-output CMAD, cloned byte-for-byte from working Maschine VU mappings
# (#10371 + #3589, identical). This signature makes a meter actually MOVE: CtrlType=LED,
# Inter=Output, @40=2, range-type fields=2, LedBlend=1 (fade), Resolution=0x3d800000.
# (My earlier VU used the button on/off signature -> Traktor treated it as binary = no move.)
# Only the per-segment band MinCtrl@80 / MaxCtrl@88 is patched.
_VU_TEMPLATE = bytes.fromhex(
    '000000040000ffff000000080000000000000000000000000000000040a000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000023ecccccd000000023f000000000000000000007f0000000000000001000000023d80000000000000')

def _cmad_vu(level):
    """LED metering output. Segment `level` (1..8) = a rising threshold that fades up to FULL.
    Band = [ (level-1)/8 , 1.0 ] — matches the WORKING #3589 VU (overlapping bands, rising Min,
    Max always 1.0). A wide band makes the blend fade smoothly across the level range = visible
    movement; the old disjoint narrow bands [k/8,(k+1)/8] snapped full instantly (looked static)."""
    b = bytearray(_VU_TEMPLATE)
    b[80:84] = struct.pack('>f', (level - 1) / 8.0)   # LedMinControllerRange (rising threshold)
    b[88:92] = struct.pack('>f', 1.0)                 # LedMaxControllerRange = 1.0 (fade to full)
    assert len(b) == 120
    return bytes(b)

def _vu_mappings():
    """Group G stereo VU of MAIN output. Main L (2704) -> left pads, Main R (2705) -> right.
    Drives BOTH pad LED variants per pad — Ch03 (PadNB) and Ch01 (PadNH) — with the metering
    recipe, since on the MK2 the visible/responsive LED variant is uncertain (#10371 used both:
    Ch01 for color, Ch03 for level). Whichever variant responds, the bar fills with level."""
    m = []
    for tid, pads in ((2704, _VU_LEFT), (2705, _VU_RIGHT)):
        for i, pad in enumerate(pads):
            note = 84 + (pad - 1)
            cmad = _cmad_vu(i + 1)
            m.append((_note_lbl(note, 2), 1, tid, cmad))   # Ch03 PadNB, level 1..8
            m.append((_note_lbl(note, 0), 1, tid, cmad))   # Ch01 PadNH, level 1..8
    return m

def _transport_mappings():
    """Group H (Ch09, notes 96-111). Play, Cue, Sync, Flux (x2 to fill 8 pads)."""
    m = []
    specs = [(100, 1), (206, 2), (125, 1), (2350, 1), (100, 1), (206, 2), (125, 1), (2350, 1)]
    for base, deck in ((96, 1), (104, 0)):
        for i, (tid, inter) in enumerate(specs):
            m.append((_note_lbl(base + i, 8), 0, tid, _cmad_btn(deck, inter)))
    return m


# ---------------------------------------------------------------------------
# Round 2: layer-2 pages (A2-H2) — reached when the Scene light is ON (Mod#2==1).
# Each shares its layer-1 page's physical pads/channel; gated to Mod#2==1 by the caller.
# All TIDs verified against djtt references except the two flagged spots (C2 64/128, F2).
# ---------------------------------------------------------------------------

def _stemfx_a2_mappings():
    """A2 (page A pads, Ch03 notes 12-27): per-stem FX send + per-deck FX-unit assign.
      notes 12-15: Deck B -> FX1/2/3/4 assign (321/322/338/339, Toggle = tap to route on/off)
      notes 16-19: Deck B stem FX-send toggle, stem slots 4-7 (239, Toggle — proven x52)
      notes 20-23: Deck A -> FX1/2/3/4 assign
      notes 24-27: Deck A stem FX-send toggle, stem slots 0-3 (239, Toggle)"""
    FXASGN = [321, 322, 338, 339]
    m = []
    for base, deck, slot0 in ((12, 1, 4), (20, 0, 0)):
        for i, tid in enumerate(FXASGN):
            m.append((_note_lbl(base + i, 2), 0, tid, _cmad_btn(deck, 1)))         # deck -> FXn (Toggle)
        for i in range(4):
            m.append((_note_lbl(base + 4 + i, 2), 0, 239, _cmad_mute(slot0 + i)))  # stem FX send (Toggle)
    return m

# C2 phrase jumps: +/-16,32,64,128 beats = beatjump indices +/-9,10,11,12. 9,10 are
# reference-confirmed; 11(64)/12(128) extrapolate the proven power-of-two sequence (5=1..10=32).
_PHRASE_AMTS = [-9, 9, -10, 10, -11, 11, -12, 12]
def _phrasejump_c2_mappings():
    """C2 (page C pads, Ch04 notes 36-51): big phrase jumps +/-16/32/64/128 beats (Beatjump 2380,
    Hold — same proven recipe as page C; 64/128 indices extrapolated)."""
    m = []
    for half_base, deck in ((36, 1), (44, 0)):
        for i, amt in enumerate(_PHRASE_AMTS):
            m.append((_note_lbl(half_base + i, 3), 0, 2380, _cmad_beatjump(deck, amt)))
    return m

# D2 remix cells 5-8 per slot (extends page D's cells 1-4). Slot stride 16, cell stride 1.
_REMIX_CELLS2 = [604, 605, 606, 607, 620, 621, 622, 623, 636, 637, 638, 639, 652, 653, 654, 655]
def _remix_d2_mappings():
    """D2 (page D pads, Ch05 notes 48-63): Deck C remix cells 5-8 (Hold trigger, Deck C —
    reference-confirmed 604-655)."""
    return [(_note_lbl(48 + i, 4), 0, tid, _cmad_btn(2, 2)) for i, tid in enumerate(_REMIX_CELLS2)]

def _toneplay_e2_mappings():
    """E2 (page E pads, Ch06 notes 60-75): tone-play — original-key RESET (0 semitones) on physical
    pad 1 (deck A) / pad 9 (deck B), then +1..+7 semitones on the other 7 pads. Notes run bottom-up
    while pads number top-down, so the reset sits at base+4 (same geometry as page E and the B2 fix).
    Key Adjust (402, Direct — proven x52). Mute other stems (page A) to play one stem melodically."""
    m = []
    for base, deck in ((60, 1), (68, 0)):
        m.append((_note_lbl(base + 4, 5), 0, 402, _cmad_keyplay(deck, 0)))     # reset = original key (pad 1/9)
        notes = [base + o for o in (0, 1, 2, 3, 5, 6, 7)]
        for n, s in zip(notes, range(1, 8)):
            m.append((_note_lbl(n, 5), 0, 402, _cmad_keyplay(deck, s)))
    return m

def _looprec_f2_mappings():
    """F2 (page F pads, Ch07 notes 72-87): Traktor LOOP RECORDER. EXPERIMENTAL — these TIDs appear
    in references but sparsely. Global engine (deck field 0). Four controls, repeated on each row
    for two-hand reach: Record/Play state (280, Direct), Size- (281, Dec), Size+ (281, Inc),
    Undo/Del (282, Direct)."""
    m = []
    ctrls = [(280, 3), (281, 6), (281, 5), (282, 3)]   # Rec/Play, Size-, Size+, Undo
    for row_base in (72, 76, 80, 84):
        for i, (tid, inter) in enumerate(ctrls):
            m.append((_note_lbl(row_base + i, 6), 0, tid, _cmad_btn(0, inter)))
    return m

def _transport_h2_mappings():
    """H2 (page H pads, Ch09 notes 96-111): Play/Cue/Sync/Flux for decks C/D — same proven
    transport recipe as page H, decks 2/3 (bottom=Deck D, top=Deck C)."""
    m = []
    specs = [(100, 1), (206, 2), (125, 1), (2350, 1), (100, 1), (206, 2), (125, 1), (2350, 1)]
    for base, deck in ((96, 3), (104, 2)):
        for i, (tid, inter) in enumerate(specs):
            m.append((_note_lbl(base + i, 8), 0, tid, _cmad_btn(deck, inter)))
    return m


# ---------------------------------------------------------------------------
# Round 3: PATTERN layer (A3-H3) — Traktor Pro 4 Pattern Player on FX3 + FX4.
# Reached via the Pattern button (CC113) which sets Modifier #2 = 2 (the 3rd state of the SAME
# modifier Scene uses: 0=layer1, 1=Scene/layer2, 2=Pattern/layer3). One modifier = one value, so
# Scene and Pattern layers can NEVER both fire (conflict structurally impossible) without touching
# layer 1/2 gating. Pattern Player is loaded into FX3/FX4 (user loads the effect); its controls
# are the proven FX-unit slots addressed by unit field (FX3=2, FX4=3).
# ---------------------------------------------------------------------------

def _cmad_fxpattern(unit, idx):
    """Select Pattern Player pattern `idx` (0-7) on FX `unit` (TID 367 = FX Knob 2 = Pattern
    Selector, Direct). The selector is a knob with 8 positions; pattern I sits at the centre of
    its 1/8 segment = value (I+0.5)/8. Direct mechanism is proven (#13002 sets 367 Direct to
    0.5); the 8 evenly-spaced per-pattern values are extrapolated from the 8 selector positions."""
    b = bytearray(_cmad_btn(unit, 3))
    b[36:40] = struct.pack('>I', 1)                     # HasValueUI = 1 (FloatInCommand needs it)
    b[40:44] = struct.pack('>I', 2)                     # ValueUIType = 2 (fader / float)
    b[44:48] = struct.pack('>f', (idx + 0.5) / 8.0)     # pattern position (float)
    return bytes(b)

def _patternpick_h3_mappings():
    """H3 (page H pads, Ch09 notes 96-111): Pattern Picker for the two drum voices.
    notes 96-103 (bottom 8) = FX3 patterns 1-8; notes 104-111 (top 8) = FX4 patterns 1-8.
    Patterns run sparse->busy, so stepping up the pads intensifies the groove."""
    m = []
    for base, unit in ((96, 2), (104, 3)):   # bottom=FX3, top=FX4
        for i in range(8):
            m.append((_note_lbl(base + i, 8), 0, 367, _cmad_fxpattern(unit, i)))
    return m

def _cmad_fxval(unit, value):
    """Set an FX float param (Dry/Wet 365 / Knob 366-368) to float `value`, Direct. FloatInCommand
    REQUIRES HasValueUI=1 + ValueUIType=2 (fader) for the set to take — a plain button writes
    HasValueUI=0/Type=1, which Traktor ignores (why params/wet-start never applied). LedMaxRange stays
    float 1.0 (the 0-1 range). Verified vs Xone:K2 #12008 + 'Instant JogFX' S4 #2610."""
    b = bytearray(_cmad_btn(unit, 3))
    b[36:40] = struct.pack('>I', 1)         # HasValueUI = 1
    b[40:44] = struct.pack('>I', 2)         # ValueUIType = 2 (fader / float)
    b[44:48] = struct.pack('>f', value)     # set value (float, 0-1)
    return bytes(b)

def _patternctrl_mappings(unit, base, ch):
    """Pattern Player CONTROL ROOM for one drum voice (FX `unit`). Used for A3 (FX3) and B3 (FX4).
    All verified FX-unit slots: On 369, Play/Mute 370, Sample 371, Pattern 367, Volume 366, Pitch
    368. 16 pads from note `base` on channel `ch`:
      row1: On(Toggle) · Play/Mute(Toggle) · Next Sample(Inc) · Prev Sample(Dec)
      row2: quick patterns 1/3/5/7 (sparse->busy)
      row3: volume 25/50/75/100 %
      row4: pitch -12 / 0 / +7 / +12 semitones"""
    m = [
        (_note_lbl(base + 0, ch), 0, 369, _cmad_btn(unit, 1)),   # Unit On/Off (Toggle)
        (_note_lbl(base + 1, ch), 0, 370, _cmad_btn(unit, 1)),   # Play/Mute (Toggle)
        (_note_lbl(base + 2, ch), 0, 371, _cmad_btn(unit, 5)),   # Next Sample (Inc)
        (_note_lbl(base + 3, ch), 0, 371, _cmad_btn(unit, 6)),   # Prev Sample (Dec)
    ]
    for i, idx in enumerate((0, 2, 4, 6)):
        m.append((_note_lbl(base + 4 + i, ch), 0, 367, _cmad_fxpattern(unit, idx)))
    for i, vol in enumerate((0.25, 0.5, 0.75, 1.0)):
        m.append((_note_lbl(base + 8 + i, ch), 0, 366, _cmad_fxval(unit, vol)))
    for i, semi in enumerate((-12, 0, 7, 12)):
        m.append((_note_lbl(base + 12 + i, ch), 0, 368, _cmad_fxval(unit, (semi + 12) / 24.0)))
    return m

def _drummix_c3_mappings():
    """C3 (page C pads, Ch04 notes 36-51): drum-voice mixer + routing — all verified.
      36-39: route deck A/B/C/D -> FX3 (338, Toggle)
      40-43: route deck A/B/C/D -> FX4 (339, Toggle)
      44-47: FX3 Play/Mute, FX4 Play/Mute, FX3 On, FX4 On
      48-51: FX3 vol lo/hi, FX4 vol lo/hi"""
    m = []
    for i in range(4):
        m.append((_note_lbl(36 + i, 3), 0, 338, _cmad_btn(i, 1)))   # deck i -> FX3
    for i in range(4):
        m.append((_note_lbl(40 + i, 3), 0, 339, _cmad_btn(i, 1)))   # deck i -> FX4
    m.append((_note_lbl(44, 3), 0, 370, _cmad_btn(2, 1)))   # FX3 Play/Mute
    m.append((_note_lbl(45, 3), 0, 370, _cmad_btn(3, 1)))   # FX4 Play/Mute
    m.append((_note_lbl(46, 3), 0, 369, _cmad_btn(2, 1)))   # FX3 On
    m.append((_note_lbl(47, 3), 0, 369, _cmad_btn(3, 1)))   # FX4 On
    m.append((_note_lbl(48, 3), 0, 366, _cmad_fxval(2, 0.3)))  # FX3 vol lo
    m.append((_note_lbl(49, 3), 0, 366, _cmad_fxval(2, 0.9)))  # FX3 vol hi
    m.append((_note_lbl(50, 3), 0, 366, _cmad_fxval(3, 0.3)))  # FX4 vol lo
    m.append((_note_lbl(51, 3), 0, 366, _cmad_fxval(3, 0.9)))  # FX4 vol hi
    return m

def _toneplay_d3_mappings():
    """D3 (page D pads, Ch05 notes 48-63): tone-play the drum voices chromatically (368 Pitch).
    48-55: FX3 pitch semitones 0..7; 56-63: FX4 pitch 0..7 — play the drums melodically."""
    m = []
    for base, unit in ((48, 2), (56, 3)):
        for i in range(8):
            m.append((_note_lbl(base + i, 4), 0, 368, _cmad_fxval(unit, (i + 12) / 24.0)))
    return m

def _sounddesign_e3_mappings():
    """E3 (page E pads, Ch06 notes 60-75): drum SOUND DESIGN per voice — flip kit samples
    (371 Inc/Dec), reset pitch (372), play/mute (370), and a 4-step Decay sweep (365 min->max).
    FX3 bottom 8, FX4 top 8."""
    m = []
    for base, unit in ((60, 2), (68, 3)):
        m.append((_note_lbl(base + 0, 5), 0, 371, _cmad_btn(unit, 5)))   # Next sample (Inc)
        m.append((_note_lbl(base + 1, 5), 0, 371, _cmad_btn(unit, 6)))   # Prev sample (Dec)
        m.append((_note_lbl(base + 2, 5), 0, 372, _cmad_btn(unit, 3)))   # Reset pitch
        m.append((_note_lbl(base + 3, 5), 0, 370, _cmad_btn(unit, 1)))   # Play/Mute (Toggle)
        for i, dec in enumerate((0.0, 0.33, 0.66, 1.0)):
            m.append((_note_lbl(base + 4 + i, 5), 0, 365, _cmad_fxval(unit, dec)))  # Decay min..max
    return m

def _gate_f3_mappings():
    """F3 (page F pads, Ch07 notes 72-87): GATE & VOLUME per voice — momentary mute-gate (370,
    Hold) to stutter the drums rhythmically, play (369), reset pitch (372), 4-step Volume
    (366 duck->full). FX3 bottom 8, FX4 top 8."""
    m = []
    for base, unit in ((72, 2), (80, 3)):
        m.append((_note_lbl(base + 0, 6), 0, 370, _cmad_btn(unit, 2)))   # Mute-gate (Hold)
        m.append((_note_lbl(base + 1, 6), 0, 370, _cmad_btn(unit, 2)))   # Mute-gate (2nd, two-hand)
        m.append((_note_lbl(base + 2, 6), 0, 369, _cmad_btn(unit, 1)))   # Play/Mute (Toggle)
        m.append((_note_lbl(base + 3, 6), 0, 372, _cmad_btn(unit, 3)))   # Reset pitch
        for i, v in enumerate((0.0, 0.33, 0.66, 1.0)):
            m.append((_note_lbl(base + 4 + i, 6), 0, 366, _cmad_fxval(unit, v)))  # Volume duck..full
    return m

def _macros_g3_mappings():
    """G3 (page G pads, Ch08 notes 84-99): one-tap MACROS (combos across BOTH voices) + quick
    pattern/play. Bottom row 84-87 = DROP (mute both) / BUILD (busy pattern) / FILL (max) /
    CLEAR (pattern 1 + reset pitch). 88-91/92-95 = FX3/FX4 quick patterns. 96-99 = play + vol."""
    m = []
    for unit in (2, 3):                                       # macros fire on BOTH voices
        m.append((_note_lbl(84, 7), 0, 370, _cmad_btn(unit, 1)))         # DROP: mute both
        m.append((_note_lbl(85, 7), 0, 367, _cmad_fxpattern(unit, 5)))   # BUILD: busy pattern
        m.append((_note_lbl(86, 7), 0, 367, _cmad_fxpattern(unit, 7)))   # FILL: max pattern
        m.append((_note_lbl(87, 7), 0, 367, _cmad_fxpattern(unit, 0)))   # CLEAR: pattern 1
        m.append((_note_lbl(87, 7), 0, 372, _cmad_btn(unit, 3)))         # CLEAR: reset pitch too
    for i, idx in enumerate((0, 2, 4, 6)):                    # quick patterns per voice
        m.append((_note_lbl(88 + i, 7), 0, 367, _cmad_fxpattern(2, idx)))
        m.append((_note_lbl(92 + i, 7), 0, 367, _cmad_fxpattern(3, idx)))
    m.append((_note_lbl(96, 7), 0, 369, _cmad_btn(2, 1)))     # FX3 play
    m.append((_note_lbl(97, 7), 0, 369, _cmad_btn(3, 1)))     # FX4 play
    m.append((_note_lbl(98, 7), 0, 366, _cmad_fxval(2, 1.0)))  # FX3 vol full
    m.append((_note_lbl(99, 7), 0, 366, _cmad_fxval(3, 1.0)))  # FX4 vol full
    return m

# Browser list-scroll ENCODER CMAD, cloned byte-for-byte from #917's Dial (CC101 -> TID 3200,
# CtrlType=2 Encoder, Interaction=4 Relative). The Dial must be in relative ("comp") mode in
# the NCC for this to scroll. Conditions zeroed.
_BROWSE_SCROLL = bytes.fromhex(
    '0000000400000002000000040000000000000000000000000000000040a00000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000001ffffff800000000100000080000000000000007f0000000000000001000000010000000100000000')

def _browse_mappings():
    """Browse button (CC87) -> toggle browser view (4209). The Dial (CC101) is layer-gated in
    perf_map: browser scroll on layers 1/2, Deck D (drum-bus) volume on the Pattern layer."""
    return [("Ch01.CC.087", 0, 4209, _cmad_btn(0, 1))]

def _cmad_voldial(deck):
    """Relative-encoder CMAD for a deck's channel Volume (TID 102), cloned from the proven dial
    scroll encoder with the deck field patched (Deck D = 3). Sensitivity may want tuning."""
    b = bytearray(_BROWSE_SCROLL)
    b[12:16] = struct.pack('>i', deck)
    return bytes(b)

def _cmad_fxon(field, interaction=2):
    """FX On/Off-type command set to ON: FX-unit/deck assign (321/322/338/339), Unit-On (369), FX
    buttons (370/371/372). These are OnOffInCommands and REQUIRE HasValueUI=1 + LedMaxRange=int 1 — a
    plain button writes HasValueUI=0 + LedMaxRange=float 1.0, which Traktor SILENTLY IGNORES. That bug
    is why FX assign/unit-on never fired (verified vs Xone:K2 #12008 + 'Instant JogFX' S4 #2610).
    interaction 2 = Hold = momentary on-while-held (G punch cut-on-release; Solo/Pattern arming that
    holds while the latching button is on). `field` = deck (assign) or FX unit (on/buttons)."""
    b = bytearray(_cmad_btn(field, interaction))
    b[36:40] = struct.pack('>I', 1)     # HasValueUI = 1
    b[44:48] = struct.pack('>I', 1)     # value = ON
    b[88:92] = struct.pack('>I', 1)     # LedMaxRange = int 1 (boolean)
    return bytes(b)

MOD3 = 2550   # Traktor Modifier #3 — FX1 "engage" state (0 = off, 1 = engaged)
MOD4 = 2551   # Traktor Modifier #4 — "volume mode" (Volume button CC7 latched -> Dial = deck volume)

def _gate2(cmad, m1, v1, m2, v2):
    """Gate by TWO modifier conditions, ANDed (slot 1 @52, slot 2 @64). Fires only when
    Mod m1 == v1 AND Mod m2 == v2."""
    b = bytearray(cmad)
    b[52:56] = struct.pack('>I', m1); b[56:60] = struct.pack('>I', 0); b[60:64] = struct.pack('>I', v1)
    b[64:68] = struct.pack('>I', m2); b[68:72] = struct.pack('>I', 0); b[72:76] = struct.pack('>I', v2)
    return bytes(b)

def _cmad_wet_gate():
    """FX1 Dry/Wet (365) HOLD at full = the Plan-B activator: wet = 1.0 while the pad is held, snaps
    back to 0 on release (the 'off'). On/off + routing are pre-armed (Solo engage / left on in Traktor),
    NOT fired by the pad, so select can't collide with on. Hold acts only on the held pad (no 16-pad
    conflict). Float command: HasValueUI=1 + ValueUIType=2."""
    b = bytearray(_cmad_btn(0, 2))          # Hold, FX Unit 1
    b[36:40] = struct.pack('>I', 1)         # HasValueUI = 1
    b[40:44] = struct.pack('>I', 2)         # ValueUIType = 2 (float / fader)
    b[44:48] = struct.pack('>f', 1.0)       # wet = full while held, 0 on release
    return bytes(b)

def _cmad_wet_ramp():
    """FX1 Dry/Wet (365) Increment + AutoRepeat: while the pad is held, re-fires on a timer and nudges
    the wet UP (clamps at full); on release it stops where it landed (Inc never resets) = freeze. Step
    = Resolution @112 (Fine ≈0.0156/tick → a few-second sweep; tunable). AutoRepeat (@16=1) is ONLY
    valid with Inc/Dec. Verified recipe: cmdr + shipped 'Instant JogFX'/'sweep out' TID-365 mappings."""
    b = bytearray(_cmad_btn(0, 5))                  # Increment, FX Unit 1
    b[16:20] = struct.pack('>I', 1)                 # AutoRepeat ON
    b[112:116] = struct.pack('>I', 0x3C800000)      # Resolution = Fine (per-tick step)
    return bytes(b)


def _transport_nav_mappings():
    """Lower-left transport + master-section nav (Ch01 CCs). Transport follows the FOCUSED
    deck (deck=-1, device DDIF=Focus). Browser scroll direction = signed int at offset 44
    (up=-1, down=+1, from #917). Grid = Toggle Last Focus (flip A<->B focus)."""
    def cc(n): return f"Ch01.CC.{n:03d}"
    # Browser list-scroll button, cloned byte-for-byte from #917 (CC110=down/+1, CC109=up/-1).
    # My old version used the generic button CMAD whose trailer (@80/@88/@36) differs from the
    # real scroll command, so only one direction scrolled. Patch only @44 (+1 down / -1 up).
    _SCROLL_TEMPLATE = bytes.fromhex(
        '0000000400000000000000030000000000000000000000000000000040a00000000000000000000100000001000000010000000000000000000000000000000000000000000000000000000000000001ffffff800000000100000080000000000000007f0000000000000001000000010000000100000000')
    def _scroll(direction):
        b = bytearray(_SCROLL_TEMPLATE); b[44:48] = struct.pack('>i', direction); return bytes(b)
    def _focus_led():
        # Grid LED ON when DECK A focused. EXACT recipe copied from a WORKING TID 9 output
        # (#1237): deck=0, LedMax=0.0, MidiMax=1 (Min=0, MidiMin=0, Invert=0, Blend=0, Reso=switch
        # already match _cmad_led_out). Traktor emits MIDI 1 only when Deck 0 (A) is the focused
        # deck, 0 otherwise -> the Grid LED lights only when Deck A is focused. (Earlier band/invert
        # guesses had the wrong shape; this matches a proven mapping byte-for-byte.)
        b = bytearray(_cmad_led_out(0))
        b[88:92] = struct.pack('>f', 0.0)   # LedMaxControllerRange = 0.0
        b[96:100] = struct.pack('>I', 1)    # MidiMax = 1
        return bytes(b)
    return [
        (cc(108), 0, 100,  _cmad_btn(-1, 1)),          # Play    -> Play/Pause (focused)
        (cc(104), 0, 206,  _cmad_btn(0, 3)),           # Restart -> jump to start, Deck A
        (cc(104), 0, 206,  _cmad_btn(1, 3)),           # Restart -> jump to start, Deck B
        (cc(109), 0, 2056, _cmad_btn(0, 1)),           # Rec     -> Audio Recorder Record/Stop, Toggle (press=start, press=stop)
        (cc(107), 0, 2588, _cmad_btn(0, 2)),           # Grid    -> Toggle Last Focus (A<->B)
        (cc(105), 0, 2380, _cmad_beatjump(-1, -7)),    # Step L  -> Beatjump -4 beats (focused)
        (cc(106), 0, 2380, _cmad_beatjump(-1, 7)),     # Step R  -> Beatjump +4 beats (focused)
        (cc(3),   0, 3076, _cmad_btn(0, 3)),           # Tempo   -> Load selected into Deck A
        (cc(100), 0, 3076, _cmad_btn(1, 3)),           # Enter   -> Load selected into Deck B
        (cc(102), 0, 3076, _cmad_btn(-1, 3)),          # Push    -> Load (focused)
        (cc(98),  0, 3328, _scroll(-1)),               # Master L -> Browser TREE select up (browse folders)
        (cc(99),  0, 3328, _scroll(1)),                # Master R -> Browser TREE select down (browse folders)
        (cc(108), 1, 100,  _cmad_led_out(-1)),         # Play LED  -> lit (green) when focused deck playing
        (cc(109), 1, 2058, _cmad_led_out(0)),          # Rec LED   -> lit (red) when recording
        (cc(107), 1, 9,    _focus_led()),              # Grid LED  -> lit when Deck A is focused
        (cc(111), 0, 8194, _cmad_btn(0, 1)),           # Note Repeat -> Cruise (Traktor's Auto-DJ) on/off (Toggle)
        (cc(111), 1, 8194, _cmad_led_out(0)),          # Note Repeat LED -> lit only while Cruise is running
    ]


def _fx_mappings():
    """FX control for the Group F/G/H display pages. The NCC perf pages already send
    Ch01 CC1-48; this device maps them to Traktor FX. The FX unit (1-4) is the deck
    field (0-3), exactly like a deck. Toggle buttons via _cmad_btn; absolute (Direct)
    knobs via _cmad_filter (a generic knob CMAD whose deck field = FX unit).
    100%-original layout that REPLACES the previously-kept third-party FX device:
      Page F: FX Unit 1 (CC1-4 btn, CC9-12 knob)  + FX Unit 2 (CC5-8 btn,  CC13-16 knob)
      Page G: FX Unit 3 (CC17-20,   CC25-28)      + FX Unit 4 (CC21-24,    CC29-32)
      Page H: all-4 overview — On+Btn1 (CC33-40), Dry/Wet+Knob1 (CC41-48)
    Per unit: buttons = On(369), Btn1(370), Btn2(371), Btn3(372);
              knobs   = Dry/Wet(365), Knob1(366), Knob2(367), Knob3(368)."""
    def cc(n): return f"Ch01.CC.{n:03d}"
    btn  = lambda u: _cmad_btn(u, 1)     # toggle button
    knob = _cmad_filter                   # generic Direct (absolute) knob; deck field = FX unit
    BTN_TIDS = [369, 370, 371, 372]
    KNB_TIDS = [365, 366, 367, 368]
    m = []
    def unit_block(unit, btn_cc0, knob_cc0):
        for i, tid in enumerate(BTN_TIDS): m.append((cc(btn_cc0 + i), 0, tid, btn(unit)))
        for i, tid in enumerate(KNB_TIDS): m.append((cc(knob_cc0 + i), 0, tid, knob(unit)))
    unit_block(0,  1,  9)    # Page F left  = FX 1
    unit_block(1,  5, 13)    # Page F right = FX 2
    unit_block(2, 17, 25)    # Page G left  = FX 3
    unit_block(3, 21, 29)    # Page G right = FX 4
    for u in range(4): m.append((cc(33 + u), 0, 369, btn(u)))    # Page H: FX1-4 On
    for u in range(4): m.append((cc(37 + u), 0, 370, btn(u)))    #         FX1-4 Btn1
    for u in range(4): m.append((cc(41 + u), 0, 365, knob(u)))   #         FX1-4 Dry/Wet
    for u in range(4): m.append((cc(45 + u), 0, 366, knob(u)))   #         FX1-4 Knob1
    return m


# ---------------------------------------------------------------------------
# Stems mappings — all 5 pages for one deck
# ---------------------------------------------------------------------------

def _cmad_volume_rel(slot):
    """Stem Slot Volume (251) as a RELATIVE encoder, for the MK2's endless top knobs (Full Mix page).
    Absolute Direct (_cmad_volume) snaps to the encoder's emulated centre (half) on load; relative
    nudges from Traktor's CURRENT value (stems default to unity) so the mix starts FULL. Same proven
    relative encoding as the dial scroll/volume (_BROWSE_SCROLL), with the stem slot in @12."""
    b = bytearray(_BROWSE_SCROLL); b[12:16] = struct.pack('>i', slot); return bytes(b)

def _stems_mappings(deck):
    """Build all stems mappings for one deck (0=A, 1=B).
    Returns list of (midi_label, mtype, tid, cmad_bytes).
    All labels use Ch02 — no conflict with Ch01 performance/hardware controls.
    mtype: 0=In, 1=Out
    """
    base_filter  = 14 + deck * 4   # A: CC14-17   B: CC18-21
    base_filt_on = 46 + deck * 4   # A: CC46-49   B: CC50-53
    base_vol     = 22 + deck * 4   # A: CC22-25   B: CC26-29
    base_mute    = 54 + deck * 4   # A: CC54-57   B: CC58-61
    base_c_knob  = 62 + deck * 4   # A: CC62-65   B: CC66-69  (page C knobs: filter)
    base_c_btn   = 70 + deck * 4   # A: CC70-73   B: CC74-77  (page C buttons: mute)
    base_fine    = 91 + deck * 4   # A: CC91-94   B: CC95-98
    mute2 = [99,100,101,102]   if deck == 0 else [120,121,122,123]
    vol3  = [78,79,80,81]      if deck == 0 else [82,83,84,103]

    # Submix target = TP MappingTargetDeck enum (RemixDeckN/Slot, also used by Stem decks):
    #   Deck A stems -> 0,1,2,3 (RemixDeck1 Slot1-4);  Deck B stems -> 4,5,6,7 (RemixDeck2 Slot1-4).
    # This field is ABSOLUTE (encodes BOTH physical deck and stem slot); DDIF is ignored for
    # Submix commands. Previously Deck B reused 0-3 and therefore collapsed onto Deck A.
    # Stem track layout (standard): slot1=Drums, slot2=Bass, slot3=Other, slot4=Vocals.
    slots = [deck * 4 + s for s in range(4)]
    m = []
    for i, slot in enumerate(slots):

        # --- Page A: Stem Filter (display knobs + filter-on buttons) ---
        m.append((f"Ch02.CC.{base_filter +i:03d}", 0, 249, _cmad_filter(slot)))
        m.append((f"Ch02.CC.{base_filt_on+i:03d}", 0, 250, _cmad_filter_on(slot)))
        m.append((f"Ch02.CC.{base_filt_on+i:03d}", 1, 250, _cmad_led_out(slot)))

        # --- Page B: Volume (encoder turn) + Mute (encoder push) ---
        m.append((f"Ch02.CC.{base_vol +i:03d}", 0, 251, _cmad_volume(slot)))
        m.append((f"Ch02.CC.{base_mute+i:03d}", 0, 259, _cmad_mute(slot)))
        m.append((f"Ch02.CC.{base_mute+i:03d}", 1, 259, _cmad_led_out(slot)))

        # --- Page C: Mix Ctrl — Filter (knobs) + Mute (buttons + LED) ---
        m.append((f"Ch02.CC.{base_c_knob+i:03d}", 0, 249, _cmad_filter(slot)))
        m.append((f"Ch02.CC.{base_c_btn +i:03d}", 0, 259, _cmad_mute(slot)))
        m.append((f"Ch02.CC.{base_c_btn +i:03d}", 1, 259, _cmad_led_out(slot)))

        # --- Page D: Fine Volume (display knobs) + Mute (display buttons + LED) ---
        m.append((f"Ch02.CC.{base_fine+i:03d}", 0, 251, _cmad_volume(slot)))
        m.append((f"Ch02.CC.{mute2[i]:03d}",    0, 259, _cmad_mute(slot)))
        m.append((f"Ch02.CC.{mute2[i]:03d}",    1, 259, _cmad_led_out(slot)))

        # --- Page E: Full-range Volume (display knobs); buttons reuse Page D mute CCs ---
        # RELATIVE (endless top knobs): nudges from Traktor's full default so the mix starts at full,
        # instead of the absolute knob snapping to its emulated centre (half) on load.
        m.append((f"Ch02.CC.{vol3[i]:03d}", 0, 251, _cmad_volume_rel(slot)))

    return m   # 13 entries per slot x 4 slots = 52 per deck


# ---------------------------------------------------------------------------
# Parse Reybans TSI — extract raw DEVI blobs (no rebuild, byte-perfect)
# ---------------------------------------------------------------------------

def parse_reybans_raw(path):
    """Return list of (name, raw_devi_bytes) for all devices in the TSI.
    The raw bytes are used as-is so performance mappings are 100% original.
    """
    with open(path, "rb") as f:
        raw = f.read()
    m = re.search(rb'Value="([A-Za-z0-9+/=]+)"', raw)
    data = base64.b64decode(m.group(1))

    # DIOM header (8) + DIOI frame (12) = 20 bytes, then DEVS frame
    devs_offset = 20
    devs_len = struct.unpack('>I', data[devs_offset+4:devs_offset+8])[0]
    devs_data = data[devs_offset+8:devs_offset+8+devs_len]

    ndev = struct.unpack('>I', devs_data[:4])[0]
    dp = 4
    result = []
    for _ in range(ndev):
        devi_len = struct.unpack('>I', devs_data[dp+4:dp+8])[0]
        blob = devs_data[dp:dp+8+devi_len]   # DEVI tag + length + payload
        name = "Unknown"
        ddic_idx = blob.find(b'DDIC')
        if ddic_idx >= 0:
            name, _ = read_utf16(blob, ddic_idx+8)
        result.append((name, blob))
        dp += 8 + devi_len
    return result


# ---------------------------------------------------------------------------
# Build a DEVI frame
# ---------------------------------------------------------------------------

def build_device_raw(device_name, deck_target, mappings):
    all_dcdts = _all_dcdt_entries()
    ddci = frame('DDCI', struct.pack('>I', len(all_dcdts)) + b''.join(all_dcdts))
    ddco = frame('DDCO', struct.pack('>I', len(all_dcdts)) + b''.join(all_dcdts))
    dddc = frame('DDDC', ddci + ddco)

    cmais = []
    dcbms = []
    for bid, (label, mtype, tid, cmad_bytes) in enumerate(mappings, start=1):
        body  = struct.pack('>III', bid, mtype, tid)
        body += frame('CMAD', cmad_bytes)
        cmais.append(frame('CMAI', body))
        dcbms.append(frame('DCBM', struct.pack('>I', bid) + utf16be_str(label)))

    cmas = frame('CMAS', struct.pack('>I', len(cmais)) + b''.join(cmais))
    dcbm_container = frame('DCBM', struct.pack('>I', len(dcbms)) + b''.join(dcbms))
    ddcb = frame('DDCB', cmas + dcbm_container)

    ddif = frame('DDIF', struct.pack('>I', deck_target))
    ddiv = frame('DDIV', utf16be_str("2.6.1 Dev") + struct.pack('>I', 449))
    ddic = frame('DDIC', utf16be_str(device_name))
    ddpt = frame('DDPT', utf16be_str("All Ports") + utf16be_str("All Ports"))
    dvst = frame('DVST', struct.pack('>I', 1) + b'\x00' * 16)

    ddat = frame('DDAT', ddif + ddiv + ddic + ddpt + dddc + ddcb + dvst)
    return frame('DEVI', utf16be_str('Generic MIDI') + ddat)


# ---------------------------------------------------------------------------
# NCC page XML generation — ALL 5 pages generated fresh each run
# ---------------------------------------------------------------------------

_LABELS = ['Drums', 'Bass', 'Other', 'Vocals']   # knob 1-4

def _ncc_btn(bid, cc, name, ch=0):
    # Gate mode: sends 127 on press-down, 0 on release.
    # Traktor Toggle(1) only acts on values >= threshold (127), ignores 0.
    # Result: each physical press = one toggle event in Traktor (clean 2-press cycle).
    # ch=15 (MIDI Ch16) is used for all stems controls — completely conflict-free.
    return (
        f'\n          <button version="1" id="Button{bid}">\n'
        f'            <controller>{cc}</controller>\n'
        f'            <channel>{ch}</channel>\n'
        f'            <off>0</off>\n'
        f'            <on>127</on>\n'
        f'            <last>0</last>\n'
        f'            <behavior onIfDown="on">gate</behavior>\n'
        f'            <reaction>ondown</reaction>\n'
        f'          <name>{name}</name></button>'
    )

def _ncc_knob(kid, cc, name, ch=0, kdefault=64):
    return (
        f'\n          <knob version="1" id="Knob{kid}">\n'
        f'            <controller>{cc}</controller>\n'
        f'            <channel>{ch}</channel>\n'
        f'            <min>0</min>\n'
        f'            <max>127</max>\n'
        f'            <default>{kdefault}</default>\n'
        f'            <last>{kdefault}</last>\n'
        f'            <range>360</range>\n'
        f'            <steps>20</steps>\n'
        f'            <bipolar>off</bipolar>\n'
        f'          <name>{name}</name></knob>'
    )

def _ncc_raw_page(page_name, buttons, knobs):
    """Generate an NCC page. Each entry is (cc, name) or (cc, name, ch).
    Stems pages use ch=15 (MIDI Ch16). Performance pages use ch=0 (MIDI Ch01).
    """
    parts = [f'\n        <page name="{page_name}">']
    for i, item in enumerate(buttons, 1):
        ch = item[2] if len(item) > 2 else 0
        parts.append(_ncc_btn(i, item[0], item[1], ch))
    for i, item in enumerate(knobs, 1):
        ch = item[2] if len(item) > 2 else 0
        parts.append(_ncc_knob(i, item[0], item[1], ch))
    parts.append('\n        </page>')
    return ''.join(parts)

def _stems_page(page_name, k_a, k_b, b_a, b_b, k_lbl, b_lbl, kdefault=64):
    # ch=1 (MIDI Ch02) for all stems controls — avoids Ch01 conflicts
    parts = [f'\n        <page name="{page_name}">']
    for i, (cc, s) in enumerate(zip(b_a, _LABELS), 1):
        parts.append(_ncc_btn(i,  cc, f'{s} {b_lbl} A', ch=1))
    for i, (cc, s) in enumerate(zip(b_b, _LABELS), 5):
        parts.append(_ncc_btn(i,  cc, f'{s} {b_lbl} B', ch=1))
    for i, (cc, s) in enumerate(zip(k_a, _LABELS), 1):
        klabel = f'{s} {k_lbl} A' if k_lbl else f'{s} A'
        parts.append(_ncc_knob(i, cc, klabel, ch=1, kdefault=kdefault))
    for i, (cc, s) in enumerate(zip(k_b, _LABELS), 5):
        klabel = f'{s} {k_lbl} B' if k_lbl else f'{s} B'
        parts.append(_ncc_knob(i, cc, klabel, ch=1, kdefault=kdefault))
    parts.append('\n        </page>')
    return ''.join(parts)

# Page A: Filter sweep + Filter on/off buttons
_PAGE_FILTER = _stems_page('Stems Filter',
    k_a=[14,15,16,17], k_b=[18,19,20,21],
    b_a=[46,47,48,49], b_b=[50,51,52,53],
    k_lbl='', b_lbl='Mute')

# Page B: Encoder turns = Volume, Encoder pushes = Mute
_PAGE_ENCODERS = _stems_page('Stems Encoders',
    k_a=[22,23,24,25], k_b=[26,27,28,29],
    b_a=[54,55,56,57], b_b=[58,59,60,61],
    k_lbl='Vol', b_lbl='Mute')

# Page C: Mix Ctrl — filter knobs + mute buttons (all stems, both decks)
_PAGE_MIX_CTRL = _stems_page('Stems Mix Ctrl',
    k_a=[62,63,64,65], k_b=[66,67,68,69],
    b_a=[70,71,72,73], b_b=[74,75,76,77],
    k_lbl='', b_lbl='Mute')

# Page D: Fine Volume (display knobs) + Mute (display buttons with LED)
_PAGE_FINE = _stems_page('Stems Fine Vol',
    k_a=[91,92,93,94], k_b=[95,96,97,98],
    b_a=[99,100,101,102], b_b=[120,121,122,123],
    k_lbl='Vol', b_lbl='Mute')

# Page E: Full Mix Volume + Mute (buttons shared with Page D)
# Volume knobs start at FULL (127), matching Traktor's stem default (unity) so the mix isn't
# halved on load; other pages keep center (64) for their filter / FX-dry-wet knobs.
_PAGE_FULL = _stems_page('Stems Full Mix',
    k_a=[78,79,80,81], k_b=[82,83,84,103],
    b_a=[99,100,101,102], b_b=[120,121,122,123],
    k_lbl='Mix', b_lbl='Mute', kdefault=127)

# Performance pages F-H — all CC1-48 on Ch01, matching original Reybans NCM2 exactly.
# Stems devices only listen on Ch02, so no conflict possible.
_PAGE_PERF_F = _ncc_raw_page('FX 1 + 2',
    buttons=[(1,'FX1 ON'),(2,'FX1 B1'),(3,'FX1 B2'),(4,'FX1 B3'),
             (5,'FX2 ON'),(6,'FX2 B1'),(7,'FX2 B2'),(8,'FX2 B3')],
    knobs=  [(9,'FX1 D/W'),(10,'FX1 K1'),(11,'FX1 K2'),(12,'FX1 K3'),
             (13,'FX2 D/W'),(14,'FX2 K1'),(15,'FX2 K2'),(16,'FX2 K3')]
)
_PAGE_PERF_G = _ncc_raw_page('FX 3 + 4',
    buttons=[(17,'FX3 ON'),(18,'FX3 B1'),(19,'FX3 B2'),(20,'FX3 B3'),
             (21,'FX4 ON'),(22,'FX4 B1'),(23,'FX4 B2'),(24,'FX4 B3')],
    knobs=  [(25,'FX3 D/W'),(26,'FX3 K1'),(27,'FX3 K2'),(28,'FX3 K3'),
             (29,'FX4 D/W'),(30,'FX4 K1'),(31,'FX4 K2'),(32,'FX4 K3')]
)
_PAGE_PERF_H = _ncc_raw_page('FX All',
    buttons=[(33,'FX1 ON'),(34,'FX2 ON'),(35,'FX3 ON'),(36,'FX4 ON'),
             (37,'FX1 B1'),(38,'FX2 B1'),(39,'FX3 B1'),(40,'FX4 B1')],
    knobs=  [(41,'FX1 D/W'),(42,'FX2 D/W'),(43,'FX3 D/W'),(44,'FX4 D/W'),
             (45,'FX1 K1'),(46,'FX2 K1'),(47,'FX3 K1'),(48,'FX4 K1')]
)

# 8 display-section pages total: A-E stems, F-H Reybans performance controls.
# Full Mix is placed FIRST (display index 0) so the MK2 boots showing the full-mix mixer —
# the hardware always defaults to page index 0, so a stored current_index won't stick.
# Only Filter<->Full Mix swap positions; B/C/D and the perf pages keep their groups.
# Pad groups are NOT reordered, so Group A keeps the stems pads (just shows Full Mix knobs).
_ALL_PAGES = (_PAGE_FULL + _PAGE_ENCODERS + _PAGE_MIX_CTRL + _PAGE_FINE + _PAGE_FILTER
              + _PAGE_PERF_F + _PAGE_PERF_G + _PAGE_PERF_H)


# ---------------------------------------------------------------------------
# NCC patching — replaces full pages blocks (idempotent, safe to re-run)
# ---------------------------------------------------------------------------

def _replace_pages_block(content, section_start, new_pages):
    """Replace content of <pages>...</pages> within a controller section."""
    pages_open = content.find('<pages>', section_start)
    if pages_open == -1:
        return content, False
    pages_close = content.find('</pages>', pages_open)
    if pages_close == -1:
        return content, False
    return content[:pages_open+7] + new_pages + content[pages_close:], True


def patch_ncc(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    original_len = len(content)

    # REMOVE handleGroupControls. That flag puts the Group A-H buttons under MIDI control (needed
    # for custom LED colors) BUT it disables the hardware's native group switching — which is what
    # switches both the A-H pad pages AND the stems display pages. With it present, all paging is
    # stuck on one page. FUNCTION FIRST: strip it so the pages switch again. (Custom A-H colors
    # need it back + a full modifier-paging rewrite of pads AND stems — a separate, bigger job.)
    content, _nh = re.subn(r'\s*<handleGroupControls/>', '', content)
    print(f"  [NCC] handleGroupControls REMOVED -> native A-H page switching restored ({_nh})")

    # 1. Replace pages block in MK2 section
    mk2_pos = content.find('<controller type="Maschine Controller MK2">')
    if mk2_pos != -1:
        content, ok = _replace_pages_block(content, mk2_pos, _ALL_PAGES)
        print(f"  [NCC] MK2 pages block replaced: {ok}")
    else:
        print("  [NCC] WARNING: MK2 controller section not found")

    # 2. Replace pages block in MK1 section (Maschine Controller, before MK2)
    mk1_pos = content.find('<controller type="Maschine Controller">')
    mk2_pos2 = content.find('<controller type="Maschine Controller MK2">')
    if mk1_pos != -1 and mk1_pos < mk2_pos2:
        content, ok = _replace_pages_block(content, mk1_pos, _ALL_PAGES)
        print(f"  [NCC] MK1 pages block replaced: {ok}")
    else:
        print("  [NCC] INFO: MK1 not found before MK2 — skipping")

    # 3. Remove Performance midi-map if still present
    perf_key = '<midi-map type="MaschineMK2" name="Performance"'
    perf_pos = content.find(perf_key)
    if perf_pos != -1:
        ws_start = perf_pos
        while ws_start > 0 and content[ws_start-1] in ' \t':
            ws_start -= 1
        if ws_start > 0 and content[ws_start-1] == '\n':
            ws_start -= 1
        depth = 0
        i = perf_pos
        perf_end = -1
        while i < len(content):
            if content[i:i+9] == '<midi-map':
                depth += 1
            elif content[i:i+11] == '</midi-map>':
                depth -= 1
                if depth == 0:
                    perf_end = i + 11
                    break
            i += 1
        if perf_end != -1:
            content = content[:ws_start] + content[perf_end:]
            print("  [NCC] Removed Performance midi-map")
    else:
        print("  [NCC] INFO: Performance midi-map not present")

    # --- Color the Loops page (Group B) pads ---
    # MK2 indexed pad palette is undocumented (NI's own forum confirms it doesn't match
    # the manual). LOOPS_COLOR is a best-guess green; confirm on hardware. If wrong, set
    # CALIBRATE=True to paint pads 1-16 with indices 1-16 and read the palette off the unit.
    # Per-deck gradient + palette discovery: each pad a distinct color (so each loop SIZE is
    # distinguishable), with Deck B (Pad1-8) = palette indices 1-8 and Deck A (Pad9-16) = 9-16,
    # so the two decks sit in different halves of the palette. The user reports which index is
    # which colour; then we lock a deliberate single-hue gradient per deck. (color-mode 0.)
    mk2sec = content.find('<controller type="Maschine Controller MK2">')   # scope to MK2!

    # IDEMPOTENCY: the .ncc is patched IN PLACE, so a prior run's mode (e.g. leftover mode-1/2
    # from VU/color experiments) persists. Normalize EVERY MK2 pad LED back to color-mode 0
    # (the interactive, native press-lighting mode) up front, so each build starts clean.
    mk2grp = content.find('<groups>', mk2sec)
    mk2grpe = content.find('</groups>', mk2grp)
    seg0 = content[mk2grp:mk2grpe]
    seg0, n0 = re.subn(r'(<unit color-type="\d+" color-mode=")\d+(")', r'\g<1>0\g<2>', seg0)
    content = content[:mk2grp] + seg0 + content[mk2grpe:]
    print(f"  [NCC] MK2 pad LEDs normalized to mode 0 (interactive) — {n0} units")

    gb = content.find('<group name="Pad Page B"', mk2sec)
    gc = content.find('<group name="Pad Page C"', gb)
    if mk2sec != -1 and gb != -1 and gc != -1:
        block = content[gb:gc]
        for pid in range(1, 17):
            color = pid   # Pad1..16 -> palette index 1..16  (Deck B=1-8, Deck A=9-16)
            block = re.sub(
                rf'(<led version="1" id="Pad{pid}[BHS]">\s*<display type="0">\s*<unit color-type="\d+" color-mode="\d+" color-on-index=")\d+(" color-off-index=")\d+(")',
                rf'\g<1>{color}\g<2>{color}\g<3>', block)
        content = content[:gb] + block + content[gc:]
        print("  [NCC] Group B colors -> per-pad palette discovery (Deck B=idx1-8, Deck A=idx9-16)")

    # --- Pad pages A,C-H: each on its OWN channel (kills cross-page note overlap) + per-deck
    # colors (Deck A top / Deck B bottom). B keeps its discovery colors set above. Colors are
    # provisional indices (palette TBD from hardware). (letter, next, channel, DeckA, DeckB) ---
    PAGES = [('A', 'B', 2, 6, 5), ('C', 'D', 3, 11, 2), ('D', 'E', 4, 8, 7),
             ('E', 'F', 5, 10, 9), ('F', 'G', 6, 4, 3), ('G', 'H', 7, 14, 13),
             ('H', None, 8, 16, 15)]
    for letter, nxt, ch, ca, cb in PAGES:
        g0 = content.find(f'<group name="Pad Page {letter}"', mk2sec)
        g1 = content.find(f'<group name="Pad Page {nxt}"', g0) if nxt else content.find('</groups>', g0)
        if g0 == -1 or g1 == -1:
            print(f"  [NCC] Group {letter}: NOT FOUND"); continue
        blk = content[g0:g1]
        blk = re.sub(r'(<pad subtype="trigger"[^>]*>\s*<note>\d+</note>\s*<channel>)0(</channel>)',
                     rf'\g<1>{ch}\g<2>', blk)               # re-channel input pads
        for pid in range(1, 17):
            c = ca if pid >= 9 else cb                       # Pad9-16=Deck A, Pad1-8=Deck B
            blk = re.sub(
                rf'(<led version="1" id="Pad{pid}[BHS]">\s*<display type="0">\s*<unit color-type="\d+" color-mode="\d+" color-on-index=")\d+(" color-off-index=")\d+(")',
                rf'\g<1>{c}\g<2>{c}\g<3>', blk)
        content = content[:g0] + blk + content[g1:]
        print(f"  [NCC] Group {letter} -> Ch{ch+1:02d}, Deck A=idx{ca}/Deck B=idx{cb}")

    # --- MK1 PORT: re-channel the MK1 ("Maschine Controller") pads exactly like the MK2 so
    # all 8 pad pages work with the UNCHANGED TSI. MK1 sends the same transport CCs (Play 108,
    # Record 109, Grid 107, Loop 104, Prev./Next 105/106, Browse 87, Group A-H 80-83/91-94) and
    # the display pages (stems + FX) are already written to MK1 above. MK1 pads are MONOCHROME
    # (no RGB) so colors are skipped. MK1 has NO Dial/jog -> knob-browse and Dial-push-load are
    # not available on MK1 (use a track-deck button workflow); documented as an MK1 limitation.
    mk1s = content.find('<controller type="Maschine Controller">')
    mk1e = content.find('<controller type="Maschine Controller MK2">')
    if mk1s != -1 and mk1e != -1 and mk1s < mk1e:
        seg1 = content[mk1s:mk1e]
        MK1_CH = {'A': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8}   # B stays Ch01 (ch0)
        MK1_NXT = {'A': 'B', 'C': 'D', 'D': 'E', 'E': 'F', 'F': 'G', 'G': 'H', 'H': None}
        nre = 0
        for L, ch in MK1_CH.items():
            g0 = seg1.find(f'<group name="Pad Page {L}"')
            nxt = MK1_NXT[L]
            g1 = seg1.find(f'<group name="Pad Page {nxt}"', g0) if nxt else seg1.find('</groups>', g0)
            if g0 == -1 or g1 == -1:
                continue
            blk = seg1[g0:g1]
            blk, c = re.subn(r'(<pad subtype="trigger"[^>]*>\s*<note>\d+</note>\s*<channel>)0(</channel>)',
                             rf'\g<1>{ch}\g<2>', blk)
            seg1 = seg1[:g0] + blk + seg1[g1:]; nre += c
        content = content[:mk1s] + seg1 + content[mk1e:]
        print(f"  [NCC] MK1 pads re-channeled per group (A,C-H -> Ch03-09; {nre} pads); B stays Ch01")
        # MK1 template index -> 0 (Full Mix is page index 0 in _ALL_PAGES, so MK1 boots to it too)
        content, _mi = re.subn(
            r'(<controller type="Maschine Controller">\s*<wrapmode>0</wrapmode>\s*<current_index>)\d+(</current_index>)',
            r'\g<1>0\g<2>', content)

    # --- Physical Group A-H buttons: each a distinct color (matches its page) ---
    mk3sec = content.find('<controller type="Maschine Controller MK3">')
    seg = content[mk2sec:mk3sec]
    # Group A-H DISTINCT colors via ARGB color-on/color-off (the form #2371, a real MK2 mapping,
    # uses for distinct group colors). The palette color-on-index form does NOT render distinct
    # on the group buttons in any mode (mode 0 idx9 / mode 1 idx1-8 all failed). ARGB = decimal
    # 0xFF000000 | R<<16 | G<<8 | B, channels 0-127 (NI 7-bit). on==off so the idle color IS the hue.
    def _argb(r, g, b): return 0xFF000000 | (r << 16) | (g << 8) | b
    GBTN = {'A': _argb(127, 0, 0),   'B': _argb(127, 63, 0),  'C': _argb(127, 127, 0),
            'D': _argb(0, 127, 0),   'E': _argb(0, 127, 127), 'F': _argb(0, 0, 127),
            'G': _argb(63, 0, 127),  'H': _argb(127, 0, 127)}
    for L, argb in GBTN.items():
        for suf in 'BHS':
            # match the color block whether currently in -index or ARGB form (idempotent)
            seg = re.sub(
                rf'(<led version="1" id="Group{L}{suf}">\s*<display type="0">\s*<unit color-type="\d+" )color-mode="\d+" color-on(?:-index)?="\d+" color-off(?:-index)?="\d+"',
                rf'\g<1>color-mode="0" color-on="{argb}" color-off="{argb}"', seg)
    content = content[:mk2sec] + seg + content[mk3sec:]
    print("  [NCC] Group A-H buttons colored distinctly")

    # Group G VU REMOVED: a moving VU on the pads is only proven on the Maschine MIKRO
    # (#10371/#3589) - no MK2 mapping does it, and the mode-2 blend it needed kept blanking
    # Group G + breaking pad colors. G is now a normal mode-0 colored page (no VU). Do NOT
    # re-add a pad VU on the MK2 without an actual working MK2 reference to copy.

    # Group E (key page): all key-shift pads one matching color; the reset pad (key 0 ->
    # Pad5=note64/E4 deck B, Pad13=note72/C5 deck A) a DIFFERENT color so it stands out. (mode 0)
    e0 = content.find('<group name="Pad Page E"', mk2sec)
    e1 = content.find('<group name="Pad Page F"', e0)
    if e0 != -1 and e1 != -1:
        blk = content[e0:e1]
        for pid in range(1, 17):
            col = 4 if pid in (5, 13) else 6   # reset pads = idx4 (distinct), shifts = idx6 (matching)
            blk = re.sub(
                rf'(<led version="1" id="Pad{pid}[BHS]">\s*<display type="0">\s*<unit color-type="\d+" color-mode=")\d+(" color-on-index=")\d+(" color-off-index=")\d+(")',
                rf'\g<1>0\g<2>{col}\g<3>{col}\g<4>', blk)
        content = content[:e0] + blk + content[e1:]
        print("  [NCC] Group E -> shifts idx6 matching, reset (Pad5/Pad13) idx4 distinct")

    # (Pad colors stay color-mode 0: one native color per page, INTERACTIVE press lighting.
    # Mode-1/2 with on==off rendered distinct hues but went "dead" - input-only pad pages have
    # no Traktor LED feedback to drive the on-state, so the press-lighting is lost. Keeping the
    # interactive mode-0 look. Vivid distinct colors WITH interactivity would need per-pad
    # state-LED output mappings - a separate, bigger job, offered if wanted.)

    # Transport/master buttons were NCC 'toggle' (latches 127/0); with a Traktor Toggle mapping
    # that needs TWO presses per action. Switch them to 'gate' so each press fires once.
    for bid in ['Play', 'Restart', 'Rec', 'Grid', 'Enter', 'Push', 'StepL', 'StepR',
                'MasterL', 'MasterR', 'Browse', 'NoteRep', 'Mute',  # MK2 ids ('NoteRep' = Note Repeat)
                'Record', 'Loop', 'Prev.', 'Next', 'Repeat']:       # MK1 ids ('Repeat' = Note Repeat)
        content = re.sub(
            rf'(<button version="1" id="{bid}">(?:(?!</button>).)*?<behavior onIfDown="on">)toggle(</behavior>)',
            r'\g<1>gate\g<2>', content, flags=re.S)
    print("  [NCC] transport buttons -> gate (single-press)")

    # Rec LED off at startup: the Rec button defaulted to <last>127</last> (lit at boot).
    # Set it to 0 so the red light is off until recording actually starts.
    content, n = re.subn(
        r'(<button version="1" id="Rec">(?:(?!</button>).)*?<last>)127(</last>)',
        r'\g<1>0\g<2>', content, flags=re.S)
    print(f"  [NCC] Rec startup LED -> off ({n} button)")

    # Play LED should reflect deck PLAY STATE (green while playing), not the button press.
    # onIfDown="on" makes the LED local (lit only while held); flip to "off" so it follows the
    # incoming MIDI Traktor sends (the Play/Pause-state output on CC108). MK2 section only.
    mk2a = content.find('<controller type="Maschine Controller MK2">')
    mk3a = content.find('<controller type="Maschine Controller MK3">')
    seg = content[mk2a:mk3a]
    # Play LED follows play state; Grid LED follows Deck-B-focused state. Both need the button
    # LED to reflect incoming MIDI (onIfDown="off") instead of the local press.
    npg = 0
    for bid in ('Play', 'Grid', 'NoteRep', 'Mute'):   # NoteRep=Cruise; Mute LED follows stem-mute state
        seg, n = re.subn(
            rf'(<button version="1" id="{bid}">(?:(?!</button>).)*?<behavior )onIfDown="on"(>)',
            r'\g<1>onIfDown="off"\g<2>', seg, flags=re.S)
        npg += n
    content = content[:mk2a] + seg + content[mk3a:]
    print(f"  [NCC] Play/Grid/NoteRep LEDs -> follow Traktor state ({npg} buttons)")

    # MK1 'Repeat' (= Note Repeat) LED also follows the Cruise state (after gate patch).
    mk1a = content.find('<controller type="Maschine Controller">')
    mk1b = content.find('<controller type="Maschine Controller MK2">')
    if mk1a != -1 and mk1b != -1 and mk1a < mk1b:
        seg_mk1 = content[mk1a:mk1b]
        seg_mk1, nr = re.subn(
            r'(<button version="1" id="Repeat">(?:(?!</button>).)*?<behavior )onIfDown="on"(>)',
            r'\g<1>onIfDown="off"\g<2>', seg_mk1, flags=re.S)
        content = content[:mk1a] + seg_mk1 + content[mk1b:]
        print(f"  [NCC] MK1 Repeat LED -> follows Cruise state ({nr})")

    # Dial (browse knob): set to relative binary-offset mode (matches the working Maschine ONE
    # reference #3217, which scrolls the Traktor browser BOTH directions). "comp" (2's complement)
    # scrolled one-way only on this hardware; "offset" is the format the MK2 Dial pairs with here.
    mk2b = content.find('<controller type="Maschine Controller MK2">')
    mk3b = content.find('<controller type="Maschine Controller MK3">')
    seg2 = content[mk2b:mk3b]
    seg2, nd = re.subn(
        r'(<wheel version="1" id="Dial">(?:(?!</wheel>).)*?<controller)(?: mode="[^"]*")?(>101</controller>)',
        r'\g<1> mode="offset"\g<2>', seg2, flags=re.S)
    content = content[:mk2b] + seg2 + content[mk3b:]
    print(f"  [NCC] Dial -> relative (offset) browse-scroll mode ({nd} wheel)")

    # Default display page = Stems Full Mix is handled by page ORDER (Full Mix is now index 0
    # in _ALL_PAGES), because the MK2 boots to page index 0 and ignores a stored page index.
    # The controller-level current_index is the TEMPLATE selector; only one template exists,
    # so it must be 0 (setting it to 4 was a no-op that the hardware ignored).
    content, ni = re.subn(
        r'(<controller type="Maschine Controller MK2">\s*<wrapmode>0</wrapmode>\s*<current_index>)\d+(</current_index>)',
        r'\g<1>0\g<2>', content)
    print(f"  [NCC] MK2 template index -> 0; default page = Full Mix via page order ({ni})")

    # Scene button (CC112) drives the Round-2 layer shift (Modifier #2). Keep its NCC behavior as
    # "toggle" + TSI Hold — the pairing the user confirmed WORKING on hardware. (An earlier change
    # to gate+Toggle broke the working scene shift and is reverted here; this also converts any
    # in-place NCC left as "gate" by that build back to "toggle".)
    content, ns = re.subn(
        r'(<button version="1" id="Scene">\s*<controller>112</controller>'
        r'(?:\s*<[^>]+>[^<]*</[^>]+>)*?\s*<behavior onIfDown="on">)(?:gate|toggle)(</behavior>)',
        r'\g<1>toggle\g<2>', content)
    print(f"  [NCC] Scene button -> toggle (restored to working state) ({ns} buttons)")

    print(f"  [NCC] Size: {original_len:,} -> {len(content):,} bytes")
    return content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

print("=" * 60)
print("GideonSTEM-Maschine  TSI + NCC Builder  (v5 — 100% original, no third-party devices)")
print("=" * 60)

stems_a = _stems_mappings(0)
stems_b = _stems_mappings(1)
print(f"\n  Stems Deck A: {len(stems_a)} mappings (Ch02)")
print(f"  Stems Deck B: {len(stems_b)} mappings (Ch02)")

print("\n[2/4] Building TSI devices...")
# Performance devices: original blobs, untouched.
# Stems: ONE device, DDIF=0 (Focus). Verified against the working DJTT MF Twister
# 4-deck stems mapping ("TW STMS V1 CABD- Main"): it uses a single Generic MIDI
# device with DDIF=0 and encodes deck+slot ENTIRELY in the CMAD deck field as 0-15
# (0-3=DeckA, 4-7=DeckB, 8-11=DeckC, 12-15=DeckD). Splitting into per-deck devices
# with DDIF=1/2 conflicts with that absolute field and breaks all controls.
devi_stems = build_device_raw("Maschine MK2 Stems", 0, stems_a + stems_b)

# Performance device: the 8 pad pages (A-H) + transport + browser. All original.
perf_map = (
            # === LAYER 1 (Scene light OFF, Mod#2==0) — the 8 pad pages A-H ===
            _gate_list(_stems_pad_mappings(), MOD2, 0)     # A  stem mute + filter
            + _gate_list(_loops_mappings(), MOD2, 0)       # B  fixed-size loops
            + _gate_list(_beatjump_mappings(), MOD2, 0)    # C  beatjump +/-4..32
            + _gate_list(_remixcell_mappings(), MOD2, 0)   # D  remix cells 1-4
            + _gate_list(_pitchplay_mappings(), MOD2, 0)   # E  key-shift -4..+3
            + _gate_list(_loopmem_mappings(), MOD2, 0)     # F  loop station + 8 memories
            + _fxselect_mappings(0)    # G  FX1 selector 1-16 (load + hold-punch; self-gated)
            + _gate_list(_transport_mappings(), MOD2, 0)   # H  transport A/B
            # === LAYER 2 (Scene light ON, Mod#2==1) — A2-H2 ===
            + _gate_list(_stemfx_a2_mappings(), MOD2, 1)      # A2 stem FX send + FX-unit assign
            + _gate_list(_looproll_b2_mappings(), MOD2, 1)    # B2 loop roll
            + _gate_list(_phrasejump_c2_mappings(), MOD2, 1)  # C2 phrase jump +/-16/32/64/128
            + _gate_list(_remix_d2_mappings(), MOD2, 1)       # D2 remix cells 5-8
            + _gate_list(_toneplay_e2_mappings(), MOD2, 1)    # E2 chromatic tone-play
            + _gate_list(_looprec_f2_mappings(), MOD2, 1)     # F2 loop recorder (EXPERIMENTAL)
            + _fxselect_mappings(1)     # G2 FX1 selector 17-32 (load + hold-punch; self-gated)
            + _gate_list(_transport_h2_mappings(), MOD2, 1)   # H2 transport C/D
            # === LAYER 3 (Pattern light ON, Mod#2==2) — Pattern Player on FX3/FX4 ===
            + _gate_list(_patternpick_h3_mappings(), MOD2, 2)        # H3 pattern picker
            + _gate_list(_patternctrl_mappings(2, 12, 2), MOD2, 2)   # A3 FX3 control room (Ch03)
            + _gate_list(_patternctrl_mappings(3, 24, 0), MOD2, 2)   # B3 FX4 control room (Ch01)
            + _gate_list(_drummix_c3_mappings(), MOD2, 2)            # C3 drum mixer + routing (Ch04)
            + _gate_list(_toneplay_d3_mappings(), MOD2, 2)           # D3 tone-play drums (Ch05)
            + _gate_list(_sounddesign_e3_mappings(), MOD2, 2)        # E3 sound design (Ch06)
            + _gate_list(_gate_f3_mappings(), MOD2, 2)               # F3 gate & volume (Ch07)
            + _gate_list(_macros_g3_mappings(), MOD2, 2)             # G3 macros (Ch08)
            # === hardware controls (not pad pages) — ungated, active in all layers ===
            + _browse_mappings() + _transport_nav_mappings()
            # Mute button (CC119) = toggle-mute ALL stem slots of decks A-D (TID 259, level-preserving).
            # CC119 is switched to GATE mode in the NCC (see gate list below) so a Traktor Toggle fires
            # once per press (no double-press) — the same proven pairing as the stem-mute pads.
            + [("Ch01.CC.119", 0, 259, _cmad_mute(s)) for s in range(16)]
            # Mute LED follows the stem-mute STATE (slot 0 as representative; all 16 mute together):
            # Traktor sends 259's state out to CC119, and the NCC flips the Mute LED to follow MIDI.
            + [("Ch01.CC.119", 1, 259, _cmad_led_out(0))]
            # === the layer shifts: Scene (CC112)->Mod#2=1, Pattern (CC113)->Mod#2=2 ===
            + [("Ch01.CC.112", 0, MOD2, _cmad_setmod2(1)),
               ("Ch01.CC.113", 0, MOD2, _cmad_setmod2(2)),
               # Pattern button ALSO auto-arms the drum bus (Hold = on while in the Pattern layer):
               ("Ch01.CC.113", 0, 338, _cmad_fxon(3)),   # route Deck D -> FX3
               ("Ch01.CC.113", 0, 339, _cmad_fxon(3)),   # route Deck D -> FX4
               ("Ch01.CC.113", 0, 369, _cmad_fxon(2)),   # FX3 unit on
               ("Ch01.CC.113", 0, 369, _cmad_fxon(3)),   # FX4 unit on
               # FX1 ENGAGE on Solo (CC118) = Mod#3 latch: route both decks + FX1 on + wet (Hold,
               # follows the latching Solo button). Engage ON -> G/G2 pads just select (FX1 held on);
               # engage OFF -> pads hold-to-punch. (Solo chosen; Volume/Tempo/Swing CC7/3/9 collide
               # with the FX device CC1-48, and Volume is reserved for master volume.)
               ("Ch01.CC.118", 0, MOD3, _cmad_setmod2(1)),   # Mod#3 = 1 (engaged), Hold
               ("Ch01.CC.118", 0, 321, _cmad_fxon(0)),    # route deck A -> FX1
               ("Ch01.CC.118", 0, 321, _cmad_fxon(1)),    # route deck B -> FX1
               ("Ch01.CC.118", 0, 369, _cmad_fxon(0)),    # FX1 unit on
               # (FX1 wet is no longer forced full by Solo — the G pad swell owns the wet so it can
               #  ramp up and freeze/hold while engaged. Solo just holds the route + unit-on.)
               # Volume button (CC7) = "volume mode" while latched (Mod#4=1): the Dial becomes the
               # focused deck's channel volume (incremental). When off, the Dial keeps its browse /
               # Deck-D roles. On Page F the Volume light stays off (hardware), so the top knob keeps
               # its F assignment there; CC7 also reaches FX2 Btn2 in the FX device (shared message).
               ("Ch01.CC.007", 0, MOD4, _cmad_setmod2(1)),
               # Dial (CC101): browse (layers 1/2) / Deck-D vol (Pattern layer) ONLY when NOT in volume
               # mode; in volume mode it drives the focused deck's volume (TID 102, focused = -1).
               ("Ch01.CC.101", 0, 3200, _gate2(bytes(_BROWSE_SCROLL), MOD2, 0, MOD4, 0)),
               ("Ch01.CC.101", 0, 3200, _gate2(bytes(_BROWSE_SCROLL), MOD2, 1, MOD4, 0)),
               ("Ch01.CC.101", 0, 102,  _gate2(_cmad_voldial(3), MOD2, 2, MOD4, 0)),
               ("Ch01.CC.101", 0, 102,  _gate(_cmad_voldial(-1), MOD4, 1))])
devi_loops = build_device_raw("Maschine MK2 Performance", 0, perf_map)
print(f"  Performance: {len(perf_map)} mappings across pad pages A-H")

# FX device: my own FX control for the Group F/G/H display pages. Replaces the
# previously-kept third-party FX device, so this build is now 100% original.
fx_map = _fx_mappings()
devi_fx = build_device_raw("Maschine MK2 FX", 0, fx_map)
print(f"  FX: {len(fx_map)} mappings (Group F/G/H -> FX units 1-4)")

all_devis = devi_stems + devi_loops + devi_fx
n_devices = 3
devs  = frame('DEVS', struct.pack('>I', n_devices) + all_devis)
dioi  = frame('DIOI', struct.pack('>I', 1))
diom  = frame('DIOM', dioi + devs)

print(f"  Binary blob: {len(diom):,} bytes")

b64 = base64.b64encode(diom).decode('ascii')
xml  = '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'
xml += '<NIXML><TraktorSettings>'
xml += f'<Entry Name="DeviceIO.Config.Controller" Type="3" Value="{b64}"></Entry>\n'
xml += '<Entry Name="Flavour" Type="1" Value="-1"></Entry>\n'
xml += '<Entry Name="Version" Type="1" Value="0"></Entry>\n'
xml += '</TraktorSettings>\n</NIXML>'

with open(OUTPUT_TSI, 'w', encoding='utf-8') as f:
    f.write(xml)
print(f"  Written: {OUTPUT_TSI}  ({len(xml):,} chars)")

print("\n[3/4] Patching NCC...")
new_ncc = patch_ncc(INPUT_NCC)
with open(OUTPUT_NCC, 'w', encoding='utf-8') as f:
    f.write(new_ncc)
print(f"  Written: {OUTPUT_NCC}")

print("\n[4/4] Copying to F:/...")
for src, dst in [(OUTPUT_TSI, "F:/" + OUTPUT_TSI),
                 (OUTPUT_NCC, "F:/" + OUTPUT_NCC)]:
    try:
        shutil.copy2(src, dst)
        print(f"  Copied: {dst}")
    except Exception as e:
        print(f"  SKIP {dst}: {e}")

print("\n=== Done ===")
print("""
TRAKTOR CONTROLLER MANAGER SETUP:
  After importing gideonSTEMsMaster.tsi, you will see 3 devices (assign In+Out ports
  to the Maschine MK2 for each):
    1. Maschine MK2 Stems        -- stem vol/mute/filter, both decks (Ch02)
    2. Maschine MK2 Performance  -- pad pages A-H + transport + browser (Ch01/03-09)
    3. Maschine MK2 FX           -- FX units 1-4 on display pages F/G/H (Ch01)
  100% original devices — no third-party mapping data.

MASCHINE CONTROLLER EDITOR SETUP:
  Import gideonSTEMsMaster.ncc. Group A-H switches the pad page AND the screen layout.
  Display pages (boots to Full Mix):
    A Stems Full Mix  B Stems Encoders  C Stems Mix Ctrl  D Stems Fine Vol  E Stems Filter
    F FX 1+2          G FX 3+4          H FX All
  STEM LABELS (knobs 1-4 = deck A, 5-8 = deck B): Drums / Bass / Other / Vocals.
  LED FEEDBACK: mute and filter-on buttons reflect live Traktor state.
""")
