from django.http import HttpRequest
from .models import Notes, NotesCategory
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
            # Get arpeggio category
            arpeggio_category = NotesCategory.objects.filter(category_name__icontains='arpeggio').first()
            if arpeggio_category:
                # Try to get first Notes object with arpeggio category
                first_arpeggio = Notes.objects.filter(category=arpeggio_category).first()
                if first_arpeggio:
                    params['notes_options_id'] = str(first_arpeggio.id)
                else:
                    # Fallback to default value
                    params['notes_options_id'] = '13'  # Minor 7 arpeggio
            else:
                # Fallback to default value if category not found
                params['notes_options_id'] = '13'  # Minor 7 arpeggio
            
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
    from django.shortcuts import render
    from .models import Notes, NotesCategory
    
    # Find arpeggio category
    arpeggio_category = NotesCategory.objects.filter(category_name__icontains='arpeggio').first()
    if arpeggio_category:
        arpeggios = Notes.objects.filter(category=arpeggio_category)
    else:
        arpeggios = []
    
    return render(request, 'arpeggio_list.html', {'arpeggios': arpeggios})
