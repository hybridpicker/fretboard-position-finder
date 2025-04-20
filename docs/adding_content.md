# Adding New Content

This guide explains how to add new musical content to the Fretboard Position Finder application.

## Overview

You can extend the application with new:
- Scales
- Arpeggios
- Chords
- Positions

This can be done through Django's admin interface, Django shell, or by creating database fixtures.

## Adding a New Scale

### Method 1: Using Django Shell

```python
from positionfinder.models import Notes, NotesCategory, NotesPosition

# Get the scales category
scales_category = NotesCategory.objects.get(id=1)

# Create the scale
new_scale = Notes.objects.create(
    category=scales_category,
    note_name='Hungarian Minor',  # Name of the scale
    ordering=15,                  # Order in menus
    tonal_root=0,
    first_note=0,                 # Root
    second_note=2,                # Major 2nd
    third_note=3,                 # Minor 3rd
    fourth_note=6,                # Augmented 4th
    fifth_note=7,                 # Perfect 5th
    sixth_note=8,                 # Minor 6th
    seventh_note=11               # Major 7th
)

# Create positions for the scale
NotesPosition.objects.create(
    notes_name=new_scale,
    position_order='Position 1',
    position_order_number=1,
    first_note=0,                # Root on 6th string
    first_note_string='ELowString',
    second_note=2,               # Major 2nd on 6th string
    second_note_string='ELowString',
    third_note=3,                # Minor 3rd on 5th string
    third_note_string='AString',
    fourth_note=6,               # Augmented 4th on 5th string
    fourth_note_string='AString',
    fifth_note=7,                # Perfect 5th on 4th string
    fifth_note_string='dString',
    sixth_note=8,                # Minor 6th on 4th string
    sixth_note_string='dString',
    seventh_note=11              # Major 7th on 3rd string
    seventh_note_string='gString'
)

# Create additional positions as needed
```

### Method 2: Using Django Admin

1. Navigate to the admin interface (`/admin/`)
2. Go to "Notes" section
3. Click "Add Note"
4. Fill in the details:
   - Select "Scales" category
   - Enter scale name
   - Enter interval values
   - Save the scale
5. Go to "Notes Positions" section
6. Click "Add Notes Position"
7. Fill in the details:
   - Select your new scale
   - Enter position name and order
   - Specify fret offsets and string assignments
   - Save the position
8. Repeat for additional positions

## Adding a New Arpeggio

The process is similar to adding a scale, but with the "Arpeggios" category:

```python
from positionfinder.models import Notes, NotesCategory, NotesPosition

# Get the arpeggios category
arpeggios_category = NotesCategory.objects.get(id=2)

# Create the arpeggio
new_arpeggio = Notes.objects.create(
    category=arpeggios_category,
    note_name='Dominant 9',       # Name of the arpeggio
    ordering=8,                   # Order in menus
    tonal_root=0,
    first_note=0,                 # Root
    second_note=4,                # Major 3rd
    third_note=7,                 # Perfect 5th
    fourth_note=10,               # Minor 7th
    fifth_note=14                 # 9th (2nd + octave)
)

# Create positions (similar to scales)
```

## Adding a New Chord Type

To add a new chord type, such as "Suspended" chords:

```python
from positionfinder.models import NotesCategory
from positionfinder.models_chords import ChordNotes

# Get the chords category
chords_category = NotesCategory.objects.get(id=3)

# Create a new chord type
sus4_chord = ChordNotes.objects.create(
    category=chords_category,
    type_name='Suspended',       # Chord type name
    chord_name='Sus4',           # Specific chord name
    range='e - g',               # String range
    ordering=6,                  # Order in menus
    chord_ordering=1,            # Order within type
    tonal_root=0,
    first_note=0,                # Root
    first_note_string='gString',
    second_note=5,               # Perfect 4th (instead of 3rd)
    second_note_string='bString',
    third_note=7,                # Perfect 5th
    third_note_string='eString'
)
```

The `save()` method will automatically:
1. Create basic position
2. Create inversions
3. Generate related chords (if applicable)

### Adding Multiple Ranges

For each chord, add the same chord with different string ranges:

```python
# Create the same chord with a different range
sus4_chord_2 = ChordNotes.objects.create(
    category=chords_category,
    type_name='Suspended',
    chord_name='Sus4',
    range='b - A',               # Different string range
    ordering=6,
    chord_ordering=1,
    tonal_root=0,
    first_note=0,
    first_note_string='dString',
    second_note=5,
    second_note_string='gString',
    third_note=7,
    third_note_string='bString'
)
```

## Adding a New Chord Group

To add an entirely new chord group (e.g., "Extended Chords"):

```python
# Create the base chord (e.g., Major 9)
extended_chord = ChordNotes.objects.create(
    category=chords_category,
    type_name='Extended',        # New type name
    chord_name='Major 9',
    range='e - E',               # Wider range for extended chords
    ordering=7,                  # Later in menu
    chord_ordering=1,
    tonal_root=0,
    first_note=0,                # Root
    first_note_string='ELowString',
    second_note=4,               # Major 3rd
    second_note_string='dString',
    third_note=7,                # Perfect 5th
    third_note_string='gString',
    fourth_note=11,              # Major 7th
    fourth_note_string='bString',
    fifth_note=14,               # 9th (2nd + octave)
    fifth_note_string='eString'
)
```

## Modifying the Chord Creation Function

If you need custom chord derivation logic, modify the `create_chord()` function in `models_chords.py`:

```python
def create_chord(id):
    chord = ChordNotes.objects.get(id=id)

    if chord.chord_name == 'Your New Base Chord':
        # Create derived chords
        derived_chord = ChordNotes.objects.create(
            category_id=chord.category.id,
            type_name=chord.type_name,
            chord_name='Derived Chord',
            range=chord.range,
            # Set appropriate intervals
            # ...
        )
        
        # Create positions for the derived chord
        create_base_position(derived_chord.id)
```

## Adding 8-String Content

For 8-string guitar content, include the additional strings in your definitions:

```python
# 8-string chord
eight_string_chord = ChordNotes.objects.create(
    # ... standard fields
    first_note=0,
    first_note_string='lowBString',  # Use the low B string
    second_note=4,
    second_note_string='ELowString',
    third_note=7,
    third_note_string='AString',
    fourth_note=11,
    fourth_note_string='dString',
    fifth_note=14,
    fifth_note_string='gString'
)
```

## Adding New Positions

To add new positions for existing scales or arpeggios:

```python
from positionfinder.models import Notes, NotesPosition

# Get the scale
scale = Notes.objects.get(note_name='Major')

# Add a new position
new_position = NotesPosition.objects.create(
    notes_name=scale,
    position_order='Position 6',  # New position name
    position_order_number=6,
    first_note=12,               # Starting at 12th fret
    first_note_string='ELowString',
    # ... other note placements
)
```

## Using Fixtures for Bulk Content

For adding multiple items, create a fixture file:

```json
[
  {
    "model": "positionfinder.notes",
    "pk": 101,
    "fields": {
      "category": 1,
      "note_name": "New Scale 1",
      "ordering": 20,
      "tonal_root": 0,
      "first_note": 0,
      "second_note": 2,
      "third_note": 4,
      "fourth_note": 5,
      "fifth_note": 7,
      "sixth_note": 9,
      "seventh_note": 11
    }
  },
  {
    "model": "positionfinder.notesposition",
    "pk": 501,
    "fields": {
      "notes_name": 101,
      "position_order": "Position 1",
      "position_order_number": 1,
      "first_note": 0,
      "first_note_string": "ELowString",
      "second_note": 2,
      "second_note_string": "ELowString",
      "third_note": 4,
      "third_note_string": "AString",
      "fourth_note": 5,
      "fourth_note_string": "AString",
      "fifth_note": 7,
      "fifth_note_string": "dString",
      "sixth_note": 9,
      "sixth_note_string": "dString",
      "seventh_note": 11,
      "seventh_note_string": "gString"
    }
  }
]
```

Save this as a file in `positionfinder/fixtures/new_content.json` and load it:

```bash
python manage.py loaddata positionfinder/fixtures/new_content.json
```

## Adding Common Jazz Voicings

Here's an example of adding common jazz chord voicings:

```python
from positionfinder.models import NotesCategory
from positionfinder.models_chords import ChordNotes

# Get the chords category
chords_category = NotesCategory.objects.get(id=3)

# Create a jazz voicing group
jazz_m7 = ChordNotes.objects.create(
    category=chords_category,
    type_name='Jazz Voicings',
    chord_name='Minor 7',
    range='d - g',               # 4-note voicing on middle strings
    ordering=8,
    chord_ordering=2,
    tonal_root=0,
    first_note=0,                # Root
    first_note_string='dString',
    second_note=3,               # Minor 3rd
    second_note_string='gString',
    third_note=7,                # Perfect 5th
    third_note_string='bString',
    fourth_note=10,              # Minor 7th
    fourth_note_string='eString'
)

# The save method will automatically create inversions
```

## Verifying New Content

After adding new content, verify it works:

1. Navigate to the main application
2. Select the appropriate category
3. Find your new scale/arpeggio/chord in the dropdown
4. Verify it displays correctly on the fretboard
5. Test in different keys

## Considerations for 8-String Content

When adding content for 8-string guitars:

1. **Extended Range**: Utilize the low B and high A strings for extended range voicings
2. **Ergonomics**: Consider the physical playability of chord voicings (hand span)
3. **String Tension**: Lower strings may need higher fret positions for clarity
4. **String Naming**: Use 'lowBString' and 'highAString' string names consistently
5. **Octave Consistency**: Be mindful of octave designations (0-4)

## Extended Scale Patterns

For 8-string guitars, create scale patterns that span all 8 strings:

```python
# 8-string scale position
NotesPosition.objects.create(
    notes_name=major_scale,
    position_order='8-String Position 1',
    position_order_number=10,  # Higher number to sort after standard positions
    first_note=0,
    first_note_string='lowBString',  # Start on low B
    second_note=2,
    second_note_string='lowBString',
    third_note=4,
    third_note_string='ELowString',
    fourth_note=5,
    fourth_note_string='ELowString',
    fifth_note=7,
    fifth_note_string='AString',
    sixth_note=9,
    sixth_note_string='AString',
    seventh_note=11,
    seventh_note_string='dString'
)
```

## Batch Creation Functions

For efficiently adding multiple related items, create helper functions:

```python
def create_extended_chord_set(type_name, ordering):
    """Create a set of extended chords with multiple voicings."""
    chords_category = NotesCategory.objects.get(id=3)
    
    # Create Major 9
    maj9 = ChordNotes.objects.create(
        category=chords_category,
        type_name=type_name,
        chord_name='Major 9',
        range='e - E',
        ordering=ordering,
        chord_ordering=1,
        # ... note definitions
    )
    
    # Create Minor 9
    min9 = ChordNotes.objects.create(
        category=chords_category,
        type_name=type_name,
        chord_name='Minor 9',
        range='e - E',
        ordering=ordering,
        chord_ordering=2,
        # ... note definitions
    )
    
    # Create Dominant 9
    dom9 = ChordNotes.objects.create(
        category=chords_category,
        type_name=type_name,
        chord_name='Dominant 9',
        range='e - E',
        ordering=ordering,
        chord_ordering=3,
        # ... note definitions
    )
    
    return [maj9, min9, dom9]

# Usage
extended_chords = create_extended_chord_set('Extended', 10)
```

## Migrating Content Between 6-String and 8-String Databases

To make content available in both databases:

1. Export specific content from one database:
   ```bash
   python manage.py dumpdata positionfinder.Notes positionfinder.NotesPosition --indent 4 --filter="notes__note_name='Your Scale'" > scale_export.json
   ```

2. Edit the JSON file to adjust string references if needed

3. Import into the other database:
   ```bash
   python manage.py loaddata scale_export.json
   ```

## Troubleshooting Content Issues

### Issue: Content Not Displaying
- Verify all required fields are filled
- Check for typos in string names
- Ensure the category ID is correct
- Confirm the note intervals are correct

### Issue: Incorrect Positions
- Verify string assignments match the intended strings
- Check fret offsets
- Test with different root notes

### Issue: Missing Derived Chords
- Check the `create_chord()` function logic
- Verify the base chord is correctly defined
- Add missing chord variations manually if needed

## Best Practices

1. **Consistent Naming**: Use consistent naming conventions for all content
2. **Logical Ordering**: Set appropriate ordering values for menu display
3. **Complete Sets**: When adding new chord types, create all common variations
4. **Test Thoroughly**: Test new content in all 12 keys
5. **Document Additions**: Keep a record of added content for future reference
6. **Backup First**: Always create a database backup before adding significant content
