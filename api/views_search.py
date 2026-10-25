"""Search API endpoints (autocomplete and direct match).

The direct-match pipeline lives in ``api.search_direct`` and the term
normalisation in ``api.search_normalize``; both are re-exported here.
"""

import logging
import re
import traceback
from urllib.parse import urlencode

from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from thefuzz import fuzz, process  # noqa: F401  (re-exported names)

from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.models_chords import ChordNotes
from positionfinder.search_utils import ROOT_NAME_TO_ID, get_root_id_from_name, parse_query

from .search_common import MIN_SCORE_THRESHOLD
from .search_direct import direct_match
from .search_normalize import normalize_search_term

__all__ = [
    "MIN_SCORE_THRESHOLD",
    "direct_match",
    "logger",
    "normalize_search_term",
    "search_autocomplete",
]

# Reduce logging to WARNING or ERROR for search logic bugfixing
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def _autocomplete_root_pk(query: str) -> int | None:
    """Resolve the root id at the start of the query (before normalization)."""
    root_match = re.search(r"^([a-gA-G][#b]?)\s", query)
    root_pk = None
    if root_match:
        root_note = root_match.group(1).capitalize().replace("♯", "#").replace("♭", "b")
        root_pk = get_root_id_from_name(root_note)
        logger.debug(
            f"[SEARCH_AUTOCOMPLETE_FUZZY] Extracted root note: '{root_note}' -> ID: {root_pk}"
        )
        if root_pk:
            # Find the canonical spelling from the mapping
            for name, pk in ROOT_NAME_TO_ID.items():
                if pk == root_pk:
                    logger.debug(
                        f"[SEARCH_AUTOCOMPLETE_FUZZY] Canonical root name for ID {root_pk}: '{name}'"
                    )
                    break
        else:
            logger.warning(
                f"[SEARCH_AUTOCOMPLETE_FUZZY] No root ID found for '{root_note}' using custom mapping."
            )
    return root_pk


def _autocomplete_scale_items(scales, root_pk: int | None, base_url: str) -> list[dict]:
    """Build the autocomplete items for all scales."""
    items = []
    for scale in scales:
        name = scale.note_name
        # Use extracted root if available, else fallback to scale.tonal_root
        if root_pk is not None:
            used_root_pk = root_pk
            logger.debug(
                f"[SEARCH_AUTOCOMPLETE_FUZZY] Assigned root param: {used_root_pk} (custom mapping)"
            )
        else:
            root_obj2 = Root.objects.filter(pitch=scale.tonal_root).first()
            used_root_pk = root_obj2.pk if root_obj2 else scale.tonal_root
            logger.debug(
                f"[SEARCH_AUTOCOMPLETE_FUZZY] Fallback root param: {used_root_pk} -> {root_obj2.name if root_obj2 else 'UNKNOWN'}"
            )
        params = {
            "root": used_root_pk,
            "models_select": 1,
            "notes_options_select": scale.pk,
            "position_select": 0,
        }
        url = f"{base_url}?{urlencode(params)}"
        items.append(
            {
                "name": name,
                "normalized_name": normalize_search_term(name),
                "type": "scale",
                "url": url,
            }
        )
    return items


def _autocomplete_arpeggio_items(arpeggio_types, base_url: str) -> list[dict]:
    """Build the autocomplete items for all arpeggio categories."""
    items = []
    for arpeggio_cat in arpeggio_types:
        name = arpeggio_cat.category_name
        url = f"{base_url}?models_select=2&notes_options_select={arpeggio_cat.pk}"
        items.append(
            {
                "name": name,
                "normalized_name": normalize_search_term(name),
                "type": "arpeggio",
                "url": url,
            }
        )
    return items


def _autocomplete_chord_items(chord_types, base_url: str) -> list[dict]:
    """Build the autocomplete items for all chord types."""
    items = []
    for chord in chord_types:
        # Use both root and chord_name for normalized display,
        # e.g. 'Dominant 7' with root G -> 'G Dominant 7'
        root_obj = None
        if hasattr(chord, "tonal_root"):
            root_obj = Root.objects.filter(pitch=chord.tonal_root).first()
        root_name = root_obj.name if root_obj else None
        display_name = normalize_search_term(
            f"{root_name} {chord.chord_name}" if root_name else chord.chord_name
        )
        url = f"{base_url}?models_select=3&notes_options_select={chord.pk}"
        items.append(
            {
                "name": display_name,  # Use display name for results!
                "normalized_name": display_name,
                "type": "chord",
                "url": url,
            }
        )
    return items


def _autocomplete_fuzzy_suggestions(normalized_query: str, all_items: list[dict]) -> list[dict]:
    """Fuzzy match the query against the normalized item names."""
    normalized_names = [item["normalized_name"] for item in all_items]
    matches = process.extract(normalized_query, normalized_names, limit=10)
    suggestions = []
    for match, score in matches:
        if score >= MIN_SCORE_THRESHOLD:
            idx = normalized_names.index(match)
            # Return the original name
            suggestions.append(
                {
                    "name": all_items[idx]["name"],
                    "type": all_items[idx]["type"],
                    "url": all_items[idx]["url"],
                }
            )
    return suggestions


def _autocomplete_results(query: str) -> JsonResponse:
    """Build the autocomplete response for a query of at least two characters."""
    # Extract root note BEFORE normalization
    root_pk = _autocomplete_root_pk(query)

    # Normalize the query to handle common notations (but NOT the root)
    normalized_query = normalize_search_term(query)
    logger.debug(f"[SEARCH_AUTOCOMPLETE_FUZZY] Normalized query: '{normalized_query}'")

    # Intent filtering: parse the query to determine the user's intent
    note, type_, quality, position, inversion = parse_query(query)

    all_items = []
    Root.objects.all()
    scales = Notes.objects.filter(category__category_name__icontains="scale").order_by("note_name")
    arpeggio_types = NotesCategory.objects.filter(category_name__icontains="arpeggio")
    chord_types = ChordNotes.objects.all()

    try:
        base_fretboard_url = reverse("fretboard")
    except Exception as e:
        logger.error(f"Could not reverse 'fretboard' URL: {e}. Falling back to '/' path.")
        base_fretboard_url = "/"

    if type_ == "scale" or type_ == "all":
        all_items += _autocomplete_scale_items(scales, root_pk, base_fretboard_url)
    if type_ == "arpeggio" or type_ == "all":
        all_items += _autocomplete_arpeggio_items(arpeggio_types, base_fretboard_url)
    # Chords (only if intent is not scale-specific)
    if type_ == "chord" or type_ == "all":
        # Only suggest chords if the query does not indicate a pentatonic/scale intent
        if not ("pentatonic" in quality.lower() or type_ == "scale"):
            all_items += _autocomplete_chord_items(chord_types, base_fretboard_url)

    suggestions = _autocomplete_fuzzy_suggestions(normalized_query, all_items)

    logger.debug(f"[SEARCH_AUTOCOMPLETE_FUZZY] Returning {len(suggestions)} filtered results.")
    return JsonResponse({"results": suggestions})


def search_autocomplete(request: HttpRequest) -> JsonResponse:
    """
    API endpoint for autocomplete suggestions using fuzzy matching.
    Returns matching scales, arpeggios, and chords.
    """
    try:
        query = request.GET.get("q", "").strip()
        logger.debug(f"[SEARCH_AUTOCOMPLETE_FUZZY] Received query: '{query}'")

        if not query or len(query) < 2:
            logger.debug("[SEARCH_AUTOCOMPLETE_FUZZY] Query too short, returning empty results")
            return JsonResponse({"results": [], "debug": "Query too short"})

        return _autocomplete_results(query)
    except Exception as e:
        logger.error(f"[SEARCH_AUTOCOMPLETE_FUZZY] Exception: {e}\n{traceback.format_exc()}")
        return JsonResponse({"results": [], "error": str(e)})
