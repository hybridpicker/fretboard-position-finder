"""
Context processors for providing data to templates globally.
"""
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
    
    # Chord type options
    # Get distinct type_name values from ChordNotes and ensure they're unique
    chord_type_options = list(set(ChordNotes.objects.values_list('type_name', flat=True)))
    chord_type_options.sort()  # Sort alphabetically
    
    # Hard-code the chord types for now to ensure only "Triads" and "Spread Triads" appear once
    # This is a temporary solution until we figure out why duplicates are appearing
    if "Triads" in chord_type_options and "Spread Triads" in chord_type_options:
        chord_type_options = ["Spread Triads", "Triads"]  # Reset to just these two values
    
    # For chord names, ranges, and positions, we can't preload all combinations
    # These will be loaded via AJAX when the user selects a chord type
    
    return {
        'unified_menu_root_options': root_options,
        'unified_menu_scale_options': scale_options,
        'unified_menu_arpeggio_options': arpeggio_options,
        'unified_menu_chord_type_options': chord_type_options,
    }
