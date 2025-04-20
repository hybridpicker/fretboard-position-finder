from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

# Ensure necessary models are imported
from positionfinder.models import Root, Notes, NotesCategory
from positionfinder.positions import NotesPosition
from positionfinder.models_chords import ChordNotes, ChordPosition
from .serializers import ChordVoicingResponseSerializer
from positionfinder.template_notes import TENSIONS, NOTES, NOTES_SHARP, SHARP_NOTES
from positionfinder.template_notes import STRING_NOTE_OPTIONS

import re
from django.core.cache import cache

# --- Only replace from here to keep most of the file intact ---

class ChordNamesView(APIView):
    """API view to get chord names based on chord type."""
    @method_decorator(csrf_exempt)  # Add CSRF exemption
    def get(self, request, format=None):
        # Log the request
        
        try:
            type_name = request.query_params.get('type_name', None)
            if not type_name:
                type_name = 'Triads'
            
            # Initialize empty list, will be populated from database
            chord_names_list = []
            
            try:
                # Debug database state
                
                # If database is accessible, get chord names from database
                try:
                    total_chords = ChordNotes.objects.count()
                    
                    # For 8-string branch, check if we have any chord data
                    if total_chords == 0:
                        # Use hardcoded defaults for 8-string branch which might not have chord data yet
                        if type_name == 'Triads':
                            chord_names_list = ['Major', 'Minor', 'Diminished', 'Augmented', 'Sus2', 'Sus4']
                        elif 'Seventh' in type_name:
                            chord_names_list = ['Major 7', 'Minor 7', 'Dominant 7', 'MinMaj 7', 'Minor 7b5']
                        else:
                            chord_names_list = ['Major', 'Minor']
                        
                        return Response({'chord_names': chord_names_list})
                    
                    # Try to get chord names from database
                    db_chord_names = ChordNotes.objects.filter(type_name=type_name)\
                                                      .values_list('chord_name', flat=True)\
                                                      .distinct()\
                                                      .order_by('chord_name')
                    
                    # Convert to list
                    chord_names_list = list(db_chord_names)
                    
                    if chord_names_list:
                    else:
                        
                        # If no results for the specific type, use appropriate defaults based on type
                        if type_name == 'Triads':
                            chord_names_list = ['Major', 'Minor', 'Diminished', 'Augmented', 'Sus2', 'Sus4']
                        elif 'Seventh' in type_name:
                            chord_names_list = ['Major 7', 'Minor 7', 'Dominant 7', 'MinMaj 7', 'Minor 7b5']
                        else:
                            # Try to get ALL chord names available before falling back to defaults
                            all_chord_names = ChordNotes.objects.values_list('chord_name', flat=True).distinct().order_by('chord_name')
                            all_chord_names_list = list(all_chord_names)
                            
                            if all_chord_names_list:
                                chord_names_list = all_chord_names_list
                            else:
                                # Only as absolutely last resort, use minimal fallback values
                                chord_names_list = ['Major', 'Minor']
                            
                except Exception as db_error:
                    # Provide specific defaults based on type without attempting another query
                    if type_name == 'Triads':
                        chord_names_list = ['Major', 'Minor', 'Diminished', 'Augmented', 'Sus2', 'Sus4']
                    elif 'Seventh' in type_name:
                        chord_names_list = ['Major 7', 'Minor 7', 'Dominant 7', 'MinMaj 7', 'Minor 7b5']
                    else:
                        chord_names_list = ['Major', 'Minor']
                    
                
            except Exception as e:
                import traceback
                
                # Provide specific defaults based on type
                if type_name == 'Triads':
                    chord_names_list = ['Major', 'Minor', 'Diminished', 'Augmented', 'Sus2', 'Sus4']
                elif 'Seventh' in type_name:
                    chord_names_list = ['Major 7', 'Minor 7', 'Dominant 7', 'MinMaj 7', 'Minor 7b5']
                else:
                    chord_names_list = ['Major', 'Minor']
                
                
            # Ensure we always have at least something to return
            if not chord_names_list:
                if type_name == 'Triads':
                    chord_names_list = ['Major', 'Minor', 'Diminished', 'Augmented', 'Sus2', 'Sus4']
                elif 'Seventh' in type_name:
                    chord_names_list = ['Major 7', 'Minor 7', 'Dominant 7', 'MinMaj 7', 'Minor 7b5']
                else:
                    chord_names_list = ['Major', 'Minor']
                
            
            # Format the response according to what the JS expects:
            # format: {'chord_names': ['Major', 'Minor', ...]}
            return Response({'chord_names': chord_names_list})
            
        except Exception as e:
            import traceback
            
            # Provide hardcoded defaults based on requested type
            if type_name == 'Triads':
                emergency_chord_names = ['Major', 'Minor', 'Diminished', 'Augmented', 'Sus2', 'Sus4']
            elif 'Seventh' in type_name:
                emergency_chord_names = ['Major 7', 'Minor 7', 'Dominant 7', 'MinMaj 7', 'Minor 7b5']
            else:
                emergency_chord_names = ['Major', 'Minor']
                
            # Return a guaranteed valid response even in case of total failure
            emergency_response = {
                'chord_names': emergency_chord_names
            }
            return Response(emergency_response)
