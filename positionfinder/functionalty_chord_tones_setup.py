from .models import Root
from .models_chords import ChordNotes
from .note_setup import build_notes
from .template_notes import TENSIONS, NOTE_NAMES
from .template_notes import NOTE_NAMES_SHARP, SHARP_NOTES

def get_functionalty_tones(notes_options_id, root):
    ALL_NOTES = [x for x in TENSIONS]
    notes = ChordNotes.objects.get(pk=notes_options_id)
    NOTES_NOTES = build_notes(notes)
    '''
    Picking out every note of range
    '''
    ALL_NOTES_NOTES = [x for x in NOTES_NOTES]
    TENSION_NOTE_LIST = [ALL_NOTES[x] for x in ALL_NOTES_NOTES]
    return TENSION_NOTE_LIST

def get_functionalty_pitches(notes_options_id, root):
    ALL_NOTES = [x for x in TENSIONS]
    notes = ChordNotes.objects.get(pk=notes_options_id)
    NOTES_NOTES = build_notes(notes)
    '''
    Picking out every note of range
    '''
    ALL_NOTES_NOTES = [x for x in NOTES_NOTES]
    return ALL_NOTES_NOTES

def get_tension_final_list(tonal_root, ALL_NOTES_NOTES, ALL_NOTES, NOTES_NOTES):
    TENSION_NOTE_FINAL = [int(x)+tonal_root for x in ALL_NOTES_NOTES]
    TENSION_NOTE_FINAL = [x-12 if x>=12 else x for x in TENSION_NOTE_FINAL]
    TENSION_NOTE_LIST = [ALL_NOTES[x] for x in TENSION_NOTE_FINAL]
    return TENSION_NOTE_LIST

def get_all_notes_functionality(root, root_id):
    selected_root_name = Root.objects.get(pk=root_id).name
    if root in SHARP_NOTES or '#' in selected_root_name:
        ALL_NOTES = [x for x in NOTE_NAMES_SHARP]
    else:
        ALL_NOTES = [x for x in NOTE_NAMES]
    return ALL_NOTES

def get_functionalty_note_names(notes_options_id, root, tonal_root, root_id):
    ALL_NOTES = get_all_notes_functionality(root, root_id)
    tonal_root =+ root
    selected_root_name = Root.objects.get(pk=root_id).name
    notes = ChordNotes.objects.get(pk=notes_options_id)
    NOTES_NOTES = build_notes(notes)
    ALL_NOTES_NOTES = [x for x in NOTES_NOTES]
    TENSION_NOTE_FINAL = get_tension_final_list(tonal_root, ALL_NOTES_NOTES, ALL_NOTES, NOTES_NOTES)
    return TENSION_NOTE_FINAL
