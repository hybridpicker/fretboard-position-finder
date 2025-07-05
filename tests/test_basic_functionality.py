"""
Basic functionality tests for fretboard position finder
Tests cursor navigation, page loads, and basic application functionality
"""

from django.test import TestCase, Client
from django.urls import reverse


class BasicFunctionalityTest(TestCase):
    """Test basic application functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_homepage_loads(self):
        """Test that homepage loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fretboard Position Finder')
    
    def test_cursor_scripts_included(self):
        """Test that cursor navigation scripts are included"""
        response = self.client.get('/')
        
        # Check for cursor navigation scripts
        self.assertContains(response, 'cursor-navigation-minimal.js',
                          msg_prefix="cursor-navigation-minimal.js not found")
        self.assertContains(response, 'chord-navigation.js',
                          msg_prefix="chord-navigation.js not found")
    
    def test_bridge_script_included(self):
        """Test that chord controller bridge script is included"""
        response = self.client.get('/')
        self.assertContains(response, 'chord-controller-bridge.js',
                          msg_prefix="chord-controller-bridge.js not found")
    
    def test_css_files_included(self):
        """Test that cursor CSS files are included"""
        response = self.client.get('/')
        
        # Check for cursor styling CSS
        self.assertContains(response, 'cursor_controls.css',
                          msg_prefix="cursor_controls.css not found")
        self.assertContains(response, 'custom-cursors.css',
                          msg_prefix="custom-cursors.css not found")
    
    def test_form_elements_present(self):
        """Test that essential form elements are present"""
        response = self.client.get('/')
        
        # Check for model selector
        self.assertContains(response, 'models_select',
                          msg_prefix="Model selector not found")
        
        # Check for root note selector
        self.assertContains(response, 'root',
                          msg_prefix="Root selector not found")
    
    def test_javascript_data_structure(self):
        """Test that JavaScript data structures are properly formatted"""
        response = self.client.get('/')
        
        # Check that voicing_data or scale_data variables are declared
        content = response.content.decode()
        has_voicing_data = 'var voicing_data' in content
        has_scale_data = 'var scale_data' in content
        
        # At least one should be present
        self.assertTrue(has_voicing_data or has_scale_data,
                       "Neither voicing_data nor scale_data found")
    
    def test_page_renders_without_errors(self):
        """Test that page renders without 500 errors"""
        test_urls = [
            '/',
            '/?models_select=1',
            '/?models_select=3',
        ]
        
        for url in test_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertNotEqual(response.status_code, 500,
                                  f"Server error for URL: {url}")
    
    def test_responsive_design_elements(self):
        """Test that responsive design elements are present"""
        response = self.client.get('/')
        
        # Check for viewport meta tag
        self.assertContains(response, 'viewport',
                          msg_prefix="Viewport meta tag not found")
    
    def test_favicon_included(self):
        """Test that favicon is included"""
        response = self.client.get('/')
        self.assertContains(response, 'favicon',
                          msg_prefix="Favicon not found")


class CursorNavigationTest(TestCase):
    """Test cursor navigation specific functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_cursor_elements_structure(self):
        """Test that cursor elements have proper structure"""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Check for cursor classes in CSS or templates
        has_cursor_elements = ('left-cursor' in content or 
                             'right-cursor' in content or
                             'cursor-navigation' in content)
        
        self.assertTrue(has_cursor_elements,
                       "No cursor navigation elements found")
    
    def test_keyboard_navigation_support(self):
        """Test that keyboard navigation support is included"""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Check for keyboard event handling
        has_keyboard_support = ('keydown' in content or 
                              'addEventListener' in content)
        
        self.assertTrue(has_keyboard_support,
                       "No keyboard navigation support found")
    
    def test_navigation_mode_detection(self):
        """Test that navigation mode detection is present"""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Check for mode detection in JavaScript
        has_mode_detection = ('mode' in content and 
                            ('scales' in content or 'chords' in content))
        
        self.assertTrue(has_mode_detection,
                       "No navigation mode detection found")


class ErrorHandlingTest(TestCase):
    """Test error handling and graceful degradation"""
    
    def setUp(self):
        self.client = Client()
    
    def test_graceful_handling_missing_parameters(self):
        """Test graceful handling when parameters are missing"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_graceful_handling_invalid_parameters(self):
        """Test graceful handling of invalid parameters"""
        test_cases = [
            '/?models_select=invalid',
            '/?root=invalid',
            '/?position_select=invalid',
        ]
        
        for url in test_cases:
            with self.subTest(url=url):
                response = self.client.get(url)
                # Should not crash with 500 error
                self.assertNotEqual(response.status_code, 500,
                                  f"Server error for invalid parameter: {url}")
    
    def test_no_javascript_errors_in_console(self):
        """Test that response doesn't contain obvious JavaScript errors"""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Check for common JavaScript error patterns
        error_patterns = [
            'undefined is not a function',
            'Cannot read property',
            'ReferenceError',
            'TypeError',
        ]
        
        for pattern in error_patterns:
            self.assertNotIn(pattern, content,
                           f"JavaScript error pattern found: {pattern}")


class PerformanceTest(TestCase):
    """Test basic performance aspects"""
    
    def setUp(self):
        self.client = Client()
    
    def test_page_load_time(self):
        """Test that page loads within reasonable time"""
        import time
        
        start_time = time.time()
        response = self.client.get('/')
        load_time = time.time() - start_time
        
        # Page should load in less than 5 seconds (very generous for tests)
        self.assertLess(load_time, 5.0,
                       f"Page load time too slow: {load_time}s")
        
        # Should return 200 OK
        self.assertEqual(response.status_code, 200)
    
    def test_response_size_reasonable(self):
        """Test that response size is reasonable"""
        response = self.client.get('/')
        
        # Response should not be empty
        self.assertGreater(len(response.content), 0,
                          "Empty response received")
        
        # Response should not be excessively large (>5MB)
        self.assertLess(len(response.content), 5 * 1024 * 1024,
                       f"Response too large: {len(response.content)} bytes")


# Test runner configuration
if __name__ == '__main__':
    import unittest
    unittest.main()