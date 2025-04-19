import os
import unittest
from django.conf import settings
from django.test import TestCase


class LogoAvailabilityTests(TestCase):
    """Tests that ensure logo files are available in the expected locations."""
    
    def test_svg_logo_exists(self):
        """Test if the SVG logo file exists in the expected location."""
        # Path to the SVG logo (regular and themed versions)
        logo_path = os.path.join(settings.STATIC_ROOT, 'media', 'logo', 'Guitar_Positions_Logo.svg')
        themed_logo_path = os.path.join(settings.STATIC_ROOT, 'media', 'logo', 'Guitar_Positions_Logo_themed.svg')
        
        # Check if the files exist
        self.assertTrue(
            os.path.exists(logo_path),
            f"Logo file not found at {logo_path}"
        )
        
        self.assertTrue(
            os.path.exists(themed_logo_path),
            f"Themed logo file not found at {themed_logo_path}"
        )
    
    def test_logo_in_static_files(self):
        """Test that the logo is included in the static files list."""
        from django.contrib.staticfiles import finders
        
        # Check if the logo can be found by the static file finder
        logo_path = finders.find('media/logo/Guitar_Positions_Logo.svg')
        themed_logo_path = finders.find('media/logo/Guitar_Positions_Logo_themed.svg')
        
        self.assertIsNotNone(
            logo_path,
            "Logo file not found in static files"
        )
        
        self.assertIsNotNone(
            themed_logo_path,
            "Themed logo file not found in static files"
        )


if __name__ == '__main__':
    # This allows running the test directly without Django test runner
    # Note: This requires Django settings to be configured
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
    django.setup()
    
    # Create a more convenient script that can be run directly
    unittest.main()
