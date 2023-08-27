from .models import Notes, Root
from .note_setup import build_notes
from .template_notes import TENSIONS, TENSIONS_OPTIONAL, NOTE_NAMES
from .template_notes import SHARP_NOTES, NOTE_NAMES_OPTION
from .template_notes import NOTE_NAMES_SHARP,NOTE_NAMES_SHARP_OPTION, SHARP_NOTES

def initialize_all_notes():
    """Initialize all note choices."""
    return [x for x in TENSIONS], [x for x in TENSIONS_OPTIONAL]

def find_tone(tone, lst):
    """Check if a tone exists in a list."""
    return any(tone in x for x in lst)

def get_functionality_tones(notes_options_id, root):
    """Get functionality tones based on note options and root."""
    ALL_NOTES, ALL_NOTES_OPTIONAL = initialize_all_notes()
    notes = Notes.objects.get(pk=notes_options_id)
    NOTES_NOTES = build_notes(notes)
    ALL_NOTES_LIST = []
    for x in NOTES_NOTES:
        # Choose the appropriate list based on whether the tone already exists
        target_list = ALL_NOTES_OPTIONAL if find_tone(ALL_NOTES[x], ALL_NOTES_LIST) else ALL_NOTES
        ALL_NOTES_LIST.append(target_list[x])
    return ALL_NOTES_LIST

def get_functionality_pitches(notes_options_id, root):
    """Get functionality pitches based on note options and root."""
    ALL_NOTES, ALL_NOTES_OPTIONAL = initialize_all_notes()
    notes = Notes.objects.get(pk=notes_options_id)
    NOTES_NOTES = build_notes(notes)
    ALL_NOTES_LIST = []
    for x in NOTES_NOTES:
        # Choose the appropriate list based on whether the tone already exists
        target_list = ALL_NOTES_OPTIONAL if find_tone(ALL_NOTES[x], ALL_NOTES_LIST) else ALL_NOTES
        ALL_NOTES_LIST.append(target_list[x])
    return ALL_NOTES_LIST

def get_tension_final_list(tonal_root, ALL_NOTES_NOTES, ALL_NOTES, NOTES_NOTES, ALL_NOTES_OPTIONAL):
    """Get the final list of tension notes."""
    TENSION_NOTE_FINAL = [(int(x) + tonal_root) % 12 for x in ALL_NOTES_NOTES]
    TENSION_LIST = []
    for x in TENSION_NOTE_FINAL:
        # Choose the appropriate list based on whether the tone already exists
        target_list = ALL_NOTES_OPTIONAL if find_tone(ALL_NOTES[x], TENSION_LIST) else ALL_NOTES
        TENSION_LIST.append(target_list[x])
    return TENSION_LIST

def get_all_notes_functionality(root, root_id):
    """Get all notes based on the root and its sharpness."""
    selected_root_name = Root.objects.get(pk=root_id).name
    if root in SHARP_NOTES or '#' in selected_root_name:
        return [x for x in NOTE_NAMES_SHARP]
    return [x for x in NOTE_NAMES]

def get_all_notes_functionality_optional(root, root_id):
    """Get all optional notes based on the root and its sharpness."""
    selected_root_name = Root.objects.get(pk=root_id).name
    if root in SHARP_NOTES or '#' in selected_root_name:
        return [x for x in NOTE_NAMES_SHARP_OPTION]
    return [x for x in NOTE_NAMES_OPTION]

def get_functionality_note_names(notes_options_id, root, tonal_root, root_id):
    """Get the final note names based on various parameters."""
    ALL_NOTES = get_all_notes_functionality(root, root_id)
    ALL_NOTES_OPTIONAL = get_all_notes_functionality_optional(root, root_id)
    tonal_root += root
    notes = Notes.objects.get(pk=notes_options_id)
    NOTES_NOTES = build_notes(notes)
    ALL_NOTES_NOTES = [x for x in NOTES_NOTES]
    TENSION_NOTE_FINAL = get_tension_final_list(tonal_root, ALL_NOTES_NOTES, ALL_NOTES, NOTES_NOTES, ALL_NOTES_OPTIONAL)
    return TENSION_NOTE_FINAL
