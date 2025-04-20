from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.template_notes import NOTES, NOTES_SHARP, TENSIONS, INVERSIONS, SHARP_NOTES
from positionfinder.template_notes import STRING_NOTE_OPTIONS
import numpy

def get_position_dict(chord_inversion, chord_name, range, type_name, root_pitch, tonal_root, selected_root_name):
    """Generate a position dictionary for a chord with given parameters.
    
    This function calculates and returns the actual notes, frets and tensions
    for a specific chord inversion on a specific string range.
    """
    
    # Get the inversion index
    x = INVERSIONS.index(chord_inversion)
    
    # Fetch the chord model instances
    chord_note = ChordNotes.objects.filter(chord_name=chord_name, range=range, type_name=type_name).first()
    if not chord_note:
        return {}
        
    chord_notes_position = ChordPosition.objects.filter(notes_name_id=chord_note.id)
    if not chord_notes_position or x >= len(chord_notes_position):
        return {}
    
    # Initialize our position dictionary
    POSITION_DICT = {}
    
    # Prepare chord data arrays for processing
    CHORD_NOTES = [
        chord_note.first_note, chord_note.second_note,
        chord_note.third_note, chord_note.fourth_note,
        chord_note.fifth_note, chord_note.sixth_note
    ]
    
    CHORD_NOTES_STRING = [
        chord_note.first_note_string, chord_note.second_note_string,
        chord_note.third_note_string, chord_note.fourth_note_string,
        chord_note.fifth_note_string, chord_note.sixth_note_string
    ]
    
    CHORD_NOTES_POSITION = [
        chord_notes_position[x].first_note, chord_notes_position[x].second_note,
        chord_notes_position[x].third_note, chord_notes_position[x].fourth_note,
        chord_notes_position[x].fifth_note, chord_notes_position[x].sixth_note
    ]
    
    # Compute combined tonal root
    combined_tonal_root = tonal_root + root_pitch
    
    # First pass: calculate fret distances to determine if we need octave adjustments
    fret_distance = []
    valid_notes_count = 0
    
    for i, note_value in enumerate(CHORD_NOTES):
        if note_value is None:
            continue
            
        valid_notes_count += 1
        chord_note_index = normalize_pitch_index(note_value + root_pitch + CHORD_NOTES_POSITION[i])
        
        # Select appropriate note name (sharp or flat)
        if combined_tonal_root in SHARP_NOTES or '#' in selected_root_name:
            chord_note_name = NOTES_SHARP[chord_note_index]
        else:
            chord_note_name = NOTES[chord_note_index]
        
        chord_note_string = CHORD_NOTES_STRING[i]
        try:
            chord_note_fret = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["fret"][0]
            fret_distance.append(chord_note_fret)
        except (KeyError, IndexError) as e:
            # Handle or log the error if necessary, e.g., print(f"Error processing note: {e}")
            pass # Continue if note/fret lookup fails
    
    # Check if we need octave adjustments based on fret distance
    needs_octave_adjustment = False
    if len(fret_distance) > 1:
        # Calculate absolute differences between adjacent frets
        fret_differences = [abs(x) for x in numpy.diff(fret_distance)]
        needs_octave_adjustment = any(diff >= 6 for diff in fret_differences)
    
    # Reset for final pass
    index = 0
    
    # Track which strings are explicitly assigned
    assigned_strings = []
    
    # Process each note
    for i, note_value in enumerate(CHORD_NOTES):
        if note_value is None:
            continue
        
        # Calculate the actual note index
        chord_note_index = normalize_pitch_index(note_value + root_pitch + CHORD_NOTES_POSITION[i])
        
        # Get note name (sharp or flat notation)
        if combined_tonal_root in SHARP_NOTES or '#' in selected_root_name:
            chord_note_name = NOTES_SHARP[chord_note_index]
        else:
            chord_note_name = NOTES[chord_note_index]
        
        chord_note_string = CHORD_NOTES_STRING[i]
        
        # Track explicitly assigned strings - only if the string is valid
        if chord_note_string and chord_note_string in STRING_NOTE_OPTIONS:
            assigned_strings.append(chord_note_string)
        elif chord_note_string:
            # Handle cases where chord_note_string exists but is not in STRING_NOTE_OPTIONS if needed
            pass
        
        # Handle octave selection based on fret distance analysis
        try:
            if needs_octave_adjustment:
                # Try to use the alternate octave for better fingering
                try:
                    note_name = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["tone"][1]
                except IndexError:
                    note_name = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["tone"][0]
            else:
                # Use the default octave
                note_name = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["tone"][0]
        except (KeyError, IndexError) as e:
            # Fallback to just the note name
            note_name = chord_note_name
        
        # Calculate tension/function (1=root, 3=third, 5=fifth, etc.)
        chord_note_tension_index = normalize_pitch_index(note_value + CHORD_NOTES_POSITION[i])
        chord_note_tension = TENSIONS[chord_note_tension_index]
        
        # For the GUI - is this an assigned note (not just a passing tone)
        is_assigned = True
        
        # Determine if this is the root note by comparing its absolute pitch class
        # to the selected root's pitch class.
        actual_note_pitch_class = normalize_pitch_index(note_value + root_pitch + CHORD_NOTES_POSITION[i])
        selected_root_pitch_class = normalize_pitch_index(root_pitch)
        is_root = (actual_note_pitch_class == selected_root_pitch_class)
        
        # Add to position dictionary - enhanced format with additional metadata
        if chord_note_string in STRING_NOTE_OPTIONS:
            POSITION_DICT[chord_note_string] = [
                note_name,            # The actual note name with octave
                chord_note_tension,   # The function (R, 3, 5, etc.)
                is_assigned,          # Explicitly flag this as an assigned note
                is_root               # Is this a root note
            ]
        else:
            # Handle cases where chord_note_string is not in STRING_NOTE_OPTIONS if needed
            pass
        
        index += 1
    
    # Add the list of assigned strings to the dictionary
    POSITION_DICT['assigned_strings'] = assigned_strings
    
    return POSITION_DICT


def normalize_pitch_index(pitch_index):
    """Normalize a pitch index to be within the 0-11 range."""
    while pitch_index >= 12:
        pitch_index -= 12
    return pitch_index

# Ensure that get_position_dict is correctly exported
__all__ = ['get_position_dict']