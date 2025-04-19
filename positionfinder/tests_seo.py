"""
SEO implementation test suite.

This module contains tests to verify that the SEO optimization
has been correctly implemented across the project.
"""
import os
import re
import json
from django.test import TestCase, Client, RequestFactory
from django.template.loader import get_template
from django.urls import reverse
from django.conf import settings
from django.db import connection

class SEOImplementationTests(TestCase):
    """Test suite for verifying SEO implementation."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all tests."""
        from positionfinder.models import Root, Notes, NotesCategory
        from positionfinder.models_chords import ChordNotes
        
        # Create categories
        cls.scale_category = NotesCategory.objects.create(category_name='Scales')
        cls.arpeggio_category = NotesCategory.objects.create(category_name='Arpeggios')
        cls.chord_category = NotesCategory.objects.create(category_name='Chords')
        
        # Create root notes
        cls.c_root = Root.objects.create(name='C', pitch=1)
        cls.d_root = Root.objects.create(name='D', pitch=3)
        
        # Create scale
        cls.major_scale = Notes.objects.create(
            category=cls.scale_category,
            note_name='Major',
            ordering=1,
            first_note=0,    # C
            third_note=4,    # E
            fifth_note=7     # G
        )
        
        # Create arpeggio
        cls.major_arpeggio = Notes.objects.create(
            category=cls.arpeggio_category,
            note_name='Major',
            ordering=1,
            first_note=0,    # C
            third_note=4,    # E
            fifth_note=7     # G
        )
        
        # Create chord with the proper model fields
        cls.major_chord = ChordNotes.objects.create(
            category=cls.chord_category,
            type_name='Triads',
            chord_name='Major',
            chord_ordering=1,
            tonal_root=1,
            range='e - g',
            first_note=0,    # C
            second_note=4,   # E
            third_note=7     # G
        )
    
    def setUp(self):
        """Set up each test."""
        self.client = Client()
        self.factory = RequestFactory()
        # Base paths for key directories
        self.templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        self.seo_templates_dir = os.path.join(self.templates_dir, 'seo')
    
    def test_seo_files_exist(self):
        """Test that all required SEO files exist."""
        # Check for existence of key SEO files
        required_files = [
            os.path.join(self.templates_dir, 'fretboardbase.html'),
            os.path.join(self.seo_templates_dir, 'chord_structured_data.html'),
            os.path.join(self.seo_templates_dir, 'scale_structured_data.html'),
            os.path.join(self.seo_templates_dir, 'arpeggio_structured_data.html'),
            os.path.join(settings.BASE_DIR, 'positionfinder', 'seo_context_processor.py'),
            os.path.join(settings.BASE_DIR, 'static', 'robots.txt'),
        ]
        
        for file_path in required_files:
            self.assertTrue(os.path.exists(file_path), f"Required SEO file doesn't exist: {file_path}")
    
    def test_seo_context_processor_registered(self):
        """Test that the SEO context processor is registered in settings."""
        # Get the template options from settings
        templates_config = settings.TEMPLATES[0]
        context_processors = templates_config['OPTIONS']['context_processors']
        
        # Check if our SEO context processor is in the list
        self.assertIn(
            'positionfinder.seo_context_processor.get_seo_metadata',
            context_processors,
            "SEO context processor not registered in settings.TEMPLATES"
        )
    
    def test_base_template_has_meta_tags(self):
        """Test that the base template includes the necessary meta tags."""
        # Get the base template content
        base_template_path = os.path.join(self.templates_dir, 'fretboardbase.html')
        with open(base_template_path, 'r') as f:
            content = f.read()
        
        # Check for key meta tag patterns
        meta_patterns = [
            r'<meta\s+name="description"',
            r'<meta\s+name="keywords"',
            r'<meta\s+property="og:title"',
            r'<meta\s+property="og:description"',
            r'<meta\s+name="twitter:title"',
            r'<meta\s+name="twitter:description"',
            r'<link\s+rel="canonical"',
        ]
        
        for pattern in meta_patterns:
            self.assertTrue(
                re.search(pattern, content, re.IGNORECASE),
                f"Missing or incorrect meta tag pattern: {pattern}"
            )
    
    def test_structured_data_templates(self):
        """Test that structured data templates have valid JSON-LD."""
        structured_data_templates = [
            'seo/chord_structured_data.html',
            'seo/scale_structured_data.html',
            'seo/arpeggio_structured_data.html',
        ]
        
        for template_name in structured_data_templates:
            # Load the template
            template = get_template(template_name)
            
            # Create a mock context with required variables
            mock_context = {
                'root_name': 'C',
                'selected_chord': 'Major',
                'selected_scale': 'Major',
                'selected_arpeggio': 'Major',
                'selected_notes': ['C', 'E', 'G'],
                'chord_function': 'R - 3 - 5',
            }
            
            # Render the template with the mock context
            rendered = template.render(mock_context)
            
            # Extract JSON-LD content
            json_ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', 
                                         rendered, re.DOTALL)
            
            # Verify we found at least one JSON-LD block
            self.assertTrue(len(json_ld_matches) > 0, 
                           f"No JSON-LD found in {template_name}")
            
            # Validate each JSON-LD block
            for json_ld in json_ld_matches:
                try:
                    parsed = json.loads(json_ld.strip())
                    # Check for required Schema.org properties
                    self.assertEqual(parsed['@context'], 'https://schema.org',
                                    f"Invalid @context in {template_name}")
                    self.assertTrue('@type' in parsed,
                                  f"Missing @type in {template_name}")
                except json.JSONDecodeError:
                    self.fail(f"Invalid JSON-LD in {template_name}: {json_ld}")
    
    def test_views_include_seo_context(self):
        """Test that views include SEO context variables."""
        from positionfinder.views_helpers import generate_seo_data
        
        # Test chord SEO data generation
        chord_data = generate_seo_data('chord', root='C', chord_type='Major', 
                                      chord_notes=['C', 'E', 'G'], positions=[])
        
        self.assertTrue('chord_structured_data' in chord_data, 
                       "Missing chord_structured_data in SEO data")
        
        # Test scale SEO data generation
        scale_data = generate_seo_data('scale', root='C', scale_type='Major', 
                                      scale_formula='1-2-3-4-5-6-7', positions=[])
        
        self.assertTrue('scale_structured_data' in scale_data, 
                       "Missing scale_structured_data in SEO data")
    
    def test_sitemap_configuration(self):
        """Test that the sitemap configuration is correct."""
        # Import the sitemap module
        try:
            from positionfinder.sitemaps import StaticViewSitemap
            
            # Verify sitemap class exists and has required methods
            instance = StaticViewSitemap()
            self.assertTrue(hasattr(instance, 'items'), 
                          "StaticViewSitemap missing items method")
            self.assertTrue(hasattr(instance, 'location'), 
                          "StaticViewSitemap missing location method")
            
            # Check that the items method returns the expected URLs
            items = instance.items()
            self.assertIn('fretboard', items, "Home view (fretboard) missing from sitemap")
            self.assertIn('about', items, "About page missing from sitemap")
        except ImportError:
            self.fail("Failed to import sitemap classes")
    
    def test_robots_txt_content(self):
        """Test that robots.txt has the expected content."""
        robots_path = os.path.join(settings.BASE_DIR, 'static', 'robots.txt')
        with open(robots_path, 'r') as f:
            content = f.read()
        
        # Check for key directives
        self.assertIn('User-agent: *', content, "Missing User-agent directive in robots.txt")
        self.assertIn('Allow: /', content, "Missing Allow directive in robots.txt")
        self.assertIn('Disallow: /admin/', content, "Missing Disallow directive for admin in robots.txt")
        self.assertIn('Sitemap:', content, "Missing Sitemap directive in robots.txt")
    
    def test_view_helper_functions(self):
        """Test SEO helper functions in views_helpers.py."""
        from positionfinder.views_helpers import generate_breadcrumbs
        
        # Test breadcrumb generation with simple structure reflecting single-page app
        breadcrumbs = [
            ('/', 'Home'),
            ('/#chords', 'Chords'),
            ('/#scales', 'Scales'),
            ('/#arpeggios', 'Arpeggios'),
        ]
        
        breadcrumbs_json = generate_breadcrumbs(breadcrumbs)
        breadcrumbs_data = json.loads(breadcrumbs_json)
        
        self.assertEqual(breadcrumbs_data['@context'], 'https://schema.org', 
                        "Invalid @context in breadcrumbs")
        self.assertEqual(breadcrumbs_data['@type'], 'BreadcrumbList', 
                        "Invalid @type in breadcrumbs")
        self.assertEqual(len(breadcrumbs_data['itemListElement']), len(breadcrumbs), 
                        "Incorrect number of breadcrumb items")
    
    def test_seo_context_processor_functionality(self):
        """Test that the SEO context processor adds variables to the template context."""
        # Create a request object
        request = self.factory.get('/')
        
        # Import the context processor function
        from positionfinder.seo_context_processor import get_seo_metadata
        
        # Call the context processor with the request
        context = get_seo_metadata(request)
        
        # Verify that the context processor adds the expected variables
        self.assertTrue('page_title' in context, "page_title missing from SEO context")
        self.assertTrue('meta_description' in context, "meta_description missing from SEO context")
        self.assertTrue('meta_keywords' in context, "meta_keywords missing from SEO context")
        
        # Check for Open Graph and Twitter variables
        self.assertTrue('og_title' in context, "og_title missing from SEO context")
        self.assertTrue('og_description' in context, "og_description missing from SEO context")
        self.assertTrue('twitter_title' in context, "twitter_title missing from SEO context")
