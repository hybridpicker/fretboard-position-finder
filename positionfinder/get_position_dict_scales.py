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
        actual_position = position[str(i)]
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
    scale_note = Notes.objects.get(note_name=scale_name)

    POSITION_DICT = {}

    # Use the helper to extract scale notes
    SCALE_NOTES = get_tones_from_notes(scale_note)

    NOTES_LIST = []
    for x in SCALE_NOTES:
        if x is not None:
            y = x + root_pitch
            if y >= 12:
                y -= 12
            if root_pitch in SHARP_NOTES or '#' in selected_root_name:
                NOTES_LIST.append(NOTES_SHARP[y])
            else:
                NOTES_LIST.append(NOTES[y])

    available_positions = NotesPosition.objects.filter(notes_name_id=scale_note.id)
    
    # First Create All_Notes_Position
    STRING_NOTE_OPTION_STRING = {}
    for key in STRING_NOTE_OPTIONS:
        TONE_DICT = []
        TONE_NOTE_OPTION_DICT = {}
        added_tones = set()
        y = 0
        for x in NOTES_LIST:
            index = SCALE_NOTES[y]
            if STRING_NOTE_OPTIONS[key][0][x][0]['tone'][0] not in added_tones:
                TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][0])
                added_tones.add(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][0])
            if len(STRING_NOTE_OPTIONS[key][0][x][0]['tone']) > 1 and STRING_NOTE_OPTIONS[key][0][x][0]['tone'][1] not in added_tones:
                TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][1])
                added_tones.add(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][1])
            TONE_NOTE_OPTION_DICT['tones'] = TONE_DICT
            y += 1
        STRING_NOTE_OPTION_STRING[key] = [TONE_NOTE_OPTION_DICT]
    POSITION_DICT['0'] = STRING_NOTE_OPTION_STRING

    # Loop through every available position
    for position in available_positions:
        STRING_NOTE_OPTION_STRING = {}
        for key in STRING_NOTE_OPTIONS:
            TONE_DICT = []
            TONE_NOTE_OPTION_DICT = {}
            added_tones = set()
            y = 0
            for x in NOTES_LIST:
                index = SCALE_NOTES[y]
                position_loop_dict = get_notes_position(position.id, root_pitch)
                check_position_one = STRING_NOTE_OPTIONS[key][0][x][0]['fret'][0]
                try:
                    check_position_two = STRING_NOTE_OPTIONS[key][0][x][0]['fret'][1]
                except IndexError:
                    check_position_two = False
                if check_position_one in position_loop_dict:
                    if STRING_NOTE_OPTIONS[key][0][x][0]['tone'][0] not in added_tones:
                        TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][0])
                        added_tones.add(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][0])
                    TONE_NOTE_OPTION_DICT['tones'] = TONE_DICT
                    y += 1
                if check_position_two in position_loop_dict:
                    if len(STRING_NOTE_OPTIONS[key][0][x][0]['tone']) > 1 and STRING_NOTE_OPTIONS[key][0][x][0]['tone'][1] not in added_tones:
                        TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][1])
                        added_tones.add(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][1])
                    TONE_NOTE_OPTION_DICT['tones'] = TONE_DICT
                    y += 1
                STRING_NOTE_OPTION_STRING[key] = [TONE_NOTE_OPTION_DICT]
            POSITION_DICT[str(position.position_order)] = STRING_NOTE_OPTION_STRING
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
