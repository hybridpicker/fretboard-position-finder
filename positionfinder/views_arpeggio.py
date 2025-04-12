from django.http import HttpRequest

from .views_base import MusicalTheoryView


class ArpeggioView(MusicalTheoryView):
    """
    View class for handling arpeggio-related functionality
    Inherits from MusicalTheoryView to leverage common functionality
    """
    
    def __init__(self):
        """Initialize with arpeggios category ID (2)"""
        super().__init__(category_id=2)
    
    def apply_defaults(self, params):
        """
        Apply arpeggio-specific default values
        
        Args:
            params: Dictionary of request parameters
        
        Returns:
            Updated parameter dictionary with defaults applied
        """
        # Default values for arpeggios
        if params['notes_options_id'] is None:
            params['notes_options_id'] = '2'  # Default arpeggio
            
        return params


def fretboard_arpeggio_view(request: HttpRequest):
    """
    View function for displaying arpeggios on the fretboard
    
    Args:
        request: The HTTP request object
    
    Returns:
        Rendered template response
    """
    arpeggio_view = ArpeggioView()
    return arpeggio_view.render(request)


def arpeggio_list(request: HttpRequest):
    """
    View function for displaying a list of arpeggios
    
    Args:
        request: The HTTP request object
    
    Returns:
        Rendered template response with arpeggio list
    """
    from .models import Notes
    from django.shortcuts import render
    
    arpeggios = Notes.objects.filter(category_id=2)  # ID 2 = Arpeggios
    return render(request, 'arpeggio_list.html', {'arpeggios': arpeggios})
