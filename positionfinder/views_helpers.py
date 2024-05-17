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
    chords = ChordNotes.objects.filter(category=chords_category).values('id', 'chord_name')[:10]  # Limit chords to 10

    # Debugging outputs
    print("Scales Category:", scales_category)
    print("Scales:", list(scales))
    print("Arpeggios Category:", arpeggios_category)
    print("Arpeggios:", list(arpeggios))
    print("Chords Category:", chords_category)
    print("Chords:", list(chords))

    # Return the menu options
    return {
        'scales_options': list(scales),
        'arpeggios_options': list(arpeggios),
        'chords_options': list(chords),
    }
