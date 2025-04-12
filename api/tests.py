from django.test import TestCase, Client
from django.urls import reverse
from positionfinder.models import Notes, Root, NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition
import json

class SearchFunctionalityTests(TestCase):
    """Test cases for the search functionality."""

    def setUp(self):
        """Set up test data."""
        # Create root notes
        self.root_c = Root.objects.create(name="C", pitch=0)
        self.root_g = Root.objects.create(name="G", pitch=7)
        self.root_a = Root.objects.create(name="A", pitch=9)
        
        # Create note categories
        self.scale_category = NotesCategory.objects.create(
            category_name="Minor Pentatonic Scale"
        )
        
        self.chord_category = NotesCategory.objects.create(
            category_name="Chords"
        )
        
        # Create chord types
        # C Major 7
        self.cmaj7 = ChordNotes.objects.create(
            category=self.chord_category,
            chord_name="Major 7",
            type_name="V1",
            range="e - d",
            tonal_root=0,  # C
            first_note=0,   # C
            first_note_string="dString",
            second_note=4,  # E
            second_note_string="gString",
            third_note=7,   # G
            third_note_string="bString",
            fourth_note=11, # B
            fourth_note_string="eString"
        )
        
        # G Dominant 7
        self.g7 = ChordNotes.objects.create(
            category=self.chord_category,
            chord_name="Dominant 7",
            type_name="V1",
            range="e - d",
            tonal_root=7,  # G
            first_note=7,   # G
            first_note_string="dString",
            second_note=11, # B
            second_note_string="gString",
            third_note=2,   # D
            third_note_string="bString",
            fourth_note=5,  # F
            fourth_note_string="eString"
        )
        
        # A Minor 7
        self.am7 = ChordNotes.objects.create(
            category=self.chord_category,
            chord_name="Minor 7",
            type_name="V1",
            range="e - d",
            tonal_root=9,  # A
            first_note=9,   # A
            first_note_string="dString",
            second_note=0,  # C
            second_note_string="gString",
            third_note=4,   # E
            third_note_string="bString",
            fourth_note=7,  # G
            fourth_note_string="eString"
        )
        
        # A Minor Scale
        self.a_minor_pentatonic = Notes.objects.create(
            category=self.scale_category,
            note_name="A Minor Pentatonic Scale",
            first_note=0,
            ordering=1
        )
        
        # Create chord positions (inversions)
        ChordPosition.objects.create(
            notes_name=self.cmaj7,
            inversion_order="Basic Position",
            first_note=0,
            second_note=0,
            third_note=0,
            fourth_note=0
        )
        
        ChordPosition.objects.create(
            notes_name=self.g7,
            inversion_order="Basic Position",
            first_note=0,
            second_note=0,
            third_note=0,
            fourth_note=0
        )
        
        ChordPosition.objects.create(
            notes_name=self.am7,
            inversion_order="Basic Position",
            first_note=0,
            second_note=0,
            third_note=0,
            fourth_note=0
        )
        
        # Initialize the test client
        self.client = Client()
        
    def test_normalize_search_term(self):
        """Test the normalize_search_term function directly."""
        from api.views_search import normalize_search_term
        
        # Test chord notation normalization
        self.assertEqual(normalize_search_term("G7"), "G Dominant 7")
        self.assertEqual(normalize_search_term("Cmaj7"), "C Major 7")
        self.assertEqual(normalize_search_term("Am7"), "A Minor 7")
        self.assertEqual(normalize_search_term("Am"), "A Minor")
        self.assertEqual(normalize_search_term("Amin"), "A Minor")
        self.assertEqual(normalize_search_term("Cm7b5"), "C Minor 7b5")
        self.assertEqual(normalize_search_term("Cdim7"), "C Diminished 7")
        self.assertEqual(normalize_search_term("Caug"), "C Augmented")
        
        # Test scale name handling
        self.assertEqual(normalize_search_term("A minor pentatonic"), "A Minor Pentatonic")
        self.assertEqual(normalize_search_term("A Minor Pentatonic"), "A Minor Pentatonic")
    
    def test_direct_match_chord_shorthand(self):
        """Test direct match with shorthand chord notation."""
        url = reverse('api:search_direct_match') + '?q=G7'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify response content
        data = json.loads(response.content)
        self.assertIn('debug', data)
        self.assertIn('matched_url', data['debug'])
        self.assertIsNotNone(data['debug']['matched_url'])
        self.assertIn('normalized_query', data['debug'])
        self.assertEqual(data['debug']['normalized_query'], 'G Dominant 7')
        
    def test_direct_match_chord_standard(self):
        """Test direct match with standard chord notation."""
        url = reverse('api:search_direct_match') + '?q=C+Major+7'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify response content
        data = json.loads(response.content)
        self.assertIn('debug', data)
        self.assertIn('matched_url', data['debug'])
        self.assertIsNotNone(data['debug']['matched_url'])
    
    def test_direct_match_scale(self):
        """Test direct match with scale notation."""
        url = reverse('api:search_direct_match') + '?q=A+Minor+Pentatonic'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify response content
        data = json.loads(response.content)
        self.assertIn('debug', data)
        self.assertIn('matched_url', data['debug'])
        self.assertIsNotNone(data['debug']['matched_url'])
    
    def test_autocomplete_chord_shorthand(self):
        """Test autocomplete with shorthand chord notation."""
        url = reverse('api:search_autocomplete') + '?q=G7'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify response content
        data = json.loads(response.content)
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)
        
        # Check if normalized name appears in results
        found = any(result['name'] == 'G Dominant 7' for result in data['results'])
        self.assertTrue(found, "G Dominant 7 should be in the results")
    
    def test_autocomplete_chord_standard(self):
        """Test autocomplete with standard chord notation."""
        url = reverse('api:search_autocomplete') + '?q=C+Major+7'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify response content
        data = json.loads(response.content)
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)
        
        # Check if exact name appears in results
        found = any(result['name'] == 'C Major 7' for result in data['results'])
        self.assertTrue(found, "C Major 7 should be in the results")
    
    def test_autocomplete_scale(self):
        """Test autocomplete with scale notation."""
        url = reverse('api:search_autocomplete') + '?q=A+Minor+Pentatonic'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify response content
        data = json.loads(response.content)
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)
        
        # Check if exact name appears in results
        found = any(result['name'] == 'A Minor Pentatonic Scale' for result in data['results'])
        self.assertTrue(found, "A Minor Pentatonic Scale should be in the results")
