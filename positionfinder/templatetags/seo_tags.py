"""
Template tags for SEO optimization in templates.
These tags help generate specialized Schema.org structured data for
different content types like scales, chords, etc.
"""
from django import template
import json

register = template.Library()

@register.simple_tag
def chord_structured_data(chord_root, chord_type, chord_positions, is_printable=True):
    """
    Generates Schema.org structured data for a chord page.
    
    Args:
        chord_root: The root note of the chord (e.g., "C")
        chord_type: The type of chord (e.g., "Major", "Minor7")
        chord_positions: List of positions/fingerings for this chord
        is_printable: Whether there is a print option available
        
    Returns:
        JSON-LD structured data for the chord
    """
    data = {
        "@context": "https://schema.org",
        "@type": "MusicComposition",
        "name": f"{chord_root} {chord_type} Chord",
        "musicCompositionForm": "Chord",
        "musicalKey": chord_root,
        "description": f"{chord_root} {chord_type} chord positions for guitar",
    }
    
    # Add extra properties if the chord has positions
    if chord_positions and len(chord_positions) > 0:
        data["numberOfPositions"] = len(chord_positions)
    
    # Add potential action for printable version
    if is_printable:
        data["potentialAction"] = {
            "@type": "ViewAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": "?print=true",
                "actionPlatform": ["http://schema.org/DesktopWebPlatform"]
            },
            "name": "Print Chord Chart"
        }
    
    return json.dumps(data)

@register.simple_tag
def scale_structured_data(scale_root, scale_type, scale_formula=None, scale_positions=None):
    """
    Generates Schema.org structured data for a scale page.
    
    Args:
        scale_root: The root note of the scale (e.g., "C")
        scale_type: The type of scale (e.g., "Major", "Minor Pentatonic")
        scale_formula: The scale formula/intervals (e.g., "1,2,3,4,5,6,7")
        scale_positions: List of positions/fingerings for this scale
        
    Returns:
        JSON-LD structured data for the scale
    """
    data = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": f"{scale_root} {scale_type} Scale",
        "description": f"{scale_root} {scale_type} scale positions and patterns for guitar",
        "keywords": f"{scale_root} {scale_type} scale, guitar scale, {scale_type} positions, {scale_root} guitar scale",
    }
    
    # Add teaching material aspect
    data["learningResourceType"] = "Guitar Scale"
    
    # Add extra properties if scale formula is available
    if scale_formula:
        data["additionalProperty"] = {
            "@type": "PropertyValue",
            "name": "Scale Formula",
            "value": scale_formula
        }
    
    # Add number of positions if available
    if scale_positions and len(scale_positions) > 0:
        data["numberOfPatterns"] = len(scale_positions)
    
    return json.dumps(data)

@register.simple_tag
def fretboard_breadcrumbs(path_parts):
    """
    Generates Schema.org breadcrumb structured data.
    
    Args:
        path_parts: List of path segments and their names
        
    Returns:
        JSON-LD structured data for breadcrumbs
    """
    breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    
    for i, (path, name) in enumerate(path_parts):
        breadcrumbs["itemListElement"].append({
            "@type": "ListItem",
            "position": i + 1,
            "name": name,
            "item": path
        })
    
    return json.dumps(breadcrumbs)
