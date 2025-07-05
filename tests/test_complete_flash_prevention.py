"""
Test the complete note flash prevention solution
"""

from django.test import TestCase, Client


class CompleteFlashPreventionTest(TestCase):
    """Test the complete note flash prevention solution"""
    
    fixtures = ['full_database.json']
    
    def setUp(self):
        self.client = Client()
    
    def test_css_backstop_file_exists(self):
        """Test that the CSS backstop file exists"""
        import os
        self.assertTrue(os.path.exists('static/css/note-flash-prevention.css'))
    
    def test_css_backstop_content(self):
        """Test that CSS backstop has correct rules"""
        with open('static/css/note-flash-prevention.css', 'r') as f:
            content = f.read()
        
        # Check for important CSS rules
        self.assertIn('visibility: hidden !important', content)
        self.assertIn('opacity: 0 !important', content)
        self.assertIn('data-note-active="true"', content)
        self.assertIn('visibility: visible !important', content)
    
    def test_css_file_included_in_header(self):
        """Test that the CSS file is included in the header template"""
        with open('templates/header/header.html', 'r') as f:
            content = f.read()
        
        self.assertIn('note-flash-prevention.css', content)
    
    def test_javascript_and_css_work_together(self):
        """Test that both JavaScript and CSS solutions are present"""
        # Check JavaScript solution
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            js_content = f.read()
        
        self.assertIn('aggressiveHideNotes', js_content)
        self.assertIn('MutationObserver', js_content)
        
        # Check CSS solution
        with open('static/css/note-flash-prevention.css', 'r') as f:
            css_content = f.read()
        
        self.assertIn('!important', css_content)
    
    def test_chord_page_includes_both_solutions(self):
        """Test that chord pages include both CSS and JS solutions"""
        response = self.client.get('/?models_select=3&root=1&chords_options_select=Major')
        content = response.content.decode()
        
        # Should include both CSS and JS files
        self.assertIn('note-flash-prevention.css', content)
        self.assertIn('cursor-navigation-minimal.js', content)
        
        self.assertEqual(response.status_code, 200)
    
    def test_v2_2_version_in_debug_output(self):
        """Test that the debug output shows v2.2"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Check version in debug output
        self.assertIn('Cursor Navigation System v2.2 loaded', content)
    
    def test_comprehensive_note_hiding_logic(self):
        """Test that the comprehensive note hiding logic is present"""
        with open('static/js/cursor-navigation-minimal.js', 'r') as f:
            content = f.read()
        
        # Should have multiple strategies
        strategies = [
            'aggressiveHideNotes',           # Immediate hiding
            'MutationObserver',              # DOM change monitoring
            'setProperty',                   # Inline style override
            'window.addEventListener',       # Window load event
            'setTimeout',                    # Delayed checks
        ]
        
        for strategy in strategies:
            with self.subTest(strategy=strategy):
                self.assertIn(strategy, content, f"Strategy {strategy} not found")


if __name__ == '__main__':
    import unittest
    unittest.main()