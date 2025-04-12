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

# Constants (Keep from functional view)
NOTE_MAPPING = {
    'c': 'C', 'cs': 'C#', 'd': 'D', 'ds': 'D#', 'e': 'E', 'f': 'F',
    'fs': 'F#', 'g': 'G', 'gs': 'G#', 'a': 'A', 'as': 'A#', 'b': 'B',
    'db': 'Db', 'eb': 'Eb', 'gb': 'Gb', 'ab': 'Ab', 'bb': 'Bb'
}
NOTE_ORDER = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
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

    INVERSION_KEYS = {'Basic Position', 'First Inversion', 'Second Inversion', 'Third Inversion'}

    def extract_notes_from_position(positions):
        nonlocal root_note # Allow modification if root is found here
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

                # If this note is marked as the root, use it to establish context
                if is_root_note_flag and not root_note:
                     root_note = NOTE_MAPPING.get(note, note.capitalize())

                mapped_note = NOTE_MAPPING.get(note, note.capitalize())
                notes.add(mapped_note)

    def traverse(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in INVERSION_KEYS and isinstance(value, list): # Check if value is a list (of position dicts)
                    extract_notes_from_position(value)
                # Check if the key itself is a range name (like 'e - g')
                elif isinstance(value, dict) and any(inv_key in value for inv_key in INVERSION_KEYS):
                     # If the value is a dictionary containing inversion keys, traverse it
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
        else:
            pass # No action needed if root_note is not found initially


    # Traverse the entire data structure to find notes within inversions
    traverse(json_data)

    valid_notes = {note for note in notes if note in NOTE_ORDER}

    if root_note and root_note in NOTE_ORDER:
        note_order_list = get_note_order(root_note)
        sorted_notes = sorted(list(valid_notes), key=lambda x: note_order_list.index(x) if x in note_order_list else float('inf'))
    else:
        sorted_notes = sorted(list(valid_notes), key=lambda x: NOTE_ORDER.index(x) if x in NOTE_ORDER else float('inf'))

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

        # Ensure category_id is correctly set if coming from URL
        if 'models_select' in request.GET:
             params['category_id'] = int(request.GET['models_select'])
        else:
             params['category_id'] = 3 # Default for chords

        # The 'range' variable used in functional view needs careful handling
        # Let's stick to 'selected_range' as the primary variable after defaulting
        params['range'] = params['selected_range'] # Keep 'range' key for compatibility if needed internally

        return params # No separate apply_defaults needed if handled here

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
        """Get available chord type options, ordered like functional view"""
        all_type_names = ChordNotes.objects.values_list('type_name', flat=True).distinct()
        ordered_types = []
        # Add standard types in specific order
        if 'Triads' in all_type_names: ordered_types.append('Triads')
        if 'Spread Triads' in all_type_names: ordered_types.append('Spread Triads')
        if 'V1' in all_type_names: ordered_types.append('V1')
        if 'V2' in all_type_names: ordered_types.append('V2')
        # Add remaining types
        for t in all_type_names:
            if t not in ordered_types:
                ordered_types.append(t)
        # Ensure Triads is present even if not in DB initially (as fallback)
        if 'Triads' not in ordered_types:
             ordered_types.insert(0, 'Triads')
        return ordered_types

    def get_range_options(self, type_name, chord_name):
        """Get range options for the current chord selection, sorted like functional view"""
        range_options_queryset = ChordNotes.objects.filter(
            type_name=type_name,
            chord_name=chord_name
        ).order_by('ordering', 'range_ordering')

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

        # Fetch range options based on the determined type/name
        range_options = []
        if initial_chord_object:
             range_options = self.get_range_options(initial_chord_object.type_name, initial_chord_object.chord_name)
        else:
             # Attempt to get ranges based on selected type/name if initial object failed
             range_options = self.get_range_options(type_id, chord_select_name)


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
            final_chord_json_data[current_range_value] = inversion_data_for_range

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

        # Determine 8-string status
        is_eight_string = any('lowB' in option.range or 'highA' in option.range for option in range_options)

        # V1/V2 existence flags
        v1_data_exists = ChordNotes.objects.filter(type_name='V1').exists()
        v2_data_exists = ChordNotes.objects.filter(type_name='V2').exists()

        # Chord function generation (simplified example, needs full logic from functional view)
        # TODO: Integrate the full chord function generation logic here if needed
        chord_function = "R-..." # Placeholder

        # Build the final context dictionary, matching functional view keys
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
            'type_options': type_options,
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
            'v1_data_exists': v1_data_exists,
            'v2_data_exists': v2_data_exists,
            'is_eight_string': is_eight_string, # Add flag
            'DEBUG': settings.DEBUG # Use Django settings DEBUG
        }

        # Add common context from helper
        common_context_data = get_common_context(request)
        context.update(common_context_data)

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
def fretboard_chords_view(request: HttpRequest):
    """
    View function for displaying chords on the fretboard using ChordView.
    """
    chord_view = ChordView()
    return chord_view.render(request)
