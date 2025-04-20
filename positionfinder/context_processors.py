"""
Context processors for providing data to templates globally.
"""
import re # Needed for natural sort
from django.conf import settings
from positionfinder.models import Root, Notes, NotesCategory
from positionfinder.positions import NotesPosition
from positionfinder.models_chords import ChordNotes, ChordPosition

def unified_menu_context(request):
    """
    Provides context variables needed for the unified menu.
    This makes all menu options available without requiring separate API calls.
    """
    # Root options (same for all modes)
    root_options = Root.objects.all().order_by('pitch', 'name')
    
    # Scale options (category_id=1)
    scale_options = Notes.objects.filter(category_id=1).order_by('ordering', 'note_name')
    
    # Arpeggio options (category_id=2)
    arpeggio_options = Notes.objects.filter(category_id=2).order_by('ordering', 'note_name')
    
    # Chord type options - Fetch and separate standard/V-System
    all_type_names = ChordNotes.objects.values_list('type_name', flat=True).distinct()

    standard_types = []
    v_system_types = []

    for t in all_type_names:
        if t in ['Triads', 'Spread Triads']:
            standard_types.append(t)
        elif t and t.startswith('V') and t[1:].isdigit(): # Check if it looks like a V-System type
            v_system_types.append(t)

    # Ensure standard types have a specific order
    ordered_standard_types = []
    if 'Triads' in standard_types: ordered_standard_types.append('Triads')
    if 'Spread Triads' in standard_types: ordered_standard_types.append('Spread Triads')
    if 'Triads' not in ordered_standard_types: # Fallback
         ordered_standard_types.insert(0, 'Triads')

    # Sort V-System types naturally (V1, V2, V3...)
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', s)]
    v_system_types_sorted = sorted(list(set(v_system_types)), key=natural_sort_key)

    # Prepare the dictionary structure expected by the template
    chord_type_options_dict = {
        'standard_types': ordered_standard_types,
        'v_system_types': v_system_types_sorted
    }
    
    # For chord names, ranges, and positions, we can't preload all combinations
    # These will be loaded via AJAX when the user selects a chord type
    
    return {
        'unified_menu_root_options': root_options,
        'unified_menu_scale_options': scale_options,
        'unified_menu_arpeggio_options': arpeggio_options,
        'unified_menu_chord_type_options': chord_type_options_dict, # Use the new dictionary
    }

def app_version_context(request):
    """
    Provides the application version to templates.
    """
    return {
        'APP_VERSION': getattr(settings, 'VERSION', '2.1'),
    }
