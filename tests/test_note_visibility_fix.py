"""
Test for note visibility fix - ensuring note names don't flash on page load
"""

from django.test import TestCase, Client


class NoteVisibilityFixTest(TestCase):
    """Test that note names are properly hidden on page load"""
    
    fixtures = ['full_database.json']
    
    def setUp(self):
        self.client = Client()
    
    def test_cursor_navigation_has_hide_function(self):
        """Test that cursor navigation script contains the hideNonActiveNotes function"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Check for the hideNonActiveNotes function
        self.assertIn('hideNonActiveNotes', content)
        self.assertIn('data-note-active', content)
        self.assertIn('visibility = \'hidden\'', content)
        self.assertIn('opacity = \'0\'', content)
    
    def test_chord_page_note_visibility_logic(self):
        """Test that chord pages include the updated cursor navigation"""
        response = self.client.get('/?models_select=3&root=1&chords_options_select=Major')
        content = response.content.decode()
        
        # Should include the updated cursor navigation script
        self.assertIn('cursor-navigation-minimal.js', content)
        self.assertEqual(response.status_code, 200)
    
    def test_version_update_in_script(self):
        """Test that the script shows v2.2"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Check version is updated to 2.2
        self.assertIn('v2.2', content)
        self.assertIn("version: '2.2'", content)
        self.assertIn('Cursor Navigation System v2.2', content)
    
    def test_immediate_execution_present(self):
        """Test that the script executes hideNonActiveNotes immediately"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Should call hideNonActiveNotes immediately
        self.assertIn('hideNonActiveNotes();', content)
        
        # Should have faster initialization (50ms instead of 100ms)
        self.assertIn('setTimeout(CursorNav.init, 50)', content)
    
    def test_transition_removal_logic(self):
        """Test that transitions are disabled during hiding"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Should remove transitions during hiding to prevent animation
        self.assertIn("transition = 'none'", content)


if __name__ == '__main__':
    import unittest
    unittest.main()