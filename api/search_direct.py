"""Direct-match search: resolves a free-text query to a single fretboard URL."""

import logging
import re
from urllib.parse import urlencode

from django.http import HttpRequest, JsonResponse
from thefuzz import fuzz, process

from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.models_chords import ChordNotes
from positionfinder.search_utils import ROOT_NAME_TO_ID, get_root_id_from_name

from .search_common import _ROOT_PREFIX_RE, MIN_SCORE_THRESHOLD, extract_root_note
from .search_normalize import normalize_search_term

logger = logging.getLogger("api.views_search")


def reverse(*args, **kwargs) -> str:
    """Resolve a URL through ``api.views_search.reverse`` so test seams still apply."""
    from api import views_search

    return views_search.reverse(*args, **kwargs)


def _fretboard_url(params: dict) -> str:
    """Build the fretboard URL for the given query parameters."""
    return f"{reverse('fretboard')}?{urlencode(params)}"


def _is_pentatonic_typo_query(query: str) -> bool:
    """Whether the query asks for a (possibly misspelled) minor pentatonic."""
    return any(term in query.lower() for term in ["pentatonic", "penatonic", "penat"]) and any(
        term in query.lower() for term in ["minor", "min"]
    )


def _is_penta_query(query: str) -> bool:
    """Whether the query contains 'penat' or 'penta'."""
    return "penat" in query.lower() or "penta" in query.lower()


def _find_minor_pentatonic_pk() -> int:
    """Look up the Minor Pentatonic scale pk, falling back to 49."""
    try:
        # Try to find Minor Pentatonic by name
        print("[DM_TRACE] Searching for 'Minor Pentatonic' in Notes table...")
        pentatonic_scales = list(Notes.objects.filter(note_name__icontains="pentatonic"))
        for scale in pentatonic_scales:
            print(f"[DM_TRACE] Found scale: ID={scale.pk}, Name={scale.note_name}")
            # If we find a scale with 'minor' and 'pentatonic', use that
            if "minor" in scale.note_name.lower() and "pentatonic" in scale.note_name.lower():
                print(f"[DM_TRACE] Found Minor Pentatonic: ID={scale.pk}")
                return scale.pk
        # Fallback to ID 49 which should be Minor Pentatonic
        print("[DM_TRACE] No Minor Pentatonic found, using fallback ID=49")
        return 49  # Assuming 49 is a specific PK
    except Exception as e:
        print(f"[DM_TRACE] Error searching for Minor Pentatonic: {str(e)}")
        return 49  # Assuming 49 is a specific PK


def _pentatonic_override_response(query: str) -> JsonResponse | None:
    """Build the direct pentatonic response for a query with a root, else None."""
    print("[DM_TRACE] *** DIRECT PENTATONIC OVERRIDE ENGAGED ***")

    root_note = extract_root_note(query)
    if root_note is None:
        return None
    print(f"[DM_TRACE] Extracted root note: '{root_note}'")

    # Find root ID
    root_pk = get_root_id_from_name(root_note)
    print(f"[DM_TRACE] Extracted root note: '{root_note}' -> ID: {root_pk}")
    if root_pk:
        # Find the canonical spelling from the mapping
        for name, pk in ROOT_NAME_TO_ID.items():
            if pk == root_pk:
                print(f"[DM_TRACE] Canonical root name for ID {root_pk}: '{name}'")
                break
    else:
        print(f"[DM_TRACE] No root ID found for '{root_note}' using custom mapping.")

    pentatonic_pk = _find_minor_pentatonic_pk()
    print(f"[DM_TRACE] Using pentatonic_pk={pentatonic_pk}")

    params = {
        "root": root_pk,
        "models_select": 1,  # Scale
        "notes_options_select": pentatonic_pk,
        "position_select": 0,
    }
    url = _fretboard_url(params)
    print(f"[DM_TRACE] DIRECT PENTATONIC URL OVERRIDE: {url}")

    # Return the URL in both formats to ensure the frontend gets it
    return JsonResponse(
        {
            "url": url,  # This is what the frontend is looking for
            "debug": {"matched_url": url},
        }
    )


def _trace_query_root(query: str) -> int | None:
    """Resolve the root id at the start of the query, tracing each step."""
    root_note = extract_root_note(query)
    root_pk = None
    if root_note is not None:
        root_pk = get_root_id_from_name(root_note)
        print(f"[DM_TRACE] Extracted root note: '{root_note}' -> ID: {root_pk}")
        if root_pk:
            # Find the canonical spelling from the mapping
            for name, pk in ROOT_NAME_TO_ID.items():
                if pk == root_pk:
                    print(f"[DM_TRACE] Canonical root name for ID {root_pk}: '{name}'")
                    break
        else:
            print(f"[DM_TRACE] No root ID found for '{root_note}' using custom mapping.")
    return root_pk


def _scale_items(roots, scale_types, root_pk: int | None) -> list[dict]:
    """Build the search items for every root and scale type."""
    items = []
    for root in roots:
        for scale_type in scale_types:
            name = f"{root.name} {scale_type.category_name}"
            # Use extracted root if available, else fallback to root.pk
            if root_pk is not None:
                used_root_pk = root_pk
                print(f"[DM_TRACE] Assigned root param: {used_root_pk} (custom mapping)")
            else:
                used_root_pk = root.pk
                print(f"[DM_TRACE] Fallback root param: {used_root_pk} -> {root.name}")
            params = {
                "root": used_root_pk,
                "models_select": 1,
                "notes_options_select": scale_type.pk,
                "position_select": 0,
            }
            url = _fretboard_url(params)
            items.append({"name": name, "type": "scale", "url": url, "search_key": name})
    return items


def _arpeggio_items(roots, arpeggio_types) -> list[dict]:
    """Build the search items for every root and arpeggio type."""
    items = []
    for root in roots:
        for arpeggio_type in arpeggio_types:
            name = f"{root.name} {arpeggio_type.category_name}"
            params = {
                "root": root.pk,
                "models_select": 2,
                "notes_options_select": arpeggio_type.pk,
                "position_select": 0,
            }
            url = _fretboard_url(params)
            items.append({"name": name, "type": "arpeggio", "url": url, "search_key": name})
    return items


def _chord_items(roots, chord_types) -> list[dict]:
    """Build the search items for every root and chord type."""
    items = []
    for root in roots:
        for chord_type in chord_types:
            # Construct the search key for chords. Use the root name and chord name.
            search_key = f"{root.name} {chord_type.chord_name}"

            params = {
                "root": root.pk,
                "models_select": 3,  # Chord
                "notes_options_select": chord_type.pk,
                "position_select": 0,
            }
            url = _fretboard_url(params)

            items.append(
                {
                    "name": search_key,  # Use the constructed search key as the display name
                    "type": "chord",
                    "url": url,
                    "search_key": search_key,
                }
            )
    return items


def _build_items(root_pk: int | None) -> list[dict]:
    """Fetch the models and build the full list of searchable items."""
    print("[DM_TRACE] Fetching models...")
    roots = Root.objects.all()
    scale_types = NotesCategory.objects.filter(category_name__icontains="scale")
    arpeggio_types = NotesCategory.objects.filter(category_name__icontains="arpeggio")
    chord_types = ChordNotes.objects.all()
    print("[DM_TRACE] Models fetched.")

    print("[DM_TRACE] Building item list...")
    all_items = []
    all_items += _scale_items(roots, scale_types, root_pk)
    all_items += _arpeggio_items(roots, arpeggio_types)
    all_items += _chord_items(roots, chord_types)
    print(f"[DM_TRACE] Item list built. Total items: {len(all_items)}")
    return all_items


def _find_exact_match(all_items: list[dict], normalized_query: str) -> dict | None:
    """Return the first item whose name equals the normalized query."""
    for item in all_items:
        if item["name"].lower() == normalized_query.lower():
            print(f"[DM_TRACE] Found exact match with normalized query: '{item['name']}'")
            return item
    return None


def _exact_match_response(
    query: str, normalized_query: str, exact_match: dict, total: int
) -> JsonResponse:
    """Build the response for an exact name match."""
    print(f"[DM_TRACE] Using exact match: '{exact_match['name']}' with URL={exact_match['url']}")
    return JsonResponse(
        {
            "debug": {
                "query": query,
                "normalized_query": normalized_query,
                "total_potential_targets": total,
                "match_method": "exact_match",
                "best_match_key": exact_match["name"],
                "best_match_score": 100,  # Perfect score for exact match
                "matched_url": exact_match["url"],
            }
        }
    )


def _log_pentatonic_diagnostics() -> None:
    """Print database diagnostics about pentatonic entries."""
    print("[DM_TRACE] Database diagnostics for Minor Pentatonic debugging:")

    # Check for pentatonic scale in NotesCategory
    try:
        pent_cats = NotesCategory.objects.filter(category_name__icontains="pentatonic")
        print(f"[DM_TRACE] Found {pent_cats.count()} NotesCategory items containing 'pentatonic':")
        for cat in pent_cats:
            print(f"[DM_TRACE]   - ID: {cat.pk}, Name: {cat.category_name}")
    except Exception as e:
        print(f"[DM_TRACE] Error checking NotesCategory: {str(e)}")

    # Check Notes table for Minor Pentatonic
    try:
        pent_notes = Notes.objects.filter(note_name__icontains="pentatonic")
        print(f"[DM_TRACE] Found {pent_notes.count()} Notes items containing 'pentatonic':")
        for note in pent_notes:
            print(
                f"[DM_TRACE]   - ID: {note.pk}, Name: {note.note_name}, Category: {note.category_id}"
            )
            # Check if ID 49 is specifically Minor Pentatonic
            if note.pk == 49:
                print(f"[DM_TRACE]   *** ID 49 CONFIRMED as: {note.note_name} ***")
    except Exception as e:
        print(f"[DM_TRACE] Error checking Notes: {str(e)}")


def _verify_pentatonic_note_49(params: dict) -> None:
    """Check that Notes pk 49 exists, else switch params to a pentatonic by name."""
    try:
        note_obj = Notes.objects.filter(pk=49).first()
        if note_obj:
            print(f"[DM_TRACE] Verified Notes object ID=49: {note_obj.note_name}")
        else:
            print("[DM_TRACE] WARNING: Notes ID=49 does not exist in database!")

            # Try to find Minor Pentatonic by name instead
            alt_note = Notes.objects.filter(note_name__icontains="minor pentatonic").first()
            if alt_note:
                print(f"[DM_TRACE] Found alternative Minor Pentatonic by name: ID={alt_note.pk}")
                # Use this ID instead
                params["notes_options_select"] = alt_note.pk
    except Exception as e:
        print(f"[DM_TRACE] Error verifying Notes ID 49: {str(e)}")


def _hardcoded_pentatonic_response(query: str, normalized_query: str) -> JsonResponse | None:
    """Build the hardcoded Minor Pentatonic response for a query with a root."""
    root_note = extract_root_note(query)
    if root_note is None:
        return None
    print(f"[DM_TRACE] Extracted root note: '{root_note}'")

    try:
        # Try to find the root object directly from the database
        root_objs = Root.objects.filter(name__iexact=root_note)
        print(f"[DM_TRACE] Found {root_objs.count()} matching Root objects for '{root_note}'")

        root_obj = root_objs.first()
        if root_obj:
            root_pk = root_obj.pk
            print(f"[DM_TRACE] Using Root object: ID={root_pk}, Name={root_obj.name}")

            # HARDCODED: Use the known ID (49) for Minor Pentatonic scale
            params = {
                "root": root_pk,
                "models_select": 1,  # Scales
                "notes_options_select": 49,  # HARDCODED ID for Minor Pentatonic
                "position_select": 0,
            }
            _verify_pentatonic_note_49(params)

            print(f"[DM_TRACE] URL parameters: {params}")

            base_url = reverse("fretboard")
            print(f"[DM_TRACE] Base URL: {base_url}")

            url = f"{base_url}?{urlencode(params)}"
            print(
                f"[DM_TRACE] Hardcoded fix: Creating direct URL for {root_note} Minor Pentatonic: {url}"
            )

            return JsonResponse(
                {
                    "debug": {
                        "query": query,
                        "normalized_query": normalized_query,
                        "match_method": "direct_pentatonic_hardcoded",
                        "best_match_key": f"{root_note} Minor Pentatonic Scale",
                        "best_match_score": 100,
                        "matched_url": url,
                    }
                }
            )
    except Exception as e:
        print(f"[DM_TRACE] Error in hardcoded pentatonic fix: {str(e)}")
    return None


def _pentatonic_special_match(
    query: str, normalized_query: str, all_items: list[dict]
) -> JsonResponse | None:
    """Find a pentatonic scale item whose root matches the query's root."""
    for item in all_items:
        if item["type"] == "scale" and "pentatonic" in item["name"].lower():
            # Extract root note from query and item
            query_root_match = re.search(_ROOT_PREFIX_RE, query)
            item_root_match = re.search(r"^([A-G][#b]?)\s", item["name"])

            if query_root_match and item_root_match:
                query_root = query_root_match.group(1).upper()
                item_root = item_root_match.group(1)

                # If roots match, this is likely our target
                if query_root == item_root:
                    print(f"[DM_TRACE] Found pentatonic match with matching root: '{item['name']}'")
                    return JsonResponse(
                        {
                            "debug": {
                                "query": query,
                                "normalized_query": normalized_query,
                                "match_method": "pentatonic_special_match",
                                "best_match_key": item["name"],
                                "best_match_score": 95,  # High score for this type of match
                                "matched_url": item["url"],
                            }
                        }
                    )
    return None


def _minor_pentatonic_special(
    query: str, normalized_query: str, all_items: list[dict]
) -> JsonResponse | None:
    """Hardcoded handling of Minor Pentatonic queries; None to continue matching."""
    print(f"[DM_TRACE] Applying HARDCODED FIX for Minor Pentatonic search: '{query}'")
    _log_pentatonic_diagnostics()

    response = _hardcoded_pentatonic_response(query, normalized_query)
    if response is not None:
        return response

    # Continue with regular matching if the hardcoded fix fails
    return _pentatonic_special_match(query, normalized_query, all_items)


def _build_processed_queries(query: str, normalized_query: str) -> list[str]:
    """Build the de-duplicated query variations used for fuzzy matching."""
    processed_queries = [
        query.lower().replace(" ", ""),
        normalized_query.lower().replace(" ", ""),
    ]

    # Add special variations for known patterns
    if "minor" in query.lower() and "penta" in query.lower():
        # Try adding "scale" suffix for pentatonic
        root_match = re.search(_ROOT_PREFIX_RE, query)
        if root_match:
            root = root_match.group(1).upper()
            processed_queries.append(f"{root}MinorPentatonicScale".lower())

    # Remove duplicates
    processed_queries = list(set(processed_queries))
    print(f"[DM_TRACE] Preprocessed queries: {processed_queries}")
    return processed_queries


def _build_choices_map(all_items: list[dict]) -> dict:
    """Map each whitespace-free lowercase search key to its first item."""
    processed_choices_map = {}
    for item in all_items:
        processed_key = item["search_key"].lower().replace(" ", "")
        # Store the *first* original item encountered for a given processed key
        # (pentatonic/scale priority branches all reduce to this rule)
        if processed_key not in processed_choices_map:
            processed_choices_map[processed_key] = item
    return processed_choices_map


def custom_pentatonic_scorer(query_str: str, choice_str: str) -> int:
    """Fuzzy scorer that boosts pentatonic scales and matching root notes."""
    base_score = fuzz.token_set_ratio(query_str, choice_str)

    # Give higher score for pentatonic scales
    if "pentatonic" in choice_str.lower() and "scale" in choice_str.lower():
        base_score += 20  # Boost pentatonic scales

    # Extract root notes for more precise matching
    query_root_match = re.search(r"([a-g][#b]?)", query_str[:2].lower())
    choice_root_match = re.search(r"([a-g][#b]?)", choice_str[:2].lower())

    if query_root_match and choice_root_match:
        if query_root_match.group(1) == choice_root_match.group(1):
            base_score += 10  # Boost for matching root note

    # Cap at 100
    return min(base_score, 100)


def _select_scorer(query: str):
    """Choose the fuzzy scorer for the query."""
    scorer_to_use = fuzz.token_set_ratio
    print(f"[DM_TRACE] Using scorer: {scorer_to_use.__name__}")

    # Special scoring for pentatonic related searches
    if _is_penta_query(query):
        scorer_to_use = custom_pentatonic_scorer
        print(f"[DM_TRACE] Using custom pentatonic scorer due to query: '{query}'")
    return scorer_to_use


def _best_query_match(
    processed_queries: list[str], choices: list[str], scorer_to_use
) -> tuple[tuple | None, str | None]:
    """Match every query variation and keep the best (result, query)."""
    best_match_result = None
    best_processed_query = None

    for processed_query in processed_queries:
        print(f"[DM_TRACE] Trying to match query variation: '{processed_query}'")

        match_result = process.extractOne(processed_query, choices, scorer=scorer_to_use)

        if match_result:
            print(
                f"[DM_TRACE] Raw result for '{processed_query}': Match='{match_result[0]}', Score={match_result[1]}"
            )

            # Keep the best match across all query variations
            if not best_match_result or match_result[1] > best_match_result[1]:
                best_match_result = match_result
                best_processed_query = processed_query
        else:
            print(f"[DM_TRACE] No result for query variation: '{processed_query}'")
    return best_match_result, best_processed_query


def _prioritize_pentatonic_scale(
    all_items: list[dict], scorer_to_use, best_processed_query: str, best_match: str, score
) -> tuple[str, int]:
    """Prefer a pentatonic scale scoring within 10 points of the best match."""
    for item in all_items:
        if item["type"] == "scale" and "pentatonic" in item["name"].lower():
            item_key = item["search_key"].lower().replace(" ", "")
            item_score = scorer_to_use(best_processed_query, item_key)

            # If this scale's score is close enough to best match, prioritize it
            if item_score >= score - 10:  # Within 10 points of best
                print(
                    f"[DM_TRACE] Prioritizing scale match: '{item['name']}' with score {item_score}"
                )
                return item_key, item_score
    return best_match, score


def _evaluate_best_match(
    query: str,
    all_items: list[dict],
    scorer_to_use,
    best_match_result: tuple | None,
    best_processed_query: str | None,
) -> tuple[str | None, int]:
    """Apply the score threshold and scale priority to the best match."""
    best_processed_match = None
    score = 0

    if best_match_result:
        best_processed_match, score = best_match_result
        print(
            f"[DM_TRACE] Best match overall from query '{best_processed_query}': Match='{best_processed_match}', Score={score}"
        )

        # Check if the score meets threshold
        if score >= MIN_SCORE_THRESHOLD:
            print(f"[DM_TRACE] Score {score} meets threshold {MIN_SCORE_THRESHOLD}.")

            # Prioritize scales for scale-related queries
            if _is_penta_query(query) or "scale" in query.lower():
                best_processed_match, score = _prioritize_pentatonic_scale(
                    all_items, scorer_to_use, best_processed_query, best_processed_match, score
                )
        else:
            print(f"[DM_TRACE] Score {score} is BELOW threshold {MIN_SCORE_THRESHOLD}.")
            # Reset match info since it didn't meet threshold; keep score for reporting
            best_processed_match = None
    else:
        print("[DM_TRACE] No match found across any query variations.")
    return best_processed_match, score


def _correct_pentatonic_chord_url(matched_url: str) -> str:
    """Replace a chord URL matched by a pentatonic search with the scale URL."""
    print(
        "[DM_TRACE] !!! WARNING: Pentatonic search is matching to a chord (models_select=3). Attempting to fix."
    )

    # Extract the root ID from the current URL
    root_param = re.search(r"root=(\d+)", matched_url)
    if root_param:
        root_id = root_param.group(1)

        # Try to correct by forcing to scale model and pentatonic
        try:
            # Look for Minor Pentatonic scale by name
            pent_scale = Notes.objects.filter(note_name__icontains="minor pentatonic").first()
            if pent_scale:
                pent_id = pent_scale.pk
                print(f"[DM_TRACE] Found Minor Pentatonic with ID={pent_id}")

                corrected_params = {
                    "root": root_id,
                    "models_select": 1,  # Scale
                    "notes_options_select": pent_id,
                    "position_select": 0,
                }
                corrected_url = _fretboard_url(corrected_params)
                print(f"[DM_TRACE] CORRECTED URL: {corrected_url}")
                matched_url = corrected_url
            else:
                print("[DM_TRACE] Could not find Minor Pentatonic scale in database")
        except Exception as e:
            print(f"[DM_TRACE] Error in pentatonic URL correction: {str(e)}")
    return matched_url


def _lookup_matched_url(
    query: str,
    best_processed_match: str | None,
    score,
    processed_choices_map: dict,
) -> tuple[str | None, str | None]:
    """Resolve the matched item to (url, original key)."""
    matched_url = None
    best_match_original_key = None

    if best_processed_match and score >= MIN_SCORE_THRESHOLD:
        # Retrieve the original item using the mapping
        original_item = processed_choices_map.get(best_processed_match)
        if original_item:
            matched_url = original_item["url"]
            best_match_original_key = original_item["search_key"]
            print(
                f"[DM_TRACE] Found original item for key '{best_match_original_key}': URL={matched_url}"
            )

            # SAFETY CHECK: Verify we're returning the right type for pentatonic searches
            if _is_penta_query(query) and "models_select=3" in matched_url:
                matched_url = _correct_pentatonic_chord_url(matched_url)
        else:
            print(
                f"[DM_TRACE] !!! ERROR: Match found, but best_processed_match '{best_processed_match}' not found back in map!"
            )
    else:
        print(f"[DM_TRACE] No match found meeting threshold {MIN_SCORE_THRESHOLD}.")
    return matched_url, best_match_original_key


def _emergency_pentatonic_url(query: str) -> str | None:
    """Last-resort Minor Pentatonic URL for penta queries without a match."""
    print("[DM_TRACE] Performing EMERGENCY PENTATONIC CHECK as last resort")
    matched_url = None

    try:
        # Query for notes containing 'pentatonic'
        pentatonic_notes = Notes.objects.filter(note_name__icontains="pentatonic")
        for note in pentatonic_notes:
            print(
                f"[DM_TRACE] DATABASE: Found pentatonic note: ID={note.pk}, Name={note.note_name}"
            )

        # Direct check for ID 49
        note_49 = Notes.objects.filter(pk=49).first()
        if note_49:
            print(f"[DM_TRACE] DATABASE: ID 49 exists as: {note_49.note_name}")
        else:
            print("[DM_TRACE] DATABASE: ID 49 DOES NOT EXIST in Notes table")

        root_note = extract_root_note(query)
        if root_note is not None:
            # Find root ID
            root_pk = get_root_id_from_name(root_note)
            print(f"[DM_TRACE] Extracted root note: '{root_note}' -> ID: {root_pk}")
            if root_pk is None:
                print(f"[DM_TRACE] No root ID found for '{root_note}' using custom mapping.")

            # Now look for Minor Pentatonic note
            pent_note = Notes.objects.filter(note_name__icontains="minor pentatonic").first()
            if pent_note:
                print(f"[DM_TRACE] EMERGENCY FIX: Found Minor Pentatonic with ID={pent_note.pk}")
                emergency_params = {
                    "root": root_pk,
                    "models_select": 1,  # Scale
                    "notes_options_select": pent_note.pk,
                    "position_select": 0,
                }
                matched_url = _fretboard_url(emergency_params)
                print(f"[DM_TRACE] EMERGENCY PENTATONIC URL: {matched_url}")
    except Exception as e:
        print(f"[DM_TRACE] Error in emergency pentatonic check: {str(e)}")
    return matched_url


def _fuzzy_match(query: str, normalized_query: str, all_items: list[dict]) -> JsonResponse:
    """Fuzzy-match the query against all items and build the debug response."""
    processed_queries = _build_processed_queries(query, normalized_query)

    processed_choices_map = _build_choices_map(all_items)
    processed_choices_list = list(processed_choices_map.keys())
    print(
        f"[DM_TRACE] Built map from {len(processed_choices_list)} unique processed keys back to original items."
    )

    scorer_to_use = _select_scorer(query)
    best_match_result, best_processed_query = _best_query_match(
        processed_queries, processed_choices_list, scorer_to_use
    )
    best_processed_match, score = _evaluate_best_match(
        query, all_items, scorer_to_use, best_match_result, best_processed_query
    )
    matched_url, best_match_original_key = _lookup_matched_url(
        query, best_processed_match, score, processed_choices_map
    )

    # EMERGENCY PENTATONIC CHECK
    if not matched_url and _is_penta_query(query):
        matched_url = _emergency_pentatonic_url(query)

    print("[DM_TRACE] Preparing JSON response.")
    return JsonResponse(
        {
            "debug": {
                "query": query,
                "normalized_query": normalized_query,
                "processed_queries": processed_queries,
                "best_processed_query": best_processed_query,
                "total_potential_targets": len(all_items),
                "unique_processed_keys": len(processed_choices_list),
                "scorer_used": getattr(scorer_to_use, "__name__", str(scorer_to_use)),
                "min_score_threshold": MIN_SCORE_THRESHOLD,
                "best_match_key": best_match_original_key
                if best_match_original_key
                else best_processed_match,
                "best_match_score": score,
                "matched_url": matched_url,
            }
        }
    )


def _match_query(query: str) -> JsonResponse:
    """Run the full matching pipeline for a non-empty query."""
    # Extract root note BEFORE normalization
    root_pk = _trace_query_root(query)

    # Normalize the query using our expanded normalize_search_term function
    normalized_query = normalize_search_term(query)
    print(f"[DM_TRACE] Normalized query: '{normalized_query}'")

    all_items = _build_items(root_pk)

    if not all_items:
        print("[DM_TRACE] No items available for searching.")
        return JsonResponse(
            {"debug": {"matched_url": None, "message": "No searchable items found."}}
        )

    # 1. Check for exact match with normalized query first (before fuzzy matching)
    exact_match = _find_exact_match(all_items, normalized_query)
    if exact_match:
        return _exact_match_response(query, normalized_query, exact_match, len(all_items))

    # 2. HARDCODED FIX: Special direct handler for Minor Pentatonic scale
    if "minor" in query.lower() and ("penat" in query.lower() or "penta" in query.lower()):
        response = _minor_pentatonic_special(query, normalized_query, all_items)
        if response is not None:
            return response

    # 3. Fuzzy matching
    return _fuzzy_match(query, normalized_query, all_items)


def direct_match(request: HttpRequest) -> JsonResponse:
    """API endpoint resolving a query to a single fretboard URL (debug JSON)."""
    query = request.GET.get("q", "").strip()
    print("[DM_TRACE] --- direct_match called ---")
    print(f"[DM_TRACE] Query: '{query}'")

    # DIRECT HACK FOR PENTATONIC
    # Check immediately if this is a pentatonic query with a typo
    if _is_pentatonic_typo_query(query):
        try:
            response = _pentatonic_override_response(query)
            if response is not None:
                return response
        except Exception as e:
            print(f"[DM_TRACE] Error in direct pentatonic override: {str(e)}")
            # Continue with regular matching if the override fails

    if not query:
        return JsonResponse({"error": "Query parameter is required."}, status=400)

    try:
        return _match_query(query)
    except Exception as e:
        print(f"[DM_TRACE] !!! EXCEPTION CAUGHT: {e}")
        logger.error(f"Error in direct_match for query '{query}': {e}", exc_info=True)
        return JsonResponse(
            {"error": "An internal server error occurred.", "details": str(e)}, status=500
        )
