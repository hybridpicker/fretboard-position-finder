# Fretboard Position Finder - Overview

## Project Overview

Fretboard Position Finder is a Django-based web application that visualizes scales, arpeggios, and chords on a guitar fretboard. The application supports both 6-string and 8-string guitar configurations, with separate PostgreSQL databases for each version.

## Primary Features

- Interactive fretboard visualization
- Support for scales, arpeggios, and chords
- Multiple position options for each musical element
- All 12 keys supported
- Both 6-string and 8-string guitar configurations

## System Architecture

### Tech Stack
- **Backend**: Django (Python)
- **Frontend**: JavaScript, HTML, CSS
- **Database**: PostgreSQL
- **Data Exchange**: JSON

### Key Components

1. **Models**: Define data structures for notes, scales, chords, and positions
2. **Views**: Handle HTTP requests and render templates
3. **Template System**: Renders the fretboard visualization
4. **Position Algorithms**: Calculate fretboard positions based on music theory

### Directory Structure

```
fretboard-position-finder/
├── fretboard/              # Django project: settings, settings_test (CI), urls, template tags
├── positionfinder/         # Main application
│   ├── models.py, models_chords.py     # Scales/arpeggios and chords (ChordNotes, ChordPosition)
│   ├── views_studio.py     # Studio single-page UI and /api/catalog/
│   ├── views.py, views_scale.py, views_chords.py, views_arpeggio.py, views_base.py
│   │                       # Classic views (/classic/, /scales, /chords, /arpeggios)
│   ├── chord_note_extraction.py        # Note walking/spelling for the chord view
│   ├── views_search.py, improved_chord_search.py, search_integration.py, search_utils.py
│   │                       # /search_json/ and query parsing
│   ├── get_position*.py, template_notes.py, *_setup.py   # Position calculation helpers
│   ├── v_system_generator.py           # V-System voicing generator
│   ├── seo_context_processor.py, sitemaps.py, templatetags/
│   └── management/commands/            # backup, create_full_dump, export_chord_data, import_data, generate_vsystem, test_unused_files
├── api/                    # REST API (views.py, views_search.py + search_direct/normalize/common)
├── tests/                  # pytest suite: unit, views, api, seo, commands
├── scripts/                # Helper scripts (legacy/ holds retired one-offs)
├── static/                 # Static assets (CSS, JS; static/studio is the Studio UI)
└── templates/              # HTML templates
```

## Application Flow

1. User selects a category (scale, arpeggio, chord)
2. User selects a specific musical element and root note
3. Application retrieves notes from the database
4. Application calculates positions on the fretboard
5. Positions are converted to JSON format
6. Frontend renders the positions on an interactive fretboard

## 6-String vs. 8-String

The project supports both 6-string and 8-string guitar configurations:

- **6-String**: Standard guitar tuning (E, A, D, G, B, E)
- **8-String**: Extended tuning (B, E, A, D, G, B, E, A)

Each version uses a separate PostgreSQL database but shares the same codebase. The application adapts to the string configuration based on database content.
