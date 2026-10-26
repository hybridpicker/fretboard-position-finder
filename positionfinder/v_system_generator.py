"""
Ted Greene's V-System implementation for the fretboard position finder.
This module provides functions to generate chord voicings following Ted Greene's V-System taxonomy.
"""

from django.db import transaction

from .models_chords import ChordNotes, create_base_position


def _default_string_sets() -> dict:
    """Standard string combinations (bass to treble) for the V-System voicings."""
    # Each combination is a tuple of strings (from bass to treble)
    return {
        # 6-string sets
        "e-E": ("ELowString", "AString", "dString", "gString", "bString", "eString"),
        # 4-string sets (most common for common V-System voicings)
        "e-b": ("bString", "gString", "dString", "eString"),  # High strings
        "d-E": ("ELowString", "AString", "dString", "gString"),  # Low strings
        "g-A": ("AString", "dString", "gString", "bString"),  # Middle strings
        # Extended 7/8 string sets
        "highA-E": (
            "ELowString",
            "AString",
            "dString",
            "gString",
            "bString",
            "eString",
            "highAString",
        ),
        "e-lowB": (
            "lowBString",
            "ELowString",
            "AString",
            "dString",
            "gString",
            "bString",
            "eString",
        ),
        "highA-lowB": (
            "lowBString",
            "ELowString",
            "AString",
            "dString",
            "gString",
            "bString",
            "eString",
            "highAString",
        ),
    }


def _default_chord_types() -> dict:
    """Available chord types and their interval structures (semitones from root)."""
    return {
        # Seventh chords - primary focus for V-System
        "Major 7": [0, 4, 7, 11],  # Root, Major 3rd, Perfect 5th, Major 7th
        "Dominant 7": [0, 4, 7, 10],  # Root, Major 3rd, Perfect 5th, Minor 7th
        "Minor 7": [0, 3, 7, 10],  # Root, Minor 3rd, Perfect 5th, Minor 7th
        "Minor 7b5": [0, 3, 6, 10],  # Root, Minor 3rd, Diminished 5th, Minor 7th
        "MinMaj 7": [0, 3, 7, 11],  # Root, Minor 3rd, Perfect 5th, Major 7th
        # Additional seventh chord types
        "Major 7(#5)": [0, 4, 8, 11],  # Root, Major 3rd, Augmented 5th, Major 7th
        "Major 7(b5)": [0, 4, 6, 11],  # Root, Major 3rd, Diminished 5th, Major 7th
        "Dominant 7(#5)": [0, 4, 8, 10],  # Root, Major 3rd, Augmented 5th, Minor 7th
        "Dominant 7(b5)": [0, 4, 6, 10],  # Root, Major 3rd, Diminished 5th, Minor 7th
        # Triads (less important for V-System, but included for completeness)
        "Major": [0, 4, 7],  # Root, Major 3rd, Perfect 5th
        "Minor": [0, 3, 7],  # Root, Minor 3rd, Perfect 5th
        "Diminished": [0, 3, 6],  # Root, Minor 3rd, Diminished 5th
        "Augmented": [0, 4, 8],  # Root, Major 3rd, Augmented 5th
    }


class VoicingSystem:
    """Implementation of Ted Greene's V-System voicing classification."""

    def __init__(self, notes_category_id: int = 1) -> None:
        """Initialize V-System generator.

        Args:
            notes_category_id (int): Category ID for the chords (default: 1 for standard chords)
        """
        self.category_id = notes_category_id

        # Define standard string combinations for different V-System voicings
        self.string_sets = _default_string_sets()

        # Major 7 chord intervals from root (in semitones)
        self.maj7_intervals = [0, 4, 7, 11]  # Root, Major 3rd, Perfect 5th, Major 7th

        # Available chord types and their interval structures (from root)
        self.chord_types = _default_chord_types()

    def _create_voicing(
        self, type_name: str, root_note: int, chord_type: str, string_set_key: str, notes: list
    ) -> "ChordNotes | None":
        """Create the chord (3 or 4 notes) for a voicing and its base positions."""
        strings = self.string_sets[string_set_key]
        with transaction.atomic():
            # Check if using 8-string ranges - they have character length issues
            if "highA" in string_set_key or "lowB" in string_set_key:
                return None

            if len(notes) not in (3, 4):
                raise ValueError(f"Unsupported number of notes: {len(notes)}")

            fields = {}
            for index, name in enumerate(("first", "second", "third", "fourth")[: len(notes)]):
                fields[f"{name}_note"] = notes[index]
                fields[f"{name}_note_string"] = strings[index]

            chord = ChordNotes.objects.create(
                category_id=self.category_id,
                type_name=type_name,
                chord_name=chord_type,
                range=string_set_key,  # Use string set key as range name
                tonal_root=root_note,
                **fields,
            )

            try:
                # Skip 8-string range creation - set an attribute to prevent it
                chord.skip_eight_string = True

                # Create positions for the chord
                create_base_position(chord.id)

                return chord
            except Exception:
                # Try to continue even if position creation fails
                return chord

    def _validated_notes(self, root_note: int, chord_type: str, string_set_key: str) -> list:
        """Validate the request and return the absolute notes of the chord."""
        if chord_type not in self.chord_types:
            raise ValueError(f"Unsupported chord type: {chord_type}")

        if string_set_key not in self.string_sets:
            raise ValueError(f"Unsupported string set: {string_set_key}")

        # Calculate the absolute notes based on root and intervals
        notes = [(root_note + interval) % 12 for interval in self.chord_types[chord_type]]

        # Ensure we have the right number of strings
        strings = self.string_sets[string_set_key]
        if len(notes) > len(strings):
            raise ValueError(
                f"Not enough strings ({len(strings)}) for chord with {len(notes)} notes"
            )
        return notes

    def generate_v1_voicing(
        self, root_note: int, chord_type: str, string_set_key: str = "e-b"
    ) -> "ChordNotes | None":
        """Generate a V-1 (close position) voicing for a given chord.

        Args:
            root_note (int): Root note value (0-11, where 0=C, 1=C#, etc.)
            chord_type (str): Type of chord (e.g., "Major 7", "Dominant 7")
            string_set_key (str): Key for the string set to use (default: "e-b")

        Returns:
            ChordNotes: The created chord notes object
        """
        notes = self._validated_notes(root_note, chord_type, string_set_key)

        # For V-1 (close position), sort the notes to ensure ascending order
        sorted_notes = sorted(notes)

        return self._create_voicing("V1", root_note, chord_type, string_set_key, sorted_notes)

    def generate_v2_voicing(
        self, root_note: int, chord_type: str, string_set_key: str = "e-b"
    ) -> "ChordNotes | None":
        """Generate a V-2 voicing (drop-2) for a given chord.

        Args:
            root_note (int): Root note value (0-11, where 0=C, 1=C#, etc.)
            chord_type (str): Type of chord (e.g., "Major 7", "Dominant 7")
            string_set_key (str): Key for the string set to use (default: "e-b")

        Returns:
            ChordNotes: The created chord notes object
        """
        original_notes = self._validated_notes(root_note, chord_type, string_set_key)

        # For V-2 (drop-2), we arrange the notes in close position first
        # Then drop the second highest note down an octave
        drop2_notes = sorted(original_notes)

        if len(drop2_notes) in (3, 4):
            # The second highest note is at index 2 (seventh chord) or 1 (triad)
            drop_note = drop2_notes[2 if len(drop2_notes) == 4 else 1]
            drop2_notes.remove(drop_note)
            drop2_notes.insert(0, (drop_note - 12) % 12)  # Insert at beginning

        return self._create_voicing("V2", root_note, chord_type, string_set_key, drop2_notes)

    def generate_all_roots_v1(
        self, chord_type: str = "Major 7", string_set_key: str = "e-b"
    ) -> list:
        """Generate V-1 voicings for all root notes (0-11) of a given chord type."""
        chords = []
        for root_note in range(12):  # Only 12 chromatic roots
            chord = self.generate_v1_voicing(root_note, chord_type, string_set_key)
            chords.append(chord)
        return chords

    def generate_all_roots_v2(
        self, chord_type: str = "Major 7", string_set_key: str = "e-b"
    ) -> list:
        """Generate V-2 voicings for all root notes of a given chord type, covering C0 to D4."""
        chords = []
        for midi_note in range(12, 63):  # 12 to 62 inclusive
            root = midi_note % 12
            chord = self.generate_v2_voicing(root, chord_type, string_set_key)
            chords.append(chord)
        return chords

    def generate_all_types_v1(self, root_note: int = 0, string_set_key: str = "e-b") -> list:
        """Generate V-1 voicings for all chord types with a given root note.

        Args:
            root_note (int): Root note value (0-11, where 0=C, 1=C#, etc.)
            string_set_key (str): Key for the string set to use (default: "e-b")

        Returns:
            list: List of created ChordNotes objects
        """
        chords = []
        for chord_type in self.chord_types:
            chord = self.generate_v1_voicing(root_note, chord_type, string_set_key)
            chords.append(chord)
        return chords

    def generate_all_types_v2(self, root_note: int = 0, string_set_key: str = "e-b") -> list:
        """Generate V-2 voicings for all chord types with a given root note.

        Args:
            root_note (int): Root note value (0-11, where 0=C, 1=C#, etc.)
            string_set_key (str): Key for the string set to use (default: "e-b")

        Returns:
            list: List of created ChordNotes objects
        """
        chords = []
        for chord_type in self.chord_types:
            chord = self.generate_v2_voicing(root_note, chord_type, string_set_key)
            chords.append(chord)
        return chords
