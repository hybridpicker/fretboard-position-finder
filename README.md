# Fretboard Position Finder

**Interactive guitar fretboard visualization for scales, chords, and arpeggios in all 12 keys**

## Features

- **Interactive Fretboard Display**: Visualize notes on the fretboard using HTML, CSS, and JavaScript.
- **Scales**: Major, Minor, Modes, Custom scales with all possible positions.
- **Arpeggios**: Major, Minor, Seventh, Extended arpeggios with multiple voicings.
- **Chords**:
  - Triads and seventh chords: Maj7, Dom7, Min7, m7♭5, Dim7.
  - V-System voicings (V3–V7, V8–V10) for 4‑note chords with fixture generation.
- **String Configurations**:
  - Standard 6‑string (E, A, D, G, B, E).
  - Extended 8‑string (B, E, A, D, G, B, E, A).
- **All 12 Keys Supported**: Generate positions for any root note.
- **Search & Filter**:
  - Find scales, chords, or arpeggios by name or note content.
  - API endpoints for JSON responses.
- **Fixtures & Management**:
  - `generate_v_system_fixture.py` script for auto-generating chord voicings.
  - Load data via Django fixtures (`python manage.py loaddata`).
- **Extensible Architecture**:
  - Modular Django apps for models, views, templates, and filters.
  - Pluggable string and tuning configurations.
- **Custom Template Filters**: Note naming, color coding, and display utilities.
- **Responsive & Themed UI**: Mobile-friendly layout and CSS theming.

## Tech Stack

- **Backend**: Django (Python 3.8+)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Database**: PostgreSQL (separate DBs for 6‑string and 8‑string)
- **Data Exchange**: JSON fixtures and REST APIs

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hybridpicker/fretboard-position-finder.git
   ```
2. Create and activate the Conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate fretboard
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy and configure environment variables in `.env`:
   ```ini
   DJANGO_SECRET_KEY=your_secret_key
   DATABASE_URL=postgres://user:pass@localhost:5432/fretboard6
   EXTRA_DATABASE_URL=postgres://user:pass@localhost:5432/fretboard8
   ```

## Configuration

In your `settings_dev.py` (or `settings.py`), add:
```python
TEMPLATES[0]['DIRS'] += [BASE_DIR / 'templates']
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR.parent / 'fretboard' / 'static_cdn'
FIXTURE_DIRS = [BASE_DIR / 'fixtures']
```

## Loading Data

```bash
python manage.py migrate
python manage.py loaddata v3_v7_voicings
# or any other fixture in /fixtures
```

## Running the Development Server

```bash
python manage.py runserver 0.0.0.0:8080
```

Open http://localhost:8080 to view the app.

## API Endpoints

- `GET /api/scales/?name=<scale>&root=<note>`
- `GET /api/arpeggios/?name=<type>&root=<note>`
- `GET /api/chords/?name=<type>&root=<note>`
- `GET /api/search/?q=<query>`

## Deployment

- **Server**: CentOS with Nginx & Gunicorn
- **Port**: 8080

Example Gunicorn command:
```bash
gunicorn fretboard.wsgi:application --bind 0.0.0.0:8080
```

## Contributing

- Create feature branches (`git checkout -b feature/xyz`).
- Follow PEP8 and Django best practices.
- Write tests using Django's testing framework.
- Run `flake8` and `npm lint` (if applicable) before committing.

## License

MIT License