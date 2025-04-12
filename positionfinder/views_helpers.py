# positionfinder/views_helpers.py
from positionfinder.models import Notes, NotesCategory  # Scales and Arpeggios
from positionfinder.models_chords import ChordNotes  # Chords

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

def get_string_config(request):
    """
    Determine string configuration (6 or 8 strings) based on request parameters.
    Returns appropriate string names and a flag for 8-string mode.
    """
    eight_string_mode = request.GET.get('eight_string', '0') == '1'
    
    if eight_string_mode:
        # 8-string configuration with high A and low B strings
        string_names = [
            'highAString', 'eString', 'bString', 'gString', 
            'dString', 'AString', 'ELowString', 'lowBString'
        ]
    else:
        # Standard 6-string configuration
        string_names = ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString']
        
    return {
        'string_names': string_names,
        'eight_string_mode': eight_string_mode,
    }
