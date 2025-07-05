"""
Tests to check if high-confidence unused files have been removed.
"""
import os
from django.test import TestCase
from django.conf import settings

class UnusedFilesTestCase(TestCase):
    """Test case to verify that high-confidence unused files have been removed."""
    
    def test_high_confidence_files_removed(self):
        """
        Test that files identified as high-confidence unused have been removed from the project.
        This helps ensure the codebase stays clean and reduces unnecessary bloat.
        """
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        
        # High-confidence unused JS files that should be removed
        unused_js_files = [
            'js/cursor-click.js',
            'js/cursor-debug.js', 
            'js/cursor-styles/custom-cursors.js',
            # Add other high-confidence unused files here
        ]
        
        # High-confidence unused CSS files that should be removed
        unused_css_files = [
            # Add CSS files here if any are identified as unused
        ]
        
        # Check that JS files have been removed
        for js_file in unused_js_files:
            file_path = os.path.join(static_dir, js_file)
            self.assertFalse(
                os.path.exists(file_path),
                f"Unused JS file still exists: {js_file}. Please remove it to keep the codebase clean."
            )
        
        # Check that CSS files have been removed  
        for css_file in unused_css_files:
            file_path = os.path.join(static_dir, css_file)
            self.assertFalse(
                os.path.exists(file_path),
                f"Unused CSS file still exists: {css_file}. Please remove it to keep the codebase clean."
            )
            
        # Additional check: Verify that unused test files have been removed from old locations
        old_test_files = [
            'positionfinder/test_unused_files.py',
            'positionfinder/test_chord_search.py',
            'positionfinder/test_search_utils.py',
            'positionfinder/test_triads.py',
            'positionfinder/test_v_system.py',
        ]
        
        for test_file in old_test_files:
            file_path = os.path.join(settings.BASE_DIR, test_file)
            self.assertFalse(
                os.path.exists(file_path),
                f"Old test file still exists: {test_file}. Should be moved to tests/ directory."
            )
