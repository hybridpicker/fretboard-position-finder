"""
Tests for the V-System implementation.
"""
from django.test import TestCase
from django.db import transaction
from .v_system_generator import VoicingSystem
from .models_chords import ChordNotes, ChordPosition
from .notes_choices import NOTES_CHOICES

class VSystemTest(TestCase):
    """
    Test cases for the Ted Greene V-System implementation.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        # Create necessary categories for tests
        from .models import NotesCategory
        self.v_system_category, _ = NotesCategory.objects.get_or_create(category_name='V-System')
        
        # Create a voicing system instance with the V-System category ID
        self.voicing_system = VoicingSystem(notes_category_id=self.v_system_category.id)
        
    def test_v1_generation(self):
        """
        Test V-1 (close position) voicing generation.
        """
        # Generate a C Major 7 chord in V-1 voicing
        chord = self.voicing_system.generate_v1_voicing(0, "Major 7", "e-b")
        
        # Verify the chord was created
        self.assertEqual(chord.type_name, "V1")
        self.assertEqual(chord.chord_name, "Major 7")
        self.assertEqual(chord.tonal_root, 0)  # C
        
        # Check if positions were created
        positions = ChordPosition.objects.filter(notes_name_id=chord.id)
        self.assertTrue(positions.exists())
        
        # Verify close position for V-1
        # Note intervals should all be within a single octave
        first_note = chord.first_note
        second_note = chord.second_note
        third_note = chord.third_note
        fourth_note = chord.fourth_note
        
        # Normalize notes to be within an octave of the first note
        while second_note < first_note:
            second_note += 12
        while third_note < second_note:
            third_note += 12
        while fourth_note < third_note:
            fourth_note += 12
            
        # The span should be less than an octave (12 semitones)
        span = fourth_note - first_note
        self.assertLess(span, 12)
        
    def test_v2_generation(self):
        """
        Test V-2 (drop-2) voicing generation.
        """
        # Generate a C Major 7 chord in V-2 voicing
        chord = self.voicing_system.generate_v2_voicing(0, "Major 7", "e-b")
        
        # Verify the chord was created
        self.assertEqual(chord.type_name, "V2")
        self.assertEqual(chord.chord_name, "Major 7")
        self.assertEqual(chord.tonal_root, 0)  # C
        
        # Check if positions were created
        positions = ChordPosition.objects.filter(notes_name_id=chord.id)
        self.assertTrue(positions.exists())
        
        # For a V-2 voicing, the second-highest note should be dropped an octave
        # So the order of the notes should not be strictly ascending
        notes = [chord.first_note, chord.second_note, chord.third_note, chord.fourth_note]
        
        # Normalize notes to be positive and comparable
        normalized_notes = notes.copy()
        for i in range(1, len(normalized_notes)):
            while normalized_notes[i] < normalized_notes[i-1]:
                normalized_notes[i] += 12
                
        # If this is truly a drop-2 voicing, the original notes should not be in ascending order
        self.assertNotEqual(notes, sorted(notes))
                
    def test_all_roots_generation(self):
        """
        Test generating voicings for all roots.
        """
        # Generate all 12 root notes for a Major 7 chord in V-1 voicing
        chords = self.voicing_system.generate_all_roots_v1("Major 7", "e-b")
        
        # Verify 12 chords were created (one for each root)
        self.assertEqual(len(chords), 12)
        
        # Check that each root is represented
        roots = [chord.tonal_root for chord in chords]
        self.assertEqual(set(roots), set(range(12)))  # 0-11 for all chromatic notes
        
    def test_all_types_generation(self):
        """
        Test generating all chord types for a root.
        """
        # Generate all chord types for C (0) in V-1 voicing
        chords = self.voicing_system.generate_all_types_v1(0, "e-b")
        
        # Verify a chord was created for each type in chord_types
        self.assertEqual(len(chords), len(self.voicing_system.chord_types))
        
        # Check that each chord type is represented
        chord_types = [chord.chord_name for chord in chords]
        self.assertEqual(set(chord_types), set(self.voicing_system.chord_types.keys()))
