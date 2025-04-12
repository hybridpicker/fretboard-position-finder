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

# Configure logging
logger = logging.getLogger(__name__)

def log_debug_info(message, data=None):
    """Helper to output debug information consistently"""
    if data:
        print(f"DEBUG: {message}")
        print(f"DATA: {json.dumps(data) if isinstance(data, (dict, list)) else data}")
    else:
        print(f"DEBUG: {message}")

def unified_search_view(request):
    """
    A unified search view that can search across chords, scales, and arpeggios
    """
    print("\n" + "="*80)
    print("UNIFIED SEARCH INITIATED")
    print(f"REQUEST METHOD: {request.method}")
    print(f"REQUEST PATH: {request.path}")
    print("="*80)
    
    # Get search parameters
    search_query = request.GET.get('search_query', '')
    search_type = request.GET.get('search_type', 'all')  # all, chords, scales, or arpeggios
    
    # Format conversion for empty strings to None for proper filtering
    if not search_query.strip():
        search_query = None
    
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
    
    log_debug_info("Unified Search: Rendering HTML template", {'total_count': total_count, 'search_query': search_query, 'search_type': search_type})
    return render(request, 'search/unified_search.html', context)

def search_chords(search_query):
    """Search for chords matching the query"""
    log_debug_info(f"Entering search_chords with query: '{search_query}'")
    try:
        # First try exact match
        exact_matches = ChordNotes.objects.filter(
            Q(chord_name__iexact=search_query) | 
            Q(type_name__iexact=search_query)
        )
        
        if exact_matches.exists():
            log_debug_info(f"search_chords: Found {exact_matches.count()} exact matches.")
            return process_chord_results(exact_matches)
        
        # Then try startswith match
        startswith_matches = ChordNotes.objects.filter(
            Q(chord_name__istartswith=search_query) | 
            Q(type_name__istartswith=search_query)
        )
        
        if startswith_matches.exists():
            log_debug_info(f"search_chords: Found {startswith_matches.count()} startswith matches.")
            return process_chord_results(startswith_matches)
        
        # Finally, fallback to contains match
        contains_matches = ChordNotes.objects.filter(
            Q(chord_name__icontains=search_query) | 
            Q(type_name__icontains=search_query)
        )
        
        log_debug_info(f"search_chords: Found {contains_matches.count()} contains matches.")
        return process_chord_results(contains_matches)
    except Exception as e:
        print(f"Error searching chords: {str(e)}")
        traceback.print_exc()
        log_debug_info(f"search_chords: Error occurred - {str(e)}")
        return []

def search_scales(search_query):
    """Search for scales matching the query"""
    log_debug_info(f"Entering search_scales with query: '{search_query}'")
    try:
        # First try exact match
        exact_matches = Scales.objects.filter(
            Q(name__iexact=search_query) | 
            Q(type__iexact=search_query)
        )
        
        if exact_matches.exists():
            log_debug_info(f"search_scales: Found {exact_matches.count()} exact matches.")
            return process_scale_results(exact_matches)
        
        # Then try startswith match
        startswith_matches = Scales.objects.filter(
            Q(name__istartswith=search_query) | 
            Q(type__istartswith=search_query)
        )
        
        if startswith_matches.exists():
            log_debug_info(f"search_scales: Found {startswith_matches.count()} startswith matches.")
            return process_scale_results(startswith_matches)
        
        # Finally, fallback to contains match
        contains_matches = Scales.objects.filter(
            Q(name__icontains=search_query) | 
            Q(type__icontains=search_query)
        )
        
        log_debug_info(f"search_scales: Found {contains_matches.count()} contains matches.")
        return process_scale_results(contains_matches)
    except Exception as e:
        print(f"Error searching scales: {str(e)}")
        traceback.print_exc()
        log_debug_info(f"search_scales: Error occurred - {str(e)}")
        return []

def search_arpeggios(search_query):
    """Search for arpeggios matching the query"""
    log_debug_info(f"Entering search_arpeggios with query: '{search_query}'")
    try:
        # For arpeggios, we'll filter the Scale model with arpeggio types
        arpeggio_types = ['Major Triad', 'Minor Triad', 'Diminished Triad', 'Augmented Triad', 
                         'Major 7', 'Minor 7', 'Dominant 7', 'Minor 7b5', 'Diminished 7']
        
        # First try exact match with arpeggio types
        exact_matches = Scale.objects.filter(
            Q(name__iexact=search_query) & 
            Q(type__in=arpeggio_types)
        )
        
        if exact_matches.exists():
            log_debug_info(f"search_arpeggios: Found {exact_matches.count()} exact matches.")
            return process_arpeggio_results(exact_matches)
        
        # Then try startswith match
        startswith_matches = Scale.objects.filter(
            Q(name__istartswith=search_query) & 
            Q(type__in=arpeggio_types)
        )
        
        if startswith_matches.exists():
            log_debug_info(f"search_arpeggios: Found {startswith_matches.count()} startswith matches.")
            return process_arpeggio_results(startswith_matches)
        
        # Finally, fallback to contains match
        contains_matches = Scale.objects.filter(
            Q(name__icontains=search_query) & 
            Q(type__in=arpeggio_types)
        )
        
        log_debug_info(f"search_arpeggios: Found {contains_matches.count()} contains matches.")
        return process_arpeggio_results(contains_matches)
    except Exception as e:
        print(f"Error searching arpeggios: {str(e)}")
        traceback.print_exc()
        log_debug_info(f"search_arpeggios: Error occurred - {str(e)}")
        return []

def process_chord_results(queryset):
    """Process chord query results into a standardized format"""
    log_debug_info(f"Entering process_chord_results with {queryset.count()} items.")
    processed_results = []
    
    for chord in queryset:
        # Get positions (inversions)
        positions = list(ChordPosition.objects.filter(notes_name=chord).values_list('inversion_order', flat=True))
        
        # Extract notes
        notes = []
        for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 'sixth_note']:
            note_value = getattr(chord, note_attr, None)
            if note_value is not None:
                notes.append(note_value)
        
        # Create a result object
        chord_result = {
            'id': chord.id,
            'name': chord.chord_name,
            'type': chord.type_name,
            'range': chord.range,
            'category': getattr(chord.category, 'category_name', None) if hasattr(chord, 'category') else None,
            'positions': positions,
            'notes': notes,
            'url': f"/en/?models_select=3&type_options_select={chord.type_name}&chords_options_select={chord.chord_name}&note_range={chord.range}"
        }
        
        log_debug_info(f"process_chord_results: Processed chord ID {chord.id}", chord_result)
        processed_results.append(chord_result)
    
    log_debug_info(f"Exiting process_chord_results with {len(processed_results)} processed items.")
    return processed_results

def process_scale_results(queryset):
    """Process scale query results into a standardized format"""
    log_debug_info(f"Entering process_scale_results with {queryset.count()} items.")
    processed_results = []
    
    for scale in queryset:
        # Get notes
        notes = []
        # Assuming scales have note fields similar to chords
        for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 
                         'sixth_note', 'seventh_note', 'eighth_note', 'ninth_note']:
            if hasattr(scale, note_attr):
                note_value = getattr(scale, note_attr, None)
                if note_value is not None:
                    notes.append(note_value)
        
        # Create a result object
        scale_result = {
            'id': scale.id,
            'name': scale.name,
            'type': scale.type,
            'notes': notes,
            'url': f"/en/?models_select=1&root_note_minor={scale.name}&scale_options_select={scale.type}"
        }
        
        log_debug_info(f"process_scale_results: Processed scale ID {scale.id}", scale_result)
        processed_results.append(scale_result)
    
    log_debug_info(f"Exiting process_scale_results with {len(processed_results)} processed items.")
    return processed_results

def process_arpeggio_results(queryset):
    """Process arpeggio query results into a standardized format"""
    log_debug_info(f"Entering process_arpeggio_results with {queryset.count()} items.")
    processed_results = []
    
    for arpeggio in queryset:
        # Get notes
        notes = []
        # Assuming arpeggios have note fields similar to chords
        for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 
                         'sixth_note', 'seventh_note']:
            if hasattr(arpeggio, note_attr):
                note_value = getattr(arpeggio, note_attr, None)
                if note_value is not None:
                    notes.append(note_value)
        
        # Create a result object
        arpeggio_result = {
            'id': arpeggio.id,
            'name': arpeggio.name,
            'type': arpeggio.type,
            'notes': notes,
            'url': f"/en/?models_select=2&root_note_chord={arpeggio.name}&chord_options_select={arpeggio.type}"
        }
        
        log_debug_info(f"process_arpeggio_results: Processed arpeggio ID {arpeggio.id}", arpeggio_result)
        processed_results.append(arpeggio_result)
    
    log_debug_info(f"Exiting process_arpeggio_results with {len(processed_results)} processed items.")
    return processed_results


@csrf_exempt
@require_http_methods(["GET", "POST"])
def chord_search_view(request):
    """
    View for searching chords with detailed debug output
    Supports both GET and POST methods
    """
    log_debug_info("="*80)
    log_debug_info("CHORD SEARCH VIEW INITIATED")
    log_debug_info(f"REQUEST METHOD: {request.method}")
    log_debug_info(f"REQUEST PATH: {request.path}")
    log_debug_info("="*80)
    
    # Detailed request debugging
    log_debug_info("\nREQUEST DETAILS:")
    log_debug_info(f"Content Type: {request.content_type}")
    log_debug_info(f"Encoding: {request.encoding}")
    log_debug_info(f"Headers: {dict(request.headers.items())}")
    
    # Get search parameters
    if request.method == 'POST':
        try:
            # Check if JSON content type
            if request.content_type and 'application/json' in request.content_type:
                try:
                    data = json.loads(request.body.decode('utf-8'))
                    search_query = data.get('search_query', '')
                    chord_type = data.get('chord_type', '')
                    note_range = data.get('note_range', '')
                    log_debug_info(f"POST JSON request received", {
                        'query': search_query,
                        'type': chord_type,
                        'range': note_range,
                        'full_data': data
                    })
                except Exception as e:
                    log_debug_info(f"Error parsing JSON: {str(e)}")
                    search_query = ''
                    chord_type = ''
                    note_range = ''
            else:
                search_query = request.POST.get('search_query', '')
                chord_type = request.POST.get('chord_type', '')
                note_range = request.POST.get('note_range', '')
                log_debug_info(f"POST form request received", {
                    'query': search_query,
                    'type': chord_type,
                    'range': note_range,
                    'all_post_data': dict(request.POST)
                })
        except Exception as e:
            log_debug_info(f"Exception in POST processing: {str(e)}")
            traceback.print_exc()
            search_query = ''
            chord_type = ''
            note_range = ''
    else:
        try:
            search_query = request.GET.get('search_query', '')
            chord_type = request.GET.get('chord_type', '')
            note_range = request.GET.get('note_range', '')
            log_debug_info(f"GET request received", {
                'query': search_query,
                'type': chord_type,
                'range': note_range,
                'all_get_params': dict(request.GET)
            })
        except Exception as e:
            log_debug_info(f"Exception in GET processing: {str(e)}")
            traceback.print_exc()
            search_query = ''
            chord_type = ''
            note_range = ''
    
    log_debug_info("\nSEARCH PARAMETERS BEFORE PROCESSING:")
    log_debug_info(f"search_query: '{search_query}' (type: {type(search_query)})")
    log_debug_info(f"chord_type: '{chord_type}' (type: {type(chord_type)})")
    log_debug_info(f"note_range: '{note_range}' (type: {type(note_range)})")
    
    # Format conversion for empty strings to None for proper filtering
    if not search_query or (isinstance(search_query, str) and not search_query.strip()):
        search_query = None
        log_debug_info("Empty search query converted to None")
    if not chord_type or (isinstance(chord_type, str) and not chord_type.strip()):
        chord_type = None
        log_debug_info("Empty chord type converted to None")
    if not note_range or (isinstance(note_range, str) and not note_range.strip()):
        note_range = None
        log_debug_info("Empty note range converted to None")
        
    log_debug_info("\nSEARCH PARAMETERS AFTER PROCESSING:")
    log_debug_info(f"search_query: '{search_query}' (type: {type(search_query).__name__})")
    log_debug_info(f"chord_type: '{chord_type}' (type: {type(chord_type).__name__})")
    log_debug_info(f"note_range: '{note_range}' (type: {type(note_range).__name__})")
    
    # Build the query
    log_debug_info("Building search query...")
    
    try:
        # Count total chords available to compare with filtered results
        total_chords = ChordNotes.objects.count()
        log_debug_info(f"Total chords in database: {total_chords}")
        
        # Print some sample records to verify data retrieval
        sample_chords = list(ChordNotes.objects.all()[:5])
        log_debug_info("Sample chord records:", 
                      [{'id': c.id, 'name': c.chord_name, 'type': c.type_name, 'range': c.range} 
                       for c in sample_chords])
        
        query = ChordNotes.objects.all()
        
        # Apply filters if parameters are provided
        if search_query:
            log_debug_info(f"Adding filter for search query: '{search_query}'")
            
            # Check what fields might match the search query for debugging
            name_matches = list(ChordNotes.objects.filter(chord_name__icontains=search_query).values_list('id', 'chord_name')[:10])
            type_matches = list(ChordNotes.objects.filter(type_name__icontains=search_query).values_list('id', 'type_name')[:10])
            log_debug_info("Potential name matches:", name_matches)
            log_debug_info("Potential type matches:", type_matches)
            
            # Enhanced search with prioritization:
            # 1. First try exact match
            exact_name_matches = ChordNotes.objects.filter(chord_name__iexact=search_query)
            exact_type_matches = ChordNotes.objects.filter(type_name__iexact=search_query)
            exact_matches_count = exact_name_matches.count() + exact_type_matches.count()
            
            if exact_matches_count > 0:
                log_debug_info(f"Found {exact_matches_count} exact matches")
                query = query.filter(
                    Q(chord_name__iexact=search_query) | 
                    Q(type_name__iexact=search_query)
                )
            else:
                # 2. Then try word boundary match (whole word)
                word_boundary_query = rf'\b{search_query}\b'
                word_boundary_matches = ChordNotes.objects.filter(
                    Q(chord_name__iregex=word_boundary_query) | 
                    Q(type_name__iregex=word_boundary_query)
                )
                
                if word_boundary_matches.exists():
                    log_debug_info("Found word boundary matches")
                    query = query.filter(
                        Q(chord_name__iregex=word_boundary_query) | 
                        Q(type_name__iregex=word_boundary_query)
                    )
                else:
                    # 3. Then try startswith match
                    startswith_matches = ChordNotes.objects.filter(
                        Q(chord_name__istartswith=search_query) | 
                        Q(type_name__istartswith=search_query)
                    )
                    
                    if startswith_matches.exists():
                        log_debug_info("Found startswith matches")
                        query = query.filter(
                            Q(chord_name__istartswith=search_query) | 
                            Q(type_name__istartswith=search_query)
                        )
                    else:
                        # 4. Finally, fallback to contains match
                        log_debug_info("Using contains matches (fallback)")
                        query = query.filter(
                            Q(chord_name__icontains=search_query) | 
                            Q(type_name__icontains=search_query)
                        )
            
            log_debug_info(f"After search query filter, count: {query.count()}")
        
        if chord_type:
            log_debug_info(f"Adding filter for chord type: '{chord_type}'")
            # Show all available chord types for debugging
            all_types = list(ChordNotes.objects.values_list('type_name', flat=True).distinct())
            log_debug_info("Available chord types:", all_types)
            
            # Get closest matching type
            # Check for exact match first
            if ChordNotes.objects.filter(type_name__iexact=chord_type).exists():
                log_debug_info(f"Found exact match for type '{chord_type}'")
                query = query.filter(type_name__iexact=chord_type)
            else:
                # Check for partial matches when exact match not found
                similar_types = [t for t in all_types if chord_type.lower() in t.lower()]
                log_debug_info(f"Similar types found: {similar_types}")
                
                if similar_types:
                    # Sort by string length to find closest match
                    similar_types.sort(key=len)
                    closest_match = similar_types[0]
                    log_debug_info(f"Using closest match type: '{closest_match}'")
                    query = query.filter(type_name=closest_match)
                else:
                    # No match found, use original filter
                    log_debug_info(f"No similar types found for '{chord_type}', using exact filter")
                    query = query.filter(type_name=chord_type)
            
            log_debug_info(f"After chord type filter, count: {query.count()}")
        
        if note_range:
            log_debug_info(f"Adding filter for note range: '{note_range}'")
            # Show all available ranges for debugging
            all_ranges = list(ChordNotes.objects.values_list('range', flat=True).distinct())
            log_debug_info("Available note ranges:", all_ranges)
            
            # Get closest matching range
            # Check for exact match first
            if ChordNotes.objects.filter(range__iexact=note_range).exists():
                log_debug_info(f"Found exact match for range '{note_range}'")
                query = query.filter(range__iexact=note_range)
            else:
                # Check for similar ranges when exact match not found
                similar_ranges = []
                
                # Normalize ranges by removing spaces for better matching
                normalized_search = note_range.replace(" ", "").lower()
                
                for r in all_ranges:
                    normalized_range = r.replace(" ", "").lower()
                    # Check if search is substring or if range is substring of search
                    if normalized_search in normalized_range or normalized_range in normalized_search:
                        similar_ranges.append(r)
                
                log_debug_info(f"Similar ranges found: {similar_ranges}")
                
                if similar_ranges:
                    # Sort by length difference to find closest match
                    similar_ranges.sort(key=lambda x: abs(len(x) - len(note_range)))
                    closest_match = similar_ranges[0]
                    log_debug_info(f"Using closest match range: '{closest_match}'")
                    query = query.filter(range=closest_match)
                else:
                    # No match found, use original filter
                    log_debug_info(f"No similar ranges found for '{note_range}', using exact filter")
                    query = query.filter(range=note_range)
            
            log_debug_info(f"After note range filter, count: {query.count()}")
        
        # Ordering
        log_debug_info("Applying ordering by 'type_name', 'chord_ordering', 'range_ordering'")
        query = query.order_by('type_name', 'chord_ordering', 'range_ordering')
        
        # Execute query
        log_debug_info("Executing query...")
        try:
            # Get the SQL to be executed
            sql_query = str(query.query)
            log_debug_info("Generated SQL:", sql_query)
            
            # Execute and get results
            results = list(query)
            log_debug_info(f"Query returned {len(results)} results")
            
            # Check first few results
            if results:
                sample_results = results[:min(5, len(results))]
                log_debug_info("Sample results:", 
                            [{'id': r.id, 'name': r.chord_name, 'type': r.type_name, 'range': r.range} 
                            for r in sample_results])
            else:
                log_debug_info("No results returned from query")
        except Exception as e:
            log_debug_info(f"Error executing query: {str(e)}")
            traceback.print_exc()
            results = []
    except Exception as e:
        log_debug_info(f"Error building or executing query: {str(e)}")
        traceback.print_exc()
        results = []
    
    # Log the SQL query (for debugging)
    log_debug_info("\nSQL QUERY INFORMATION:")
    try:
        last_query = connection.queries[-1]['sql'] if connection.queries else "No query executed"
        log_debug_info("SQL Query:", last_query)
        
        # Display query time if available
        if connection.queries and 'time' in connection.queries[-1]:
            query_time = connection.queries[-1]['time']
            log_debug_info(f"Query execution time: {query_time} seconds")
    except Exception as e:
        log_debug_info(f"Error retrieving SQL query: {str(e)}")
        traceback.print_exc()
    
    # Process results for display
    processed_results = []
    
    log_debug_info("\n" + "-"*50)
    log_debug_info(f"Processing {len(results)} search results for chord_search_view...")
    log_debug_info("-"*50)
    
    for i, chord in enumerate(results):
        log_debug_info(f"\nProcessing chord {i+1}/{len(results)} (ID: {chord.id}):")
        log_debug_info(f"  Name: {chord.chord_name}")
        log_debug_info(f"  Type: {chord.type_name}")
        log_debug_info(f"  Range: {chord.range}")
        
        # Get root category
        root_category = None
        try:
            if hasattr(chord, 'category'):
                if chord.category:
                    root_category = chord.category.category_name
                    log_debug_info(f"  Category: {root_category}")
                else:
                    log_debug_info("  Category: None (chord.category is None)")
            else:
                log_debug_info("  Category: Not available (no category attribute)")
        except Exception as e:
            log_debug_info(f"  Error retrieving category: {str(e)}")
            traceback.print_exc()
        
        # Get positions (inversions)
        positions = []
        try:
            position_query = ChordPosition.objects.filter(notes_name=chord)
            position_count = position_query.count()
            log_debug_info(f"  Found {position_count} positions/inversions")
            
            if position_count > 0:
                position_details = list(position_query.values('id', 'inversion_order'))
                log_debug_info(f"  Position details: {position_details}")
                
            positions = list(position_query.values_list('inversion_order', flat=True))
            log_debug_info(f"  Position values: {positions}")
        except Exception as e:
            log_debug_info(f"  Error retrieving positions: {str(e)}")
            traceback.print_exc()
        
        # Extract notes
        notes = []
        note_details = {}
        try:
            for note_attr in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 'sixth_note']:
                note_value = getattr(chord, note_attr, None)
                if note_value is not None:
                    notes.append(note_value)
                    note_details[note_attr] = note_value
            
            log_debug_info(f"  Notes: {notes}")
            log_debug_info(f"  Note details: {note_details}")
        except Exception as e:
            log_debug_info(f"  Error extracting notes: {str(e)}")
            traceback.print_exc()
        
        # Create a chord result object
        try:
            chord_result = {
                'id': chord.id,
                'name': chord.chord_name,
                'type': chord.type_name,
                'range': chord.range,
                'category': root_category,
                'positions': positions,
                'notes': notes
            }
            
            processed_results.append(chord_result)
            log_debug_info(f"  Added to processed results. Total now: {len(processed_results)}")
        except Exception as e:
            log_debug_info(f"  Error creating chord result object: {str(e)}")
            traceback.print_exc()
    
    log_debug_info("\n" + "-"*50)
    log_debug_info(f"Finished processing {len(processed_results)} chord results for chord_search_view")
    log_debug_info("-"*50)
    
    log_debug_info("\nPREPARING RESPONSE for chord_search_view:")
    # Check if JSON response is requested
    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        log_debug_info(f"AJAX Request? {is_ajax}")
        
        if is_ajax:
            log_debug_info("Returning JSON response")
            response_data = {
                'results': processed_results,
                'count': len(processed_results),
                'search_params': {
                    'query': search_query,
                    'type': chord_type,
                    'range': note_range
                }
            }
            log_debug_info(f"JSON Response keys: {response_data.keys()}")
            log_debug_info(f"Results count: {len(processed_results)}")
            return JsonResponse(response_data)
        
        # Prepare context for template rendering
        log_debug_info("Preparing template context")
        
        # Get all available chord types for dropdown
        try:
            chord_types = list(ChordNotes.objects.values_list('type_name', flat=True).distinct())
            chord_types.sort()
            log_debug_info(f"Available chord types ({len(chord_types)}): {chord_types[:20]}...") # Log first 20
        except Exception as e:
            log_debug_info(f"Error retrieving chord types: {str(e)}")
            chord_types = []
        
        # Get all available note ranges for dropdown
        try:
            note_ranges = list(ChordNotes.objects.values_list('range', flat=True).distinct())
            note_ranges.sort()
            log_debug_info(f"Available note ranges ({len(note_ranges)}): {note_ranges}")
        except Exception as e:
            log_debug_info(f"Error retrieving note ranges: {str(e)}")
            note_ranges = []
        
        # Prepare template context
        try:
            context = {
                'search_query': search_query or '',
                'chord_type': chord_type or '',
                'note_range': note_range or '',
                'chord_types': chord_types,
                'note_ranges': note_ranges,
                'results': processed_results,
                'result_count': len(processed_results),
                'show_fretboard': False,  # No need to show fretboard on search page
            }
            
            # Add common context
            try:
                common_context = get_common_context(request)
                context.update(common_context)
                log_debug_info(f"Added common context keys: {list(common_context.keys())}")
            except Exception as e:
                log_debug_info(f"Error getting common context: {str(e)}")
                traceback.print_exc()
            
            # Final context summary
            log_debug_info(f"Final context keys: {list(context.keys())}")
            log_debug_info(f"Final result count: {context['result_count']}")
            
            log_debug_info("Rendering template 'chord_search.html'")
            log_debug_info("="*80 + "\n")
            
            return render(request, 'chord_search.html', context)
        except Exception as e:
            log_debug_info(f"Error preparing context: {str(e)}")
            traceback.print_exc()
            log_debug_info("Rendering chord_search.html with error message.")
            return render(request, 'chord_search.html', {'error': str(e)})
    except Exception as e:
        log_debug_info(f"Error preparing response: {str(e)}")
        traceback.print_exc()
        log_debug_info("Rendering chord_search.html with error message due to response preparation failure.")
        return render(request, 'chord_search.html', {'error': str(e)})
