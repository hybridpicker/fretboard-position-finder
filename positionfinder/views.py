from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from .views_helpers import get_common_context # Import the correct helper
# Removed import for non-existent get_initial_menu_options


def about_view(request):
    # Removed call to non-existent get_initial_menu_options
    context = {
        'show_fretboard': False, # Assuming this controls fretboard display
    }
    # Add common context variables (including optimization flag)
    common_context = get_common_context(request)
    context.update(common_context)
    return render(request, 'about.html', context)


def impressum_view(request):
    # Removed call to non-existent get_initial_menu_options
    context = {
        'show_fretboard': False, # Assuming this controls fretboard display
    }
    # Add common context variables (including optimization flag)
    common_context = get_common_context(request)
    context.update(common_context)
    return render(request, 'impressum.html', context)


def fretboard_unified_view(request):
    """
    Unified view that dispatches to the appropriate view handler based on the 'models_select' parameter.
    - models_select=1: Scales
    - models_select=2: Arpeggios
    - models_select=3: Chords
    Default is scales if not specified.
    """
    # Import the view functions here to avoid circular import issues
    from positionfinder.views_scale import fretboard_scale_view
    from positionfinder.views_arpeggio import fretboard_arpeggio_view
    from positionfinder.views_chords import fretboard_chords_view
    
    # Determine which mode to render
    try:
        category_id = request.GET.get('models_select', '1')
    except MultiValueDictKeyError:
        category_id = '1'  # Default to scales
    
    # Call the appropriate view handler without redirecting
    if category_id == '2':
        # Arpeggios - call view directly instead of redirecting
        return fretboard_arpeggio_view(request)
    elif category_id == '3':
        # Chords - call view directly instead of redirecting
        return fretboard_chords_view(request)
    else:
        # Default or Scales (category_id == '1')
        return fretboard_scale_view(request)


def chord_search_test_view(request):
    """
    View for testing the chord search functionality.
    Renders a test page that includes all necessary JS for testing the chord search logic.
    """
    context = {
        'show_fretboard': True,  # We need the fretboard to be displayed
    }
    # Add common context variables
    common_context = get_common_context(request)
    context.update(common_context)
    return render(request, 'test_chords.html', context)
