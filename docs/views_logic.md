# Views and Application Logic

This document explains the views and application logic that power the Fretboard Position Finder.

## View Structure

The application is organized into specialized view modules:

1. **views.py** - Basic views (about, impressum)
2. **views_scale.py** - Scale-specific views
3. **views_chords.py** - Chord-specific views
4. **views_arpeggio.py** - Arpeggio-specific views
5. **views_helpers.py** - Shared helper functions

## Main View Flow

Each primary view follows a similar pattern:

1. Process GET parameters (root note, category, musical element, position)
2. Retrieve model data based on parameters
3. Calculate fretboard positions
4. Generate JSON data for the frontend
5. Render the template with the data

## Scales View (views_scale.py)

The `fretboard_scale_view` function handles scale visualization:

```python
def fretboard_scale_view(request):
    # Process GET parameters
    root_id = request.GET.get('root', 1)
    category_id = request.GET.get('models_select', 1)
    notes_options_id = request.GET.get('notes_options_select', '1')
    position_id = request.GET.get('position_select', '0')
    
    # Redirect if not a scale request
    if category_id == '2':
        return redirect('show_arpeggio_fretboard')
    if category_id == '3':
        return redirect('show_chords_fretboard')
    
    # Get data from models
    root_pitch = Root.objects.get(pk=root_id).pitch
    notes_options = Notes.objects.filter(category=category_id).order_by('ordering')
    position_options = NotesPosition.objects.filter(notes_name=notes_options_id)
    
    # Calculate musical information
    tones = get_notes_tones(notes_options_id, root_pitch, tonal_root, root_id)
    tensions = get_functionality_tones(notes_options_id, root_pitch)
    root = get_root_note(root_pitch, tonal_root, root_id)
    
    # Generate position dictionary
    position_json_data = get_scale_position_dict(...)
    
    # Format for JSON
    scale_json_data = json.dumps(position_json_data)
    
    # Render template with context
    return render(request, 'fretboard.html', context)
```

## Chords View (views_chords.py)

The `fretboard_chords_view` function handles chord visualization:

```python
def fretboard_chords_view(request):
    # Process GET parameters
    root_id = request.GET.get('root', 1)
    category_id = request.GET.get('models_select', 3)
    type_id = request.GET.get('type_options_select', 'Triads')
    chord_select_name = request.GET.get('chords_options_select', 'Major')
    range = request.GET.get('note_range', 'e - g')
    
    # Redirect if not a chord request
    if category_id == '2':
        return redirect('show_arpeggio_fretboard')
    elif category_id == '1':
        return redirect('show_scale_fretboard')
    
    # Get chord object
    chord_object = ChordNotes.objects.get(chord_name=chord_select_name,
                                         type_name=type_id, range=range)
    
    # Get related data
    tonal_root = chord_object.tonal_root
    position_options = ChordPosition.objects.filter(notes_name_id=chord_object.id)
    
    # Generate chord JSON data
    chord_json_data = {
        "chord": chord_object.chord_name,
        "type": chord_object.type_name,
        "root": get_root_note(root_pitch, tonal_root, root_id),
        "note_range": range
    }
    
    # Add inversions and positions
    for inversion in position_options:
        position_json_data = get_position_dict(...)
        chord_json_data[inversion.inversion_order] = position_json_data
    
    # Format for JSON
    chord_json_data = json.dumps(chord_json_data)
    
    # Render template with context
    return render(request, 'fretboard.html', context)
```

## Helpers (views_helpers.py)

The `get_menu_options` function provides navigation data for all views:

```python
def get_menu_options():
    # IDs of the categories
    scales_category_id = 1  # ID 1 = Scales
    arpeggios_category_id = 2  # ID 2 = Arpeggios
    chords_category_id = 3  # ID 3 = Chords

    # Retrieve the categories
    scales_category = NotesCategory.objects.get(id=scales_category_id)
    arpeggios_category = NotesCategory.objects.get(id=arpeggios_category_id)
    chords_category = NotesCategory.objects.get(id=chords_category_id)

    # Retrieve notes based on the categories
    scales = Notes.objects.filter(category=scales_category).values('id', 'note_name')
    arpeggios = Notes.objects.filter(category=arpeggios_category).values('id', 'note_name')
    chords = ChordNotes.objects.filter(category=chords_category).values('id', 'type_name')
    
    # Remove duplicates from chords
    unique_chords = list({chord['type_name']: chord for chord in chords}.values())

    # Return the menu options
    return {
        'scales_options': list(scales),
        'arpeggios_options': list(arpeggios),
        'chords_options': unique_chords,
    }
```

## Position Calculation Logic

### Scale Position Calculation

The scale position calculation happens in `get_position_dict_scales.py`:

```python
def get_scale_position_dict(scale_name, root_id, root_pitch, tonal_root, root_name):
    # Get positions from database
    notes_object = Notes.objects.filter(note_name=scale_name).first()
    all_positions = NotesPosition.objects.filter(notes_name=notes_object)
    
    # Initialize result dictionary
    position_dict = {}
    
    # Process each position
    for position in all_positions:
        positions = []
        
        # Add each note to the position
        for string in string_names:
            # Calculate note placement on string
            note = calculate_note_position(root_pitch, position.first_note, string)
            positions.append({string: note})
        
        # Add to result dictionary
        position_dict[position.position_order] = positions
    
    return position_dict
```

### Chord Position Calculation

The chord position calculation happens in `get_position_dict_chords.py`:

```python
def get_position_dict(inversion_name, chord_name, string_range, 
                      type_name, root_pitch, tonal_root, root_name):
    # Get chord objects
    chord_object = ChordNotes.objects.get(chord_name=chord_name,
                                         type_name=type_name,
                                         range=string_range)
    
    position_object = ChordPosition.objects.get(notes_name=chord_object,
                                              inversion_order=inversion_name)
    
    # Initialize result array
    positions = []
    
    # Calculate note placements
    if chord_object.first_note_string:
        note = calculate_note_position(root_pitch, position_object.first_note, 
                                     chord_object.first_note_string)
        positions.append({chord_object.first_note_string: note})
    
    # Add more notes...
    
    return positions
```

## Note Position Mapping

The actual mapping of notes to fretboard positions happens with the template_notes.py `STRING_NOTE_OPTIONS` dictionary:

```python
def calculate_note_position(root_pitch, interval, string):
    # Calculate the resulting pitch
    note_pitch = (root_pitch + interval) % 12
    
    # Get the corresponding note name
    note_name = NOTE_NAMES[note_pitch].lower()
    
    # Look up the positions in STRING_NOTE_OPTIONS
    string_options = STRING_NOTE_OPTIONS[string][0]
    note_options = string_options[note_name]
    
    # Return the note information
    return note_options
```

## 8-String Support in Views

The views support 8-string configuration through:

1. **String names list**: Includes all eight strings in the correct order
   ```python
   string_names = ['lowBString', 'ELowString', 'AString', 'dString', 
                  'gString', 'bString', 'eString', 'highAString']
   ```

2. **Template context**: Passed to the template for rendering
   ```python
   context = {
       # ... other context data
       'string_names': string_names,
   }
   ```

3. **Position calculation**: Adapts based on the available strings in the database

## Frontend Integration

The backend passes position data to the frontend as JSON:

```python
scale_json_data = json.dumps(position_json_data)
context = {
    'scale_json_data': scale_json_data,
    # ... other context
}
```

In the template, this data is accessed with JavaScript:

```javascript
// In fretboard.html
var scaleData = JSON.parse('{{ scale_json_data|safe }}');
// Use scaleData to render the fretboard
```

## URL Routing

The URL routing is defined in `urls.py`:

```python
urlpatterns = [
    path('', views_scale.fretboard_scale_view, name='show_scale_fretboard'),
    path('arpeggio/', views_arpeggio.fretboard_arpeggio_view, name='show_arpeggio_fretboard'),
    path('chords/', views_chords.fretboard_chords_view, name='show_chords_fretboard'),
    path('about/', views.about_view, name='about'),
    path('impressum/', views.impressum_view, name='impressum'),
]
```

Each view is associated with a specific URL pattern and name for reverse lookups.

## View Optimization

### Caching Opportunities

For better performance, consider caching:

1. **Menu Options**: Cache the results of `get_menu_options()`
2. **Position Dictionaries**: Cache the generated position dictionaries

```python
from django.core.cache import cache

# Cache key based on parameters
cache_key = f"scale_{root_id}_{notes_options_id}_{position_id}"

# Try to get from cache first
position_json_data = cache.get(cache_key)
if position_json_data is None:
    # Generate if not in cache
    position_json_data = get_scale_position_dict(...)
    # Store in cache for future requests
    cache.set(cache_key, position_json_data, 60*60*24)  # 24 hour cache
```

### Database Query Optimization

Reduce database queries by:

1. **Using select_related**: For foreign key relationships
   ```python
   chord_object = ChordNotes.objects.select_related('category').get(id=notes_options_id)
   ```

2. **Prefetching related objects**: For reverse relationships
   ```python
   position_options = NotesPosition.objects.prefetch_related('notes_name').filter(...)
   ```

## Custom Template Tags

The application uses custom template tags in the `templatetags` directory for additional template functionality.

## Extending the Views

To add a new view for a different musical concept:

1. Create a new view file (e.g., `views_new_concept.py`)
2. Define the view function following the pattern of existing views
3. Add appropriate URL pattern in `urls.py`
4. Create or modify templates as needed
5. Add the new option to `get_menu_options()` in `views_helpers.py`
