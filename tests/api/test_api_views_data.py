"""Tests for the database-backed API views using the real studio music fixture."""
import itertools
from unittest import mock

import pytest
from django.urls import reverse

from positionfinder.models import Notes, NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.positions import NotesPosition

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("music_data")]

DEFAULT_FIVE = [0, 1, 2, 3, 4, 5]


def orders(response):
    return [p["position_order"] for p in response.json()["positions"]]


def inversions(response):
    return [p["inversion_order"] for p in response.json()["positions"]]


_pks = itertools.count(900_001)  # explicit keys: sequences are not advanced by the fixture


def make_chord(type_name="Zt", chord_name="Zc", rng="e - g", ordering=None, fourth=None):
    """Create a synthetic chord and drop the inversions ChordNotes.save() generates for it."""
    chord = ChordNotes.objects.create(
        pk=next(_pks),
        category=NotesCategory.objects.get(category_name="Chords"),
        type_name=type_name,
        chord_name=chord_name,
        range=rng,
        range_ordering=ordering,
        fourth_note=fourth,
    )
    ChordPosition.objects.filter(notes_name=chord).delete()
    return chord


def make_note(name, category="Scales"):
    return Notes.objects.create(
        pk=next(_pks), category=NotesCategory.objects.get(category_name=category), note_name=name
    )


# --------------------------------------------------------------------------- chord-names
class TestChordNames:
    url = "api:ajax_chord_names"

    def names(self, response):
        return [c["chord_name"] for c in response.json()["chord_names"]]

    def test_names_for_known_type_sorted(self, api_get):
        response = api_get(reverse(self.url), type_name="Triads")
        assert response.status_code == 200
        assert self.names(response) == ["Augmented", "Diminished", "Major", "Minor"]

    def test_seventh_chord_type(self, api_get):
        names = self.names(api_get(reverse(self.url), type_name="V1"))
        assert names == ["Dominant 7", "Major 7", "Minor 7", "Minor 7b5", "Minor7b5"]

    def test_no_duplicates_in_response(self, api_get):
        names = self.names(api_get(reverse(self.url), type_name="Spread Triads"))
        assert len(names) == len(set(names)) == 4

    def test_missing_type_uses_first_type_in_database(self, api_get):
        first = ChordNotes.objects.values_list("type_name", flat=True).distinct().first()
        expected = sorted(set(ChordNotes.objects.filter(type_name=first).values_list("chord_name", flat=True)))
        assert self.names(api_get(reverse(self.url))) == expected

    def test_unknown_type_returns_all_chord_names(self, api_get):
        names = self.names(api_get(reverse(self.url), type_name="NoSuchType"))
        assert names == [
            "Augmented", "Diminished", "Dominant 7", "Major", "Major 7",
            "Minor", "Minor 7", "Minor 7b5", "Minor7b5",
        ]

    def test_count_failure_falls_back_to_all_names(self, api_get):
        with mock.patch.object(ChordNotes.objects, "count", side_effect=RuntimeError("db")):
            response = api_get(reverse(self.url), type_name="Triads")
        assert response.status_code == 200
        names = self.names(response)
        assert {"Major", "Minor", "Dominant 7", "Major 7"} <= set(names)
        assert len(names) == len(set(names))

    def test_total_database_failure_returns_major_minor(self, api_get):
        with mock.patch.object(ChordNotes.objects, "count", side_effect=RuntimeError("db")), \
                mock.patch.object(ChordNotes.objects, "values_list", side_effect=RuntimeError("db")):
            response = api_get(reverse(self.url), type_name="Triads")
        assert response.json() == {"chord_names": [{"chord_name": "Major"}, {"chord_name": "Minor"}]}

    def test_first_type_lookup_failure_defaults_to_triads(self, api_get):
        # values_list fails for the first-type lookup and for everything afterwards
        with mock.patch.object(ChordNotes.objects, "values_list", side_effect=RuntimeError("db")), \
                mock.patch.object(ChordNotes.objects, "filter", side_effect=RuntimeError("db")):
            response = api_get(reverse(self.url))
        assert response.json() == {"chord_names": [{"chord_name": "Major"}, {"chord_name": "Minor"}]}

    def test_request_failure_falls_back_to_database_names(self, api_get, break_view_query_params):
        response = api_get(reverse(self.url), type_name="Triads")
        assert response.status_code == 200
        names = self.names(response)
        assert names and set(names) <= {"Major", "Minor", "Diminished", "Augmented", "Dominant 7",
                                        "Major 7", "Minor 7", "Minor 7b5", "Minor7b5"}


# --------------------------------------------------------------------------- chord-ranges
class TestChordRanges:
    url = "api:ajax_chord_ranges"

    def ranges(self, response):
        return [r["range"] for r in response.json()["ranges"]]

    def test_specific_type_and_chord_ordered_by_range_ordering(self, api_get):
        response = api_get(reverse(self.url), type_name="Triads", chord_name="Major")
        assert response.status_code == 200
        body = response.json()["ranges"]
        assert [r["range"] for r in body] == ["e - g", "a - b", "A - B", "b - d", "g - A", "d - E"]
        # ids are real ChordNotes primary keys
        assert all(ChordNotes.objects.filter(pk=r["id"], range=r["range"]).exists() for r in body)

    def test_six_string_default_drops_eight_string_ranges(self, api_get):
        response = api_get(reverse(self.url), type_name="V1", chord_name="Major 7")
        assert self.ranges(response) == ["e - d", "b - A", "g - E"]

    def test_eight_string_query_param_keeps_all_ranges(self, api_get):
        response = api_get(reverse(self.url), type_name="V1", chord_name="Major 7", string_mode="eight-string")
        assert self.ranges(response) == ["e - d", "highA - g", "b - A", "g - E", "d - lowB"]

    def test_eight_string_cookie(self, api_get, client):
        client.cookies["stringConfig"] = "eight-string"
        response = api_get(reverse(self.url), type_name="V1", chord_name="Major 7")
        assert "highA - g" in self.ranges(response)

    def test_query_param_wins_over_cookie(self, api_get, client):
        client.cookies["stringConfig"] = "eight-string"
        response = api_get(reverse(self.url), type_name="V1", chord_name="Major 7", string_mode="six-string")
        assert "highA - g" not in self.ranges(response)

    def test_invalid_mode_is_treated_as_six_string(self, api_get):
        response = api_get(reverse(self.url), type_name="V1", chord_name="Major 7", string_mode="bogus")
        assert self.ranges(response) == ["e - d", "b - A", "g - E"]

    def test_missing_params_use_first_chord_of_database(self, api_get):
        first = ChordNotes.objects.first()
        expected = list(
            ChordNotes.objects.filter(type_name=first.type_name, chord_name=first.chord_name)
            .order_by("range_ordering")
            .values_list("range", flat=True)
        )
        response = api_get(reverse(self.url))
        assert response.status_code == 200
        assert self.ranges(response) == expected

    def test_only_chord_name_given_fills_type_from_database(self, api_get):
        response = api_get(reverse(self.url), chord_name="Major")
        assert response.status_code == 200
        assert response.json()["ranges"]

    def test_only_type_name_given_fills_chord_from_database(self, api_get):
        response = api_get(reverse(self.url), type_name="Triads")
        assert response.status_code == 200
        assert response.json()["ranges"]

    def test_limit_of_eight_ranges(self, api_get):
        for i in range(10):
            make_chord("Zlim", "Zname", f"r{i}", ordering=i)
        response = api_get(reverse(self.url), type_name="Zlim", chord_name="Zname")
        assert self.ranges(response) == [f"r{i}" for i in range(8)]

    def test_duplicate_range_names_are_collapsed(self, api_get):
        make_chord("Zdup", "Zname", "same", ordering=1)
        make_chord("Zdup", "Zname", "same", ordering=2)
        make_chord("Zdup", "Zname", "other", ordering=3)
        assert self.ranges(api_get(reverse(self.url), type_name="Zdup", chord_name="Zname")) == ["same", "other"]

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: fallback queries use .distinct('range') with order_by('range_ordering'); "
        "PostgreSQL rejects DISTINCT ON that does not match ORDER BY, so the except branch "
        "silently returns the hard-coded ranges instead of the database ranges",
    )
    def test_unknown_type_falls_back_to_ranges_of_chord_name(self, api_get):
        response = api_get(reverse(self.url), type_name="NoSuchType", chord_name="Major 7")
        body = response.json()["ranges"]
        assert body
        assert all(isinstance(r["id"], int) for r in body)  # real database rows, not the hard-coded defaults

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: same DISTINCT ON / ORDER BY mismatch in the type-wide fallback query",
    )
    def test_unknown_chord_falls_back_to_ranges_of_type(self, api_get):
        response = api_get(reverse(self.url), type_name="V1", chord_name="NoSuchChord")
        body = response.json()["ranges"]
        assert body
        assert all(isinstance(r["id"], int) for r in body)

    def test_unknown_type_and_chord_still_returns_usable_ranges(self, api_get):
        response = api_get(reverse(self.url), type_name="NoSuchType", chord_name="NoSuchChord")
        assert response.status_code == 200
        body = response.json()["ranges"]
        assert body
        assert all({"id", "range"} <= set(r) for r in body)

    def test_database_failure_returns_standard_ranges(self, api_get):
        with mock.patch("api.views.ChordNotes") as chord_notes:
            chord_notes.objects.filter.side_effect = RuntimeError("db")
            response = api_get(reverse(self.url), type_name="Triads", chord_name="Major")
        assert response.json()["ranges"] == [
            {"id": "1", "range": "e - g"},
            {"id": "2", "range": "b - d"},
            {"id": "3", "range": "g - A"},
            {"id": "4", "range": "d - E"},
            {"id": "5", "range": "A - B"},
        ]

    def test_missing_params_and_first_lookup_failure_is_400(self, api_get):
        with mock.patch("api.views.ChordNotes") as chord_notes:
            chord_notes.objects.first.side_effect = RuntimeError("db")
            response = api_get(reverse(self.url))
        assert response.status_code == 400
        assert response.json() == {"error": "Missing required parameters: type_name, chord_name"}

    def test_empty_database_uses_string_range_choices(self, api_get):
        # a MagicMock iterates as an empty sequence, so every list(...) call is []
        with mock.patch("api.views.ChordNotes", mock.MagicMock()):
            response = api_get(reverse(self.url), type_name="X", chord_name="Y", string_mode="eight-string")
        from positionfinder.string_range_choices import STRING_RANGE_CHOICES

        expected = [{"id": str(i + 1), "range": c[0]} for i, c in enumerate(STRING_RANGE_CHOICES)][:6]
        assert response.json()["ranges"] == expected

    def test_empty_database_six_string_filters_default_ranges(self, api_get):
        with mock.patch("api.views.ChordNotes", mock.MagicMock()):
            response = api_get(reverse(self.url), type_name="X", chord_name="Y")
        ranges = self.ranges(response)
        assert ranges
        assert not any("highA" in r or "lowB" in r for r in ranges)

    def test_broken_range_choices_use_hardcoded_ranges(self, api_get):
        with mock.patch("api.views.ChordNotes", mock.MagicMock()), \
                mock.patch("positionfinder.string_range_choices.STRING_RANGE_CHOICES", 5):
            response = api_get(reverse(self.url), type_name="X", chord_name="Y", string_mode="eight-string")
        assert self.ranges(response) == ["e - g", "b - d", "g - A", "d - E", "A - B", "highA - e"]

    def test_everything_filtered_out_leaves_single_range(self, api_get):
        # only 8-string ranges exist and we are in 6-string mode
        chord_notes = mock.MagicMock()
        rows = [{"id": 1, "range": "highA - e"}, {"id": 2, "range": "e - lowB"}]
        chord_notes.objects.filter.return_value.order_by.return_value.values.return_value = rows
        with mock.patch("api.views.ChordNotes", chord_notes):
            response = api_get(reverse(self.url), type_name="X", chord_name="Y")
        assert response.json() == {"ranges": [{"id": "1", "range": "e - g"}]}

    def test_unexpected_failure_returns_emergency_ranges_six_string(self, api_get):
        with mock.patch("builtins.print", side_effect=OSError("closed")):
            response = api_get(reverse(self.url), type_name="Triads", chord_name="Major")
        assert self.ranges(response) == ["e - g", "b - d", "g - A"]

    def test_unexpected_failure_returns_emergency_ranges_eight_string(self, api_get):
        with mock.patch("builtins.print", side_effect=OSError("closed")):
            response = api_get(reverse(self.url), type_name="Triads", chord_name="Major",
                               string_mode="eight-string")
        assert self.ranges(response) == ["e - g", "b - d", "g - A", "highA - e", "e - lowB"]


# --------------------------------------------------------------------------- chord-positions
class TestChordPositions:
    url = "api:ajax_chord_positions"

    def test_positions_for_triad(self, api_get):
        response = api_get(reverse(self.url), chord_notes_id="52")
        assert response.status_code == 200
        assert inversions(response) == ["Basic Position", "First Inversion", "Second Inversion"]

    def test_positions_for_seventh_chord_include_third_inversion(self, api_get):
        seventh = ChordNotes.objects.filter(fourth_note__isnull=False).first()
        assert inversions(api_get(reverse(self.url), chord_notes_id=str(seventh.pk))) == [
            "Basic Position", "First Inversion", "Second Inversion", "Third Inversion",
        ]

    def test_missing_id_uses_first_chord(self, api_get):
        first = ChordNotes.objects.first()
        expected = list(ChordPosition.objects.filter(notes_name=first).order_by("inversion_order")
                        .values_list("inversion_order", flat=True))
        assert inversions(api_get(reverse(self.url))) == expected

    def test_chord_without_positions_falls_back_to_other_triads(self, api_get):
        chord = make_chord()
        response = api_get(reverse(self.url), chord_notes_id=str(chord.pk))
        assert inversions(response) == ["Basic Position", "First Inversion", "Second Inversion"]

    def test_seventh_chord_without_positions_falls_back_to_other_sevenths(self, api_get):
        chord = make_chord(fourth=10)
        response = api_get(reverse(self.url), chord_notes_id=str(chord.pk))
        assert inversions(response) == [
            "Basic Position", "First Inversion", "Second Inversion", "Third Inversion",
        ]

    def test_unknown_id_falls_back_to_all_inversions(self, api_get):
        response = api_get(reverse(self.url), chord_notes_id="999999999")
        assert inversions(response) == [
            "Basic Position", "First Inversion", "Second Inversion", "Third Inversion",
        ]

    def test_non_numeric_id_falls_back_to_all_inversions(self, api_get):
        response = api_get(reverse(self.url), chord_notes_id="abc")
        assert response.status_code == 200
        assert len(inversions(response)) == 4

    def test_database_failure_uses_all_positions(self, api_get):
        with mock.patch("api.views.ChordPosition") as chord_position:
            chord_position.objects.filter.side_effect = RuntimeError("db")
            chord_position.objects.values.return_value.distinct.return_value.order_by.return_value = [
                {"inversion_order": "Basic Position"}
            ]
            response = api_get(reverse(self.url), chord_notes_id="52")
        assert response.json() == {"positions": [{"inversion_order": "Basic Position"}]}

    def test_database_failure_with_no_positions_uses_root_position(self, api_get):
        with mock.patch("api.views.ChordPosition") as chord_position:
            chord_position.objects.filter.side_effect = RuntimeError("db")
            chord_position.objects.values.return_value.distinct.return_value.order_by.return_value = []
            response = api_get(reverse(self.url), chord_notes_id="52")
        assert response.json() == {"positions": [{"inversion_order": "Root Position"}]}

    def test_total_database_failure_uses_root_position(self, api_get):
        with mock.patch("api.views.ChordPosition") as chord_position:
            chord_position.objects.filter.side_effect = RuntimeError("db")
            chord_position.objects.values.side_effect = RuntimeError("db")
            response = api_get(reverse(self.url), chord_notes_id="52")
        assert response.json() == {"positions": [{"inversion_order": "Root Position"}]}

    def test_first_chord_lookup_failure_is_400(self, api_get):
        with mock.patch("api.views.ChordNotes") as chord_notes:
            chord_notes.objects.first.side_effect = RuntimeError("db")
            response = api_get(reverse(self.url))
        assert response.status_code == 400
        assert response.json() == {"error": "Missing required parameter: chord_notes_id"}

    def test_request_failure_returns_first_three_positions(self, api_get, break_view_query_params):
        response = api_get(reverse(self.url), chord_notes_id="52")
        assert response.status_code == 200
        assert len(response.json()["positions"]) == 3

    def test_request_failure_and_database_failure_returns_root_position(self, api_get, break_view_query_params):
        with mock.patch("api.views.ChordPosition") as chord_position:
            chord_position.objects.values.side_effect = RuntimeError("db")
            response = api_get(reverse(self.url), chord_notes_id="52")
        assert response.json() == {"positions": [{"inversion_order": "Root Position"}]}

    def test_request_failure_with_no_positions_returns_root_position(self, api_get, break_view_query_params):
        with mock.patch("api.views.ChordPosition") as chord_position:
            chord_position.objects.values.return_value.distinct.return_value.__getitem__.return_value = []
            response = api_get(reverse(self.url), chord_notes_id="52")
        assert response.json() == {"positions": [{"inversion_order": "Root Position"}]}


# --------------------------------------------------------------------------- scale-positions
class TestScalePositions:
    url = "api:ajax_scale_positions"

    def test_missing_notes_id_is_400(self, api_get):
        response = api_get(reverse(self.url))
        assert response.status_code == 400
        assert response.json() == {"error": "Missing required parameter: notes_id"}

    def test_major_scale_has_seven_database_positions(self, api_get):
        assert orders(api_get(reverse(self.url), notes_id="1")) == [0, 1, 2, 3, 4, 5, 6]

    def test_minor_pentatonic_has_five_database_positions(self, api_get):
        assert orders(api_get(reverse(self.url), notes_id="49")) == DEFAULT_FIVE

    def test_positions_are_unique_and_sorted(self, api_get):
        values = orders(api_get(reverse(self.url), notes_id="5"))
        assert values == sorted(set(values))
        assert values[0] == 0

    def test_unknown_note_gets_default_positions(self, api_get):
        assert orders(api_get(reverse(self.url), notes_id="999999")) == DEFAULT_FIVE

    @pytest.mark.parametrize("value", ["abc", "1.5", "-"])
    def test_non_numeric_id_gets_default_positions(self, api_get, value):
        assert orders(api_get(reverse(self.url), notes_id=value)) == DEFAULT_FIVE

    def test_note_without_positions_borrows_from_similar_note(self, api_get):
        a = make_note("Zeta Scale")
        b = make_note("Zeta Scale")
        NotesPosition.objects.create(notes_name=b, position_order=1, position="1,2")
        NotesPosition.objects.create(notes_name=b, position_order=2, position="3,4")
        assert orders(api_get(reverse(self.url), notes_id=str(a.pk))) == [0, 1, 2]

    @pytest.mark.parametrize(
        "name,category,expected",
        [
            ("Zmajor", "Scales", list(range(8))),        # major-like -> 7 positions
            ("Zmajor pentatonic", "Scales", DEFAULT_FIVE),  # excluded from the 7-position rule
            ("Zblues", "Scales", DEFAULT_FIVE),
            ("Zpentatonic", "Scales", DEFAULT_FIVE),
            ("Zarp", "Arpeggios", DEFAULT_FIVE),
            ("Zother", "Scales", DEFAULT_FIVE),
        ],
    )
    def test_note_without_any_positions_is_guessed_from_name(self, api_get, name, category, expected):
        note = make_note(name, category)
        assert orders(api_get(reverse(self.url), notes_id=str(note.pk))) == expected

    def test_similar_note_without_positions_still_guesses_from_name(self, api_get):
        a = make_note("Ymajor")
        make_note("Ymajor")
        assert orders(api_get(reverse(self.url), notes_id=str(a.pk))) == list(range(8))

    def test_database_error_gets_default_positions(self, api_get):
        with mock.patch.object(Notes.objects, "get", side_effect=RuntimeError("db")):
            response = api_get(reverse(self.url), notes_id="1")
        assert orders(response) == DEFAULT_FIVE

    def test_unexpected_error_returns_standard_positions(self, api_get):
        with mock.patch("api.views.int", side_effect=RuntimeError("boom"), create=True):
            response = api_get(reverse(self.url), notes_id="1")
        assert response.status_code == 200
        assert orders(response) == DEFAULT_FIVE


# --------------------------------------------------------------------------- arpeggio-positions
class TestArpeggioPositions:
    url = "api:ajax_arpeggio_positions"

    def test_missing_notes_id_is_400(self, api_get):
        response = api_get(reverse(self.url))
        assert response.status_code == 400
        assert response.json() == {"error": "Missing required parameter: notes_id"}

    def test_positions_from_database(self, api_get):
        # arpeggio "Major 7" (id 2) has five stored positions
        assert orders(api_get(reverse(self.url), notes_id="2")) == [0, 1, 2, 3, 4, 5]

    def test_database_positions_replace_default(self, api_get):
        note = make_note("Zarp", "Arpeggios")
        for order in (3, 1):
            NotesPosition.objects.create(notes_name=note, position_order=order, position="1")
        assert orders(api_get(reverse(self.url), notes_id=str(note.pk))) == [0, 1, 3]

    def test_note_without_positions_keeps_default(self, api_get):
        note = make_note("Zarp", "Arpeggios")
        assert orders(api_get(reverse(self.url), notes_id=str(note.pk))) == DEFAULT_FIVE

    def test_unknown_note_gets_default(self, api_get):
        assert orders(api_get(reverse(self.url), notes_id="999999")) == DEFAULT_FIVE

    def test_non_numeric_id_gets_default(self, api_get):
        assert orders(api_get(reverse(self.url), notes_id="abc")) == DEFAULT_FIVE

    def test_structure_probe_failure_is_ignored(self, api_get):
        with mock.patch.object(Notes.objects, "count", side_effect=RuntimeError("db")):
            response = api_get(reverse(self.url), notes_id="2")
        assert orders(response) == [0, 1, 2, 3, 4, 5]

    def test_lookup_failure_keeps_default(self, api_get):
        with mock.patch.object(Notes.objects, "get", side_effect=RuntimeError("db")):
            response = api_get(reverse(self.url), notes_id="2")
        assert orders(response) == DEFAULT_FIVE

    def test_unexpected_error_returns_standard_positions(self, api_get):
        with mock.patch("api.views.int", side_effect=RuntimeError("boom"), create=True):
            response = api_get(reverse(self.url), notes_id="2")
        assert response.status_code == 200
        assert orders(response) == DEFAULT_FIVE


# --------------------------------------------------------------------------- emergency
class TestEmergencyPositions:
    def get(self, client, name="api:emergency_positions", **params):
        return client.get(reverse(name), params)

    def test_chord_names_from_database_for_known_type(self, client):
        response = self.get(client, type_name="Triads")
        assert response.status_code == 200
        names = [c["chord_name"] for c in response.json()["chord_names"]]
        assert set(names) == {"Major", "Minor", "Diminished", "Augmented"}

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: chord names are not de-duplicated (default model ordering defeats .distinct()), "
        "so the endpoint returns every chord name once per stored row",
    )
    def test_chord_names_are_unique(self, client):
        names = [c["chord_name"] for c in self.get(client, type_name="Triads").json()["chord_names"]]
        assert len(names) == len(set(names))

    def test_alias_url_behaves_identically(self, client):
        a = self.get(client, "api:emergency_chord_names", type_name="V1").json()
        b = self.get(client, "api:emergency_positions", type_name="V1").json()
        assert a == b

    @pytest.mark.parametrize(
        "type_name,expected",
        [
            ("Triads", ["Major", "Minor", "Diminished", "Augmented"]),
            ("Spread Triads", ["Major", "Minor", "Diminished", "Augmented"]),
            ("V9", ["Major", "Minor"]),
        ],
    )
    def test_unknown_type_uses_static_names(self, client, type_name, expected):
        with mock.patch("api.views.ChordNotes") as chord_notes:
            chord_notes.objects.filter.side_effect = RuntimeError("db")
            response = self.get(client, type_name=type_name)
        assert [c["chord_name"] for c in response.json()["chord_names"]] == expected

    def test_type_without_database_rows_uses_static_names(self, client):
        response = self.get(client, type_name="Triads x")  # not in database, no 'Triads'/'Spread' fix needed
        assert [c["chord_name"] for c in response.json()["chord_names"]] == ["Major", "Minor", "Diminished", "Augmented"]
        response = self.get(client, type_name="Nope")
        assert [c["chord_name"] for c in response.json()["chord_names"]] == ["Major", "Minor"]

    def test_ranges_for_type_and_chord(self, client):
        response = self.get(client, type_name="Triads", chord_name="Major")
        ranges = response.json()["ranges"]
        assert len(ranges) == 6
        assert ranges[0] == {"id": "1", "range": "e - g"}
        assert ranges[-1] == {"id": "6", "range": "highA - e"}

    @pytest.mark.parametrize("chord_id,count", [("1", 3), ("52", 3), ("4", 4), ("5", 4), ("6", 4)])
    def test_inversions_for_chord_notes_id(self, client, chord_id, count):
        response = self.get(client, chord_notes_id=chord_id)
        assert len(response.json()["positions"]) == count
        assert response.json()["positions"][0] == {"inversion_order": "Root Position"}
        if count == 4:
            assert response.json()["positions"][-1] == {"inversion_order": "Third Inversion"}

    @pytest.mark.parametrize(
        "notes_id,expected_last",
        [("49", 5), ("1", 7), ("2", 7), ("3", 7), ("4", 5), ("999", 5)],
    )
    def test_scale_positions_by_notes_id(self, client, notes_id, expected_last):
        response = self.get(client, notes_id=notes_id)
        assert [p["position_order"] for p in response.json()["positions"]] == list(range(expected_last + 1))

    def test_no_parameters_returns_all_notes_only(self, client):
        assert self.get(client).json() == {"positions": [{"position_order": 0}]}

    def test_unexpected_error_returns_all_notes_only(self):
        from types import SimpleNamespace

        from api.views import emergency_positions

        response = emergency_positions(SimpleNamespace())  # no .GET -> AttributeError inside the view
        assert response.status_code == 200
        assert response.content == b'{"positions": [{"position_order": 0}]}'
