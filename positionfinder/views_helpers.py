"""
Helper functions for the positionfinder views.
"""
import os
import json
from django.conf import settings
from django.urls import reverse

def get_common_context(request):
    """
    Get common context variables for templates.
    """
    # Check if we should use the optimized chord view
    # First check the user preference (via a cookie or session)
    use_optimized = request.session.get('use_optimized_chord_view', None)
    
    # If not set in the session, check the query parameter
    if use_optimized is None:
        use_optimized = request.GET.get('optimized', None)
        if use_optimized is not None:
            # Convert string to boolean and store in session
            use_optimized = use_optimized.lower() in ('true', 'yes', '1')
            request.session['use_optimized_chord_view'] = use_optimized
    
    # If still not set, check the environment variable or settings
    if use_optimized is None:
        use_optimized = getattr(settings, 'USE_OPTIMIZED_CHORD_VIEW', False)
    
    # Common context values
    context = {
        'use_optimized_chord_view': use_optimized,
    }
    
    return context

def generate_seo_data(content_type, **kwargs):
    """
    Generate structured data for SEO based on content type.
    
    Args:
        content_type: 'scale', 'chord', 'arpeggio', or 'mode'
        **kwargs: Content-specific parameters:
            - For scales: root, scale_type, scale_formula, positions
            - For chords: root, chord_type, chord_notes, positions
            - For arpeggios: root, arpeggio_type, notes, positions
            - For modes: root, mode_name, parent_scale, positions
    
    Returns:
        Dictionary with structured data JSON
    """
    if content_type == 'chord':
        root = kwargs.get('root', '')
        chord_type = kwargs.get('chord_type', '')
        chord_notes = kwargs.get('chord_notes', [])
        positions = kwargs.get('positions', [])
        
        # Create chord description from notes
        notes_description = ', '.join(chord_notes) if chord_notes else ''
        
        # Get position fret (if available)
        position_fret = positions[0].get('position') if positions and len(positions) > 0 else None
        
        # Create structured data
        structured_data = {
            "@context": "https://schema.org",
            "@type": "MusicComposition",
            "name": f"{root} {chord_type} Chord",
            "musicCompositionForm": "Chord",
            "musicalKey": root,
            "description": f"{root} {chord_type} chord positions for guitar",
        }
        
        return {
            'chord_structured_data': json.dumps(structured_data),
            'chord_root': root,
            'chord_type': chord_type,
            'chord_notes_description': notes_description,
            'chord_position_fret': position_fret
        }
        
    elif content_type == 'scale':
        root = kwargs.get('root', '')
        scale_type = kwargs.get('scale_type', '')
        scale_formula = kwargs.get('scale_formula', '')
        positions = kwargs.get('positions', [])
        
        # Create structured data
        structured_data = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": f"{root} {scale_type} Scale",
            "description": f"{root} {scale_type} scale positions and patterns for guitar",
            "keywords": f"{root} {scale_type} scale, guitar scale, {scale_type} positions, {root} guitar scale",
            "learningResourceType": "Guitar Scale"
        }
        
        return {
            'scale_structured_data': json.dumps(structured_data),
            'scale_root': root,
            'scale_type': scale_type,
            'scale_formula': scale_formula
        }
        
    elif content_type == 'arpeggio':
        root = kwargs.get('root', '')
        arpeggio_type = kwargs.get('arpeggio_type', '')
        notes = kwargs.get('notes', [])
        positions = kwargs.get('positions', [])
        
        # Create structured data
        structured_data = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": f"{root} {arpeggio_type} Arpeggio",
            "description": f"{root} {arpeggio_type} arpeggio positions and patterns for guitar",
            "keywords": f"{root} {arpeggio_type} arpeggio, guitar arpeggio, {arpeggio_type} positions, {root} guitar arpeggio",
            "learningResourceType": "Guitar Arpeggio"
        }
        
        return {
            'arpeggio_structured_data': json.dumps(structured_data),
            'arpeggio_root': root,
            'arpeggio_type': arpeggio_type,
            'arpeggio_notes': ', '.join(notes) if notes else ''
        }
    
    # Default empty response
    return {}

def generate_breadcrumbs(path_parts):
    """
    Generate breadcrumb data for SEO.
    
    Args:
        path_parts: List of tuples (url, name) for breadcrumb path
        
    Returns:
        Breadcrumb structured data as a JSON string
    """
    breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    
    for i, (url, name) in enumerate(path_parts):
        breadcrumbs["itemListElement"].append({
            "@type": "ListItem",
            "position": i + 1,
            "name": name,
            "item": url
        })
    
    return json.dumps(breadcrumbs)
