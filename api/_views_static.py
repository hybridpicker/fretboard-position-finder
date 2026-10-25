"""Static / DB-free API views (split out of ``api.views``, which re-exports them)."""

import re

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChordVoicingResponseSerializer

# Constants for guitar specifications
TUNINGS = {
    "6-string": ["E", "A", "D", "G", "B", "E"],
    "7-string": ["B", "E", "A", "D", "G", "B", "E"],
    "8-string": ["F#", "B", "E", "A", "D", "G", "B", "E"],
}

# String combinations for all instruments
STRING_COMBINATIONS = {
    "6-string": [("6-3"), ("5-2"), ("4-1")],
    "7-string": [("7-4"), ("6-3"), ("5-2"), ("4-1")],
    "8-string": [("8-5"), ("7-4"), ("6-3"), ("5-2"), ("4-1")],
}


def _orders(*values: int) -> list[dict]:
    """Build ``[{"position_order": n}, ...]`` for the given numbers."""
    return [{"position_order": value} for value in values]


class ChordVoicingView(APIView):
    """API view for chord voicings."""

    permission_classes = []  # Override default permissions that require a queryset

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request: Request, format: str | None = None) -> Response:
        """
        Get chord voicings based on query parameters.

        Required parameters:
        - chord: Chord name (e.g., G7, Cmaj7)
        - voicing_group: V-System group (e.g., V-2)
        - instrument: Guitar type (6-string, 7-string, 8-string)
        - string_set: String set (e.g., 6-3, 5-2)
        """
        chord = request.query_params.get("chord", None)
        voicing_group = request.query_params.get("voicing_group", None)
        instrument = request.query_params.get("instrument", "6-string")
        string_set = request.query_params.get("string_set", "6-3")

        if not chord or not voicing_group:
            return Response(
                {"error": "Missing required parameters (chord, voicing_group)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Normalize voicing group format (V-2 or V2 -> V-2)
        if not voicing_group.startswith("V-") and voicing_group.startswith("V"):
            voicing_group = f"V-{voicing_group[1:]}"

        # Parse chord (e.g., G7 -> root: G, type: 7)
        chord_match = re.match(r"([A-G][#b]?)([^#b]*)", chord)
        if not chord_match:
            return Response({"error": "Invalid chord format"}, status=status.HTTP_400_BAD_REQUEST)

        # V-system generator removed: voicings stay an empty placeholder
        response_data = {
            "voicing_group": voicing_group,
            "instrument": instrument,
            "string_set": string_set,
            "chord": chord,
            "voicings": [],
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

    def get(self, request: Request, format: str | None = None) -> Response:
        """Get all available tunings and corresponding string sets."""
        response_data = {"tunings": TUNINGS, "string_sets": STRING_COMBINATIONS}

        return Response(response_data)


class VoicingGroupsView(APIView):
    """API view for available V-System voicing groups."""

    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request: Request, format: str | None = None) -> Response:
        """Get all available V-System voicing groups."""
        response_data = {
            "seventh_chords": [],  # Placeholder for removed v-system functionality
            "triads": [],  # Placeholder for removed v-system functionality
        }

        return Response(response_data)


class ChordTypesView(APIView):
    """API view for available chord types."""

    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request: Request, format: str | None = None) -> Response:
        """Get all available chord types with their interval structures."""
        # Basic chord intervals as replacement
        chord_intervals = {
            "Major": [0, 4, 7],
            "Minor": [0, 3, 7],
            "Dominant 7": [0, 4, 7, 10],
            "Major 7": [0, 4, 7, 11],
            "Minor 7": [0, 3, 7, 10],
        }

        response_data = {"chord_types": chord_intervals}

        return Response(response_data)


def _fallback_position_orders(notes_id: str) -> list[dict]:
    """Position list for the fallback view, derived from the scale id."""
    positions = _orders(0)
    try:
        notes_id_int = int(notes_id) if notes_id.isdigit() else 0
        if notes_id_int == 49:  # Blues scale ID: 5 positions
            positions.extend(_orders(*range(1, 6)))
        elif notes_id_int in [1, 2, 3]:  # Major scale IDs: 7 positions
            positions.extend(_orders(*range(1, 8)))
        else:  # Default for other scales: 5 positions
            positions.extend(_orders(*range(1, 6)))
    except Exception:
        # Default to 5 positions if we can't determine the scale type
        positions.extend(_orders(*range(1, 6)))
    return positions


# Fallback view that always returns a valid response
class FallbackPositionsView(APIView):
    """Fallback API view that returns appropriate positions based on scale type."""

    permission_classes = []  # Override default permissions that require a queryset

    def get(self, request: Request, format: str | None = None) -> Response:
        """Return scale positions guessed from ``notes_id`` without touching the DB."""
        try:
            notes_id = request.query_params.get("notes_id", "unknown")
            return Response({"positions": _fallback_position_orders(notes_id)})
        except Exception:
            # Even in case of error, return a minimal valid response with only 'All Notes'
            return Response({"positions": [{"position_order": 0}]})
