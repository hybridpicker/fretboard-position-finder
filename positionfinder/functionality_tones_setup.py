from .models import Notes, Root
from .models_chords import ChordNotes
from .note_setup import build_notes
from .template_notes import (
    NOTE_NAMES,
    NOTE_NAMES_OPTION,
    NOTE_NAMES_SHARP,
    NOTE_NAMES_SHARP_OPTION,
    SHARP_NOTES,
    TENSIONS,
    TENSIONS_OPTIONAL,
)


def find_tone(tone: str, lst: list) -> bool:
    """Whether the tone occurs in any entry of the list."""
    return any(tone in x for x in lst)


def get_notes_object(notes_options_id: int) -> Notes | ChordNotes | None:
    """
    Try to get notes from Notes or ChordNotes model
    """
    try:
        return Notes.objects.get(pk=notes_options_id)
    except Notes.DoesNotExist:
        try:
            return ChordNotes.objects.get(pk=notes_options_id)
        except ChordNotes.DoesNotExist:
            return None


def get_functionality_tones(notes_options_id: int, root: int) -> list[str]:
    """Return the tension names (R, 3, 5, ...) of a scale or chord."""
    ALL_NOTES = [x for x in TENSIONS]
    ALL_NOTES_OPTIONAL = [x for x in TENSIONS_OPTIONAL]

    notes = get_notes_object(notes_options_id)
    if not notes:
        return []

    NOTES_NOTES = build_notes(notes)
    """
    Picking out every note of range
    """
    ALL_NOTES_LIST = []
    for x in NOTES_NOTES:
        if find_tone(ALL_NOTES[x], ALL_NOTES_LIST):
            """
            TODO: Define function that also find multiple tension:
            If b11 already in list use optional Tension
            """
            ALL_NOTES_LIST.append(ALL_NOTES_OPTIONAL[x])
        else:
            ALL_NOTES_LIST.append(ALL_NOTES[x])
    return ALL_NOTES_LIST


def get_functionality_pitches(notes_options_id: int, root: int) -> list[str]:
    """Return the tension names of a scale or chord, using optional names for repeats."""
    ALL_NOTES = [x for x in TENSIONS]
    ALL_NOTES_OPTIONAL = [x for x in TENSIONS_OPTIONAL]

    notes = get_notes_object(notes_options_id)
    if not notes:
        return []

    NOTES_NOTES = build_notes(notes)
    """
    Picking out every note of range
    """
    ALL_NOTES_LIST = []
    for x in NOTES_NOTES:
        if find_tone(ALL_NOTES[x], ALL_NOTES_LIST):
            """
            Check if consequent C - B Tones are in a heptatonic Scale
            """
            ALL_NOTES_LIST.append(ALL_NOTES_OPTIONAL[x])
        else:
            ALL_NOTES_LIST.append(ALL_NOTES[x])
    return ALL_NOTES_LIST


def get_tension_final_list(
    tonal_root: int,
    ALL_NOTES_NOTES: list,
    ALL_NOTES: list,
    NOTES_NOTES: list,
    ALL_NOTES_OPTIONAL: list,
) -> list[str]:
    """Map note values onto note names, using optional names for repeated letters."""
    TENSION_NOTE_FINAL = [int(x) + tonal_root for x in ALL_NOTES_NOTES]
    TENSION_NOTE_FINAL = [x - 12 if x >= 12 else x for x in TENSION_NOTE_FINAL]
    TENSION_LIST = []
    for x in TENSION_NOTE_FINAL:
        if find_tone(ALL_NOTES[x], TENSION_LIST):
            TENSION_LIST.append(ALL_NOTES_OPTIONAL[x])
        else:
            TENSION_LIST.append(ALL_NOTES[x])
    return TENSION_LIST


def get_all_notes_functionality(root: int, root_id: int) -> list[str]:
    """Return the 12 note names in sharp or flat spelling."""
    selected_root_name = Root.objects.get(pk=root_id).name
    if root in SHARP_NOTES or "#" in selected_root_name:
        ALL_NOTES = [x for x in NOTE_NAMES_SHARP]
    else:
        ALL_NOTES = [x for x in NOTE_NAMES]
    return ALL_NOTES


def get_all_notes_functionality_optional(root: int, root_id: int) -> list[str]:
    """Return the 12 optional (enharmonic) note names in sharp or flat spelling."""
    selected_root_name = Root.objects.get(pk=root_id).name
    if root in SHARP_NOTES or "#" in selected_root_name:
        ALL_NOTES = [x for x in NOTE_NAMES_SHARP_OPTION]
    else:
        ALL_NOTES = [x for x in NOTE_NAMES_OPTION]
    return ALL_NOTES


def get_functionality_note_names(
    notes_options_id: int, root: int, tonal_root: int, root_id: int
) -> list[str]:
    """Return the note names of a scale or chord for the selected root."""
    ALL_NOTES = get_all_notes_functionality(root, root_id)
    ALL_NOTES_OPTIONAL = get_all_notes_functionality_optional(root, root_id)
    tonal_root += root
    Root.objects.get(pk=root_id)  # raises DoesNotExist for an unknown root id

    notes = get_notes_object(notes_options_id)
    if not notes:
        return []

    NOTES_NOTES = build_notes(notes)
    ALL_NOTES_NOTES = [x for x in NOTES_NOTES]
    TENSION_NOTE_FINAL = get_tension_final_list(
        tonal_root, ALL_NOTES_NOTES, ALL_NOTES, NOTES_NOTES, ALL_NOTES_OPTIONAL
    )
    return TENSION_NOTE_FINAL
