# Data Models Documentation

This document provides detailed information about the data models used in the Fretboard Position Finder application.

## Overview

The application uses several interconnected models to represent musical concepts:

1. **Categories** - Types of musical elements (scales, arpeggios, chords)
2. **Root Notes** - The 12 possible root notes (C, C#, D, etc.)
3. **Notes** - Scale and arpeggio definitions
4. **Note Positions** - Fretboard positions for scales and arpeggios
5. **Chord Notes** - Chord definitions
6. **Chord Positions** - Chord inversions and positions

## Core Models (models.py)

### Root

Represents the 12 possible root notes in music.

```python
class Root(models.Model):
    name = models.CharField(max_length=30)
    pitch = models.IntegerField()

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('pitch', 'name')
        verbose_name = u'Rootnote'
        verbose_name_plural = u'Rootnotes'
```

Key fields:
- `name`: Name of the root note (e.g., 'C', 'C#', 'D')
- `pitch`: Numeric representation of pitch (0 for C, 1 for C#, etc.)

### NotesCategory

Categorizes musical elements into scales, arpeggios, and chords.

```python
class NotesCategory(models.Model):
    category_name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.category_name)

    class Meta:
        verbose_name = u'category name'
        verbose_name_plural = u'category names'
```

Key fields:
- `category_name`: Name of the category ('Scales', 'Arpeggios', 'Chords')

### Notes

Defines scale and arpeggio structures through interval relationships.

```python
class Notes(models.Model):
    category = models.ForeignKey(NotesCategory, on_delete=models.CASCADE)
    note_name = models.CharField(max_length=30)
    ordering = models.IntegerField(null=True, blank=True)
    chords = ChordChoicesField(_("Chord Name"), null=True, blank=True)
    tonal_root = models.IntegerField(default=0)
    first_note = models.IntegerField(default=0)  # Always the root
    second_note = models.IntegerField(null=True, blank=True)
    third_note = models.IntegerField(null=True, blank=True)
    fourth_note = models.IntegerField(null=True, blank=True)
    # ... more notes up to twelth_note

    def __str__(self):
        return '%s : %s' % (self.category, self.note_name)

    class Meta:
        ordering = ['category', 'ordering', 'note_name']
        verbose_name = u'Tones for Scale'
        verbose_name_plural = u'Tones for Scales'
```

Key fields:
- `category`: Reference to NotesCategory
- `note_name`: Name of the scale or arpeggio (e.g., 'Major', 'Minor', 'Dorian')
- `tonal_root`: Defines the tonal space of the notes
- `first_note` through `twelth_note`: Intervals from the root (in semitones)

Example: Major scale intervals would be [0, 2, 4, 5, 7, 9, 11]

## Position Models

### NotesPosition

Defines specific positions on the fretboard for scales and arpeggios.

```python
class NotesPosition(models.Model):
    notes_name = models.ForeignKey(Notes, on_delete=models.CASCADE)
    position_order = models.CharField(max_length=20, null=True, blank=True)
    position_order_number = models.IntegerField(null=True, blank=True)
    first_note = models.IntegerField(default=0)
    first_note_string = models.CharField(max_length=30, null=True, blank=True)
    # ... more notes and string assignments

    def __str__(self):
        return '%s : %s' % (self.notes_name, self.position_order)

    class Meta:
        ordering = ('notes_name', 'position_order_number')
        verbose_name = u'Scale position'
        verbose_name_plural = u'Scale positions'
```

Key fields:
- `notes_name`: Reference to a Notes object
- `position_order`: Name of the position (e.g., 'Position 1', 'Position 2')
- `first_note` through `seventh_note`: Fret offsets for each note in the position
- `first_note_string` through `seventh_note_string`: String assignments for each note

## Chord Models (models_chords.py)

### ChordNotes

Defines chord structures with string assignments.

```python
class ChordNotes(models.Model):
    category = models.ForeignKey(NotesCategory, on_delete=models.CASCADE)
    ordering = models.IntegerField(null=True, blank=True)
    type_name = models.CharField(max_length=30)
    chord_name = ChordChoicesField(_("Chord Name"), default="Major 7")
    chord_ordering = models.IntegerField(null=True, blank=True)
    range = StringRangeChoicesField(_("String Range"), default="e - g")
    range_ordering = models.IntegerField(null=True, blank=True)
    tonal_root = models.IntegerField(default=0)
    first_note = NotesChoicesField(_("First Note"), default=0)
    first_note_string = StringChoicesField(_("String for Note"), null=True, blank=True)
    # ... more notes and string assignments

    def save(self, *args, **kwargs):
        super(ChordNotes, self).save(*args, **kwargs)
        create_chords = create_chord(self.id)

    def __str__(self):
        return '%s : %s (%s)' % (self.type_name, self.chord_name, self.range)

    class Meta:
        ordering = ['category', 'ordering', 'range_ordering', 'chord_ordering']
        verbose_name = u'Tones for Chord'
        verbose_name_plural = u'Tones for Chords'
```

Key fields:
- `category`: Reference to NotesCategory
- `type_name`: Chord type descriptor (e.g., 'Triads', 'V2', 'V3')
- `chord_name`: Name of the chord (e.g., 'Major', 'Minor', 'Major 7')
- `range`: String range for the chord (e.g., 'e - g', 'b - A')
- `first_note` through `sixth_note`: Intervals from the root (in semitones)
- `first_note_string` through `sixth_note_string`: String assignments

The `save()` method automatically creates related chords through the `create_chord()` function, which generates variations like minor, diminished, and augmented chords from a major chord, or minor7, dominant7, etc. from a major7 chord.

### ChordPosition

Defines inversions for chords.

```python
class ChordPosition(models.Model):
    notes_name = models.ForeignKey(ChordNotes, on_delete=models.CASCADE)
    inversion_order = ChordInversionChoicesField(_("Inversion for Chord"), null=True, blank=True)
    first_note = models.IntegerField(default=0)
    second_note = models.IntegerField(null=True, blank=True)
    third_note = models.IntegerField(null=True, blank=True)
    fourth_note = models.IntegerField(null=True, blank=True)
    fifth_note = models.IntegerField(null=True, blank=True)
    sixth_note = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return '"%s" %s : %s %s (%s)' % (self.notes_name, self.inversion_order,
                               self.notes_name.type_name, self.notes_name.chord_name,
                               self.notes_name.chord_ordering)

    class Meta:
        ordering = ('notes_name', 'inversion_order')
        verbose_name = u'Chord position'
        verbose_name_plural = u'Chord positions'
```

Key fields:
- `notes_name`: Reference to a ChordNotes object
- `inversion_order`: Name of the inversion (e.g., 'Basic Position', 'First Inversion')
- `first_note` through `sixth_note`: Fret offsets for each note in the inversion

## Helper Models and Fields

### StringChoicesField (string_choices.py)

Custom field for string selections.

```python
STRING_CHOICES = {
    'eString': _(u'eString'),
    'bString': _(u'bString'),
    'gString': _(u'gString'),
    'dString': _(u'dString'),
    'AString': _(u'AString'),
    'ELowString': _(u'ELowString'),
    'lowBString': _(u'lowBString'),      # 8-string only
    'highAString': _(u'highAString'),    # 8-string only
}

class StringChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(STRING_CHOICES.items()))
        kwargs['max_length'] = 20
        super(StringChoicesField, self).__init__(*args, **kwargs)
```

### StringRangeChoicesField (string_range_choices.py)

Custom field for string range selections.

```python
STRING_RANGE_CHOICES = {
    'a - b': _(u'a - b'),
    'e - g': _(u'e - g'),
    # ... many more combinations
}

class StringRangeChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(STRING_RANGE_CHOICES.items()))
        kwargs['max_length'] = 8
        super(StringRangeChoicesField, self).__init__(*args, **kwargs)
```

## Model Relationships

1. **NotesCategory** is referenced by:
   - Notes
   - ChordNotes

2. **Notes** is referenced by:
   - NotesPosition

3. **ChordNotes** is referenced by:
   - ChordPosition

## 8-String Extensions

The 8-string version extends the models with:

1. Additional strings in STRING_CHOICES:
   - 'lowBString': Low B string below the standard low E
   - 'highAString': High A string above the standard high E

2. Additional string range combinations in STRING_RANGE_CHOICES that include the new strings

3. The model structure remains the same, but the data includes references to the additional strings

## Creating and Extending Models

### Adding a New Scale

```python
from positionfinder.models import Notes, NotesCategory

# Get the scales category
scales_category = NotesCategory.objects.get(category_name='Scales')

# Create a new scale (e.g., Altered Scale)
altered_scale = Notes.objects.create(
    category=scales_category,
    note_name='Altered',
    ordering=10,  # Position in menus
    tonal_root=0,
    first_note=0,   # Root
    second_note=1,  # b2
    third_note=3,   # #2
    fourth_note=4,  # 3
    fifth_note=6,   # b5
    sixth_note=8,   # #5
    seventh_note=10  # b7
)
```

### Adding a New Chord Type

```python
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

# Get the chords category
chords_category = NotesCategory.objects.get(category_name='Chords')

# Create a new chord type (e.g., Add9 chord)
add9_chord = ChordNotes.objects.create(
    category=chords_category,
    type_name='Add9',
    chord_name='Major Add9',
    range='e - g',
    ordering=5,  # Position in menus
    tonal_root=0,
    first_note=0,   # Root
    first_note_string='gString',
    second_note=4,  # Major 3rd
    second_note_string='bString',
    third_note=7,   # Perfect 5th
    third_note_string='eString',
    fourth_note=14,  # 9th (2nd + octave)
    fourth_note_string='eString'
)
```

The `save()` method will automatically create base positions and inversions.
