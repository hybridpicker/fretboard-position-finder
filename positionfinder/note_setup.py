from django.forms.models import model_to_dict
from .models import Notes, Root
from .models_chords import ChordNotes
from .template_notes import NOTES, NOTES_SHARP, OCTAVES, SHARP_NOTES

''' notes_notes from Field '''
def build_notes(notes):
    # Handle Notes model
    if isinstance(notes, Notes):
        cleaned = model_to_dict(notes,
                                fields=[field.name for field in Notes._meta.fields if field.name not in
                                        ["note_name", "category", "id", "tonal_root", "ordering", "chords"]])
    # Handle ChordNotes model
    elif isinstance(notes, ChordNotes):
        cleaned = model_to_dict(notes,
                                fields=[field.name for field in ChordNotes._meta.fields if field.name not in
                                        ["chord_name", "category", "id", "tonal_root", "ordering", "type_name", 
                                         "chord_ordering", "range", "range_ordering"]])
    else:
        # Default empty dict if neither model matches
        cleaned = {}
        
    return [v for f, v in cleaned.items() if v is not None]

def get_tonal_all_notes_append(tonal_root, selected_root_name):
    all_notes = []
    if tonal_root in SHARP_NOTES or '#' in selected_root_name:
        for x in OCTAVES:
            for y in NOTES_SHARP:
                all_notes.append(y+str(x))
    else:
        for x in OCTAVES:
            for y in NOTES:
                all_notes.append(y+str(x))
    return all_notes

def all_notes_append(root, all_notes, notes_notes):
    all_notes_notes = []
    for y in OCTAVES:
        octave = y * 12 + int(root)
        for x in notes_notes:
            if x + octave < len(all_notes):
                all_notes_notes.append(x + octave)
    return all_notes_notes

# Create your views here.
def get_notes_tones(notes_options_id, root, tonal_root, root_id):
    tonal_root = int(tonal_root) + int(root)
    selected_root_name = Root.objects.get(pk=root_id).name
    if tonal_root > 12:
        root -= 12
    all_notes = get_tonal_all_notes_append(tonal_root, selected_root_name)
    
    # Try to get from Notes model first
    try:
        notes = Notes.objects.get(pk=notes_options_id)
    except Notes.DoesNotExist:
        # If not found, try to get from ChordNotes model (for arpeggios)
        try:
            notes = ChordNotes.objects.get(pk=notes_options_id)
        except ChordNotes.DoesNotExist:
            # If not found in either model, return empty list
            return []
    
    notes_notes = build_notes(notes)
    # Picking out every note of range
    all_notes_notes = all_notes_append(root, all_notes, notes_notes)
    notes_note_list = []
    for x in all_notes_notes:
        notes_notes = all_notes[x]
        notes_note_list.append(notes_notes)
    return notes_note_list
