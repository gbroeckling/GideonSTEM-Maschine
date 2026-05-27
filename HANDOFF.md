# GideonSTEM-Maschine — Maintainer Handoff

**Read this first if you are taking over the project.** It describes the *current shipped
state*, how to build/test/publish, the architecture decisions that actually matter, and
the open issues. Other docs in this folder are older and partly stale — see §10.

Last updated: 2026-05-26. Current release: **v0.2-alpha** (100% original — no third-party
mapping data), live at **https://maps.djtechtools.com/mappings/22496**.

---

## 1. What this project is
A **Traktor Pro 4** controller mapping for the **Native Instruments Maschine MK2** that
turns it into a 2-deck STEMS mixer + performance pad surface (loops, beatjump, remix,
key, loop-roll, VU meter, transport) + browser/transport controller.

Two deliverables, both required by the end user:
- `gideonSTEMsMaster.tsi` — the Traktor mapping (import in Controller Manager).
- `gideonSTEMsMaster.ncc` — the NI Controller Editor configuration (load in CE).

The **release** copies are renamed `GideonSTEM-Maschine.tsi/.ncc` and zipped with the
end-user `README` into `GideonSTEM-Maschine_v0.1-alpha.zip` (folder
`release_GideonSTEM-Maschine/`).

---

## 2. Build system — `build_gideonStemsMaster.py`
One command rebuilds everything:
```
python3 build_gideonStemsMaster.py
```
What it does:
1. Builds **all three** Traktor devices in code (no external mapping is read — as of v0.2
   the build is fully self-contained) and emits `gideonSTEMsMaster.tsi`.
2. **Patches `gideonSTEMsMaster.ncc` IN PLACE** (input == output; `INPUT_NCC == OUTPUT_NCC`).
   The big `.ncc` is the full NI Controller Editor config for *all* NI controllers; we only
   touch the `<controller type="Maschine Controller MK2">` section.
3. Auto-copies the outputs to `F:/` if mounted (the test-machine USB key — see §4).

**Idempotent:** safe to run repeatedly. The NCC patches replace whole blocks / set known
attributes, so re-running converges to the same output.

> **History:** earlier versions kept a third-party "Performance Pages" FX device verbatim
> from `Reybans_Maschine_MK2_reference.tsi`. v0.2 replaced it with an original
> `Maschine MK2 FX` device, so the build no longer reads any external mapping. The Reybans
> file is no longer a dependency (the `parse_reybans_raw`/`REYBANS_TSI` code is now dead).

### The Traktor side (TSI) — three devices (all original)
- **`Maschine MK2 Stems`** — ONE device, `DDIF=0` (Focus). Stem controls on **MIDI Ch02**.
- **`Maschine MK2 Performance`** — the 8 pad pages + transport/browser, mostly **Ch01** + the
  per-page pad channels (see §3).
- **`Maschine MK2 FX`** — FX units 1–4 for the Group F/G/H display pages, **Ch01 CC1–48**.
  The **FX unit (1–4) is the CMAD deck field (0–3)**, exactly like a deck; built from
  `_cmad_btn` (toggle) + `_cmad_filter` (Direct knob). See `_fx_mappings()`.

### STEMS encoding (the single most important gotcha)
Stem submix commands (Slot Volume 251, Mute 259, Filter Adjust 249, Filter On 250) encode
**deck AND slot together in the CMAD deck field as an absolute 0–15**: Deck A = 0–3,
Deck B = 4–7, C = 8–11, D = 12–15. Use **one Focus device**. **Do NOT** split into per-deck
`DDIF=1/2` devices — that conflicts with the absolute field and breaks all stem control.
(Verified against the DJTT MF Twister 4-deck stems mapping.)

---

## 3. Pad paging is CHANNEL-BASED (not modifiers)
This is the central architecture decision and it contradicts the older notes.

- The 16 pads are **re-channeled per Group page**. The hardware's **native Group A–H
  switching** changes which MIDI channel the pads send on, and Traktor listens per channel:
  - A = Ch03 · B = Ch01 · C = Ch04 · D = Ch05 · E = Ch06 · F = Ch07 · G = Ch03+Ch01 (VU) · H = Ch09
- Each Group also switches the on-screen **display page** (they move together).
- A **modifier-based** paging approach was tried earlier and **abandoned** — it broke 7 of 8
  pad pages on hardware. Do not resurrect it without a very good reason. (The stale notes in
  §10 describe that dead approach as if current — ignore those sections.)

### `handleGroupControls` — the key tradeoff
The NCC flag `<handleGroupControls/>` puts the Group A–H buttons under MIDI control (which is
what you'd need to set **custom A–H button LED colors**), **but it disables native group
switching → all paging sticks on one page.** We therefore **REMOVE** it (function over
cosmetics). Consequence: the Group buttons show the **native Maschine colors**, and custom
per-group colors are NOT possible without re-architecting paging onto modifiers.

### Default display page
The MK2 always boots to **display page index 0**, ignoring a stored `current_index`. So
"Stems Full Mix is the default" is achieved by **ordering** Full Mix first in `_ALL_PAGES`
(it's swapped with Filter). Pad groups are NOT reordered, so Group A keeps the stems pads.

### Browse Dial (was the long-standing bug)
The Dial relative-encoding format is set **only** by the NCC `<controller mode="…">`:
`comp` (2's-complement) scrolled one-way; **`offset` (binary-offset) scrolls both ways** —
matches the working "Maschine ONE" reference. The Traktor TSI encoder is format-agnostic
(byte-identical across all working references), so never chase this in the .tsi.

---

### Maschine MK1 port (same `.tsi` + `.ncc`)
The build also patches the **`Maschine Controller`** (MK1) NCC section so one file set drives
both controllers. MK1 sends the same transport CCs as MK2 (Play 108, Record 109, Grid 107,
Loop 104, Prev./Next 105/106, Browse 87, Group A–H 80–83/91–94) and the display pages are
written to MK1 too — so the only patch MK1 needs is the **same per-group pad re-channeling**
(A→Ch03 … H→Ch09, B stays Ch01), done in the `MK1 PORT` block in `patch_ncc`. RGB color
patches are MK2-only (MK1 is monochrome). MK1 has **no `<wheel id="Dial">`**, so the Dial-mode
patch simply doesn't match it; knob-browse / Dial-load are unavailable on MK1 (documented).
To extend other controllers, replicate this pattern on their NCC section (Mikro has 0 knobs —
needs a redesigned, pad-centric layout, not a drop-in).

## 4. How to test (the shuttle workflow)
There is **no Maschine on this build machine.** Testing happens on a **separate machine**;
files move on a **USB key (drive `F:`)**.
1. Build (`python3 build_gideonStemsMaster.py`). If the key is in this machine, it auto-copies
   `gideonSTEMsMaster.tsi/.ncc` to `F:/`. If `F:` is "not found", the key is in the test machine.
2. Carry the key to the test machine.
3. **Controller Editor:** File → Open Configuration → the `.ncc`.
4. **Traktor:** Preferences → Controller Manager → Import the `.tsi`; then **assign In-Port
   AND Out-Port** to the MK2 for **all three devices** (LEDs/VU need the Out-Port).

---

## 5. Pad pages & controls (ground truth = the build script)
Pad page note/channel/TID details live in `build_gideonStemsMaster.py` functions
(`_stems_pad_mappings`, `_loops_mappings`, `_beatjump_mappings`, `_remixcell_mappings`,
`_pitchplay_mappings`, `_looproll_mappings`, `_vu_mappings`, `_transport_mappings`,
`_transport_nav_mappings`). Summary:

| Group | Pads | Channel | TID |
|---|---|---|---|
| A | Stem mute + filter-on (per deck) | Ch03, notes 12–27 | 259 / 250 |
| B | Fixed loops 1/8…16 | Ch01, notes 24–39 | 2317 |
| C | Beatjump ±4/±8/±16/±32 | Ch04, notes 36–51 | 2380 |
| D | Remix Deck C 4×4 grid | Ch05, notes 48–63 | 600/616/632/648 +cell |
| E | Key shift −4…+3 (0=reset) | Ch06, notes 60–75 | 402 |
| F | Loop roll 1/16…8 | Ch07, notes 72–87 | 2317 |
| G | Main-output VU (LED out) | Ch03+Ch01, notes 84–99 | 2704/2705 |
| H | Play/Cue/Sync/Flux | Ch09, notes 96–111 | 100/206/125/2350 |

Transport/nav (Ch01 CCs): Play 108, Restart 104 (jumps start on **A and B**), Rec 109,
Grid 107 (Toggle Last Focus 2588), Step 105/106 (beatjump ∓4), Tempo 3 (Load Deck A 3076),
Enter 100 (Load Deck B), Dial push 102 (Load focused), Master 98/99 (browser scroll),
Dial turn 101 (browser scroll, encoder), Browse 87 (toggle browser view 4209).
Display knobs k1–8 = stems (CC vary per page); k1=Drums k2=Bass k3=Other k4=Vocals, k5–8 = 2nd deck.

The CMAD templates for 2317/2380/402/VU/scroll are **cloned byte-for-byte from working DJTT
mappings** and only the deck (offset 12) and value (offset 44) are patched — see the `_*_TEMPLATE`
hex constants. Don't hand-build these.

---

## 6. Diagrams (the listing image)
- `make_layout.py` → `master.png` (clean control map), `padA..H.png` (8 pad maps),
  `cheatsheet.png` (composite).
- `annotate_template.py` → `template_labeled.png` — writes labels onto the clean MK2
  template (`images/Screenshot 2026-05-26 221606.png`) via green-region auto-detection.
- `listing_image.png` = annotated control map + 8 pad maps; this is what's on the DJTT listing.
Regenerate: `python3 make_layout.py && python3 annotate_template.py`, then re-composite.

---

## 7. Publishing / updating on DJTechTools
Account: **garry@bcmail.net** (password is in the user's Engram memory / password sheet —
NOT stored here). Authenticated session uses `djtt/cookies.txt` + `curl --ssl-no-revoke`.

- **New mapping (2 steps):** `GET /mappings/new` (grab `authenticity_token`) → multipart
  `POST /mappings` (title, `mapping[midi_controller_ids][]=180` = NI Maschine MK2,
  `mapping[software_id]=29` = Traktor, description HTML, image). That redirects to
  `/mappings/{id}/mapping_versions/new` → multipart `POST .../mapping_versions` with
  `mapping_version[mapping_file]=@zip`, `version`, `notes`. **The mapping file is the 2nd step.**
- **Edit (e.g. change image/description):** `GET /mappings/22496/edit` (fresh token) →
  multipart `POST /mappings/22496` with `_method=patch` and the fields (resend title/
  controllers/software/description so they aren't wiped) + `mapping[image]=@png`.
- The `+1/0/-1` maturity is a **community vote**, not author-set; "alpha" lives in the description.

---

## 8. Open issues (alpha)
- **FX layer (Group F/G/H)** — rebuilt original in v0.2; built from proven CMAD helpers and
  the verified FX-unit-in-deck-field encoding, but **not yet hardware-confirmed**. Verify On/
  Dry-Wet/Knobs/Buttons for all 4 units. (Was hardware-untested at publish time.)
- **Group G VU movement** — metering output signature is in place (CtrlType=LED, Inter=Output,
  reso=0x3d800000, per-segment bands); needs hardware confirmation with the Out-Port assigned.
- **Custom A–H button colors** — not possible without `handleGroupControls`, which breaks
  native paging (§3). Would require migrating paging to modifiers across pads + display.
- **Grid / Play LEDs** — output mappings present (Grid lit on Deck B focus; Play green on play);
  verify on hardware.
- **Stems Full Mix default** — handled via page order; confirm it boots correctly on hardware.
- **Browse Dial** — FIXED (`offset` mode), user-confirmed bidirectional.

---

## 9. File inventory
- `build_gideonStemsMaster.py` — the generator (source of truth for the mapping).
- `gideonSTEMsMaster.tsi` / `.ncc` — current build (working filenames).
- `release_GideonSTEM-Maschine/` + `GideonSTEM-Maschine_v0.1-alpha.zip` — release bundle.
- `README_gideonSTEMsMaster.md` — **end-user** guide (also shipped in the zip as README.md).
- `Reybans_Maschine_MK2_reference.tsi` — **no longer used by the build** (v0.2 is self-
  contained). Third-party; **exclude from any public repo**. Safe to delete or archive.
- `make_layout.py`, `annotate_template.py`, `images/`, `*.png` — diagram generation.
- `djtt/` — DJTT session cookies, downloaded reference zips (`dl*.bin`), saved page HTML.
- Reference mappings (ground truth): `djtt/dl2371` (MK2 Remix), `cand_917.bin` (4Decks
  Cue/Fx/Stem, best-commented), `cand_1237.bin` (loops), `cand_6426.bin` (slicer/pitch),
  `dig_10371.bin`/`djtt/3589` (VU), `djtt/dl3217.bin` (Maschine ONE = offset Dial + focus),
  `ref_TW_stems_*` / `ref_Twisted_Gratification_*` (stems encoding), `dig_9481.bin` (Key 402).
- Decode helpers: `extract_vu.py`, `study_vu*.py`, plus the parser snippet in §9 of TRAKTOR_MAPPING_NOTES.

---

## 10. Older docs — what to trust
- `MASCHINE_MK2_PROJECT_REFERENCE.md` — **excellent deep reference** for the TSI binary format,
  enums, and TID lists. Trust those sections. **Ignore** its "current state / roadmap" and any
  modifier-paging plan — they predate the shipped channel-based build.
- `TRAKTOR_MAPPING_NOTES.md` — good format notes & TID list. **Its §9b "pad paging = modifiers"
  is the ABANDONED approach** — the shipped build is channel-based (§3 here wins).
- `README_gideonSTEMsMaster.md` — end-user facing, accurate.
- **This file (`HANDOFF.md`) is the current source of truth for project state & architecture.**

---

## 11. Engram / memory
Project context, fixes, and the DJTT upload flow are saved in Engram (search
"gideonStemsMaster", "djtechtools", "maschine"). The publish details + upload recipe are
Engram obs #455; the browse-knob fix is #454. DJTT credentials are in Engram #430.
