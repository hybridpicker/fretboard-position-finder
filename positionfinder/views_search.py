import json
import logging
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Root, NotesCategory, Notes
from .models_chords import ChordNotes, ChordPosition

# Scale is an alias for Notes with scale category for testing compatibility
Scale = Notes
from .views_helpers import get_common_context
from .search_utils import parse_query, best_fuzzy_match, resolve_root, NOTES as NOTE_NAMES, ROOT_NAME_TO_ID

# Configure logging
logger = logging.getLogger(__name__)

def log_debug_info(message, data=None):
    """Helper to output debug information consistently"""
    if data:
        logger.debug(f"DEBUG: {message}")
        logger.debug(f"DATA: {json.dumps(data) if isinstance(data, (dict, list)) else data}")
    else:
        logger.debug(f"DEBUG: {message}")

def search_json(request):
    """
    JSON API endpoint for search results across chords, scales, and arpeggios.
    Returns results in a standardized JSON format for API consumers.
    """
    try:
        # Get search parameters
        query = request.GET.get('q', '')
        search_type = request.GET.get('search_type', 'all')

        logger.debug(f"[DEBUG] Raw query: {query}")
        logger.debug(f"[DEBUG] Search type: {search_type}")

        # Format conversion for empty strings to None for proper filtering
        if not query.strip():
            logger.debug("[DEBUG] Empty query string received. Returning empty results.")
            return JsonResponse({
                'query': '',
                'total_results': 0,
                'chord_results': [],
                'scale_results': [],
                'arpeggio_results': []
            })

        # --- Enhanced parsing and normalization ---
        note, type_, quality, position, inversion = parse_query(query)
        logger.debug(f"[DEBUG] Parsed query -> note: {note}, type: {type_}, quality: {quality}, position: {position}, inversion: {inversion}")
        # Compose normalized query for downstream search functions
        normalized_query = f"{note} {quality}".strip()
        logger.debug(f"[DEBUG] Normalized query for search: '{normalized_query}'")

        results = {
            'chord_results': [],
            'scale_results': [],
            'arpeggio_results': []
        }

        # Only run the search for the type indicated by parse_query (or explicit search_type)
        if search_type == 'chords' or (search_type == 'all' and type_ == 'chord'):
            chord_results = search_chords(query)
            logger.debug(f"[DEBUG] Chord queryset count: {len(chord_results)}")
            results['chord_results'] = chord_results
            logger.debug(f"[DEBUG] Processed chord results: {results['chord_results']}")
        if search_type == 'scales' or (search_type == 'all' and type_ == 'scale'):
            scale_results = search_scales(normalized_query)
            logger.debug(f"[DEBUG] Scale queryset count: {len(scale_results)}")
            # Patch: Generate URLs using the blueprint scale id (`notes_options_select`) for dynamic scales
            for item in scale_results:
                if item.get('id') is None and note and quality:
                    from .search_utils import get_root_id_from_name
                    root_id = get_root_id_from_name(note)
                    # Look up blueprint scale record for this quality
                    blueprint = Notes.objects.filter(
                        category__category_name__icontains='scale',
                        note_name__icontains=quality
                    ).first()
                    notes_options_select = blueprint.pk if blueprint else ''
                    item['url'] = f"/?root={root_id}&models_select=1&notes_options_select={notes_options_select}&position_select=0"
            results['scale_results'] = scale_results
            logger.debug(f"[DEBUG] Processed scale results: {results['scale_results']}")
        if search_type == 'arpeggios' or (search_type == 'all' and type_ == 'arpeggio'):
            # Pass parsed components directly
            arpeggio_results = search_arpeggios(note=note, quality=quality, type_=type_)
            logger.debug(f"[DEBUG] Arpeggio queryset count: {len(arpeggio_results)}")
            results['arpeggio_results'] = arpeggio_results
            logger.debug(f"[DEBUG] Processed arpeggio results: {results['arpeggio_results']}")

        # Calculate total results
        total_results = (
            len(results['chord_results']) + 
            len(results['scale_results']) + 
            len(results['arpeggio_results'])
        )
        logger.debug(f"[DEBUG] Total results: {total_results}")

        # Return formatted response
        logger.debug(f"[DEBUG] Final JSON response: {{'query': query, 'total_results': total_results, ...}}")
        return JsonResponse({
            'query': query,
            'total_results': total_results,
            'chord_results': results['chord_results'],
            'scale_results': results['scale_results'],
            'arpeggio_results': results['arpeggio_results']
        })
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[ERROR] Exception in search_json: {e}\n{tb}")
        return JsonResponse({'error': str(e), 'traceback': tb}, status=500)

def unified_search_view(request):
    """
    A unified search view that can search across chords, scales, and arpeggios
    """
    logger.debug("\n" + "="*80)
    logger.debug("UNIFIED SEARCH INITIATED")
    logger.debug(f"REQUEST METHOD: {request.method}")
    logger.debug(f"REQUEST PATH: {request.path}")
    logger.debug("="*80)
    
    # Get search parameters
    search_query = request.GET.get('search_query', '')
    search_type = request.GET.get('search_type', 'all')  # all, chords, scales, or arpeggios
    logger.debug(f"[DEBUG] search_query: {search_query}")
    logger.debug(f"[DEBUG] search_type: {search_type}")
    
    # Format conversion for empty strings to None for proper filtering
    if not search_query.strip():
        logger.debug("[DEBUG] Empty search_query string received. Returning empty results.")
        search_query = None
    
    # Parse and normalize the query using parse_query
    note, type_, quality, position, inversion = parse_query(search_query or "")
    logger.debug(f"[DEBUG] Parsed query -> note: {note}, type: {type_}, quality: {quality}, position: {position}, inversion: {inversion}")
    normalized_query = f"{note} {quality}".strip()
    logger.debug(f"[DEBUG] Normalized query for search: '{normalized_query}'")

    results = {
        'chords': [],
        'scales': [],
        'arpeggios': []
    }
    
    total_count = 0
    
    # Search for chords if requested
    if search_type in ['all', 'chords'] and search_query:
        chord_results = search_chords(search_query)
        results['chords'] = chord_results
        total_count += len(chord_results)
        log_debug_info(f"Unified Search: Found {len(chord_results)} chords", chord_results[:5]) # Log first 5 results
    
    # Search for scales if requested
    if search_type in ['all', 'scales'] and search_query:
        scale_results = search_scales(search_query)
        results['scales'] = scale_results
        total_count += len(scale_results)
        log_debug_info(f"Unified Search: Found {len(scale_results)} scales", scale_results[:5]) # Log first 5 results
    
    # Search for arpeggios if requested - FIXED: Pass parsed components instead of raw query
    if search_type in ['all', 'arpeggios'] and search_query:
        arpeggio_results = search_arpeggios(note=note, quality=quality, type_=type_)
        results['arpeggios'] = arpeggio_results
        total_count += len(arpeggio_results)
        log_debug_info(f"Unified Search: Found {len(arpeggio_results)} arpeggios", arpeggio_results[:5]) # Log first 5 results
    
    # Check if JSON response is requested
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        log_debug_info("Unified Search: Returning JSON response", {'total_count': total_count, 'search_query': search_query, 'search_type': search_type})
        return JsonResponse({
            'results': results,
            'total_count': total_count,
            'search_query': search_query or '',
            'search_type': search_type
        })
    
    # Prepare context for template rendering
    context = {
        'search_query': search_query or '',
        'search_type': search_type,
        'results': results,
        'total_count': total_count,
    }
    
    # Add common context
    common_context = get_common_context(request)
    context.update(common_context)
    
    logger.debug(f"[DEBUG] Results summary: {{'total_count': total_count, 'search_query': search_query, 'search_type': search_type, 'results': results}}")
    log_debug_info("Unified Search: Rendering HTML template", {'total_count': total_count, 'search_query': search_query, 'search_type': search_type})
    return render(request, 'search/unified_search.html', context)

def search_chords(search_query):
    """Search for chords matching the query, supporting combined type and position queries like 'Major7 V2' and common synonyms."""
    logger.debug(f"Entering search_chords with query: '{search_query}'")
    try:
        from .search_utils import parse_query, best_fuzzy_match
        note, _, quality, _, _ = parse_query(search_query)
        chord_options = list(ChordNotes.objects.values_list('chord_name', flat=True).distinct())
        type_options = list(ChordNotes.objects.values_list('type_name', flat=True).distinct())

        # Map parsed quality to canonical chord_name in DB
        CHORD_QUALITY_MAP = {
            'maj7': 'Major 7',
            'major7': 'Major 7',
            'min7': 'Minor 7',
            'm7': 'Minor 7',
            'minor7': 'Minor 7',
            'dim7': 'Diminished 7',
            'm7b5': 'Minor 7b5',
            'dom7': 'Dominant 7',
            'dominant 7': 'Dominant 7',
            'major': 'Major',
            'minor': 'Minor',
            'dim': 'Diminished',
            'diminished': 'Diminished',
            'aug': 'Augmented',
            'augmented': 'Augmented',
            # Add more as needed
        }
        chord_name = CHORD_QUALITY_MAP.get(quality.lower(), quality.title() if quality else None)
        logger.debug(f"search_chords: Parsed quality '{quality}' mapped to chord_name '{chord_name}'")
        # Try to match both chord_name and type_name
        matched_chord = best_fuzzy_match(chord_name or '', chord_options, cutoff=0.7, case_sensitive=False) if chord_name else None
        matched_type = best_fuzzy_match(search_query, type_options, cutoff=0.7, case_sensitive=False)
        found = False
        if matched_chord and matched_type:
            for cn in [matched_chord]:
                for tn in [matched_type]:
                    matches = ChordNotes.objects.filter(Q(chord_name__icontains=cn) & Q(type_name__icontains=tn))
                    if matches.exists():
                        found = True
                        logger.debug(f"search_chords: Found {len(matches)} matches for chord_name='{cn}', type_name='{tn}'.")
                        filtered = matches.filter(tonal_root=ROOT_NAME_TO_ID.get(note)) if note else matches
                        return process_chord_results(filtered, root_note=note)
        elif matched_chord:
            for cn in [matched_chord]:
                matches = ChordNotes.objects.filter(chord_name__icontains=cn)
                if matches.exists():
                    found = True
                    logger.debug(f"search_chords: Found {len(matches)} matches for chord_name='{cn}'.")
                    filtered = matches.filter(tonal_root=ROOT_NAME_TO_ID.get(note)) if note else matches
                    return process_chord_results(filtered, root_note=note)
        elif matched_type:
            for tn in [matched_type]:
                matches = ChordNotes.objects.filter(type_name__icontains=tn)
                if matches.exists():
                    found = True
                    logger.debug(f"search_chords: Found {len(matches)} matches for type_name='{tn}'.")
                    filtered = matches.filter(tonal_root=ROOT_NAME_TO_ID.get(note)) if note else matches
                    return process_chord_results(filtered, root_note=note)
        if not found:
            logger.debug(f"search_chords: No matches found for chord_name='{matched_chord}', type_name='{matched_type}', including variants.")
            return []
    except Exception as e:
        logger.error(f"Error searching chords: {str(e)}")
        logger.error(traceback.format_exc())
        logger.debug(f"search_chords: Error occurred - {str(e)}")
        return []

def process_chord_results(queryset, root_note=None):
    """Process chord query results into a standardized format"""
    logger.debug(f"Entering process_chord_results with {len(queryset)} items.")
    chords_to_process = list(queryset)
    # Robust filtering: Try tonal_root, then fallback to name prefix, else skip filtering
    if root_note:
        root_id = ROOT_NAME_TO_ID.get(root_note)
        filtered = [ch for ch in chords_to_process if getattr(ch, 'tonal_root', None) == root_id]
        logger.debug(f"Filtered by tonal_root ({root_note} -> {root_id}): {len(filtered)} matches.")
        if filtered:
            chords_to_process = filtered
        else:
            # Fallback: match by chord_name prefix (e.g., 'A Major 7')
            fallback = [ch for ch in chords_to_process if str(ch.chord_name).lower().startswith(root_note.lower())]
            logger.debug(f"Fallback by chord_name prefix '{root_note}': {len(fallback)} matches.")
            if fallback:
                chords_to_process = fallback
            else:
                logger.debug(f"No matches for tonal_root or chord_name prefix, skipping root filter.")
    # Now prioritize e-string voicings among filtered chords
    prioritized = [ch for ch in chords_to_process if 'e' in getattr(ch, 'range', '') and 'E' not in getattr(ch, 'range', '')]
    if prioritized:
        logger.debug(f"Prioritized e-string voicings: {len(prioritized)} matches.")
        chords_to_process = prioritized
    processed_results = []
    for chord in chords_to_process:
        positions = list(ChordPosition.objects.filter(notes_name=chord).values_list('inversion_order', flat=True))
        notes = []
        for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 'sixth_note']:
            note_value = getattr(chord, note_attr, None)
            if note_value is not None:
                notes.append(note_value)
        # Calculate intervals if not present
        intervals = []
        if hasattr(chord, 'intervals') and chord.intervals:
            intervals = chord.intervals
        else:
            if notes and len(notes) > 1:
                root_pitch = notes[0]
                intervals = [(n - root_pitch) % 12 for n in notes]
        # Compose name with root if not present
        name = chord.chord_name
        if root_note and not name.lower().startswith(root_note.lower()):
            name = f"{root_note} {name}"
        url = f"/?root={ROOT_NAME_TO_ID.get(root_note, getattr(chord, 'tonal_root', 1))}&models_select=3&type_options_select={chord.type_name}&chords_options_select={chord.chord_name}&note_range={chord.range}&position_select=Root+Position"
        chord_result = {
            'id': chord.id,
            'name': name,
            'type': chord.type_name,
            'category': getattr(chord.category, 'category_name', None) if hasattr(chord, 'category') else None,
            'positions': positions,
            'notes': notes,
            'intervals': intervals,
            'url': url
        }
        logger.debug(f"process_chord_results: Processed chord ID {chord.id}", chord_result)
        processed_results.append(chord_result)
    logger.debug(f"Exiting process_chord_results with {len(processed_results)} processed items.")
    return processed_results

def search_scales(search_query):
    """Search for scales by root and scale type (quality)."""
    logger.debug(f"Entering search_scales with query: '{search_query}'")
    # Parse canonical note and quality
    note, _, quality, _, _ = parse_query(search_query)
    from .search_utils import resolve_root
    root_obj = resolve_root(note)
    logger.debug(f"search_scales: Resolved root '{note}' to DB object: {root_obj}")
    if not root_obj:
        logger.debug(f"search_scales: No valid root found for '{note}', aborting search.")
        return []
    try:
        qs = Notes.objects.filter(category__category_name__icontains='scale')
        if search_query.isdigit():
            qs = qs.filter(pk=int(search_query))
        else:
            qs = qs.filter(tonal_root=ROOT_NAME_TO_ID.get(note))
            qs = qs.filter(note_name__icontains=quality)
        logger.debug(f"search_scales: Final queryset count: {qs.count()}")
        if qs.exists():
            results = process_scale_results(qs, user_note=note, user_quality=quality)
            return results
        logger.debug(f"search_scales: No results found for '{search_query}'.")
        return []
    except Exception as e:
        logger.error(f"Error searching scales: {str(e)}")
        logger.error(traceback.format_exc())
        logger.debug(f"search_scales: Error occurred - {str(e)}")
        return []

def process_scale_results(queryset, user_note=None, user_quality=None):
    """Process scale query results into a standardized format, preserving user note and quality for naming if possible."""
    logger.debug(f"Entering process_scale_results with {len(queryset)} items.")
    processed_results = []
    for scale in queryset:
        notes = []
        for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 
                         'sixth_note', 'seventh_note', 'eighth_note', 'ninth_note']:
            if hasattr(scale, note_attr):
                value = getattr(scale, note_attr, None)
                if value is not None:
                    notes.append(value)
        # Calculate intervals if not present
        intervals = []
        if hasattr(scale, 'intervals') and scale.intervals:
            intervals = scale.intervals
        else:
            if notes and len(notes) > 1:
                root_pitch = notes[0]
                intervals = [(n - root_pitch) % 12 for n in notes]
        name = scale.note_name
        if user_note and not name.lower().startswith(user_note.lower()):
            name = f"{user_note} {name}"
        url = f"/?root={getattr(scale, 'tonal_root', 1)}&models_select=1&notes_options_select={scale.id}&position_select=0"
        scale_result = {
            'id': scale.id,
            'name': name,
            'type': getattr(scale.category, 'category_name', '') if hasattr(scale, 'category') else '',
            'notes': notes,
            'intervals': intervals,
            'url': url
        }
        logger.debug(f"process_scale_results: Processed scale ID {scale.id}", scale_result)
        processed_results.append(scale_result)
    logger.debug(f"Exiting process_scale_results with {len(processed_results)} processed items.")
    return processed_results

def search_arpeggios(note=None, quality=None, type_=None):
    """Search for arpeggios using parsed components: note, quality, and type."""
    logger.debug(f"Entering search_arpeggios with note='{note}', quality='{quality}', type_='{type_}'")
    try:
        # Need best_fuzzy_match here if using it for quality
        from .search_utils import best_fuzzy_match
        from .models import Notes, NotesCategory, Root

        # Start with base arpeggio query - Use Notes model with arpeggio category
        arpeggio_category = NotesCategory.objects.filter(category_name__icontains='arpeggio').first()
        
        if not arpeggio_category:
            logger.error("No arpeggio category found in NotesCategory model.")
            return []
            
        qs = Notes.objects.filter(category=arpeggio_category)
        
        # Store the root information for later use in result processing
        # but don't filter by it since arpeggios are stored as templates with tonal_root=0
        root_obj = None
        root_id = None
        
        if note:
            # Get root object for later URL generation, but don't filter query by it
            root_obj = Root.objects.filter(name__iexact=note).first()
            if not root_obj:
                # Try alternate lookup
                from .search_utils import ROOT_NAME_TO_ID
                root_id = ROOT_NAME_TO_ID.get(note)
                if root_id:
                    root_obj = Root.objects.filter(id=root_id).first()
            
            if root_obj:
                logger.debug(f"Found root_obj for '{note}': ID={root_obj.id}, pitch={root_obj.pitch}")
                # For arpeggios, we might want to filter by tonal_root if they have specific root assignments
                # qs = qs.filter(tonal_root=root_obj.pitch)
            else:
                logger.warning(f"Could not find root for note: {note}")

        # If quality is provided, find arpeggios that match this quality
        if quality:
            # Define quality mappings to improve search precision
            quality_terms = {
                'minor': ['Minor', 'minor', 'Min', 'm'],
                'major': ['Major', 'major', 'Maj', 'M'],
                'diminished': ['Diminished', 'diminished', 'Dim', 'dim', 'o'],
                'augmented': ['Augmented', 'augmented', 'Aug', 'aug', '+'],
                'dominant': ['Dominant', 'dominant', 'Dom', 'dom']
            }
            
            # Find which quality group the search term belongs to
            search_quality_group = None
            for group, terms in quality_terms.items():
                if quality.lower() in [t.lower() for t in terms]:
                    search_quality_group = group
                    break
            
            # Apply quality filtering with priority for exact matches
            quality_filters = Q()
            if search_quality_group:
                # Add exact match terms for the identified quality group
                for term in quality_terms.get(search_quality_group, []):
                    quality_filters |= Q(note_name__icontains=term)
                logger.debug(f"Applying quality filters for '{quality}': {quality_filters}")
                qs = qs.filter(quality_filters)
            else:
                # If quality doesn't match any known group, use it directly
                logger.debug(f"Applying direct quality filter for '{quality}'")
                qs = qs.filter(note_name__icontains=quality)
            
            # Sort results by relevance (exact matches first)
            # This ensures Minor arpeggios appear before Major when searching for "minor"
            if search_quality_group:
                results_list = list(qs)
                # Move exact matches to the front
                results_list.sort(key=lambda x: (search_quality_group.lower() not in x.note_name.lower()))
                # Convert back to a QuerySet-like list
                qs = results_list
        else:
            logger.debug("No quality provided, skipping quality filter.")

        # Handle pentatonic type if specified
        if type_ and type_.lower() == 'pentatonic':
            # If we've sorted, filter in Python
            if isinstance(qs, list):
                qs = [item for item in qs if 'pentatonic' in item.note_name.lower()]
            else:
                qs = qs.filter(note_name__icontains='pentatonic')

        logger.debug(f"search_arpeggios: Final queryset count before processing: {len(qs) if isinstance(qs, list) else qs.count()}")

        if qs:
            # Pass the root information to the processing function
            return process_arpeggio_results(qs, root_note=note, root_obj=root_obj, quality=quality)
        else:
            # If specific search yields no results, consider a broader fallback (optional)
            # For now, return empty if specific filters match nothing.
            logger.debug(f"search_arpeggios: No results found for note='{note}', quality='{quality}'.")
            return []

    except Exception as e:
        logger.error(f"Error searching arpeggios: {str(e)}")
        logger.error(traceback.format_exc())
        logger.debug(f"search_arpeggios: Error occurred - {str(e)}")
        return []

def process_arpeggio_results(queryset, root_note=None, root_obj=None, quality=None):
    """Process arpeggio query results into a standardized format"""
    # Handle both QuerySet and list objects
    count = len(queryset) if isinstance(queryset, list) else queryset.count()
    logger.debug(f"Process arpeggio results for {count} items, root_note={root_note}")
    
    results = []
    base_url = "/"
    from .models import Root
    
    for arpeggio in queryset:
        try:
            # Extract notes for this arpeggio 
            notes = []
            for i in range(1, 13):  # Assuming up to 12 notes
                note_attr = f'{"first" if i == 1 else "second" if i == 2 else "third" if i == 3 else "fourth" if i == 4 else "fifth" if i == 5 else "sixth" if i == 6 else "seventh" if i == 7 else "eigth" if i == 8 else "ninth" if i == 9 else "tenth" if i == 10 else "eleventh" if i == 11 else "twelth"}_note'
                note_value = getattr(arpeggio, note_attr, None)
                if note_value is not None:
                    notes.append(note_value)
                    
            # Calculate intervals if possible, else use empty list
            intervals = []
            if hasattr(arpeggio, 'intervals') and arpeggio.intervals:
                intervals = arpeggio.intervals
            else:
                # Try to infer intervals from notes if possible (e.g., relative to root)
                if notes and len(notes) > 1:
                    root_pitch = notes[0]
                    intervals = [(n - root_pitch) % 12 for n in notes]

            # Compose name with root if not present
            name = arpeggio.note_name
            if root_note and not name.lower().startswith(root_note.lower()):
                name = f"{root_note} {name}"
            
            # Get the root ID for URL generation
            root_id = None
            if root_obj:
                root_id = root_obj.id
            elif root_note:
                # Try to find root by name
                root_obj = Root.objects.filter(name__iexact=root_note).first()
                if root_obj:
                    root_id = root_obj.id
                else:
                    # Try lookup in mapping
                    from .search_utils import ROOT_NAME_TO_ID
                    root_id = ROOT_NAME_TO_ID.get(root_note)
            
            if not root_id:
                # Default to A if all else fails
                logger.warning(f"Could not find root ID for arpeggio {arpeggio.id}, using default ID 14")
                root_id = 14  # Default to A
            
            # Always set type to include 'Arpeggio'
            type_str = "Arpeggio"
            
            # Generate URL for this arpeggio - include models_select=2 for arpeggios
            # Use the specific arpeggio ID in the URL
            url_params = {
                'root': root_id,
                'models_select': 2,  # Code for arpeggios
                'notes_options_select': arpeggio.id,
                'position_select': 0
            }
            
            url = f"{base_url}?root={root_id}&models_select=2&notes_options_select={arpeggio.id}&position_select=0"
            
            results.append({
                'id': arpeggio.id,
                'name': name,
                'type': type_str,
                'notes': notes,
                'intervals': intervals,
                'url': url
            })
            
        except Exception as e:
            logger.error(f"Error processing arpeggio {getattr(arpeggio, 'id', 'unknown')}: {str(e)}")
            logger.error(traceback.format_exc())
    
    return results
