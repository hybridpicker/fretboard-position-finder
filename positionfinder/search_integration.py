"""
Integration module for the improved chord search functionality
This module integrates the improved chord search with the existing search logic
without changing the database structure or view logic.
"""
import logging
import importlib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def integrated_search_json(request, original_search_function):
    """
    A wrapper for the search_json function that enhances chord search results
    
    Args:
        request: The HTTP request
        original_search_function: The original search_json function to wrap
    
    Returns:
        The response from the original function but with enhanced chord results
    """
    logger.debug("Using integrated search with improved chord functionality")
    
    # Get query details
    query = request.GET.get('q', '').strip()
    
    # If no query, just use the original function
    if not query:
        return original_search_function(request)
    
    # Lazy import to avoid circular dependencies
    from .search_utils import parse_query
    
    # Check if this is a chord-specific query
    note, type_, quality, position, inversion = parse_query(query)
    is_chord_query = type_ == 'chord' or 'chord' in query.lower()
    
    logger.debug(f"Parsed query: note={note}, type={type_}, quality={quality}, position={position}, is_chord_query={is_chord_query}")
    
    # For chord searches, enhance with our improved search
    if is_chord_query:
        # Import here to avoid circular imports
        from .improved_chord_search import improved_search_chords
        
        # Process with our improved search
        response = original_search_function(request)
        
        # Get the response data
        response_data = response.data if hasattr(response, 'data') else response.content
        
        # Replace chord results with our improved results
        chord_results = improved_search_chords(query)
        
        # Convert to the expected format
        formatted_results = []
        for item in chord_results:
            formatted_results.append({
                'note_name': item.get('name', ''),
                'description': item.get('type', ''),
                'intervals': item.get('intervals', ''),
                'url': item.get('url', '')
            })
        
        # Update the response
        if hasattr(response, 'data'):
            response.data['chord_results'] = formatted_results
            response.data['total_results'] = (
                len(response.data.get('scale_results', [])) + 
                len(response.data.get('arpeggio_results', [])) + 
                len(formatted_results)
            )
        else:
            # For JsonResponse objects
            import json
            data = json.loads(response.content)
            data['chord_results'] = formatted_results
            data['total_results'] = (
                len(data.get('scale_results', [])) + 
                len(data.get('arpeggio_results', [])) + 
                len(formatted_results)
            )
            response.content = json.dumps(data)
        
        return response
    
    # For non-chord searches, just use the original function
    return original_search_function(request)

def integrated_search_chords(query):
    """
    An enhanced replacement for the search_chords function
    
    Args:
        query: The search query
    
    Returns:
        A list of chord results
    """
    logger.debug(f"Using integrated search_chords with query: '{query}'")
    
    # Lazy import to avoid circular dependencies
    from .improved_chord_search import improved_search_chords
    
    # Use our improved search
    return improved_search_chords(query)

def apply_chord_search_integration():
    """
    Apply the integration by monkey-patching the relevant functions
    
    This enables the enhanced chord search without modifying the original code.
    """
    try:
        logger.info("Integrating improved chord search...")
        
        # Import the original module
        from . import views_search
        
        # Store the original function
        original_search_json = views_search.search_json
        original_search_chords = views_search.search_chords
        
        # Replace with our integrated versions
        views_search.search_json = lambda request: integrated_search_json(request, original_search_json)
        views_search.search_chords = integrated_search_chords
        
        logger.info("Successfully integrated improved chord search")
        return True
    except Exception as e:
        logger.error(f"Failed to integrate improved chord search: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
