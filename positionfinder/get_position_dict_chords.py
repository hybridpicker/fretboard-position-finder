import numpy

from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.template_notes import (
    INVERSIONS,
    NOTES,
    NOTES_SHARP,
    SHARP_NOTES,
    STRING_NOTE_OPTIONS,
    TENSIONS,
)


def _note_fields(obj) -> list:
    """Return the first six note values of a ChordNotes/ChordPosition row."""
    return [
        obj.first_note,
        obj.second_note,
        obj.third_note,
        obj.fourth_note,
        obj.fifth_note,
        obj.sixth_note,
    ]


def _note_name_for(
    note_value: int, offset: int, root_pitch: int, use_sharps: bool
) -> tuple[int, str]:
    """Return (pitch index, sharp/flat note name) of a chord note."""
    chord_note_index = normalize_pitch_index(note_value + root_pitch + offset)
    if use_sharps:
        return chord_note_index, NOTES_SHARP[chord_note_index]
    return chord_note_index, NOTES[chord_note_index]


def _needs_octave_adjustment(
    chord_notes: list, chord_strings: list, offsets: list, root_pitch: int, use_sharps: bool
) -> bool:
    """First pass: do adjacent chord frets jump by 6 or more (alternate octave needed)?"""
    fret_distance = []
    for i, note_value in enumerate(chord_notes):
        if note_value is None:
            continue

        _, chord_note_name = _note_name_for(note_value, offsets[i], root_pitch, use_sharps)
        chord_note_string = chord_strings[i]
        try:
            chord_note_fret = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["fret"][
                0
            ]
            fret_distance.append(chord_note_fret)
        except (KeyError, IndexError):
            pass  # Continue if note/fret lookup fails

    if len(fret_distance) > 1:
        # Calculate absolute differences between adjacent frets
        fret_differences = [abs(x) for x in numpy.diff(fret_distance)]
        return any(diff >= 6 for diff in fret_differences)
    return False


def _tone_name(chord_note_string: str | None, chord_note_name: str, use_alternate: bool) -> str:
    """Return the note name with octave for a string, falling back to the plain name."""
    try:
        if use_alternate:
            # Try to use the alternate octave for better fingering
            tones = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["tone"]
            try:
                return tones[1]
            except IndexError:
                return tones[0]
        # Use the default octave
        return STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["tone"][0]
    except (KeyError, IndexError):
        # Fallback to just the note name
        return chord_note_name


def _note_entry(
    note_value: int,
    offset: int,
    chord_note_string: str | None,
    root_pitch: int,
    use_sharps: bool,
    needs_octave_adjustment: bool,
) -> list:
    """Build the [note name, tension, is_assigned, is_root] entry of one chord note."""
    # Calculate the actual note index and name (sharp or flat notation)
    actual_note_pitch_class, chord_note_name = _note_name_for(
        note_value, offset, root_pitch, use_sharps
    )
    note_name = _tone_name(chord_note_string, chord_note_name, needs_octave_adjustment)

    # Calculate tension/function (1=root, 3=third, 5=fifth, etc.)
    chord_note_tension = TENSIONS[normalize_pitch_index(note_value + offset)]

    # Determine if this is the root note by comparing its absolute pitch class
    # to the selected root's pitch class.
    is_root = actual_note_pitch_class == normalize_pitch_index(root_pitch)

    return [
        note_name,  # The actual note name with octave
        chord_note_tension,  # The function (R, 3, 5, etc.)
        True,  # Explicitly flag this as an assigned note
        is_root,  # Is this a root note
    ]


def get_position_dict(
    chord_inversion: str,
    chord_name: str,
    range: str,
    type_name: str,
    root_pitch: int,
    tonal_root: int,
    selected_root_name: str,
) -> dict:
    """Generate a position dictionary for a chord with given parameters.

    This function calculates and returns the actual notes, frets and tensions
    for a specific chord inversion on a specific string range.
    """

    # Get the inversion index
    x = INVERSIONS.index(chord_inversion)

    # Fetch the chord model instances
    chord_note = ChordNotes.objects.filter(
        chord_name=chord_name, range=range, type_name=type_name
    ).first()
    if not chord_note:
        return {}

    chord_notes_position = ChordPosition.objects.filter(notes_name_id=chord_note.id)
    if not chord_notes_position or x >= len(chord_notes_position):
        return {}

    return _build_position_dict(
        chord_note, chord_notes_position[x], root_pitch, tonal_root, selected_root_name
    )


def _build_position_dict(
    chord_note: ChordNotes,
    position_row: ChordPosition,
    root_pitch: int,
    tonal_root: int,
    selected_root_name: str,
) -> dict:
    """Compute the string -> note entries (plus assigned_strings) of one inversion."""
    # Initialize our position dictionary
    POSITION_DICT = {}

    # Prepare chord data arrays for processing
    CHORD_NOTES = _note_fields(chord_note)
    CHORD_NOTES_STRING = [
        chord_note.first_note_string,
        chord_note.second_note_string,
        chord_note.third_note_string,
        chord_note.fourth_note_string,
        chord_note.fifth_note_string,
        chord_note.sixth_note_string,
    ]
    CHORD_NOTES_POSITION = _note_fields(position_row)

    # Compute combined tonal root
    combined_tonal_root = tonal_root + root_pitch
    use_sharps = combined_tonal_root in SHARP_NOTES or "#" in selected_root_name

    needs_octave_adjustment = _needs_octave_adjustment(
        CHORD_NOTES, CHORD_NOTES_STRING, CHORD_NOTES_POSITION, root_pitch, use_sharps
    )

    # Track which strings are explicitly assigned
    assigned_strings = []

    # Process each note
    for i, note_value in enumerate(CHORD_NOTES):
        if note_value is None:
            continue
        chord_note_string = CHORD_NOTES_STRING[i]

        # Track explicitly assigned strings - only if the string is valid
        if chord_note_string and chord_note_string in STRING_NOTE_OPTIONS:
            assigned_strings.append(chord_note_string)

        # Add to position dictionary - enhanced format with additional metadata
        if chord_note_string in STRING_NOTE_OPTIONS:
            POSITION_DICT[chord_note_string] = _note_entry(
                note_value,
                CHORD_NOTES_POSITION[i],
                chord_note_string,
                root_pitch,
                use_sharps,
                needs_octave_adjustment,
            )

    # Add the list of assigned strings to the dictionary
    POSITION_DICT["assigned_strings"] = assigned_strings

    return POSITION_DICT


def normalize_pitch_index(pitch_index: int) -> int:
    """Normalize a pitch index to be within the 0-11 range."""
    while pitch_index >= 12:
        pitch_index -= 12
    return pitch_index


# Ensure that get_position_dict is correctly exported
__all__ = ["get_position_dict"]
