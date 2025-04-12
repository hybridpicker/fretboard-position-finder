"""
Module for calculating and processing fretboard positions
Contains optimized functions for position calculations, transposition, and position ordering
"""
from collections import OrderedDict
from functools import lru_cache

from .models import Notes
from .positions import NotesPosition
from .template_notes import NOTES, NOTES_SHARP, TENSIONS, SHARP_NOTES
from .template_notes import STRING_NOTE_OPTIONS, STRINGS, NOTES_SCORE


@lru_cache(maxsize=128)
def get_position_data(position_id, root_pitch):
    """
    Get position data with caching for performance
    
    Args:
        position_id: ID of the position
        root_pitch: Root pitch to transpose by
        
    Returns:
        Position data list
    """
    from .get_position import get_notes_position
    return get_notes_position(position_id, root_pitch)


def get_note_list(scale_note, root_pitch, selected_root_name):
    """
    Get list of notes for a scale/arpeggio based on root pitch
    
    Args:
        scale_note: Note model containing scale/arpeggio data
        root_pitch: Pitch of the root note
        selected_root_name: Name of the selected root note
        
    Returns:
        List of notes in the scale/arpeggio
    """
    # Extract scale/arpeggio notes
    scale_notes = [
        scale_note.first_note, scale_note.second_note,
        scale_note.third_note, scale_note.fourth_note,
        scale_note.fifth_note, scale_note.sixth_note,
        scale_note.seventh_note, scale_note.eigth_note,
        scale_note.ninth_note, scale_note.tenth_note,
        scale_note.eleventh_note, scale_note.twelth_note
    ]
    
    # Build list of actual notes based on root pitch
    notes_list = []
    for note in scale_notes:
        if note is not None:
            y = note + root_pitch
            if y >= 12:
                y -= 12
            if root_pitch in SHARP_NOTES or '#' in selected_root_name:
                notes_list.append(NOTES_SHARP[y])
            else:
                notes_list.append(NOTES[y])
                
    return notes_list


def find_transposable_positions(position_options, position_data):
    """
    Find positions that can be transposed down one fret
    
    Args:
        position_options: Number of available positions
        position_data: Dictionary of position data
        
    Returns:
        List of position indices that can be transposed
    """
    transposable_positions = []
    
    for i in range(1, position_options):
        # Skip if position doesn't exist in data
        if str(i) not in position_data:
            continue
            
        actual_position = position_data[str(i)]
        can_transpose = True
        
        for string in STRINGS:
            # Skip strings not in this position
            if string not in actual_position:
                continue
                
            # Skip if no tones on this string
            if not actual_position[string] or 'tones' not in actual_position[string][0]:
                continue
                
            # Check each tone on this string
            tones = actual_position[string][0].get('tones', [])
            for tone in tones:
                # Skip malformed tones
                if not tone or len(tone) < 2:
                    continue
                    
                # Extract base note and pitch
                base_note = tone[:-1]
                pitch = int(tone[-1])
                
                # Check if this tone can be played one fret lower
                lower_tone = f"{base_note}{pitch-1}"
                
                # Check if lower tone is available on this string
                if (string in STRING_NOTE_OPTIONS and
                    base_note in STRING_NOTE_OPTIONS[string][0] and
                    'tone' in STRING_NOTE_OPTIONS[string][0][base_note][0] and
                    lower_tone in STRING_NOTE_OPTIONS[string][0][base_note][0]['tone']):
                    # This tone can be transposed
                    continue
                else:
                    # This tone cannot be transposed
                    can_transpose = False
                    break
                    
            if not can_transpose:
                break
                
        if can_transpose and i not in transposable_positions:
            transposable_positions.append(i)
            
    return transposable_positions


def transpose_positions(position_data, transposable_positions):
    """
    Transpose the identified positions down one fret
    
    Args:
        position_data: Dictionary of position data
        transposable_positions: List of position indices to transpose
        
    Returns:
        Updated position data with transposed positions
    """
    for position_index in transposable_positions:
        position_key = str(position_index)
        
        # Skip if position doesn't exist
        if position_key not in position_data:
            continue
            
        # Process each string in the position
        for string in STRINGS:
            if string not in position_data[position_key]:
                continue
                
            # Skip if no tones or malformed data
            if not position_data[position_key][string] or 'tones' not in position_data[position_key][string][0]:
                continue
                
            # Get the tones for this string
            tones = position_data[position_key][string][0]['tones']
            
            # Transpose each tone down one fret
            transposed_tones = []
            for tone in tones:
                # Skip malformed tones
                if not tone or len(tone) < 2:
                    continue
                    
                # Extract base note and pitch
                base_note = tone[:-1]
                pitch = int(tone[-1])
                
                # Create transposed tone
                transposed_tone = f"{base_note}{pitch-1}"
                transposed_tones.append(transposed_tone)
                
            # Update the tones with transposed ones
            position_data[position_key][string][0]['tones'] = transposed_tones
            
    return position_data


def calculate_position_scores(position_data):
    """
    Calculate a score for each position based on its notes
    
    Args:
        position_data: Dictionary of position data
        
    Returns:
        Ordered dictionary of positions sorted by score
    """
    score_board = {}
    
    # Calculate score for each position
    for i in range(1, len(position_data)):
        position_key = str(i)
        
        # Skip if position doesn't exist or doesn't have E string
        if position_key not in position_data or 'eString' not in position_data[position_key]:
            continue
            
        # Skip if no tones on E string
        if not position_data[position_key]['eString'] or 'tones' not in position_data[position_key]['eString'][0]:
            continue
            
        # Get tones on E string
        e_string_tones = position_data[position_key]['eString'][0]['tones']
        
        # Calculate score for each tone
        tone_scores = []
        for tone in e_string_tones:
            # Skip malformed tones
            if not tone or len(tone) < 2:
                continue
                
            # Extract base note and pitch
            base_note = tone[0]
            pitch = int(tone[-1])
            
            # Calculate score (base note value + octave value)
            if base_note in NOTES_SCORE:
                score = NOTES_SCORE[base_note] + (pitch * 12)
                tone_scores.append(score)
                
        # Calculate average score for the position
        if tone_scores:
            score_board[i] = sum(tone_scores) / len(tone_scores)
            
    # Sort positions by score
    return OrderedDict(sorted(score_board.items(), key=lambda t: t[1]))


def reorder_positions(position_data):
    """
    Reorder positions based on their calculated scores
    
    Args:
        position_data: Dictionary of position data
        
    Returns:
        Dictionary with reordered positions
    """
    # Calculate scores and get ordered positions
    ordered_positions = calculate_position_scores(position_data)
    position_order = list(ordered_positions.keys())
    
    # Create new dictionary with reordered positions
    new_position_data = {}
    
    # First add "all notes" position
    if '0' in position_data:
        new_position_data['0'] = position_data['0']
        
    # Add other positions in score order
    for i, orig_position in enumerate(position_order, 1):
        new_position_data[str(i)] = position_data[str(orig_position)]
        
    return new_position_data


def get_scale_position_dict_improved(scale_name, root_note_id, root_pitch, tonal_root, selected_root_name):
    """
    Improved function to get position dictionary for scales/arpeggios
    Optimized version of get_scale_position_dict with better performance and readability
    
    Args:
        scale_name: Name of the scale/arpeggio
        root_note_id: ID of the root note
        root_pitch: Pitch of the root note
        tonal_root: Tonal root offset
        selected_root_name: Name of the selected root
        
    Returns:
        Dictionary with position data
    """
    # Get scale note data
    scale_note = Notes.objects.get(note_name=scale_name)
    
    # Get list of notes for this scale/arpeggio
    notes_list = get_note_list(scale_note, root_pitch, selected_root_name)
    
    # Initialize position dictionary
    position_dict = {}
    
    # Create "all notes" position (position 0)
    all_notes_position = {}
    for string in STRINGS:
        string_tones = []
        added_tones = set()
        
        # Add all tones for notes in this scale/arpeggio
        for note in notes_list:
            if note in STRING_NOTE_OPTIONS[string][0]:
                for tone in STRING_NOTE_OPTIONS[string][0][note][0]['tone']:
                    if tone not in added_tones:
                        string_tones.append(tone)
                        added_tones.add(tone)
                        
        # Create tone dictionary for this string
        all_notes_position[string] = [{'tones': string_tones}]
        
    # Add all notes position to the dictionary
    position_dict['0'] = all_notes_position
    
    # Get available positions for this scale/arpeggio
    available_positions = NotesPosition.objects.filter(notes_name_id=scale_note.id)
    
    # Create position data for each available position
    for position in available_positions:
        position_data = {}
        position_frets = get_position_data(position.id, root_pitch)
        
        for string in STRINGS:
            string_tones = []
            added_tones = set()
            
            # Check each note in the scale/arpeggio
            for note in notes_list:
                if note in STRING_NOTE_OPTIONS[string][0]:
                    # Check each potential fret position
                    for i, fret in enumerate(STRING_NOTE_OPTIONS[string][0][note][0]['fret']):
                        if fret in position_frets:
                            # This note is in this position on this string
                            tone = STRING_NOTE_OPTIONS[string][0][note][0]['tone'][i]
                            if tone not in added_tones:
                                string_tones.append(tone)
                                added_tones.add(tone)
                                
            # Create tone dictionary for this string in this position
            position_data[string] = [{'tones': string_tones}]
            
        # Add this position to the dictionary
        position_dict[str(position.position_order)] = position_data
        
    return position_dict


def process_scale_positions(scale_name, root_note_id, root_pitch, tonal_root, selected_root_name):
    """
    Process scale/arpeggio positions with transposition and reordering
    
    Args:
        scale_name: Name of the scale/arpeggio
        root_note_id: ID of the root note
        root_pitch: Pitch of the root note
        tonal_root: Tonal root offset
        selected_root_name: Name of the selected root
        
    Returns:
        Dictionary with processed position data
    """
    # Get initial position data
    position_data = get_scale_position_dict_improved(
        scale_name, root_note_id, root_pitch, tonal_root, selected_root_name
    )
    
    # Process position data if we have more than one position
    if len(position_data) > 1:
        # Get number of positions
        note = Notes.objects.get(note_name=scale_name)
        position_count = NotesPosition.objects.filter(notes_name__note_name=scale_name).count()
        
        # Find positions that can be transposed
        transposable_positions = find_transposable_positions(position_count, position_data)
        
        # Transpose positions
        position_data = transpose_positions(position_data, transposable_positions)
        
        # Reorder positions
        position_data = reorder_positions(position_data)
    
    # Add metadata
    position_data["name"] = scale_name
    position_data["root"] = get_root_note(root_pitch, tonal_root, root_note_id)
    
    return position_data


def get_root_note(root_pitch, tonal_root, root_id):
    """Import and call the original get_root_note function"""
    from .root_note_setup import get_root_note as original_get_root_note
    return original_get_root_note(root_pitch, tonal_root, root_id)
