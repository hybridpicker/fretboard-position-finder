"""
Helper functions for the positionfinder views.
"""
import os
from django.conf import settings

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
