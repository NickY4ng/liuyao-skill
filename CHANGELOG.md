# Changelog

## [1.1.0] - 2026-05-01

### Added
- `hexagrams.py` — 64 hexagrams complete database
- `interpret.py` — Hexagram interpretation algorithm
- `liuyao.py` — Core Liu Yao logic module
- `validate_deep.py` — Deep validation tool for hexagram accuracy
- Test suite in `tests/test_liuyao.py`

### Fixed
- Step counter drift: now uses `len(session["yaos"])` as ground truth
- Pattern matching: substring match for hexagram names
- Gan-Zhi calendar calculation: correct day stem/branch offset
- Moving line detection: only Old Yang/Old Yin are moving lines
- Session file safety: atomic write with temp file + os.replace()
- `start_divination` no longer auto-tosses first coin

### Changed
- Updated `liuyao_interactive.py` with all 2026-04-27 fixes
- Updated `liuyao_interpret.py` with complete interpretation pipeline
- Refactored `naga.py` for better hexagram lookup
- Cleaned up dead code (removed YAO_TYPES, COIN_EMOJI mappings)

## [1.0.0] - 2026-04-19

### Added
- Initial release
- Interactive coin-toss divination (6 tosses)
- Basic hexagram interpretation
- Six Spirits arrangement
- Pattern analysis (Six Clash, Wandering Soul, Returning Soul)
- Emoji-based beautiful output
