from .models import Notes, Root
from .note_setup import build_notes
from .template_notes import TENSIONS, TENSIONS_OPTIONAL, NOTE_NAMES
from .template_notes import HEPTATONIC_BASE_NOTES
from .template_notes import SHARP_NOTES, NOTE_NAMES_OPTION
from .template_notes import NOTE_NAMES_SHARP,NOTE_NAMES_SHARP_OPTION, SHARP_NOTES

def find_tone(tone, lst):
    return any(tone in x for x in lst)

def get_functionality_tones(notes_options_id, root):
    ALL_NOTES = [x for x in TENSIONS]
    ALL_NOTES_OPTIONAL = [x for x in TENSIONS_OPTIONAL]
    notes = Notes.objects.get(pk=notes_options_id)
    NOTES_NOTES = build_notes(notes)
    '''
    Picking out every note of range
    '''
    ALL_NOTES_LIST = []
    for x in NOTES_NOTES:
        if find_tone(ALL_NOTES[x], ALL_NOTES_LIST):
            '''
            TODO: Define function that also find multiple tension:
            If b11 already in list use optional Tension
            '''
            ALL_NOTES_LIST.append(ALL_NOTES_OPTIONAL[x])
        else:
            ALL_NOTES_LIST.append(ALL_NOTES[x])
    return ALL_NOTES_LIST

def get_functionality_pitches(notes_options_id, root):
    ALL_NOTES = [x for x in TENSIONS]
    ALL_NOTES_OPTIONAL = [x for x in TENSIONS_OPTIONAL]
    notes = Notes.objects.get(pk=notes_options_id)
    NOTES_NOTES = build_notes(notes)
    '''
    Picking out every note of range
    '''
    ALL_NOTES_LIST = []
    for x in NOTES_NOTES:
        if find_tone(ALL_NOTES[x], ALL_NOTES_LIST):
            '''
            Check if consequent C - B Tones are in a heptatonic Scale
            '''
            ALL_NOTES_LIST.append(ALL_NOTES_OPTIONAL[x])
        else:
            ALL_NOTES_LIST.append(ALL_NOTES[x])
    return ALL_NOTES_LIST

def get_tension_final_list(tonal_root, ALL_NOTES_NOTES, ALL_NOTES, NOTES_NOTES, ALL_NOTES_OPTIONAL):
    TENSION_NOTE_FINAL = [int(x)+tonal_root for x in ALL_NOTES_NOTES]
    TENSION_NOTE_FINAL = [x-12 if x>=12 else x for x in TENSION_NOTE_FINAL]
    TENSION_LIST = []
    for x in TENSION_NOTE_FINAL:
        if find_tone(ALL_NOTES[x], TENSION_LIST):
            TENSION_LIST.append(ALL_NOTES_OPTIONAL[x])
        else:
            TENSION_LIST.append(ALL_NOTES[x])
    return TENSION_LIST

def get_all_notes_functionality(root, root_id):
    selected_root_name = Root.objects.get(pk=root_id).name
    if root in SHARP_NOTES or '#' in selected_root_name:
        ALL_NOTES = [x for x in NOTE_NAMES_SHARP]
    else:
        ALL_NOTES = [x for x in NOTE_NAMES]
    return ALL_NOTES


def get_all_notes_functionality_optional(root, root_id):
    selected_root_name = Root.objects.get(pk=root_id).name
    if root in SHARP_NOTES or '#' in selected_root_name:
        ALL_NOTES = [x for x in NOTE_NAMES_SHARP_OPTION]
    else:
        ALL_NOTES = [x for x in NOTE_NAMES_OPTION]
    return ALL_NOTES


def get_functionality_note_names(notes_options_id, root, tonal_root, root_id):
    ALL_NOTES = get_all_notes_functionality(root, root_id)
    ALL_NOTES_OPTIONAL = get_all_notes_functionality_optional(root, root_id)
    tonal_root =+ root
    selected_root_name = Root.objects.get(pk=root_id).name
    notes = Notes.objects.get(pk=notes_options_id)
    NOTES_NOTES = build_notes(notes)
    ALL_NOTES_NOTES = [x for x in NOTES_NOTES]
    TENSION_NOTE_FINAL = get_tension_final_list(tonal_root, ALL_NOTES_NOTES, ALL_NOTES, NOTES_NOTES, ALL_NOTES_OPTIONAL)
    return TENSION_NOTE_FINAL
