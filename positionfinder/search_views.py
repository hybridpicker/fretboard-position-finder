"""
Search views for the fretboard position finder
"""
import re
import logging
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
from positionfinder.models import Notes, Root, NotesCategory
from positionfinder.models_chords import ChordNotes
# Removed import for non-existent get_initial_menu_options

# Set up logger
logger = logging.getLogger(__name__)

def normalize_search_term(term):
    """
    Normalize search terms for better matching, handling common variations
    """
    # Convert to lowercase
    term = term.lower()
    
    # Handle sharp/flat notation variations
    term = term.replace('#', 'sharp').replace('♯', 'sharp')
    term = term.replace('b', 'flat').replace('♭', 'flat')
    
    # Handle common abbreviations
    term = term.replace('maj', 'major').replace('min', 'minor')
    term = term.replace('dom', 'dominant').replace('dim', 'diminished')
    term = term.replace('aug', 'augmented')
    
    return term

def search_view(request):
    """
    Main search view function that handles searching for root notes and types.
    """
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', None)
    string_filter = request.GET.get('strings', 'all')
    root_filter = request.GET.get('root', 'all')
    logger.debug(f"[SEARCH_VIEW] Query: '{query}', Category: {category_filter}, Strings: {string_filter}, Root: {root_filter}")
    
    # Store recent searches in session
    if query and len(query) > 1:
        recent_searches = request.session.get('recent_searches', [])
        # Add to recent searches if not already there
        if query not in recent_searches:
            recent_searches.insert(0, query)
            # Keep only the latest 5 searches
            recent_searches = recent_searches[:5]
            request.session['recent_searches'] = recent_searches
    
    # If no query, just render the search page with recent searches
    if not query:
        logger.debug("[SEARCH_VIEW] No query provided, rendering empty search page.")
        context = {
            'recent_searches': request.session.get('recent_searches', []),
        }
        return render(request, 'search/search_results.html', context)
    
    # Search logic
    scale_results = []
    arpeggio_results = []
    chord_results = []
    
    # Split query into potential note and type components
    query_parts = query.split(' ', 1)
    root_query = query_parts[0] if query_parts else ''
    type_query = query_parts[1] if len(query_parts) > 1 else ''
    
    # Common musical terms for types that might be searched
    musical_terms = ['major', 'minor', 'diminished', 'augmented', 'dominant', 
                     'suspended', 'pentatonic', 'blues', 'lydian', 'dorian', 
                     'phrygian', 'mixolydian', 'locrian', 'ionian', 'aeolian']
    
    # If the query has multiple parts, try to identify root note and type
    if type_query:
        logger.debug(f"[SEARCH_VIEW] Searching by note '{root_query}' and type '{type_query}'")
        # Look for exact matches with note and type
        scales, arpeggios, chords = search_by_note_and_type(root_query, type_query)
        scale_results.extend(scales)
        arpeggio_results.extend(arpeggios)
        chord_results.extend(chords)
    else:
        # If single term, check if it's a common musical term (like "minor")
        if query.lower() in musical_terms:
            logger.debug(f"[SEARCH_VIEW] Query '{query}' is a musical term, searching by type only.")
            # Search by type only
            scales, arpeggios, chords = search_by_type_only(query)
            scale_results.extend(scales)
            arpeggio_results.extend(arpeggios)
            chord_results.extend(chords)
        else:
            logger.debug(f"[SEARCH_VIEW] Query '{query}' is not a musical term, searching by note and type separately.")
            # Try to match the single term as a note or as a type
            note_scales, note_arpeggios, note_chords = search_by_note_only(query)
            type_scales, type_arpeggios, type_chords = search_by_type_only(query)
            
            scale_results.extend(note_scales)
            scale_results.extend(type_scales)
            arpeggio_results.extend(note_arpeggios)
            arpeggio_results.extend(type_arpeggios)
            chord_results.extend(note_chords)
            chord_results.extend(type_chords)
    
    # If a category filter is specified, only return those results
    if category_filter:
        logger.debug(f"[SEARCH_VIEW] Applying category filter: {category_filter}")
        if category_filter == 'scales':
            arpeggio_results = []
            chord_results = []
        elif category_filter == 'arpeggios':
            scale_results = []
            chord_results = []
        elif category_filter == 'chords':
            scale_results = []
            arpeggio_results = []
    
    # Count total results
    # Remove duplicates (simple approach based on URL, might need refinement)
    scale_results = list({item['url']: item for item in scale_results}.values())
    arpeggio_results = list({item['url']: item for item in arpeggio_results}.values())
    chord_results = list({item['url']: item for item in chord_results}.values())
    
    total_results = len(scale_results) + len(arpeggio_results) + len(chord_results)
    logger.debug(f"[SEARCH_VIEW] Found {len(scale_results)} scales, {len(arpeggio_results)} arpeggios, {len(chord_results)} chords. Total: {total_results}")
    
    context = {
        'query': query,
        'scale_results': scale_results,
        'arpeggio_results': arpeggio_results,
        'chord_results': chord_results,
        'total_results': total_results,
        'recent_searches': request.session.get('recent_searches', []),
        'category_filter': category_filter,
        'string_filter': string_filter,
        'root_filter': root_filter,
    }
    
    return render(request, 'search/search_results.html', context)

def search_json(request):
    """
    JSON API endpoint for the search overlay.
    Returns search results in JSON format for AJAX requests.
    """
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', None)
    string_filter = request.GET.get('strings', 'all')
    root_filter = request.GET.get('root', 'all')
    logger.debug(f"[SEARCH_JSON] Query: '{query}', Category: {category_filter}, Strings: {string_filter}, Root: {root_filter}")
    
    # Store recent searches in session
    if query and len(query) > 1:
        recent_searches = request.session.get('recent_searches', [])
        # Add to recent searches if not already there
        if query not in recent_searches:
            recent_searches.insert(0, query)
            # Keep only the latest 5 searches
            recent_searches = recent_searches[:5]
            request.session['recent_searches'] = recent_searches
    
    # If no query, return empty results
    if not query:
        logger.debug("[SEARCH_JSON] No query provided, returning empty results.")
        return JsonResponse({
            'query': '',
            'total_results': 0,
            'scale_results': [],
            'arpeggio_results': [],
            'chord_results': []
        })
    
    # Search logic - same as search_view but returns JSON
    scale_results = []
    arpeggio_results = []
    chord_results = []
    
    # Split query into potential note and type components
    query_parts = query.split(' ', 1)
    root_query = query_parts[0] if query_parts else ''
    type_query = query_parts[1] if len(query_parts) > 1 else ''
    
    # Common musical terms for types that might be searched
    musical_terms = ['major', 'minor', 'diminished', 'augmented', 'dominant', 
                     'suspended', 'pentatonic', 'blues', 'lydian', 'dorian', 
                     'phrygian', 'mixolydian', 'locrian', 'ionian', 'aeolian']
    
    # If the query has multiple parts, try to identify root note and type
    if type_query:
        logger.debug(f"[SEARCH_JSON] Searching by note '{root_query}' and type '{type_query}'")
        # Look for exact matches with note and type
        scales, arpeggios, chords = search_by_note_and_type(root_query, type_query)
        scale_results.extend(scales)
        arpeggio_results.extend(arpeggios)
        chord_results.extend(chords)
    else:
        # If single term, check if it's a common musical term (like "minor")
        if query.lower() in musical_terms:
            logger.debug(f"[SEARCH_JSON] Query '{query}' is a musical term, searching by type only.")
            # Search by type only
            scales, arpeggios, chords = search_by_type_only(query)
            scale_results.extend(scales)
            arpeggio_results.extend(arpeggios)
            chord_results.extend(chords)
        else:
            logger.debug(f"[SEARCH_JSON] Query '{query}' is not a musical term, searching by note and type separately.")
            # Try to match the single term as a note or as a type
            note_scales, note_arpeggios, note_chords = search_by_note_only(query)
            type_scales, type_arpeggios, type_chords = search_by_type_only(query)
            
            scale_results.extend(note_scales)
            scale_results.extend(type_scales)
            arpeggio_results.extend(note_arpeggios)
            arpeggio_results.extend(type_arpeggios)
            chord_results.extend(note_chords)
            chord_results.extend(type_chords)
    
    # If a category filter is specified, only return those results
    if category_filter:
        logger.debug(f"[SEARCH_JSON] Applying category filter: {category_filter}")
        if category_filter == 'scales':
            arpeggio_results = []
            chord_results = []
        elif category_filter == 'arpeggios':
            scale_results = []
            chord_results = []
        elif category_filter == 'chords':
            scale_results = []
            arpeggio_results = []
    
    # Remove duplicates before preparing JSON
    scale_results = list({item['url']: item for item in scale_results}.values())
    arpeggio_results = list({item['url']: item for item in arpeggio_results}.values())
    chord_results = list({item['url']: item for item in chord_results}.values())

    # Prepare JSON response
    scale_result_data = []
    for item in scale_results:
        scale_result_data.append({
            'note_name': item.get('note_name', ''),
            'description': item.get('description', ''),
            'intervals': item.get('intervals', ''),
            'url': item.get('url', '')
        })
    
    arpeggio_result_data = []
    for item in arpeggio_results:
        arpeggio_result_data.append({
            'note_name': item.get('note_name', ''),
            'description': item.get('description', ''),
            'intervals': item.get('intervals', ''),
            'url': item.get('url', '')
        })
    
    chord_result_data = []
    for item in chord_results:
        chord_result_data.append({
            'note_name': item.get('note_name', ''),
            'description': item.get('description', ''),
            'intervals': item.get('intervals', ''),
            'url': item.get('url', '')
        })
    
    # Count total results
    total_results = len(scale_result_data) + len(arpeggio_result_data) + len(chord_result_data)
    logger.debug(f"[SEARCH_JSON] Found {len(scale_result_data)} scales, {len(arpeggio_result_data)} arpeggios, {len(chord_result_data)} chords. Total: {total_results}")
    
    # Return JSON response
    return JsonResponse({
        'query': query,
        'total_results': total_results,
        'scale_results': scale_result_data,
        'arpeggio_results': arpeggio_result_data,
        'chord_results': chord_result_data,
    })

def search_by_note_and_type(note_query, type_query):
    """
    Search for matches where both note and type are specified.
    """
    logger.debug(f"[search_by_note_and_type] Searching for note: '{note_query}', type: '{type_query}'")
    scale_results = []
    arpeggio_results = []
    chord_results = []
    
    # Search for scales
    try:
        # Find matching root notes
        roots = Root.objects.filter(Q(name__icontains=note_query))
        
        for root in roots:
            # Find matching types
            types = NotesCategory.objects.filter(Q(category_name__icontains=type_query)) # Use category_name
            
            for note_type in types:
                # Check if this combination exists as a scale
                scale = Notes.objects.filter(tonal_root=root.id, category_id=note_type.id).first() # Use category_id
                
                if scale:
                    note_name = f"{root.name} {note_type.category_name}" # Use category_name
                    
                    # Build the URL for the scale
                    url = reverse('fretboard') + f'?models_select={note_type.id}&notes_options_select={scale.id}&root={root.id}'
                    
                    scale_results.append({
                        'note_name': note_name,
                        'description': note_type.category_name, # Use category_name
                        'intervals': scale.intervals if scale else '', # Get intervals from Notes object
                        'url': url
                    })
    except Exception as e:
        logger.error(f"[search_by_note_and_type] Error in scale search: {e}\n{traceback.format_exc()}")
    
    # Search for arpeggios (similar logic as scales)
    try:
        roots = Root.objects.filter(Q(name__icontains=note_query))
        
        for root in roots:
            # Find arpeggio types
            types = NotesCategory.objects.filter(Q(category_name__icontains=type_query), Q(category_name='arpeggio')) # Filter by category_name='arpeggio'
            
            for note_type in types:
                # Check if this combination exists as a arpeggio
                arpeggio = Notes.objects.filter(tonal_root=root.id, category_id=note_type.id).first() # Use category_id
                
                if arpeggio:
                    note_name = f"{root.name} {note_type.category_name}" # Use category_name
                    
                    # Build the URL for the arpeggio
                    url = reverse('fretboard') + f'?models_select={note_type.id}&notes_options_select={arpeggio.id}&root={root.id}'
                    
                    arpeggio_results.append({
                        'note_name': note_name,
                        'description': note_type.category_name, # Use category_name
                        'intervals': arpeggio.intervals if arpeggio else '', # Get intervals from Notes object
                        'url': url
                    })
    except Exception as e:
        logger.error(f"[search_by_note_and_type] Error in arpeggio search: {e}\n{traceback.format_exc()}")
    
    # Search for chords
    try:
        roots = Root.objects.filter(Q(name__icontains=note_query))
        
        for root in roots:
            # Find matching chord types
            chord_matches = ChordNotes.objects.filter(Q(type_name__icontains=type_query)) # Use type_name instead of non-existent chord_type
            
            for chord_match in chord_matches:
                chord_name = f"{root.name}{chord_match.type_name}" # Use type_name
                
                # Build the URL for the chord
                url = reverse('fretboard') + f'?models_select=3&notes_options_select={chord_match.id}'
                
                chord_results.append({
                    'note_name': chord_name,
                    'description': chord_match.chord_name,
                    'intervals': chord_match.chord_formula,
                    'url': url
                })
    except Exception as e:
        logger.error(f"[search_by_note_and_type] Error in chord search: {e}\n{traceback.format_exc()}")
    
    logger.debug(f"[search_by_note_and_type] Found {len(scale_results)} scales, {len(arpeggio_results)} arpeggios, {len(chord_results)} chords.")
    return scale_results, arpeggio_results, chord_results

def search_by_note_only(note_query):
    """
    Search for matches where only the note is specified.
    """
    logger.debug(f"[search_by_note_only] Searching for note: '{note_query}'")
    scale_results = []
    arpeggio_results = []
    chord_results = []
    
    try:
        # Find matching root notes
        roots = Root.objects.filter(Q(name__icontains=note_query))
        
        for root in roots:
            # For scales - get common scales for this root
            scale_types = NotesCategory.objects.filter(category_name='scale')[:5]  # Filter by category_name
            
            for scale_type in scale_types: # scale_type is a NotesCategory
                # Find the specific Notes instance for this root and category
                scale_note = Notes.objects.filter(tonal_root=root.id, category_id=scale_type.id).first() # Use category_id
                if scale_note:
                    note_name = f"{root.name} {scale_type.category_name}" # Use category_name
                    
                    # Build the URL using the Notes object ID
                    url = reverse('fretboard') + f'?models_select={scale_type.id}&notes_options_select={scale_note.id}&root={root.id}'
                    
                    scale_results.append({
                        'note_name': note_name,
                        'description': scale_type.category_name, # Use category_name
                        'intervals': scale_note.intervals, # Get intervals from Notes object
                        'url': url
                })
            
            # For arpeggios - get common arpeggios for this root
            arpeggio_types = NotesCategory.objects.filter(category_name='arpeggio')[:3]  # Filter by category_name
            
            for arpeggio_type in arpeggio_types: # arpeggio_type is a NotesCategory
                # Find the specific Notes instance for this root and category
                arpeggio_note = Notes.objects.filter(tonal_root=root.id, category_id=arpeggio_type.id).first() # Use category_id
                if arpeggio_note:
                    note_name = f"{root.name} {arpeggio_type.category_name}" # Use category_name
                    
                    # Build the URL using the Notes object ID
                    url = reverse('fretboard') + f'?models_select={arpeggio_type.id}&notes_options_select={arpeggio_note.id}&root={root.id}'
                    
                    arpeggio_results.append({
                        'note_name': note_name,
                        'description': arpeggio_type.category_name, # Use category_name
                        'intervals': arpeggio_note.intervals, # Get intervals from Notes object
                        'url': url
                })
            
            # For chords - get common chords for this root
            chord_types = ChordNotes.objects.all()[:5]  # Limit to 5 common chord types
            
            for chord_type in chord_types:
                chord_name = f"{root.name}{chord_type.type_name}" # Use type_name
                
                # Build the URL for the chord
                url = reverse('fretboard') + f'?models_select=3&notes_options_select={chord_type.id}'
                
                chord_results.append({
                    'note_name': chord_name,
                    'description': chord_type.chord_name,
                    'intervals': chord_type.chord_formula,
                    'url': url
                })
    except Exception as e:
        logger.error(f"[search_by_note_only] Error: {e}\n{traceback.format_exc()}")
    
    logger.debug(f"[search_by_note_only] Found {len(scale_results)} scales, {len(arpeggio_results)} arpeggios, {len(chord_results)} chords.")
    return scale_results, arpeggio_results, chord_results

def search_by_type_only(type_query):
    """
    Search for matches where only the type is specified (e.g., "minor").
    """
    logger.debug(f"[search_by_type_only] Searching for type: '{type_query}'")
    scale_results = []
    arpeggio_results = []
    chord_results = []
    
    try:
        # Find matching scale types
        scale_types = NotesCategory.objects.filter(
            Q(category_name__icontains=type_query) # Use category_name
        ).filter(category_name='scale') # Filter by category_name
        
        common_roots = Root.objects.filter(name__in=['C', 'A', 'G', 'E', 'D'])  # Common root notes
        
        for scale_type in scale_types:
            for root in common_roots[:3]:  # Limit to 3 common roots
                # Find the specific Notes instance for this root and category
                scale_note = Notes.objects.filter(tonal_root=root.id, category_id=scale_type.id).first() # Use category_id
                if scale_note:
                    note_name = f"{root.name} {scale_type.category_name}" # Use category_name
                    
                    # Build the URL using the Notes object ID
                    url = reverse('fretboard') + f'?models_select={scale_type.id}&notes_options_select={scale_note.id}&root={root.id}'
                    
                    scale_results.append({
                        'note_name': note_name,
                        'description': scale_type.category_name, # Use category_name
                        'intervals': scale_note.intervals, # Get intervals from Notes object
                        'url': url
                })
        
        # Find matching arpeggio types
        arpeggio_types = NotesCategory.objects.filter(
            Q(category_name__icontains=type_query) # Use category_name
        ).filter(category_name='arpeggio') # Filter by category_name
        
        for arpeggio_type in arpeggio_types:
            for root in common_roots[:2]:  # Limit to 2 common roots
                # Find the specific Notes instance for this root and category
                arpeggio_note = Notes.objects.filter(tonal_root=root.id, category_id=arpeggio_type.id).first() # Use category_id
                if arpeggio_note:
                    note_name = f"{root.name} {arpeggio_type.category_name}" # Use category_name
                    
                    # Build the URL using the Notes object ID
                    url = reverse('fretboard') + f'?models_select={arpeggio_type.id}&notes_options_select={arpeggio_note.id}&root={root.id}'
                    
                    arpeggio_results.append({
                        'note_name': note_name,
                        'description': arpeggio_type.category_name, # Use category_name
                        'intervals': arpeggio_note.intervals, # Get intervals from Notes object
                        'url': url
                    })
        
        # Find matching chord types
        chord_types = ChordNotes.objects.filter(
            Q(type_name__icontains=type_query) | # Use type_name instead of non-existent chord_type
            Q(chord_name__icontains=type_query)
        )
        
        for chord_type in chord_types:
            for root in common_roots[:3]:  # Limit to 3 common roots
                chord_name = f"{root.name}{chord_type.type_name}" # Use type_name
                
                # Build the URL for the chord
                url = reverse('fretboard') + f'?models_select=3&notes_options_select={chord_type.id}'
                
                chord_results.append({
                    'note_name': chord_name,
                    'description': chord_type.chord_name,
                    'intervals': chord_type.chord_formula,
                    'url': url
                })
    except Exception as e:
        logger.error(f"[search_by_type_only] Error: {e}\n{traceback.format_exc()}")
    
    logger.debug(f"[search_by_type_only] Found {len(scale_results)} scales, {len(arpeggio_results)} arpeggios, {len(chord_results)} chords.")
    return scale_results, arpeggio_results, chord_results

def search_autocomplete(request):
    """
    API endpoint that returns autocomplete suggestions for search
    """
    query = request.GET.get('q', '').strip()
    logger.debug(f"[search_autocomplete] Received query: '{query}'")
    results = []
    
    if len(query) < 2:
        logger.debug("[search_autocomplete] Query too short, returning empty results.")
        return JsonResponse({'results': results})
    
    # Normalize query
    normalized_query = normalize_search_term(query)
    
    # Get scales
    try:
        scales_category = NotesCategory.objects.get(category_name__icontains='scale')
        scale_results = Notes.objects.filter(
            category=scales_category.id,
            note_name__icontains=normalized_query
        ).order_by('ordering')[:5]
        
        logger.debug(f"[search_autocomplete] Found {scale_results.count()} matching scales.")
        for scale in scale_results:
            results.append({
                'name': scale.note_name,
                'type': 'scale',
                'url': reverse('fretboard') + f'?models_select={scales_category.id}&notes_options_select={scale.id}'
            })
    except NotesCategory.DoesNotExist:
        logger.warning("[search_autocomplete] Scale category not found in NotesCategory.")
        pass # Category not found
    except Exception as e:
        logger.error(f"[search_autocomplete] Error searching scales: {e}\n{traceback.format_exc()}")
    
    # Get arpeggios
    try:
        arpeggio_category = NotesCategory.objects.get(category_name__icontains='arpeggio')
        arpeggio_results = Notes.objects.filter(
            category=arpeggio_category.id,
            note_name__icontains=normalized_query
        ).order_by('ordering')[:5]
        
        logger.debug(f"[search_autocomplete] Found {arpeggio_results.count()} matching arpeggios.")
        for arpeggio in arpeggio_results:
            results.append({
                'name': arpeggio.note_name,
                'type': 'arpeggio',
                'url': reverse('fretboard') + f'?models_select={arpeggio_category.id}&notes_options_select={arpeggio.id}'
            })
    except NotesCategory.DoesNotExist:
        logger.warning("[search_autocomplete] Arpeggio category not found in NotesCategory.")
        pass # Category not found
    except Exception as e:
        logger.error(f"[search_autocomplete] Error searching arpeggios: {e}\n{traceback.format_exc()}")
    
    # Get chords
    try:
        chord_results = ChordNotes.objects.filter(
            chord_name__icontains=normalized_query
        ).distinct().order_by('chord_name')[:5]
        logger.debug(f"[search_autocomplete] Found {chord_results.count()} matching chords.")
        
        for chord in chord_results:
            chord_root = chord.root if hasattr(chord, 'root') and chord.root else chord.chord_name.split()[0]
            results.append({
                'name': chord.chord_name,
                'type': 'chord',
                'url': (
                    reverse('chordbase') +
                    f'?root_note_choice={chord_root}&chord_type_choice={chord.chord_name.replace(chord_root, "").strip()}'
                )
            })
    except Exception as e:
        logger.error(f"[search_autocomplete] Error searching chords: {e}\n{traceback.format_exc()}")
    
    # Get root notes
    try:
        root_results = Root.objects.filter(name__icontains=normalized_query)[:5]
        logger.debug(f"[search_autocomplete] Found {root_results.count()} matching roots.")
        
        for root in root_results:
            results.append({
                'name': root.name,
                'type': 'root',
                'url': reverse('search') + f'?q={root.name}'
            })
    except Exception as e:
        logger.error(f"[search_autocomplete] Error searching roots: {e}\n{traceback.format_exc()}")

    # Remove duplicates by name before returning
    unique_results = []
    seen_names = set()
    for result in results:
        if result['name'] not in seen_names:
            unique_results.append(result)
            seen_names.add(result['name'])
            
    # Limit results
    unique_results = unique_results[:10] # Limit overall results
    logger.debug(f"[search_autocomplete] Returning {len(unique_results)} unique results.")
    
    return JsonResponse({'results': unique_results})

def get_string_count_from_range(range_str):
    """
    Determine the number of strings from a range string
    """
    if not range_str:
        return 6  # Default
    
    if 'highA' in range_str:
        return 8  # 8-string (with high A)
    elif 'lowB' in range_str:
        return 7  # 7-string
    else:
        return 6  # 6-string

def get_intervals_from_notes(note_obj):
    """
    Get a formatted string of intervals from a Notes object
    """
    if not hasattr(note_obj, 'notes_set'):
        return ""
    
    try:
        notes_set = note_obj.notes_set
        if notes_set:
            return ", ".join(notes_set.split())
    except (AttributeError, TypeError):
        pass
        
    return ""
