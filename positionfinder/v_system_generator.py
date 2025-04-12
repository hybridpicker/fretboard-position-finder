"""
Ted Greene's V-System implementation for the fretboard position finder.
This module provides functions to generate chord voicings following Ted Greene's V-System taxonomy.
"""
from django.db import transaction
from .models_chords import ChordNotes, ChordPosition, create_base_position
from .notes_choices import NOTES_CHOICES

class VoicingSystem:
    """Implementation of Ted Greene's V-System voicing classification."""
    
    def __init__(self, notes_category_id=1):
        """Initialize V-System generator.
        
        Args:
            notes_category_id (int): Category ID for the chords (default: 1 for standard chords)
        """
        self.category_id = notes_category_id
        
        # Define standard string combinations for different V-System voicings
        # Each combination is a tuple of strings (from bass to treble)
        self.string_sets = {
            # 6-string sets
            "e-E": ("ELowString", "AString", "dString", "gString", "bString", "eString"),
            # 4-string sets (most common for common V-System voicings)
            "e-b": ("bString", "gString", "dString", "eString"),  # High strings
            "d-E": ("ELowString", "AString", "dString", "gString"),  # Low strings
            "g-A": ("AString", "dString", "gString", "bString"),  # Middle strings
            # Extended 7/8 string sets
            "highA-E": ("ELowString", "AString", "dString", "gString", "bString", "eString", "highAString"),
            "e-lowB": ("lowBString", "ELowString", "AString", "dString", "gString", "bString", "eString"),
            "highA-lowB": ("lowBString", "ELowString", "AString", "dString", "gString", "bString", "eString", "highAString"),
        }
        
        # Major 7 chord intervals from root (in semitones)
        self.maj7_intervals = [0, 4, 7, 11]  # Root, Major 3rd, Perfect 5th, Major 7th
        
        # Available chord types and their interval structures (from root)
        # Using standard naming conventions for chords
        self.chord_types = {
            # Seventh chords - primary focus for V-System
            "Major 7": [0, 4, 7, 11],        # Root, Major 3rd, Perfect 5th, Major 7th
            "Dominant 7": [0, 4, 7, 10],     # Root, Major 3rd, Perfect 5th, Minor 7th
            "Minor 7": [0, 3, 7, 10],        # Root, Minor 3rd, Perfect 5th, Minor 7th
            "Minor 7b5": [0, 3, 6, 10],      # Root, Minor 3rd, Diminished 5th, Minor 7th
            "MinMaj 7": [0, 3, 7, 11],       # Root, Minor 3rd, Perfect 5th, Major 7th
            
            # Additional seventh chord types
            "Major 7(#5)": [0, 4, 8, 11],    # Root, Major 3rd, Augmented 5th, Major 7th
            "Major 7(b5)": [0, 4, 6, 11],    # Root, Major 3rd, Diminished 5th, Major 7th
            "Dominant 7(#5)": [0, 4, 8, 10], # Root, Major 3rd, Augmented 5th, Minor 7th
            "Dominant 7(b5)": [0, 4, 6, 10], # Root, Major 3rd, Diminished 5th, Minor 7th
            
            # Triads (less important for V-System, but included for completeness)
            "Major": [0, 4, 7],             # Root, Major 3rd, Perfect 5th
            "Minor": [0, 3, 7],             # Root, Minor 3rd, Perfect 5th
            "Diminished": [0, 3, 6],        # Root, Minor 3rd, Diminished 5th
            "Augmented": [0, 4, 8],         # Root, Major 3rd, Augmented 5th
        }

    def generate_v1_voicing(self, root_note, chord_type, string_set_key="e-b"):
        """Generate a V-1 (close position) voicing for a given chord.
        
        Args:
            root_note (int): Root note value (0-11, where 0=C, 1=C#, etc.)
            chord_type (str): Type of chord (e.g., "Major 7", "Dominant 7")
            string_set_key (str): Key for the string set to use (default: "e-b")
            
        Returns:
            ChordNotes: The created chord notes object
        """
        if chord_type not in self.chord_types:
            raise ValueError(f"Unsupported chord type: {chord_type}")
            
        if string_set_key not in self.string_sets:
            raise ValueError(f"Unsupported string set: {string_set_key}")
            
        # Get the intervals for the chord type
        intervals = self.chord_types[chord_type]
        
        # Calculate the absolute notes based on root and intervals
        notes = [(root_note + interval) % 12 for interval in intervals]
        
        # Get strings for this voicing (we'll use as many as we need based on chord type)
        strings = self.string_sets[string_set_key]
        
        # For V-1 (close position), we arrange the notes in close position
        # This means they should be arranged with no skips between chord tones
        
        # Sort the notes to ensure they're in ascending order for close position
        sorted_notes = sorted(notes)
        
        # Ensure we have the right number of strings
        if len(sorted_notes) > len(strings):
            raise ValueError(f"Not enough strings ({len(strings)}) for chord with {len(sorted_notes)} notes")
            
        # Print for debugging
        
        # Now create the chord
        with transaction.atomic():
            try:
                # Check if using 8-string ranges - they have character length issues
                if "highA" in string_set_key or "lowB" in string_set_key:
                    return None
                
                if len(sorted_notes) == 3:  # Triad
                    chord = ChordNotes.objects.create(
                        category_id=self.category_id,
                        type_name="V1",  # V-1 voicing type
                        chord_name=chord_type,
                        range=string_set_key,  # Use string set key as range name
                        tonal_root=root_note,
                        first_note=sorted_notes[0],
                        first_note_string=strings[0],
                        second_note=sorted_notes[1],
                        second_note_string=strings[1],
                        third_note=sorted_notes[2],
                        third_note_string=strings[2],
                        # No need for fourth_note for triads
                    )
                    
                elif len(sorted_notes) == 4:  # Seventh chord
                    chord = ChordNotes.objects.create(
                        category_id=self.category_id,
                        type_name="V1",  # V-1 voicing type
                        chord_name=chord_type,
                        range=string_set_key,  # Use string set key as range name
                        tonal_root=root_note,
                        first_note=sorted_notes[0],
                        first_note_string=strings[0],
                        second_note=sorted_notes[1],
                        second_note_string=strings[1],
                        third_note=sorted_notes[2],
                        third_note_string=strings[2],
                        fourth_note=sorted_notes[3],
                        fourth_note_string=strings[3],
                    )
                else:
                    raise ValueError(f"Unsupported number of notes: {len(sorted_notes)}")
                
                try:
                    # Skip 8-string range creation - set an attribute to prevent it
                    chord.skip_eight_string = True
                    
                    # Create positions for the chord
                    create_base_position(chord.id)
                    
                    return chord
                except Exception as e:
                    # Try to continue even if position creation fails
                    return chord
                
            except Exception as e:
                raise
            
    def generate_v2_voicing(self, root_note, chord_type, string_set_key="e-b"):
        """Generate a V-2 voicing (drop-2) for a given chord.
        
        Args:
            root_note (int): Root note value (0-11, where 0=C, 1=C#, etc.)
            chord_type (str): Type of chord (e.g., "Major 7", "Dominant 7")
            string_set_key (str): Key for the string set to use (default: "e-b")
            
        Returns:
            ChordNotes: The created chord notes object
        """
        if chord_type not in self.chord_types:
            raise ValueError(f"Unsupported chord type: {chord_type}")
            
        if string_set_key not in self.string_sets:
            raise ValueError(f"Unsupported string set: {string_set_key}")
            
        # Get the intervals for the chord type
        intervals = self.chord_types[chord_type]
        
        # Calculate the absolute notes based on root and intervals
        original_notes = [(root_note + interval) % 12 for interval in intervals]
        
        # Get strings for this voicing
        strings = self.string_sets[string_set_key]
        
        # Ensure we have the right number of strings
        if len(original_notes) > len(strings):
            raise ValueError(f"Not enough strings ({len(strings)}) for chord with {len(original_notes)} notes")
        
        # For V-2 (drop-2), we arrange the notes in close position first
        # Then drop the second highest note down an octave
        sorted_notes = sorted(original_notes)
        drop2_notes = sorted_notes.copy()
        
        # Print for debugging
        
        # If it's a seventh chord (4 notes)
        if len(drop2_notes) == 4:
            # The second highest note is at index 2
            # Drop it down an octave
            drop_note = drop2_notes[2]
            drop2_notes.remove(drop_note)
            drop2_notes.insert(0, (drop_note - 12) % 12)  # Insert at beginning
            
        # If it's a triad (3 notes)
        elif len(drop2_notes) == 3:
            # The second highest note is at index 1
            # Drop it down an octave
            drop_note = drop2_notes[1]
            drop2_notes.remove(drop_note)
            drop2_notes.insert(0, (drop_note - 12) % 12)  # Insert at beginning
            
        # Print for debugging
        
        # Now create the chord
        with transaction.atomic():
            try:
                # Check if using 8-string ranges - they have character length issues
                if "highA" in string_set_key or "lowB" in string_set_key:
                    return None
                
                if len(drop2_notes) == 3:  # Triad
                    chord = ChordNotes.objects.create(
                        category_id=self.category_id,
                        type_name="V2",  # V-2 voicing type
                        chord_name=chord_type,
                        range=string_set_key,  # Use string set key as range name
                        tonal_root=root_note,
                        first_note=drop2_notes[0],
                        first_note_string=strings[0],
                        second_note=drop2_notes[1],
                        second_note_string=strings[1],
                        third_note=drop2_notes[2],
                        third_note_string=strings[2],
                        # No need for fourth_note for triads
                    )
                    
                elif len(drop2_notes) == 4:  # Seventh chord
                    chord = ChordNotes.objects.create(
                        category_id=self.category_id,
                        type_name="V2",  # V-2 voicing type
                        chord_name=chord_type,
                        range=string_set_key,  # Use string set key as range name
                        tonal_root=root_note,
                        first_note=drop2_notes[0],
                        first_note_string=strings[0],
                        second_note=drop2_notes[1],
                        second_note_string=strings[1],
                        third_note=drop2_notes[2],
                        third_note_string=strings[2],
                        fourth_note=drop2_notes[3],
                        fourth_note_string=strings[3],
                    )
                    
                else:
                    raise ValueError(f"Unsupported number of notes: {len(drop2_notes)}")
                
                try:
                    # Skip 8-string range creation - set an attribute to prevent it
                    chord.skip_eight_string = True
                    
                    # Create positions for the chord
                    create_base_position(chord.id)
                    
                    return chord
                except Exception as e:
                    # Try to continue even if position creation fails
                    return chord
                
            except Exception as e:
                raise
            
    def generate_all_roots_v1(self, chord_type="Major 7", string_set_key="e-b"):
        """Generate V-1 voicings for all root notes of a given chord type.
        
        Args:
            chord_type (str): Type of chord (e.g., "Major 7", "Dominant 7")
            string_set_key (str): Key for the string set to use (default: "e-b")
            
        Returns:
            list: List of created ChordNotes objects
        """
        chords = []
        for root in range(12):  # 0-11 for all chromatic notes
            chord = self.generate_v1_voicing(root, chord_type, string_set_key)
            chords.append(chord)
        return chords
        
    def generate_all_roots_v2(self, chord_type="Major 7", string_set_key="e-b"):
        """Generate V-2 voicings for all root notes of a given chord type.
        
        Args:
            chord_type (str): Type of chord (e.g., "Major 7", "Dominant 7")
            string_set_key (str): Key for the string set to use (default: "e-b")
            
        Returns:
            list: List of created ChordNotes objects
        """
        chords = []
        for root in range(12):  # 0-11 for all chromatic notes
            chord = self.generate_v2_voicing(root, chord_type, string_set_key)
            chords.append(chord)
        return chords
        
    def generate_all_types_v1(self, root_note=0, string_set_key="e-b"):
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

    def generate_all_types_v2(self, root_note=0, string_set_key="e-b"):
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
