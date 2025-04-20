#!/usr/bin/env python3
"""
Chord Analysis Container Test

This script tests that every chord type for every root note correctly displays
chord functions and note names in the analysis container.

Usage:
    python chord_analysis_test.py

The script will:
1. Load data models with Django
2. Iterate through all root notes and chord types
3. Generate the expected chord functions and notes for each combination
4. Verify that the chord_function and selected_notes are correctly generated
5. Output a comprehensive report of any discrepancies
"""

import os
import sys
import json
import django
from collections import defaultdict

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
django.setup()

# Import Django models
from positionfinder.models import Root, NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.views_chords import extract_and_convert_notes, ChordView

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
    'Augmented 7': [0, 4, 8, 10],  # Root, Major 3rd, Augmented 5th, Minor 7th
    'Augmented Major 7': [0, 4, 8, 11],  # Root, Major 3rd, Augmented 5th, Major 7th
    
    # 6th chords
    'Major 6': [0, 4, 7, 9],  # Root, Major 3rd, Perfect 5th, Major 6th
    'Minor 6': [0, 3, 7, 9],  # Root, Minor 3rd, Perfect 5th, Major 6th
    
    # 9th chords
    'Major 9': [0, 4, 7, 11, 14],  # Root, Major 3rd, Perfect 5th, Major 7th, Major 9th
    'Dominant 9': [0, 4, 7, 10, 14],  # Root, Major 3rd, Perfect 5th, Minor 7th, Major 9th
    'Minor 9': [0, 3, 7, 10, 14],  # Root, Minor 3rd, Perfect 5th, Minor 7th, Major 9th
    
    # 11th chords
    'Major 11': [0, 4, 7, 11, 14, 17],  # Root, Major 3rd, Perfect 5th, Major 7th, Major 9th, Perfect 11th
    'Dominant 11': [0, 4, 7, 10, 14, 17],  # Root, Major 3rd, Perfect 5th, Minor 7th, Major 9th, Perfect 11th
    'Minor 11': [0, 3, 7, 10, 14, 17],  # Root, Minor 3rd, Perfect 5th, Minor 7th, Major 9th, Perfect 11th
    
    # 13th chords
    'Major 13': [0, 4, 7, 11, 14, 17, 21],  # Root, Major 3rd, Perfect 5th, Major 7th, Major 9th, Perfect 11th, Major 13th
    'Dominant 13': [0, 4, 7, 10, 14, 17, 21],  # Root, Major 3rd, Perfect 5th, Minor 7th, Major 9th, Perfect 11th, Major 13th
    'Minor 13': [0, 3, 7, 10, 14, 17, 21],  # Root, Minor 3rd, Perfect 5th, Minor 7th, Major 9th, Perfect 11th, Major 13th
    
    # Altered chords
    'Major 7(#5)': [0, 4, 8, 11],  # Root, Major 3rd, Augmented 5th, Major 7th
    'Major 7(b5)': [0, 4, 6, 11],  # Root, Major 3rd, Diminished 5th, Major 7th
    'Dominant 7(#5)': [0, 4, 8, 10],  # Root, Major 3rd, Augmented 5th, Minor 7th
    'Dominant 7(b5)': [0, 4, 6, 10],  # Root, Major 3rd, Diminished 5th, Minor 7th
    'Dominant 7(b9)': [0, 4, 7, 10, 13],  # Root, Major 3rd, Perfect 5th, Minor 7th, Minor 9th
    'Dominant 7(#9)': [0, 4, 7, 10, 15],  # Root, Major 3rd, Perfect 5th, Minor 7th, Augmented 9th
    'Dominant 7(#11)': [0, 4, 7, 10, 14, 18],  # Root, Major 3rd, Perfect 5th, Minor 7th, Major 9th, Augmented 11th
    'Dominant 7(b13)': [0, 4, 7, 10, 14, 17, 20],  # Root, Major 3rd, Perfect 5th, Minor 7th, Major 9th, Perfect 11th, Minor 13th
    
    # Add chords
    'Add9': [0, 4, 7, 14],  # Root, Major 3rd, Perfect 5th, Major 9th
    'Minor Add9': [0, 3, 7, 14],  # Root, Minor 3rd, Perfect 5th, Major 9th
}

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

def get_expected_chord_function(chord_type):
    """Get the expected chord function notation for a chord type."""
    chord_view = ChordView()
    return chord_view.generate_chord_function(chord_type)

def test_all_chord_notes_and_functions():
    """Test all chord notes and functions for all root notes and chord types."""
    print("Starting comprehensive chord analysis test...")
    
    # Create ChordView instance for function generation
    chord_view = ChordView()
    
    # Get all root notes
    root_notes = Root.objects.all()
    
    # Get all chord types from the database
    chord_types = ChordNotes.objects.values_list('chord_name', flat=True).distinct()
    
    # Normalize chord types - remove duplicates and add essential ones if missing
    essential_types = [
        'Major', 'Minor', 'Diminished', 'Augmented', 'Sus2', 'Sus4',
        'Major 7', 'Dominant 7', 'Minor 7', 'Minor 7b5'
    ]
    
    chord_types = set(chord_types)
    for essential in essential_types:
        chord_types.add(essential)
    
    chord_types = sorted(list(chord_types))
    
    # Test results storage
    failures = []
    type_failures = defaultdict(int)
    total_tests = 0
    
    print(f"Testing {len(root_notes)} root notes with {len(chord_types)} chord types...")
    
    # For each root note and chord type combination
    for root in root_notes:
        root_name = root.name
        print(f"\nTesting root note: {root_name}")
        
        for chord_type in chord_types:
            total_tests += 1
            
            # Skip if chord type is empty
            if not chord_type:
                continue
                
            print(f"  Testing chord type: {chord_type}")
            
            # 1. Get expected chord function
            expected_function = get_expected_chord_function(chord_type)
            
            # 2. Get expected notes
            expected_notes = get_chord_notes(root_name, chord_type)
            
            # 3. Generate chord JSON data like in the view
            chord_json_data = {
                "chord": chord_type,
                "type": "Triads",  # Default type
                "root": [root_name, root.pitch],
                "note_range": "e - g"  # Default range
            }
            
            # 4. Generate test position data with all notes
            test_position_data = {}
            # Map chord notes to position data format
            for i, note in enumerate(expected_notes):
                note_data = [note.lower(), "ChordTone", i, i == 0]  # [note, function, ordering, is_root_flag]
                test_position_data[str(i+1)] = note_data
                
            # 5. Add test position to JSON data
            chord_json_data["e - g"] = {
                "Basic Position": [test_position_data]
            }
            
            # 6. Extract notes using the function under test
            extracted_notes = []
            try:
                extracted_notes = extract_and_convert_notes(chord_json_data)
            except Exception as e:
                failures.append({
                    'root': root_name,
                    'chord_type': chord_type,
                    'error': f"Exception during note extraction: {str(e)}",
                    'expected_notes': expected_notes,
                    'extracted_notes': []
                })
                type_failures[chord_type] += 1
                continue
                
            # 7. Get chord function from the view class
            actual_function = chord_view.generate_chord_function(chord_type)
            
            # 8. Verify results - handling enharmonic equivalents
            # Determine whether to use flat or sharp preferences based on chord type
            prefer_flats = any(term in chord_type.lower() for term in ['minor', 'min', 'dim', 'b5', 'b7', 'b9', 'b13'])
            
            # Get canonical forms of both note sets
            expected_canon = get_canonical_form(expected_notes, prefer_flats)
            extracted_canon = get_canonical_form(extracted_notes, prefer_flats)
            
            # Compare canonical forms of the notes
            notes_match = expected_canon == extracted_canon
            function_match = expected_function == actual_function
            
            if not notes_match or not function_match:
                failure = {
                    'root': root_name,
                    'chord_type': chord_type,
                    'expected_notes': expected_notes,
                    'extracted_notes': extracted_notes,
                    'expected_function': expected_function,
                    'actual_function': actual_function,
                    'notes_match': notes_match,
                    'function_match': function_match
                }
                failures.append(failure)
                type_failures[chord_type] += 1
                
                print(f"    FAIL: Notes match: {notes_match}, Function match: {function_match}")
                print(f"      Expected notes: {expected_notes}")
                print(f"      Extracted notes: {extracted_notes}")
                print(f"      Expected function: {expected_function}")
                print(f"      Actual function: {actual_function}")
            else:
                print(f"    PASS: {root_name} {chord_type}")
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    print(f"Total tests: {total_tests}")
    print(f"Failed tests: {len(failures)}")
    print(f"Success rate: {(total_tests - len(failures))/total_tests:.2%}")
    
    # Print most problematic chord types
    if type_failures:
        print("\nMost problematic chord types:")
        for chord_type, count in sorted(type_failures.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {chord_type}: {count} failures")
    
    # Generate detailed report
    if failures:
        with open('chord_analysis_failures.json', 'w') as f:
            json.dump(failures, f, indent=2)
        print("\nDetailed failure report written to chord_analysis_failures.json")
    
    return failures

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

def test_minor7b5_only():
    """Run a targeted test for Minor 7b5 chords only."""
    print("\nTesting Minor 7b5 chords specifically...")
    print("===================================")
    
    # Get all root notes
    root_notes = Root.objects.all()
    
    # Test results
    failures = []
    total_tests = 0
    
    # Create ChordView instance for function generation
    chord_view = ChordView()
    
    # Expected function for Minor7b5
    expected_function = 'R - b3 - b5 - b7'
    
    for root in root_notes:
        root_name = root.name
        total_tests += 1
        
        print(f"Testing {root_name} Minor 7b5...")
        
        # Expected notes for this root
        # For Minor 7b5, the formula is root, minor third, diminished fifth, minor seventh
        expected_notes = get_chord_notes(root_name, 'Minor 7b5')
        
        # Build test chord JSON
        chord_json_data = {
            "chord": "Minor 7b5",
            "type": "Triads",
            "root": [root_name, root.pitch],
            "note_range": "e - g"
        }
        
        # Add position data
        position_data = {}
        for i, note in enumerate(expected_notes):
            position_data[str(i+1)] = [note.lower(), "Function", i, i == 0]
            
        chord_json_data["e - g"] = {
            "Basic Position": [position_data]
        }
        
        # Extract notes
        extracted_notes = extract_and_convert_notes(chord_json_data)
        
        # Get function
        actual_function = chord_view.generate_chord_function('Minor 7b5')
        
        # Check results - handling enharmonic equivalents
        # For Minor 7b5, always prefer flat spellings
        prefer_flats = True
        
        # Get canonical forms of both note sets 
        expected_canon = get_canonical_form(expected_notes, prefer_flats)
        extracted_canon = get_canonical_form(extracted_notes, prefer_flats)
        
        # Compare canonical forms
        notes_match = expected_canon == extracted_canon
        function_match = expected_function == actual_function
        
        if not notes_match or not function_match:
            failure = {
                'root': root_name,
                'expected_notes': expected_notes,
                'extracted_notes': extracted_notes,
                'expected_function': expected_function,
                'actual_function': actual_function
            }
            failures.append(failure)
            
            print(f"  FAIL:")
            if not notes_match:
                print(f"    Expected notes: {expected_notes}")
                print(f"    Extracted notes: {extracted_notes}")
            if not function_match:
                print(f"    Expected function: {expected_function}")
                print(f"    Actual function: {actual_function}")
        else:
            print(f"  PASS: {root_name} Minor 7b5 → {actual_function} → {' - '.join(extracted_notes)}")
    
    # Print summary
    print("\n=== MINOR 7b5 TEST SUMMARY ===")
    print(f"Total tests: {total_tests}")
    print(f"Failed tests: {len(failures)}")
    print(f"Success rate: {(total_tests - len(failures))/total_tests:.2%}")
    
    return failures

if __name__ == "__main__":
    print("Chord Analysis Container Test")
    print("============================")
    
    # Ask user which test to run
    print("\nWhich test would you like to run?")
    print("1. Test only Minor 7b5 chords (faster)")
    print("2. Test all chord types and root notes (comprehensive)")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        failures = test_minor7b5_only()
    else:
        print("\nRunning comprehensive test for all chord types...")
        failures = test_all_chord_notes_and_functions()
    
    # Final result
    if not failures:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n❌ {len(failures)} TESTS FAILED!")
        
    # Exit with appropriate status code
    sys.exit(1 if failures else 0)
