from django.http import HttpRequest

from .views_base import MusicalTheoryView
from .models_chords import ChordNotes


class ScaleView(MusicalTheoryView):
    """
    View class for handling scale-related functionality
    Inherits from MusicalTheoryView to leverage common functionality
    """
    
    def __init__(self):
        """Initialize with scales category ID (1)"""
        super().__init__(category_id=1)
    
    def apply_defaults(self, params):
        """
        Apply scale-specific default values
        
        Args:
            params: Dictionary of request parameters
        
        Returns:
            Updated parameter dictionary with defaults applied
        """
        # Default values for scales
        if params['notes_options_id'] is None:
            params['notes_options_id'] = '1'  # Default scale
            
        return params
    
    def add_view_specific_context(self, context, params):
        """
        Add scale-specific context variables
        
        Args:
            context: Base context dictionary
            params: Dictionary of processed parameters
        
        Returns:
            Updated context dictionary with scale-specific variables
        """
        # Add chord name if available
        try:
            context['chord_name'] = context['notes_options'].get(pk=params['notes_options_id']).chords
        except:
            context['chord_name'] = ''
            
        # Check for V1/V2 data existence for the unified menu
        v1_data_exists = ChordNotes.objects.filter(type_name='V1').exists()
        v2_data_exists = ChordNotes.objects.filter(type_name='V2').exists()
        
        context['v1_data_exists'] = v1_data_exists
        context['v2_data_exists'] = v2_data_exists
        
        return context


def fretboard_scale_view(request: HttpRequest):
    """
    View function for displaying scales on the fretboard
    
    Args:
        request: The HTTP request object
    
    Returns:
        Rendered template response
    """
    scale_view = ScaleView()
    return scale_view.render(request)
