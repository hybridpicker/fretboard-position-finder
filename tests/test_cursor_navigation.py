"""
Simple verification tests for cursor navigation functionality
"""

from django.test import TestCase, Client


class CursorNavigationVerificationTest(TestCase):
    """Verify cursor navigation is working correctly"""
    
    fixtures = ['full_database.json']
    
    def setUp(self):
        self.client = Client()
    
    def test_scale_page_loads_with_cursor_navigation(self):
        """Test that scale pages load with cursor navigation scripts"""
        # Test C Major scale
        url = '/?root=1&models_select=1&notes_options_select=1&position_select=0'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cursor-navigation-minimal.js')
    
    def test_chord_page_loads_with_navigation(self):
        """Test that chord pages load with navigation scripts"""
        # Test C Major chord
        url = '/?models_select=3&root=1&chords_options_select=Major&position_select=Root+Position'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'chord-navigation.js')
    
    def test_chord_inversion_navigation_urls(self):
        """Test that chord inversion URLs work correctly"""
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
            
            # Should contain chord navigation script
            self.assertContains(response, 'chord-navigation.js')
    
    def test_css_cursor_styling_included(self):
        """Test that cursor styling CSS is included"""
        response = self.client.get('/')
        
        # Check for cursor styling CSS files
        self.assertContains(response, 'cursor_controls.css')
        self.assertContains(response, 'custom-cursors.css')
    
    def test_bridge_script_present(self):
        """Test that chord controller bridge script is present"""
        response = self.client.get('/')
        self.assertContains(response, 'chord-controller-bridge.js')
    
    def test_no_old_cursor_files(self):
        """Test that old cursor files are not included"""
        response = self.client.get('/')
        content = response.content.decode()
        
        # These old files should not be present
        old_files = [
            'chord-cursor-direct.js',
            'chord-cursor-fix-final.js', 
            'chord-cursor-minimal.js',
            'chord-cursor-working.js'
        ]
        
        for old_file in old_files:
            self.assertNotIn(old_file, content,
                           f"Old cursor file {old_file} should not be included")
    
    def test_clean_javascript_structure(self):
        """Test that JavaScript structure is clean"""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Should have minimal number of cursor navigation scripts
        cursor_script_count = content.count('cursor-navigation')
        
        # Should only have 2: cursor-navigation-minimal.js and chord-navigation.js  
        self.assertLessEqual(cursor_script_count, 3,
                           f"Too many cursor navigation scripts: {cursor_script_count}")
    
    def test_page_functionality_basic(self):
        """Basic functionality test"""
        urls = [
            '/',
            '/?models_select=1&root=1',  # Scales
            '/?models_select=3&root=1',  # Chords
        ]
        
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Fretboard Position Finder')


if __name__ == '__main__':
    import unittest
    unittest.main()