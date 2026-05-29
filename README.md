# GideonSTEM-Maschine

A **Traktor Pro 4** controller mapping for the **Native Instruments Maschine MK2**
(and **MK1** — same file set) — a 2-deck STEMS mixer + a **24-page** performance pad
surface (loops, beatjump, remix, key, tone-play, loop-roll, phrase-jump, loop recorder,
a drum **Pattern Player**, and an FX selector) + 4-unit FX control + browser/transport,
generated from a Python build. The 8 Group buttons × **3 layers** (Base / Scene / Pattern)
give 24 pad pages, plus 8 screen pages.

**Live (alpha):** https://maps.djtechtools.com/mappings/22496

> **100% original.** The mapping is generated entirely by `build_gideonStemsMaster.py`;
> it contains no third-party mapping data.

## Repo layout
| Path | What |
|------|------|
| `build_gideonStemsMaster.py` | The generator. `python3 build_gideonStemsMaster.py` rebuilds the `.tsi` + patches the `.ncc`. |
| `make_layout.py` | Generates all layout diagrams (control map, 24 pad maps across 3 layers, 8 screen maps, cheatsheets, full `layout_guide`) into `diagrams_out/`. |
| `make_public_catalog.py` | Generates the sanitized `TID_catalog_public.xlsx` (public TID reference; strips third-party content). |
| `gideonSTEMsMaster.tsi` / `.ncc` | Build outputs (the `.ncc` is also the build's in-place input). |
| `release_GideonSTEM-Maschine/` | Release bundle (renamed files + README + `diagrams/` + public spreadsheet). |
| `README_gideonSTEMsMaster.md` | **End-user guide** (install, full 24-page layout, diagrams, credits). |
| `HANDOFF.md` | **Maintainer guide** — architecture, build/test/publish, open issues. **Start here to contribute.** |
| `MASCHINE_MK2_PROJECT_REFERENCE.md`, `TRAKTOR_MAPPING_NOTES.md` | Deep TSI-format / command-ID reference (some sections predate the current build — see HANDOFF §10). |

## Build
```
python3 build_gideonStemsMaster.py
```
Requires Python 3 + Pillow (for the diagram scripts). Self-contained — reads only its own
`gideonSTEMsMaster.ncc` (committed) and writes the `.tsi` + `.ncc`.

## Status
**Alpha (v0.4).** Core stems / pads / transport / browse and the Scene + Pattern layers
are on hardware; the **Group G FX-select pads do not work reliably yet** (top fix in
progress), and some LED/metering outputs are pending hardware confirmation. See
`HANDOFF.md` §8.

## License
**GPL‑3.0** (see `LICENSE`) — © 2026 Garry Broeckling. The mapping is original work;
third‑party reference mappings used during development are **excluded** from this repo
(see `.gitignore`) and were studied only as format references. Security policy: `SECURITY.md`.
