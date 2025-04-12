from .models import Root
from .template_notes import NOTES, NOTES_SHARP, OCTAVES, SHARP_NOTES

def get_root_note(root: int, tonal_root: int, root_id: int) -> list[str]:
    """
    Calculates all possible note names for a given root pitch across multiple octaves,
    considering sharp/flat preference.

    Args:
        root: The base pitch index of the root note (0-11).
        tonal_root: An integer offset, often used for modal context, which also influences sharp/flat preference.
        root_id: The primary key (ID) of the Root object in the database, used to determine sharp/flat preference based on the root note's name (e.g., "C#" vs "Db").

    Returns:
        A list of strings, where each string is a note name with its octave number
        (e.g., ['C2', 'C3', 'C4']).
    """

    # 1. Determine Sharp/Flat Preference & Select Note List
    selected_root_name = Root.objects.get(pk=root_id).name

    # Calculate combined tonal root for SHARP_NOTES check, correcting the normalization logic from reference
    combined_tonal_root = int(tonal_root) + int(root)
    if combined_tonal_root >= 12: # Corrected normalization check (was > 12 in ref)
         combined_tonal_root -= 12 # Normalize to 0-11 range

    # Use the combined_tonal_root for the check, as was done implicitly via all_notes_append in ref
    if combined_tonal_root in SHARP_NOTES or "#" in selected_root_name:
        notes_to_use = NOTES_SHARP
    else:
        notes_to_use = NOTES

    # 2. Build Master Note List (all_notes)
    all_notes = []
    for octave in OCTAVES:
        for note_name in notes_to_use:
            all_notes.append(note_name + str(octave))

    # 3. Calculate Root Pitch Indices (root_pitch_list)
    root_pitch_list = []
    for octave in OCTAVES:
        # Ensure root is treated as int
        absolute_pitch_index = octave * 12 + int(root)
        root_pitch_list.append(absolute_pitch_index)

    # 4. Select Root Notes
    notes_note_list = []
    for pitch_index in root_pitch_list:
        # Basic bounds check for safety, although logic should ensure correctness
        if 0 <= pitch_index < len(all_notes):
             notes_notes = all_notes[pitch_index]
             notes_note_list.append(notes_notes)
        # else: Consider logging or raising an error if index is out of bounds in a real application

    # 5. Return
    return notes_note_list
