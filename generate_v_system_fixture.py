import json
import os

# --- Configuration ---
MODEL_NAME = "positionfinder.chordnotes"
CATEGORY = 3
TONAL_ROOT_TO_GENERATE = 3  # 0:A, 1:A#, 2:B, 3:C, 4:C#, 5:D, 6:D#, 7:E, 8:F, 9:F#, 10:G, 11:G#
OUTPUT_FILENAME = "v3_v7_voicings.json"
OUTPUT_DIR = os.path.join("positionfinder", "fixtures")

# Chord definitions: [chord_ordering, name, interval_1, interval_2, interval_3, interval_4]
CHORD_TYPES = [
    [1, "Major 7", 0, 4, 7, 11],
    [2, "Dominant 7", 0, 4, 7, 10],
    [3, "Minor 7", 0, 3, 7, 10],
    [4, "Minor 7b5", 0, 3, 6, 10],
    [5, "Diminished 7", 0, 3, 6, 9],
]

# V-System string sets for 8-string (F# B E A D G B E)
# Format: [V-GroupName, lowest_string_name, string_2, string_3, highest_string_name]
V_SYSTEM_STRINGS = [
    ["V3", "DString", "GString", "BString", "eString"],
    ["V4", "AString", "DString", "GString", "BString"],
    ["V5", "ELowString", "AString", "DString", "GString"],
    ["V6", "BLowString", "ELowString", "AString", "DString"],
    ["V7", "FSharpLowString", "BLowString", "ELowString", "AString"],
    # V8-V14 would be defined here if needed
]


def generate_fixture_data():
    """Generates the fixture data for V-System chords."""
    fixture_data = []
    root = TONAL_ROOT_TO_GENERATE

    for v_group_name, s1, s2, s3, s4 in V_SYSTEM_STRINGS:
        lowest_string = s1
        highest_string = s4
        # Adjust range string format slightly for clarity
        range_str = f"{highest_string.replace('String', '')} - {lowest_string.replace('String', '')}"

        for chord_order, chord_name, i1, i2, i3, i4 in CHORD_TYPES:
            fields = {
                "category": CATEGORY,
                "ordering": None,
                "type_name": v_group_name,
                "chord_name": chord_name,
                "chord_ordering": chord_order,
                "range": range_str,
                "range_ordering": None,
                "tonal_root": root,
                "first_note": i1, # Assuming lowest pitch note is interval 1 on lowest string
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
    print("Generating V-System chord fixture data...")
    generated_data = generate_fixture_data()
    write_json_file(generated_data, OUTPUT_DIR, OUTPUT_FILENAME)
    print(f"Generated {len(generated_data)} chord entries for root C (tonal_root={TONAL_ROOT_TO_GENERATE}).")
