# API Reference

This document provides detailed documentation for the core functions and modules in the Fretboard Position Finder application.

## Note Setup Module

`note_setup.py` - Functions for handling note and scale processing.

### get_notes_tones

```python
def get_notes_tones(notes_id, root_pitch, tonal_root, root_id)
```

**Purpose:** Calculates the actual pitches of notes in a scale or arpeggio.

**Parameters:**
- `notes_id` (int): ID of the Notes object
- `root_pitch` (int): Pitch of the root note (0-11)
- `tonal_root` (int): Tonal root offset
- `root_id` (int): ID of the root note

**Returns:**
- `list`: List of note pitches (integers)

**Example:**
```python
# Get the pitches for C Major scale
root = Root.objects.get(name='C')
major_scale = Notes.objects.get(category__category_name='Scales', note_name='Major')
pitches = get_notes_tones(major_scale.id, root.pitch, 0, root.id)
# Result: [0, 2, 4, 5, 7, 9, 11]
```

## Root Note Setup Module

`root_note_setup.py` - Functions for handling root notes.

### get_root_note

```python
def get_root_note(root_pitch, tonal_root, root_id)
```

**Purpose:** Gets the appropriate root note with octave designation.

**Parameters:**
- `root_pitch` (int): Pitch of the root note (0-11)
- `tonal_root` (int): Tonal root offset
- `root_id` (int): ID of the root note

**Returns:**
- `list`: List containing the root note name with octave

**Example:**
```python
# Get the root note for C
root_note = get_root_note(0, 0, 1)
# Result: ['c1']
```

## Position Calculation Module

`get_position.py` - Core position calculation functions.

### get_notes_position

```python
def get_notes_position(notes_id, position_id, root_pitch, tonal_root, root_id)
```

**Purpose:** Gets the position notes for a scale or arpeggio.

**Parameters:**
- `notes_id` (int): ID of the Notes object
- `position_id` (int): ID of the position
- `root_pitch` (int): Pitch of the root note (0-11)
- `tonal_root` (int): Tonal root offset
- `root_id` (int): ID of the root note

**Returns:**
- `dict`: Dictionary containing position notes

**Example:**
```python
# Get position 1 for C Major scale
positions = get_notes_position(1, 1, 0, 0, 1)
```

## Scale Position Dictionary Module

`get_position_dict_scales.py` - Functions for generating scale position dictionaries.

### get_scale_position_dict

```python
def get_scale_position_dict(scale_name, root_id, root_pitch, tonal_root, root_name)
```

**Purpose:** Generates a dictionary of fretboard positions for a scale.

**Parameters:**
- `scale_name` (str): Name of the scale
- `root_id` (int): ID of the root note
- `root_pitch` (int): Pitch of the root note (0-11)
- `tonal_root` (int): Tonal root offset
- `root_name` (str): Name of the root note

**Returns:**
- `dict`: Dictionary containing scale positions for all positions

**Example:**
```python
# Get position dictionary for C Major scale
positions = get_scale_position_dict('Major', 1, 0, 0, 'C')
```

### transpose_actual_position

```python
def transpose_actual_position(position_json_data, transposable_position)
```

**Purpose:** Transposes position data to match different root notes.

**Parameters:**
- `position_json_data` (dict): Original position data
- `transposable_position` (dict): Transposition information

**Returns:**
- `dict`: Transposed position data

## Chord Position Dictionary Module

`get_position_dict_chords.py` - Functions for generating chord position dictionaries.

### get_position_dict

```python
def get_position_dict(inversion_name, chord_name, range_name, type_name, root_pitch, tonal_root, root_name)
```

**Purpose:** Generates a dictionary of fretboard positions for a chord.

**Parameters:**
- `inversion_name` (str): Name of the inversion
- `chord_name` (str): Name of the chord
- `range_name` (str): String range for the chord
- `type_name` (str): Chord type name
- `root_pitch` (int): Pitch of the root note (0-11)
- `tonal_root` (int): Tonal root offset
- `root_name` (str): Name of the root note

**Returns:**
- `dict`: Dictionary containing chord position data

**Example:**
```python
# Get position dictionary for C Major 7 chord
position = get_position_dict('Basic Position', 'Major 7', 'e - g', 'V2', 0, 0, 'C')
```

## Functionality Tones Module

`functionality_tones_setup.py` - Functions for calculating note functions.

### get_functionality_tones

```python
def get_functionality_tones(notes_id, root_pitch)
```

**Purpose:** Gets the functional descriptions of notes in a scale or arpeggio.

**Parameters:**
- `notes_id` (int): ID of the Notes object
- `root_pitch` (int): Pitch of the root note (0-11)

**Returns:**
- `list`: List of note function descriptions (e.g., 'Root', 'Major 3rd')

**Example:**
```python
# Get the functional descriptions for C Major scale
functions = get_functionality_tones(1, 0)
# Result: ['Root', 'Major 2nd', 'Major 3rd', 'Perfect 4th', 'Perfect 5th', 'Major 6th', 'Major 7th']
```

### get_functionality_note_names

```python
def get_functionality_note_names(notes_id, root_pitch, tonal_root, root_id)
```

**Purpose:** Gets the actual note names for a scale or arpeggio.

**Parameters:**
- `notes_id` (int): ID of the Notes object
- `root_pitch` (int): Pitch of the root note (0-11)
- `tonal_root` (int): Tonal root offset
- `root_id` (int): ID of the root note

**Returns:**
- `list`: List of note names (e.g., 'C', 'D', 'E')

**Example:**
```python
# Get the note names for C Major scale
note_names = get_functionality_note_names(1, 0, 0, 1)
# Result: ['C', 'D', 'E', 'F', 'G', 'A', 'B']
```

## Templates Notes Module

`template_notes.py` - Constants and data structures for note mapping.

### Constants

```python
NOTES = ['c', 'db', 'd', 'eb', 'e', 'f', 'gb', 'g', 'ab', 'a', 'bb', 'b']
NOTES_SHARP = ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b']
OCTAVES = [-1, 0, 1, 2, 3, 4]
TENSIONS = ['R', 'b9', '9', 'b3', '3', '11', '#11', '5', 'b13', '13', 'b7', '7']
```

### STRING_NOTE_OPTIONS

A complex dictionary mapping each string to its possible notes and fret positions.

**Purpose:** Provides the mapping between note names and their positions on each string.

**Example:**
```python
# Look up the position of C on the high E string
c_on_e_string = STRING_NOTE_OPTIONS["eString"][0]["c"]
# Result: [{"tone": ["c3"], "fret": [8]}]
```

## String Choices Module

`string_choices.py` - String definitions and custom fields.

### STRING_CHOICES

```python
STRING_CHOICES = {
    'eString': _(u'eString'),
    'bString': _(u'bString'),
    'gString': _(u'gString'),
    'dString': _(u'dString'),
    'AString': _(u'AString'),
    'ELowString': _(u'ELowString'),
    'lowBString': _(u'lowBString'),
    'highAString': _(u'highAString'),
}
```

**Purpose:** Defines the available strings for the guitar.

### StringChoicesField

```python
class StringChoicesField(models.CharField)
```

**Purpose:** Custom Django model field for string selections.

**Usage:**
```python
class MyModel(models.Model):
    string = StringChoicesField(_("String for Note"), null=True, blank=True)
```

## String Range Choices Module

`string_range_choices.py` - String range definitions and custom fields.

### STRING_RANGE_CHOICES

```python
STRING_RANGE_CHOICES = {
    'a - b': _(u'a - b'),
    'e - g': _(u'e - g'),
    # ... many more combinations
}
```

**Purpose:** Defines the available string ranges for chords.

### StringRangeChoicesField

```python
class StringRangeChoicesField(models.CharField)
```

**Purpose:** Custom Django model field for string range selections.

**Usage:**
```python
class MyModel(models.Model):
    range = StringRangeChoicesField(_("String Range"), default="e - g")
```

## Chord Creation Functions

`models_chords.py` - Functions for creating chord variations.

### create_chord

```python
def create_chord(id)
```

**Purpose:** Creates related chord variations from a base chord.

**Parameters:**
- `id` (int): ID of the base ChordNotes object

**Returns:**
- None (creates chord objects as side effect)

**Example:**
```python
# Create variations for a Major 7 chord
maj7_chord = ChordNotes.objects.create(chord_name='Major 7', ...)
# create_chord is called automatically in the save() method
```

### create_base_position

```python
def create_base_position(id)
```

**Purpose:** Creates the basic position for a chord.

**Parameters:**
- `id` (int): ID of the ChordNotes object

**Returns:**
- None (creates ChordPosition object as side effect)

### create_fourthnote_positions

```python
def create_fourthnote_positions(w, x, y, z, chord_id)
```

**Purpose:** Creates inversions for a 4-note chord.

**Parameters:**
- `w`, `x`, `y`, `z` (int): Interval values between chord tones
- `chord_id` (int): ID of the ChordNotes object

**Returns:**
- None (creates ChordPosition objects as side effect)

## View Helper Functions

`views_helpers.py` - Helper functions for views.

### get_menu_options

```python
def get_menu_options()
```

**Purpose:** Gets the options for navigation menus.

**Parameters:**
- None

**Returns:**
- `dict`: Dictionary containing menu options for scales, arpeggios, and chords

**Example:**
```python
menu = get_menu_options()
scales = menu['scales_options']
arpeggios = menu['arpeggios_options']
chords = menu['chords_options']
```

## Django Models

### Notes

```python
class Notes(models.Model)
```

**Purpose:** Represents a scale or arpeggio definition.

**Key fields:**
- `category`: ForeignKey to NotesCategory
- `note_name`: Name of the scale or arpeggio
- `first_note` through `twelth_note`: Intervals from the root

**Example:**
```python
# Create a major scale
major = Notes.objects.create(
    category=NotesCategory.objects.get(category_name='Scales'),
    note_name='Major',
    first_note=0,   # Root
    second_note=2,  # Major 2nd
    third_note=4,   # Major 3rd
    fourth_note=5,  # Perfect 4th
    fifth_note=7,   # Perfect 5th
    sixth_note=9,   # Major 6th
    seventh_note=11 # Major 7th
)
```

### ChordNotes

```python
class ChordNotes(models.Model)
```

**Purpose:** Represents a chord definition.

**Key fields:**
- `category`: ForeignKey to NotesCategory
- `type_name`: Chord type (e.g., 'Triads', 'V2')
- `chord_name`: Name of the chord (e.g., 'Major 7')
- `range`: String range (e.g., 'e - g')
- `first_note` through `sixth_note`: Intervals from the root
- `first_note_string` through `sixth_note_string`: String assignments

**Example:**
```python
# Create a major 7 chord
major7 = ChordNotes.objects.create(
    category=NotesCategory.objects.get(category_name='Chords'),
    type_name='V2',
    chord_name='Major 7',
    range='e - g',
    first_note=0,                # Root
    first_note_string='gString',
    second_note=4,               # Major 3rd
    second_note_string='bString',
    third_note=7,                # Perfect 5th
    third_note_string='eString',
    fourth_note=11,              # Major 7th
    fourth_note_string='eString'
)
```

## JavaScript API

### Core Fretboard Functions

These functions handle the rendering and interaction of the fretboard display.

#### renderFretboard

```javascript
function renderFretboard(scaleData, stringNames)
```

**Purpose:** Renders the fretboard with notes.

**Parameters:**
- `scaleData` (object): JSON data containing position information
- `stringNames` (array): Array of string names to render

**Example:**
```javascript
renderFretboard(JSON.parse(scaleJsonData), ['ELowString', 'AString', 'dString', 'gString', 'bString', 'eString']);
```

#### highlightNotes

```javascript
function highlightNotes(position, positionName)
```

**Purpose:** Highlights notes for a specific position.

**Parameters:**
- `position` (object): Position data
- `positionName` (string): Name of the position

**Example:**
```javascript
highlightNotes(scaleData["Position 1"], "Position 1");
```

### Utility Functions

#### getNoteColor

```javascript
function getNoteColor(tension)
```

**Purpose:** Determines the color for a note based on its function.

**Parameters:**
- `tension` (string): Note function (e.g., 'Root', 'Major 3rd')

**Returns:**
- `string`: CSS color value

**Example:**
```javascript
const color = getNoteColor('Root');  // Returns the root note color
```

#### getNoteLabel

```javascript
function getNoteLabel(note, showOctave)
```

**Purpose:** Formats a note name for display.

**Parameters:**
- `note` (string): Raw note name (e.g., 'c2')
- `showOctave` (boolean): Whether to include octave number

**Returns:**
- `string`: Formatted note name

**Example:**
```javascript
const label = getNoteLabel('c2', true);  // Returns 'C2'
```
