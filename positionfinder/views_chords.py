import json
import re  # Import regex for natural sorting

from django.conf import settings
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from .chord_note_extraction import (  # noqa: F401  (re-exported)
    FLAT_ENHARMONICS,
    INVERSION_KEYS,
    MINOR_7B5_NOTES,
    NOTE_MAPPING,
    NOTE_ORDER,
    SHARP_ENHARMONICS,
    extract_and_convert_notes,
    get_note_order,
)
from .get_position_dict_chords import get_position_dict

# Model imports
from .models import NotesCategory, Root
from .models_chords import ChordNotes, ChordPosition
from .note_validation import validate_and_filter_note_positions  # Import validation function

# Helper function imports
from .views_base import MusicalTheoryView  # Import base class
from .views_helpers import get_common_context  # Use current helper function

NOTE_RANGE_ORDER = [
    "highA - g",
    "e - d",
    "b - A",
    "g - E",
    "d - lowB",
    "highA - lowB",
    "highA - b",
    "highA - e",
    "a - b",
    "highA - A",
    "highA - E",
    "e - g",
    "e - A",
    "e - E",
    "e - B",
    "e - lowB",
    "b - d",
    "b - E",
    "b - B",
    "b - lowB",
    "g - A",
    "g - B",
    "g - lowB",
    "d - E",
    "d - B",
    "A - B",
    "A - lowB",
    "E - lowB",
]


def _natural_sort_key(s: str) -> list:
    """Sort key splitting digit runs so that V2 < V10."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split("([0-9]+)", s)]


def _range_sort_key(range_option) -> int:
    """Sort key placing ranges in NOTE_RANGE_ORDER (unknown ranges last)."""
    range_value = range_option.range
    try:
        return NOTE_RANGE_ORDER.index(range_value)
    except ValueError:
        return 999  # Put unknown ranges at the end


# Basic chord functions based on common chord types
CHORD_FUNCTIONS = {
    # Triads
    "Major": "R - 3 - 5",
    "Minor": "R - b3 - 5",
    "Diminished": "R - b3 - b5",
    "Augmented": "R - 3 - #5",
    "Sus2": "R - 2 - 5",
    "Sus4": "R - 4 - 5",
    # 7th chords
    "Major 7": "R - 3 - 5 - 7",
    "Dominant 7": "R - 3 - 5 - b7",
    "Minor 7": "R - b3 - 5 - b7",
    "Minor Major 7": "R - b3 - 5 - 7",
    "MinMaj 7": "R - b3 - 5 - 7",  # Alternative name
    "Diminished 7": "R - b3 - b5 - bb7",
    "Half-Diminished 7": "R - b3 - b5 - b7",
    "Min7b5": "R - b3 - b5 - b7",  # Alternative name
    "Minor 7b5": "R - b3 - b5 - b7",  # Essential - this is what your chord is
    "Augmented 7": "R - 3 - #5 - b7",
    "Augmented Major 7": "R - 3 - #5 - 7",
    # 6th chords
    "Major 6": "R - 3 - 5 - 6",
    "Minor 6": "R - b3 - 5 - 6",
    # 9th chords
    "Major 9": "R - 3 - 5 - 7 - 9",
    "Dominant 9": "R - 3 - 5 - b7 - 9",
    "Minor 9": "R - b3 - 5 - b7 - 9",
    # 11th chords
    "Major 11": "R - 3 - 5 - 7 - 9 - 11",
    "Dominant 11": "R - 3 - 5 - b7 - 9 - 11",
    "Minor 11": "R - b3 - 5 - b7 - 9 - 11",
    # 13th chords
    "Major 13": "R - 3 - 5 - 7 - 9 - 11 - 13",
    "Dominant 13": "R - 3 - 5 - b7 - 9 - 11 - 13",
    "Minor 13": "R - b3 - 5 - b7 - 9 - 11 - 13",
    # Altered chords
    "Major 7(#5)": "R - 3 - #5 - 7",
    "Major 7(b5)": "R - 3 - b5 - 7",
    "Dominant 7(#5)": "R - 3 - #5 - b7",
    "Dominant 7(b5)": "R - 3 - b5 - b7",
    "Dominant 7(b9)": "R - 3 - 5 - b7 - b9",
    "Dominant 7(#9)": "R - 3 - 5 - b7 - #9",
    "Dominant 7(#11)": "R - 3 - 5 - b7 - #11",
    "Dominant 7(b13)": "R - 3 - 5 - b7 - b13",
    # Add chords
    "Add9": "R - 3 - 5 - 9",
    "Minor Add9": "R - b3 - 5 - 9",
}


# Class Based View (Merging functional logic into CBV structure)
class ChordView(MusicalTheoryView):
    """
    View class for handling chord-related functionality.
    Merges logic from the previously working functional view.
    """

    def __init__(self) -> None:
        """Initialize with chords category ID (3)"""
        super().__init__(category_id=3)  # Assuming MusicalTheoryView handles this

    # Keep helper from previous CBV attempts
    def _get_request_param(self, request, param_name, default=None):
        """Helper to get GET parameters with a default."""
        return request.GET.get(param_name, default)

    def process_request(self, request: HttpRequest) -> dict:
        """
        Process request parameters, mirroring the functional view's logic.
        """
        params = {}
        # Mirror defaults and extraction from functional view
        params["root_id"] = int(self._get_request_param(request, "root", 1))
        params["category_id"] = int(self._get_request_param(request, "models_select", 3))
        params["type_id"] = self._get_request_param(
            request, "type_options_select", "Triads"
        )  # Default from functional view was Triads
        params["chord_select_name"] = self._get_request_param(
            request, "chords_options_select", "Major"
        )  # Default from functional view was Major
        params["selected_range"] = self._get_request_param(
            request, "note_range", "e - g"
        )  # Default range
        params["position_select"] = self._get_request_param(
            request, "position_select", "Root Position"
        )  # Default from functional view

        # Check for string configuration (6 or 8 string)
        # First try to get from cookie
        string_config = self._get_string_config_from_cookie(request)
        params["is_six_string"] = (
            string_config != "eight-string"
        )  # True if not explicitly 'eight-string'

        # Ensure category_id is correctly set if coming from URL
        if "models_select" in request.GET:
            params["category_id"] = int(request.GET["models_select"])
        else:
            params["category_id"] = 3  # Default for chords

        # The 'range' variable used in functional view needs careful handling
        # Let's stick to 'selected_range' as the primary variable after defaulting
        params["range"] = params[
            "selected_range"
        ]  # Keep 'range' key for compatibility if needed internally

        return params  # No separate apply_defaults needed if handled here

    def _get_string_config_from_cookie(self, request):
        """Get string configuration from cookies"""
        string_config = request.COOKIES.get("stringConfig", "six-string")
        print(f"Views - String configuration from cookie: {string_config}")

        # Also check localStorage if available via JavaScript
        # This would require client-side interaction, we'll add debug output

        return string_config

    # --- Methods to fetch options (adapted from functional view / previous CBV attempts) ---

    def get_selected_root_object(self, root_id: int) -> Root:
        """Get the selected root object by ID"""
        try:
            return Root.objects.get(id=root_id)
        except Root.DoesNotExist:
            return Root.objects.get(id=1)  # Fallback

    def get_all_root_options(self) -> QuerySet:
        """Get all available root options"""
        return Root.objects.all()

    def get_category_objects(self) -> QuerySet:
        """Get all category objects"""
        return NotesCategory.objects.all()

    def get_chord_options(self, type_id: str) -> QuerySet:
        """Get chord options for the selected type, ordered"""
        return (
            ChordNotes.objects.filter(type_name=type_id)
            .values_list("chord_name", flat=True)
            .order_by("chord_ordering")
            .distinct()
        )

    def get_type_options(self) -> dict:
        """Get available chord type options, separated into standard and V-System."""
        # Fetch all distinct type names for category 3 (Chords)
        all_type_names = (
            ChordNotes.objects.filter(category=3).values_list("type_name", flat=True).distinct()
        )

        standard_types = []
        v_system_types = []

        # Separate types
        for t in all_type_names:
            if t in ["Triads", "Spread Triads"]:
                standard_types.append(t)
            elif t.startswith("V") and t[1:].isdigit():  # Check if it looks like a V-System type
                v_system_types.append(t)

        # Ensure standard types have a specific order
        ordered_standard_types = []
        if "Triads" in standard_types:
            ordered_standard_types.append("Triads")
        if "Spread Triads" in standard_types:
            ordered_standard_types.append("Spread Triads")

        # Ensure Triads is present even if not in DB initially (as fallback for UI?)
        if "Triads" not in ordered_standard_types:
            ordered_standard_types.insert(0, "Triads")

        # Ensure uniqueness before sorting, just in case the distinct query didn't work as expected
        unique_v_system_types = list(set(v_system_types))

        v_system_types_sorted = sorted(unique_v_system_types, key=_natural_sort_key)
        print(
            f"[DEBUG] UNIQUE V-System types sorted in get_type_options: {v_system_types_sorted}"
        )  # DEBUG

        return {"standard_types": ordered_standard_types, "v_system_types": v_system_types_sorted}

    def get_range_options(
        self, type_name: str, chord_name: str, is_six_string: bool = True
    ) -> list:
        """
        Get range options for the current chord selection, sorted like functional view

        Args:
            type_name: The chord type name
            chord_name: The chord name
            is_six_string: If True, filter out 8-string specific ranges
        """
        range_options_queryset = ChordNotes.objects.filter(
            type_name=type_name, chord_name=chord_name
        ).order_by("ordering", "range_ordering")

        # Filter out 8-string specific ranges if in 6-string mode
        if is_six_string:
            # Exclude ranges containing 'highA' or 'lowB'
            range_options_queryset = range_options_queryset.exclude(
                range__contains="highA"
            ).exclude(range__contains="lowB")

        range_options = sorted(list(range_options_queryset), key=_range_sort_key)
        return range_options

    # --- Method to generate position data for a SINGLE range (inner loop logic) ---
    def get_inversion_data_for_range(
        self,
        position_options: list,
        chord_name: str,
        current_range_value: str,
        type_name: str,
        root_pitch: int,
        tonal_root: int,
        selected_root_name: str,
    ) -> dict:
        """
        Generates the dictionary of inversion data for a specific range.
        Mirrors the inner loop (lines 407-428) of the functional view.
        """
        range_data = {}  # Holds data for all inversions within this range
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
                    selected_root_name,
                )

                # Apply validation (ensure this function exists and is imported)
                validated_position = validate_and_filter_note_positions(position_dict)

                # Store validated data directly as an object, not wrapped in a list
                range_data[inversion_name] = validated_position

            except Exception:
                range_data[inversion_name] = {}  # Add empty dict placeholder on error

        return range_data

    def _fetch_initial_chord(self, type_id, chord_select_name, selected_range_value):
        """Find the initial ChordNotes object; returns (object, tonal_root, positions)."""
        try:
            # Prioritize exact match for type, name, and selected range
            initial_chord_object = ChordNotes.objects.filter(
                type_name=type_id, chord_name=chord_select_name, range=selected_range_value
            ).first()

            # Fallback if no match for the specific range
            if not initial_chord_object:
                initial_chord_object = ChordNotes.objects.filter(
                    type_name=type_id, chord_name=chord_select_name
                ).first()

            # Further fallback if still no match
            if not initial_chord_object:
                initial_chord_object = ChordNotes.objects.filter(type_name=type_id).first()

            # Ultimate fallback
            if not initial_chord_object:
                initial_chord_object = ChordNotes.objects.first()
                if not initial_chord_object:
                    raise Http404(
                        "No ChordNotes found in the database."
                    )  # Critical error if DB is empty

            tonal_root = initial_chord_object.tonal_root
            # Fetch position options (inversions) based on this initial object
            position_options = list(
                ChordPosition.objects.filter(notes_name_id=initial_chord_object.id)
            )

        except Exception:
            # Handle error gracefully (the Http404 above is swallowed here as well)
            initial_chord_object = None
            tonal_root = 0
            position_options = []

        return initial_chord_object, tonal_root, position_options

    def _build_chord_json_data(
        self,
        params: dict,
        range_options: list,
        position_options: list,
        tonal_root: int,
        root_pitch: int,
        selected_root_name: str,
    ) -> dict:
        """Build the chord JSON structure with inversion data for every range."""
        type_id = params["type_id"]
        chord_select_name = params["chord_select_name"]
        final_chord_json_data = {
            "chord": chord_select_name,
            "type": type_id,
            "root": [selected_root_name, root_pitch],  # Use list [name, pitch]
            "note_range": params["selected_range"],  # The initially selected range
        }

        # Outer loop: Iterate through all available ranges for this chord
        for range_option in range_options:
            current_range_value = range_option.range
            inversion_data_for_range = self.get_inversion_data_for_range(
                position_options,
                chord_select_name,
                current_range_value,
                type_id,  # Use the selected type_id
                root_pitch,
                tonal_root,  # Use the consistent tonal_root
                selected_root_name,
            )
            print(
                f"[VSystemDebug] Range: {current_range_value} inversion_data_for_range: {inversion_data_for_range}"
            )
            final_chord_json_data[current_range_value] = inversion_data_for_range

        print(
            f"[VSystemDebug] final_chord_json_data: {json.dumps(final_chord_json_data, indent=2)}"
        )
        return final_chord_json_data

    def _build_seo_context(
        self,
        selected_root_name: str,
        chord_select_name: str,
        selected_notes: list,
        position_options,
    ) -> dict:
        """Build the SEO-related template context entries."""
        # Import SEO helper functions
        from .views_helpers import generate_seo_data

        seo_data = generate_seo_data(
            "chord",
            root=selected_root_name,
            chord_type=chord_select_name,
            chord_notes=selected_notes,
            positions=[{"position": p.inversion_order} for p in position_options],
        )

        breadcrumbs_data = [
            ("/", "Home"),
            ("/chords/", "Chords"),
            (f"/chords/{selected_root_name.lower()}/", f"{selected_root_name} Chords"),
            (
                f"/chords/{selected_root_name.lower()}/{chord_select_name.lower().replace(' ', '-')}/",
                f"{selected_root_name} {chord_select_name}",
            ),
        ]

        return {
            "page_title": f"{selected_root_name} {chord_select_name} Chord | Guitar Positions & Voicings",
            "meta_description": f"Learn to play {selected_root_name} {chord_select_name} chord on guitar with our interactive tool. Multiple positions, voicings, and fingerings across the entire fretboard.",
            "meta_keywords": f"{selected_root_name} {chord_select_name} chord, {chord_select_name} guitar chord, guitar chord fingerings, guitar chord positions",
            "og_title": f"{selected_root_name} {chord_select_name} Chord | Guitar Positions",
            "og_description": f"Complete {selected_root_name} {chord_select_name} chord positions and voicings for guitar. Interactive fretboard visualization.",
            "twitter_title": f"{selected_root_name} {chord_select_name} Chord",
            "twitter_description": f"All {selected_root_name} {chord_select_name} chord voicings and positions.",
            "breadcrumbs": breadcrumbs_data,
            "structured_data": seo_data,
        }

    def _build_template_context(self, params: dict, parts: dict) -> dict:
        """Assemble the template context from request params and computed parts."""
        root_id = params["root_id"]
        category_id = params["category_id"]
        type_id = params["type_id"]
        chord_select_name = params["chord_select_name"]
        selected_range_value = params["selected_range"]
        selected_root_name = parts["selected_root_name"]
        all_root_options = parts["all_root_options"]
        category_objects = parts["category_objects"]
        position_options = parts["position_options"]
        range_options = parts["range_options"]
        type_options = parts["type_options"]
        chord_options = parts["chord_options"]
        final_chord_json_data = parts["final_chord_json_data"]
        selected_notes = parts["selected_notes"]
        # Determine 8-string status based on cookie configuration rather than available ranges
        is_eight_string = not params["is_six_string"]
        chord_function = self.generate_chord_function(chord_select_name)
        seo_context = self._build_seo_context(
            selected_root_name, chord_select_name, selected_notes, position_options
        )

        return {
            "selected_chord": chord_select_name,
            "root_id": root_id,
            "root_name": selected_root_name,
            "root_options": all_root_options,
            "selected_category": category_id,
            "category": category_objects,
            "position_options": position_options,  # Pass the list of position objects
            "range_options": range_options,
            "chord_type_options": type_options,  # Use the key expected by the template
            "chord_json_data": json.dumps(final_chord_json_data),
            "chord_options": chord_options,
            "selected_type": type_id,
            "note_range": selected_range_value,  # Use selected_range_value
            "selected_range": selected_range_value,
            "string_names": [
                "lowBString",
                "ELowString",
                "AString",
                "dString",
                "gString",
                "bString",
                "eString",
                "highAString",
            ],  # Keep static list
            "selected_notes": selected_notes,
            "selected_position": params["position_select"],  # Pass the position name from params
            "chord_function": chord_function,  # Add generated function
            "is_eight_string": is_eight_string,  # Add flag
            "DEBUG": settings.DEBUG,  # Use Django settings DEBUG
            # SEO specific context
            **seo_context,
        }

    def _resolve_range_options(
        self, initial_chord_object, type_id: str, chord_select_name: str, is_six_string: bool
    ) -> list:
        """Fetch range options based on the determined (or selected) type/name."""
        if initial_chord_object:
            return self.get_range_options(
                initial_chord_object.type_name, initial_chord_object.chord_name, is_six_string
            )
        # Attempt to get ranges based on selected type/name if initial object failed
        return self.get_range_options(type_id, chord_select_name, is_six_string)

    def _extract_selected_notes(self, final_chord_json_data: dict) -> list:
        """Extract the selected notes, falling back to an empty list on any error."""
        selected_notes: list = []
        if final_chord_json_data:
            try:
                selected_notes = extract_and_convert_notes(final_chord_json_data)
            except Exception:
                pass  # No specific action: fall back to empty notes
        return selected_notes

    def _without_eight_string_ranges(self, range_options: list) -> list:
        """Drop ranges that need the 8-string extension (lowB / highA)."""
        return [
            option
            for option in range_options
            if "lowB" not in option.range and "highA" not in option.range
        ]

    def _log_v_system_types(self, context: dict) -> None:
        """Print debug info about the V-System types in the final context."""
        if "chord_type_options" in context and "v_system_types" in context["chord_type_options"]:
            print(
                f"[DEBUG] Final v_system_types in context: {context['chord_type_options']['v_system_types']}"
            )
        else:
            print("[DEBUG] chord_type_options or v_system_types not found in final context")

    def get_context(self, request: HttpRequest) -> dict:
        """
        Build the template context, mirroring the functional view's logic.
        """
        params = self.process_request(request)

        root_id = params["root_id"]
        type_id = params["type_id"]
        chord_select_name = params["chord_select_name"]
        selected_range_value = params["selected_range"]

        # --- Fetch initial objects and options (mirroring functional view) ---
        category_objects = self.get_category_objects()
        selected_root_object = self.get_selected_root_object(root_id)
        root_pitch = selected_root_object.pitch
        selected_root_name = selected_root_object.name
        all_root_options = self.get_all_root_options()
        type_options = self.get_type_options()
        chord_options = self.get_chord_options(type_id)

        initial_chord_object, tonal_root, position_options = self._fetch_initial_chord(
            type_id, chord_select_name, selected_range_value
        )

        # Get string config mode (6 or 8 string)
        is_six_string = params["is_six_string"]

        range_options = self._resolve_range_options(
            initial_chord_object, type_id, chord_select_name, is_six_string
        )

        final_chord_json_data = self._build_chord_json_data(
            params, range_options, position_options, tonal_root, root_pitch, selected_root_name
        )

        selected_notes = self._extract_selected_notes(final_chord_json_data)

        # Additional safety check: if we're in 6-string mode, force-filter the range options again
        if params["is_six_string"]:
            range_options = self._without_eight_string_ranges(range_options)

        context = self._build_template_context(
            params,
            dict(
                selected_root_name=selected_root_name,
                all_root_options=all_root_options,
                category_objects=category_objects,
                position_options=position_options,
                range_options=range_options,
                type_options=type_options,
                chord_options=chord_options,
                final_chord_json_data=final_chord_json_data,
                selected_notes=selected_notes,
            ),
        )

        # Add common context from helper
        common_context_data = get_common_context(request)
        context.update(common_context_data)
        self._log_v_system_types(context)

        return context

    def render(self, request: HttpRequest) -> HttpResponse:
        """Render the template with the generated context."""
        try:
            context = self.get_context(request)
            return render(request, "fretboard.html", context)
        except Http404:
            # Handle cases where essential data isn't found
            # Render an error page or return a specific response
            # return render(request, 'error_page.html', {'message': str(e)})
            # For now, re-raise or handle as appropriate
            raise
        except Exception:
            # Log the full traceback
            import traceback

            traceback.print_exc()
            # Render a generic error page
            # return render(request, 'error_page.html', {'message': 'An unexpected error occurred.'})
            # For now, re-raise
            raise

    # Keep the simple view function that uses the class
    def generate_chord_function(self, chord_name: str) -> str:
        """
        Generate chord function notation based on chord name.
        For example:
        - Major 7 -> R - 3 - 5 - 7
        - Minor 7 -> R - b3 - 5 - b7
        - etc.
        """
        chord_functions = CHORD_FUNCTIONS

        print(f"DEBUG: Generating chord function for chord name: '{chord_name}'")

        # Normalize chord name - remove any spaces and convert to lowercase for more flexible matching
        normalized_name = chord_name.lower().replace(" ", "")

        # Check for exact match first
        if chord_name in chord_functions:
            return chord_functions[chord_name]

        # Special case handling for Minor 7b5 which might be encoded differently
        if (
            normalized_name == "minor7b5"
            or normalized_name == "min7b5"
            or "minor7b5" in normalized_name
        ):
            return "R - b3 - b5 - b7"

        # Return the function for the given chord name, or a default if not found
        result = chord_functions.get(chord_name, "R - ...")
        print(f"DEBUG: Returning chord function: '{result}' for chord: '{chord_name}'")
        return result


def fretboard_chords_view(request: HttpRequest) -> HttpResponse:
    """
    View function for displaying chords on the fretboard using ChordView.
    """
    chord_view = ChordView()
    return chord_view.render(request)
