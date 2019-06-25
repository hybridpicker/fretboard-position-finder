from positionfinder.models import Notes
from positionfinder.positions import NotesPosition
from positionfinder.template_notes import NOTES, NOTES_SHARP, TENSIONS, INVERSIONS, SHARP_NOTES
from positionfinder.template_notes import STRING_NOTE_OPTIONS
from positionfinder.get_position import get_notes_position
import numpy
import json

def get_scale_position_dict(scale_name, root_note_id, root_pitch, tonal_root, selected_root_name):

    scale_note = Notes.objects.get(note_name=scale_name)
    scale_notes_position = NotesPosition.objects.filter(notes_name_id=scale_note.id)

    INVERSION_DICT = {}
    POSITION_DICT = {}

    SCALE_NOTES = [scale_note.first_note, scale_note.second_note,
                   scale_note.third_note, scale_note.fourth_note,
                   scale_note.fifth_note, scale_note.sixth_note]

    NOTES_LIST = []
    for x in SCALE_NOTES:
        if x is not None:
            NOTES_LIST.append(NOTES[x])

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
            TONE_NOTE_OPTION_DICT['tones'] = TONE_DICT
            TENSION_DICT.append(TENSIONS[index])
            TENSION_OPTION_DICT['tensions'] = TENSION_DICT
            MULTIPLE_DICT = [ TONE_NOTE_OPTION_DICT, TENSION_OPTION_DICT ]
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
                position_loop_dict = get_notes_position(position.id, root_note_id)
                check_position_one = STRING_NOTE_OPTIONS[key][0][x][0]['fret'][0]
                try:
                    check_position_two = STRING_NOTE_OPTIONS[key][0][x][0]['fret'][1]
                except IndexError:
                    check_position_two = False
                if check_position_one in position_loop_dict:
                    TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][0])
                    TONE_NOTE_OPTION_DICT['tones'] = TONE_DICT
                    TENSION_DICT.append(TENSIONS[index])
                    TENSION_OPTION_DICT['tensions'] = TENSION_DICT
                    MULTIPLE_DICT = [ TONE_NOTE_OPTION_DICT, TENSION_OPTION_DICT ]
                    y += 1
                    STRING_NOTE_OPTION_STRING[key] = MULTIPLE_DICT
                if check_position_two in position_loop_dict:
                    TONE_DICT.append(STRING_NOTE_OPTIONS[key][0][x][0]['tone'][1])
                    TONE_NOTE_OPTION_DICT['tones'] = TONE_DICT
                    TENSION_DICT.append(TENSIONS[index])
                    TENSION_OPTION_DICT['tensions'] = TENSION_DICT
                    MULTIPLE_DICT = [ TONE_NOTE_OPTION_DICT, TENSION_OPTION_DICT ]
                    y += 1
                    STRING_NOTE_OPTION_STRING[key] = MULTIPLE_DICT
                POSITION_DICT[str(position.position_order)] = STRING_NOTE_OPTION_STRING
    return POSITION_DICT
