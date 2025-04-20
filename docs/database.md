# Database Configuration and Schema

This document describes the database structure and configuration for the Fretboard Position Finder project.

## Database Configuration

The project uses two separate PostgreSQL databases:
- **6-String Version**: `fretboard-devel`
- **8-String Version**: `fretboard`

To switch between versions, modify the database name in `local_settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # For 6-String: 'NAME': 'fretboard-devel',
        # For 8-String: 'NAME': 'fretboard',
        'NAME': 'fretboard',  # Current setting
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Database Schema

### Key Tables

1. **NotesCategory**
   - Categories for musical elements (scales, arpeggios, chords)
   
2. **Root**
   - Root notes (C, C#, D, etc.)
   - Contains pitch information
   
3. **Notes** (for scales and arpeggios)
   - Defines scale and arpeggio structures
   - References NotesCategory
   - Contains interval information
   
4. **NotesPosition**
   - Defines positions for scales and arpeggios
   - References Notes
   
5. **ChordNotes**
   - Defines chord structures
   - References NotesCategory
   - Contains string assignments
   
6. **ChordPosition**
   - Defines chord inversions
   - References ChordNotes

### Entity Relationship Diagram

```
┌───────────────┐         ┌───────┐
│ NotesCategory │◄────────┤ Notes │
└───────────────┘         └───┬───┘
                              │
                              │
                      ┌───────▼──────┐
                      │ NotesPosition │
                      └───────────────┘

┌───────────────┐         ┌───────────┐
│ NotesCategory │◄────────┤ ChordNotes │
└───────────────┘         └─────┬─────┘
                               │
                               │
                        ┌──────▼──────┐
                        │ChordPosition │
                        └─────────────┘
```

## Schema Details

### NotesCategory

```sql
CREATE TABLE positionfinder_notescategory (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(30) NOT NULL
);
```

Sample data:
- id=1, category_name='Scales'
- id=2, category_name='Arpeggios'
- id=3, category_name='Chords'

### Root

```sql
CREATE TABLE positionfinder_root (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    pitch INTEGER NOT NULL
);
```

Sample data:
- id=1, name='C', pitch=0
- id=2, name='C#', pitch=1
- id=3, name='D', pitch=2

### Notes (Scales and Arpeggios)

```sql
CREATE TABLE positionfinder_notes (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES positionfinder_notescategory(id),
    note_name VARCHAR(30) NOT NULL,
    ordering INTEGER NULL,
    chords VARCHAR(30) NULL,
    tonal_root INTEGER DEFAULT 0,
    first_note INTEGER DEFAULT 0,
    second_note INTEGER NULL,
    third_note INTEGER NULL,
    fourth_note INTEGER NULL,
    fifth_note INTEGER NULL,
    sixth_note INTEGER NULL,
    seventh_note INTEGER NULL,
    eigth_note INTEGER NULL,
    ninth_note INTEGER NULL,
    tenth_note INTEGER NULL,
    eleventh_note INTEGER NULL,
    twelth_note INTEGER NULL
);
```

### NotesPosition

```sql
CREATE TABLE positionfinder_notesposition (
    id SERIAL PRIMARY KEY,
    notes_name_id INTEGER REFERENCES positionfinder_notes(id),
    position_order VARCHAR(20) NULL,
    position_order_number INTEGER NULL,
    first_note INTEGER DEFAULT 0,
    first_note_string VARCHAR(30) NULL,
    second_note INTEGER NULL,
    second_note_string VARCHAR(30) NULL,
    third_note INTEGER NULL,
    third_note_string VARCHAR(30) NULL,
    fourth_note INTEGER NULL,
    fourth_note_string VARCHAR(30) NULL,
    fifth_note INTEGER NULL,
    fifth_note_string VARCHAR(30) NULL,
    sixth_note INTEGER NULL,
    sixth_note_string VARCHAR(30) NULL,
    seventh_note INTEGER NULL,
    seventh_note_string VARCHAR(30) NULL
);
```

### ChordNotes

```sql
CREATE TABLE positionfinder_chordnotes (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES positionfinder_notescategory(id),
    ordering INTEGER NULL,
    type_name VARCHAR(30) NOT NULL,
    chord_name VARCHAR(30) DEFAULT 'Major 7',
    chord_ordering INTEGER NULL,
    range VARCHAR(8) DEFAULT 'e - g',
    range_ordering INTEGER NULL,
    tonal_root INTEGER DEFAULT 0,
    first_note INTEGER DEFAULT 0,
    first_note_string VARCHAR(20) NULL,
    second_note INTEGER DEFAULT 4,
    second_note_string VARCHAR(20) NULL,
    third_note INTEGER DEFAULT 7,
    third_note_string VARCHAR(20) NULL,
    fourth_note INTEGER NULL,
    fourth_note_string VARCHAR(20) NULL,
    fifth_note INTEGER NULL,
    fifth_note_string VARCHAR(20) NULL,
    sixth_note INTEGER NULL,
    sixth_note_string VARCHAR(20) NULL
);
```

### ChordPosition

```sql
CREATE TABLE positionfinder_chordposition (
    id SERIAL PRIMARY KEY,
    notes_name_id INTEGER REFERENCES positionfinder_chordnotes(id),
    inversion_order VARCHAR(20) NULL,
    first_note INTEGER DEFAULT 0,
    second_note INTEGER NULL,
    third_note INTEGER NULL,
    fourth_note INTEGER NULL,
    fifth_note INTEGER NULL,
    sixth_note INTEGER NULL
);
```

## Key Differences Between 6-String and 8-String Databases

The schema structure is identical between the 6-string and 8-string databases, but the data differs in the following ways:

1. **String References**: 8-string data includes references to 'lowBString' and 'highAString' in string fields
2. **String Ranges**: 8-string data includes additional range combinations in the ChordNotes table
3. **Position Data**: 8-string positions utilize the extended range

## Data Migration Between Databases

To migrate data between databases:

1. Export data from the source database:
```bash
pg_dump -U postgres -t positionfinder_* -d fretboard > fretboard_export.sql
```

2. Import data to the target database:
```bash
psql -U postgres -d fretboard-devel < fretboard_export.sql
```

Alternatively, use Django's fixtures:

1. Export data:
```bash
python manage.py dumpdata positionfinder --indent 4 > dump.json
```

2. Import data:
```bash
python manage.py loaddata dump.json
```

## Database Backup Strategy

For production databases, implement a regular backup schedule:

```bash
# Daily backup script
pg_dump -U postgres -d fretboard > /backups/fretboard_$(date +%Y%m%d).sql
pg_dump -U postgres -d fretboard-devel > /backups/fretboard-devel_$(date +%Y%m%d).sql

# Cleanup old backups (keep last 30 days)
find /backups/ -name "fretboard_*.sql" -mtime +30 -delete
find /backups/ -name "fretboard-devel_*.sql" -mtime +30 -delete
```
