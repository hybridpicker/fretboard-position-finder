"""Tests for the search endpoints (autocomplete, direct match) with the real music fixture."""
from unittest import mock
from urllib.parse import parse_qs, urlparse

import pytest
from django.urls import NoReverseMatch, reverse

from api.views_search import normalize_search_term
from positionfinder.models import Notes, Root
from positionfinder.models_chords import ChordNotes

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("music_data")]

AUTOCOMPLETE = "api:search_autocomplete"
DIRECT = "api:search_direct_match"


def params(url):
    """Query parameters of a fretboard url as a flat dict of strings."""
    parsed = urlparse(url)
    assert parsed.path == "/"
    return {k: v[0] for k, v in parse_qs(parsed.query).items()}


def debug(response):
    return response.json()["debug"]


# --------------------------------------------------------------------- normalize_search_term
class TestNormalizeSearchTerm:
    @pytest.mark.parametrize(
        "term,expected",
        [
            ("G7", "G Dominant 7"),
            ("g7", "G Dominant 7"),
            ("F#7", "F# Dominant 7"),
            ("Cmaj7", "C Major 7"),
            ("  Cm7 ", "C Minor 7"),
            ("cmin7", "C Minor 7"),
            ("c#min7", "C# Minor 7"),
            ("Am", "A Minor"),
            ("Dmin", "D Minor"),
            ("Cø", "C Minor 7b5"),
            ("Cm7b5", "C Minor 7b5"),
            ("C°", "C Diminished 7"),
            ("Cdim7", "C Diminished 7"),
            ("Caug", "C Augmented"),
        ],
    )
    def test_chord_shorthand(self, term, expected):
        assert normalize_search_term(term) == expected

    @pytest.mark.parametrize(
        "term,expected",
        [
            ("C Major 7", "C Major 7"),
            ("g dominant 7", "G Dominant 7"),
            ("a Minor", "A Minor"),
            ("c major", "C Major"),
            ("d diminished", "D Diminished"),
        ],
    )
    def test_spaced_names_are_capitalised(self, term, expected):
        assert normalize_search_term(term) == expected

    @pytest.mark.parametrize(
        "term,expected",
        [
            ("a minor pentatonic", "A Minor Pentatonic"),
            ("A Minor Pentatonic", "A Minor Pentatonic"),
            ("A major pentatonic", "A Major Pentatonic"),
            ("c major blues", "C Major Blues"),
            ("e minor pentatonic scale", "E Minor Pentatonic Scale"),
        ],
    )
    def test_scale_names(self, term, expected):
        assert normalize_search_term(term) == expected

    @pytest.mark.parametrize(
        "term,expected",
        [
            ("xyz", "xyz"),
            ("e blues", "e blues"),
            ("x #", "x sharp"),
            ("c Bb", "c bflat"),
            ("c maj", "c Major"),
        ],
    )
    def test_generic_replacements(self, term, expected):
        assert normalize_search_term(term) == expected

    @pytest.mark.parametrize("term", ["penatonic", "pennatonic", "panatonik"])
    def test_typo_in_pentatonic_is_corrected(self, term):
        # typo fixing only runs when the capitalised-name shortcut did not return earlier
        assert normalize_search_term(term) == "pentatonic"

    @pytest.mark.parametrize("term,expected", [("Bb7", "Bb Dominant 7"), ("Bbmaj7", "Bb Major 7")])
    @pytest.mark.xfail(strict=True, reason="BUG: the root is upper-cased as a whole, so flats become 'BB'")
    def test_flat_roots_keep_their_case(self, term, expected):
        assert normalize_search_term(term) == expected

    @pytest.mark.xfail(strict=True, reason="BUG: 'maj' -> 'Major' also rewrites 'major', giving 'Majoror'")
    def test_major_is_not_expanded_twice(self):
        assert "Majoror" not in normalize_search_term("ab major scale")


# --------------------------------------------------------------------- autocomplete
class TestAutocomplete:
    @pytest.mark.parametrize("query", [None, "", " ", "c", " a "])
    def test_short_query_returns_empty_results(self, api_get, query):
        data = {} if query is None else {"q": query}
        response = api_get(reverse(AUTOCOMPLETE), **data)
        assert response.status_code == 200
        assert response.json() == {"results": [], "debug": "Query too short"}

    def test_root_and_scale_name_produce_scale_urls(self, api_get):
        response = api_get(reverse(AUTOCOMPLETE), q="A Minor Pentatonic")
        results = response.json()["results"]
        assert [r["name"] for r in results] == ["Minor Pentatonic", "Pentatonic"]
        assert all(r["type"] == "scale" for r in results)
        # root 14 is A in the canonical root mapping; 49 / 4 are the Notes pks
        assert params(results[0]["url"]) == {
            "root": "14", "models_select": "1", "notes_options_select": "49", "position_select": "0",
        }
        assert params(results[1]["url"])["notes_options_select"] == "4"

    def test_query_is_stripped(self, api_get):
        padded = api_get(reverse(AUTOCOMPLETE), q="  A Minor Pentatonic  ").json()
        plain = api_get(reverse(AUTOCOMPLETE), q="A Minor Pentatonic").json()
        assert padded == plain

    def test_lowercase_root_is_recognised(self, api_get):
        results = api_get(reverse(AUTOCOMPLETE), q="e dorian").json()["results"]
        assert results[0]["name"] == "Dorian"
        assert params(results[0]["url"])["root"] == "7"

    def test_flat_root_uses_mapped_id(self, api_get):
        results = api_get(reverse(AUTOCOMPLETE), q="Eb Dorian").json()["results"]
        assert params(results[0]["url"])["root"] == "5"

    def test_unmapped_root_is_tolerated(self, api_get):
        response = api_get(reverse(AUTOCOMPLETE), q="E# Dorian")
        assert response.status_code == 200
        assert "results" in response.json()
        assert "error" not in response.json()

    def test_arpeggio_query(self, api_get):
        results = api_get(reverse(AUTOCOMPLETE), q="C Arpeggios").json()["results"]
        assert results == [
            {"name": "Arpeggios", "type": "arpeggio", "url": "/?models_select=2&notes_options_select=2"}
        ]

    def test_scale_without_root_uses_root_of_tonal_pitch(self, api_get):
        results = api_get(reverse(AUTOCOMPLETE), q="pentatonic").json()["results"]
        by_name = {r["name"]: r for r in results}
        assert set(by_name) == {"Pentatonic", "Minor Pentatonic"}
        # tonal_root 0 -> Root with pitch 0 -> C (pk 1)
        assert params(by_name["Minor Pentatonic"]["url"])["root"] == "1"

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: without a root in the query the scale url uses Notes.tonal_root as root id "
        "(negative for modes such as Dorian), which is not a valid Root primary key",
    )
    def test_mode_without_root_gets_valid_root_id(self, api_get):
        results = api_get(reverse(AUTOCOMPLETE), q="Dorian").json()["results"]
        dorian = next(r for r in results if r["name"] == "Dorian")
        assert Root.objects.filter(pk=int(params(dorian["url"])["root"])).exists()

    def test_chord_suggestion_points_to_chord_notes(self, api_get):
        results = api_get(reverse(AUTOCOMPLETE), q="Cmaj7").json()["results"]
        assert results
        first = results[0]
        assert first["type"] == "chord"
        assert first["name"] == "C Major 7"
        query = params(first["url"])
        assert query["models_select"] == "3"
        assert ChordNotes.objects.get(pk=query["notes_options_select"]).chord_name == "Major 7"

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: identical suggestions are repeated (match lookup always uses the first index "
        "of the normalised name), e.g. 'C Major 7' is returned ten times",
    )
    def test_results_contain_no_duplicates(self, api_get):
        results = api_get(reverse(AUTOCOMPLETE), q="Cmaj7").json()["results"]
        pairs = [(r["name"], r["url"]) for r in results]
        assert len(pairs) == len(set(pairs))

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: chord suggestions ignore the root typed by the user ('G7' -> 'C Dominant 7') "
        "because the display name is built from ChordNotes.tonal_root",
    )
    def test_chord_suggestion_keeps_requested_root(self, api_get):
        results = api_get(reverse(AUTOCOMPLETE), q="G7").json()["results"]
        assert results[0]["name"] == "G Dominant 7"

    def test_pentatonic_query_suggests_no_chords(self, api_get):
        results = api_get(reverse(AUTOCOMPLETE), q="A Minor Pentatonic").json()["results"]
        assert {r["type"] for r in results} == {"scale"}

    def test_gibberish_has_no_results(self, api_get):
        assert api_get(reverse(AUTOCOMPLETE), q="xyzzyq").json() == {"results": []}

    def test_result_limit_is_ten(self, api_get):
        assert len(api_get(reverse(AUTOCOMPLETE), q="Cmaj7").json()["results"]) <= 10

    def test_unreversible_fretboard_url_falls_back_to_root_path(self, api_get):
        with mock.patch("api.views_search.reverse", side_effect=NoReverseMatch("nope")):
            results = api_get(reverse(AUTOCOMPLETE), q="C Arpeggios").json()["results"]
        assert results[0]["url"] == "/?models_select=2&notes_options_select=2"

    def test_internal_error_is_reported_in_json(self, api_get):
        with mock.patch("api.views_search.parse_query", side_effect=ValueError("kaputt")):
            response = api_get(reverse(AUTOCOMPLETE), q="C Major")
        assert response.status_code == 200
        assert response.json() == {"results": [], "error": "kaputt"}


# --------------------------------------------------------------------- direct match
class TestDirectMatchBasics:
    @pytest.mark.parametrize("query", [None, "", "   "])
    def test_missing_query_is_400(self, api_get, query):
        data = {} if query is None else {"q": query}
        response = api_get(reverse(DIRECT), **data)
        assert response.status_code == 400
        assert response.json() == {"error": "Query parameter is required."}

    @pytest.mark.parametrize(
        "query,root,models,chord_name",
        [
            ("G7", "11", "3", "Dominant 7"),
            ("G Dominant 7", "11", "3", "Dominant 7"),
            ("C Major 7", "1", "3", "Major 7"),
            ("Gmaj7", "11", "3", "Major 7"),
            ("Am", "14", "3", "Minor"),
            ("Bb Minor 7", "15", "3", "Minor 7"),
            ("F#7", "10", "3", "Dominant 7"),
        ],
    )
    def test_exact_chord_match(self, api_get, query, root, models, chord_name):
        info = debug(api_get(reverse(DIRECT), q=query))
        assert info["match_method"] == "exact_match"
        assert info["best_match_score"] == 100
        assert info["query"] == query
        target = params(info["matched_url"])
        assert target["root"] == root
        assert target["models_select"] == models
        assert target["position_select"] == "0"
        assert ChordNotes.objects.get(pk=target["notes_options_select"]).chord_name == chord_name

    def test_exact_arpeggio_match(self, api_get):
        info = debug(api_get(reverse(DIRECT), q="D Arpeggios"))
        assert info["match_method"] == "exact_match"
        assert info["best_match_key"] == "D Arpeggios"
        assert params(info["matched_url"]) == {
            "root": "4", "models_select": "2", "notes_options_select": "2", "position_select": "0",
        }

    def test_exact_scale_match_is_case_insensitive(self, api_get):
        info = debug(api_get(reverse(DIRECT), q="d SCALES"))
        assert info["match_method"] == "exact_match"
        assert params(info["matched_url"])["models_select"] == "1"

    def test_debug_block_is_complete_for_fuzzy_matches(self, api_get):
        info = debug(api_get(reverse(DIRECT), q="xyzzy"))
        assert set(info) == {
            "query", "normalized_query", "processed_queries", "best_processed_query",
            "total_potential_targets", "unique_processed_keys", "scorer_used",
            "min_score_threshold", "best_match_key", "best_match_score", "matched_url",
        }
        assert info["scorer_used"] == "token_set_ratio"
        assert info["min_score_threshold"] == 80
        assert info["total_potential_targets"] == 17 * (1 + 1 + ChordNotes.objects.count())

    def test_unmatched_query_has_no_url(self, api_get):
        info = debug(api_get(reverse(DIRECT), q="xyzzy"))
        assert info["matched_url"] is None
        assert info["best_match_key"] is None
        assert info["best_match_score"] < 80

    def test_weak_match_below_threshold_is_rejected(self, api_get):
        info = debug(api_get(reverse(DIRECT), q="C blues"))
        assert info["matched_url"] is None
        assert 0 < info["best_match_score"] < 80

    def test_pentatonic_typo_without_minor_uses_emergency_lookup(self, api_get):
        info = debug(api_get(reverse(DIRECT), q="C Pentatonic"))
        assert info["scorer_used"] == "custom_pentatonic_scorer"
        assert params(info["matched_url"]) == {
            "root": "1", "models_select": "1", "notes_options_select": "49", "position_select": "0",
        }

    def test_internal_error_returns_500(self, api_get):
        with mock.patch.object(Root.objects, "all", side_effect=RuntimeError("kaputt")):
            response = api_get(reverse(DIRECT), q="C Major")
        assert response.status_code == 500
        assert response.json() == {"error": "An internal server error occurred.", "details": "kaputt"}


class TestDirectMatchPentatonicShortcuts:
    @pytest.mark.parametrize(
        "query,root",
        [
            ("A minor pentatonic", "14"),
            ("a MINOR Pentatonic", "14"),
            ("E min pentatonic", "7"),
            ("Eb minor penatonic", "5"),
            ("F# minor penat", "10"),
            ("g minor pentatonic scale", "11"),
        ],
    )
    def test_override_returns_minor_pentatonic_url(self, api_get, query, root):
        data = api_get(reverse(DIRECT), q=query).json()
        assert data["url"] == data["debug"]["matched_url"]
        assert params(data["url"]) == {
            "root": root, "models_select": "1", "notes_options_select": "49", "position_select": "0",
        }

    def test_override_prefers_the_minor_pentatonic_note_over_id_49(self, api_get):
        # a note with a different primary key that is named like the scale wins over the literal 49
        other = Notes.objects.get(pk=49)
        other.note_name = "Renamed"
        other.save()
        Notes.objects.create(pk=990_001, category=other.category, note_name="Minor Pentatonic Alt")
        data = api_get(reverse(DIRECT), q="A minor pentatonic").json()
        assert params(data["url"])["notes_options_select"] == "990001"

    def test_override_falls_back_to_id_49_without_matching_note(self, api_get):
        Notes.objects.filter(pk=49).update(note_name="Renamed")
        data = api_get(reverse(DIRECT), q="A minor pentatonic").json()
        assert params(data["url"])["notes_options_select"] == "49"

    def test_override_falls_back_to_id_49_when_lookup_fails(self, api_get):
        with mock.patch.object(Notes.objects, "filter", side_effect=RuntimeError("db")):
            data = api_get(reverse(DIRECT), q="A minor pentatonic").json()
        assert params(data["url"])["notes_options_select"] == "49"

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: roots such as 'E#' or 'Fb' have no mapped id, so the shortcut builds 'root=None'",
    )
    def test_override_with_unmapped_root_does_not_emit_none(self, api_get):
        data = api_get(reverse(DIRECT), q="E# minor pentatonic").json()
        assert "root=None" not in data["url"]

    def test_override_failure_continues_with_regular_matching(self, api_get):
        calls = []
        real_reverse = reverse

        def flaky(*args, **kwargs):
            calls.append(1)
            if len(calls) == 1:
                raise NoReverseMatch("first call fails")
            return real_reverse(*args, **kwargs)

        with mock.patch("api.views_search.reverse", side_effect=flaky):
            data = api_get(reverse(DIRECT), q="A minor pentatonic").json()
        assert data["debug"]["match_method"] == "direct_pentatonic_hardcoded"
        assert params(data["debug"]["matched_url"])["notes_options_select"] == "49"

    def test_query_without_root_continues_after_override(self, api_get):
        info = debug(api_get(reverse(DIRECT), q="minor pentatonic"))
        # no root -> no shortcut applies, regular fuzzy search with the pentatonic scorer
        assert info["scorer_used"] == "custom_pentatonic_scorer"
        assert "match_method" not in info

    @pytest.mark.parametrize("query,root", [("A minor penta", "14"), ("e minor penta", "7"), ("Bb minor penta", "15")])
    def test_hardcoded_fix_for_short_pentatonic_names(self, api_get, query, root):
        info = debug(api_get(reverse(DIRECT), q=query))
        assert info["match_method"] == "direct_pentatonic_hardcoded"
        assert info["best_match_score"] == 100
        assert info["best_match_key"].endswith("Minor Pentatonic Scale")
        target = params(info["matched_url"])
        assert target["root"] == root
        assert target["notes_options_select"] == "49"

    def test_hardcoded_fix_uses_named_note_when_id_49_is_missing(self, api_get):
        Notes.objects.filter(pk=49).delete()
        alt = Notes.objects.create(pk=990_002, category_id=1, note_name="Minor Pentatonic")
        info = debug(api_get(reverse(DIRECT), q="A minor penta"))
        assert params(info["matched_url"])["notes_options_select"] == str(alt.pk)

    def test_hardcoded_fix_keeps_49_when_it_cannot_be_verified(self, api_get):
        real_filter = Notes.objects.filter

        def flaky(*args, **kwargs):
            if kwargs.get("pk") == 49:
                raise RuntimeError("db")
            return real_filter(*args, **kwargs)

        with mock.patch.object(Notes.objects, "filter", side_effect=flaky):
            info = debug(api_get(reverse(DIRECT), q="A minor penta"))
        assert params(info["matched_url"])["notes_options_select"] == "49"

    def test_diagnostic_failures_do_not_stop_the_hardcoded_fix(self, api_get):
        from positionfinder.models import NotesCategory

        real_cat, real_notes = NotesCategory.objects.filter, Notes.objects.filter

        def failing(real):
            def _filter(*args, **kwargs):
                if "pentatonic" in kwargs.values():
                    raise RuntimeError("db")
                return real(*args, **kwargs)

            return _filter

        with mock.patch.object(NotesCategory.objects, "filter", side_effect=failing(real_cat)), \
                mock.patch.object(Notes.objects, "filter", side_effect=failing(real_notes)):
            info = debug(api_get(reverse(DIRECT), q="A minor penta"))
        assert info["match_method"] == "direct_pentatonic_hardcoded"
        assert params(info["matched_url"])["notes_options_select"] == "49"

    def test_unknown_root_object_falls_through_to_fuzzy_matching(self, api_get):
        Root.objects.filter(name="A").delete()
        info = debug(api_get(reverse(DIRECT), q="A minor penta"))
        assert info.get("match_method") != "direct_pentatonic_hardcoded"
        assert info["scorer_used"] == "custom_pentatonic_scorer"

    def test_root_lookup_error_falls_through(self, api_get):
        real_filter = Root.objects.filter

        def flaky(*args, **kwargs):
            if "name__iexact" in kwargs:
                raise RuntimeError("db")
            return real_filter(*args, **kwargs)

        with mock.patch.object(Root.objects, "filter", side_effect=flaky):
            info = debug(api_get(reverse(DIRECT), q="A minor penta"))
        assert info.get("match_method") != "direct_pentatonic_hardcoded"
        assert info["scorer_used"] == "custom_pentatonic_scorer"
