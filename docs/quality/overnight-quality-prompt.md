# Overnight quality session — fretboard-position-finder

You are running an unattended overnight session on the Django project
`fretboard-position-finder` (repo root is your working directory). Nobody will
answer questions until the morning. Work autonomously, make decisions yourself,
log them, and stop only when the stop criteria below are met.

## Goal

Raise **code quality, test coverage and maintainability** of this codebase to
the highest level that can be reached **without changing user-visible
behaviour**. Pure refactoring, tests, tooling, docs. Work in a measure → fix →
verify → commit → push loop until no further meaningful gain is possible.

## Hard constraints (never violate)

1. **No behaviour changes.** Every URL, view, API response, template output,
   fixture content and JS behaviour must stay identical. Refactor only.
2. **No migrations, no model field changes, no fixture data edits.**
   `manage.py makemigrations --check --dry-run` must stay clean.
3. **Git discipline.** Work on a branch cut from `master` (your worktree branch).
   Never commit to or push `master`, never force-push, never rewrite pushed
   history. Small atomic commits, imperative subject, body explains the why.
   Every commit ends with the trailer
   `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
   Push after every green commit. At the end open ONE pull request against
   `master` with a before/after summary. Do not merge it.
4. **Do not touch:** `apps/`, `.claude/worktrees/`, `docs/feedback/`,
   `pre-push-dump.sh`, `scripts/backup_db.*`, `scripts/create_db_dump.sh`,
   deployment files, `local_settings.py`, anything under `fixtures/` or
   `positionfinder/fixtures/`. Do not run `pre-push-dump.sh`.
5. **Secrets and data (Tier 2).** This is internal source code without personal
   data. Never print, log or commit the contents of `local_settings.py`, DB
   credentials, SECRET_KEY, or database dumps. Never add real personal data to
   tests; use synthetic data only.
6. **Dependencies.** No new runtime dependencies. Dev tooling (ruff, coverage,
   pytest plugins) is fine; pin it in `requirements.txt` (not
   `requirements-prod.txt`).
7. **Native apps are synced later** (web and Mac/iOS/Android must ship the same
   state). If you refactor anything under `static/studio`, `templates/studio`
   or icons, keep behaviour identical and list those files in the final report
   so the native sync can be done afterwards.
8. Run everything with the project venv: `.venv/bin/python -m pytest`,
   `.venv/bin/python manage.py ...`. Never use the system Python.

## Phase 0 — baseline (do this first, commit nothing yet)

- Confirm Postgres is reachable (`pg_isready`). If it is down, start it with
  `brew services start postgresql@<installed version>`. If the test database
  still cannot be created, add `fretboard/settings_test.py` (imports base
  settings, overrides DATABASES with SQLite in-memory) and point `pytest.ini`
  at it. Document this decision in the log.
- Run the full suite with coverage:
  `.venv/bin/python -m pytest --cov=positionfinder --cov=api --cov=utils --cov=fretboard --cov-report=term-missing -q`
- Record: tests collected / passed / failed / errors, wall time, total
  coverage, per-module coverage of the ten least-covered modules.
- Run `ruff check .` (install ruff into the venv if missing) and count findings
  by rule. Run `python manage.py check`.
- Write all baseline numbers to `docs/quality/2026-10-25-overnight-log.md`
  (create it). Keep a metrics table there; append a row after every
  iteration. Also log every non-obvious decision there in one line.

## Phase 1 — make the test suite trustworthy

- Fix or remove failing/erroring tests first. A test that documents a real
  bug is NOT removed: mark it `xfail(strict=True)` with the reason, and list
  the bug in the final report.
- Consolidate test locations: tests currently live in `tests/`,
  `positionfinder/tests/`, `positionfinder/test_*.py`, `positionfinder/tests_seo.py`
  and loose root files (`test_arpeggio_search.py`, `chord_analysis_test.py`,
  `run_seo_tests.py`, `test_seo.sh`). Move everything into `tests/` with a
  clear layout (`tests/unit/`, `tests/views/`, `tests/api/`, `tests/seo/`),
  keep every test's intent, and make `pytest` from the repo root collect all
  of them. Root-level `check_*.py` / `fix_*.py` scripts: if a `grep` over the
  repo and `git log -S` show they are one-off scripts, move them to
  `scripts/legacy/` with a README line each, or delete them if they are
  demonstrably superseded; log the decision.
- Add a `.coveragerc` (or `[tool.coverage]` in a new `pyproject.toml`) that
  omits migrations, tests, `manage.py`, settings and vendor files, and
  enables branch coverage.
- Make the suite fast and deterministic: use `pytest-django` DB reuse where
  safe, session-scoped fixtures for the fixture load, no network, no
  sleeps. Target: full suite under 2 minutes.

## Phase 2 — coverage

Target: **≥ 90 % line coverage and ≥ 80 % branch coverage** over
`positionfinder`, `api`, `utils`, `fretboard` (excluding the omit list), with
every remaining uncovered block either covered or justified in the log.
Priorities, in order:

1. Core music logic (pure functions, highest value, easiest to test):
   `position_calculator.py`, `optimized_positions.py`, `optimized_chords.py`,
   `get_position*.py`, `v_system_generator.py`, `ergonomic_position.py`,
   `chord_validation.py`, `note_validation.py`, `improved_chord_search.py`,
   `search_utils.py`, `template_notes.py`, `ordering.py`, `templatetags/`.
2. Views and API endpoints via Django test client: every URL in the URLconfs
   gets at least one 200-path test plus the relevant 404/400 paths;
   JSON responses are asserted on structure and representative values.
3. Management commands, context processors, sitemaps, SEO helpers.
4. Property-style tests where the domain allows it (e.g. every chord in the
   fixtures resolves to playable positions, every scale position is within the
   fretboard bounds, transposition is invertible). Use `hypothesis` only if it
   stays fast; otherwise parametrize over the fixture data.

Tests must assert real behaviour, not just "does not raise". Prefer small
focused tests over giant integration tests. Never weaken an existing assertion
to make coverage easier.

## Phase 3 — code quality and maintainability

- Add `ruff` configuration (line length 100, isort, pyflakes, pyupgrade,
  bugbear, django rules). Fix every finding; do not blanket-ignore rules
  except with a one-line justification in the config.
- Remove dead code: unused imports, unused functions/modules
  (verify with `grep -rn` across Python, templates and JS before deleting),
  commented-out blocks, duplicate implementations (several modules implement
  overlapping position/chord lookups — unify behind one implementation while
  keeping all call sites behaviour-identical, proven by tests written in
  Phase 2 BEFORE the refactor).
- Split oversized modules and functions: no function over ~60 lines, no
  module over ~800 lines in the core packages, unless splitting would hurt
  readability (log the exception).
- Add type hints and short docstrings to all public functions in the core
  packages. Run `mypy` in a lenient mode on the core packages and fix obvious
  errors; do not chase full strictness.
- Settings: make sure nothing in `fretboard/settings.py` depends on
  `local_settings.py` being present for tests and CI.
- JavaScript under `static/` (64 non-vendor files): remove files proven
  unused by `test_unused_files`-style checks and template grep, fix obvious
  duplication, but do not introduce a build chain or change behaviour. Only
  add JS tests if a zero-build runner (e.g. node's built-in test runner over
  pure functions) can be added without touching page code.
- Templates: remove unused templates and template tags only after a grep over
  views, includes and extends shows zero references.

## Phase 4 — tooling, CI, docs

- `Makefile` (or `scripts/dev.sh`) with targets: `test`, `coverage`, `lint`,
  `format`, `check` (runs all of them).
- `.pre-commit-config.yaml` with ruff (lint + format) and a pytest quick run
  of the unit tests.
- `.github/workflows/ci.yml`: Python matrix on the version in `.venv`,
  Postgres service, install `requirements.txt`, run `make check`, upload a
  coverage summary, fail below the coverage threshold reached in this session
  (`--cov-fail-under`).
- Update `docs/development.md` and the README test section to match the new
  layout and commands. Keep docs short and correct; no marketing text.

## Loop and stop criteria

Repeat: measure → pick the highest-value item → change → full verification →
commit → push → append metrics row. Full verification before EVERY commit:

```
.venv/bin/python -m pytest -q --cov --cov-report=term-missing
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
```
plus a smoke run of the test client against the main pages (`/`, chord,
scale, arpeggio, search, API root) returning 200.

**Stop only when ALL of these hold:**
- Suite green, deterministic (run it twice), under 2 minutes.
- Coverage ≥ 90 % line / ≥ 80 % branch on the core packages, or every
  remaining gap justified in the log.
- `ruff check` and `ruff format --check` clean, `manage.py check` clean,
  no pending migrations.
- No known dead code, no module/function over the size limits without a
  logged exception, public core functions typed and documented.
- CI workflow, pre-commit and Makefile in place and documented.
- Three consecutive iterations produced no measurable improvement in any
  metric.

Do not stop for any other reason. On errors, diagnose and retry; if a step is
truly impossible, log why, skip only that step and continue with the rest.
Never ask the user questions; make the call and log it.

## Final report (last thing you do)

Write `docs/quality/2026-10-25-overnight-report.md` and put the same content
in the PR description:
- Metrics table before/after (tests, time, line/branch coverage per package,
  ruff findings, modules/functions over size limits, LOC removed/added).
- Commit list with one line each.
- Bugs found but not fixed (with the xfail tests that pin them).
- Files under `static/studio`, `templates/studio` or icons that changed
  (for the native-app sync).
- Open risks and the recommended next steps.
