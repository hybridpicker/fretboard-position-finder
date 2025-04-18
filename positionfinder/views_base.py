import json
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .models import Notes, NotesCategory, Root
from .positions import NotesPosition
from .note_setup import get_notes_tones
from .root_note_setup import get_root_note
from .functionality_tones_setup import get_functionality_tones, get_functionality_pitches, get_functionality_note_names
from .get_position import get_notes_position
from .template_notes import ALL_NOTES_POSITION
from .get_position_dict_scales import get_scale_position_dict, get_transposable_positions, transpose_actual_position, re_ordering_positions
from .views_helpers import get_common_context


class MusicalTheoryView:
    """
    Base class for all musical theory views (scales, arpeggios, chords)
    Centralizes common functionality and standardizes request handling
    """
    
    def __init__(self, category_id, template_name='fretboard.html'):
        """
        Initialize with category ID and template name
        
        Args:
            category_id: ID for the specific musical category (1=scales, 2=arpeggios, 3=chords)
            template_name: The template to render
        """
        self.category_id = category_id
        self.template_name = template_name
        self.all_notes_position = ALL_NOTES_POSITION
        
    def process_request(self, request):
        """
        Process GET parameters with standardized error handling
        
        Args:
            request: The HTTP request object
        
        Returns:
            Dictionary of processed parameters with defaults applied
        """
        params = {
            'root_id': self._get_request_param(request, 'root', 1),
            'category_id': self._get_request_param(request, 'models_select', self.category_id),
            'position_id': self._get_request_param(request, 'position_select', '0'),
            'notes_options_id': self._get_request_param(request, 'notes_options_select', None)
        }
        
        # Apply category-specific defaults
        return self.apply_defaults(params)
    
    def _get_request_param(self, request, param_name, default_value):
        """
        Helper method to safely get request parameters
        
        Args:
            request: The HTTP request object
            param_name: The name of the parameter to get
            default_value: Default value if parameter is missing
        
        Returns:
            The parameter value or default
        """
        if request.method != 'GET':
            return default_value
            
        try:
            value = request.GET[param_name]
            return value
        except (MultiValueDictKeyError, KeyError):
            return default_value
    
    def apply_defaults(self, params):
        """
        Apply category-specific defaults to parameters
        
        Args:
            params: Dictionary of request parameters
        
        Returns:
            Updated parameter dictionary
        """
        # Override in subclasses
        return params
    
    def get_position_data(self, notes_options_id, root_pitch, position_id='0'):
        """
        Get position data based on notes options and root pitch
        
        Args:
            notes_options_id: ID of the selected notes option
            root_pitch: Pitch of the selected root note
            position_id: Selected position ID, '0' for all notes
        
        Returns:
            Position data for the template
        """
        try:
            if position_id != '0':
                position = get_notes_position(position_id, root_pitch)
            else:
                position = self.all_notes_position
        except ObjectDoesNotExist:
            position = self.all_notes_position
            
        return position
        
    def build_position_json(self, selected_notes_name, selected_root_id, root_pitch, tonal_root, selected_root_name, notes_options_id):
        """
        Build position JSON data for the template
        
        Args:
            selected_notes_name: Name of the selected notes
            selected_root_id: ID of the selected root
            root_pitch: Pitch of the selected root note
            tonal_root: Tonal root offset
            selected_root_name: Name of the selected root
            notes_options_id: ID of the selected notes option
        
        Returns:
            JSON data for positions
        """
        position_json_data = get_scale_position_dict(
            selected_notes_name, 
            selected_root_id, 
            root_pitch, 
            tonal_root, 
            selected_root_name
        )
        
        # Process position data if we have more than one position and it's not an arpeggio
        if len(position_json_data) > 1 and self.category_id != 2:
            try:
                x = Notes.objects.get(id=notes_options_id).note_name
                y = len(NotesPosition.objects.all().filter(notes_name__note_name=x))
                transposable_position = get_transposable_positions(y, position_json_data)
                position_json_data = transpose_actual_position(position_json_data, transposable_position)
                position_json_data = re_ordering_positions(position_json_data)
            except Notes.DoesNotExist:
                # Skip position processing for arpeggios or if notes don't exist
                pass
        
        # Add metadata to position data
        selected_root_options = get_root_note(root_pitch, tonal_root, selected_root_id)
        position_json_data["name"] = selected_notes_name
        position_json_data["root"] = selected_root_options
        
        return json.dumps(position_json_data)
    
    def get_context(self, request, params):
        """
        Build common template context
        
        Args:
            request: The HTTP request object
            params: Dictionary of processed parameters
        
        Returns:
            Dictionary with context data for template rendering
        """
        # Extract parameters
        root_id = params['root_id']
        category_id = params['category_id']
        position_id = params['position_id']
        notes_options_id = params['notes_options_id']
        
        # Get DB objects
        root_obj = Root.objects.get(pk=root_id)
        root_pitch = root_obj.pitch
        print(f"[ROOT DEBUG] Context root_id={root_id} -> Root: {root_obj} (pitch={root_pitch})")
        
        # For arpeggios (category_id=2), use ChordNotes
        if int(category_id) == 2:
            from .models_chords import ChordNotes
            notes_options = ChordNotes.objects.filter(category_id=category_id)
            position_options = []  # TODO: implement arpeggio positions
        else:
            # For scales and chords, use Notes
            notes_options = Notes.objects.filter(category_id=category_id)
            position_options = NotesPosition.objects.filter(notes_name=notes_options_id)
            
            # Check if the requested position_id exists within the available options for the selected notes
            # Fallback to 'All Notes' ('0') if the specific position doesn't exist to prevent DoesNotExist error
            if position_id != '0' and not position_options.filter(pk=position_id).exists():
                position_id = '0'
        
        # Calculate data for template
        tonal_root = 0  # Default tonal root
        tones = get_notes_tones(notes_options_id, root_pitch, tonal_root, root_id)
        tensions = get_functionality_tones(notes_options_id, root_pitch)
        root = get_root_note(root_pitch, tonal_root, root_id)
        position = self.get_position_data(notes_options_id, root_pitch, position_id)
        
        # Common metadata
        selected_category_name = NotesCategory.objects.get(pk=category_id).category_name
        selected_root_name = root_obj.name
        selected_root_id = root_obj.id
        
        # Format position name
        if position_id != '0':
            selected_position_name = NotesPosition.objects.get(pk=position_id).position_order
            selected_position_name = f'Position: {selected_position_name}'
        else:
            selected_position_name = 'All Notes'
            
        # Get the name of the selected notes
        if int(category_id) == 2:  # Arpeggios
            from .models_chords import ChordNotes
            try:
                chord_notes = ChordNotes.objects.get(pk=notes_options_id)
                selected_notes_name = chord_notes.chord_name
            except ChordNotes.DoesNotExist:
                selected_notes_name = "Unknown Arpeggio"
        else:  # Scales or Chords
            try:
                selected_notes_name = Notes.objects.get(pk=notes_options_id).note_name
            except Notes.DoesNotExist:
                selected_notes_name = "Unknown"
        
        # Prepare functionality data
        note_names = get_functionality_note_names(notes_options_id, root_pitch, tonal_root, root_id)
        tension_pitches = get_functionality_pitches(notes_options_id, root_pitch)
        
        # Build JSON data
        tensions_json_data = {"tensions": tensions}
        tension_json_data = json.dumps(tensions_json_data)
        note_name_json_data = {"tones": note_names}
        note_name_json_data = json.dumps(note_name_json_data)
        
        # Build position data JSON
        scale_json_data = self.build_position_json(
            selected_notes_name,
            selected_root_id,
            root_pitch,
            tonal_root,
            selected_root_name,
            notes_options_id
        )
        
        # String names (mirror-reversed for the template)
        string_names = ["lowBString", "ELowString", "AString", "dString", "gString", "bString", "eString", "highAString"]
        
        # Base context
        context = {
            'scale_json_data': scale_json_data,
            'tension_json_data': tension_json_data,
            'note_name_json_data': note_name_json_data,
            'tones': tones,
            'root': root,
            'root_options': Root.objects.all(),
            'position_options': position_options,
            'position': position,
            'category': NotesCategory.objects.all(),
            'selected_category': int(category_id),
            'notes_options': notes_options,
            'selected_notes': int(notes_options_id),
            'selected_position': position_id if position_id is not None else '0',
            'tensions': tensions,
            'tension_pitches': tension_pitches,
            'note_names': note_names,
            'selected_root_name': selected_root_name,
            'selected_root_id': selected_root_id,
            'selected_category_name': selected_category_name,
            'selected_notes_name': selected_notes_name,
            'string_names': string_names,
        }
        
        # Add common context from helper
        common_context = get_common_context(request)
        context.update(common_context)
        
        return context
        
    def render(self, request):
        """
        Process request and render the template
        
        Args:
            request: The HTTP request object
        
        Returns:
            Rendered template response
        """
        params = self.process_request(request)
        context = self.get_context(request, params)
        
        # Allow subclasses to add view-specific context
        context = self.add_view_specific_context(context, params)
        
        return render(request, self.template_name, context)
    
    def add_view_specific_context(self, context, params):
        """
        Add view-specific context variables
        
        Args:
            context: Base context dictionary
            params: Dictionary of processed parameters
        
        Returns:
            Updated context dictionary
        """
        # Override in subclasses
        return context
