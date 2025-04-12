# String Configurations

This document details how the Fretboard Position Finder handles different string configurations for 6-string and 8-string guitars.

## Overview

The application supports two guitar configurations:
- **6-String Guitar**: Standard tuning (E, A, D, G, B, E)
- **8-String Guitar**: Extended tuning (B, E, A, D, G, B, E, A)

The codebase is designed to adapt to both configurations without requiring significant structural changes.

## String Definitions

Strings are defined in `string_choices.py`:

```python
STRING_CHOICES = {
    'eString': _(u'eString'),         # High E (1st string)
    'bString': _(u'bString'),         # B (2nd string)
    'gString': _(u'gString'),         # G (3rd string)
    'dString': _(u'dString'),         # D (4th string)
    'AString': _(u'AString'),         # A (5th string)
    'ELowString': _(u'ELowString'),   # Low E (6th string)
    'lowBString': _(u'lowBString'),   # Low B (7th string, 8-string guitar only)
    'highAString': _(u'highAString'), # High A (8th string, 8-string guitar only)
}
```

The `StringChoicesField` is a custom Django field that provides these options in models:

```python
class StringChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(STRING_CHOICES.items()))
        kwargs['max_length'] = 20
        super(StringChoicesField, self).__init__(*args, **kwargs)
```

## String Ranges

String ranges define which subset of strings a chord or scale uses. These are defined in `string_range_choices.py`:

```python
STRING_RANGE_CHOICES = {
    'a - b': _(u'a - b'),   # High A to B (8-string only)
    'e - g': _(u'e - g'),   # High E to G (common for 6-string)
    'b - d': _(u'b - d'),   # B to D
    'g - A': _(u'g - A'),   # G to A
    'd - E': _(u'd - E'),   # D to Low E
    'A - B': _(u'A - B'),   # A to Low B (8-string only)
    # Many more combinations...
}
```

The 8-string configuration adds combinations that include 'lowBString' and 'highAString'.

## Note Mapping

Note positions on each string are defined in `template_notes.py` in the `STRING_NOTE_OPTIONS` dictionary:

```python
STRING_NOTE_OPTIONS = {
    "eString": [{
        "c": [{"tone": ["c3"], "fret": [8]}],
        "cs": [{"tone": ["cs3"], "fret": [9]}],
        # ... more notes
    }],
    # ... other 6-string entries
    "lowBString": [{
        "c": [{"tone": ["c0", "c1"], "fret": [1, 13]}],
        # ... more notes with lower octaves
    }],
    "highAString": [{
        "c": [{"tone": ["c4"], "fret": [3, 15]}],
        # ... more notes with higher octaves
    }]
}
```

Each string has a dictionary mapping note names to their positions (frets) and octave designations.

Key differences in the 8-string extension:
- **lowBString**: Contains lower-octave notes (octave 0)
- **highAString**: Contains higher-octave notes (octave 4)

## View Implementation

In the views (e.g., `views_scale.py`, `views_chords.py`), string names are passed to templates in the correct order:

```python
# For 6-string configuration
string_names = ['ELowString', 'AString', 'dString', 'gString', 'bString', 'eString']

# For 8-string configuration
string_names = ['lowBString', 'ELowString', 'AString', 'dString', 'gString', 'bString', 'eString', 'highAString']
```

The order is from lowest-pitched string (bottom of fretboard) to highest-pitched string (top of fretboard).

## Frontend Rendering

The frontend JavaScript adapts to render the appropriate number of strings based on the data received. When working with an 8-string configuration, the fretboard display includes all eight strings.

## Octave Handling

Octave designations in note names (e.g., "c3", "fs2") follow a consistent pattern:
- Octave 0: Extended low range (8-string only)
- Octave 1: Standard low range
- Octave 2: Middle range
- Octave 3: Standard high range
- Octave 4: Extended high range (8-string only)

This provides proper pitch context when displaying note names.

## String Assignment in Chord Models

Chord models use string assignments to specify which string each note is played on:

```python
chord = ChordNotes.objects.create(
    # ... other fields
    first_note=0,                  # Root note
    first_note_string='gString',   # Root played on G string
    second_note=4,                 # Major third
    second_note_string='bString',  # Third played on B string
    third_note=7,                  # Perfect fifth
    third_note_string='eString',   # Fifth played on high E string
)
```

The 8-string version extends these assignments to include 'lowBString' and 'highAString'.

## Adding New String Configurations

To add support for a different string configuration (e.g., 7-string, 12-string):

1. Update `STRING_CHOICES` in `string_choices.py` to include new strings
2. Add appropriate entries to `STRING_NOTE_OPTIONS` in `template_notes.py`
3. Update string range options in `STRING_RANGE_CHOICES`
4. Create a new database with appropriate string data
5. Update view string_names lists to include the correct strings in order

## Switching Between Configurations

To switch between 6-string and 8-string configurations:

1. Change database configuration in `local_settings.py`
2. Restart the application

No code changes are required as the application adapts based on the available string data.

## Testing String Configurations

When testing, ensure each configuration works correctly:

```python
# Test for 6-string compatibility
def test_6string_compatibility():
    # Test with 6-string database
    # Verify that only 6 strings are used in chord positions
    pass

# Test for 8-string compatibility
def test_8string_compatibility():
    # Test with 8-string database
    # Verify that 8 strings are properly displayed
    # Verify that 8-string chord voicings work correctly
    pass
```

## String-Specific Optimizations

For better performance with 8-string configurations:

1. Use string ranges that make musical sense (e.g., 'b - E' rather than 'a - B')
2. Group similar voicings across both configurations
3. Consider ergonomic concerns (wider reach between strings)
