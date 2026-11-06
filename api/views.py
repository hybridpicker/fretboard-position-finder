# V-system imports removed
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Ensure necessary models are imported
from positionfinder.models import Notes
from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.positions import NotesPosition

from ._views_static import (  # noqa: F401  (re-exported public names)
    STRING_COMBINATIONS,
    TUNINGS,
    ChordTypesView,
    ChordVoicingView,
    FallbackPositionsView,
    TuningOptionsView,
    VoicingGroupsView,
    _orders,
)

# --- Shared helpers -----------------------------------------------------------------------


def _chord_name_dicts(names) -> list[dict]:
    """Wrap chord names as ``{"chord_name": name}`` dicts."""
    return [{"chord_name": name} for name in names]


def _major_minor() -> list[dict]:
    """Minimal last-resort chord name list."""
    return _chord_name_dicts(["Major", "Minor"])


def _standard_ranges(count: int) -> list[dict]:
    """Hardcoded common string ranges (first ``count`` entries)."""
    ranges = [
        {"id": "1", "range": "e - g"},
        {"id": "2", "range": "b - d"},
        {"id": "3", "range": "g - A"},
        {"id": "4", "range": "d - E"},
        {"id": "5", "range": "A - B"},
        {"id": "6", "range": "highA - e"},
    ]
    return ranges[:count]


def _all_inversions() -> list[dict]:
    """Every distinct inversion name stored in the database."""
    return list(
        ChordPosition.objects.values("inversion_order").distinct().order_by("inversion_order")
    )


# Ultra-simple emergency fallback endpoints that don't use DRF


def _emergency_chord_names(type_name: str) -> JsonResponse:
    """Chord names for a type, from the DB or a static fallback."""
    try:
        db_chord_names = (
            ChordNotes.objects.filter(type_name=type_name)
            .values_list("chord_name", flat=True)
            .distinct()
        )

        if db_chord_names.exists():
            # Convert to the format expected by the UI
            return JsonResponse({"chord_names": _chord_name_dicts(db_chord_names)})
    except Exception:
        pass  # Continue to fallback if database query fails

    # Fallback values if database query failed
    if "Triads" in type_name or "Spread" in type_name:
        return JsonResponse(
            {"chord_names": _chord_name_dicts(["Major", "Minor", "Diminished", "Augmented"])}
        )
    return JsonResponse({"chord_names": _major_minor()})


def _emergency_inversions(chord_notes_id: str) -> JsonResponse:
    """Inversion names for a chord id (a fourth inversion for 7th chords)."""
    positions = [
        {"inversion_order": "Root Position"},
        {"inversion_order": "First Inversion"},
        {"inversion_order": "Second Inversion"},
    ]
    if chord_notes_id in ["4", "5", "6"]:  # For 7th chords
        positions.append({"inversion_order": "Third Inversion"})

    return JsonResponse({"positions": positions})


def _emergency_scale_positions(notes_id: str) -> JsonResponse:
    """Scale/arpeggio positions based on a simplified notes_id mapping."""
    if notes_id in ["1", "2", "3"]:  # Major scale and other 7-position scales
        positions = _orders(*range(0, 8))
    else:  # Blues scale ID (49) and every other scale: 0-5
        positions = _orders(*range(0, 6))
    return JsonResponse({"positions": positions})


def emergency_positions(request: HttpRequest) -> JsonResponse:
    """Most basic view possible that always returns a valid position response."""
    try:
        # Check for specific type parameters to handle different types of requests
        type_name = request.GET.get("type_name", "")
        notes_id = request.GET.get("notes_id", "")
        chord_name = request.GET.get("chord_name", "")
        chord_notes_id = request.GET.get("chord_notes_id", "")

        if type_name and not chord_name:  # chord_names request
            return _emergency_chord_names(type_name)
        elif type_name and chord_name:  # chord_ranges request
            return JsonResponse({"ranges": _standard_ranges(6)})
        elif chord_notes_id:  # chord_positions request (inversions)
            return _emergency_inversions(chord_notes_id)
        elif notes_id:  # scale/arpeggio positions request
            return _emergency_scale_positions(notes_id)

        # Default to positions response
        return JsonResponse({"positions": [{"position_order": 0}]})

    except Exception:
        # Fail absolutely silently
        return JsonResponse({"positions": [{"position_order": 0}]})


# --- New Views for Dynamic Menu Options ---

_UNSET = object()  # marks a local that was never assigned (see ChordNamesView)


def _default_type_name() -> str:
    """First chord type in the database, or "Triads" if unavailable."""
    # Try to get the first available type from database instead of hardcoding
    try:
        first_type = ChordNotes.objects.values_list("type_name", flat=True).distinct().first()
        if first_type:
            return first_type
        # Only if database is empty, use a fallback
        return "Triads"
    except Exception:
        return "Triads"


def _chord_names_of_type(type_name: str) -> list[dict]:
    """Ordered chord-name dicts for a chord type."""
    db_chord_names = (
        ChordNotes.objects.filter(type_name=type_name)
        .values_list("chord_name", flat=True)
        .distinct()
        .order_by("chord_name")
    )
    return _chord_name_dicts(db_chord_names)


def _query_chord_names(type_name: str) -> list[dict]:
    """Chord names for a type; falls back to all names, then Major/Minor."""
    ChordNotes.objects.count()

    # Add debug info
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT type_name, chord_name, COUNT(*) FROM positionfinder_chordnotes GROUP BY type_name, chord_name ORDER BY COUNT(*) DESC LIMIT 10"
        )
        cursor.fetchall()

    chord_names_list = _chord_names_of_type(type_name)
    if not chord_names_list:
        chord_names_list = _chord_names_of_type(type_name)

    if chord_names_list:
        return chord_names_list

    # No results for the specific type: try ALL chord names available
    all_chord_names = (
        ChordNotes.objects.values_list("chord_name", flat=True).distinct().order_by("chord_name")
    )
    all_chord_names_list = list(all_chord_names)
    if all_chord_names_list:
        return _chord_name_dicts(all_chord_names_list)
    # Only as absolutely last resort, use minimal fallback values
    return _major_minor()


def _load_chord_names(type_name: str) -> list[dict]:
    """Chord names for a type with layered fallbacks; never raises."""
    try:
        try:
            return _query_chord_names(type_name)
        except Exception:
            # Try querying for ANY chord names as fallback
            try:
                all_chord_names = ChordNotes.objects.values_list("chord_name", flat=True).distinct()
                all_name_values = list(all_chord_names)
                if all_name_values:
                    return _chord_name_dicts(all_name_values)
                return _major_minor()  # Last resort
            except Exception:
                return _major_minor()  # Absolute last resort
    except Exception:
        return _major_minor()  # Absolute last resort


def _dedupe_chord_names(chord_names_list: list[dict]) -> list[dict]:
    """Remove duplicate chord names while preserving order."""
    seen = set()
    return [
        item
        for item in chord_names_list
        if not (item.get("chord_name") in seen or seen.add(item.get("chord_name")))
    ]


def _recover_chord_names(type_name) -> list[dict]:
    """Chord names after an unexpected failure in ``ChordNamesView.get``."""
    try:
        if type_name is _UNSET:
            raise UnboundLocalError("type_name")
        db_chord_names = (
            ChordNotes.objects.filter(type_name=type_name)
            .values_list("chord_name", flat=True)
            .distinct()
            .order_by("chord_name")
        )

        if db_chord_names.exists():
            return _chord_name_dicts(db_chord_names)
        # Fallback to basic chord types that exist in our database
        return _chord_name_dicts(["Major", "Minor", "Diminished", "Augmented"])
    except Exception:
        try:
            all_chord_names = (
                ChordNotes.objects.values_list("chord_name", flat=True)
                .distinct()
                .order_by("chord_name")[:10]
            )
            all_chord_names_list = list(all_chord_names)
            if all_chord_names_list:
                return _chord_name_dicts(all_chord_names_list)
            return _major_minor()
        except Exception:
            return _major_minor()


class ChordNamesView(APIView):
    """API view to get chord names based on chord type."""

    permission_classes = []  # Override default permissions that require a queryset

    @method_decorator(csrf_exempt)  # Add CSRF exemption
    def get(self, request: Request, format: str | None = None) -> Response:
        """Return the chord names available for ``type_name``."""
        type_name = _UNSET
        try:
            type_name = request.query_params.get("type_name", None)
            if not type_name:
                type_name = _default_type_name()

            chord_names_list = _load_chord_names(type_name)

            # Ensure we always have at least something to return and remove duplicates
            if not chord_names_list:
                chord_names_list = _major_minor()
            else:
                chord_names_list = _dedupe_chord_names(chord_names_list)

            return Response({"chord_names": chord_names_list})

        except Exception:
            # Format response consistently no matter what
            return Response({"chord_names": _recover_chord_names(type_name)})


def _resolve_string_mode(request: Request) -> str:
    """String configuration (six/eight) from query param, then cookie."""
    string_mode = request.query_params.get("string_mode", None)
    if not string_mode:
        string_mode = request.COOKIES.get("stringConfig", "six-string")

    if string_mode not in ["six-string", "eight-string"]:
        string_mode = "six-string"
    return string_mode


def _default_ranges() -> list[dict]:
    """Ranges derived from STRING_RANGE_CHOICES, else the hardcoded set."""
    try:
        from positionfinder.string_range_choices import STRING_RANGE_CHOICES

        default_ranges = [
            {"id": str(i + 1), "range": choice[0]} for i, choice in enumerate(STRING_RANGE_CHOICES)
        ]
        return default_ranges[:6]  # Limit to 6 choices
    except Exception:
        return _standard_ranges(6)


def _lookup_ranges(type_name: str, chord_name: str) -> list[dict]:
    """Ranges for a chord, widening the search until something is found."""
    ranges_list = []
    if type_name and chord_name:
        ranges_list = list(
            ChordNotes.objects.filter(type_name=type_name, chord_name=chord_name)
            .order_by("range_ordering")
            .values("id", "range")
        )

    # No specific ranges: all ranges used for this chord name in any type
    if not ranges_list:
        ranges_list = list(
            ChordNotes.objects.filter(chord_name=chord_name)
            .order_by("range_ordering")
            .values("id", "range")
            .distinct("range")
        )

    # Still none: all ranges for this chord type
    if not ranges_list:
        ranges_list = list(
            ChordNotes.objects.filter(type_name=type_name)
            .order_by("range_ordering")
            .values("id", "range")
            .distinct("range")
        )

    # Still none: all ranges from all chords
    if not ranges_list:
        ranges_list = list(
            ChordNotes.objects.values("id", "range").distinct("range").order_by("range_ordering")
        )

    # Empty database: use the standard ranges
    if not ranges_list:
        ranges_list = _default_ranges()
    return ranges_list


def _tidy_ranges(ranges_list: list[dict], is_six_string: bool) -> list[dict]:
    """Unique-by-name, 6-string filtered and capped range list."""
    seen_ranges = set()
    unique_ranges = []
    for range_obj in ranges_list:
        range_name = range_obj.get("range")
        if range_name and range_name not in seen_ranges:
            seen_ranges.add(range_name)
            unique_ranges.append(range_obj)

    ranges_list = unique_ranges

    # Filter out 8-string specific ranges if in 6-string mode
    if is_six_string:
        ranges_list = [
            r
            for r in ranges_list
            if not (r.get("range") and ("highA" in r.get("range") or "lowB" in r.get("range")))
        ]

    # Ensure reasonable limit (don't overwhelm the UI)
    if len(ranges_list) > 8:
        ranges_list = ranges_list[:8]
    return ranges_list


def _fill_missing_range_params(type_name, chord_name):
    """Complete type/chord from the first DB row; returns (type, chord, error)."""
    try:
        sample_chord = ChordNotes.objects.first()
        if sample_chord:
            if not type_name:
                type_name = sample_chord.type_name
            if not chord_name:
                chord_name = sample_chord.chord_name
        else:
            return (
                type_name,
                chord_name,
                Response(
                    {"error": "Missing required parameters and no database values found"},
                    status=status.HTTP_400_BAD_REQUEST,
                ),
            )
    except Exception:
        return (
            type_name,
            chord_name,
            Response(
                {"error": "Missing required parameters: type_name, chord_name"},
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )
    return type_name, chord_name, None


class ChordRangesView(APIView):
    """API view to get chord ranges based on type and name."""

    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request: Request, format: str | None = None) -> Response:
        """Return the string ranges available for ``type_name``/``chord_name``."""
        try:
            type_name = request.query_params.get("type_name", None)
            chord_name = request.query_params.get("chord_name", None)

            string_mode = _resolve_string_mode(request)
            is_six_string = string_mode == "six-string"

            # Debug string configuration
            print(f"API - String configuration: {string_mode}, is_six_string: {is_six_string}")

            if not type_name or not chord_name:
                # Try to get valid values from database instead of returning error
                type_name, chord_name, error = _fill_missing_range_params(type_name, chord_name)
                if error is not None:
                    return error

            try:
                ranges_list = _lookup_ranges(type_name, chord_name)
                ranges_list = _tidy_ranges(ranges_list, is_six_string)
            except Exception:
                # Fallback to standard range options after error
                ranges_list = _standard_ranges(5)

            # Ensure we always have at least one range
            if not ranges_list:
                ranges_list = [{"id": "1", "range": "e - g"}]

            return Response({"ranges": ranges_list})

        except Exception:
            # Always return a standard set of ranges
            # If in 6-string mode, don't include 8-string ranges
            if is_six_string:
                emergency_ranges = _standard_ranges(3)
            else:
                emergency_ranges = [
                    {"id": "1", "range": "e - g"},
                    {"id": "2", "range": "b - d"},
                    {"id": "3", "range": "g - A"},
                    {"id": "4", "range": "highA - e"},
                    {"id": "5", "range": "e - lowB"},
                ]

            return Response({"ranges": emergency_ranges})


def _root_position() -> list[dict]:
    """Minimal single-inversion fallback."""
    return [{"inversion_order": "Root Position"}]


def _fill_chord_notes_id(chord_notes_id):
    """Pick the first DB chord id when missing; returns (id, error)."""
    try:
        sample_chord = ChordNotes.objects.first()
        if sample_chord:
            return str(sample_chord.id), None
        return None, Response(
            {"error": "Missing chord_notes_id and no database values found"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        return None, Response(
            {"error": "Missing required parameter: chord_notes_id"},
            status=status.HTTP_400_BAD_REQUEST,
        )


def _similar_chord_inversions(chord_notes_id: str) -> list[dict]:
    """Inversions inferred from similar chords when the chord has none."""
    try:
        chord = ChordNotes.objects.get(id=chord_notes_id)

        # Check if it's a seventh chord based on fourth_note
        is_seventh = chord.fourth_note is not None

        # Common inversions from other chords of the same kind
        kind = ChordPosition.objects.filter(notes_name__fourth_note__isnull=not is_seventh)
        positions_list = list(kind.values("inversion_order").distinct().order_by("inversion_order"))

        if not positions_list:
            # Get all position types as last resort
            positions_list = _all_inversions()

    except ChordNotes.DoesNotExist:
        # Get all position types as fallback
        positions_list = _all_inversions()

    # If still no positions found, use minimal fallback
    if not positions_list:
        positions_list = _root_position()
    return positions_list


def _chord_inversions(chord_notes_id: str) -> list[dict]:
    """Inversions of a chord, falling back through increasingly generic queries."""
    positions_list = []
    try:
        positions = (
            ChordPosition.objects.filter(notes_name_id=chord_notes_id)
            .order_by("inversion_order")
            .values("inversion_order")
        )
        positions_list = list(positions)

        if not positions_list:
            positions_list = _similar_chord_inversions(chord_notes_id)

    except Exception:
        # Try to get ANY positions from database
        try:
            positions_list = _all_inversions()
            if not positions_list:
                positions_list = _root_position()
        except Exception:
            positions_list = _root_position()
    return positions_list


class ChordPositionsView(APIView):
    """API view to get chord positions/inversions based on ChordNotes ID."""

    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request: Request, format: str | None = None) -> Response:
        """Return the inversions available for ``chord_notes_id``."""
        try:
            chord_notes_id = request.query_params.get("chord_notes_id", None)
            if not chord_notes_id:
                # Try to get a valid ID from database instead of returning error
                chord_notes_id, error = _fill_chord_notes_id(chord_notes_id)
                if error is not None:
                    return error

            positions_list = _chord_inversions(chord_notes_id)

            # Ensure we always have at least one position
            if not positions_list:
                positions_list = _root_position()

            return Response({"positions": positions_list})

        except Exception:
            # Try to get positions from database even after critical error
            try:
                emergency_positions = list(
                    ChordPosition.objects.values("inversion_order").distinct()[:3]
                )
                if not emergency_positions:
                    emergency_positions = _root_position()
            except Exception:
                emergency_positions = _root_position()

            return Response({"positions": emergency_positions})


def _guess_positions_from_name(positions: list[dict], note) -> None:
    """Append 7 (major modes) or 5 positions based on the note name."""
    note_name = note.note_name.lower()

    if "major" in note_name and "pentatonic" not in note_name:
        # Major scale and modes typically have 7 positions
        positions.extend(_orders(*range(1, 8)))
    else:
        # Blues, pentatonic, arpeggios and other scales: 5 positions
        positions.extend(_orders(*range(1, 6)))


def _extend_scale_positions(positions: list[dict], notes_id_int: int) -> None:
    """Add the DB (or guessed) positions of a scale note to ``positions``."""
    try:
        note = Notes.objects.get(id=notes_id_int)

        # Get all positions for this specific note from the database
        db_positions = (
            NotesPosition.objects.filter(notes_name_id=notes_id_int)
            .order_by("position_order")
            .values("position_order")
            .distinct()
        )
        db_positions_list = list(db_positions)

        if db_positions_list:
            positions.extend(db_positions_list)
            return

        # Get positions for other scales/arpeggios of the same type
        similar_notes = Notes.objects.filter(
            category=note.category, note_name=note.note_name
        ).exclude(id=note.id)

        if similar_notes.exists():
            similar_positions = (
                NotesPosition.objects.filter(notes_name__in=similar_notes)
                .order_by("position_order")
                .values("position_order")
                .distinct()
            )
            positions.extend(list(similar_positions))

        # If still no positions, try to determine based on note name
        if len(positions) <= 1:  # Only "All Notes" position
            _guess_positions_from_name(positions, note)

    except Notes.DoesNotExist:
        # Use default positions for unknown scale/arpeggio
        positions.extend(_orders(*range(1, 6)))

    except Exception:
        # Use default positions on database error
        positions.extend(_orders(*range(1, 6)))


def _unique_sorted_positions(positions: list[dict]) -> list[dict]:
    """Deduplicate by position_order and sort numerically."""
    seen = set()
    unique_positions = []
    for pos in positions:
        order = pos.get("position_order")
        if order not in seen:
            seen.add(order)
            unique_positions.append(pos)

    return sorted(unique_positions, key=lambda x: int(x.get("position_order", 0)))


class ScalePositionsView(APIView):
    """API view to get scale positions based on Notes ID."""

    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request: Request, format: str | None = None) -> Response:
        """Return the scale positions available for ``notes_id``."""
        notes_id = request.query_params.get("notes_id", None)
        if not notes_id:
            return Response(
                {"error": "Missing required parameter: notes_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Start with the "All Notes" position which is always included
            positions = _orders(0)

            try:
                _extend_scale_positions(positions, int(notes_id))
            except ValueError:
                # Fall back to default positions
                positions.extend(_orders(*range(1, 6)))

            return Response({"positions": _unique_sorted_positions(positions)})

        except Exception:
            # Always return a valid response with default positions even on error
            return Response({"positions": _orders(*range(0, 6))})


def _probe_arpeggio_tables() -> None:
    """Touch the Notes/NotesPosition tables with sample queries (debug aid)."""
    try:
        Notes.objects.count()
        NotesPosition.objects.count()

        # Sample a few entries from Notes for arpeggio notes
        sample_notes = Notes.objects.filter(category__category_name="Arpeggios")[:5]
        for _note in sample_notes:
            pass

        # Sample a few entries from NotesPosition for arpeggio notes
        if sample_notes.exists():
            sample_note_ids = [note.id for note in sample_notes]
            sample_positions = NotesPosition.objects.filter(notes_name_id__in=sample_note_ids)[:5]
            for _pos in sample_positions:
                pass
    except Exception:
        pass


def _arpeggio_positions(notes_id_int: int) -> list[dict]:
    """Default five positions, replaced by the DB ones when they exist."""
    # For arpeggios, most have 5 positions by default
    positions = _orders(0, *range(1, 6))

    try:
        Notes.objects.get(id=notes_id_int)
        qs = NotesPosition.objects.filter(notes_name_id=notes_id_int)

        if qs.exists():
            # Override the default positions with actual ones from DB
            position_values = qs.order_by("position_order").values("position_order")
            positions = _orders(0)  # Keep "All Notes"
            positions.extend(list(position_values))
    except Exception:
        pass  # Keep the default positions set above
    return positions


class ArpeggioPositionsView(APIView):
    """API view to get arpeggio positions based on Notes ID."""

    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request: Request, format: str | None = None) -> Response:
        """Return the arpeggio positions available for ``notes_id``."""
        notes_id = request.query_params.get("notes_id", None)
        if not notes_id:
            return Response(
                {"error": "Missing required parameter: notes_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        _probe_arpeggio_tables()

        try:
            try:
                positions = _arpeggio_positions(int(notes_id))
            except ValueError:
                # Fall back to default arpeggio positions
                positions = _orders(0, *range(1, 6))

            return Response({"positions": positions})

        except Exception:
            # Always return a valid response with default positions even on error
            return Response({"positions": _orders(*range(0, 6))})
