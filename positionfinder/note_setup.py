# positionfinder/note_setup.py
from django.forms.models import model_to_dict
from .models import Notes, Root
from .template_notes import NOTES, NOTES_SHARP, OCTAVES, SHARP_NOTES

''' notes_notes from Field '''
def build_notes(notes):
    cleaned = model_to_dict(notes,
                            fields=[field.name for field in Notes._meta.fields if field.name not in
                                    ["note_name", "category", "id", "tonal_root", "ordering", "chords"]])
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
    notes = Notes.objects.get(pk=notes_options_id)
#    root = pitches[0]
    notes_notes = build_notes(notes)
    # Picking out every note of range
    all_notes_notes = all_notes_append(root, all_notes, notes_notes)
    notes_note_list = []
    for x in all_notes_notes:
        notes_notes = all_notes[x]
        notes_note_list.append(notes_notes)
    return notes_note_list
