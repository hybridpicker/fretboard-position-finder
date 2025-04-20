#!/usr/bin/env python3
"""
Single Page Application SEO Checker

This script is specialized for checking the SEO implementation in a single-page
guitar fretboard position finder application, where chords, scales, and arpeggios
are all served from the home route.

Usage:
    ./venv/bin/python check_spa_seo.py http://localhost:8000/
"""

import argparse
import sys
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse

# Try to import colorama for colored output
try:
    import colorama
    from colorama import Fore, Style
    colorama.init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # Create dummy color classes
    class DummyFore:
        def __getattr__(self, name):
            return ""
    class DummyStyle:
        def __getattr__(self, name):
            return ""
    Fore = DummyFore()
    Style = DummyStyle()

def validate_json_ld(scripts):
    """Validate JSON-LD structured data."""
    valid_scripts = []
    for script in scripts:
        try:
            data = json.loads(script.string)
            if '@context' in data and data['@context'] == 'https://schema.org':
                valid_scripts.append(data)
        except (json.JSONDecodeError, AttributeError):
            continue
    return valid_scripts

def print_success(message):
    """Print a success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print an error message."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print an info message."""
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")

def check_url_seo(url):
    """Check a URL for SEO elements specific to the guitar fretboard app."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print_error(f"Error fetching URL: {e}")
        return False
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Initialize the SEO score
    seo_score = 0
    max_score = 12  # Increased for more SPA-specific checks
    
    print_info(f"SEO Analysis for Guitar Fretboard Position Finder at: {url}")
    print("=" * 70)
    
    # Check title
    title = soup.title.string if soup.title else None
    print(f"Title: {title or 'Missing'}")
    if title and len(title) > 10 and len(title) < 70:
        print_success("Title length is good (10-70 characters)")
        seo_score += 1
    else:
        print_error("Title should be between 10-70 characters")
    
    # Check meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    desc_content = meta_desc.get('content') if meta_desc else None
    print(f"Meta Description: {desc_content[:100] + '...' if desc_content and len(desc_content) > 100 else desc_content or 'Missing'}")
    
    if desc_content:
        if len(desc_content) > 50 and len(desc_content) < 160:
            print_success("Meta description length is good (50-160 characters)")
            seo_score += 1
        else:
            print_error("Meta description should be between 50-160 characters")
    else:
        print_error("Meta description is missing")
    
    # Check meta keywords
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    keywords_content = meta_keywords.get('content') if meta_keywords else None
    if keywords_content:
        print(f"Meta Keywords: {keywords_content[:100] + '...' if len(keywords_content) > 100 else keywords_content}")
        if "guitar" in keywords_content.lower() and ("fretboard" in keywords_content.lower() or "chord" in keywords_content.lower() or "scale" in keywords_content.lower()):
            print_success("Keywords contain relevant guitar-related terms")
            seo_score += 1
        else:
            print_warning("Keywords should include more relevant guitar-related terms")
    else:
        print_error("Meta keywords missing")
    
    # Check headings
    h1_tags = soup.find_all('h1')
    if len(h1_tags) == 1:
        print_success(f"Page has exactly one H1 heading: \"{h1_tags[0].text.strip()}\"")
        seo_score += 1
    elif len(h1_tags) > 1:
        print_error(f"Page has multiple H1 headings ({len(h1_tags)})")
    else:
        print_error("Page has no H1 heading")
    
    # Check for music-specific terms in headings
    music_terms = ["chord", "scale", "arpeggio", "fretboard", "guitar", "position", "note"]
    headings_with_terms = 0
    all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    for heading in all_headings:
        heading_text = heading.text.lower()
        if any(term in heading_text for term in music_terms):
            headings_with_terms += 1
    
    print(f"Music-related terms in headings: {headings_with_terms}/{len(all_headings)}")
    if headings_with_terms >= len(all_headings) / 2:
        print_success("Headings contain good keyword density for musical terms")
        seo_score += 1
    else:
        print_warning("Consider using more musical terms in headings")
    
    # Check canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    canonical_href = canonical.get('href') if canonical else None
    print(f"Canonical URL: {canonical_href or 'Missing'}")
    
    if canonical_href:
        print_success("Canonical URL found")
        seo_score += 1
    else:
        print_error("Canonical URL missing")
    
    # Check Open Graph tags
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    og_image = soup.find('meta', attrs={'property': 'og:image'})
    
    print("Open Graph Tags:")
    print(f"  - Title: {og_title.get('content') if og_title else 'Missing'}")
    print(f"  - Description: {og_desc.get('content')[:100] + '...' if og_desc and len(og_desc.get('content', '')) > 100 else (og_desc.get('content') if og_desc else 'Missing')}")
    print(f"  - Image: {og_image.get('content') if og_image else 'Missing'}")
    
    if og_title and og_desc and og_image:
        print_success("All Open Graph tags found")
        seo_score += 1
    else:
        print_error("Some Open Graph tags missing")
    
    # Check Twitter Card tags
    twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
    twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
    twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
    
    print("Twitter Card Tags:")
    print(f"  - Title: {twitter_title.get('content') if twitter_title else 'Missing'}")
    print(f"  - Description: {twitter_desc.get('content')[:100] + '...' if twitter_desc and len(twitter_desc.get('content', '')) > 100 else (twitter_desc.get('content') if twitter_desc else 'Missing')}")
    print(f"  - Card Type: {twitter_card.get('content') if twitter_card else 'Missing'}")
    
    if twitter_title and twitter_desc and twitter_card:
        print_success("All Twitter Card tags found")
        seo_score += 1
    else:
        print_error("Some Twitter Card tags missing")
    
    # Check structured data
    json_ld_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
    valid_json_ld = validate_json_ld(json_ld_scripts)
    
    print(f"Structured Data (JSON-LD): {len(valid_json_ld)} valid schema(s)")
    
    if valid_json_ld:
        # Print the types of structured data
        for i, data in enumerate(valid_json_ld):
            print(f"  - Schema {i+1}: @type = {data.get('@type', 'Unknown')}")
        
        # Check for WebApplication or MusicApplication schema
        app_schema = False
        music_schema = False
        
        for data in valid_json_ld:
            schema_type = data.get('@type', '')
            if schema_type == 'WebApplication':
                app_schema = True
            if schema_type in ['MusicComposition', 'HowTo'] and any(term in json.dumps(data) for term in ['chord', 'scale', 'arpeggio', 'guitar']):
                music_schema = True
        
        if app_schema:
            print_success("WebApplication schema found")
            seo_score += 1
        else:
            print_warning("WebApplication schema recommended for better app visibility")
            
        if music_schema:
            print_success("Music-related schema found")
            seo_score += 1
        else:
            print_warning("Consider adding music-specific structured data")
    else:
        print_error("No valid structured data found")
    
    # Check for responsive design meta tag
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    viewport_content = viewport.get('content') if viewport else None
    print(f"Viewport Meta Tag: {viewport_content or 'Missing'}")
    
    if viewport_content and 'width=device-width' in viewport_content:
        print_success("Responsive design meta tag found")
        seo_score += 1
    else:
        print_error("Responsive design meta tag missing or incorrect")
    
    # Check for language declaration
    html_tag = soup.find('html')
    lang_attr = html_tag.get('lang') if html_tag else None
    print(f"Language Attribute: {lang_attr or 'Missing'}")
    
    if lang_attr:
        print_success("Language attribute declared")
        seo_score += 1
    else:
        print_error("Language attribute missing")
    
    # SPA-specific: Check for loading indicators (important for SEO as they indicate JS dependency)
    loading_indicators = soup.find_all(string=re.compile('loading|processing|wait|please wait'))
    if loading_indicators:
        print_warning(f"Found {len(loading_indicators)} loading indicators. Make sure content is accessible without JavaScript")
    else:
        print_success("No loading indicators found - content may be accessible without JavaScript")
        seo_score += 1
    
    # Calculate and display the SEO score
    seo_score_percent = (seo_score / max_score) * 100
    
    print("\n" + "=" * 70)
    print(f"SEO Score: {seo_score_percent:.1f}% ({seo_score}/{max_score})")
    
    if seo_score_percent >= 90:
        print_success("Excellent! Your fretboard app has very good SEO optimization.")
    elif seo_score_percent >= 70:
        print_warning("Good. Your fretboard app has decent SEO optimization but could be improved.")
    elif seo_score_percent >= 50:
        print_warning("Fair. Your fretboard app needs more work on SEO optimization.")
    else:
        print_error("Poor. Your fretboard app requires significant SEO improvements.")
    
    print("\nSpecific recommendations for guitar fretboard position finder:")
    
    # Provide guitar-specific recommendations
    recommendations = []
    if not music_schema:
        recommendations.append("Add music-specific structured data with MusicComposition schemas for chords and scales")
    
    if not og_image:
        recommendations.append("Add Open Graph image showing the fretboard interface for better social sharing")
    
    if headings_with_terms < len(all_headings) / 2:
        recommendations.append("Use more guitar-specific terminology in headings (chords, scales, arpeggios, positions)")
    
    recommendations.append("Consider adding FAQ schema for common questions about guitar positions")
    recommendations.append("Ensure chord and scale names are visible in the HTML source (not just rendered via JavaScript)")
    
    for i, recommendation in enumerate(recommendations, 1):
        print(f"{i}. {recommendation}")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("Guitar Fretboard Position Finder - SEO Analysis Tool")
    print("=" * 70)
    print("Analyzing your site for search engine optimization...\n")
    
    parser = argparse.ArgumentParser(description='Check a single-page guitar fretboard app for SEO elements')
    parser.add_argument('url', help='URL to check (typically the home page)')
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\nExample usage:")
        print("  ./venv/bin/python check_spa_seo.py http://localhost:8000/")
        sys.exit(1)
    
    args = parser.parse_args()
    url = args.url
    
    # Validate URL format
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print_error("Error: Invalid URL format. Please provide a complete URL including http:// or https://")
        sys.exit(1)
    
    success = check_url_seo(url)
    
    print("\n" + "=" * 70)
    if success:
        print("SEO Analysis Complete - See recommendations above")
    else:
        print("SEO Analysis Failed - Check connection to your server")
    print("=" * 70)
    
    if not success:
        sys.exit(1)
