"""
Improved chord search functionality for fretboard-position-finder
This module enhances the search logic for chords to better handle queries 
like "Gmaj7 V2" or "A Major Spread Triad".
"""
import logging
import re
import traceback

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Chord quality mappings to standardize search terms
CHORD_QUALITY_MAP = {
    'maj7': 'Major 7',
    'maj': 'Major',
    'major7': 'Major 7',
    'major': 'Major',
    'min7': 'Minor 7',
    'minor7': 'Minor 7',
    'min': 'Minor',
    'minor': 'Minor',
    'm7': 'Minor 7', 
    'm': 'Minor',
    'dim7': 'Diminished 7',
    'dim': 'Diminished',
    'diminished': 'Diminished',
    'm7b5': 'Minor 7b5',
    'dom7': 'Dominant 7',
    '7': 'Dominant 7',
    'dominant 7': 'Dominant 7',
    'aug': 'Augmented',
    'augmented': 'Augmented',
    '+': 'Augmented',
    'sus4': 'Sus4',
    'sus2': 'Sus2',
    '6': 'Major 6',
    '9': 'Dominant 9',
    '11': 'Dominant 11',
    '13': 'Dominant 13',
}

def improved_search_chords(search_query):
    """
    Enhanced search for chords supporting combined type, root, and position queries.
    Examples: 'Gmaj7 V2', 'A Major Spread Triad', 'C#min7'
    
    Returns a list of chord results with full metadata.
    """
    logger.debug(f"Entering improved_search_chords with query: '{search_query}'")
    results = []
    
    try:
        # Import needed modules here to avoid circular imports
        from django.db.models import Q
        from .models_chords import ChordNotes, ChordPosition
        from .search_utils import parse_query, ROOT_NAME_TO_ID
        
        # 1. Parse the query to extract components
        note, type_, quality, position, inversion = parse_query(search_query)
        logger.debug(f"Parsed query -> note: {note}, type: {type_}, quality: {quality}, position: {position}, inversion: {inversion}")
        
        # 2. Map the quality to a canonical chord name
        chord_name = CHORD_QUALITY_MAP.get(quality.lower(), quality.capitalize() if quality else None)
        logger.debug(f"Mapped quality '{quality}' to chord_name '{chord_name}'")
        
        # 3. Check for special queries like "Spread Triad"
        is_spread_triad_query = "spread" in search_query.lower() and "triad" in search_query.lower()
        
        # 3. Build the query filters
        filters = Q()
        
        # Handle chord name/quality
        if chord_name:
            filters &= Q(chord_name__icontains=chord_name)
        
        # Handle special case for spread triads
        if is_spread_triad_query:
            filters &= Q(type_name__icontains="Spread")
            logger.debug("Detected Spread Triad query, applying special filter")
        # Handle position name (e.g., V2, Spread Triads)
        elif position:
            if re.match(r'V\d+', position, re.IGNORECASE):
                position_number = position.upper()  # Normalize to uppercase for V-system
                filters &= Q(type_name__iexact=position_number)
            elif position:
                # For other positions like "Spread Triads"
                filters &= Q(type_name__icontains=position)
        
        # Run the query
        logger.debug(f"Searching with filters: {filters}")
        matches = ChordNotes.objects.filter(filters)
        logger.debug(f"Found {matches.count()} initial matches")
        
        # 4. Further filter by root note if specified
        if note:
            root_id = ROOT_NAME_TO_ID.get(note)
            if root_id:
                filtered_matches = matches.filter(tonal_root=root_id)
                if filtered_matches.exists():
                    matches = filtered_matches
                    logger.debug(f"Filtered to {matches.count()} matches by root {note} (ID: {root_id})")
                else:
                    logger.debug(f"No matches with root {note} (ID: {root_id}), keeping original results")
        
        # 5. Special handling for "Spread Triad" searches if still needed
        if is_spread_triad_query and matches.count() == 0:
            # Try a broader search for "Spread" in type_name
            logger.debug("No matches for Spread Triad, trying broader 'Spread' search")
            spread_matches = ChordNotes.objects.filter(type_name__icontains="Spread")
            
            # Further filter by chord name if available
            if chord_name:
                spread_matches = spread_matches.filter(chord_name__icontains=chord_name)
            
            # Further filter by root if available
            if note and root_id:
                spread_matches = spread_matches.filter(tonal_root=root_id)
            
            matches = spread_matches
            logger.debug(f"Found {matches.count()} matches with broader 'Spread' search")
        
        # 6. Process the matches into structured results
        results = process_improved_chord_results(matches, root_note=note)
        logger.debug(f"Processed {len(results)} final chord results")
        
        # 7. If no matches found but we have both root and quality, try a looser search
        if not results and note and quality:
            logger.debug(f"No exact matches - trying looser search for {note} {quality}")
            
            # First try with just chord name
            looser_filters = Q(chord_name__icontains=chord_name) if chord_name else Q()
            looser_matches = ChordNotes.objects.filter(looser_filters)
            
            # Apply root filtering if possible
            if note:
                root_id = ROOT_NAME_TO_ID.get(note)
                if root_id:
                    filtered_matches = looser_matches.filter(tonal_root=root_id)
                    if filtered_matches.exists():
                        looser_matches = filtered_matches
            
            if looser_matches.exists():
                logger.debug(f"Looser search found {looser_matches.count()} matches")
                results = process_improved_chord_results(looser_matches, root_note=note)
        
        return results
    
    except Exception as e:
        logger.error(f"Error in improved_search_chords: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def process_improved_chord_results(queryset, root_note=None):
    """
    Process chord query results into a standardized format with better display formatting.
    Handles root note display and proper URL construction.
    """
    # Import needed modules here to avoid circular imports
    from .search_utils import ROOT_NAME_TO_ID
    
    logger.debug(f"Processing {queryset.count() if hasattr(queryset, 'count') else len(queryset)} chord results")
    processed_results = []
    
    for chord in queryset:
        try:
            # 1. Get chord positions
            from .models_chords import ChordPosition
            positions = list(ChordPosition.objects.filter(notes_name=chord).values_list('inversion_order', flat=True))
            
            # 2. Collect the notes from this chord
            notes = []
            for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 'sixth_note']:
                note_value = getattr(chord, note_attr, None)
                if note_value is not None:
                    notes.append(note_value)
            
            # 3. Calculate intervals if needed
            intervals = []
            if hasattr(chord, 'intervals') and chord.intervals:
                intervals = chord.intervals
            elif notes and len(notes) > 1:
                root_pitch = notes[0]
                intervals = [(n - root_pitch) % 12 for n in notes]
            
            # 4. Get the appropriate root name (user-supplied or from the chord)
            display_root = root_note
            url_root_id = None
            
            # If the user provided a root note, use it for display
            if root_note:
                display_root = root_note
                url_root_id = ROOT_NAME_TO_ID.get(root_note)
            else:
                # Otherwise use the chord's tonal_root if available
                tonal_root = getattr(chord, 'tonal_root', None)
                if tonal_root is not None:
                    # Find the root name for this tonal_root
                    for name, root_id in ROOT_NAME_TO_ID.items():
                        if root_id == tonal_root:
                            display_root = name
                            url_root_id = root_id
                            break
            
            # Default to C (ID 1) if we couldn't determine a root
            if not url_root_id:
                url_root_id = 1
                if not display_root:
                    display_root = "C"
            
            # 5. Compose the chord name for display
            name = chord.chord_name
            if not name.startswith(display_root):
                name = f"{display_root} {name}"
            
            # 6. Build the URL for this chord
            url = f"/?root={url_root_id}&models_select=3&type_options_select={chord.type_name}&chords_options_select={chord.chord_name}&note_range={chord.range}"
            
            # Add position to URL if we have positions
            if positions:
                position_param = "Basic+Position" if "Basic Position" in positions else "Root+Position"
                url += f"&position_select={position_param}"
            
            # 7. Construct the result object
            chord_result = {
                'id': chord.id,
                'name': name,
                'type': chord.type_name,
                'category': getattr(chord.category, 'category_name', None) if hasattr(chord, 'category') else 'Chord',
                'positions': positions,
                'notes': notes,
                'intervals': intervals,
                'url': url,
                'range': getattr(chord, 'range', ''),
                'tonal_root': getattr(chord, 'tonal_root', None),
            }
            
            processed_results.append(chord_result)
            
        except Exception as e:
            logger.error(f"Error processing chord {getattr(chord, 'id', 'unknown')}: {str(e)}")
            continue
    
    # Sort results - prioritize V-system positions (V1, V2, etc.) and common ranges
    def sort_key(item):
        # Special handling for "Spread Triads" - give it highest priority
        type_name = item.get('type', '')
        if "Spread" in type_name:
            return (-1, 0)  # This will sort before everything else
        
        # Sort V-system positions next, alphabetically
        v_match = re.match(r'V(\d+)', type_name)
        if v_match:
            v_number = int(v_match.group(1))
            return (0, v_number)
        
        # Sort by range - prefer common ranges
        range_val = item.get('range', '')
        if 'e - g' in range_val:
            return (1, 0)  # High priority common range
        if 'b - d' in range_val:
            return (1, 1)
        
        # Everything else by ID
        return (2, item.get('id', 0))
    
    # Apply sorting if we have results
    if processed_results:
        processed_results.sort(key=sort_key)
    
    return processed_results
