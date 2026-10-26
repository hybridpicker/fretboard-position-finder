"""Unit tests for positionfinder.views_chords helpers and the ChordView class."""

import json

import pytest
from django.http import Http404
from django.test import RequestFactory

from positionfinder import views_chords
from positionfinder.models import Root
from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.views_chords import (
    ChordView,
    extract_and_convert_notes,
    fretboard_chords_view,
    get_note_order,
)

RF = RequestFactory()


def pos(**strings):
    """Build one position dict: pos(eString=['g2', '5', True, False])."""
    return {"assigned_strings": list(strings), **strings}


PITCH = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}


def pitches(names):
    return [PITCH[n] for n in names]


BUG_SPELLING = (
    "BUG: spelling preference is inverted: minor chords (prefer_flats) turn flats into sharps and "
    "non-minor chords turn sharps into flats, contradicting the code comments"
)


def chord_json(name, root, positions, rng="e - g", inversion="Basic Position"):
    data = {"chord": name, rng: {inversion: positions}}
    if root is not None:
        data["root"] = root
    return data


# ----------------------------------------------------------------------------- get_note_order
def test_get_note_order_rotates_to_root():
    order = get_note_order("D")
    assert order[0] == "D"
    assert order[-1] == "Db"
    assert len(order) == 17


def test_get_note_order_unknown_root_returns_default():
    assert get_note_order("X") == views_chords.NOTE_ORDER


# ----------------------------------------------------------------------------- extract_and_convert_notes
def test_extract_uses_top_level_root_only_when_no_positions():
    assert extract_and_convert_notes({"chord": "Major", "root": ["C", 0]}) == ["C"]


def test_extract_collects_notes_from_inversion_lists_sorted_from_root():
    data = chord_json(
        "Major",
        ["A", 9],
        [
            pos(
                eString=["c#3", "3", True, False],
                bString=["e2", "5", True, False],
                gString=["a2", "R", True, True],
            )
        ],
    )
    result = extract_and_convert_notes(data)
    assert result[0] == "A" and result[-1] == "E"
    assert pitches(result) == [9, 1, 4]


def test_extract_without_top_level_root_uses_root_flag_from_note():
    data = chord_json(
        "Major",
        None,
        [
            pos(
                eString=["g2", "5", True, False],
                bString=["e2", "3", True, False],
                gString=["c2", "R", True, True],
            )
        ],
    )
    assert extract_and_convert_notes(data) == ["C", "E", "G"]


def test_extract_without_any_root_sorts_by_global_note_order():
    data = chord_json(
        "Major",
        None,
        [pos(eString=["g2", "5", True, False], bString=["e2", "3", True, False])],
    )
    assert extract_and_convert_notes(data) == ["E", "G"]


def test_extract_skips_invalid_entries():
    data = chord_json(
        "Major",
        ["C", 0],
        [
            {
                "assigned_strings": ["eString"],
                "eString": ["e2", "3"],
                "bString": None,
                "gString": "not-a-list",
                "dString": [None, "x"],
                "AString": ["lowBString", "x"],
                "ELowString": ["x9", "?"],
                "highAString": [],
            }
        ],
    )
    assert extract_and_convert_notes(data) == ["C", "E"]


def test_extract_handles_nested_lists_and_non_container_items():
    data = {
        "chord": "Major",
        "root": ["C", 0],
        "extra": [{"e - g": {"Basic Position": [pos(eString=["g2", "5"])]}}, "text"],
    }
    assert extract_and_convert_notes(data) == ["C", "G"]


@pytest.mark.xfail(strict=True, reason=BUG_SPELLING)
def test_extract_prefers_flats_for_minor_chords():
    data = chord_json("Minor", ["C", 0], [pos(eString=["d#3", "b3"], bString=["g2", "5"])])
    assert extract_and_convert_notes(data) == ["C", "Eb", "G"]


@pytest.mark.xfail(strict=True, reason=BUG_SPELLING)
def test_extract_prefers_sharps_for_major_chords():
    data = chord_json("Major", ["C", 0], [pos(eString=["eb3", "3"], bString=["g2", "5"])])
    assert extract_and_convert_notes(data) == ["C", "D#", "G"]


@pytest.mark.parametrize("chord", ["Minor", "Major"])
def test_extract_keeps_pitches_whatever_the_spelling(chord):
    data = chord_json(chord, ["C", 0], [pos(eString=["d#3", "x"], bString=["g2", "5"])])
    assert pitches(extract_and_convert_notes(data)) == [0, 3, 7]


def test_extract_removes_enharmonic_duplicates():
    data = chord_json("Major", ["C", 0], [pos(eString=["c#3", "x"], bString=["db2", "x"])])
    result = extract_and_convert_notes(data)
    assert len(result) == 2
    assert pitches(result) == [0, 1]


def test_extract_root_candidate_falls_back_to_first_note():
    # root note is not part of the traversed notes (empty top-level root name is falsy)
    data = chord_json("Major", None, [pos(eString=["g2", "5"], bString=["e2", "3"])])
    assert extract_and_convert_notes(data) == ["E", "G"]


MIN7B5 = [
    ("C", ["C", "Eb", "Gb", "Bb"]),
    ("D", ["D", "F", "Ab", "C"]),
    ("E", ["E", "G", "Bb", "D"]),
    ("F", ["F", "Ab", "B", "Eb"]),
    ("G", ["G", "Bb", "Db", "F"]),
    ("A", ["A", "C", "Eb", "G"]),
    ("B", ["B", "D", "F", "A"]),
    ("Bb", ["Bb", "Db", "E", "Ab"]),
    ("Eb", ["Eb", "Gb", "A", "Db"]),
    ("Ab", ["Ab", "B", "D", "Gb"]),
    ("Db", ["Db", "E", "G", "B"]),
    ("Gb", ["Gb", "A", "C", "E"]),
]


@pytest.mark.parametrize("root,expected", MIN7B5)
def test_extract_minor_7b5_uses_fixed_spelling(root, expected):
    data = chord_json("Minor 7b5", [root, 0], [pos(eString=["c3", "R"])])
    assert extract_and_convert_notes(data) == expected


@pytest.mark.parametrize(
    "root,expected",
    [("A#", ["Bb", "Db", "E", "Ab"]), ("C#", ["Db", "E", "G", "B"]), ("F#", ["Gb", "A", "C", "E"])],
)
@pytest.mark.xfail(
    strict=True,
    reason="BUG: the 'standardise sharp roots to flats' step uses SHARP_ENHARMONICS "
    "backwards, so sharp roots keep their sharp spelling",
)
def test_extract_minor_7b5_sharp_roots_are_flat_spelled(root, expected):
    data = chord_json("Minor 7b5", [root, 0], [pos(eString=["c3", "R"])])
    assert extract_and_convert_notes(data) == expected


@pytest.mark.parametrize(
    "root,expected",
    [
        ("A#", [10, 1, 4, 8]),
        ("C#", [1, 4, 7, 11]),
        ("F#", [6, 9, 0, 4]),
        ("D#", [3, 6, 9, 1]),
        ("G#", [8, 11, 2, 6]),
    ],
)
def test_extract_minor_7b5_sharp_roots_have_correct_pitches(root, expected):
    data = chord_json("Minor 7b5", [root, 0], [pos(eString=["c3", "R"])])
    assert pitches(extract_and_convert_notes(data)) == expected


@pytest.mark.parametrize("name", ["Min7b5", "minor 7b5 something"])
def test_extract_minor_7b5_name_variants(name):
    data = chord_json(name, ["C", 0], [pos(eString=["c3", "R"])])
    assert extract_and_convert_notes(data) == ["C", "Eb", "Gb", "Bb"]


def test_extract_minor_7b5_without_root_keeps_extracted_notes():
    data = chord_json("Minor 7b5", None, [pos(eString=["c3", "R"], bString=["eb3", "b3"])])
    assert pitches(extract_and_convert_notes(data)) == [0, 3]


def test_extract_ignores_empty_top_level_root_name():
    data = chord_json("Major", [""], [pos(eString=["g2", "5"], bString=["e2", "3"])])
    assert extract_and_convert_notes(data) == ["E", "G"]


# ----------------------------------------------------------------------------- generate_chord_function
@pytest.mark.parametrize(
    "name,expected",
    [
        ("Major", "R - 3 - 5"),
        ("Minor 7", "R - b3 - 5 - b7"),
        ("Dominant 7", "R - 3 - 5 - b7"),
        ("Diminished 7", "R - b3 - b5 - bb7"),
        ("Minor 7b5", "R - b3 - b5 - b7"),
        ("Minor7b5", "R - b3 - b5 - b7"),
        ("MIN7B5", "R - b3 - b5 - b7"),
        ("Dominant 7(b9)", "R - 3 - 5 - b7 - b9"),
        ("Add9", "R - 3 - 5 - 9"),
        ("Something Else", "R - ..."),
    ],
)
def test_generate_chord_function(name, expected):
    assert ChordView().generate_chord_function(name) == expected


# ----------------------------------------------------------------------------- process_request
def test_process_request_defaults():
    params = ChordView().process_request(RF.get("/chords"))
    assert params == {
        "root_id": 1,
        "category_id": 3,
        "type_id": "Triads",
        "chord_select_name": "Major",
        "selected_range": "e - g",
        "position_select": "Root Position",
        "is_six_string": True,
        "range": "e - g",
    }


def test_process_request_reads_query_and_eight_string_cookie():
    request = RF.get(
        "/chords",
        {
            "root": "5",
            "models_select": "3",
            "type_options_select": "V2",
            "chords_options_select": "Minor 7",
            "note_range": "b - A",
            "position_select": "Basic Position",
        },
    )
    request.COOKIES["stringConfig"] = "eight-string"
    params = ChordView().process_request(request)
    assert params["root_id"] == 5
    assert params["type_id"] == "V2"
    assert params["chord_select_name"] == "Minor 7"
    assert params["selected_range"] == params["range"] == "b - A"
    assert params["is_six_string"] is False


def test_process_request_invalid_root_raises_value_error():
    with pytest.raises(ValueError):
        ChordView().process_request(RF.get("/chords", {"root": "abc"}))


def test_get_string_config_default_and_cookie():
    view = ChordView()
    assert view._get_string_config_from_cookie(RF.get("/")) == "six-string"
    request = RF.get("/")
    request.COOKIES["stringConfig"] = "eight-string"
    assert view._get_string_config_from_cookie(request) == "eight-string"


# ----------------------------------------------------------------------------- DB-backed helpers
@pytest.mark.django_db
@pytest.mark.usefixtures("music_data")
class TestChordViewQueries:
    def test_selected_root_object_found(self):
        assert ChordView().get_selected_root_object(14).name == "A"

    def test_selected_root_object_falls_back_to_id_one(self):
        assert ChordView().get_selected_root_object(424242).id == 1

    def test_all_root_options_and_categories(self):
        view = ChordView()
        assert view.get_all_root_options().count() == 17
        assert sorted(c.category_name for c in view.get_category_objects()) == [
            "Arpeggios",
            "Chords",
            "Scales",
        ]

    def test_chord_options_for_type(self):
        options = list(ChordView().get_chord_options("Triads"))
        assert "Major" in options and "Minor" in options
        assert len(options) == len(set(options))

    def test_chord_options_unknown_type_empty(self):
        assert list(ChordView().get_chord_options("Nope")) == []

    def test_type_options_split_standard_and_v_system(self):
        options = ChordView().get_type_options()
        assert options["standard_types"][0] == "Triads"
        assert "Spread Triads" in options["standard_types"]
        v = options["v_system_types"]
        assert v[:3] == ["V1", "V2", "V3"]
        assert v == sorted(v, key=lambda s: int(s[1:]))  # natural, not lexicographic

    def test_type_options_ignore_other_type_names(self):
        template = ChordNotes.objects.filter(category=3).first()
        template.pk = None
        template.type_name = "Foo"
        template.save()
        options = ChordView().get_type_options()
        assert "Foo" not in options["standard_types"] + options["v_system_types"]

    def test_range_options_six_string_excludes_eight_string_ranges(self):
        ranges = [r.range for r in ChordView().get_range_options("V1", "Major 7", True)]
        assert ranges
        assert all("highA" not in r and "lowB" not in r for r in ranges)

    def test_range_options_eight_string_includes_all_and_sorted(self):
        ranges = [r.range for r in ChordView().get_range_options("V1", "Major 7", False)]
        assert any("lowB" in r or "highA" in r for r in ranges)
        order = views_chords.NOTE_RANGE_ORDER
        indices = [order.index(r) if r in order else 999 for r in ranges]
        assert indices == sorted(indices)

    def test_range_options_unknown_range_sorted_last(self):
        template = ChordNotes.objects.filter(type_name="V1", chord_name="Major 7").first()
        template.pk = None
        template.range = "zz - yy"
        template.save()
        ranges = [r.range for r in ChordView().get_range_options("V1", "Major 7", True)]
        assert ranges[-1] == "zz - yy"

    def test_inversion_data_empty_positions(self):
        assert (
            ChordView().get_inversion_data_for_range([], "Major", "e - g", "Triads", 0, 0, "C")
            == {}
        )

    def test_inversion_data_builds_dict_per_inversion(self):
        chord = ChordNotes.objects.filter(
            type_name="Triads", chord_name="Major", range="e - g"
        ).first()
        positions = list(ChordPosition.objects.filter(notes_name_id=chord.id))
        data = ChordView().get_inversion_data_for_range(
            positions, "Major", "e - g", "Triads", 0, chord.tonal_root, "C"
        )
        assert set(data) == {p.inversion_order for p in positions}
        for value in data.values():
            assert "assigned_strings" in value

    def test_inversion_data_swallows_errors_into_empty_dict(self, monkeypatch):
        def boom(*args, **kwargs):
            raise RuntimeError("broken")

        monkeypatch.setattr(views_chords, "get_position_dict", boom)
        chord = ChordNotes.objects.filter(type_name="Triads", chord_name="Major").first()
        positions = list(ChordPosition.objects.filter(notes_name_id=chord.id))
        data = ChordView().get_inversion_data_for_range(
            positions, "Major", "e - g", "Triads", 0, 0, "C"
        )
        assert data == {p.inversion_order: {} for p in positions}

    # --- get_context / render
    def request_with_session(self, query):
        request = RF.get("/chords", query)
        request.session = {}
        return request

    def test_get_context_core_values(self):
        ctx = ChordView().get_context(
            self.request_with_session(
                {"root": "14", "type_options_select": "V1", "chords_options_select": "Minor 7"}
            )
        )
        assert ctx["root_name"] == "A" and ctx["root_id"] == 14
        assert ctx["selected_chord"] == "Minor 7"
        assert ctx["chord_function"] == "R - b3 - 5 - b7"
        assert ctx["meta_description"].startswith("Learn to play A Minor 7 chord")
        assert ctx["breadcrumbs"][-1] == ("/chords/a/minor-7/", "A Minor 7")
        assert ctx["structured_data"]["chord_root"] == "A"
        data = json.loads(ctx["chord_json_data"])
        assert data["root"] == ["A", 9]
        assert data["note_range"] == "e - g"

    def test_get_context_position_options_are_inversions_of_initial_chord(self):
        ctx = ChordView().get_context(self.request_with_session({}))
        inversions = [p.inversion_order for p in ctx["position_options"]]
        assert inversions
        assert all(isinstance(i, str) for i in inversions)

    def test_get_context_falls_back_when_range_missing(self):
        ctx = ChordView().get_context(self.request_with_session({"note_range": "no - such"}))
        assert ctx["selected_range"] == "no - such"
        assert ctx["range_options"]

    def test_get_context_falls_back_when_chord_name_missing(self):
        ctx = ChordView().get_context(self.request_with_session({"chords_options_select": "Nope"}))
        assert ctx["selected_chord"] == "Nope"
        assert ctx["position_options"]
        assert ctx["chord_function"] == "R - ..."

    def test_get_context_falls_back_when_type_missing(self):
        ctx = ChordView().get_context(self.request_with_session({"type_options_select": "Nope"}))
        assert ctx["selected_type"] == "Nope"
        assert ctx["position_options"]
        assert list(ctx["chord_options"]) == []

    def test_get_context_without_any_chord_data_is_swallowed(self):
        ChordNotes.objects.all().delete()
        ctx = ChordView().get_context(self.request_with_session({}))
        assert ctx["position_options"] == []
        assert ctx["range_options"] == []
        assert ctx["selected_notes"] == ["C"]
        assert ctx["chord_type_options"]["v_system_types"] == []

    def test_get_context_survives_note_extraction_failure(self, monkeypatch):
        def boom(_):
            raise RuntimeError("bad data")

        monkeypatch.setattr(views_chords, "extract_and_convert_notes", boom)
        ctx = ChordView().get_context(self.request_with_session({}))
        assert ctx["selected_notes"] == []

    def test_get_context_six_string_filters_range_options(self):
        ctx = ChordView().get_context(
            self.request_with_session(
                {"type_options_select": "V1", "chords_options_select": "Major 7"}
            )
        )
        assert ctx["is_eight_string"] is False
        assert all("lowB" not in r.range and "highA" not in r.range for r in ctx["range_options"])

    def test_render_re_raises_unexpected_errors(self):
        Root.objects.all().delete()
        request = self.request_with_session({})
        with pytest.raises(Root.DoesNotExist):
            ChordView().render(request)

    def test_render_re_raises_http404(self, monkeypatch):
        def not_found(self, request):
            raise Http404("gone")

        monkeypatch.setattr(ChordView, "get_context", not_found)
        with pytest.raises(Http404):
            ChordView().render(self.request_with_session({}))

    def test_fretboard_chords_view_function_renders_response(self):
        response = fretboard_chords_view(self.request_with_session({}))
        assert response.status_code == 200
        assert b"Major" in response.content

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: extract_and_convert_notes only reads inversion values that are lists, but "
        "ChordView stores them as dicts, so selected_notes only ever contains the root note",
    )
    def test_selected_notes_contain_all_chord_tones(self):
        ctx = ChordView().get_context(self.request_with_session({}))
        assert ctx["selected_notes"] == ["C", "E", "G"]
