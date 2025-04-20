"""
Test to check that unused static files have been cleaned up from the project.
This test will fail if high-confidence unused files are still present in the project.
This encourages keeping the codebase clean of unused assets.

Usage:
    python manage.py test positionfinder.test_unused_files
"""

import os
from pathlib import Path
from django.test import TestCase
from django.conf import settings


class UnusedFilesTestCase(TestCase):
    """Test case to verify that high-confidence unused files have been removed."""

    def test_high_confidence_files_removed(self):
        """
        Test that high-confidence unused JavaScript files are not present.
        This test will fail if any of these files still exist.
        """
        # List of high confidence unused JS files that should be removed
        high_confidence_js_files = [
            "base_fixed.js",
            "c_major_final_fix.js",
            "c_major_fix.js",
            "c_major_fix_v2.js",
            "chord_note_autofix.js",
            "chord_ui_enhancements_fixed.js",
            "debug-helpers.js",
            "direct_keyboard_fix.js",
            "fixed-chord-inversions.js",
            "installHook.js",
            "keyboard_navigation_fix.js",
            "root_note_fix.js",
        ]

        # Get the static JS directory path
        static_js_dir = Path(settings.BASE_DIR) / 'static' / 'js'
        
        # Check each file
        existing_files = []
        for file in high_confidence_js_files:
            file_path = static_js_dir / file
            if file_path.exists():
                existing_files.append(file)
        
        # If any files exist, fail the test with a helpful message
        if existing_files:
            files_str = "\n  - ".join(existing_files)
            self.fail(
                f"The following unused files still exist and should be removed:\n"
                f"  - {files_str}\n\n"
                f"To clean up these files, run:\n"
                f"  $ ./utils/cleanup_unused.sh\n"
                f"Or remove them manually after making a backup."
            )

    def test_medium_confidence_files_reviewed(self):
        """
        Test to ensure medium confidence files have been reviewed.
        This test passes by default but logs a reminder to review these files.
        """
        # List of medium confidence files that should be reviewed
        medium_confidence_files = [
            # JS files
            "chord-inversion-cycling.js",
            "chord_note_data.js",
            "chord_note_validation_init.js",
            "chord_note_validation_ui.js",
            "chord_note_validator.js",
            "cursor-render.js",
            "cursor_cleanup.js",
            "cursor_regenerator.js",
            "disable-chord-inversions.js",
            "note-string-mapper.js",
            "single_keyboard_navigation.js",
            "string-definitions.js",
            "string-error-handler.js",
            "user_friendly_chord_selector.js",
            "v1-chord-support.js",
            "v1_compatibility.js",
            # CSS files
            "chord-inversion-cycling.css",
            "cursor-images.css",
        ]
        
        # Get the static directories
        static_js_dir = Path(settings.BASE_DIR) / 'static' / 'js'
        static_css_dir = Path(settings.BASE_DIR) / 'static' / 'css'
        
        # Check which files exist
        js_files = [f for f in medium_confidence_files if f.endswith('.js') and (static_js_dir / f).exists()]
        css_files = [f for f in medium_confidence_files if f.endswith('.css') and (static_css_dir / f).exists()]
        
        # Log but don't fail - this is just a reminder
        if js_files or css_files:
            if js_files:
                for file in js_files:
                    print(f"Unused JS file found (Reminder): {file}")
            if css_files:
                for file in css_files:
                    print(f"Unused CSS file found (Reminder): {file}")
