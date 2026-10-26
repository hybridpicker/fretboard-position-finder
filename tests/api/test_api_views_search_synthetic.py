"""Search endpoints against small synthetic databases (branches the full fixture cannot reach)."""

from unittest import mock
from urllib.parse import parse_qs, urlparse

import pytest
from django.urls import reverse

from api.views_search import normalize_search_term
from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.models_chords import ChordNotes

pytestmark = pytest.mark.django_db

AUTOCOMPLETE = "api:search_autocomplete"
DIRECT = "api:search_direct_match"


def params(url):
    parsed = urlparse(url)
    assert parsed.path == "/"
    return {k: v[0] for k, v in parse_qs(parsed.query).items()}


def debug(response):
    return response.json()["debug"]


def root(name, pitch, pk):
    return Root.objects.create(pk=pk, name=name, pitch=pitch)


def category(name, pk):
    return NotesCategory.objects.create(pk=pk, category_name=name)


def chord(cat, name, pk, tonal_root=0):
    return ChordNotes.objects.create(
        pk=pk, category=cat, type_name="T", chord_name=name, range="e - g", tonal_root=tonal_root
    )


def reject_kwarg(manager, value):
    """Patch manager.filter so that any call containing ``value`` as a keyword value fails."""
    real = manager.filter

    def _filter(*args, **kwargs):
        if value in kwargs.values():
            raise RuntimeError("db")
        return real(*args, **kwargs)

    return mock.patch.object(manager, "filter", side_effect=_filter)


class TestNormalizeWithOtherWhitespace:
    """Roots the space shortcut does not capitalise fall through to the scale pattern."""

    def test_lowercase_sharp_root_reaches_scale_pattern(self):
        # 'a#' is not recognised as a root by the space shortcut, so the scale pattern runs
        assert normalize_search_term("a# minor pentatonic") == "A# Minor Pentatonic"

    def test_scale_pattern_returns_original_for_other_scales(self):
        assert normalize_search_term("c# major blues") == "c# major blues"


class TestAutocompleteSynthetic:
    def test_empty_database_has_no_results(self, api_get):
        assert api_get(reverse(AUTOCOMPLETE), q="C Major").json() == {"results": []}

    def test_chord_without_matching_root_uses_chord_name_only(self, api_get):
        c = chord(category("Chords", 3), "Dominant 7", 500, tonal_root=3)  # no Root with pitch 3
        results = api_get(reverse(AUTOCOMPLETE), q="Dominant 7").json()["results"]
        assert len(results) == 1
        assert results[0]["name"].lower() == "dominant 7"
        assert results[0]["type"] == "chord"
        assert results[0]["url"] == f"/?models_select=3&notes_options_select={c.pk}"

    def test_root_less_major_chord_keeps_its_name(self, api_get):
        chord(category("Chords", 3), "Major 7", 500, tonal_root=3)
        results = api_get(reverse(AUTOCOMPLETE), q="Major 7").json()["results"]
        assert results[0]["name"] == "Major 7"

    def test_chord_name_is_prefixed_with_root_of_tonal_pitch(self, api_get):
        root("C", 0, 1)
        chord(category("Chords", 3), "Major 7", 500)
        results = api_get(reverse(AUTOCOMPLETE), q="C Major 7").json()["results"]
        assert results[0]["name"] == "C Major 7"

    def test_scale_with_unknown_tonal_root_keeps_raw_value(self, api_get):
        scales = category("Scales", 1)
        Notes.objects.create(pk=600, category=scales, note_name="Lydian", tonal_root=-5)
        results = api_get(reverse(AUTOCOMPLETE), q="Lydian").json()["results"]
        assert results[0]["name"] == "Lydian"
        assert params(results[0]["url"])["root"] == "-5"

    def test_scale_uses_root_matching_tonal_pitch(self, api_get):
        root("C", 0, 1)
        scales = category("Scales", 1)
        Notes.objects.create(pk=600, category=scales, note_name="Dorian", tonal_root=0)
        results = api_get(reverse(AUTOCOMPLETE), q="Dorian").json()["results"]
        assert params(results[0]["url"])["root"] == "1"

    def test_intent_all_offers_every_type_except_pentatonic_chords(self, api_get):
        scales = category("Scales", 1)
        category("Arpeggios", 2)
        Notes.objects.create(pk=600, category=scales, note_name="Pentatonic")
        chord(category("Chords", 3), "Pentatonic Chord", 500)
        with mock.patch(
            "api.views_search.parse_query", return_value=("A", "all", "minor", "", "basic position")
        ):
            results = api_get(reverse(AUTOCOMPLETE), q="Pentatonic").json()["results"]
        assert {r["type"] for r in results} == {"scale", "chord"}
        with mock.patch(
            "api.views_search.parse_query",
            return_value=("A", "all", "minor pentatonic", "", "basic position"),
        ):
            results = api_get(reverse(AUTOCOMPLETE), q="Pentatonic").json()["results"]
        assert {r["type"] for r in results} == {"scale"}


class TestDirectMatchSynthetic:
    def test_empty_database_reports_no_items(self, api_get):
        response = api_get(reverse(DIRECT), q="C Major")
        assert response.status_code == 200
        assert response.json() == {
            "debug": {"matched_url": None, "message": "No searchable items found."}
        }

    def test_override_without_any_notes_uses_fallback_id(self, api_get):
        data = api_get(reverse(DIRECT), q="G minor pentatonic").json()
        assert params(data["url"]) == {
            "root": "11",
            "models_select": "1",
            "notes_options_select": "49",
            "position_select": "0",
        }

    def test_override_picks_minor_pentatonic_note_by_name(self, api_get):
        scales = category("Scales", 1)
        Notes.objects.create(pk=601, category=scales, note_name="Major Pentatonic")
        Notes.objects.create(pk=602, category=scales, note_name="Minor Pentatonic")
        data = api_get(reverse(DIRECT), q="G minor pentatonic").json()
        assert params(data["url"])["notes_options_select"] == "602"

    def test_hardcoded_fix_without_any_pentatonic_note_keeps_id_49(self, api_get):
        root("A", 9, 14)
        category("Scales", 1)
        info = debug(api_get(reverse(DIRECT), q="A minor penta"))
        assert info["match_method"] == "direct_pentatonic_hardcoded"
        assert params(info["matched_url"]) == {
            "root": "14",
            "models_select": "1",
            "notes_options_select": "49",
            "position_select": "0",
        }

    def test_hardcoded_fix_prefers_existing_id_49(self, api_get):
        root("A", 9, 14)
        scales = category("Scales", 1)
        Notes.objects.create(pk=49, category=scales, note_name="Whatever")
        info = debug(api_get(reverse(DIRECT), q="A minor penta"))
        assert params(info["matched_url"])["notes_options_select"] == "49"

    def test_pentatonic_special_match_when_hardcoded_fix_fails(self, api_get):
        root("A", 9, 14)
        category("Minor Pentatonic Scale", 7)
        with reject_kwarg(Root.objects, "A"):
            info = debug(api_get(reverse(DIRECT), q="A minor penta"))
        assert info["match_method"] == "pentatonic_special_match"
        assert info["best_match_key"] == "A Minor Pentatonic Scale"
        assert info["best_match_score"] == 95
        assert params(info["matched_url"]) == {
            "root": "14",
            "models_select": "1",
            "notes_options_select": "7",
            "position_select": "0",
        }

    def test_special_match_requires_matching_root(self, api_get):
        root("C", 0, 1)
        category("Minor Pentatonic Scale", 7)
        with reject_kwarg(Root.objects, "A"):
            info = debug(api_get(reverse(DIRECT), q="A minor penta"))
        assert info.get("match_method") != "pentatonic_special_match"

    def test_fuzzy_pentatonic_match_prefers_pentatonic_scale(self, api_get):
        root("A", 9, 14)
        category("Minor Pentatonic Scale", 7)
        info = debug(api_get(reverse(DIRECT), q="A pentatonic"))
        assert info["scorer_used"] == "custom_pentatonic_scorer"
        assert info["best_match_score"] >= 80
        assert params(info["matched_url"]) == {
            "root": "14",
            "models_select": "1",
            "notes_options_select": "7",
            "position_select": "0",
        }

    def test_duplicate_scale_names_keep_first_item(self, api_get):
        root("A", 9, 14)
        category("Minor Pentatonic Scale", 7)
        category("Minor Pentatonic Scale", 8)
        info = debug(api_get(reverse(DIRECT), q="A pentatonic"))
        assert info["unique_processed_keys"] == 1
        assert params(info["matched_url"])["notes_options_select"] == "7"

    def test_typo_query_matches_item_containing_pentatonic(self, api_get):
        root("A", 9, 14)
        chord(category("Chords", 3), "Pentatonic", 500)
        info = debug(api_get(reverse(DIRECT), q="A penatonic chord"))
        assert info["unique_processed_keys"] == 1
        assert info["best_match_score"] >= 80
        assert info["best_match_key"] == "A Pentatonic"

    def test_typo_in_pentatonic_is_normalised_to_exact_match(self, api_get):
        root("A", 9, 14)
        chord(category("Chords", 3), "Pentatonic", 500)
        info = debug(api_get(reverse(DIRECT), q="A penatonic"))
        assert info["match_method"] == "exact_match"
        assert info["best_match_key"] == "A Pentatonic"

    def test_pentatonic_query_matching_chord_is_corrected_to_scale(self, api_get):
        root("A", 9, 14)
        chords = category("Chords", 3)
        chord(chords, "Pentatonic Chord", 500)
        Notes.objects.create(pk=602, category=chords, note_name="Minor Pentatonic")
        info = debug(api_get(reverse(DIRECT), q="A pentatonic chor"))
        assert params(info["matched_url"]) == {
            "root": "14",
            "models_select": "1",
            "notes_options_select": "602",
            "position_select": "0",
        }

    def test_pentatonic_chord_match_is_kept_without_a_scale_to_switch_to(self, api_get):
        root("A", 9, 14)
        c = chord(category("Chords", 3), "Pentatonic Chord", 500)
        info = debug(api_get(reverse(DIRECT), q="A pentatonic chor"))
        assert params(info["matched_url"])["models_select"] == "3"
        assert params(info["matched_url"])["notes_options_select"] == str(c.pk)

    def test_scale_correction_failure_keeps_chord_match(self, api_get):
        root("A", 9, 14)
        chords = category("Chords", 3)
        chord(chords, "Pentatonic Chord", 500)
        Notes.objects.create(pk=602, category=chords, note_name="Minor Pentatonic")
        with reject_kwarg(Notes.objects, "minor pentatonic"):
            info = debug(api_get(reverse(DIRECT), q="A pentatonic chor"))
        assert params(info["matched_url"])["models_select"] == "3"


class TestEmergencyPentatonic:
    """Low scoring pentatonic queries fall back to a hand-built minor pentatonic url."""

    @pytest.fixture(autouse=True)
    def world(self):
        root("A", 9, 14)
        category("Chords", 3)
        category("Scales", 1)  # gives the search something to (poorly) match against

    def test_builds_url_from_named_note(self, api_get):
        Notes.objects.create(pk=602, category_id=3, note_name="Minor Pentatonic")
        info = debug(api_get(reverse(DIRECT), q="Q penta"))
        assert info["matched_url"] is None  # no root -> nothing to build
        info = debug(api_get(reverse(DIRECT), q="B penta"))
        assert params(info["matched_url"]) == {
            "root": "17",
            "models_select": "1",
            "notes_options_select": "602",
            "position_select": "0",
        }

    def test_without_note_there_is_no_url(self, api_get):
        info = debug(api_get(reverse(DIRECT), q="B penta"))
        assert info["matched_url"] is None

    def test_existing_id_49_is_only_logged(self, api_get):
        Notes.objects.create(pk=49, category_id=3, note_name="Something")
        info = debug(api_get(reverse(DIRECT), q="B penta"))
        assert info["matched_url"] is None

    def test_lookup_failure_is_swallowed(self, api_get):
        with reject_kwarg(Notes.objects, "pentatonic"):
            response = api_get(reverse(DIRECT), q="B penta")
        assert response.status_code == 200
        assert debug(response)["matched_url"] is None

    def test_unmapped_root_does_not_emit_none(self, api_get):
        Notes.objects.create(pk=602, category_id=3, note_name="Minor Pentatonic")
        info = debug(api_get(reverse(DIRECT), q="E# penta"))
        assert "root=None" not in (info["matched_url"] or "")

    def test_unmapped_root_in_regular_query_is_tolerated(self, api_get):
        info = debug(api_get(reverse(DIRECT), q="E# Scales"))
        assert "matched_url" in info
