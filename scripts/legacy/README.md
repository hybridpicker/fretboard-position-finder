# Legacy one-off scripts

Moved out of the repository root. None is imported by application code or
tests; they are kept for reference only and are not maintained.

- `add_arpeggios.py` - one-off arpeggio data insertion (see `fix_summary.md`).
- `arpeggio_search_debug.py` - manual arpeggio search debugging (formerly `test_arpeggio_search.py`).
- `check_a_minor_pentatonic.py`, `check_arpeggios.py` - ad-hoc data inspection.
- `check_logo_files.py` - superseded by `tests/views/test_logo_availability.py`.
- `check_spa_seo.py`, `check_url_seo.py` - live-server SEO checks (`python scripts/legacy/check_spa_seo.py <url>`); see `SEO_README.md`.
- `chord_analysis_test.py` - report script; the asserted part lives in `tests/unit/test_chord_analysis.py`.
- `cleanup_chord_nodes.py`, `create_fixtures.py`, `fix_arpeggio_urls.py`, `fix_search_arpeggios.py` - one-off data repair scripts.
