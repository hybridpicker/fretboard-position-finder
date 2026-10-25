import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError

from .functionality_tones_setup import (
    get_functionality_note_names,
    get_functionality_pitches,
    get_functionality_tones,
)
from .get_position import get_notes_position
from .get_position_dict_scales import (
    get_scale_position_dict,
    get_transposable_positions,
    re_ordering_positions,
    transpose_actual_position,
)
from .models import Notes, NotesCategory, Root
from .note_setup import get_notes_tones
from .positions import NotesPosition
from .root_note_setup import get_root_note
from .template_notes import ALL_NOTES_POSITION
from .views_helpers import get_common_context

# String names (mirror-reversed for the template)
STRING_NAMES = [
    "lowBString",
    "ELowString",
    "AString",
    "dString",
    "gString",
    "bString",
    "eString",
    "highAString",
]


class MusicalTheoryView:
    """
    Base class for all musical theory views (scales, arpeggios, chords)
    Centralizes common functionality and standardizes request handling
    """

    def __init__(self, category_id: int, template_name: str = "fretboard.html") -> None:
        """
        Initialize with category ID and template name

        Args:
            category_id: ID for the specific musical category (1=scales, 2=arpeggios, 3=chords)
            template_name: The template to render
        """
        self.category_id = category_id
        self.template_name = template_name
        self.all_notes_position = ALL_NOTES_POSITION

    def process_request(self, request: HttpRequest) -> dict:
        """
        Process GET parameters with standardized error handling

        Args:
            request: The HTTP request object

        Returns:
            Dictionary of processed parameters with defaults applied
        """
        params = {
            "root_id": self._get_request_param(request, "root", 1),
            "category_id": self._get_request_param(request, "models_select", self.category_id),
            "position_id": self._get_request_param(request, "position_select", "0"),
            "notes_options_id": self._get_request_param(request, "notes_options_select", None),
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
        if request.method != "GET":
            return default_value

        try:
            value = request.GET[param_name]
            return value
        except (MultiValueDictKeyError, KeyError):
            return default_value

    def apply_defaults(self, params: dict) -> dict:
        """
        Apply category-specific defaults to parameters

        Args:
            params: Dictionary of request parameters

        Returns:
            Updated parameter dictionary
        """
        # Override in subclasses
        return params

    def get_position_data(
        self, notes_options_id: str | int | None, root_pitch: int, position_id: str = "0"
    ) -> object:
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
            if position_id != "0":
                position = get_notes_position(position_id, root_pitch)
            else:
                position = self.all_notes_position
        except ObjectDoesNotExist:
            position = self.all_notes_position

        return position

    def build_position_json(
        self,
        selected_notes_name: str,
        selected_root_id: int,
        root_pitch: int,
        tonal_root: int,
        selected_root_name: str,
        notes_options_id: str | int | None,
    ) -> str:
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
            selected_notes_name, selected_root_id, root_pitch, tonal_root, selected_root_name
        )

        # Process position data if we have more than one position and it's not an arpeggio
        if len(position_json_data) > 1 and self.category_id != 2:
            try:
                x = Notes.objects.get(id=notes_options_id).note_name
                y = len(NotesPosition.objects.all().filter(notes_name__note_name=x))
                transposable_position = get_transposable_positions(y, position_json_data)
                position_json_data = transpose_actual_position(
                    position_json_data, transposable_position
                )
                position_json_data = re_ordering_positions(position_json_data)
            except Notes.DoesNotExist:
                # Skip position processing for arpeggios or if notes don't exist
                pass

        # Add metadata to position data
        selected_root_options = get_root_note(root_pitch, tonal_root, selected_root_id)
        position_json_data["name"] = selected_notes_name
        position_json_data["root"] = selected_root_options

        return json.dumps(position_json_data)

    def _resolve_options(self, category_id, notes_options_id, position_id):
        """Return (notes_options, position_options, position_id) for the category."""
        # For arpeggios (category_id=2), use Notes model with arpeggio category
        if int(category_id) == 2:
            # Find arpeggio category
            arpeggio_category = NotesCategory.objects.filter(
                category_name__icontains="arpeggio"
            ).first()
            if arpeggio_category:
                notes_options = Notes.objects.filter(category=arpeggio_category)
            else:
                notes_options = Notes.objects.none()
            position_options = []  # TODO: implement arpeggio positions
        else:
            # For scales and chords, use Notes
            notes_options = Notes.objects.filter(category_id=category_id)
            position_options = NotesPosition.objects.filter(notes_name=notes_options_id)

            # Check if the requested position_id exists within the available options for the selected notes
            # Fallback to 'All Notes' ('0') if the specific position doesn't exist to prevent DoesNotExist error
            if position_id != "0" and not position_options.filter(pk=position_id).exists():
                position_id = "0"
        return notes_options, position_options, position_id

    def _selected_notes_name(self, notes_options_id, category_id):
        """Get the name of the selected notes - Use Notes model for all categories."""
        try:
            return Notes.objects.get(pk=notes_options_id).note_name
        except Notes.DoesNotExist:
            # For arpeggios, try to lookup by ID directly in the get_scale_position_dict function
            if int(category_id) == 2:
                return str(notes_options_id)  # Pass the ID directly to get_scale_position_dict
            return "Unknown"

    def _compute_template_data(
        self, root_obj, root_id, category_id, position_id, notes_options_id
    ) -> dict:
        """Compute tones, tensions, positions and JSON data for the template."""
        root_pitch = root_obj.pitch
        data: dict = {}
        # Calculate data for template
        tonal_root = 0  # Default tonal root
        data["tones"] = get_notes_tones(notes_options_id, root_pitch, tonal_root, root_id)
        data["tensions"] = get_functionality_tones(notes_options_id, root_pitch)
        data["root"] = get_root_note(root_pitch, tonal_root, root_id)
        data["position"] = self.get_position_data(notes_options_id, root_pitch, position_id)

        # Common metadata
        data["selected_category_name"] = NotesCategory.objects.get(pk=category_id).category_name

        # Format position name
        if position_id != "0":
            NotesPosition.objects.get(pk=position_id)  # raises if the position does not exist

        data["selected_notes_name"] = self._selected_notes_name(notes_options_id, category_id)

        # Prepare functionality data
        data["note_names"] = get_functionality_note_names(
            notes_options_id, root_pitch, tonal_root, root_id
        )
        data["tension_pitches"] = get_functionality_pitches(notes_options_id, root_pitch)

        # Build position data JSON
        data["scale_json_data"] = self.build_position_json(
            data["selected_notes_name"],
            root_obj.id,
            root_pitch,
            tonal_root,
            root_obj.name,
            notes_options_id,
        )
        return data

    def get_context(self, request: HttpRequest, params: dict) -> dict:
        """
        Build common template context

        Args:
            request: The HTTP request object
            params: Dictionary of processed parameters

        Returns:
            Dictionary with context data for template rendering
        """
        # Extract parameters
        root_id = params["root_id"]
        category_id = params["category_id"]
        position_id = params["position_id"]
        notes_options_id = params["notes_options_id"]

        # Get DB objects
        root_obj = Root.objects.get(pk=root_id)
        root_pitch = root_obj.pitch
        print(f"[ROOT DEBUG] Context root_id={root_id} -> Root: {root_obj} (pitch={root_pitch})")

        notes_options, position_options, position_id = self._resolve_options(
            category_id, notes_options_id, position_id
        )

        data = self._compute_template_data(
            root_obj, root_id, category_id, position_id, notes_options_id
        )

        # Base context
        context = {
            "scale_json_data": data["scale_json_data"],
            "tension_json_data": json.dumps({"tensions": data["tensions"]}),
            "note_name_json_data": json.dumps({"tones": data["note_names"]}),
            "tones": data["tones"],
            "root": data["root"],
            "root_options": Root.objects.all(),
            "position_options": position_options,
            "position": data["position"],
            "category": NotesCategory.objects.all(),
            "selected_category": int(category_id),
            "notes_options": notes_options,
            "selected_notes": int(notes_options_id),
            "selected_position": position_id if position_id is not None else "0",
            "tensions": data["tensions"],
            "tension_pitches": data["tension_pitches"],
            "note_names": data["note_names"],
            "selected_root_name": root_obj.name,
            "selected_root_id": root_obj.id,
            "selected_category_name": data["selected_category_name"],
            "selected_notes_name": data["selected_notes_name"],
            "string_names": list(STRING_NAMES),  # mirror-reversed for the template
        }

        # Add common context from helper
        context.update(get_common_context(request))

        return context

    def render(self, request: HttpRequest) -> HttpResponse:
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

    def add_view_specific_context(self, context: dict, params: dict) -> dict:
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
