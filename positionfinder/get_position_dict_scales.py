from positionfinder.models import Notes
from positionfinder.positions import NotesPosition
from positionfinder.template_notes import NOTES, NOTES_SHARP, TENSIONS, SHARP_NOTES
from positionfinder.template_notes import STRING_NOTE_OPTIONS, STRINGS, NOTES_SCORE
from positionfinder.get_position import get_notes_position
import json
from collections import OrderedDict

# Function for getting every transposable Position
def get_transposable_positions(position_options, position):
    transposition_positions = []
    for i in range(1, position_options):
        key = str(i)
        if key not in position:
            continue
        actual_position = position[key]
        transposition = []
        for string in STRINGS:
            try:
                if 'tones' in actual_position[string][0] and actual_position[string][0]['tones']:
                    lowest_tone = actual_position[string][0]['tones'][0]
                else:
                    continue  # Skip this string if there are no tones
                if 'tones' in actual_position[string][0] and actual_position[string][0]['tones']:
                    actual_tones = actual_position[string][0]['tones']
                else:
                    continue  # Skip this string if there are no tones
                for tone in actual_tones:
                    # Delete Range
                    x = tone[:-1]
                    base_note = x
                    # Check if every base_note is available in a lower position
                    pitch = int(tone[-1]) - 1
                    lower_tone = base_note + str(pitch)
                    if lower_tone in STRING_NOTE_OPTIONS[string][0][base_note][0]['tone']:
                        transposition.append(True)
                    else:
                        transposition.append(False)
            except KeyError:
                pass
        if not False in transposition:
            if i not in transposition_positions:
                transposition_positions.append(i)
    return transposition_positions

# Add a helper to extract tones from a Notes object
def get_tones_from_notes(notes_obj):
    note_fields = [
        'first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note',
        'sixth_note', 'seventh_note', 'eigth_note', 'ninth_note', 'tenth_note',
        'eleventh_note', 'twelth_note'
    ]
    return [getattr(notes_obj, f) for f in note_fields if getattr(notes_obj, f) is not None]

def get_scale_position_dict(scale_name, root_note_id, root_pitch, tonal_root, selected_root_name):
    # Retrieve scale and build base note list
    try:
        # First try to get the scale by ID (for arpeggios/scales selected from the search)
        # Try to convert scale_name to an integer if it's a numeric string (likely an ID)
        scale_id = None
        try:
            if isinstance(scale_name, str) and scale_name.isdigit():
                scale_id = int(scale_name)
        except (ValueError, TypeError):
            pass
        
        if scale_id:
            scale_note = Notes.objects.get(id=scale_id)
        else:
            # Try by exact name if not found by ID
            scale_note = Notes.objects.get(note_name=scale_name)
    except Notes.DoesNotExist:
        # If exact match fails, try case-insensitive contains match
        matching_notes = Notes.objects.filter(note_name__icontains=scale_name)
        if not matching_notes.exists():
            # If still not found, try just the last part of the name (e.g., "Minor Triad" from "A Minor Triad")
            parts = scale_name.split()
            if len(parts) > 1:
                # Try with the latter part(s) of the name
                search_term = ' '.join(parts[1:])
                matching_notes = Notes.objects.filter(note_name__icontains=search_term)
        
        if matching_notes.exists():
            scale_note = matching_notes.first()
        else:
            raise Notes.DoesNotExist(f"Cannot find Notes with name: {scale_name}")
    
    SCALE_NOTES = get_tones_from_notes(scale_note)
    NOTES_LIST = []
    for interval in SCALE_NOTES:
        if interval is None:
            continue
        step = (interval + root_pitch) % 12
        NOTES_LIST.append(NOTES_SHARP[step] if root_pitch in SHARP_NOTES or '#' in selected_root_name else NOTES[step])
    # Fetch available positions
    available_positions = NotesPosition.objects.filter(notes_name_id=scale_note.id)
    POSITION_DICT = {}
    # Position '0': open strings
    base_dict = {}
    for string in STRING_NOTE_OPTIONS:
        cell = STRING_NOTE_OPTIONS[string][0]
        tones = []
        for note in NOTES_LIST:
            info = cell.get(note, [{}])[0]
            for tone in info.get('tone', []):
                if tone not in tones:
                    tones.append(tone)
        base_dict[string] = [{'tones': tones}]
    POSITION_DICT['0'] = base_dict
    # Fretted positions
    for pos in available_positions:
        fretted = {}
        pos_list = get_notes_position(pos.id, root_pitch)
        for string in STRING_NOTE_OPTIONS:
            cell = STRING_NOTE_OPTIONS[string][0]
            tones = []
            for note in NOTES_LIST:
                info = cell.get(note, [{}])[0]
                frets = info.get('fret', [])
                tone_opts = info.get('tone', [])
                for idx, fret in enumerate(frets):
                    if idx < len(tone_opts) and fret in pos_list:
                        tone = tone_opts[idx]
                        if tone not in tones:
                            tones.append(tone)
            fretted[string] = [{'tones': tones}]
        POSITION_DICT[str(pos.position_order)] = fretted
    return POSITION_DICT

def transpose_position(y):
    y_trans = []
    for x in y:
        base = x[:(len(x) - 1)]
        z = x[-1]
        y_trans.append(str(base) + str((int(z) - 1)))
    return y_trans

def transpose_actual_position(position, transposable_position):
    for x in transposable_position:
        for string in STRINGS:
            if 'tones' in position[str(x)][string][0]:
                y = position[str(x)][string][0]['tones']
                y = transpose_position(y)
                position[str(x)][string][0]['tones'] = y
            else:
                # Skip this string if there are no tones
                continue
    return position

def ordering_positions(position):
    score_board = {}
    for i in range(1, len(position)):
        score_list = []
        # Check if 'tones' key exists and is not empty
        if 'eString' in position[str(i)] and position[str(i)]['eString'] and 'tones' in position[str(i)]['eString'][0]:
            tones = position[str(i)]['eString'][0]['tones']
            for pos in tones:
                # Make sure the position is valid
                if pos and len(pos) > 1:
                    try:
                        score = NOTES_SCORE[pos[0]] + (int(pos[-1]) * 12)
                        score_list.append(score)
                    except (KeyError, ValueError):
                        # Skip this position if we can't calculate a score
                        pass
        
        if score_list:  # Only calculate if we have scores
            score_board[i] = sum(score_list) / len(score_list)
        else:
            score_board[i] = 0  # Default score for empty positions
    
    if not score_board:  # If there are no positions to order, return empty OrderedDict
        return OrderedDict()
        
    ordered_score = OrderedDict(sorted(score_board.items(), key=lambda t: t[1]))
    return ordered_score

def re_ordering_positions(position):
    new_order = ordering_positions(position)
    re_order_list = list(new_order.keys())
    new_position = {}
    for i, ordering in enumerate(re_order_list, 1):
        new_position[str(i)] = position[str(ordering)]
    new_position['0'] = position['0']
    return new_position
