"""API views against an empty database, plus fakes for query stages PostgreSQL cannot reach."""
from unittest import mock

import pytest
from django.urls import reverse

from positionfinder.models import NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition

pytestmark = pytest.mark.django_db


def make_chord(fourth=None):
    category = NotesCategory.objects.create(category_name="Chords")
    chord = ChordNotes.objects.create(
        category=category, type_name="Zt", chord_name="Zc", range="e - g", fourth_note=fourth
    )
    ChordPosition.objects.filter(notes_name=chord).delete()  # save() generates inversions
    return chord


def names(response):
    return [c["chord_name"] for c in response.json()["chord_names"]]


class TestEmptyDatabase:
    def test_database_is_really_empty(self):
        assert not ChordNotes.objects.exists()

    def test_chord_names_without_type_fall_back_to_major_minor(self, api_get):
        response = api_get(reverse("api:ajax_chord_names"))
        assert response.status_code == 200
        assert names(response) == ["Major", "Minor"]

    def test_chord_names_with_type_fall_back_to_major_minor(self, api_get):
        assert names(api_get(reverse("api:ajax_chord_names"), type_name="V1")) == ["Major", "Minor"]

    def test_chord_ranges_without_params_is_400(self, api_get):
        response = api_get(reverse("api:ajax_chord_ranges"))
        assert response.status_code == 400
        assert response.json() == {"error": "Missing required parameters and no database values found"}

    def test_chord_ranges_with_params_returns_standard_ranges(self, api_get):
        response = api_get(reverse("api:ajax_chord_ranges"), type_name="V1", chord_name="Major 7")
        assert response.status_code == 200
        assert [r["range"] for r in response.json()["ranges"]] == ["e - g", "b - d", "g - A", "d - E", "A - B"]

    def test_chord_positions_without_id_is_400(self, api_get):
        response = api_get(reverse("api:ajax_chord_positions"))
        assert response.status_code == 400
        assert response.json() == {"error": "Missing chord_notes_id and no database values found"}

    def test_chord_positions_unknown_id_returns_root_position(self, api_get):
        response = api_get(reverse("api:ajax_chord_positions"), chord_notes_id="5")
        assert response.json() == {"positions": [{"inversion_order": "Root Position"}]}

    def test_triad_without_any_positions_returns_root_position(self, api_get):
        chord = make_chord()
        response = api_get(reverse("api:ajax_chord_positions"), chord_notes_id=str(chord.pk))
        assert response.json() == {"positions": [{"inversion_order": "Root Position"}]}

    def test_seventh_chord_without_any_positions_returns_root_position(self, api_get):
        chord = make_chord(fourth=10)
        response = api_get(reverse("api:ajax_chord_positions"), chord_notes_id=str(chord.pk))
        assert response.json() == {"positions": [{"inversion_order": "Root Position"}]}

    def test_request_failure_without_positions_returns_root_position(self, api_get, break_view_query_params):
        response = api_get(reverse("api:ajax_chord_positions"), chord_notes_id="5")
        assert response.json() == {"positions": [{"inversion_order": "Root Position"}]}

    @pytest.mark.parametrize("name", ["api:ajax_scale_positions", "api:ajax_arpeggio_positions"])
    def test_position_views_default_without_notes(self, api_get, name):
        response = api_get(reverse(name), notes_id="3")
        assert [p["position_order"] for p in response.json()["positions"]] == [0, 1, 2, 3, 4, 5]

    def test_emergency_chord_names_use_static_fallback(self, client):
        response = client.get(reverse("api:emergency_positions"), {"type_name": "Spread Triads"})
        assert names(response) == ["Major", "Minor", "Diminished", "Augmented"]
        response = client.get(reverse("api:emergency_chord_names"), {"type_name": "V3"})
        assert names(response) == ["Major", "Minor"]

    def test_chord_names_request_failure_uses_static_fallback(self, api_get, break_view_query_params):
        assert names(api_get(reverse("api:ajax_chord_names"))) == ["Major", "Minor"]


class _FakeQuerySet(list):
    """Chainable stand-in for the queryset calls used by ChordRangesView."""

    def order_by(self, *args):
        return self

    def values(self, *args):
        return self

    def distinct(self, *args):
        return self


class _FakeChordNotes:
    """Stand-in for ChordNotes whose queryset stages return configurable rows."""

    def __init__(self, specific=(), by_chord=(), by_type=(), everything=()):
        self.rows = {
            frozenset({"type_name", "chord_name"}): specific,
            frozenset({"chord_name"}): by_chord,
            frozenset({"type_name"}): by_type,
        }
        self.everything = everything
        self.objects = self

    def filter(self, **kwargs):
        return _FakeQuerySet(self.rows[frozenset(kwargs)])

    def values(self, *args):
        return _FakeQuerySet(self.everything)


ROW = [{"id": 7, "range": "x - y"}]


class TestChordRangesFallbackStages:
    """With a working DISTINCT ON the later fallback stages would be used in this order."""

    def ranges(self, api_get, fake, **params):
        with mock.patch("api.views.ChordNotes", fake):
            response = api_get(reverse("api:ajax_chord_ranges"), type_name="T", chord_name="C", **params)
        assert response.status_code == 200
        return response.json()["ranges"]

    def test_specific_rows_win(self, api_get):
        fake = _FakeChordNotes(specific=ROW, by_chord=[{"id": 1, "range": "a - b"}])
        assert self.ranges(api_get, fake) == ROW

    def test_chord_name_stage(self, api_get):
        assert self.ranges(api_get, _FakeChordNotes(by_chord=ROW)) == ROW

    def test_type_name_stage(self, api_get):
        assert self.ranges(api_get, _FakeChordNotes(by_type=ROW)) == ROW

    def test_all_chords_stage(self, api_get):
        assert self.ranges(api_get, _FakeChordNotes(everything=ROW)) == ROW

    def test_rows_without_range_name_are_dropped(self, api_get):
        fake = _FakeChordNotes(specific=[{"id": 1, "range": ""}, {"id": 2, "range": "k - l"}])
        assert self.ranges(api_get, fake) == [{"id": 2, "range": "k - l"}]


class TestChordNamesLateFallbacks:
    def test_failure_after_type_lookup_uses_database_names(self, api_get):
        from rest_framework.response import Response as RealResponse

        calls = []

        def flaky(*args, **kwargs):
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("render failed")
            return RealResponse(*args, **kwargs)

        ChordNotes.objects.create(
            category=NotesCategory.objects.create(category_name="Chords"),
            type_name="Zt", chord_name="Zc", range="e - g",
        )
        with mock.patch("api.views.Response", side_effect=flaky):
            response = api_get(reverse("api:ajax_chord_names"), type_name="Zt")
        assert [c["chord_name"] for c in response.json()["chord_names"]] == ["Zc"]

    def test_failure_after_type_lookup_without_rows_uses_four_basic_names(self, api_get):
        from rest_framework.response import Response as RealResponse

        calls = []

        def flaky(*args, **kwargs):
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("render failed")
            return RealResponse(*args, **kwargs)

        with mock.patch("api.views.Response", side_effect=flaky):
            response = api_get(reverse("api:ajax_chord_names"), type_name="Zt")
        assert [c["chord_name"] for c in response.json()["chord_names"]] == [
            "Major", "Minor", "Diminished", "Augmented",
        ]
