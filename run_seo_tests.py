#!/usr/bin/env python3
"""
SEO Test Runner

This script runs only the SEO tests to verify the implementation.
"""
import os
import sys
import subprocess
import django
from django.conf import settings

def run_tests():
    """Run SEO tests."""
    print("\nRunning Django tests for SEO implementation...\n")
    try:
        # Use sys.executable to get the current Python interpreter path
        python_path = sys.executable
        # Run the tests directly using manage.py
        subprocess.run([python_path, "manage.py", "test", "positionfinder.tests_seo"], check=True)
        print("\nSEO tests passed!\n")
        return 0
    except subprocess.CalledProcessError:
        print("\nSEO tests failed!\n")
        return 1

def validate_templates():
    """Validate Django templates."""
    print("\nValidating templates...\n")
    try:
        # Use sys.executable to get the current Python interpreter path
        python_path = sys.executable
        subprocess.run([python_path, "manage.py", "validate_templates"], check=True)
        print("\nTemplate validation passed!\n")
        return 0
    except subprocess.CalledProcessError:
        print("\nTemplate validation failed!\n")
        return 1

def check_meta_tags():
    """Check meta tags in base template."""
    # Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fretboard.settings")
    django.setup()
    
    print("\nChecking meta tags in base template...\n")
    base_template = os.path.join(settings.BASE_DIR, 'templates', 'fretboardbase.html')
    
    if not os.path.exists(base_template):
        print(f"Base template not found: {base_template}")
        return 1
    
    with open(base_template, 'r') as f:
        content = f.read()
    
    # Check for key meta tag patterns
    meta_patterns = {
        'description': r'<meta\s+name="description"',
        'keywords': r'<meta\s+name="keywords"',
        'og:title': r'<meta\s+property="og:title"',
        'og:description': r'<meta\s+property="og:description"',
        'twitter:title': r'<meta\s+name="twitter:title"',
        'twitter:description': r'<meta\s+name="twitter:description"',
        'canonical': r'<link\s+rel="canonical"',
        'json-ld': r'<script\s+type="application/ld\+json"',
    }
    
    missing = []
    found = []
    
    import re
    for name, pattern in meta_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            found.append(name)
        else:
            missing.append(name)
    
    if missing:
        print("Missing meta tags:")
        for tag in missing:
            print(f"  - {tag}")
        return 1
    else:
        print("All meta tags found:")
        for tag in found:
            print(f"  - {tag}")
        return 0

if __name__ == "__main__":
    print("=" * 70)
    print("Running SEO Implementation Tests")
    print("=" * 70)
    
    test_failures = run_tests()
    template_failures = validate_templates()
    metatag_failures = check_meta_tags()
    
    total_failures = test_failures + template_failures + metatag_failures
    
    print("\n" + "=" * 70)
    print(f"Test Results: {'PASSED' if total_failures == 0 else 'FAILED'}")
    print("=" * 70)
    
    if total_failures == 0:
        print("\n✅ All SEO tests passed!")
        print("\nYour SEO implementation is properly set up.")
        print("For a more comprehensive check of a running instance, use:")
        print("  ./venv/bin/python check_spa_seo.py http://localhost:8000/")
    else:
        print("\n❌ Some SEO tests failed.")
        print("\nPlease fix the issues and run the tests again.")
    
    sys.exit(total_failures)
