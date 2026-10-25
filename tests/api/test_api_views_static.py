"""Tests for the static / parameter-only API views (no music data needed)."""

import pytest
from django.urls import reverse
from rest_framework.request import Request

from api.views import STRING_COMBINATIONS, TUNINGS

pytestmark = pytest.mark.django_db


class TestTuningOptions:
    def test_returns_tunings_and_string_sets(self, client):
        response = client.get(reverse("api:tuning_options"))
        assert response.status_code == 200
        data = response.json()
        assert data["tunings"]["6-string"] == ["E", "A", "D", "G", "B", "E"]
        assert data["tunings"]["7-string"][0] == "B"
        assert data["tunings"]["8-string"][0] == "F#"
        assert data["string_sets"]["6-string"] == ["6-3", "5-2", "4-1"]
        assert data["string_sets"]["8-string"][0] == "8-5"

    def test_matches_module_constants(self, client):
        data = client.get(reverse("api:tuning_options")).json()
        assert data == {"tunings": TUNINGS, "string_sets": STRING_COMBINATIONS}

    def test_string_counts_match_instrument(self, client):
        data = client.get(reverse("api:tuning_options")).json()
        for instrument, strings in (("6-string", 6), ("7-string", 7), ("8-string", 8)):
            assert len(data["tunings"][instrument]) == strings
            assert len(data["string_sets"][instrument]) == strings - 3


class TestVoicingGroups:
    def test_returns_empty_placeholder_lists(self, client):
        response = client.get(reverse("api:voicing_groups"))
        assert response.status_code == 200
        assert response.json() == {"seventh_chords": [], "triads": []}


class TestChordTypes:
    def test_returns_basic_chord_intervals(self, client):
        response = client.get(reverse("api:chord_types"))
        assert response.status_code == 200
        types = response.json()["chord_types"]
        assert types["Major"] == [0, 4, 7]
        assert types["Minor"] == [0, 3, 7]
        assert types["Dominant 7"] == [0, 4, 7, 10]
        assert types["Major 7"] == [0, 4, 7, 11]
        assert types["Minor 7"] == [0, 3, 7, 10]
        assert len(types) == 5


class TestChordVoicings:
    url = "api:chord_voicings"

    def test_valid_request_echoes_parameters(self, client):
        response = client.get(
            reverse(self.url),
            {"chord": "G7", "voicing_group": "V-2", "instrument": "7-string", "string_set": "5-2"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "voicing_group": "V-2",
            "instrument": "7-string",
            "string_set": "5-2",
            "chord": "G7",
            "voicings": [],
        }

    def test_defaults_for_instrument_and_string_set(self, client):
        data = client.get(reverse(self.url), {"chord": "Cmaj7", "voicing_group": "V-1"}).json()
        assert data["instrument"] == "6-string"
        assert data["string_set"] == "6-3"

    @pytest.mark.parametrize(
        "group,expected", [("V2", "V-2"), ("V-2", "V-2"), ("V12", "V-12"), ("W3", "W3")]
    )
    def test_voicing_group_is_normalised(self, client, group, expected):
        response = client.get(reverse(self.url), {"chord": "C", "voicing_group": group})
        assert response.status_code == 200
        assert response.json()["voicing_group"] == expected

    @pytest.mark.parametrize(
        "params",
        [
            {},
            {"chord": "G7"},
            {"voicing_group": "V-2"},
            {"chord": "", "voicing_group": "V-2"},
        ],
    )
    def test_missing_required_parameters_is_400(self, client, params):
        response = client.get(reverse(self.url), params)
        assert response.status_code == 400
        assert response.json() == {"error": "Missing required parameters (chord, voicing_group)"}

    @pytest.mark.parametrize("chord", ["H7", "xyz", "7", "1"])
    def test_invalid_chord_format_is_400(self, client, chord):
        response = client.get(reverse(self.url), {"chord": chord, "voicing_group": "V-2"})
        assert response.status_code == 400
        assert response.json() == {"error": "Invalid chord format"}

    @pytest.mark.parametrize("chord", ["C#m7b5", "Bbmaj7", "AΔ7", "Gø", "Edim7", "Faug", "C", "Dm"])
    def test_accepts_chord_suffix_variants(self, client, chord):
        response = client.get(reverse(self.url), {"chord": chord, "voicing_group": "V-3"})
        assert response.status_code == 200
        assert response.json()["chord"] == chord

    def test_over_long_chord_fails_serializer_validation(self, client):
        response = client.get(reverse(self.url), {"chord": "C" + "x" * 40, "voicing_group": "V-2"})
        assert response.status_code == 500
        assert "chord" in response.json()

    def test_over_long_instrument_fails_serializer_validation(self, client):
        response = client.get(
            reverse(self.url), {"chord": "C", "voicing_group": "V-2", "instrument": "x" * 11}
        )
        assert response.status_code == 500
        assert "instrument" in response.json()

    def test_response_is_cached_for_identical_query(self, client):
        url = reverse(self.url)
        first = client.get(url, {"chord": "C", "voicing_group": "V-9"})
        second = client.get(url, {"chord": "C", "voicing_group": "V-9"})
        assert first.status_code == second.status_code == 200
        assert first.json() == second.json()


class TestFallbackPositions:
    url = "api:fallback_positions"

    @staticmethod
    def orders(response):
        return [p["position_order"] for p in response.json()["positions"]]

    def test_without_notes_id_defaults_to_five_positions(self, client):
        response = client.get(reverse(self.url))
        assert response.status_code == 200
        assert self.orders(response) == [0, 1, 2, 3, 4, 5]

    def test_blues_id_has_five_positions(self, client):
        assert self.orders(client.get(reverse(self.url), {"notes_id": "49"})) == [0, 1, 2, 3, 4, 5]

    @pytest.mark.parametrize("notes_id", ["1", "2", "3"])
    def test_major_ids_have_seven_positions(self, client, notes_id):
        assert self.orders(client.get(reverse(self.url), {"notes_id": notes_id})) == list(range(8))

    @pytest.mark.parametrize("notes_id", ["10", "x", "-3", ""])
    def test_other_or_invalid_ids_get_default(self, client, notes_id):
        assert self.orders(client.get(reverse(self.url), {"notes_id": notes_id})) == [
            0,
            1,
            2,
            3,
            4,
            5,
        ]

    def test_inner_failure_defaults_to_five_positions(self, client, monkeypatch):
        # int() failing is not possible for digit strings, so make isdigit raise via a str subclass
        class Weird(str):
            def isdigit(self):
                raise RuntimeError("boom")

        monkeypatch.setattr(
            Request, "query_params", property(lambda self: {"notes_id": Weird("5")})
        )
        response = client.get(reverse(self.url))
        assert response.status_code == 200
        assert self.orders(response) == [0, 1, 2, 3, 4, 5]

    def test_outer_failure_returns_only_all_notes(self, client, break_view_query_params):
        response = client.get(reverse(self.url))
        assert response.status_code == 200
        assert response.json() == {"positions": [{"position_order": 0}]}
