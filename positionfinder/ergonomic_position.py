import copy
from .notes_choices import STRING_RANGE_CHOICES

STRING_CHOICES = {
    'eString': 1,
    'bString': 2,
    'gString': 3,
    'dString': 4,
    'AString': 5,
    'ELowString': 6,
    'lowBString': 7,
    'highAString': 8,
}

def calculate_stretch(position):
    fret_numbers = []
    string_numbers = []

    for string, note_info in position.items():
        note = note_info[0]
        fret_number = int(''.join(filter(str.isdigit, note)))
        fret_numbers.append(fret_number)
        string_numbers.append(STRING_CHOICES[string])

    fret_stretch = max(fret_numbers) - min(fret_numbers)
    string_stretch = max(string_numbers) - min(string_numbers)
    return fret_stretch + string_stretch

def find_alternative_string(string_name, fret_number):
    alternatives = {
        "eString": ["bString", "gString"],
        "bString": ["gString", "dString"],
        "gString": ["dString", "AString"],
        "dString": ["AString", "ELowString"],
        "AString": ["ELowString", "lowBString"],
        "ELowString": ["lowBString", "highAString"],
        "lowBString": ["highAString", "eString"],
        "highAString": ["eString", "bString"]
    }

    for alt_string in alternatives[string_name]:
        if 0 <= fret_number <= 17:  # Assuming the guitar has 17 frets
            return alt_string

    return None

def find_alternative_string_positions(position):
    new_position = copy.deepcopy(position)
    alternative_found = False

    for string, note_info in list(position.items()):
        note = note_info[0]
        fret_number = int(''.join(filter(str.isdigit, note)))
        alternative_string = find_alternative_string(string, fret_number)

        if alternative_string:
            new_position[alternative_string] = new_position.pop(string)
            alternative_found = True

    return new_position if alternative_found else None

def find_more_ergonomic_position(selected_position, chord_data, note_range):
    min_stretch = calculate_stretch(selected_position)
    best_position = selected_position

    for pos_name, pos_data in chord_data[note_range].items():
        for position in pos_data:
            current_stretch = calculate_stretch(position)
            if current_stretch < min_stretch:
                min_stretch = current_stretch
                best_position = position

    return best_position

def apply_ergonomic_adjustment(chord_data):
    note_range = chord_data['note_range']
    if note_range not in chord_data:
        raise KeyError(f"note_range '{note_range}' not found in chord_data")
    
    for pos_name, positions in chord_data[note_range].items():
        for i, position in enumerate(positions):
            ergonomic_position = find_more_ergonomic_position(position, chord_data, note_range)
            if ergonomic_position:
                chord_data[note_range][pos_name][i] = ergonomic_position
            alternative_position = find_alternative_string_positions(position)
            if alternative_position:
                alt_stretch = calculate_stretch(alternative_position)
                if alt_stretch < calculate_stretch(ergonomic_position):
                    chord_data[note_range][pos_name][i] = alternative_position

    return chord_data