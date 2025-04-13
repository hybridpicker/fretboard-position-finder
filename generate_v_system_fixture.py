import json
import os

# --- Configuration ---
MODEL_NAME = "positionfinder.chordnotes"
CATEGORY = 3
OUTPUT_FILENAME = "v3_v5_voicings_all_roots_corrected.json" # Corrected V3-V5 only
OUTPUT_DIR = os.path.join("positionfinder", "fixtures")

# Chord definitions: [chord_ordering, name, interval_1, interval_2, interval_3, interval_4]
CHORD_TYPES = [
    [1, "Major 7", 0, 4, 7, 11],
    [2, "Dominant 7", 0, 4, 7, 10],
    [3, "Minor 7", 0, 3, 7, 10],
    [4, "Minor 7b5", 0, 3, 6, 10],
    [5, "Diminished 7", 0, 3, 6, 9],
]

# User's String Names and assumed Pitch Order (0=lowest, 7=highest)
STRING_PITCH_ORDER = {
    "lowB": 0, "E": 1, "A": 2, "D": 3, "g": 4, "b": 5, "e": 6, "highA": 7
}

# Corrected V-System string sets for 8-string based on user names & adjacency
# Format: [V-GroupName, string_on_lowest_pitch_fret, string_2, string_3, string_on_highest_pitch_fret]
# Intervals (i1, i2, i3, i4) are assigned sequentially to s1, s2, s3, s4
V_SYSTEM_STRINGS = [
    # V1, V2 omitted for now
    ["V3", "A", "D", "g", "b"],       # Strings 6,5,4,3
    ["V4", "E", "A", "D", "g"],       # Strings 7,6,5,4
    ["V5", "lowB", "E", "A", "D"],    # Strings 8,7,6,5
    # V6-V14 require specific skipped-string definitions from user
]


def get_range_string(string_set):
    """Calculates the range string based on actual min/max pitch."""
    min_pitch = float('inf')
    max_pitch = float('-inf')
    min_pitch_name = ""
    max_pitch_name = ""

    for s_name in string_set:
        pitch_val = STRING_PITCH_ORDER.get(s_name, -1) # Find pitch value
        if pitch_val != -1:
            if pitch_val < min_pitch:
                min_pitch = pitch_val
                min_pitch_name = s_name
            if pitch_val > max_pitch:
                max_pitch = pitch_val
                max_pitch_name = s_name

    if min_pitch_name and max_pitch_name:
        return f"{max_pitch_name} - {min_pitch_name}"
    else:
        return "Error - Unknown String"

def generate_fixture_data():
    """Generates the fixture data for V-System chords (Corrected V3-V5) for all 12 roots.""" # Updated docstring
    fixture_data = []

    # Loop through all 12 tonal roots
    for root in range(12):
        for v_group_name, s1, s2, s3, s4 in V_SYSTEM_STRINGS:
            # Calculate range based on the actual highest/lowest pitch strings in the set
            current_string_set = [s1, s2, s3, s4]
            range_str = get_range_string(current_string_set)

            for chord_order, chord_name, i1, i2, i3, i4 in CHORD_TYPES:
                fields = {
                    "category": CATEGORY,
                    "ordering": None,
                    "type_name": v_group_name,
                    "chord_name": chord_name,
                    "chord_ordering": chord_order,
                    "range": range_str, # Use correctly calculated range
                    "range_ordering": None,
                    "tonal_root": root,
                    "first_note": i1, # Assigning intervals in ascending order to strings as listed
                    "first_note_string": s1,
                    "second_note": i2,
                    "second_note_string": s2,
                    "third_note": i3,
                    "third_note_string": s3,
                    "fourth_note": i4,
                    "fourth_note_string": s4,
                    "fifth_note": None,
                    "fifth_note_string": None,
                    "sixth_note": None,
                    "sixth_note_string": None
                }

                chord_entry = {
                    "model": MODEL_NAME,
                    "pk": None,
                    "fields": fields
                }
                fixture_data.append(chord_entry)

    return fixture_data

def write_json_file(data, directory, filename):
    """Writes the data to a JSON file."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2) # Use indent for readability
        print(f"Successfully generated fixture file: {filepath}")
    except IOError as e:
        print(f"Error writing file {filepath}: {e}")

if __name__ == "__main__":
    print("Generating V-System chord fixture data (Corrected V3-V5 strings/range) for all roots...") # Updated print message
    generated_data = generate_fixture_data()
    write_json_file(generated_data, OUTPUT_DIR, OUTPUT_FILENAME)
    print(f"Generated {len(generated_data)} chord entries for V3-V5 (corrected) across all 12 roots.") # Updated print message
