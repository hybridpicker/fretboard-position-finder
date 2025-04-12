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
# V-system imports removed

import re
from django.core.cache import cache

# Constants for guitar specifications
TUNINGS = {
    '6-string': ['E', 'A', 'D', 'G', 'B', 'E'],
    '7-string': ['B', 'E', 'A', 'D', 'G', 'B', 'E'],
    '8-string': ['F#', 'B', 'E', 'A', 'D', 'G', 'B', 'E']
}

# String combinations for all instruments
STRING_COMBINATIONS = {
    '6-string': [('6-3'), ('5-2'), ('4-1')],
    '7-string': [('7-4'), ('6-3'), ('5-2'), ('4-1')],
    '8-string': [('8-5'), ('7-4'), ('6-3'), ('5-2'), ('4-1')]
}

class ChordVoicingView(APIView):
    """API view for chord voicings."""
    permission_classes = []  # Override default permissions that require a queryset

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request, format=None):
        """
        Get chord voicings based on query parameters.

        Required parameters:
        - chord: Chord name (e.g., G7, Cmaj7)
        - voicing_group: V-System group (e.g., V-2)
        - instrument: Guitar type (6-string, 7-string, 8-string)
        - string_set: String set (e.g., 6-3, 5-2)
        """
        chord = request.query_params.get('chord', None)
        voicing_group = request.query_params.get('voicing_group', None)
        instrument = request.query_params.get('instrument', '6-string')
        string_set = request.query_params.get('string_set', '6-3')

        if not chord or not voicing_group:
            return Response(
                {'error': 'Missing required parameters (chord, voicing_group)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Normalize voicing group format (V-2 or V2 -> V-2)
        if not voicing_group.startswith('V-') and voicing_group.startswith('V'):
            voicing_group = f"V-{voicing_group[1:]}"

        # Parse chord (e.g., G7 -> root: G, type: 7)
        chord_match = re.match(r'([A-G][#b]?)([^#b]*)', chord)
        if not chord_match:
            return Response(
                {'error': 'Invalid chord format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        root_note, chord_suffix = chord_match.groups()

        # Map chord suffixes to actual chord names
        chord_type_mapping = {
            '': 'Major',
            'maj': 'Major',
            'min': 'Minor',
            'm': 'Minor',
            '7': 'Dominant 7',
            'maj7': 'Major 7',
            'M7': 'Major 7',
            'min7': 'Minor 7',
            'm7': 'Minor 7',
            'Δ': 'Major 7',
            'Δ7': 'Major 7',
            'mΔ7': 'MinMaj 7',
            'mM7': 'MinMaj 7',
            'm7b5': 'Minor 7b5',
            'ø': 'Minor 7b5',
            'ø7': 'Minor 7b5',
            'dim': 'Diminished',
            'dim7': 'Diminished',
            'o': 'Diminished',
            'o7': 'Diminished',
            'aug': 'Augmented',
            '+': 'Augmented',
            '7#5': 'Dominant 7(#5)',
            '7+': 'Dominant 7(#5)',
            '7b5': 'Dominant 7(b5)',
            'maj7#5': 'Major 7(#5)',
            'maj7b5': 'Major 7(b5)',
            'M7#5': 'Major 7(#5)',
            'M7b5': 'Major 7(b5)',
        }

        chord_name = chord_type_mapping.get(chord_suffix, 'Major')

        # V-system fret span check removed

        # V-system generator removed
        voicings = []  # Placeholder for removed v-system functionality

        # Create response data
        response_data = {
            'voicing_group': voicing_group,
            'instrument': instrument,
            'string_set': string_set,
            'chord': chord,
            'voicings': voicings
        }

        # Validate with serializer
        serializer = ChordVoicingResponseSerializer(data=response_data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TuningOptionsView(APIView):
    """API view for retrieving available tunings and string sets."""
    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request, format=None):
        """Get all available tunings and corresponding string sets."""
        # V-system import removed

        response_data = {
            'tunings': TUNINGS,
            'string_sets': STRING_COMBINATIONS
        }

        return Response(response_data)

class VoicingGroupsView(APIView):
    """API view for available V-System voicing groups."""
    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request, format=None):
        """Get all available V-System voicing groups."""
        # V-system imports removed

        response_data = {
            'seventh_chords': [],  # Placeholder for removed v-system functionality
            'triads': []  # Placeholder for removed v-system functionality
        }

        return Response(response_data)

class ChordTypesView(APIView):
    """API view for available chord types."""
    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request, format=None):
        """Get all available chord types with their interval structures."""
        # V-system imports removed

        # Basic chord intervals as replacement
        chord_intervals = {
            'Major': [0, 4, 7],
            'Minor': [0, 3, 7],
            'Dominant 7': [0, 4, 7, 10],
            'Major 7': [0, 4, 7, 11],
            'Minor 7': [0, 3, 7, 10]
        }

        response_data = {
            'chord_types': chord_intervals
        }

        return Response(response_data)

# Fallback view that always returns a valid response
class FallbackPositionsView(APIView):
    """Fallback API view that returns appropriate positions based on scale type."""
    permission_classes = []  # Override default permissions that require a queryset
    
    def get(self, request, format=None):
        # Log the request
        
        try:
            # Get notes_id to determine scale type
            notes_id = request.query_params.get('notes_id', 'unknown')
            
            # Start with "All Notes"
            positions = [{'position_order': 0}]
            
            # Determine positions based on scale type
            try:
                notes_id_int = int(notes_id) if notes_id.isdigit() else 0
                
                # For specific scale types
                if notes_id_int == 49:  # Blues scale ID
                    # Blues scale typically has 5 positions
                    for i in range(1, 6):
                        positions.append({'position_order': i})
                elif notes_id_int in [1, 2, 3]:  # Major scale IDs
                    # Major scale has 7 positions
                    for i in range(1, 8):
                        positions.append({'position_order': i})
                else:
                    # Default for other scales: 5 positions
                    for i in range(1, 6):
                        positions.append({'position_order': i})
            except Exception as e:
                # Default to 5 positions if we can't determine the scale type
                for i in range(1, 6):
                    positions.append({'position_order': i})
            
            return Response({'positions': positions})
        except Exception as e:
            # Even in case of error, return a minimal valid response with only 'All Notes'
            return Response({'positions': [{'position_order': 0}]})

# Ultra-simple emergency fallback endpoints that don't use DRF
from django.http import JsonResponse

def emergency_positions(request):
    """Most basic view possible that always returns a valid position response."""
    try:
        import traceback
        
        # Check for specific type parameters to handle different types of requests
        type_name = request.GET.get('type_name', '')
        notes_id = request.GET.get('notes_id', '')
        chord_name = request.GET.get('chord_name', '')
        chord_notes_id = request.GET.get('chord_notes_id', '')
        
        # If this looks like a chord_names request
        if type_name and not chord_name:
            # Return chord names for the given type
            if 'Triads' in type_name:
                return JsonResponse({'chord_names': [
                    {'chord_name': 'Major'},
                    {'chord_name': 'Minor'},
                    {'chord_name': 'Diminished'},
                    {'chord_name': 'Augmented'},
                    {'chord_name': 'Sus2'},
                    {'chord_name': 'Sus4'}
                ]})
            elif 'Spread' in type_name:
                return JsonResponse({'chord_names': [
                    {'chord_name': 'Major'},
                    {'chord_name': 'Minor'},
                    {'chord_name': 'Diminished'},
                    {'chord_name': 'Sus2'},
                    {'chord_name': 'Sus4'}
                ]})
            else:
                return JsonResponse({'chord_names': [
                    {'chord_name': 'Major'},
                    {'chord_name': 'Minor'}
                ]})
        
        # If this looks like a chord_ranges request
        elif type_name and chord_name:
            # Return ranges for the given chord
            return JsonResponse({
                'ranges': [
                    {'id': '1', 'range': 'e - g'},
                    {'id': '2', 'range': 'b - d'},
                    {'id': '3', 'range': 'g - A'},
                    {'id': '4', 'range': 'd - E'},
                    {'id': '5', 'range': 'A - B'},
                    {'id': '6', 'range': 'highA - e'}
                ]
            })
        
        # If this looks like a chord_positions request (inversions)
        elif chord_notes_id:
            # Return some inversions based on the chord_notes_id
            positions = [
                {'inversion_order': 'Root Position'},
                {'inversion_order': 'First Inversion'},
                {'inversion_order': 'Second Inversion'}
            ]
            if chord_notes_id in ['4', '5', '6']:  # For 7th chords
                positions.append({'inversion_order': 'Third Inversion'})
                
            return JsonResponse({'positions': positions})
            
        # If this looks like a scale/arpeggio positions request
        elif notes_id:
            # Return positions based on scale type
            # This is a simplified mapping - you'll need to adjust according to your actual scales
            # We use the notes_id to determine the scale type
            
            # Default to positions 0-5 for most scales
            default_positions = [
                {'position_order': 0},  # All Notes
                {'position_order': 1},
                {'position_order': 2},
                {'position_order': 3},
                {'position_order': 4},
                {'position_order': 5}
            ]
            
            # Special handling for certain scales based on notes_id
            if notes_id in ['49']:  # Blues scale ID
                # Blues scale typically has 5 positions (plus "All Notes")
                positions = [
                    {'position_order': 0},  # All Notes
                    {'position_order': 1},
                    {'position_order': 2},
                    {'position_order': 3},
                    {'position_order': 4},
                    {'position_order': 5}
                ]
            elif notes_id in ['1', '2', '3']:  # Major scale and other 7-position scales
                # Major scale has 7 positions (plus "All Notes")
                positions = [
                    {'position_order': 0},  # All Notes
                    {'position_order': 1},
                    {'position_order': 2},
                    {'position_order': 3},
                    {'position_order': 4},
                    {'position_order': 5},
                    {'position_order': 6},
                    {'position_order': 7}
                ]
            else:
                # Use default for other scales
                positions = default_positions
                
                # Log for debugging
                
            return JsonResponse({'positions': positions})
        
        # Default to positions response
        return JsonResponse({'positions': [{'position_order': 0}]})
        
    except Exception as e:
        # Fail absolutely silently
        return JsonResponse({'positions': [{'position_order': 0}]})

# No template view needed


# --- New Views for Dynamic Menu Options ---

class ChordNamesView(APIView):
    """API view to get chord names based on chord type."""
    permission_classes = []  # Override default permissions that require a queryset
    
    @method_decorator(csrf_exempt)  # Add CSRF exemption
    def get(self, request, format=None):
        # Log the request
        
        try:
            type_name = request.query_params.get('type_name', None)
            if not type_name:
                # Try to get the first available type from database instead of hardcoding
                try:
                    first_type = ChordNotes.objects.values_list('type_name', flat=True).distinct().first()
                    if first_type:
                        type_name = first_type
                    else:
                        # Only if database is empty, use a fallback
                        type_name = 'Triads'
                except Exception as e:
                    type_name = 'Triads'
            
            # Initialize empty list, will be populated from database
            chord_names_list = []
            
            try:
                # Debug database state
                
                # If database is accessible, get chord names from database
                try:
                    total_chords = ChordNotes.objects.count()
                    
                    # Add debug info
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute(f"SELECT type_name, chord_name, COUNT(*) FROM positionfinder_chordnotes GROUP BY type_name, chord_name ORDER BY COUNT(*) DESC LIMIT 10")
                        duplicates = cursor.fetchall()
                    
                    # Use the emergency endpoint's hardcoded data for Triads
                    if type_name == 'Triads':
                        chord_names_list = [
                            {'chord_name': 'Major'},
                            {'chord_name': 'Minor'},
                            {'chord_name': 'Diminished'},
                            {'chord_name': 'Augmented'},
                            {'chord_name': 'Sus2'},
                            {'chord_name': 'Sus4'}
                        ]
                    else:
                        # Try to get chord names from database
                        db_chord_names = ChordNotes.objects.filter(type_name=type_name)\
                                                        .values_list('chord_name', flat=True)\
                                                        .distinct()\
                                                        .order_by('chord_name')
                        
                        # Convert the db_chord_names to objects with 'chord_name' property
                        chord_names_list = [{'chord_name': name} for name in db_chord_names]
                    
                    if chord_names_list:
                        # If chord names are found for the specific type, do nothing here for now
                        pass
                    else:
                        # TODO: Implement logic to fetch all chord names if specific type yields no results
                        pass
                        
                        # If no results for the specific type, try to get ALL chord names available
                        # This is better than hardcoding defaults
                        all_chord_names = ChordNotes.objects.values_list('chord_name', flat=True).distinct().order_by('chord_name')
                        all_chord_names_list = list(all_chord_names)
                        
                        if all_chord_names_list:
                            # Convert to objects with 'chord_name' property
                            chord_names_list = [{'chord_name': name} for name in all_chord_names_list]
                        else:
                            # Only as absolutely last resort, use minimal fallback values
                            chord_names_list = [
                                {'chord_name': 'Major'},
                                {'chord_name': 'Minor'}
                            ]
                            
                except Exception as db_error:
                    # Try querying for ANY chord names as fallback
                    try:
                        all_chord_names = ChordNotes.objects.values_list('chord_name', flat=True).distinct()
                        all_name_values = list(all_chord_names)
                        if all_name_values:
                            chord_names_list = [{'chord_name': name} for name in all_name_values]
                        else:
                            # Last resort
                            chord_names_list = [
                                {'chord_name': 'Major'},
                                {'chord_name': 'Minor'}
                            ]
                    except Exception:
                        # Absolute last resort
                        chord_names_list = [
                            {'chord_name': 'Major'},
                            {'chord_name': 'Minor'}
                        ]
                
            except Exception as e:
                import traceback
                
                # Absolute last resort
                chord_names_list = [
                    {'chord_name': 'Major'},
                    {'chord_name': 'Minor'}
                ]
                
            # Ensure we always have at least something to return and remove duplicates
            if not chord_names_list:
                chord_names_list = [
                    {'chord_name': 'Major'},
                    {'chord_name': 'Minor'}
                ]
            else:
                # Remove duplicates while preserving order
                seen = set()
                chord_names_list = [
                    item for item in chord_names_list 
                    if not (item.get('chord_name') in seen or seen.add(item.get('chord_name')))
                ]
                
            
            # Format the response in both formats for maximum compatibility
            formatted_response = {
                'chord_names': chord_names_list
            }
            
            return Response(formatted_response)
            
        except Exception as e:
            import traceback
            
            # Return hardcoded response for known chord types
            if type_name == 'Triads':
                emergency_chord_names = [
                    {'chord_name': 'Major'},
                    {'chord_name': 'Minor'},
                    {'chord_name': 'Diminished'},
                    {'chord_name': 'Augmented'},
                    {'chord_name': 'Sus2'},
                    {'chord_name': 'Sus4'}
                ]
            else:
                # Try to get from database, fallback to defaults if that fails
                try:
                    all_chord_names = ChordNotes.objects.values_list('chord_name', flat=True).distinct().order_by('chord_name')[:10]
                    all_chord_names_list = list(all_chord_names)
                    if all_chord_names_list:
                        emergency_chord_names = [{'chord_name': name} for name in all_chord_names_list]
                    else:
                        emergency_chord_names = [
                            {'chord_name': 'Major'},
                            {'chord_name': 'Minor'}
                        ]
                except Exception:
                    emergency_chord_names = [
                        {'chord_name': 'Major'},
                        {'chord_name': 'Minor'}
                    ]
                
            # Format response consistently no matter what
            formatted_emergency_response = {
                'chord_names': emergency_chord_names
            }
            
            return Response(formatted_emergency_response)

class ChordRangesView(APIView):
    """API view to get chord ranges based on type and name."""
    permission_classes = []  # Override default permissions that require a queryset
    
    def get(self, request, format=None):
        
        try:
            type_name = request.query_params.get('type_name', None)
            chord_name = request.query_params.get('chord_name', None)
            
            # Check for string configuration (6 or 8 string) from cookie and query param
            # Try query param first (for direct testing)
            string_mode = request.query_params.get('string_mode', None)
            if not string_mode:
                # Then try cookie
                string_mode = request.COOKIES.get('stringConfig', 'eight-string')
            
            # Set defaults if still not found
            if string_mode not in ['six-string', 'eight-string']:
                string_mode = 'eight-string'
                
            is_six_string = string_mode == 'six-string'
            
            # Debug string configuration
            print(f"API - String configuration: {string_mode}, is_six_string: {is_six_string}")
    
            if not type_name or not chord_name:
                # Try to get valid values from database instead of returning error
                try:
                    # Get first valid type and chord name from database
                    sample_chord = ChordNotes.objects.first()
                    if sample_chord:
                        if not type_name:
                            type_name = sample_chord.type_name
                        if not chord_name:
                            chord_name = sample_chord.chord_name
                    else:
                        return Response({'error': 'Missing required parameters and no database values found'}, 
                                        status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error': 'Missing required parameters: type_name, chord_name'}, 
                                    status=status.HTTP_400_BAD_REQUEST)
            
            # Initialize empty ranges list
            ranges_list = []
    
            try:
                # First, try to get ranges specific to the requested chord type and name
                if type_name and chord_name:
                    specific_ranges = ChordNotes.objects.filter(type_name=type_name, chord_name=chord_name)\
                                                      .order_by('range_ordering')\
                                                      .values('id', 'range')
                    specific_ranges_list = list(specific_ranges)
                    
                    if specific_ranges_list:
                        ranges_list = specific_ranges_list
                    else:
                        # No specific ranges found for this type/chord combo, do nothing here
                        pass
                
                # If no specific ranges found, get all ranges used for this chord name in any type
                if not ranges_list:
                    chord_ranges = ChordNotes.objects.filter(chord_name=chord_name)\
                                                   .order_by('range_ordering')\
                                                   .values('id', 'range')\
                                                   .distinct('range')
                    chord_ranges_list = list(chord_ranges)
                    
                    if chord_ranges_list:
                        ranges_list = chord_ranges_list
                    else:
                        # No ranges found for this specific chord name, do nothing here
                        pass
                
                # If still no ranges, get all ranges for this chord type
                if not ranges_list:
                    type_ranges = ChordNotes.objects.filter(type_name=type_name)\
                                                   .order_by('range_ordering')\
                                                   .values('id', 'range')\
                                                   .distinct('range')
                    type_ranges_list = list(type_ranges)
                    
                    if type_ranges_list:
                        ranges_list = type_ranges_list
                    else:
                        # No ranges found for this specific type, do nothing here
                        pass
                
                # If still no ranges, get all ranges from all chords
                if not ranges_list:
                    all_ranges = ChordNotes.objects.values('id', 'range')\
                                                  .distinct('range')\
                                                  .order_by('range_ordering')
                    all_ranges_list = list(all_ranges)
                    
                    if all_ranges_list:
                        ranges_list = all_ranges_list
                    else:
                        # No ranges found at all, do nothing here
                        pass
                
                # If we still have no ranges (e.g., empty database), use these standard ranges
                if not ranges_list:
                    # Get common range values from the database definition
                    try:
                        from positionfinder.string_range_choices import STRING_RANGE_CHOICES
                        default_ranges = [{'id': str(i+1), 'range': choice[0]} 
                                         for i, choice in enumerate(STRING_RANGE_CHOICES)]
                        ranges_list = default_ranges[:6]  # Limit to 6 choices
                    except Exception as import_error:
                        # Absolute last resort - hardcoded common ranges
                        ranges_list = [
                            {'id': '1', 'range': 'e - g'},
                            {'id': '2', 'range': 'b - d'},
                            {'id': '3', 'range': 'g - A'},
                            {'id': '4', 'range': 'd - E'},
                            {'id': '5', 'range': 'A - B'},
                            {'id': '6', 'range': 'highA - e'}
                        ]
                
                # Make sure we have unique ranges (by range name)
                seen_ranges = set()
                unique_ranges = []
                for range_obj in ranges_list:
                    range_name = range_obj.get('range')
                    if range_name and range_name not in seen_ranges:
                        seen_ranges.add(range_name)
                        unique_ranges.append(range_obj)
                
                ranges_list = unique_ranges
                
                # Filter out 8-string specific ranges if in 6-string mode
                if is_six_string:
                    ranges_list = [r for r in ranges_list 
                                  if not (r.get('range') and 
                                         ('highA' in r.get('range') or 'lowB' in r.get('range')))]
                
                # Ensure reasonable limit (don't overwhelm the UI)
                if len(ranges_list) > 8:
                    ranges_list = ranges_list[:8]
                    
            except Exception as db_error:
                import traceback
                
                # Fallback to standard range options after error
                ranges_list = [
                    {'id': '1', 'range': 'e - g'},
                    {'id': '2', 'range': 'b - d'},
                    {'id': '3', 'range': 'g - A'},
                    {'id': '4', 'range': 'd - E'},
                    {'id': '5', 'range': 'A - B'}
                ]
            
            # Ensure we always have at least one range
            if not ranges_list:
                ranges_list = [{'id': '1', 'range': 'e - g'}]
                
                
            return Response({'ranges': ranges_list})
            
        except Exception as e:
            import traceback
            
            # Always return a standard set of ranges
            # If in 6-string mode, don't include 8-string ranges
            if is_six_string:
                emergency_ranges = [
                    {'id': '1', 'range': 'e - g'},
                    {'id': '2', 'range': 'b - d'},
                    {'id': '3', 'range': 'g - A'}
                ]
            else:
                emergency_ranges = [
                    {'id': '1', 'range': 'e - g'},
                    {'id': '2', 'range': 'b - d'},
                    {'id': '3', 'range': 'g - A'},
                    {'id': '4', 'range': 'highA - e'},
                    {'id': '5', 'range': 'e - lowB'}
                ]
                
            return Response({'ranges': emergency_ranges})


class ChordPositionsView(APIView):
    """API view to get chord positions/inversions based on ChordNotes ID."""
    permission_classes = []  # Override default permissions that require a queryset
    
    def get(self, request, format=None):
        
        try:
            chord_notes_id = request.query_params.get('chord_notes_id', None)
            if not chord_notes_id:
                # Try to get a valid ID from database instead of returning error
                try:
                    # Get first valid ID from database
                    sample_chord = ChordNotes.objects.first()
                    if sample_chord:
                        chord_notes_id = str(sample_chord.id)
                    else:
                        return Response({'error': 'Missing chord_notes_id and no database values found'}, 
                                       status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error': 'Missing required parameter: chord_notes_id'}, 
                                   status=status.HTTP_400_BAD_REQUEST)
    
            # Initialize positions list
            positions_list = []
    
            try:
                # Try to fetch positions from database
                
                # First try to get positions for the specific chord notes ID
                positions = ChordPosition.objects.filter(notes_name_id=chord_notes_id)\
                                                .order_by('inversion_order')\
                                                .values('inversion_order')
                
                # Convert to list for serializing
                positions_list = list(positions)
                
                if positions_list:
                    # Positions found, do nothing here for now
                    pass
                else:
                    # No positions found, proceed to check chord type
                    pass
                    
                    # If no positions found, check if chord exists and determine if it's a triad or seventh chord
                    try:
                        chord = ChordNotes.objects.get(id=chord_notes_id)
                        
                        # Check if it's a seventh chord based on fourth_note
                        is_seventh = chord.fourth_note is not None
                        
                        # Get common inversions from database based on other similar chords
                        if is_seventh:
                            # Find positions from other seventh chords
                            seventh_positions = ChordPosition.objects.filter(
                                notes_name__fourth_note__isnull=False
                            ).values('inversion_order').distinct().order_by('inversion_order')
                            
                            positions_list = list(seventh_positions)
                        else:
                            # Find positions from other triads
                            triad_positions = ChordPosition.objects.filter(
                                notes_name__fourth_note__isnull=True
                            ).values('inversion_order').distinct().order_by('inversion_order')
                            
                            positions_list = list(triad_positions)
                            
                        if not positions_list:
                            # Get all position types as last resort
                            all_positions = ChordPosition.objects.values('inversion_order').distinct().order_by('inversion_order')
                            positions_list = list(all_positions)
                            
                    except ChordNotes.DoesNotExist:
                        # Get all position types as fallback
                        all_positions = ChordPosition.objects.values('inversion_order').distinct().order_by('inversion_order')
                        positions_list = list(all_positions)
                    
                    # If still no positions found, use minimal fallback
                    if not positions_list:
                        positions_list = [{'inversion_order': 'Root Position'}]
                    
            except Exception as db_error:
                
                # Try to get ANY positions from database
                try:
                    all_positions = ChordPosition.objects.values('inversion_order').distinct().order_by('inversion_order')
                    positions_list = list(all_positions)
                    
                    if positions_list:
                        # Positions found, do nothing here, use the list
                        pass
                    else:
                        positions_list = [{'inversion_order': 'Root Position'}]
                except Exception:
                    positions_list = [{'inversion_order': 'Root Position'}]
            
            # Ensure we always have at least one position
            if not positions_list:
                positions_list = [{'inversion_order': 'Root Position'}]
                
            
            return Response({'positions': positions_list})
            
        except Exception as e:
            import traceback
            
            # Try to get positions from database even after critical error
            try:
                emergency_positions = list(ChordPosition.objects.values('inversion_order').distinct()[:3])
                if not emergency_positions:
                    emergency_positions = [{'inversion_order': 'Root Position'}]
            except Exception:
                emergency_positions = [{'inversion_order': 'Root Position'}]
                
            return Response({'positions': emergency_positions})


class ScalePositionsView(APIView):
    """API view to get scale positions based on Notes ID."""
    permission_classes = []  # Override default permissions that require a queryset
    
    def get(self, request, format=None):
        # Import required modules
        import traceback
        from positionfinder.models import Notes, NotesCategory
        from positionfinder.positions import NotesPosition
        
        
        notes_id = request.query_params.get('notes_id', None)
        if not notes_id:
            return Response({'error': 'Missing required parameter: notes_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Start with the "All Notes" position which is always included
            positions = [{'position_order': 0}]  # All Notes
            
            # Try to convert notes_id to int
            try:
                notes_id_int = int(notes_id)
                
                # Try to get the note object to determine its type and name
                try:
                    note = Notes.objects.get(id=notes_id_int)
                    
                    # Get all positions for this specific note from the database
                    db_positions = NotesPosition.objects.filter(notes_name_id=notes_id_int)\
                                                       .order_by('position_order')\
                                                       .values('position_order')\
                                                       .distinct()
                    
                    # Convert to list of dictionaries
                    db_positions_list = list(db_positions)
                    
                    if db_positions_list:
                        # Add all the database positions to our list
                        positions.extend(db_positions_list)
                    else:
                        
                        # Get positions for other scales/arpeggios of the same type
                        similar_notes = Notes.objects.filter(
                            category=note.category,
                            note_name=note.note_name
                        ).exclude(id=note.id)
                        
                        if similar_notes.exists():
                            similar_positions = NotesPosition.objects.filter(
                                notes_name__in=similar_notes
                            ).order_by('position_order').values('position_order').distinct()
                            
                            similar_positions_list = list(similar_positions)
                            if similar_positions_list:
                                positions.extend(similar_positions_list)
                            else:
                                # No similar positions found, do nothing here
                                pass
                        
                        # If still no positions, try to determine based on note name
                        if len(positions) <= 1:  # Only "All Notes" position
                            # Check note name to determine number of positions
                            note_name = note.note_name.lower()
                            
                            if 'major' in note_name and not 'pentatonic' in note_name:
                                # Major scale and modes typically have 7 positions
                                for i in range(1, 8):
                                    positions.append({'position_order': i})
                            elif 'blues' in note_name or 'pentatonic' in note_name:
                                # Blues and pentatonic scales typically have 5 positions
                                for i in range(1, 6):
                                    positions.append({'position_order': i})
                            elif note.category.category_name == 'Arpeggios':
                                # Arpeggios typically have 5 positions
                                for i in range(1, 6):
                                    positions.append({'position_order': i})
                            else:
                                # Default for other scales: 5 positions
                                for i in range(1, 6):
                                    positions.append({'position_order': i})
                
                except Notes.DoesNotExist:
                    # Use default positions for unknown scale/arpeggio
                    for i in range(1, 6):
                        positions.append({'position_order': i})
                
                except Exception as db_error:
                    # Use default positions on database error
                    for i in range(1, 6):
                        positions.append({'position_order': i})
                
            except ValueError as ve:
                # Fall back to default positions
                for i in range(1, 6):
                    positions.append({'position_order': i})
            
            # Deduplicate positions by position_order value
            seen = set()
            unique_positions = []
            for pos in positions:
                order = pos.get('position_order')
                if order not in seen:
                    seen.add(order)
                    unique_positions.append(pos)
            
            # Sort positions by position_order
            sorted_positions = sorted(unique_positions, key=lambda x: int(x.get('position_order', 0)))
            
            
            return Response({'positions': sorted_positions})
                
        except Exception as e:
            # Catch-all for any other errors
            
            # Always return a valid response with default positions even on error
            return Response({
                'positions': [
                    {'position_order': 0},  # All Notes
                    {'position_order': 1},
                    {'position_order': 2},
                    {'position_order': 3},
                    {'position_order': 4},
                    {'position_order': 5}
                ]
            })


class ArpeggioPositionsView(APIView):
    """API view to get arpeggio positions based on Notes ID."""
    permission_classes = []  # Override default permissions that require a queryset
    
    def get(self, request, format=None):
        # Import required modules for debugging
        import traceback
        import json
        from django.db import connection
        
        notes_id = request.query_params.get('notes_id', None)
        if not notes_id:
            return Response({'error': 'Missing required parameter: notes_id'}, status=status.HTTP_400_BAD_REQUEST)

        # Check the database structure to help debug
        try:
            # Log the models involved
            from positionfinder.models import Notes
            from positionfinder.positions import NotesPosition
            
            # Check if Notes table has entries
            notes_count = Notes.objects.count()
            
            # Check if NotesPosition table has entries
            positions_count = NotesPosition.objects.count()
            
            # Sample a few entries from Notes for debugging
            sample_notes = Notes.objects.filter(category__category_name='Arpeggios')[:5]
            for note in sample_notes:
                # Placeholder for processing each sample note if needed
                pass
                
            # Sample a few entries from NotesPosition for arpeggio notes
            if sample_notes.exists():
                sample_note_ids = [note.id for note in sample_notes]
                sample_positions = NotesPosition.objects.filter(notes_name_id__in=sample_note_ids)[:5]
                for pos in sample_positions:
                    # Placeholder for processing each sample position if needed
                    pass
        except Exception as struct_err:
            # Placeholder for handling structure errors if needed
            pass

        try:
            # Start with just "All Notes"
            positions = [{'position_order': 0}]  # All Notes
            
            # Try to convert notes_id to int first
            try:
                notes_id_int = int(notes_id)
                
                # For arpeggios, most have 5 positions by default
                # We can add special cases based on specific arpeggio types
                
                # Major and Minor arpeggios typically have 5 positions
                for i in range(1, 6):
                    positions.append({'position_order': i})
                
                # Try to get actual positions from database
                try:
                    note = Notes.objects.get(id=notes_id_int)
                    
                    # Debug the query
                    
                    # Show the raw SQL for debugging
                    qs = NotesPosition.objects.filter(notes_name_id=notes_id_int)
                    
                    # Check if any positions exist
                    if qs.exists():
                        # Get only the position_order values and order them
                        position_values = qs.order_by('position_order').values('position_order')
                        
                        
                        # Override the default positions with actual ones from DB
                        positions = [{'position_order': 0}]  # Keep "All Notes"
                        positions.extend(list(position_values))
                    else:
                        # Handle case where qs is empty if needed
                        pass
                except Exception as db_error:
                    # Keep the default positions set above
                    pass # Explicitly do nothing if DB error occurs
                
            except ValueError as ve:
                # Fall back to default arpeggio positions
                for i in range(1, 6):
                    positions.append({'position_order': i})
            
            # Always return a valid response
            return Response({'positions': positions})
                
        except Exception as e:
            # Catch-all for any other errors
            
            # Always return a valid response with default positions even on error
            return Response({
                'positions': [
                    {'position_order': 0},  # All Notes
                    {'position_order': 1},
                    {'position_order': 2},
                    {'position_order': 3},
                    {'position_order': 4},
                    {'position_order': 5}
                ]
            })
