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
├── fretboard/              # Main Django project
│   ├── settings.py         # Project settings
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI configuration
├── positionfinder/         # Main application
│   ├── models.py           # Models for scales and arpeggios
│   ├── models_chords.py    # Models for chords
│   ├── views.py            # Basic views
│   ├── views_scale.py      # Scale-specific views
│   ├── views_chords.py     # Chord-specific views
│   ├── views_arpeggio.py   # Arpeggio-specific views
│   ├── string_choices.py   # String configuration
│   ├── template_notes.py   # Note position mapping
│   └── get_position.py     # Position calculation logic
├── static/                 # Static assets (CSS, JS)
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
