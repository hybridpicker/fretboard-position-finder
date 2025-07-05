"""
Test for aggressive note hiding fix
"""

from django.test import TestCase, Client


class AggressiveNoteHidingTest(TestCase):
    """Test the aggressive note hiding implementation"""
    
    fixtures = ['full_database.json']
    
    def setUp(self):
        self.client = Client()
    
    def test_aggressive_hide_function_present(self):
        """Test that aggressiveHideNotes function is implemented"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Check for aggressive hiding function
        self.assertIn('aggressiveHideNotes', content)
        self.assertIn('setProperty', content)
        self.assertIn("'important'", content)
    
    def test_mutation_observer_implementation(self):
        """Test that MutationObserver is implemented for continuous monitoring"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Check for MutationObserver implementation
        self.assertIn('MutationObserver', content)
        self.assertIn('startNoteVisibilityGuard', content)
        self.assertIn('attributeFilter', content)
    
    def test_important_styles_override(self):
        """Test that inline styles are set with !important"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Check for !important style overrides
        self.assertIn("setProperty('visibility', 'hidden', 'important')", content)
        self.assertIn("setProperty('opacity', '0', 'important')", content)
    
    def test_multiple_timing_checks(self):
        """Test that hiding runs at multiple intervals"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Check for multiple setTimeout calls (updated for fixed version)
        self.assertIn('setTimeout(() =>', content)
        self.assertIn('hideNotesCallCount <= 3', content)
        self.assertIn('}, 100)', content)
        self.assertIn('}, 500)', content)
        self.assertIn('}, 1000)', content)
    
    def test_window_load_event_listener(self):
        """Test that hiding occurs on window load event"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Check for window load event
        self.assertIn("window.addEventListener('load'", content)
        self.assertIn('Window fully loaded', content)
    
    def test_class_removal_logic(self):
        """Test that problematic classes are removed"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Check for class removal
        self.assertIn("classList.remove('active', 'show-name', 'visible')", content)


if __name__ == '__main__':
    import unittest
    unittest.main()