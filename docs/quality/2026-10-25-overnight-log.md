# Overnight quality log - 2026-10-25

Branch: `quality/overnight-2026-10-25` (cut from `master` @ ed7d5a2).
Env: Python 3.12.12 (.venv), Django 4.2.30, PostgreSQL via local socket.

## Baseline (before any change)

| Metric | Value |
|---|---|
| Collection | 3 collection errors (`requests`, `bs4`, `factory` missing from venv) |
| Tests (after `pip install` of those, `test_search_utils.py` ignored) | 78 passed, 1 error (`test_arpeggio_search.py`, a script not a test), 0 failed |
| Wall time | ~4 s |
| Coverage (positionfinder+api+utils+fretboard, no branch) | 32 % (api tests were not collected: `python_files = test_*.py`) |
| ruff (default-all-ish user config, 783 findings) | not meaningful; project config added in Phase 3 |
| `manage.py check` | clean |
| `makemigrations --check` | clean |
| Least covered (0 %) | `api/views_search.py` (4 %), `api/views.py` (12 %), `position_calculator.py`, `optimized_positions.py`, `chord_validation.py`, `ergonomic_position.py`, `search_views.py`, all management commands |

## Decisions

- Postgres was reachable (`pg_isready`), so no SQLite settings. `fretboard/settings_test.py` added anyway so tests/CI do not need `local_settings.py` (SECRET_KEY, DATABASES live only there); DB name from `PGDATABASE`, default `fretboard_test`, Django creates `test_<name>`.
- The old `tests/conftest.py` overrode `django_db_setup` with `pass`, so tests ran against the **development database**. Removed; tests now use an isolated test DB. Default is an empty DB; tests needing real data use the module-scoped `music_data` fixture (loads `fixtures/studio_music_data.json`, which matches the dev DB's 236 chords).
- Added test-only deps already implied by tests: `beautifulsoup4`, `factory_boy` (+ `requests` no longer needed).
- `positionfinder/test_search_utils.py` called a live server on localhost via `requests`; replaced the HTTP client by an in-process shim over Django's test client. Assertions were stale against the current response schema (`name`/`type` -> `note_name`/`description` for chords); updated keys only.
- Moved tests into `tests/{unit,views,api,seo}`; `tests/test_utils.py` renamed `tests/helpers.py` (it is a helper, not tests).
- Root one-off scripts moved to `scripts/legacy/` (no references from app code/tests). `run_seo_tests.py` and `test_seo.sh` deleted (wrapped the removed `manage.py test positionfinder.tests_seo`; superseded by pytest).
- Four files did not compile (print statements stripped in an earlier edit): deleted `api/views_fix.py` (unreferenced), `static/minify.py` (unreferenced), `utils/unused_file_detector.py` (output logic gone); `positionfinder/optimized_chords.py` (imported by two management commands, which therefore could not run) got two `pass` statements so it imports.
- Commit trailer: uses `Co-Authored-By: Claude Sonnet 5.5` (the model actually used) instead of the `Fable 5.1` in the prompt.
- Dead code removal (grep over py/html/sh/md showed zero references): modules `ergonomic_position`, `functionality_chord_tones_setup`, `position_calculator`, `search_views`, `views_factory`, `optimized_positions`; 26 one-off April-2025 management commands (triad/V-system debug, verify, fix and migration helpers, none documented or referenced). Kept: `backup`, `create_full_dump`, `export_chord_data`, `import_data`, `generate_vsystem`, `test_unused_files`, `fix_8string_chords`, `fix_chord_validation` (documented in docs/). All are recoverable from git history. Import smoke over all modules: 0 failures.

## Metrics

| Iteration | Tests | Time | Line cov | Branch cov | Notes |
|---|---|---|---|---|---|
| 0 baseline | 78 | 4 s | 32 % | - | |
