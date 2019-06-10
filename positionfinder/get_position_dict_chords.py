from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.template_notes import NOTES, NOTES_SHARP, TENSIONS, INVERSIONS, SHARP_NOTES
from positionfinder.template_notes import STRING_NOTE_OPTIONS
import numpy

def get_position_dict(chord_inversion, chord_note_id, root_pitch, tonal_root, selected_root_name):
    x = INVERSIONS.index(chord_inversion)

    chord_note = ChordNotes.objects.get(id=chord_note_id)
    chord_notes_position = ChordPosition.objects.filter(notes_name_id=chord_note_id)

    INVERSION_DICT = {}
    POSITION_DICT = {}

    CHORD_NOTES = [chord_note.first_note, chord_note.second_note,
                   chord_note.third_note, chord_note.fourth_note,
                   chord_note.fifth_note, chord_note.sixth_note]

    CHORD_NOTES_STRING = [chord_note.first_note_string, chord_note.second_note_string,
                          chord_note.third_note_string, chord_note.fourth_note_string,
                          chord_note.fifth_note_string, chord_note.sixth_note_string]

    CHORD_NOTES_POSITION = [chord_notes_position[x].first_note, chord_notes_position[x].second_note,
                           chord_notes_position[x].third_note, chord_notes_position[x].fourth_note,
                           chord_notes_position[x].fifth_note, chord_notes_position[x].sixth_note]


    index = 0

    tonal_root = tonal_root + root_pitch

    fret_distance = []
    for y in CHORD_NOTES:
        if y is not None:
            chord_note_index = y + root_pitch + CHORD_NOTES_POSITION[index]
            if chord_note_index >= 12:
                chord_note_index = chord_note_index - 12
            if tonal_root in SHARP_NOTES or '#' in selected_root_name:
                chord_note_name = NOTES_SHARP[chord_note_index]
            else:
                chord_note_name = NOTES[chord_note_index]
            chord_note_string = CHORD_NOTES_STRING[index]
            chord_note_fret = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["fret"][0]
            fret_distance.append(chord_note_fret)
            index += 1

    v = numpy.diff(fret_distance)
    v = [abs(x) for x in v]

    index = 0
    if any(abs(element) >= 6 for element in v):
        for y in CHORD_NOTES:
            if y is not None:
                chord_note_index = y + root_pitch + CHORD_NOTES_POSITION[index]
                if chord_note_index >= 12:
                    chord_note_index = chord_note_index - 12
                if tonal_root in SHARP_NOTES or '#' in selected_root_name:
                    chord_note_name = NOTES_SHARP[chord_note_index]
                    print(chord_note_name)
                else:
                    chord_note_name = NOTES[chord_note_index]
                chord_note_string = CHORD_NOTES_STRING[index]
                try :
                    chord_note_name = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["tone"][1]
                except IndexError:
                    chord_note_name = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["tone"][0]
                chord_note_tension_index = y + CHORD_NOTES_POSITION[index]
                if chord_note_tension_index >= 12:
                    chord_note_tension_index = chord_note_tension_index - 12
                chord_note_tension = TENSIONS[chord_note_tension_index]
                POSITION_DICT[chord_note_string] = [chord_note_name, chord_note_tension]
                index += 1

        return POSITION_DICT

    else:
        for y in CHORD_NOTES:
            if y is not None:
                chord_note_index = y + root_pitch + CHORD_NOTES_POSITION[index]
                if chord_note_index >= 12:
                    chord_note_index = chord_note_index - 12
                if tonal_root in SHARP_NOTES or '#' in selected_root_name:
                    chord_note_name = NOTES_SHARP[chord_note_index]
                    print(chord_note_name)
                else:
                    chord_note_name = NOTES[chord_note_index]
                chord_note_string = CHORD_NOTES_STRING[index]
                chord_note_name = STRING_NOTE_OPTIONS[chord_note_string][0][chord_note_name][0]["tone"][0]
                chord_note_tension_index = y + CHORD_NOTES_POSITION[index]
                if chord_note_tension_index >= 12:
                    chord_note_tension_index = chord_note_tension_index - 12
                chord_note_tension = TENSIONS[chord_note_tension_index]
                POSITION_DICT[chord_note_string] = [chord_note_name, chord_note_tension]
                index += 1

        return POSITION_DICT
