# positionfinder/root_chord_note_setup.py
from .models import Root
from .template_notes import NOTES, NOTES_SHARP, OCTAVES, SHARP_NOTES

def all_notes_append(tonal_root, root_id):
    all_notes = []
    selected_root_name = Root.objects.get(pk=root_id).name
    if tonal_root in SHARP_NOTES or "#" in selected_root_name:
        for x in OCTAVES:
            for y in NOTES_SHARP:
                all_notes.append(y+str(x))
    else:
        for x in OCTAVES:
            for y in NOTES:
                all_notes.append(y+str(x))
    return all_notes

def root_pitch_list_append(root):
    root_pitch_list = []
    for y in OCTAVES:
        z = y*12+root
        root_pitch_list.append(z)
    return root_pitch_list

# Get every possible RootNote from Pitch
def get_root_note(root, tonal_root, root_id):
    notes_note_list = []
    tonal_root = int(tonal_root) + int(root)
    if tonal_root > 12:
        tonal_root -= 12
    all_notes = all_notes_append(tonal_root, root_id)
    root_pitch_list = root_pitch_list_append(root)
    for x in root_pitch_list:
        notes_notes = all_notes[x]
        notes_note_list.append(notes_notes)
    return notes_note_list
