from positionfinder.models import Notes
from positionfinder.positions import NotesPosition
from positionfinder.template_notes import NOTES, NOTES_SHARP, TENSIONS, INVERSIONS, SHARP_NOTES
from positionfinder.template_notes import STRING_NOTE_OPTIONS, STRINGS
from positionfinder.get_position import get_notes_position
import numpy
import json
import pprint

# Function for getting every transposable Positon
def get_transposable_positions(position_options, position):
    transposition_positions = []
    for i in range (0, position_options + 1):
        actual_position = position[str(i)]
        transposition = []
        for string in STRINGS:
            lowest_tone = actual_position[string][0]['tones'][0]
            actual_tones = actual_position[string][0]['tones']
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
        if not False in transposition:
            if i not in transposition_positions:
                transposition_positions.append(i)
    return transposition_positions

def get_scale_position_dict(scale_name, root_note_id, root_pitch, tonal_root, selected_root_name):

    scale_note = Notes.objects.get(note_name=scale_name)

    POSITION_DICT = {}

    SCALE_NOTES = [scale_note.first_note, scale_note.second_note,
                   scale_note.third_note, scale_note.fourth_note,
                   scale_note.fifth_note, scale_note.sixth_note,
                   scale_note.seventh_note, scale_note.eigth_note,
                   scale_note.ninth_note, scale_note.tenth_note,
                   scale_note.eleventh_note, scale_note.twelth_note]

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
    TONE_NOTE_OPTION_DICT = {}

    for key in STRING_NOTE_OPTIONS:
        TONE_DICT = []
        TENSION_DICT = []
        TONE_NOTE_OPTION_DICT = {}
        TENSION_OPTION_DICT = {}
        y = 0
        for x in NOTES_LIST:
            index = SCALE_NOTES[y]
            TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][0])
            TENSION_DICT.append(TENSIONS[index])
#            TENSION_OPTION_DICT['tensions'] = TENSION_DICT
            try:
                TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][1])
                TONE_NOTE_OPTION_DICT['tones'] = TONE_DICT
            except IndexError:
                k = False
            MULTIPLE_DICT = [ TONE_NOTE_OPTION_DICT ]
            y += 1
        STRING_NOTE_OPTION_STRING[key] = MULTIPLE_DICT
    POSITION_DICT['0'] = STRING_NOTE_OPTION_STRING

    # Loop through every available position
    for position in available_positions:
        STRING_NOTE_OPTION_STRING = {}
        for key in STRING_NOTE_OPTIONS:
            TONE_DICT = []
            TENSION_DICT = []
            TONE_NOTE_OPTION_DICT = {}
            TENSION_OPTION_DICT = {}
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
                    TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][0])
                    TONE_NOTE_OPTION_DICT['tones'] = TONE_DICT
                    TENSION_DICT.append(TENSIONS[index])
 #                   TENSION_OPTION_DICT['tensions'] = TENSION_DICT
                    MULTIPLE_DICT = [ TONE_NOTE_OPTION_DICT ]
                    y += 1
                    STRING_NOTE_OPTION_STRING[key] = MULTIPLE_DICT
                if check_position_two in position_loop_dict:
                    TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][1])
                    TONE_NOTE_OPTION_DICT['tones'] = TONE_DICT
                    TENSION_DICT.append(TENSIONS[index])
#                  TENSION_OPTION_DICT['tensions'] = TENSION_DICT
                    MULTIPLE_DICT = [ TONE_NOTE_OPTION_DICT ]
                    y += 1
                    STRING_NOTE_OPTION_STRING[key] = MULTIPLE_DICT
                POSITION_DICT[str(position.position_order)] = STRING_NOTE_OPTION_STRING
    return POSITION_DICT

def transpose_position(y):
    y_trans = []
    for x in y:
        base = x[:(len(x) -1)]
        z = x[-1]
        y_trans.append(str(base) + str((int(z) - 1)))

    y = y_trans
    return y

def transpose_actual_position(position, transposable_position):
    for x in transposable_position:
        for string in STRINGS:
            y = position[str(x)][string][0]['tones']
            y = transpose_position(y)
            position[str(x)][string][0]['tones'] = y
    return position

