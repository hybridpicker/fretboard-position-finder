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
    
    # Search for arpeggios if requested
    if search_type in ['all', 'arpeggios'] and search_query:
        arpeggio_results = search_arpeggios(search_query)
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
        from .search_utils import parse_query
        note, _, quality, _, _ = parse_query(search_query)
        chord_options = list(ChordNotes.objects.values_list('chord_name', flat=True).distinct())
        type_options = list(ChordNotes.objects.values_list('type_name', flat=True).distinct())
        matched_chord = best_fuzzy_match(search_query, chord_options, cutoff=0.7, case_sensitive=False)
        matched_type = best_fuzzy_match(search_query, type_options, cutoff=0.7, case_sensitive=False)
        found = False
        if matched_chord and matched_type:
            for cn in [matched_chord]:
                for tn in [matched_type]:
                    matches = ChordNotes.objects.filter(Q(chord_name__icontains=cn) & Q(type_name__icontains=tn))
                    if matches.exists():
                        found = True
                        logger.debug(f"search_chords: Found {len(matches)} matches for chord_name='{cn}', type_name='{tn}'.")
                        # Filter for root note if present
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
    # Filter for correct root first, then prioritize e-string voicings
    chords_to_process = list(queryset)
    if root_note:
        root_id = ROOT_NAME_TO_ID.get(root_note)
        if root_id is not None:
            chords_to_process = [ch for ch in chords_to_process if getattr(ch, 'tonal_root', None) == root_id]
    # Now prioritize e-string voicings among filtered chords
    prioritized = [ch for ch in chords_to_process if 'e' in getattr(ch, 'range', '') and 'E' not in getattr(ch, 'range', '')]
    if prioritized:
        chords_to_process = prioritized
    processed_results = []
    for chord in chords_to_process:
        positions = list(ChordPosition.objects.filter(notes_name=chord).values_list('inversion_order', flat=True))
        notes = []
        for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 'sixth_note']:
            note_value = getattr(chord, note_attr, None)
            if note_value is not None:
                notes.append(note_value)
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
    quality_opts = list(Notes.objects.filter(category__category_name__icontains='scale').values_list('note_name', flat=True).distinct())
    db_qual = best_fuzzy_match(quality, quality_opts, cutoff=0.7, case_sensitive=False) or quality
    logger.debug(f"search_scales: db_qual='{db_qual}' (from quality='{quality}')")
    # Define intervals for dynamic scale generation, including modes and common scales
    intervals_map = {
        'minor pentatonic': [0, 3, 5, 7, 10],
        'major pentatonic': [0, 2, 4, 7, 9],
        'pentatonic': [0, 2, 4, 7, 9],
        'major': [0, 2, 4, 5, 7, 9, 11],         # Ionian
        'minor': [0, 2, 3, 5, 7, 8, 10],        # Aeolian
        'dorian': [0, 2, 3, 5, 7, 9, 10],       # Dorian mode
        'phrygian': [0, 1, 3, 5, 7, 8, 10],     # Phrygian
        'lydian': [0, 2, 4, 6, 7, 9, 11],       # Lydian
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],   # Mixolydian
        'aeolian': [0, 2, 3, 5, 7, 8, 10],      # Aeolian
        'locrian': [0, 1, 3, 5, 6, 8, 10],      # Locrian
        'harmonic minor': [0, 2, 3, 5, 7, 8, 11], # Harmonic Minor
        'harmonic major': [0, 2, 4, 5, 7, 8, 11], # Harmonic Major
        'melodic minor': [0, 2, 3, 5, 7, 9, 11]  # Melodic Minor
    }
    intervals = intervals_map.get(db_qual.lower())
    logger.debug(f"search_scales: intervals for db_qual='{db_qual.lower()}': {intervals}")
    if intervals:
        exists = Notes.objects.filter(
            category__category_name__icontains='scale',
            tonal_root=ROOT_NAME_TO_ID.get(note),
            note_name__icontains=db_qual
        ).exists()
        logger.debug(f"search_scales: Notes exists for root={ROOT_NAME_TO_ID.get(note)}, db_qual='{db_qual}': {exists}")
        if not exists:
            notes_vals = [(ROOT_NAME_TO_ID.get(note) + iv) % 12 for iv in intervals]
            tension_map = {0: 'R', 3: 'b3', 5: '11', 7: '5', 10: 'b7', 2: '2', 4: '3', 9: '6'}
            tensions = [tension_map.get(iv, str(iv)) for iv in intervals]
            notenames = [NOTE_NAMES[nv] for nv in notes_vals]
            logger.debug(f"search_scales: Returning dynamic pentatonic result for {note} {quality}")
            return [{
                'id': None,
                'name': f"{note} {quality}".strip().title(),
                'type': 'Scales',
                'notes': notes_vals,
                'tensions': tensions,
                'notenames': notenames
            }]
    try:
        qs = Notes.objects.filter(category__category_name__icontains='scale')
        if search_query.isdigit():
            qs = qs.filter(pk=int(search_query))
        else:
            qs = qs.filter(tonal_root=ROOT_NAME_TO_ID.get(note))
            qs = qs.filter(note_name__icontains=quality)
        logger.debug(f"search_scales: Final queryset count: {qs.count()}")
        if qs.exists():
            results = process_scale_results(qs)
            display = f"{note} {quality}".strip().title()
            for item in results:
                item['name'] = display
            return results
        logger.debug(f"search_scales: No results found for '{search_query}'.")
        return []
    except Exception as e:
        logger.error(f"Error searching scales: {str(e)}")
        logger.error(traceback.format_exc())
        logger.debug(f"search_scales: Error occurred - {str(e)}")
        return []

def process_scale_results(queryset):
    """Process scale query results into a standardized format"""
    logger.debug(f"Entering process_scale_results with {len(queryset)} items.")
    processed_results = []
    for scale in queryset:
        notes = []
        for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 
                         'sixth_note', 'seventh_note', 'eighth_note', 'ninth_note']:
            if hasattr(scale, note_attr):
                note_value = getattr(scale, note_attr, None)
                if note_value is not None:
                    notes.append(note_value)
        # Use resolve_root to get the correct Root object
        from .search_utils import resolve_root
        # Try to get the note name from scale.tonal_root
        root_obj = None
        if hasattr(scale, 'tonal_root'):
            try:
                pitch_val = int(scale.tonal_root)
                note_name = NOTE_NAMES[pitch_val % 12]
                root_obj = resolve_root(note_name)
            except Exception as e:
                logger.debug(f"process_scale_results: Could not resolve root from tonal_root {scale.tonal_root}: {e}")
        # Fallback: try by pitch if resolve_root fails
        if not root_obj and hasattr(scale, 'tonal_root'):
            try:
                root_obj = Root.objects.filter(pitch=scale.tonal_root).first()
            except Exception as e:
                logger.debug(f"process_scale_results: Fallback by pitch failed for tonal_root {scale.tonal_root}: {e}")
        root_pk = root_obj.pk if root_obj else None
        if root_pk is None:
            logger.error(f"process_scale_results: Could not resolve root for tonal_root={getattr(scale, 'tonal_root', None)} (scale id={scale.id})")
            root_pk = 1  # Final fallback; consider None or raise
        url = f"/?root={root_pk}&models_select=1&notes_options_select={scale.pk}&position_select=0"
        scale_result = {
            'id': scale.id,
            'name': scale.note_name,
            'type': scale.category.category_name,
            'notes': notes,
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

        # Start with base arpeggio query
        qs = ChordNotes.objects.filter(category__category_name__icontains='arpeggio')

        # Filter by root note if provided
        if note:
            from .models import Root
            # First try to find the note by name
            root_obj = Root.objects.filter(name__iexact=note).first()
            
            if root_obj:
                # Use the pitch value for filtering (not the ID)
                root_pitch = root_obj.pitch
                logger.debug(f"Filtering arpeggios by root_pitch: {root_pitch} (for note: {note}, ID: {root_obj.id})")
                qs = qs.filter(tonal_root=root_pitch)
            else:
                # Fall back to the old method if note isn't found
                root_id = ROOT_NAME_TO_ID.get(note)
                if root_id is not None:
                    # Get the corresponding pitch for this ID
                    root_obj = Root.objects.filter(id=root_id).first()
                    if root_obj:
                        root_pitch = root_obj.pitch
                        logger.debug(f"Filtering arpeggios by root_pitch: {root_pitch} (from ID: {root_id} for note: {note})")
                        qs = qs.filter(tonal_root=root_pitch)
                    else:
                        logger.debug(f"Filtering arpeggios by root_id: {root_id} (for note: {note})")
                        qs = qs.filter(tonal_root=root_id)
                else:
                    logger.warning(f"Could not find root_id or pitch for note: {note}. Skipping root filter.")

        # Filter by quality if provided
        if quality:
            # Use Q object for more flexible quality matching (e.g., 'minor', 'Min', 'm')
            quality_filters = Q()
            # Add common variations - adjust these based on your actual data patterns
            variations = [quality, quality.capitalize(), quality.lower()]
            if quality.lower() == 'minor':
                variations.extend(['Min', 'm', 'minor pentatonic', 'Minor Pentatonic'])
            elif quality.lower() == 'major':
                 variations.extend(['Maj', 'major pentatonic', 'Major Pentatonic']) # Add other variations if needed

            # Build Q object for OR conditions
            for var in set(variations): # Use set to avoid duplicate checks
                 quality_filters |= Q(chord_name__icontains=var)

            logger.debug(f"Applying flexible quality filters for '{quality}': {quality_filters}")
            qs = qs.filter(quality_filters)
        else:
             logger.debug("No quality provided, skipping quality filter.")

        # Note: Filtering by type_ (e.g., 'arpeggio') against type_name might be redundant
        # if category filter is already applied, but can be added for robustness if needed.
        if type_ and type_.lower() == 'pentatonic':
            qs = qs.filter(type_name__icontains='pentatonic')

        logger.debug(f"search_arpeggios: Final queryset count before processing: {qs.count()}")

        if qs.exists():
            # Pass the original parsed note to the processing function for display name consistency
            return process_arpeggio_results(qs, root_note=note)
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

def process_arpeggio_results(queryset, root_note=None):
    """Process arpeggio query results into a standardized format"""
    logger.debug(f"Entering process_arpeggio_results with {len(queryset)} items.")
    processed_results = []
    for arpeggio in queryset:
        notes = []
        for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 'sixth_note', 'seventh_note']:
            if hasattr(arpeggio, note_attr):
                note_value = getattr(arpeggio, note_attr, None)
                if note_value is not None:
                    notes.append(note_value)
        # Compose name with root if not present
        name = arpeggio.chord_name
        if root_note and not name.lower().startswith(root_note.lower()):
            name = f"{root_note} {name}"
        
        # Get root ID for URL generation
        from .models import Root
        root_id = None
        if root_note:
            # Try to find root by name
            root_obj = Root.objects.filter(name__iexact=root_note).first()
            if root_obj:
                root_id = root_obj.id
        else:
            # Try to find root from arpeggio.tonal_root
            root_obj = Root.objects.filter(pitch=arpeggio.tonal_root).first()
            if root_obj:
                root_id = root_obj.id
        
        # Fallback if no root found
        if not root_id:
            # Use a default or log warning
            root_id = 14  # Default to A if no root found
            logger.warning(f"Could not find root ID for arpeggio {arpeggio.id}, using default ID 14")
        
        # Always set type to include 'Arpeggio' (robust to DB)
        type_base = arpeggio.type_name.strip()
        if not type_base:
            type_str = "Arpeggio"
        elif "arpeggio" in type_base.lower():
            type_str = type_base
        else:
            type_str = f"{type_base} Arpeggio"
            
        arpeggio_result = {
            'id': arpeggio.id,
            'name': name,
            'type': type_str,
            'notes': notes,
            'url': f"/?root={root_id}&models_select=2&notes_options_select={arpeggio.id}&position_select=0"
        }
        
        logger.debug(f"process_arpeggio_results: Processed arpeggio ID {arpeggio.id}", arpeggio_result)
        processed_results.append(arpeggio_result)
    
    logger.debug(f"Exiting process_arpeggio_results with {len(processed_results)} processed items.")
    return processed_results
