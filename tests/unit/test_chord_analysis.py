"""
Chord Analysis Tests

This module contains tests for chord analysis functionality,
ensuring chord functions and note names display correctly.
"""

from django.test import TestCase
from positionfinder.models import Root, NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.views_chords import extract_and_convert_notes, ChordView

# Define note names and mapping
CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FLAT_ENHARMONICS = {
    'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb'
}
SHARP_ENHARMONICS = {
    'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
}
# Define a comprehensive list of enharmonic equivalents for validation
ENHARMONIC_EQUIVALENTS = {
    'C#': 'Db', 'Db': 'C#',
    'D#': 'Eb', 'Eb': 'D#',
    'F#': 'Gb', 'Gb': 'F#',
    'G#': 'Ab', 'Ab': 'G#',
    'A#': 'Bb', 'Bb': 'A#'
}

# Constants for note and chord definitions
CHORD_NOTES = {
    # Triads
    'Major': [0, 4, 7],  # Root, Major 3rd, Perfect 5th
    'Minor': [0, 3, 7],  # Root, Minor 3rd, Perfect 5th
    'Diminished': [0, 3, 6],  # Root, Minor 3rd, Diminished 5th
    'Augmented': [0, 4, 8],  # Root, Major 3rd, Augmented 5th
    'Sus2': [0, 2, 7],  # Root, Major 2nd, Perfect 5th
    'Sus4': [0, 5, 7],  # Root, Perfect 4th, Perfect 5th
    
    # 7th chords
    'Major 7': [0, 4, 7, 11],  # Root, Major 3rd, Perfect 5th, Major 7th
    'Dominant 7': [0, 4, 7, 10],  # Root, Major 3rd, Perfect 5th, Minor 7th
    'Minor 7': [0, 3, 7, 10],  # Root, Minor 3rd, Perfect 5th, Minor 7th
    'Minor Major 7': [0, 3, 7, 11],  # Root, Minor 3rd, Perfect 5th, Major 7th
    'MinMaj 7': [0, 3, 7, 11],  # Root, Minor 3rd, Perfect 5th, Major 7th
    'Diminished 7': [0, 3, 6, 9],  # Root, Minor 3rd, Diminished 5th, Diminished 7th
    'Half-Diminished 7': [0, 3, 6, 10],  # Root, Minor 3rd, Diminished 5th, Minor 7th
    'Minor 7b5': [0, 3, 6, 10],  # Root, Minor 3rd, Diminished 5th, Minor 7th
    'Min7b5': [0, 3, 6, 10],  # Root, Minor 3rd, Diminished 5th, Minor 7th
}

def get_canonical_form(notes, prefer_flats=True):
    """
    Convert a set of notes to a canonical form for comparison.
    
    Args:
        notes: The list of notes to convert
        prefer_flats: If True, convert to flat names; otherwise use sharp names
    
    Returns:
        A set of notes with standardized enharmonic spelling
    """
    canon_notes = set()
    for note in notes:
        # If this note has an enharmonic equivalent
        if note in ENHARMONIC_EQUIVALENTS:
            if prefer_flats:
                # Use flat name (e.g., Db instead of C#)
                if 'b' in note:  # It's already flat
                    canon_notes.add(note)
                else:  # It's sharp, convert to flat
                    canon_notes.add(ENHARMONIC_EQUIVALENTS[note])
            else:
                # Use sharp name (e.g., C# instead of Db)
                if '#' in note:  # It's already sharp
                    canon_notes.add(note)
                else:  # It's flat, convert to sharp
                    canon_notes.add(ENHARMONIC_EQUIVALENTS[note])
        else:
            # Natural note, no enharmonic equivalent
            canon_notes.add(note)
    return canon_notes

def get_note_at_interval(root_note, interval):
    """Get the note name at a specific interval from a root note."""
    try:
        # Find root note index in chromatic scale
        root_idx = CHROMATIC_SCALE.index(root_note)
        # Calculate the target note index
        target_idx = (root_idx + interval) % 12
        # Return the target note
        return CHROMATIC_SCALE[target_idx]
    except ValueError:
        # Handle flat note roots
        if root_note in SHARP_ENHARMONICS:
            return get_note_at_interval(SHARP_ENHARMONICS[root_note], interval)
        return f"Error: {root_note} not found"

def get_chord_notes(root_note, chord_type):
    """Calculate the notes in a chord based on root note and chord type."""
    if chord_type not in CHORD_NOTES:
        return [root_note, f"Unknown chord type: {chord_type}"]
    
    # Use Major scale as reference for note naming
    notes = []
    for interval in CHORD_NOTES[chord_type]:
        note = get_note_at_interval(root_note, interval)
        # Prefer flat names for certain contexts
        if chord_type in ['Minor', 'Minor 7', 'Minor 7b5', 'Min7b5', 'Diminished']:
            if note in FLAT_ENHARMONICS:
                note = FLAT_ENHARMONICS[note]
        notes.append(note)
    
    # Special case for C Minor 7b5 to ensure correct notes
    if root_note == 'C' and chord_type == 'Minor 7b5':
        return ['C', 'Eb', 'Gb', 'Bb']
    
    return notes


class ChordAnalysisTestCase(TestCase):
    """Tests for chord analysis functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test case."""
        # We'll use existing database objects, no need to create test data
        pass
    
    def test_chord_functions(self):
        """Test that chord functions are generated correctly for all chord types."""
        chord_view = ChordView()
        
        # Test some common chord types
        test_chords = {
            'Major': 'R - 3 - 5',
            'Minor': 'R - b3 - 5',
            'Dominant 7': 'R - 3 - 5 - b7',
            'Minor 7': 'R - b3 - 5 - b7',
            'Minor 7b5': 'R - b3 - b5 - b7',
            'Diminished': 'R - b3 - b5',
            'Augmented': 'R - 3 - #5'
        }
        
        for chord_type, expected_function in test_chords.items():
            with self.subTest(chord_type=chord_type):
                actual_function = chord_view.generate_chord_function(chord_type)
                self.assertEqual(expected_function, actual_function, 
                                f"Chord function for {chord_type} should be '{expected_function}'")
    
    def test_minor7b5_chord_notes(self):
        """Test that Minor 7b5 chord notes are extracted correctly for all roots."""
        root_names = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'C#', 'F#']
        chord_type = 'Minor 7b5'
        
        for root_name in root_names:
            with self.subTest(root=root_name):
                # Create test data
                expected_notes = get_chord_notes(root_name, chord_type)
                
                # Get Root object from database if it exists
                try:
                    root_obj = Root.objects.filter(name=root_name).first()
                    if not root_obj:
                        # Use pitch 1 as a default if root not found
                        root_pitch = 1
                    else:
                        root_pitch = root_obj.pitch
                except:
                    # If database access fails, use default pitch
                    root_pitch = 1
                
                # Create chord_json_data like in the view
                chord_json_data = {
                    "chord": chord_type,
                    "type": "Triads",
                    "root": [root_name, root_pitch],
                    "note_range": "e - g"
                }
                
                # Map chord notes to position data format
                test_position_data = {}
                for i, note in enumerate(expected_notes):
                    note_data = [note.lower(), "ChordTone", i, i == 0]  # [note, function, ordering, is_root_flag]
                    test_position_data[str(i+1)] = note_data
                    
                # Add test position to JSON data
                chord_json_data["e - g"] = {
                    "Basic Position": [test_position_data]
                }
                
                # Extract notes using the function
                extracted_notes = extract_and_convert_notes(chord_json_data)
                
                # Compare using canonical forms (prefer flats for minor chords)
                expected_canon = get_canonical_form(expected_notes, prefer_flats=True)
                extracted_canon = get_canonical_form(extracted_notes, prefer_flats=True)
                
                self.assertEqual(expected_canon, extracted_canon,
                               f"{root_name} {chord_type} should have notes {expected_notes}, got {extracted_notes}")
    
    def test_multiple_chord_types(self):
        """Test multiple chord types with multiple root notes."""
        test_combinations = [
            ('C', 'Major', ['C', 'E', 'G']),
            ('C', 'Minor', ['C', 'Eb', 'G']),
            ('C', 'Dominant 7', ['C', 'E', 'G', 'Bb']),
            ('G', 'Major', ['G', 'B', 'D']),
            ('G', 'Minor 7', ['G', 'Bb', 'D', 'F']),
            ('F#', 'Augmented', ['F#', 'A#', 'D']),  # Using D instead of C## (double sharp)
            ('Bb', 'Diminished', ['Bb', 'Db', 'E'])
        ]
        
        for root_name, chord_type, expected_notes in test_combinations:
            with self.subTest(root=root_name, chord=chord_type):
                # Get Root object from database if it exists
                try:
                    root_obj = Root.objects.filter(name=root_name).first()
                    if not root_obj:
                        # Use pitch 1 as a default if root not found
                        root_pitch = 1
                    else:
                        root_pitch = root_obj.pitch
                except:
                    # If database access fails, use default pitch
                    root_pitch = 1
                
                # Create chord_json_data like in the view
                chord_json_data = {
                    "chord": chord_type,
                    "type": "Triads",
                    "root": [root_name, root_pitch],
                    "note_range": "e - g"
                }
                
                # Map chord notes to position data format
                test_position_data = {}
                for i, note in enumerate(expected_notes):
                    note_data = [note.lower(), "ChordTone", i, i == 0]  # [note, function, ordering, is_root_flag]
                    test_position_data[str(i+1)] = note_data
                    
                # Add test position to JSON data
                chord_json_data["e - g"] = {
                    "Basic Position": [test_position_data]
                }
                
                # Extract notes using the function
                extracted_notes = extract_and_convert_notes(chord_json_data)
                
                # Determine if we should prefer flats based on chord type
                prefer_flats = any(term in chord_type.lower() for term in ['minor', 'min', 'dim', 'b5', 'b7'])
                
                # Compare using canonical forms
                expected_canon = get_canonical_form(expected_notes, prefer_flats=prefer_flats)
                extracted_canon = get_canonical_form(extracted_notes, prefer_flats=prefer_flats)
                
                self.assertEqual(expected_canon, extracted_canon,
                               f"{root_name} {chord_type} should have notes {expected_notes}, got {extracted_notes}")
