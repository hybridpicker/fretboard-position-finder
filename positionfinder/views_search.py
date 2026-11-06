import json
import logging
import traceback

from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Notes, NotesCategory, Root
from .models_chords import ChordNotes, ChordPosition
from .search_utils import (
    PITCH_TO_ROOT_NAME,
    ROOT_NAME_TO_ID,
    ROOT_NAME_TO_PITCH,
    parse_query,
    resolve_root,
)
from .views_helpers import get_common_context

# Scale is an alias for Notes with scale category for testing compatibility
Scale = Notes

# Configure logging
logger = logging.getLogger(__name__)


_CHORD_NOTE_ATTRS = (
    "first_note",
    "second_note",
    "third_note",
    "fourth_note",
    "fifth_note",
    "sixth_note",
)

_SCALE_NOTE_ATTRS = (
    "first_note",
    "second_note",
    "third_note",
    "fourth_note",
    "fifth_note",
    "sixth_note",
    "seventh_note",
    "eighth_note",
    "ninth_note",
)

# NOTE: "eigth" and "twelth" are misspelled on purpose: they mirror the model field names.
_ARPEGGIO_NOTE_ATTRS = (
    "first_note",
    "second_note",
    "third_note",
    "fourth_note",
    "fifth_note",
    "sixth_note",
    "seventh_note",
    "eigth_note",
    "ninth_note",
    "tenth_note",
    "eleventh_note",
    "twelth_note",
)

# Map parsed quality to canonical chord_name in DB
_CHORD_QUALITY_MAP = {
    "maj7": "Major 7",
    "major7": "Major 7",
    "min7": "Minor 7",
    "m7": "Minor 7",
    "minor7": "Minor 7",
    "dim7": "Diminished 7",
    "m7b5": "Minor 7b5",
    "dom7": "Dominant 7",
    "dominant 7": "Dominant 7",
    "major": "Major",
    "minor": "Minor",
    "dim": "Diminished",
    "diminished": "Diminished",
    "aug": "Augmented",
    "augmented": "Augmented",
}

# Quality mappings to improve arpeggio search precision
_ARPEGGIO_QUALITY_TERMS = {
    "minor": ["Minor", "minor", "Min", "m"],
    "major": ["Major", "major", "Maj", "M"],
    "diminished": ["Diminished", "diminished", "Dim", "dim", "o"],
    "augmented": ["Augmented", "augmented", "Aug", "aug", "+"],
    "dominant": ["Dominant", "dominant", "Dom", "dom"],
}


def log_debug_info(message: str, data: dict | list | str | None = None) -> None:
    """Helper to output debug information consistently"""
    if data:
        logger.debug(f"DEBUG: {message}")
        logger.debug(f"DATA: {json.dumps(data) if isinstance(data, (dict, list)) else data}")
    else:
        logger.debug(f"DEBUG: {message}")


def _collect_notes(obj, attrs: tuple) -> list:
    """Collect the non-None note values of ``obj`` for the given attribute names."""
    notes = []
    for note_attr in attrs:
        value = getattr(obj, note_attr, None)
        if value is not None:
            notes.append(value)
    return notes


def _infer_intervals(obj, notes: list) -> list:
    """Return the object's intervals, or infer them relative to the first note."""
    intervals = []
    if hasattr(obj, "intervals") and obj.intervals:
        intervals = obj.intervals
    else:
        if notes and len(notes) > 1:
            root_pitch = notes[0]
            intervals = [(n - root_pitch) % 12 for n in notes]
    return intervals


def _prefixed_name(name: str, root_note: str | None) -> str:
    """Prefix ``name`` with the root note unless it already starts with it."""
    if root_note and not name.lower().startswith(root_note.lower()):
        return f"{root_note} {name}"
    return name


def _search_json_scales(note, quality, normalized_query: str) -> list:
    """Run the scale search for search_json and patch URLs of dynamic scales."""
    scale_results = search_scales(normalized_query)
    logger.debug(f"[DEBUG] Scale queryset count: {len(scale_results)}")
    # Patch: Generate URLs using the blueprint scale id (`notes_options_select`) for dynamic scales
    for item in scale_results:
        if item.get("id") is None and note and quality:
            from .search_utils import get_root_id_from_name

            root_id = get_root_id_from_name(note)
            # Look up blueprint scale record for this quality
            blueprint = Notes.objects.filter(
                category__category_name__icontains="scale", note_name__icontains=quality
            ).first()
            notes_options_select = blueprint.pk if blueprint else ""
            item["url"] = (
                f"/?root={root_id}&models_select=1&notes_options_select={notes_options_select}&position_select=0"
            )
    return scale_results


def _empty_search_json_response() -> JsonResponse:
    """Response for an empty query: no results of any kind."""
    return JsonResponse(
        {
            "query": "",
            "total_results": 0,
            "chord_results": [],
            "scale_results": [],
            "arpeggio_results": [],
        }
    )


def _search_json_results(query, search_type, note, type_, quality, normalized_query) -> dict:
    """Run the searches selected by search_type/type_ for search_json."""
    results = {"chord_results": [], "scale_results": [], "arpeggio_results": []}

    # Only run the search for the type indicated by parse_query (or explicit search_type)
    if search_type == "chords" or (search_type == "all" and type_ == "chord"):
        chord_results = search_chords(query)
        logger.debug(f"[DEBUG] Chord queryset count: {len(chord_results)}")
        results["chord_results"] = chord_results
        logger.debug(f"[DEBUG] Processed chord results: {results['chord_results']}")
    if search_type == "scales" or (search_type == "all" and type_ == "scale"):
        results["scale_results"] = _search_json_scales(note, quality, normalized_query)
        logger.debug(f"[DEBUG] Processed scale results: {results['scale_results']}")
    if search_type == "arpeggios" or (search_type == "all" and type_ == "arpeggio"):
        # Pass parsed components directly
        arpeggio_results = search_arpeggios(note=note, quality=quality, type_=type_)
        logger.debug(f"[DEBUG] Arpeggio queryset count: {len(arpeggio_results)}")
        results["arpeggio_results"] = arpeggio_results
        logger.debug(f"[DEBUG] Processed arpeggio results: {results['arpeggio_results']}")
    return results


def search_json(request: HttpRequest) -> JsonResponse:
    """
    JSON API endpoint for search results across chords, scales, and arpeggios.
    Returns results in a standardized JSON format for API consumers.
    """
    try:
        # Get search parameters
        query = request.GET.get("q", "")
        search_type = request.GET.get("search_type", "all")

        logger.debug(f"[DEBUG] Raw query: {query}")
        logger.debug(f"[DEBUG] Search type: {search_type}")

        # Format conversion for empty strings to None for proper filtering
        if not query.strip():
            logger.debug("[DEBUG] Empty query string received. Returning empty results.")
            return _empty_search_json_response()

        # --- Enhanced parsing and normalization ---
        note, type_, quality, position, inversion = parse_query(query)
        logger.debug(
            f"[DEBUG] Parsed query -> note: {note}, type: {type_}, quality: {quality}, position: {position}, inversion: {inversion}"
        )
        # Compose normalized query for downstream search functions
        normalized_query = f"{note} {quality}".strip()
        logger.debug(f"[DEBUG] Normalized query for search: '{normalized_query}'")

        results = _search_json_results(query, search_type, note, type_, quality, normalized_query)

        # Calculate total results
        total_results = (
            len(results["chord_results"])
            + len(results["scale_results"])
            + len(results["arpeggio_results"])
        )
        logger.debug(f"[DEBUG] Total results: {total_results}")

        # Return formatted response
        logger.debug(
            "[DEBUG] Final JSON response: {'query': query, 'total_results': total_results, ...}"
        )
        return JsonResponse(
            {
                "query": query,
                "total_results": total_results,
                "chord_results": results["chord_results"],
                "scale_results": results["scale_results"],
                "arpeggio_results": results["arpeggio_results"],
            }
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[ERROR] Exception in search_json: {e}\n{tb}")
        return JsonResponse({"error": str(e), "traceback": tb}, status=500)


def _unified_search_results(search_query, search_type, note, quality, type_) -> tuple[dict, int]:
    """Collect chord, scale and arpeggio results for the unified search view."""
    results = {"chords": [], "scales": [], "arpeggios": []}

    total_count = 0

    # Search for chords if requested
    if search_type in ["all", "chords"] and search_query:
        chord_results = search_chords(search_query)
        results["chords"] = chord_results
        total_count += len(chord_results)
        log_debug_info(
            f"Unified Search: Found {len(chord_results)} chords", chord_results[:5]
        )  # Log first 5 results

    # Search for scales if requested
    if search_type in ["all", "scales"] and search_query:
        scale_results = search_scales(search_query)
        results["scales"] = scale_results
        total_count += len(scale_results)
        log_debug_info(
            f"Unified Search: Found {len(scale_results)} scales", scale_results[:5]
        )  # Log first 5 results

    # Search for arpeggios if requested - FIXED: Pass parsed components instead of raw query
    if search_type in ["all", "arpeggios"] and search_query:
        arpeggio_results = search_arpeggios(note=note, quality=quality, type_=type_)
        results["arpeggios"] = arpeggio_results
        total_count += len(arpeggio_results)
        log_debug_info(
            f"Unified Search: Found {len(arpeggio_results)} arpeggios", arpeggio_results[:5]
        )  # Log first 5 results
    return results, total_count


def _log_unified_search_start(request: HttpRequest) -> None:
    """Log the banner for a unified search request."""
    logger.debug("\n" + "=" * 80)
    logger.debug("UNIFIED SEARCH INITIATED")
    logger.debug(f"REQUEST METHOD: {request.method}")
    logger.debug(f"REQUEST PATH: {request.path}")
    logger.debug("=" * 80)


def unified_search_view(request: HttpRequest) -> HttpResponse:
    """
    A unified search view that can search across chords, scales, and arpeggios
    """
    _log_unified_search_start(request)

    # Get search parameters
    search_query = request.GET.get("search_query", "")
    search_type = request.GET.get("search_type", "all")  # all, chords, scales, or arpeggios
    logger.debug(f"[DEBUG] search_query: {search_query}")
    logger.debug(f"[DEBUG] search_type: {search_type}")

    # Format conversion for empty strings to None for proper filtering
    if not search_query.strip():
        logger.debug("[DEBUG] Empty search_query string received. Returning empty results.")
        search_query = None

    # Parse and normalize the query using parse_query
    note, type_, quality, position, inversion = parse_query(search_query or "")
    logger.debug(
        f"[DEBUG] Parsed query -> note: {note}, type: {type_}, quality: {quality}, position: {position}, inversion: {inversion}"
    )
    normalized_query = f"{note} {quality}".strip()
    logger.debug(f"[DEBUG] Normalized query for search: '{normalized_query}'")

    results, total_count = _unified_search_results(search_query, search_type, note, quality, type_)

    # Check if JSON response is requested
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        log_debug_info(
            "Unified Search: Returning JSON response",
            {"total_count": total_count, "search_query": search_query, "search_type": search_type},
        )
        return JsonResponse(
            {
                "results": results,
                "total_count": total_count,
                "search_query": search_query or "",
                "search_type": search_type,
            }
        )

    # Prepare context for template rendering
    context = {
        "search_query": search_query or "",
        "search_type": search_type,
        "results": results,
        "total_count": total_count,
    }

    # Add common context
    common_context = get_common_context(request)
    context.update(common_context)

    logger.debug(
        "[DEBUG] Results summary: {'total_count': total_count, 'search_query': search_query, 'search_type': search_type, 'results': results}"
    )
    log_debug_info(
        "Unified Search: Rendering HTML template",
        {"total_count": total_count, "search_query": search_query, "search_type": search_type},
    )
    return render(request, "search/unified_search.html", context)


def _chord_matches(matched_chord, matched_type):
    """Return the ChordNotes queryset for the fuzzy matches, or None if there is no match."""
    if matched_chord and matched_type:
        matches = ChordNotes.objects.filter(
            Q(chord_name__icontains=matched_chord) & Q(type_name__icontains=matched_type)
        )
        if matches.exists():
            logger.debug(
                f"search_chords: Found {len(matches)} matches for chord_name='{matched_chord}', type_name='{matched_type}'."
            )
            return matches
    elif matched_chord:
        matches = ChordNotes.objects.filter(chord_name__icontains=matched_chord)
        if matches.exists():
            logger.debug(
                f"search_chords: Found {len(matches)} matches for chord_name='{matched_chord}'."
            )
            return matches
    elif matched_type:
        matches = ChordNotes.objects.filter(type_name__icontains=matched_type)
        if matches.exists():
            logger.debug(
                f"search_chords: Found {len(matches)} matches for type_name='{matched_type}'."
            )
            return matches
    return None


def search_chords(search_query: str) -> list[dict]:
    """Search for chords matching the query, supporting combined type and position queries like 'Major7 V2' and common synonyms."""
    logger.debug(f"Entering search_chords with query: '{search_query}'")
    try:
        from .search_utils import best_fuzzy_match, parse_query

        note, _, quality, _, _ = parse_query(search_query)
        chord_options = list(ChordNotes.objects.values_list("chord_name", flat=True).distinct())
        type_options = list(ChordNotes.objects.values_list("type_name", flat=True).distinct())

        chord_name = _CHORD_QUALITY_MAP.get(quality.lower(), quality.title() if quality else None)
        logger.debug(
            f"search_chords: Parsed quality '{quality}' mapped to chord_name '{chord_name}'"
        )
        # Try to match both chord_name and type_name
        matched_chord = (
            best_fuzzy_match(chord_name or "", chord_options, cutoff=0.7, case_sensitive=False)
            if chord_name
            else None
        )
        matched_type = best_fuzzy_match(
            search_query, type_options, cutoff=0.7, case_sensitive=False
        )
        matches = _chord_matches(matched_chord, matched_type)
        if matches is not None:
            filtered = matches.filter(tonal_root=ROOT_NAME_TO_PITCH.get(note)) if note else matches
            return process_chord_results(filtered, root_note=note)
        logger.debug(
            f"search_chords: No matches found for chord_name='{matched_chord}', type_name='{matched_type}', including variants."
        )
        return []
    except Exception as e:
        logger.error(f"Error searching chords: {str(e)}")
        logger.error(traceback.format_exc())
        logger.debug(f"search_chords: Error occurred - {str(e)}")
        return []


def _filter_chords_by_root(chords: list, root_note: str) -> list:
    """Filter chords by tonal_root, falling back to a name prefix, else keep all."""
    root_pitch = ROOT_NAME_TO_PITCH.get(root_note)
    filtered = [ch for ch in chords if getattr(ch, "tonal_root", None) == root_pitch]
    logger.debug(f"Filtered by tonal_root ({root_note} -> {root_pitch}): {len(filtered)} matches.")
    if filtered:
        return filtered
    # Fallback: match by chord_name prefix (e.g., 'A Major 7')
    fallback = [ch for ch in chords if str(ch.chord_name).lower().startswith(root_note.lower())]
    logger.debug(f"Fallback by chord_name prefix '{root_note}': {len(fallback)} matches.")
    if fallback:
        return fallback
    logger.debug("No matches for tonal_root or chord_name prefix, skipping root filter.")
    return chords


def _chord_to_result(chord, root_note: str | None) -> dict:
    """Convert one chord model instance into the standardized result dict."""
    positions = list(
        ChordPosition.objects.filter(notes_name=chord).values_list("inversion_order", flat=True)
    )
    notes = _collect_notes(chord, _CHORD_NOTE_ATTRS)
    intervals = _infer_intervals(chord, notes)
    name = _prefixed_name(chord.chord_name, root_note)
    root_id = (
        ROOT_NAME_TO_ID.get(root_note)
        or ROOT_NAME_TO_ID[PITCH_TO_ROOT_NAME.get(getattr(chord, "tonal_root", 0), "C")]
    )
    url = f"/?root={root_id}&models_select=3&type_options_select={chord.type_name}&chords_options_select={chord.chord_name}&note_range={chord.range}&position_select=Root+Position"
    return {
        "id": chord.id,
        "name": name,
        "type": chord.type_name,
        "category": getattr(chord.category, "category_name", None)
        if hasattr(chord, "category")
        else None,
        "positions": positions,
        "notes": notes,
        "intervals": intervals,
        "url": url,
    }


def process_chord_results(queryset: QuerySet | list, root_note: str | None = None) -> list[dict]:
    """Process chord query results into a standardized format"""
    logger.debug(f"Entering process_chord_results with {len(queryset)} items.")
    chords_to_process = list(queryset)
    # Robust filtering: Try tonal_root, then fallback to name prefix, else skip filtering
    if root_note:
        chords_to_process = _filter_chords_by_root(chords_to_process, root_note)
    # Now prioritize e-string voicings among filtered chords
    prioritized = [
        ch
        for ch in chords_to_process
        if "e" in getattr(ch, "range", "") and "E" not in getattr(ch, "range", "")
    ]
    if prioritized:
        logger.debug(f"Prioritized e-string voicings: {len(prioritized)} matches.")
        chords_to_process = prioritized
    processed_results = []
    for chord in chords_to_process:
        chord_result = _chord_to_result(chord, root_note)
        logger.debug(f"process_chord_results: Processed chord ID {chord.id}", chord_result)
        processed_results.append(chord_result)
    logger.debug(f"Exiting process_chord_results with {len(processed_results)} processed items.")
    return processed_results


def search_scales(search_query: str) -> list[dict]:
    """Search for scales by root and scale type (quality)."""
    logger.debug(f"Entering search_scales with query: '{search_query}'")
    # Parse canonical note and quality
    note, _, quality, _, _ = parse_query(search_query)
    root_obj = resolve_root(note)
    logger.debug(f"search_scales: Resolved root '{note}' to DB object: {root_obj}")
    if not root_obj:
        logger.debug(f"search_scales: No valid root found for '{note}', aborting search.")
        return []
    try:
        qs = Notes.objects.filter(category__category_name__icontains="scale")
        if search_query.isdigit():
            qs = qs.filter(pk=int(search_query))
        else:
            # Search for specific root scales, fallback to templates (tonal_root=0)
            qs_specific = qs.filter(tonal_root=root_obj.pitch, note_name__icontains=quality)
            qs_template = qs.filter(tonal_root=0, note_name__icontains=quality)
            qs = qs_specific if qs_specific.exists() else qs_template
        logger.debug(f"search_scales: Final queryset count: {qs.count()}")
        if qs.exists():
            results = process_scale_results(qs, user_note=note, user_quality=quality)
            return results
        logger.debug(f"search_scales: No results found for '{search_query}'.")
        return []
    except Exception as e:
        logger.error(f"Error searching scales: {str(e)}")
        logger.error(traceback.format_exc())
        logger.debug(f"search_scales: Error occurred - {str(e)}")
        return []


def _scale_to_result(scale, user_note: str | None) -> dict:
    """Convert one scale model instance into the standardized result dict."""
    notes = _collect_notes(scale, _SCALE_NOTE_ATTRS)
    intervals = _infer_intervals(scale, notes)
    name = _prefixed_name(scale.note_name, user_note)
    root_id = ROOT_NAME_TO_ID.get(user_note, 1)
    url = f"/?root={root_id}&models_select=1&notes_options_select={scale.id}&position_select=0"
    return {
        "id": scale.id,
        "name": name,
        "type": getattr(scale.category, "category_name", "") if hasattr(scale, "category") else "",
        "notes": notes,
        "intervals": intervals,
        "url": url,
    }


def process_scale_results(
    queryset: QuerySet | list, user_note: str | None = None, user_quality: str | None = None
) -> list[dict]:
    """Process scale query results into a standardized format, preserving user note and quality for naming if possible."""
    logger.debug(f"Entering process_scale_results with {len(queryset)} items.")
    processed_results = []
    for scale in queryset:
        scale_result = _scale_to_result(scale, user_note)
        logger.debug(f"process_scale_results: Processed scale ID {scale.id}", scale_result)
        processed_results.append(scale_result)
    logger.debug(f"Exiting process_scale_results with {len(processed_results)} processed items.")
    return processed_results


def _find_arpeggio_root(note: str):
    """Look up the Root for ``note`` (for URL generation only), or None."""
    root_obj = Root.objects.filter(name__iexact=note).first()
    if not root_obj:
        # Try alternate lookup
        root_id = ROOT_NAME_TO_ID.get(note)
        if root_id:
            root_obj = Root.objects.filter(id=root_id).first()

    if root_obj:
        logger.debug(f"Found root_obj for '{note}': ID={root_obj.id}, pitch={root_obj.pitch}")
    else:
        logger.warning(f"Could not find root for note: {note}")
    return root_obj


def _filter_arpeggios_by_quality(qs, quality: str):
    """Filter arpeggios by quality; may return a relevance-sorted list instead of a QuerySet."""
    # Find which quality group the search term belongs to
    search_quality_group = None
    for group, terms in _ARPEGGIO_QUALITY_TERMS.items():
        if quality.lower() in [t.lower() for t in terms]:
            search_quality_group = group
            break

    # Apply quality filtering with priority for exact matches
    quality_filters = Q()
    if search_quality_group:
        # Add exact match terms for the identified quality group
        for term in _ARPEGGIO_QUALITY_TERMS.get(search_quality_group, []):
            quality_filters |= Q(note_name__icontains=term)
        logger.debug(f"Applying quality filters for '{quality}': {quality_filters}")
        qs = qs.filter(quality_filters)
    else:
        # If quality doesn't match any known group, use it directly
        logger.debug(f"Applying direct quality filter for '{quality}'")
        qs = qs.filter(note_name__icontains=quality)

    # Sort results by relevance (exact matches first)
    # This ensures Minor arpeggios appear before Major when searching for "minor"
    if search_quality_group:
        results_list = list(qs)
        # Move exact matches to the front
        results_list.sort(key=lambda x: search_quality_group.lower() not in x.note_name.lower())
        # Convert back to a QuerySet-like list
        qs = results_list
    return qs


def search_arpeggios(
    note: str | None = None, quality: str | None = None, type_: str | None = None
) -> list[dict]:
    """Search for arpeggios using parsed components: note, quality, and type."""
    logger.debug(
        f"Entering search_arpeggios with note='{note}', quality='{quality}', type_='{type_}'"
    )
    try:
        # Start with base arpeggio query - Use Notes model with arpeggio category
        arpeggio_category = NotesCategory.objects.filter(
            category_name__icontains="arpeggio"
        ).first()

        if not arpeggio_category:
            logger.error("No arpeggio category found in NotesCategory model.")
            return []

        qs = Notes.objects.filter(category=arpeggio_category)

        # Store the root information for later use in result processing
        # but don't filter by it since arpeggios are stored as templates with tonal_root=0
        root_obj = None

        if note:
            root_obj = _find_arpeggio_root(note)

        # If quality is provided, find arpeggios that match this quality
        if quality:
            qs = _filter_arpeggios_by_quality(qs, quality)
        else:
            logger.debug("No quality provided, skipping quality filter.")

        # Handle pentatonic type if specified
        if type_ and type_.lower() == "pentatonic":
            # If we've sorted, filter in Python
            if isinstance(qs, list):
                qs = [item for item in qs if "pentatonic" in item.note_name.lower()]
            else:
                qs = qs.filter(note_name__icontains="pentatonic")

        logger.debug(
            f"search_arpeggios: Final queryset count before processing: {len(qs) if isinstance(qs, list) else qs.count()}"
        )

        if qs:
            # Pass the root information to the processing function
            return process_arpeggio_results(qs, root_note=note, root_obj=root_obj, quality=quality)
        else:
            # If specific search yields no results, consider a broader fallback (optional)
            # For now, return empty if specific filters match nothing.
            logger.debug(
                f"search_arpeggios: No results found for note='{note}', quality='{quality}'."
            )
            return []

    except Exception as e:
        logger.error(f"Error searching arpeggios: {str(e)}")
        logger.error(traceback.format_exc())
        logger.debug(f"search_arpeggios: Error occurred - {str(e)}")
        return []


def _arpeggio_root_id(arpeggio, root_note, root_obj):
    """Resolve the root id for an arpeggio URL; returns (root_id, root_obj)."""
    root_id = None
    if root_obj:
        root_id = root_obj.id
    elif root_note:
        # Try to find root by name
        root_obj = Root.objects.filter(name__iexact=root_note).first()
        if root_obj:
            root_id = root_obj.id
        else:
            # Try lookup in mapping
            root_id = ROOT_NAME_TO_ID.get(root_note)

    if not root_id:
        # Default to A if all else fails
        logger.warning(f"Could not find root ID for arpeggio {arpeggio.id}, using default ID 14")
        root_id = 14  # Default to A
    return root_id, root_obj


def process_arpeggio_results(
    queryset: QuerySet | list,
    root_note: str | None = None,
    root_obj=None,
    quality: str | None = None,
) -> list[dict]:
    """Process arpeggio query results into a standardized format"""
    # Handle both QuerySet and list objects
    count = len(queryset) if isinstance(queryset, list) else queryset.count()
    logger.debug(f"Process arpeggio results for {count} items, root_note={root_note}")

    results = []
    base_url = "/"

    for arpeggio in queryset:
        try:
            # Extract notes for this arpeggio (up to 12 notes)
            notes = _collect_notes(arpeggio, _ARPEGGIO_NOTE_ATTRS)
            intervals = _infer_intervals(arpeggio, notes)
            name = _prefixed_name(arpeggio.note_name, root_note)
            root_id, root_obj = _arpeggio_root_id(arpeggio, root_note, root_obj)

            # Always set type to include 'Arpeggio'
            type_str = "Arpeggio"

            # Generate URL for this arpeggio - include models_select=2 for arpeggios
            # Use the specific arpeggio ID in the URL
            url = f"{base_url}?root={root_id}&models_select=2&notes_options_select={arpeggio.id}&position_select=0"

            results.append(
                {
                    "id": arpeggio.id,
                    "name": name,
                    "type": type_str,
                    "notes": notes,
                    "intervals": intervals,
                    "url": url,
                }
            )

        except Exception as e:
            logger.error(
                f"Error processing arpeggio {getattr(arpeggio, 'id', 'unknown')}: {str(e)}"
            )
            logger.error(traceback.format_exc())

    return results
