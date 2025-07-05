"""
Test version update to v2.2
"""

from django.test import TestCase, Client
import os


class VersionUpdateTest(TestCase):
    """Test that version has been updated to v2.2"""
    
    fixtures = ['full_database.json']
    
    def setUp(self):
        self.client = Client()
    
    def test_cursor_navigation_version_updated_file(self):
        """Test that cursor navigation JavaScript file shows v2.2"""
        file_path = 'static/js/cursor-navigation-minimal.js'
        
        self.assertTrue(os.path.exists(file_path), 
                       f"Cursor navigation file {file_path} does not exist")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check version in header comment
        self.assertIn('v2.2', content)
        self.assertIn('Minimalist Cursor Navigation System v2.2', content)
        
        # Check version in code
        self.assertIn("version: '2.2'", content)
    
    def test_css_and_js_files_exist(self):
        """Test that v2.2 CSS and JS files exist on filesystem"""
        files_to_check = [
            'static/css/base.2.2.0.css',
            'static/js/fretboard_chords.2.2.0.js',
            'static/js/fretboard_scales.2.2.0.js'
        ]
        
        for file_path in files_to_check:
            with self.subTest(file_path=file_path):
                self.assertTrue(os.path.exists(file_path), 
                               f"Version 2.2 file {file_path} does not exist")
    
    def test_chord_page_uses_v2_2_js(self):
        """Test that chord pages reference v2.2 JavaScript files"""
        response = self.client.get('/?models_select=3&root=1&chords_options_select=Major')
        content = response.content.decode()
        
        # Should reference v2.2 fretboard chords JS
        self.assertIn('fretboard_chords.2.2.0.js', content)
        
        # Should reference v2.2 base CSS
        self.assertIn('base.2.2.0.css', content)


if __name__ == '__main__':
    import unittest
    unittest.main()