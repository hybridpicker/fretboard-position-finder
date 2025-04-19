import os
import pytest
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

class TestTonePlayability(TestCase):
    """
    Test class to verify that:
    1. All tone files exist in the static directory
    2. All tones defined in JavaScript data structure exist as audio files
    3. All tones are correctly mapped to strings in the fretboard
    """
    
    def setUp(self):
        """Set up the test environment."""
        self.client = Client()
        # Path to static media directory for tone sounds
        self.tone_dir = os.path.join(settings.BASE_DIR, 'static', 'media', 'tone_sounds')
        
        # Get the complete list of strings on the fretboard
        self.string_array = [
            'highAString', 'eString', 'bString', 'gString', 
            'dString', 'AString', 'ELowString', 'lowBString'
        ]
        
        # Expected NOTES structure from base.2.0.4.js
        self.expected_notes = {
            'eString': [['f2'], ['fs2', 'gb2'], ['g2'], ['gs2', 'ab2'], ['a2'], ['as2', 'bb2'], ['b2'], ['c3'], ['cs3', 'db3'], ['d3'], ['ds3', 'eb3'], ['e3'], ['f3'], ['fs3', 'gb3'], ['g3'], ['gs3', 'ab3'], ['a3']],
            'bString': [['c2'], ['cs2', 'db2'], ['d2'], ['ds2', 'eb2'], ['e2'], ['f2'], ['fs2', 'gb2'], ['g2'], ['gs2', 'ab2'], ['a2'], ['as2', 'bb2'], ['b2'], ['c3'], ['cs3', 'db3'], ['d3'], ['ds3', 'eb3'], ['e3']],
            'gString': [['gs1', 'ab1'], ['a1'], ['as1', 'bb1'], ['b1'], ['c2'], ['cs2', 'db2'], ['d2'], ['ds2', 'eb2'], ['e2'], ['f2'], ['fs2', 'gb2'], ['g2'], ['gs2', 'ab2'], ['a2'], ['as2', 'bb2'], ['b2'], ['c3']],
            'dString': [['ds1', 'eb1'], ['e1'], ['f1'], ['fs1', 'gb1'], ['g1'], ['gs1', 'ab1'], ['a1'], ['as1', 'bb1'], ['b1'], ['c2'], ['cs2', 'db2'], ['d2'], ['ds2', 'eb2'], ['e2'], ['f2'], ['fs2', 'gb2'], ['g2']],
            'AString': [['as0', 'bb0'], ['b0'], ['c1'], ['cs1', 'db1'], ['d1'], ['ds1', 'eb1'], ['e1'], ['f1'], ['fs1', 'gb1'], ['g1'], ['gs1', 'ab1'], ['a1'], ['as1', 'bb1'], ['b1'], ['c2'], ['cs2', 'db2'], ['d2']],
            'ELowString': [['f0'], ['fs0', 'gb0'], ['g0'], ['gs0', 'ab0'], ['a0'], ['as0', 'bb0'], ['b0'], ['c1'], ['cs1', 'db1'], ['d1'], ['ds1', 'eb1'], ['e1'], ['f1'], ['fs1', 'gb1'], ['g1'], ['gs1', 'ab1'], ['a1']],
            'highAString': [['as2', 'bb2'], ['b2'], ['c3'], ['cs3', 'db3'], ['d3'], ['ds3', 'eb3'], ['e3'], ['f3'], ['fs3', 'gb3'], ['g3'], ['gs3', 'ab3'], ['a3'], ['as3', 'bb3'], ['b3'], ['c4'], ['cs4', 'db4'], ['d4']],
            'lowBString': [['c0'], ['cs0', 'db0'], ['d0'], ['ds0', 'eb0'], ['e0'], ['f0'], ['fs0', 'gb0'], ['g0'], ['gs0', 'ab0'], ['a0'], ['as0', 'bb0'], ['b0'], ['c1'], ['cs1', 'db1'], ['d1'], ['ds1', 'eb1'], ['e1']]
        }
    
    def test_tone_files_exist(self):
        """Test if all tone files exist in the static directory."""
        if not os.path.exists(self.tone_dir):
            self.fail(f"Tone directory '{self.tone_dir}' does not exist")
        
        # Get a flat list of all expected tones
        all_expected_tones = []
        for string_name, frets in self.expected_notes.items():
            for fret in frets:
                for tone in fret:
                    if tone not in all_expected_tones:
                        all_expected_tones.append(tone)
        
        print(f"Found {len(all_expected_tones)} unique tones in the NOTES data structure")
        
        # Check if tone files exist
        missing_files = []
        existing_files = []
        
        for tone in all_expected_tones:
            tone_file = f"{tone}.mp3"
            tone_path = os.path.join(self.tone_dir, tone_file)
            if not os.path.exists(tone_path):
                missing_files.append(tone_file)
            else:
                existing_files.append(tone_file)
        
        if missing_files:
            self.fail(f"{len(missing_files)} tone files are missing: {', '.join(missing_files)}")
        
        print(f"All {len(existing_files)} expected tone files exist")
    
    def test_js_notes_structure_integrity(self):
        """Test the integrity of the NOTES data structure."""
        # Ensure all strings defined in string_array have entries in NOTES
        for string_name in self.string_array:
            self.assertIn(string_name, self.expected_notes, 
                         f"String '{string_name}' exists in string_array but missing from NOTES")
        
        # Ensure each string has the expected number of frets (17 positions)
        for string_name, frets in self.expected_notes.items():
            self.assertEqual(len(frets), 17, 
                            f"String '{string_name}' should have 17 frets but has {len(frets)}")
    
    def test_enharmonic_equivalents(self):
        """Test that enharmonic equivalents are properly defined."""
        # Define all possible enharmonic pairs in both orders for flexibility
        enharmonic_pairs = [
            ('cs', 'db'), ('db', 'cs'),
            ('ds', 'eb'), ('eb', 'ds'),
            ('fs', 'gb'), ('gb', 'fs'),
            ('gs', 'ab'), ('ab', 'gs'),
            ('as', 'bb'), ('bb', 'as')
        ]
        
        # Test each string
        for string_name, frets in self.expected_notes.items():
            for fret in frets:
                # Skip frets with only one note
                if len(fret) < 2:
                    continue
                
                # Check that the two notes in the fret are enharmonic equivalents
                note1 = fret[0].rstrip('0123456789')
                note2 = fret[1].rstrip('0123456789')
                
                # Create a tuple with the two notes (without octave)
                fret_pair = (note1, note2)
                
                # Check if the pair is a valid enharmonic equivalent
                self.assertIn(fret_pair, enharmonic_pairs, 
                            f"Notes {fret} on {string_name} are not valid enharmonic equivalents")
    
    def test_octave_consistency(self):
        """Test that octave numbers are consistent across the fretboard."""
        # For each string, octave should be consistent or increment logically
        for string_name, frets in self.expected_notes.items():
            prev_octave = None
            
            for fret_index, fret in enumerate(frets):
                # Get octave from the first note in each fret
                current_octave = int(fret[0][-1])
                
                if prev_octave is not None:
                    # Octave should either stay the same or increment by 1
                    octave_diff = current_octave - prev_octave
                    self.assertIn(octave_diff, [0, 1], 
                                f"Unexpected octave jump on {string_name} from fret {fret_index-1} to {fret_index}")
                
                prev_octave = current_octave

    def test_adjacent_string_pitch_relationships(self):
        """Test that pitch relationships between adjacent strings are correct."""
        # Expected intervals between adjacent strings (in semitones)
        string_intervals = [
            ('highAString', 'eString', 5),    # Perfect 4th (A to E)
            ('eString', 'bString', 5),        # Perfect 4th (E to B)
            ('bString', 'gString', 4),        # Major 3rd (B to G)
            ('gString', 'dString', 5),        # Perfect 4th (G to D)
            ('dString', 'AString', 5),        # Perfect 4th (D to A)
            ('AString', 'ELowString', 5),     # Perfect 4th (A to E)
            ('ELowString', 'lowBString', 5)   # Perfect 4th (E to B)
        ]
        
        note_values = {
            'c': 0, 'cs': 1, 'db': 1, 'd': 2, 'ds': 3, 'eb': 3, 'e': 4, 'f': 5, 
            'fs': 6, 'gb': 6, 'g': 7, 'gs': 8, 'ab': 8, 'a': 9, 'as': 10, 'bb': 10, 'b': 11
        }
        
        for upper_string, lower_string, expected_interval in string_intervals:
            # Compare the open strings (first fret, first tone)
            upper_note = self.expected_notes[upper_string][0][0]
            lower_note = self.expected_notes[lower_string][0][0]
            
            # Extract note name and octave
            upper_note_name = upper_note.rstrip('0123456789')
            upper_octave = int(upper_note[-1])
            lower_note_name = lower_note.rstrip('0123456789')
            lower_octave = int(lower_note[-1])
            
            # Calculate the interval in semitones
            octave_diff = upper_octave - lower_octave
            note_diff = note_values[upper_note_name] - note_values[lower_note_name]
            total_interval = note_diff + (octave_diff * 12)
            
            # The interval may be negative if the upper string is lower in pitch
            actual_interval = (total_interval + 12) % 12 if expected_interval < 0 else total_interval
            
            self.assertEqual(actual_interval, expected_interval, 
                           f"Expected interval of {expected_interval} semitones between {upper_string} and {lower_string}, got {actual_interval}")

    def test_tone_file_playability_api(self):
        """Test if tone files are playable via an API endpoint (optional)."""
        # This is a placeholder for a potential API test
        # In a real implementation, you could:
        # 1. Create an API endpoint that tries to play tones
        # 2. Call it for each tone and check the response
        pass
