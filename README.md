# Fretboard-Position-Finder
Position Generator on Guitar-Fretboard for Scales, Arpeggios, Chords in all 12 Keys

Fretboard-Position-Finder helps guitarists from nearly all levels to show chord-, scale and arpeggio-notes on the guitar fretboard.

## Powered with

It is based on the Framework Django. After writing the scale notes into the database, this app is able to create all possible variations with Python and renders them into a JSON file. JavaScript makes the data visible on the HTML fretboard.

   - Python
   - JavaScript
   - JSON
   
## Fretboard-Position-Finder in Action
https://github.com/hybridpicker/fretboard-position-finder/assets/40589021/d23ab0b0-7ac6-43af-b8cb-4007e0994221

## Idea
Design, Frontend and Backup-Code is made by Lukas Schönsgibl (aka hybridpicker)

## Website
https://guitar-positions.org

## Instructions

Need some little additions in **settings.py**:

For finding templates add this line into TEMPLATES:

```python
os.path.join(BASE_DIR, 'templates')
```

Then insert this block into **settings.py**:

```python

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'fretboard/static_cdn')

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
]
```

Fretboard-Position-Finder loads all fingerings, that are stored as **fixtures** with the migrate-command:
```python
python manage.py migrate
```