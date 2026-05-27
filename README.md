# GideonSTEM-Maschine

A **Traktor Pro 4** controller mapping for the **Native Instruments Maschine MK2** —
a 2-deck STEMS mixer + performance pad surface (loops, beatjump, remix, key, loop-roll,
VU meter, transport) + FX control + browser/transport, generated from a Python build.

**Live (alpha):** https://maps.djtechtools.com/mappings/22496

> **100% original.** The mapping is generated entirely by `build_gideonStemsMaster.py`;
> it contains no third-party mapping data.

## Repo layout
| Path | What |
|------|------|
| `build_gideonStemsMaster.py` | The generator. `python3 build_gideonStemsMaster.py` rebuilds the `.tsi` + patches the `.ncc`. |
| `make_layout.py`, `annotate_template.py` | Generate the labeled layout diagrams. |
| `gideonSTEMsMaster.tsi` / `.ncc` | Build outputs (the `.ncc` is also the build's in-place input). |
| `release_GideonSTEM-Maschine/` | Release bundle (renamed files + README + `diagrams/`). |
| `README_gideonSTEMsMaster.md` | **End-user guide** (install, full layout, diagrams, credits). |
| `HANDOFF.md` | **Maintainer guide** — architecture, build/test/publish, open issues. **Start here to contribute.** |
| `MASCHINE_MK2_PROJECT_REFERENCE.md`, `TRAKTOR_MAPPING_NOTES.md` | Deep TSI-format / command-ID reference (some sections predate the current build — see HANDOFF §10). |

## Build
```
python3 build_gideonStemsMaster.py
```
Requires Python 3 + Pillow (for the diagram scripts). Self-contained — reads only its own
`gideonSTEMsMaster.ncc` (committed) and writes the `.tsi` + `.ncc`.

## Status
**Alpha.** Core stems / pads / transport / browse confirmed on hardware; FX layer (v0.2)
and some LED/VU outputs are pending hardware confirmation. See `HANDOFF.md` §8.

## License
**GPL‑3.0** (see `LICENSE`) — © 2026 Garry Broeckling. The mapping is original work;
third‑party reference mappings used during development are **excluded** from this repo
(see `.gitignore`) and were studied only as format references. Security policy: `SECURITY.md`.
