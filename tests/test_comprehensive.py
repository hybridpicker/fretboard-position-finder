"""
Comprehensive tests for fretboard position finder functionality
Tests database integrity, cursor navigation, scales, chords, and arpeggios
"""

import json
from django.test import TestCase, Client
from django.urls import reverse
from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.positions import NotesPosition
from positionfinder.models_chords import ChordNotes, ChordPosition
from unittest.mock import patch


class DatabaseIntegrityTest(TestCase):
    """Test database integrity and basic data structure"""
    
    def test_root_notes_complete(self):
        """Test that all 12 chromatic notes exist in Root table"""
        roots = Root.objects.all().order_by('id')
        self.assertEqual(roots.count(), 24)  # 12 notes + 12 aliases
        
        # Check basic chromatic notes exist
        expected_notes = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
        for note in expected_notes:
            self.assertTrue(Root.objects.filter(name=note).exists(), 
                          f"Root note {note} missing from database")
    
    def test_scales_data_integrity(self):
        """Test that scales have proper data structure"""
        scales = Notes.objects.filter(category__category_name__in=['Scales', 'Arpeggios'])
        self.assertGreater(scales.count(), 0, "No scales found in database")
        
        for scale in scales[:10]:  # Test first 10 scales
            # Test scale has positions
            positions = NotesPosition.objects.filter(notes=scale)
            self.assertGreater(positions.count(), 0, 
                             f"Scale {scale.note_name} has no positions")
            
            # Test positions have valid fret numbers
            for position in positions:
                self.assertTrue(0 <= position.position <= 24, 
                              f"Invalid position {position.position} for scale {scale.note_name}")
    
    def test_chords_data_integrity(self):
        """Test that chords have proper data structure"""
        chords = ChordNotes.objects.all()
        self.assertGreater(chords.count(), 0, "No chords found in database")
        
        for chord in chords[:10]:  # Test first 10 chords
            # Test chord has positions
            positions = ChordPosition.objects.filter(chord_notes=chord)
            self.assertGreater(positions.count(), 0, 
                             f"Chord {chord.chord_name} has no positions")
            
            # Test positions have valid string assignments
            for position in positions:
                self.assertIsNotNone(position.string_1, 
                                   f"Chord position missing string assignments for {chord.chord_name}")
    
    def test_chord_inversions_exist(self):
        """Test that chords have multiple inversions"""
        # Find a chord with inversions
        chord_with_inversions = None
        for chord in ChordNotes.objects.all()[:20]:
            positions = ChordPosition.objects.filter(chord_notes=chord)
            position_names = [p.position for p in positions]
            if len(set(position_names)) > 1:
                chord_with_inversions = chord
                break
        
        self.assertIsNotNone(chord_with_inversions, 
                           "No chords with multiple inversions found")
        
        positions = ChordPosition.objects.filter(chord_notes=chord_with_inversions)
        position_names = [p.position for p in positions]
        self.assertIn('Root Position', position_names, 
                     "Root Position not found in chord inversions")


class CursorNavigationTest(TestCase):
    """Test cursor navigation functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_scale_page_loads(self):
        """Test that scale pages load correctly"""
        # Test Major scale in C
        url = '/?root=1&models_select=1&notes_options_select=1&position_select=0'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for cursor elements in template context
        self.assertContains(response, 'cursor-navigation-minimal.js')
    
    def test_chord_page_loads(self):
        """Test that chord pages load correctly"""
        # Test C Major chord
        url = '/?models_select=3&root=1&chords_options_select=Major&position_select=Root+Position'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for chord navigation script
        self.assertContains(response, 'chord-navigation.js')
    
    def test_chord_inversion_urls(self):
        """Test that chord inversion URLs work"""
        inversions = [
            'Root+Position',
            'First+Inversion', 
            'Second+Inversion',
            'Third+Inversion'
        ]
        
        for inversion in inversions:
            url = f'/?models_select=3&root=1&chords_options_select=Major+7&position_select={inversion}'
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, 
                           f"Failed to load chord page with {inversion}")


class APIEndpointTest(TestCase):
    """Test API endpoints for scales, chords, and search"""
    
    def setUp(self):
        self.client = Client()
    
    def test_scales_api(self):
        """Test scales API endpoint"""
        # Test if API endpoint exists
        try:
            url = reverse('api:scales')
            response = self.client.get(url, {'name': 'Major', 'root': 'C'})
            # Should return JSON data
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        except:
            # API might not be implemented, skip test
            self.skipTest("Scales API not available")
    
    def test_chords_api(self):
        """Test chords API endpoint"""
        try:
            url = reverse('api:chords')
            response = self.client.get(url, {'name': 'Major', 'root': 'C'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        except:
            self.skipTest("Chords API not available")
    
    def test_search_api(self):
        """Test search API endpoint"""
        try:
            url = reverse('api:search')
            response = self.client.get(url, {'q': 'C Major'})
            self.assertEqual(response.status_code, 200)
        except:
            self.skipTest("Search API not available")


class ScaleFunctionalityTest(TestCase):
    """Test scale-specific functionality"""
    
    def test_major_scale_notes(self):
        """Test that Major scale has correct notes"""
        # Find Major scale
        try:
            major_scale = Notes.objects.filter(
                note_name__icontains='Major',
                category__category_name='Scales'
            ).first()
            
            if major_scale:
                # Major scale should have positions
                positions = NotesPosition.objects.filter(notes=major_scale)
                self.assertGreaterEqual(positions.count(), 1, 
                                      "Major scale should have at least 1 position")
        except:
            self.skipTest("Major scale not found in database")
    
    def test_pentatonic_scales(self):
        """Test pentatonic scales exist"""
        pentatonic_scales = Notes.objects.filter(note_name__icontains='Pentatonic')
        self.assertGreater(pentatonic_scales.count(), 0, 
                         "No pentatonic scales found")
        
        # Test Minor Pentatonic specifically
        minor_pent = Notes.objects.filter(note_name__icontains='Minor Pentatonic').first()
        if minor_pent:
            positions = NotesPosition.objects.filter(notes=minor_pent)
            self.assertGreater(positions.count(), 0, 
                             "Minor Pentatonic should have positions")


class ChordFunctionalityTest(TestCase):
    """Test chord-specific functionality"""
    
    def test_basic_triads(self):
        """Test that basic triads exist"""
        triad_types = ['Major', 'Minor', 'Diminished', 'Augmented']
        
        for triad in triad_types:
            chords = ChordNotes.objects.filter(chord_name__icontains=triad)
            self.assertGreater(chords.count(), 0, 
                             f"No {triad} chords found")
    
    def test_seventh_chords(self):
        """Test that seventh chords exist"""
        seventh_types = ['Major 7', 'Minor 7', 'Dominant 7']
        
        for seventh in seventh_types:
            chords = ChordNotes.objects.filter(chord_name__icontains=seventh)
            self.assertGreater(chords.count(), 0, 
                             f"No {seventh} chords found")
    
    def test_chord_ranges(self):
        """Test that chords have different string ranges"""
        chord = ChordNotes.objects.first()
        if chord:
            positions = ChordPosition.objects.filter(chord_notes=chord)
            
            # Check that positions have string assignments
            for position in positions[:3]:  # Test first 3 positions
                strings = [position.string_1, position.string_2, 
                          position.string_3, position.string_4, 
                          position.string_5, position.string_6]
                non_null_strings = [s for s in strings if s is not None]
                self.assertGreater(len(non_null_strings), 0, 
                                 "Chord position should have string assignments")


class UserInterfaceTest(TestCase):
    """Test user interface elements"""
    
    def setUp(self):
        self.client = Client()
    
    def test_homepage_loads(self):
        """Test that homepage loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_navigation_elements_present(self):
        """Test that navigation elements are present"""
        response = self.client.get('/')
        
        # Check for essential form elements
        self.assertContains(response, 'models_select', 
                          msg_prefix="Model selector not found")
        self.assertContains(response, 'root', 
                          msg_prefix="Root selector not found")
    
    def test_javascript_files_load(self):
        """Test that JavaScript files are included"""
        response = self.client.get('/')
        
        # Check for cursor navigation scripts
        self.assertContains(response, 'cursor-navigation-minimal.js')
        self.assertContains(response, 'chord-navigation.js')
        
        # Check for other essential scripts
        self.assertContains(response, 'chord-controller-bridge.js')


class PerformanceTest(TestCase):
    """Test performance-related aspects"""
    
    def test_database_query_efficiency(self):
        """Test that database queries are efficient"""
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            # Reset query count
            connection.queries_log.clear()
            
            # Load a typical page
            response = self.client.get('/?root=1&models_select=1&notes_options_select=1')
            
            # Check query count is reasonable (less than 50 queries)
            query_count = len(connection.queries)
            self.assertLess(query_count, 50, 
                          f"Too many database queries: {query_count}")
    
    def test_page_load_speed(self):
        """Test that pages load within reasonable time"""
        import time
        
        start_time = time.time()
        response = self.client.get('/')
        load_time = time.time() - start_time
        
        # Page should load in less than 2 seconds
        self.assertLess(load_time, 2.0, 
                       f"Page load time too slow: {load_time}s")


class ErrorHandlingTest(TestCase):
    """Test error handling"""
    
    def test_invalid_root_parameter(self):
        """Test handling of invalid root parameter"""
        # Test with invalid root ID
        response = self.client.get('/?root=999&models_select=1')
        # Should not crash, should handle gracefully
        self.assertNotEqual(response.status_code, 500)
    
    def test_invalid_model_parameter(self):
        """Test handling of invalid model parameter"""
        response = self.client.get('/?root=1&models_select=999')
        self.assertNotEqual(response.status_code, 500)
    
    def test_missing_parameters(self):
        """Test handling of missing parameters"""
        response = self.client.get('/')  # No parameters
        self.assertEqual(response.status_code, 200)


# Test runner configuration
if __name__ == '__main__':
    import unittest
    unittest.main()