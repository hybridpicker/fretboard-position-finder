# Guitar Fretboard Position Finder SEO Tools

This directory contains tools for testing and analyzing the SEO implementation of your guitar fretboard position finder application.

## Overview

The SEO implementation includes:

- Meta tags for proper search engine indexing
- Open Graph tags for social media sharing
- Twitter Card tags for Twitter sharing
- Schema.org structured data for rich search results
- Canonical URLs to prevent duplicate content
- Sitemap.xml for search engine crawling
- Robots.txt for crawler directives

## Testing Tools

### 1. SEO Tests Runner

This script runs Django tests to verify that all SEO components are properly installed and configured.

```bash
# Run the tests
./venv/bin/python run_seo_tests.py
```

This will:
- Run Django tests for the SEO implementation
- Validate templates
- Check for required meta tags
- Provide an overall pass/fail result

### 2. SPA SEO Checker

This tool analyzes a running instance of your application for SEO best practices.

```bash
# Start your Django server
./venv/bin/python manage.py runserver

# In another terminal, run the SEO checker
./venv/bin/python check_spa_seo.py http://localhost:8000/
```

This will analyze:
- Meta tags and descriptions
- Structured data (JSON-LD)
- Heading structure
- Music and guitar-specific terminology
- Mobile responsiveness
- Social sharing tags
- ...and more

## Troubleshooting

If you encounter issues with the tests:

1. Make sure you're using the virtual environment's Python interpreter
2. Ensure all SEO files are in the correct locations
3. Check that the SEO context processor is registered in settings.py
4. Verify that structured data templates have valid JSON

## SEO Implementation Details

The SEO implementation for the guitar fretboard position finder includes:

- **Base Template**: Meta tags in `fretboardbase.html`
- **Context Processor**: Dynamic SEO metadata in `positionfinder/seo_context_processor.py`
- **Structured Data**: Template-specific schemas in `templates/seo/` directory
- **Sitemap**: Simple sitemap for single-page application in `positionfinder/sitemaps.py`
- **Robots.txt**: Basic directives in `static/robots.txt`

## Best Practices

1. Keep meta descriptions between 50-160 characters
2. Use music/guitar-specific terminology in headings
3. Ensure chord, scale, and arpeggio names are visible in the HTML
4. Use structured data for chord and scale content
5. Provide high-quality Open Graph images for social sharing
