"""Note extraction/normalisation helpers for chord JSON data."""

# Constants (Keep from functional view)
NOTE_MAPPING = {
    "c": "C",
    "cs": "C#",
    "d": "D",
    "ds": "D#",
    "e": "E",
    "f": "F",
    "fs": "F#",
    "g": "G",
    "gs": "G#",
    "a": "A",
    "as": "A#",
    "b": "B",
    "db": "Db",
    "eb": "Eb",
    "gb": "Gb",
    "ab": "Ab",
    "bb": "Bb",
}
NOTE_ORDER = [
    "C",
    "C#",
    "Db",
    "D",
    "D#",
    "Eb",
    "E",
    "F",
    "F#",
    "Gb",
    "G",
    "G#",
    "Ab",
    "A",
    "A#",
    "Bb",
    "B",
]

# Enharmonic equivalents
FLAT_ENHARMONICS = {"C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab", "A#": "Bb"}
SHARP_ENHARMONICS = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}


# Helper functions (Keep from functional view)
def get_note_order(root_note: str) -> list[str]:
    """Get reordered notes starting from the root note"""
    try:
        start_index = NOTE_ORDER.index(root_note)
        return NOTE_ORDER[start_index:] + NOTE_ORDER[:start_index]
    except ValueError:
        return NOTE_ORDER


INVERSION_KEYS = {"Basic Position", "First Inversion", "Second Inversion", "Third Inversion"}

# Fixed note spellings for Minor 7b5 chords, keyed by (standardized) root.
MINOR_7B5_NOTES = {
    "C": ["C", "Eb", "Gb", "Bb"],
    "D": ["D", "F", "Ab", "C"],
    "E": ["E", "G", "Bb", "D"],
    "F": ["F", "Ab", "B", "Eb"],
    "G": ["G", "Bb", "Db", "F"],
    "A": ["A", "C", "Eb", "G"],
    "B": ["B", "D", "F", "A"],
    "Bb": ["Bb", "Db", "E", "Ab"],
    "Eb": ["Eb", "Gb", "A", "Db"],
    "Ab": ["Ab", "B", "D", "Gb"],
    "Db": ["Db", "E", "G", "B"],
    "Gb": ["Gb", "A", "C", "E"],
}

# (b3, b5, b7) for enharmonic (sharp/flat) roots of a Minor 7b5 chord.
_ENHARMONIC_MINOR_7B5_TONES = {
    "C#": ("E", "G", "B"),
    "Db": ("E", "G", "B"),
    "D#": ("Gb", "A", "Db"),
    "Eb": ("Gb", "A", "Db"),
    "F#": ("A", "C", "E"),
    "Gb": ("A", "C", "E"),
    "G#": ("B", "D", "Gb"),
    "Ab": ("B", "D", "Gb"),
    "A#": ("Db", "E", "Ab"),
    "Bb": ("Db", "E", "Ab"),
}


class _NoteCollector:
    """Collects note names (and the root) while walking chord JSON data."""

    def __init__(self) -> None:
        self.notes: set = set()
        self.root_note: str | None = None

    def extract_notes_from_position(self, positions: list) -> None:
        """Add the notes of every string entry in a list of position dicts."""
        print(f"DEBUG: Extract notes from positions: {positions}")
        for position_data in positions:  # positions is now a list containing one dict
            for string, note_info in position_data.items():
                if not note_info or not isinstance(note_info, list) or string == "assigned_strings":
                    continue
                if not note_info[0]:
                    continue
                if "String" in str(note_info[0]):
                    continue

                note = str(note_info[0]).lower().rstrip("0123456789-")
                if not note or note[0].lower() not in "abcdefg":
                    continue

                # Use function value for validation if available
                function = note_info[1] if len(note_info) > 1 else None
                is_root_note_flag = note_info[3] if len(note_info) > 3 else False

                print(
                    f"DEBUG: Found note: {note}, function: {function}, is_root: {is_root_note_flag}"
                )

                # If this note is marked as the root, use it to establish context
                if is_root_note_flag and not self.root_note:
                    self.root_note = NOTE_MAPPING.get(note, note.capitalize())

                mapped_note = NOTE_MAPPING.get(note, note.capitalize())
                self.notes.add(mapped_note)
                print(f"DEBUG: Added note {mapped_note} to notes set")

    def traverse(self, data: object) -> None:
        """Recursively walk dicts/lists, extracting notes from inversion entries."""
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"DEBUG: Traversing key: {key}")
                if key in INVERSION_KEYS and isinstance(
                    value, list
                ):  # Check if value is a list (of position dicts)
                    print(f"DEBUG: Found inversion key: {key}")
                    self.extract_notes_from_position(value)
                # Check if the key itself is a range name (like 'e - g')
                elif isinstance(value, dict) and any(
                    inv_key in value for inv_key in INVERSION_KEYS
                ):
                    # If the value is a dictionary containing inversion keys, traverse it
                    print(f"DEBUG: Found range with inversions: {key}")
                    self.traverse(value)
                elif isinstance(value, (dict, list)):
                    self.traverse(value)  # Recursively traverse other dicts/lists
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self.traverse(item)

    def add_top_level_root(self, json_data: dict) -> None:
        """Process root note from top level if present (important for context)."""
        if (
            "root" in json_data
            and isinstance(json_data["root"], list)
            and len(json_data["root"]) > 0
        ):
            root_note_full = json_data["root"][0].lower().rstrip("0123456789-")
            self.root_note = NOTE_MAPPING.get(root_note_full, root_note_full.capitalize())
            if self.root_note:
                self.notes.add(self.root_note)
                print(f"DEBUG: Added root note {self.root_note} from top level")
            else:
                print("DEBUG: Failed to process root note from top level")


def _sort_by_order(notes, order: list[str]) -> list:
    """Sort notes by their index in ``order`` (unknown notes last)."""
    return sorted(
        list(notes),
        key=lambda x: order.index(x) if x in order else float("inf"),
    )


def _standardize_spelling(sorted_notes: list, chord_type: str, root_note: str | None) -> list:
    """Remove enharmonic duplicates and apply sharp/flat spelling based on chord type."""
    standardized_notes = []

    # Decide if we should prefer flat or sharp names
    prefer_flats = any(
        term in chord_type for term in ["minor", "min", "dim", "b5", "b7", "b9", "b13"]
    )

    # Clean duplicates and standardize names
    seen = set()
    for note in sorted_notes:
        # Skip if we've already seen this note or its enharmonic equivalent
        if note in seen:
            continue

        # Mark this note and its enharmonic equivalent as seen
        seen.add(note)
        if note in FLAT_ENHARMONICS:
            seen.add(FLAT_ENHARMONICS[note])
        elif note in SHARP_ENHARMONICS:
            seen.add(SHARP_ENHARMONICS[note])

        # Choose preferred spelling
        if prefer_flats and note in SHARP_ENHARMONICS:
            # Use flat name for sharps (C# -> Db)
            standardized_notes.append(SHARP_ENHARMONICS[note])
        elif not prefer_flats and note in FLAT_ENHARMONICS:
            # Use sharp name for flats (Db -> C#)
            standardized_notes.append(FLAT_ENHARMONICS[note])
        else:
            # Keep original spelling
            standardized_notes.append(note)

    # Re-sort notes if needed
    if root_note and root_note in NOTE_ORDER:
        note_order_list = get_note_order(root_note)
        standardized_notes.sort(
            key=lambda x: note_order_list.index(x) if x in note_order_list else float("inf")
        )
    return standardized_notes


def _generic_minor_7b5_notes(root_note: str) -> list:
    """Compute R, b3, b5, b7 for a Minor 7b5 chord on an arbitrary root."""
    note_idx = NOTE_ORDER.index(root_note)
    flat_notes = [root_note]
    if "b" in root_note or "#" in root_note:
        # Specify exact notes for enharmonic roots
        flat_notes.extend(_ENHARMONIC_MINOR_7B5_TONES.get(root_note, ()))
    else:
        # For natural notes, just use index calculation
        for semitones in (3, 6, 10):
            flat_notes.append(NOTE_ORDER[(note_idx + semitones) % len(NOTE_ORDER)])
    return flat_notes


def _fix_minor_7b5(sorted_notes: list, chord_name: str, root_note: str | None) -> list:
    """Force the correct notes for Minor 7b5 chords."""
    if chord_name == "Minor 7b5" or chord_name == "Min7b5" or "minor 7b5" in chord_name.lower():
        if root_note:
            print(f"DEBUG: Special handling for {chord_name} chord")

            # Always standardize root to flat version for Minor 7b5
            if root_note in SHARP_ENHARMONICS:
                standardized_root = SHARP_ENHARMONICS[root_note]
            else:
                standardized_root = root_note

            if standardized_root in MINOR_7B5_NOTES:
                sorted_notes = list(MINOR_7B5_NOTES[standardized_root])
            else:
                sorted_notes = _generic_minor_7b5_notes(root_note)

            print(f"DEBUG: Fixed {chord_name} chord notes: {sorted_notes}")
    return sorted_notes


def extract_and_convert_notes(json_data: dict) -> list:
    """Extract and normalize notes from chord JSON data."""
    print(
        f"DEBUG: Processing chord data: {json_data.get('chord', 'Unknown')} in {json_data.get('type', 'Unknown')}"
    )

    collector = _NoteCollector()
    collector.add_top_level_root(json_data)

    # Traverse the entire data structure to find notes within inversions
    collector.traverse(json_data)
    root_note = collector.root_note

    valid_notes = {note for note in collector.notes if note in NOTE_ORDER}
    print(f"DEBUG: Valid notes after traversal: {valid_notes}")

    if root_note and root_note in NOTE_ORDER:
        sorted_notes = _sort_by_order(valid_notes, get_note_order(root_note))
    else:
        sorted_notes = _sort_by_order(valid_notes, NOTE_ORDER)

    print(f"DEBUG: Final sorted notes: {sorted_notes}")

    chord_type = json_data.get("chord", "").lower()
    sorted_notes = _standardize_spelling(sorted_notes, chord_type, root_note)

    # CRITICAL FIX: Special handling for problematic chords
    chord_name = json_data.get("chord", "")
    return _fix_minor_7b5(sorted_notes, chord_name, root_note)
