#!/usr/bin/env python3
"""
This script checks for unused JavaScript and CSS files in the fretboard-position-finder project.
It analyzes template files for references to static assets and provides recommendations for cleanup.

Usage:
    python unused_file_detector.py

Author: Claude
Date: 2025-04-06
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Configuration
PROJECT_ROOT = Path.home() / "Coding" / "Django" / "fretboard-position-finder"
STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATE_DIR = PROJECT_ROOT / "templates"
JS_DIR = STATIC_DIR / "js"
CSS_DIR = STATIC_DIR / "css"

def collect_static_files():
    """Collect all JS and CSS files from the static directory."""
    js_files = set()
    css_files = set()
    
    # Collect JS files
    for file in JS_DIR.glob('**/*.js'):
        js_files.add(file.name)
    
    # Collect CSS files
    for file in CSS_DIR.glob('**/*.css'):
        css_files.add(file.name)
    
    return js_files, css_files

def scan_for_references():
    """Scan all template files for references to static JS and CSS files."""
    referenced_js = set()
    referenced_css = set()
    
    # Track where each file is referenced
    js_references = defaultdict(list)
    css_references = defaultdict(list)
    
    # Regular expressions to match static file references
    js_patterns = [
        re.compile(r"static\s+['\"](js/[^'\"]+)"),
        re.compile(r"script\s+src=['\"](?:[^'\"]*)/([^/'\"]+\.js)['\"]")
    ]
    
    css_patterns = [
        re.compile(r"static\s+['\"](css/[^'\"]+)"),
        re.compile(r"link\s+[^>]*href=['\"](?:[^'\"]*)/([^/'\"]+\.css)['\"]")
    ]
    
    # Scan all HTML files in template directory
    for root, _, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Find all references to JS files
                        for pattern in js_patterns:
                            for match in pattern.finditer(content):
                                filename = match.group(1)
                                if filename.startswith('js/'):
                                    filename = filename[3:]  # Remove 'js/' prefix
                                referenced_js.add(filename)
                                js_references[filename].append(file_path)
                        
                        # Find all references to CSS files
                        for pattern in css_patterns:
                            for match in pattern.finditer(content):
                                filename = match.group(1)
                                if filename.startswith('css/'):
                                    filename = filename[4:]  # Remove 'css/' prefix
                                referenced_css.add(filename)
                                css_references[filename].append(file_path)
                                
                except Exception as e:
    
    # Also scan JavaScript files for dynamic imports or references
    for js_file in JS_DIR.glob('**/*.js'):
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for dynamic script loading
                dynamic_patterns = [
                    re.compile(r"document\.createElement\(['\"]script['\"]\)[^;]*src\s*=\s*['\"](?:[^'\"]*)/([^/'\"]+\.js)['\"]"),
                    re.compile(r"import\s+.+\s+from\s+['\"]([^'\"]+)['\"]")
                ]
                
                for pattern in dynamic_patterns:
                    for match in pattern.finditer(content):
                        filename = match.group(1)
                        if not filename.endswith('.js'):
                            filename += '.js'
                        referenced_js.add(filename)
                        js_references[filename].append(str(js_file))
        except Exception as e:
    
    return referenced_js, referenced_css, js_references, css_references

def analyze_file_content(file_path):
    """Analyze a file's content to determine if it appears to be used or modified."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for commented-out code (an indicator of potential obsolete file)
            comment_ratio = content.count('//') / max(1, len(content.splitlines()))
            
            # Check for TODOs or FIXMEs
            has_todo = 'TODO' in content or 'FIXME' in content
            
            # Check for version indicators
            has_version = bool(re.search(r'v\d+\.\d+', content))
            
            return {
                'size': len(content),
                'comment_ratio': comment_ratio,
                'has_todo': has_todo,
                'has_version': has_version,
                'likely_obsolete': comment_ratio > 0.3 and has_todo
            }
    except Exception as e:
        return {'error': str(e)}

def find_unused_files():
    """Find JS and CSS files that aren't referenced in any template."""
    js_files, css_files = collect_static_files()
    referenced_js, referenced_css, js_references, css_references = scan_for_references()
    
    # Find unused files
    unused_js = js_files - referenced_js
    unused_css = css_files - referenced_css
    
    # Analyze each unused file
    js_analysis = {}
    for file in unused_js:
        file_path = JS_DIR / file
        if file_path.exists():
            js_analysis[file] = analyze_file_content(file_path)
    
    css_analysis = {}
    for file in unused_css:
        file_path = CSS_DIR / file
        if file_path.exists():
            css_analysis[file] = analyze_file_content(file_path)
    
    # Categorize files by likelihood of being safe to delete
    high_confidence_js = []
    medium_confidence_js = []
    low_confidence_js = []
    
    for file in unused_js:
        if file in js_analysis:
            analysis = js_analysis[file]
            
            # High confidence: Debug files, temporary fixes, or files with many comments
            if ('debug' in file.lower() or 
                'fix' in file.lower() or 
                'old' in file.lower() or
                (analysis.get('comment_ratio', 0) > 0.4)):
                high_confidence_js.append(file)
            
            # Medium confidence: Files with TODOs or versioning info
            elif analysis.get('has_todo', False) or analysis.get('has_version', False):
                medium_confidence_js.append(file)
            
            # Low confidence: Everything else
            else:
                low_confidence_js.append(file)
    
    high_confidence_css = []
    medium_confidence_css = []
    low_confidence_css = []
    
    for file in unused_css:
        if file in css_analysis:
            analysis = css_analysis[file]
            
            # Similar criteria as JS
            if ('debug' in file.lower() or 
                'fix' in file.lower() or 
                'old' in file.lower()):
                high_confidence_css.append(file)
            elif analysis.get('has_todo', False) or analysis.get('has_version', False):
                medium_confidence_css.append(file)
            else:
                low_confidence_css.append(file)
    
    # Print results
    
    
    
    # Detailed recommendations
    
    
    if high_confidence_js:
        for file in sorted(high_confidence_js):
    
    if high_confidence_css:
        for file in sorted(high_confidence_css):
    
    
    if medium_confidence_js:
        for file in sorted(medium_confidence_js):
    
    if medium_confidence_css:
        for file in sorted(medium_confidence_css):
    
    
    if low_confidence_js:
        for file in sorted(low_confidence_js):
    
    if low_confidence_css:
        for file in sorted(low_confidence_css):
    
    # Generate cleanup script
    
    
    for file in sorted(high_confidence_js):
    
    
    for file in sorted(high_confidence_css):
    
    
    # Recommendations
    
    return unused_js, unused_css

if __name__ == "__main__":
    find_unused_files()
