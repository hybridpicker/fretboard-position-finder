#!/usr/bin/env python3
"""
URL SEO Checker Tool

This script checks a given URL for SEO elements and provides a report.
It can be used to verify that all SEO elements are correctly implemented
on your guitar fretboard position finder application.

Usage:
    python check_url_seo.py http://localhost:8000/
"""

import argparse
import sys
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse

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

def check_url_seo(url):
    """Check a URL for SEO elements."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return False
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Initialize the SEO score
    seo_score = 0
    max_score = 10
    
    print(f"SEO Analysis for: {url}")
    print("=" * 50)
    
    # Check title
    title = soup.title.string if soup.title else None
    print(f"Title: {title or 'Missing'}")
    if title and len(title) > 10 and len(title) < 70:
        print("✓ Title length is good (10-70 characters)")
        seo_score += 1
    else:
        print("✗ Title should be between 10-70 characters")
    
    # Check meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    desc_content = meta_desc.get('content') if meta_desc else None
    print(f"Meta Description: {desc_content or 'Missing'}")
    
    if desc_content:
        if len(desc_content) > 50 and len(desc_content) < 160:
            print("✓ Meta description length is good (50-160 characters)")
            seo_score += 1
        else:
            print("✗ Meta description should be between 50-160 characters")
    else:
        print("✗ Meta description is missing")
    
    # Check meta keywords
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    keywords_content = meta_keywords.get('content') if meta_keywords else None
    print(f"Meta Keywords: {keywords_content or 'Missing'}")
    
    if keywords_content:
        seo_score += 1
        print("✓ Meta keywords found")
    else:
        print("✗ Meta keywords missing")
    
    # Check headings
    h1_tags = soup.find_all('h1')
    print(f"H1 Headings: {len(h1_tags)}")
    
    if len(h1_tags) == 1:
        print("✓ Page has exactly one H1 heading")
        seo_score += 1
    elif len(h1_tags) > 1:
        print("✗ Page has multiple H1 headings")
    else:
        print("✗ Page has no H1 heading")
    
    # Check canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    canonical_href = canonical.get('href') if canonical else None
    print(f"Canonical URL: {canonical_href or 'Missing'}")
    
    if canonical_href:
        print("✓ Canonical URL found")
        seo_score += 1
    else:
        print("✗ Canonical URL missing")
    
    # Check Open Graph tags
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    og_image = soup.find('meta', attrs={'property': 'og:image'})
    
    print("Open Graph Tags:")
    print(f"  - Title: {og_title.get('content') if og_title else 'Missing'}")
    print(f"  - Description: {og_desc.get('content') if og_desc else 'Missing'}")
    print(f"  - Image: {og_image.get('content') if og_image else 'Missing'}")
    
    if og_title and og_desc and og_image:
        print("✓ All Open Graph tags found")
        seo_score += 1
    else:
        print("✗ Some Open Graph tags missing")
    
    # Check Twitter Card tags
    twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
    twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
    twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
    
    print("Twitter Card Tags:")
    print(f"  - Title: {twitter_title.get('content') if twitter_title else 'Missing'}")
    print(f"  - Description: {twitter_desc.get('content') if twitter_desc else 'Missing'}")
    print(f"  - Card Type: {twitter_card.get('content') if twitter_card else 'Missing'}")
    
    if twitter_title and twitter_desc and twitter_card:
        print("✓ All Twitter Card tags found")
        seo_score += 1
    else:
        print("✗ Some Twitter Card tags missing")
    
    # Check structured data
    json_ld_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
    valid_json_ld = validate_json_ld(json_ld_scripts)
    
    print(f"Structured Data (JSON-LD): {len(valid_json_ld)} valid schema(s)")
    
    if valid_json_ld:
        print("✓ Valid structured data found")
        # Print the types of structured data
        for i, data in enumerate(valid_json_ld):
            print(f"  - Schema {i+1}: @type = {data.get('@type', 'Unknown')}")
        seo_score += 1
    else:
        print("✗ No valid structured data found")
    
    # Check for responsive design meta tag
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    viewport_content = viewport.get('content') if viewport else None
    print(f"Viewport Meta Tag: {viewport_content or 'Missing'}")
    
    if viewport_content and 'width=device-width' in viewport_content:
        print("✓ Responsive design meta tag found")
        seo_score += 1
    else:
        print("✗ Responsive design meta tag missing or incorrect")
    
    # Check for language declaration
    html_tag = soup.find('html')
    lang_attr = html_tag.get('lang') if html_tag else None
    print(f"Language Attribute: {lang_attr or 'Missing'}")
    
    if lang_attr:
        print("✓ Language attribute declared")
        seo_score += 1
    else:
        print("✗ Language attribute missing")
    
    # Check for JavaScript handling
    print("\nJavaScript Analysis:")
    scripts = soup.find_all('script', attrs={'src': True})
    inline_scripts = soup.find_all('script', attrs={'src': False})
    print(f"  - External scripts: {len(scripts)}")
    print(f"  - Inline scripts: {len(inline_scripts)}")
    
    # Calculate and display the SEO score
    seo_score_percent = (seo_score / max_score) * 100
    
    print("\nSEO Score: {:.1f}% ({}/{})".format(seo_score_percent, seo_score, max_score))
    
    if seo_score_percent >= 90:
        print("Excellent! Your page has very good SEO optimization.")
    elif seo_score_percent >= 70:
        print("Good. Your page has decent SEO optimization but could be improved.")
    elif seo_score_percent >= 50:
        print("Fair. Your page needs more work on SEO optimization.")
    else:
        print("Poor. Your page requires significant SEO improvements.")
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Check a URL for SEO elements')
    parser.add_argument('url', help='URL to check')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    url = args.url
    
    # Validate URL format
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print("Error: Invalid URL format. Please provide a complete URL including http:// or https://")
        sys.exit(1)
    
    success = check_url_seo(url)
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
