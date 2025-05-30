import json
from django.http import HttpRequest, Http404
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.conf import settings

# Model imports
from .models import Root, NotesCategory
from .models_chords import ChordNotes, ChordPosition

# Helper function imports
from .root_chord_note_setup import get_root_note # Used in functional view, might not be needed directly in CBV context building
from .get_position_dict_chords import get_position_dict
from .note_validation import validate_and_filter_note_positions # Import validation function
from .views_helpers import get_common_context # Use current helper function
from .views_base import MusicalTheoryView # Import base class

import re # Import regex for natural sorting

# Constants (Keep from functional view)
NOTE_MAPPING = {
    'c': 'C', 'cs': 'C#', 'd': 'D', 'ds': 'D#', 'e': 'E', 'f': 'F',
    'fs': 'F#', 'g': 'G', 'gs': 'G#', 'a': 'A', 'as': 'A#', 'b': 'B',
    'db': 'Db', 'eb': 'Eb', 'gb': 'Gb', 'ab': 'Ab', 'bb': 'Bb'
}
NOTE_ORDER = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']

# Enharmonic equivalents
FLAT_ENHARMONICS = {
    'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb'
}
SHARP_ENHARMONICS = {
    'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
}
NOTE_RANGE_ORDER = [
    'highA - g', 'e - d', 'b - A', 'g - E', 'd - lowB', 'highA - lowB',
    'highA - b', 'highA - e', 'a - b', 'highA - A', 'highA - E',
    'e - g', 'e - A', 'e - E', 'e - B', 'e - lowB',
    'b - d', 'b - E', 'b - B', 'b - lowB',
    'g - A', 'g - B', 'g - lowB', 'd - E', 'd - B', 'A - B', 'A - lowB', 'E - lowB'
]

# Helper functions (Keep from functional view)
def get_note_order(root_note):
    """Get reordered notes starting from the root note"""
    try:
        start_index = NOTE_ORDER.index(root_note)
        return NOTE_ORDER[start_index:] + NOTE_ORDER[:start_index]
    except ValueError:
        return NOTE_ORDER

def extract_and_convert_notes(json_data):
    """Extract and normalize notes from chord JSON data."""
    notes = set()
    root_note = None
    print(f"DEBUG: Processing chord data: {json_data.get('chord', 'Unknown')} in {json_data.get('type', 'Unknown')}")

    INVERSION_KEYS = {'Basic Position', 'First Inversion', 'Second Inversion', 'Third Inversion'}

    def extract_notes_from_position(positions):
        nonlocal root_note # Allow modification if root is found here
        print(f"DEBUG: Extract notes from positions: {positions}")
        for position_data in positions: # positions is now a list containing one dict
             for string, note_info in position_data.items():
                if not note_info or not isinstance(note_info, list) or string == 'assigned_strings':
                    continue
                if not note_info[0]: continue
                if 'String' in str(note_info[0]): continue

                note = str(note_info[0]).lower().rstrip('0123456789-')
                if not note or not note[0].lower() in 'abcdefg': continue

                # Use function value for validation if available
                function = note_info[1] if len(note_info) > 1 else None
                is_root_note_flag = note_info[3] if len(note_info) > 3 else False

                print(f"DEBUG: Found note: {note}, function: {function}, is_root: {is_root_note_flag}")

                # If this note is marked as the root, use it to establish context
                if is_root_note_flag and not root_note:
                     root_note = NOTE_MAPPING.get(note, note.capitalize())

                mapped_note = NOTE_MAPPING.get(note, note.capitalize())
                notes.add(mapped_note)
                print(f"DEBUG: Added note {mapped_note} to notes set")

    def traverse(data):
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"DEBUG: Traversing key: {key}")
                if key in INVERSION_KEYS and isinstance(value, list): # Check if value is a list (of position dicts)
                    print(f"DEBUG: Found inversion key: {key}")
                    extract_notes_from_position(value)
                # Check if the key itself is a range name (like 'e - g')
                elif isinstance(value, dict) and any(inv_key in value for inv_key in INVERSION_KEYS):
                     # If the value is a dictionary containing inversion keys, traverse it
                     print(f"DEBUG: Found range with inversions: {key}")
                     traverse(value)
                elif isinstance(value, (dict, list)):
                     traverse(value) # Recursively traverse other dicts/lists
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    traverse(item)

    # Process root note from top level if present (important for context)
    if "root" in json_data and isinstance(json_data["root"], list) and len(json_data["root"]) > 0:
        root_note_full = json_data["root"][0].lower().rstrip('0123456789-')
        root_note = NOTE_MAPPING.get(root_note_full, root_note_full.capitalize())
        if root_note:
             notes.add(root_note)
             print(f"DEBUG: Added root note {root_note} from top level")
        else:
            print(f"DEBUG: Failed to process root note from top level")


    # Traverse the entire data structure to find notes within inversions
    traverse(json_data)

    valid_notes = {note for note in notes if note in NOTE_ORDER}
    print(f"DEBUG: Valid notes after traversal: {valid_notes}")

    if root_note and root_note in NOTE_ORDER:
        note_order_list = get_note_order(root_note)
        sorted_notes = sorted(list(valid_notes), key=lambda x: note_order_list.index(x) if x in note_order_list else float('inf'))
    else:
        sorted_notes = sorted(list(valid_notes), key=lambda x: NOTE_ORDER.index(x) if x in NOTE_ORDER else float('inf'))

    print(f"DEBUG: Final sorted notes: {sorted_notes}")
    
    # Remove enharmonic duplicates (like A# and Bb appearing together)
    # and standardize based on chord type and root note
    
    # First, fix potential root note issues
    root_candidate = None
    for note in sorted_notes:
        # If we find the actual root note in our list
        if root_note and (note == root_note or 
                          (note in FLAT_ENHARMONICS and FLAT_ENHARMONICS[note] == root_note) or
                          (note in SHARP_ENHARMONICS and SHARP_ENHARMONICS[note] == root_note)):
            root_candidate = note
            break
    
    # Use the first note as root if we couldn't find a match
    if not root_candidate and sorted_notes:
        root_candidate = sorted_notes[0]
    
    # Handle standard note naming based on chord type
    standardized_notes = []
    chord_type = json_data.get('chord', '').lower()
    
    # Decide if we should prefer flat or sharp names
    prefer_flats = any(term in chord_type for term in ['minor', 'min', 'dim', 'b5', 'b7', 'b9', 'b13'])
    
    # Clean duplicates and standardize names
    seen = set()
    for note in sorted_notes:
        # Skip if we've already seen this note or its enharmonic equivalent
        if note in seen:
            continue
            
        # Mark this note and its enharmonic equivalent as seen
        seen.add(note)
        if note in FLAT_ENHARMONICS:
            seen.add(FLAT_ENHARMONICS[note])
        elif note in SHARP_ENHARMONICS:
            seen.add(SHARP_ENHARMONICS[note])
            
        # Choose preferred spelling
        if prefer_flats and note in SHARP_ENHARMONICS:
            # Use flat name for sharps (C# -> Db)
            standardized_notes.append(SHARP_ENHARMONICS[note])
        elif not prefer_flats and note in FLAT_ENHARMONICS:
            # Use sharp name for flats (Db -> C#)
            standardized_notes.append(FLAT_ENHARMONICS[note])
        else:
            # Keep original spelling
            standardized_notes.append(note)
    
    # Re-sort notes if needed
    if root_note and root_note in NOTE_ORDER:
        note_order_list = get_note_order(root_note)
        standardized_notes.sort(key=lambda x: note_order_list.index(x) if x in note_order_list else float('inf'))
    
    # Use the standardized list
    sorted_notes = standardized_notes
    
    # CRITICAL FIX: Special handling for problematic chords
    chord_name = json_data.get('chord', '')
    # Handle special case for Minor 7b5 - always force correct notes
    if chord_name == 'Minor 7b5' or chord_name == 'Min7b5' or 'minor 7b5' in chord_name.lower():
        if root_note:
            print(f"DEBUG: Special handling for {chord_name} chord")
            
            # Always standardize root to flat version for Minor 7b5 
            if root_note in SHARP_ENHARMONICS:
                standardized_root = SHARP_ENHARMONICS[root_note]
            else:
                standardized_root = root_note
                
            # For standardized flat-based roots, use predefined note patterns
            if standardized_root == 'C':
                sorted_notes = ['C', 'Eb', 'Gb', 'Bb']
            elif standardized_root == 'D':
                sorted_notes = ['D', 'F', 'Ab', 'C']
            elif standardized_root == 'E':
                sorted_notes = ['E', 'G', 'Bb', 'D']
            elif standardized_root == 'F':
                sorted_notes = ['F', 'Ab', 'B', 'Eb']
            elif standardized_root == 'G':
                sorted_notes = ['G', 'Bb', 'Db', 'F']
            elif standardized_root == 'A':
                sorted_notes = ['A', 'C', 'Eb', 'G']
            elif standardized_root == 'B':
                sorted_notes = ['B', 'D', 'F', 'A']
            elif standardized_root == 'Bb':
                sorted_notes = ['Bb', 'Db', 'E', 'Ab']
            elif standardized_root == 'Eb':
                sorted_notes = ['Eb', 'Gb', 'A', 'Db']
            elif standardized_root == 'Ab':
                sorted_notes = ['Ab', 'B', 'D', 'Gb']
            elif standardized_root == 'Db':
                sorted_notes = ['Db', 'E', 'G', 'B']
            elif standardized_root == 'Gb':
                sorted_notes = ['Gb', 'A', 'C', 'E']
            else:
                # Generic calculation for any root
                note_idx = NOTE_ORDER.index(root_note)
                # Always use the flat versions (b3, b5, b7) for consistency
                flat_notes = []
                # Root note
                flat_notes.append(root_note)
                # b3 - minor third
                if 'b' in root_note or '#' in root_note:
                    # Specify exact notes for enharmonic roots
                    if root_note == 'C#' or root_note == 'Db':
                        flat_notes.append('E')
                    elif root_note == 'D#' or root_note == 'Eb':
                        flat_notes.append('Gb')
                    elif root_note == 'F#' or root_note == 'Gb':
                        flat_notes.append('A')
                    elif root_note == 'G#' or root_note == 'Ab':
                        flat_notes.append('B')
                    elif root_note == 'A#' or root_note == 'Bb':
                        flat_notes.append('Db')
                else:
                    # For natural notes, just use index calculation
                    minor_third_idx = (note_idx + 3) % len(NOTE_ORDER)
                    flat_notes.append(NOTE_ORDER[minor_third_idx])
                
                # b5 - diminished fifth
                if 'b' in root_note or '#' in root_note:
                    # Specify exact notes for enharmonic roots
                    if root_note == 'C#' or root_note == 'Db':
                        flat_notes.append('G')
                    elif root_note == 'D#' or root_note == 'Eb':
                        flat_notes.append('A')
                    elif root_note == 'F#' or root_note == 'Gb':
                        flat_notes.append('C')
                    elif root_note == 'G#' or root_note == 'Ab':
                        flat_notes.append('D')
                    elif root_note == 'A#' or root_note == 'Bb':
                        flat_notes.append('E')
                else:
                    # For natural notes, just use index calculation
                    dim_fifth_idx = (note_idx + 6) % len(NOTE_ORDER)
                    flat_notes.append(NOTE_ORDER[dim_fifth_idx])
                
                # b7 - minor seventh
                if 'b' in root_note or '#' in root_note:
                    # Specify exact notes for enharmonic roots
                    if root_note == 'C#' or root_note == 'Db':
                        flat_notes.append('B')
                    elif root_note == 'D#' or root_note == 'Eb':
                        flat_notes.append('Db')
                    elif root_note == 'F#' or root_note == 'Gb':
                        flat_notes.append('E')
                    elif root_note == 'G#' or root_note == 'Ab':
                        flat_notes.append('Gb')
                    elif root_note == 'A#' or root_note == 'Bb':
                        flat_notes.append('Ab')
                else:
                    # For natural notes, just use index calculation
                    minor_seventh_idx = (note_idx + 10) % len(NOTE_ORDER)
                    flat_notes.append(NOTE_ORDER[minor_seventh_idx])
                
                sorted_notes = flat_notes
                
            print(f"DEBUG: Fixed {chord_name} chord notes: {sorted_notes}")
    
    # Return only unique notes in order
    return sorted_notes


# Class Based View (Merging functional logic into CBV structure)
class ChordView(MusicalTheoryView):
    """
    View class for handling chord-related functionality.
    Merges logic from the previously working functional view.
    """

    def __init__(self):
        """Initialize with chords category ID (3)"""
        super().__init__(category_id=3) # Assuming MusicalTheoryView handles this

    # Keep helper from previous CBV attempts
    def _get_request_param(self, request, param_name, default=None):
        """Helper to get GET parameters with a default."""
        return request.GET.get(param_name, default)

    def process_request(self, request):
        """
        Process request parameters, mirroring the functional view's logic.
        """
        params = {}
        # Mirror defaults and extraction from functional view
        params['root_id'] = int(self._get_request_param(request, 'root', 1))
        params['category_id'] = int(self._get_request_param(request, 'models_select', 3))
        params['type_id'] = self._get_request_param(request, 'type_options_select', 'Triads') # Default from functional view was Triads
        params['chord_select_name'] = self._get_request_param(request, 'chords_options_select', 'Major') # Default from functional view was Major
        params['selected_range'] = self._get_request_param(request, 'note_range', 'e - g') # Default range
        params['position_select'] = self._get_request_param(request, 'position_select', 'Root Position') # Default from functional view
        
        # Check for string configuration (6 or 8 string)
        # First try to get from cookie
        string_config = self._get_string_config_from_cookie(request)
        params['is_six_string'] = string_config != 'eight-string'  # True if not explicitly 'eight-string'

        # Ensure category_id is correctly set if coming from URL
        if 'models_select' in request.GET:
             params['category_id'] = int(request.GET['models_select'])
        else:
             params['category_id'] = 3 # Default for chords

        # The 'range' variable used in functional view needs careful handling
        # Let's stick to 'selected_range' as the primary variable after defaulting
        params['range'] = params['selected_range'] # Keep 'range' key for compatibility if needed internally

        return params # No separate apply_defaults needed if handled here
    
    def _get_string_config_from_cookie(self, request):
        """Get string configuration from cookies"""
        string_config = request.COOKIES.get('stringConfig', 'six-string')
        print(f"Views - String configuration from cookie: {string_config}")
        
        # Also check localStorage if available via JavaScript
        # This would require client-side interaction, we'll add debug output
        
        return string_config

    # --- Methods to fetch options (adapted from functional view / previous CBV attempts) ---

    def get_selected_root_object(self, root_id):
        """Get the selected root object by ID"""
        try:
            return Root.objects.get(id=root_id)
        except Root.DoesNotExist:
            return Root.objects.get(id=1) # Fallback

    def get_all_root_options(self):
        """Get all available root options"""
        return Root.objects.all()

    def get_category_objects(self):
        """Get all category objects"""
        return NotesCategory.objects.all()

    def get_chord_options(self, type_id):
        """Get chord options for the selected type, ordered"""
        return ChordNotes.objects.filter(type_name=type_id).values_list(
            'chord_name', flat=True
        ).order_by('chord_ordering').distinct()

    def get_type_options(self):
        """Get available chord type options, separated into standard and V-System."""
        # Fetch all distinct type names for category 3 (Chords)
        all_type_names = ChordNotes.objects.filter(category=3).values_list('type_name', flat=True).distinct()

        standard_types = []
        v_system_types = []

        # Separate types
        for t in all_type_names:
            if t in ['Triads', 'Spread Triads']:
                standard_types.append(t)
            elif t.startswith('V') and t[1:].isdigit(): # Check if it looks like a V-System type
                v_system_types.append(t)
            # else: # Handle other potential types if needed
            #     pass

        # Ensure standard types have a specific order
        ordered_standard_types = []
        if 'Triads' in standard_types: ordered_standard_types.append('Triads')
        if 'Spread Triads' in standard_types: ordered_standard_types.append('Spread Triads')

        # Ensure Triads is present even if not in DB initially (as fallback for UI?)
        if 'Triads' not in ordered_standard_types:
            ordered_standard_types.insert(0, 'Triads')

        # Ensure uniqueness before sorting, just in case the distinct query didn't work as expected
        unique_v_system_types = list(set(v_system_types))
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower()
                    for text in re.split('([0-9]+)', s)]

        v_system_types_sorted = sorted(unique_v_system_types, key=natural_sort_key)
        print(f"[DEBUG] UNIQUE V-System types sorted in get_type_options: {v_system_types_sorted}") # DEBUG

        return {
            'standard_types': ordered_standard_types,
            'v_system_types': v_system_types_sorted
        }

    def get_range_options(self, type_name, chord_name, is_six_string=True):
        """
        Get range options for the current chord selection, sorted like functional view
        
        Args:
            type_name: The chord type name
            chord_name: The chord name
            is_six_string: If True, filter out 8-string specific ranges
        """
        range_options_queryset = ChordNotes.objects.filter(
            type_name=type_name,
            chord_name=chord_name
        ).order_by('ordering', 'range_ordering')
        
        # Filter out 8-string specific ranges if in 6-string mode
        if is_six_string:
            # Exclude ranges containing 'highA' or 'lowB'
            range_options_queryset = range_options_queryset.exclude(
                range__contains='highA'
            ).exclude(
                range__contains='lowB'
            )

        def get_sort_key(range_option):
            range_value = range_option.range
            try:
                return NOTE_RANGE_ORDER.index(range_value)
            except ValueError:
                return 999 # Put unknown ranges at the end

        range_options = sorted(list(range_options_queryset), key=get_sort_key)
        return range_options

    # --- Method to generate position data for a SINGLE range (inner loop logic) ---
    def get_inversion_data_for_range(self, position_options, chord_name, current_range_value, type_name, root_pitch, tonal_root, selected_root_name):
        """
        Generates the dictionary of inversion data for a specific range.
        Mirrors the inner loop (lines 407-428) of the functional view.
        """
        range_data = {} # Holds data for all inversions within this range
        if not position_options:
             return {}

        for position in position_options:
            inversion_name = position.inversion_order
            try:
                # Get the position dictionary from the helper function
                position_dict = get_position_dict(
                    inversion_name,
                    chord_name,
                    current_range_value,
                    type_name,
                    root_pitch,
                    tonal_root,
                    selected_root_name
                )

                # Apply validation (ensure this function exists and is imported)
                validated_position = validate_and_filter_note_positions(position_dict)

                # Store validated data directly as an object, not wrapped in a list
                range_data[inversion_name] = validated_position

            except Exception as e:
                range_data[inversion_name] = {} # Add empty dict placeholder on error

        return range_data

    # --- Main Context Building Method ---
    def get_context(self, request):
        """
        Build the template context, mirroring the functional view's logic.
        """
        params = self.process_request(request)

        # Extract parameters from processed params
        root_id = params['root_id']
        category_id = params['category_id']
        type_id = params['type_id']
        chord_select_name = params['chord_select_name']
        selected_range_value = params['selected_range']
        selected_position_name = params['position_select'] # e.g., "Root Position"

        # --- Fetch initial objects and options (mirroring functional view) ---
        category_objects = self.get_category_objects()
        selected_root_object = self.get_selected_root_object(root_id)
        root_pitch = selected_root_object.pitch
        selected_root_name = selected_root_object.name
        all_root_options = self.get_all_root_options()
        type_options = self.get_type_options()
        chord_options = self.get_chord_options(type_id)

        # Fetch the initial ChordNotes object based on selected type/name/range
        # This determines the initial tonal_root and the set of positions (inversions)
        try:
            # Prioritize exact match for type, name, and selected range
            initial_chord_object = ChordNotes.objects.filter(
                type_name=type_id,
                chord_name=chord_select_name,
                range=selected_range_value
            ).first()

            # Fallback if no match for the specific range
            if not initial_chord_object:
                initial_chord_object = ChordNotes.objects.filter(
                    type_name=type_id,
                    chord_name=chord_select_name
                ).first()

            # Further fallback if still no match
            if not initial_chord_object:
                 initial_chord_object = ChordNotes.objects.filter(type_name=type_id).first()

            # Ultimate fallback
            if not initial_chord_object:
                 initial_chord_object = ChordNotes.objects.first()
                 if not initial_chord_object:
                      raise Http404("No ChordNotes found in the database.") # Critical error if DB is empty

            tonal_root = initial_chord_object.tonal_root
            # Fetch position options (inversions) based on this initial object
            position_options = list(ChordPosition.objects.filter(notes_name_id=initial_chord_object.id))

        except Exception as e:
            # Handle error gracefully, maybe set defaults or raise 404
            initial_chord_object = None
            tonal_root = 0
            position_options = []
            # Consider raising Http404 if essential data is missing

        # Get string config mode (6 or 8 string)
        is_six_string = params['is_six_string']
        
        # Fetch range options based on the determined type/name
        range_options = []
        if initial_chord_object:
             range_options = self.get_range_options(initial_chord_object.type_name, initial_chord_object.chord_name, is_six_string)
        else:
             # Attempt to get ranges based on selected type/name if initial object failed
             range_options = self.get_range_options(type_id, chord_select_name, is_six_string)


        # --- Build the comprehensive chord_json_data (mirroring functional view) ---
        final_chord_json_data = {
            "chord": chord_select_name,
            "type": type_id,
            "root": [selected_root_name, root_pitch], # Use list [name, pitch]
            "note_range": selected_range_value # The initially selected range
        }

        # Outer loop: Iterate through all available ranges for this chord
        for range_option in range_options:
            current_range_value = range_option.range
            # Call helper to get inversion data for this specific range
            # Pass the *consistent* position_options list and tonal_root
            inversion_data_for_range = self.get_inversion_data_for_range(
                position_options,
                chord_select_name,
                current_range_value,
                type_id, # Use the selected type_id
                root_pitch,
                tonal_root, # Use the consistent tonal_root
                selected_root_name
            )
            # --- DEBUG: Log inversion data for this range ---
            print(f"[VSystemDebug] Range: {current_range_value} inversion_data_for_range: {inversion_data_for_range}")
            final_chord_json_data[current_range_value] = inversion_data_for_range

        # --- DEBUG: Log final chord_json_data structure ---
        print(f"[VSystemDebug] final_chord_json_data: {json.dumps(final_chord_json_data, indent=2)}")
        # --- Extract notes and build final context ---
        selected_notes = []
        if final_chord_json_data:
            try:
                # Pass the whole structure as it was done in the functional view
                selected_notes = extract_and_convert_notes(final_chord_json_data)
            except Exception as e:
                # Optionally log the error or handle it
                # print(f"An error occurred during note extraction: {e}") # Example logging
                pass # Indicate that no specific action is taken here

        # Determine 8-string status based on cookie configuration rather than available ranges
        is_eight_string = not params['is_six_string']
        
        # Additional safety check: if we're in 6-string mode, force-filter the range options again
        # This ensures no 8-string ranges slip through any part of the code
        if params['is_six_string']:
            range_options = [option for option in range_options 
                             if 'lowB' not in option.range and 'highA' not in option.range]

        # Chord function generation
        chord_function = self.generate_chord_function(chord_select_name)

        # Build the final context dictionary, matching functional view keys
        # Import SEO helper functions
        from .views_helpers import generate_seo_data, generate_breadcrumbs
        
        # Generate SEO data
        seo_data = generate_seo_data('chord', 
            root=selected_root_name,
            chord_type=chord_select_name,
            chord_notes=selected_notes,
            positions=[{'position': p.inversion_order} for p in position_options]
        )
        
        # Generate breadcrumbs
        breadcrumbs_data = [
            ('/', 'Home'),
            ('/chords/', 'Chords'),
            (f'/chords/{selected_root_name.lower()}/', f'{selected_root_name} Chords'),
            (f'/chords/{selected_root_name.lower()}/{chord_select_name.lower().replace(" ", "-")}/', f'{selected_root_name} {chord_select_name}')
        ]
        
        # Page title and meta description
        page_title = f'{selected_root_name} {chord_select_name} Chord | Guitar Positions & Voicings'
        meta_description = f'Learn to play {selected_root_name} {chord_select_name} chord on guitar with our interactive tool. Multiple positions, voicings, and fingerings across the entire fretboard.'
        
        context = {
            'selected_chord': chord_select_name,
            'root_id': root_id,
            'root_name': selected_root_name,
            'root_options': all_root_options,
            # 'notes_options': ???, # What corresponds to this in functional view? Maybe ChordNotes.objects.filter(category=category_id)?
            'selected_category': category_id,
            'category': category_objects,
            'position_options': position_options, # Pass the list of position objects
            'range_options': range_options,
            'chord_type_options': type_options, # Use the key expected by the template
            'chord_json_data': json.dumps(final_chord_json_data),
            'chord_options': chord_options,
            'selected_type': type_id,
            # 'first_range_option': ???, # Logic for this was in functional view, add if needed
            'note_range': selected_range_value, # Use selected_range_value
            'selected_range': selected_range_value,
            'string_names': ["lowBString", "ELowString", "AString", "dString", "gString", "bString", "eString", "highAString"], # Keep static list
            # 'selected_type': type_id, # Already included
            'selected_notes': selected_notes,
            'selected_position': selected_position_name, # Pass the position name from params
            'chord_function': chord_function, # Add generated function
            'is_eight_string': is_eight_string, # Add flag
            'DEBUG': settings.DEBUG, # Use Django settings DEBUG
            
            # SEO specific context
            'page_title': page_title,
            'meta_description': meta_description,
            'meta_keywords': f'{selected_root_name} {chord_select_name} chord, {chord_select_name} guitar chord, guitar chord fingerings, guitar chord positions',
            'og_title': f'{selected_root_name} {chord_select_name} Chord | Guitar Positions',
            'og_description': f'Complete {selected_root_name} {chord_select_name} chord positions and voicings for guitar. Interactive fretboard visualization.',
            'twitter_title': f'{selected_root_name} {chord_select_name} Chord',
            'twitter_description': f'All {selected_root_name} {chord_select_name} chord voicings and positions.',
            'breadcrumbs': breadcrumbs_data,
            'structured_data': seo_data
        }

        # Add common context from helper
        common_context_data = get_common_context(request)
        context.update(common_context_data)

        if 'chord_type_options' in context and 'v_system_types' in context['chord_type_options']:
            print(f"[DEBUG] Final v_system_types in context: {context['chord_type_options']['v_system_types']}")
        else:
            print("[DEBUG] chord_type_options or v_system_types not found in final context")

        return context

    def render(self, request):
        """Render the template with the generated context."""
        try:
            context = self.get_context(request)
            return render(request, 'fretboard.html', context)
        except Http404 as e:
             # Handle cases where essential data isn't found
             # Render an error page or return a specific response
             # return render(request, 'error_page.html', {'message': str(e)})
             # For now, re-raise or handle as appropriate
             raise
        except Exception as e:
             # Log the full traceback
             import traceback
             traceback.print_exc()
             # Render a generic error page
             # return render(request, 'error_page.html', {'message': 'An unexpected error occurred.'})
             # For now, re-raise
             raise


# Keep the simple view function that uses the class
    def generate_chord_function(self, chord_name):
        """
        Generate chord function notation based on chord name.
        For example:
        - Major 7 -> R - 3 - 5 - 7
        - Minor 7 -> R - b3 - 5 - b7
        - etc.
        """
        # Basic chord functions based on common chord types
        chord_functions = {
            # Triads
            'Major': 'R - 3 - 5',
            'Minor': 'R - b3 - 5',
            'Diminished': 'R - b3 - b5',
            'Augmented': 'R - 3 - #5',
            'Sus2': 'R - 2 - 5',
            'Sus4': 'R - 4 - 5',
            
            # 7th chords
            'Major 7': 'R - 3 - 5 - 7',
            'Dominant 7': 'R - 3 - 5 - b7',
            'Minor 7': 'R - b3 - 5 - b7',
            'Minor Major 7': 'R - b3 - 5 - 7',
            'MinMaj 7': 'R - b3 - 5 - 7',  # Alternative name
            'Diminished 7': 'R - b3 - b5 - bb7',
            'Half-Diminished 7': 'R - b3 - b5 - b7',
            'Min7b5': 'R - b3 - b5 - b7',  # Alternative name
            'Minor 7b5': 'R - b3 - b5 - b7',  # Essential - this is what your chord is
            'Augmented 7': 'R - 3 - #5 - b7',
            'Augmented Major 7': 'R - 3 - #5 - 7',
            
            # 6th chords
            'Major 6': 'R - 3 - 5 - 6',
            'Minor 6': 'R - b3 - 5 - 6',
            
            # 9th chords
            'Major 9': 'R - 3 - 5 - 7 - 9',
            'Dominant 9': 'R - 3 - 5 - b7 - 9',
            'Minor 9': 'R - b3 - 5 - b7 - 9',
            
            # 11th chords
            'Major 11': 'R - 3 - 5 - 7 - 9 - 11',
            'Dominant 11': 'R - 3 - 5 - b7 - 9 - 11',
            'Minor 11': 'R - b3 - 5 - b7 - 9 - 11',
            
            # 13th chords
            'Major 13': 'R - 3 - 5 - 7 - 9 - 11 - 13',
            'Dominant 13': 'R - 3 - 5 - b7 - 9 - 11 - 13',
            'Minor 13': 'R - b3 - 5 - b7 - 9 - 11 - 13',
            
            # Altered chords
            'Major 7(#5)': 'R - 3 - #5 - 7',
            'Major 7(b5)': 'R - 3 - b5 - 7',
            'Dominant 7(#5)': 'R - 3 - #5 - b7',
            'Dominant 7(b5)': 'R - 3 - b5 - b7',
            'Dominant 7(b9)': 'R - 3 - 5 - b7 - b9',
            'Dominant 7(#9)': 'R - 3 - 5 - b7 - #9',
            'Dominant 7(#11)': 'R - 3 - 5 - b7 - #11',
            'Dominant 7(b13)': 'R - 3 - 5 - b7 - b13',
            
            # Add chords
            'Add9': 'R - 3 - 5 - 9',
            'Minor Add9': 'R - b3 - 5 - 9'
        }
        
        print(f"DEBUG: Generating chord function for chord name: '{chord_name}'")
        
        # Normalize chord name - remove any spaces and convert to lowercase for more flexible matching
        normalized_name = chord_name.lower().replace(" ", "")
        
        # Check for exact match first
        if chord_name in chord_functions:
            return chord_functions[chord_name]
            
        # Special case handling for Minor 7b5 which might be encoded differently
        if normalized_name == "minor7b5" or normalized_name == "min7b5" or "minor7b5" in normalized_name:
            return 'R - b3 - b5 - b7'
            
        # Return the function for the given chord name, or a default if not found
        result = chord_functions.get(chord_name, 'R - ...')
        print(f"DEBUG: Returning chord function: '{result}' for chord: '{chord_name}'")
        return result

def fretboard_chords_view(request: HttpRequest):
    """
    View function for displaying chords on the fretboard using ChordView.
    """
    chord_view = ChordView()
    return chord_view.render(request)
