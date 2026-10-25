"""Pure-function tests (no database) for the core positionfinder helpers."""
from collections import OrderedDict

import pytest

from positionfinder import template_notes as tn
from positionfinder.chord_position_choices import INVERSION_CHOICES, ChordInversionChoicesField
from positionfinder.get_position_dict_chords import normalize_pitch_index
from positionfinder.get_position_dict_scales import (
    get_tones_from_notes,
    get_transposable_positions,
    ordering_positions,
    re_ordering_positions,
    transpose_actual_position,
    transpose_position,
)
from positionfinder.functionality_tones_setup import find_tone
from positionfinder.note_validation import (
    apply_note_validation,
    validate_and_filter_note_positions,
)
from positionfinder.notes_choices import (
    CHORD_CHOICES,
    NOTES_CHOICES,
    ChordChoicesField,
    NotesChoicesField,
)
from positionfinder.string_choices import STRING_CHOICES, TUNING_NOTES, StringChoicesField
from positionfinder.string_range_choices import STRING_RANGE_CHOICES, StringRangeChoicesField
from positionfinder.root_note_setup import root_pitch_list_append


# --------------------------------------------------------------------------- note_validation

class TestValidateAndFilterNotePositions:
    def test_empty_input_returns_empty_dict(self):
        assert validate_and_filter_note_positions({}) == {}
        assert validate_and_filter_note_positions(None) == {}

    def test_drops_unassigned_strings(self):
        data = {
            "assigned_strings": ["eString"],
            "eString": ["e3", "R", True, True],
            "bString": ["b2", "3", True, False],
        }
        result = validate_and_filter_note_positions(data)
        assert set(result) == {"assigned_strings", "eString"}
        assert result["assigned_strings"] == ["eString"]

    def test_keeps_existing_root_untouched(self):
        data = {
            "assigned_strings": ["eString", "bString"],
            "eString": ["e3", "R", True, False],
            "bString": ["b2", "3", True, True],
        }
        result = validate_and_filter_note_positions(data)
        assert result["eString"][3] is False
        assert result["bString"][3] is True

    def test_promotes_first_note_to_root_when_none_is_root(self):
        data = {
            "assigned_strings": ["eString", "bString"],
            "eString": ["e3", "R", True, False],
            "bString": ["b2", "3", True, False],
        }
        result = validate_and_filter_note_positions(data)
        assert result["eString"][3] is True
        assert result["bString"][3] is False

    def test_does_not_mutate_input_lists(self):
        data = {
            "assigned_strings": ["eString"],
            "eString": ["e3", "R", True, False],
        }
        validate_and_filter_note_positions(data)
        assert data["eString"][3] is False

    def test_only_assigned_strings_key_has_no_root_promotion(self):
        result = validate_and_filter_note_positions({"assigned_strings": ["eString"]})
        assert result == {"assigned_strings": ["eString"]}

    def test_short_lists_are_not_promoted(self):
        data = {"assigned_strings": ["eString"], "eString": ["e3", "R"]}
        result = validate_and_filter_note_positions(data)
        assert result["eString"] == ["e3", "R"]

    def test_non_list_value_is_passed_through(self):
        data = {"assigned_strings": ["eString"], "eString": "raw"}
        result = validate_and_filter_note_positions(data)
        assert result["eString"] == "raw"

    def test_missing_assigned_strings_yields_empty_assignment(self):
        result = validate_and_filter_note_positions({"eString": ["e3", "R", True, True]})
        assert result == {"assigned_strings": []}


class TestApplyNoteValidation:
    def test_validates_each_position_in_place(self):
        ctx = {
            "positions": [
                {"assigned_strings": ["eString"], "eString": ["e3", "R", True, False], "bString": ["x"]},
                {},
            ]
        }
        out = apply_note_validation(ctx)
        assert out is ctx
        assert set(out["positions"][0]) == {"assigned_strings", "eString"}
        assert out["positions"][0]["eString"][3] is True
        assert out["positions"][1] == {}

    def test_context_without_positions_is_returned_unchanged(self):
        ctx = {"other": 1}
        assert apply_note_validation(ctx) == {"other": 1}


# --------------------------------------------------------------------------- scale position helpers

class TestTransposePosition:
    def test_lowers_octave_digit_by_one(self):
        assert transpose_position(["c3", "ds4", "g2"]) == ["c2", "ds3", "g1"]

    def test_empty(self):
        assert transpose_position([]) == []

    @pytest.mark.parametrize("tones", [["c3"], ["fs4", "a3", "d2"], ["gb5"]])
    def test_transpose_then_raise_is_identity(self, tones):
        lowered = transpose_position(tones)
        raised = [t[:-1] + str(int(t[-1]) + 1) for t in lowered]
        assert raised == tones


def _scale_position():
    return {
        "0": {s: [{"tones": []}] for s in tn.STRINGS},
        "1": {
            **{s: [{"tones": []}] for s in tn.STRINGS},
            "eString": [{"tones": ["f3", "g3"]}],
        },
        "2": {
            **{s: [{"tones": []}] for s in tn.STRINGS},
            "eString": [{"tones": ["c3"]}],
        },
        "3": {s: [{"no_tones_key": 1}] for s in tn.STRINGS},
    }


class TestTransposeActualPosition:
    def test_transposes_only_selected_positions(self):
        pos = _scale_position()
        out = transpose_actual_position(pos, [1])
        assert out["1"]["eString"][0]["tones"] == ["f2", "g2"]
        assert out["2"]["eString"][0]["tones"] == ["c3"]

    def test_strings_without_tones_key_are_skipped(self):
        pos = _scale_position()
        out = transpose_actual_position(pos, [3])
        assert out["3"]["eString"] == [{"no_tones_key": 1}]


class TestOrderingPositions:
    def test_orders_by_average_score_of_e_string(self):
        pos = _scale_position()
        # position 1 = f3,g3 -> (4+36 + 5+36)/2 = 40.5 ; position 2 = c3 -> 37; 3 has no tones -> 0
        pos["3"] = {"eString": [{"tones": []}]}
        ordered = ordering_positions(pos)
        assert isinstance(ordered, OrderedDict)
        assert list(ordered) == [3, 2, 1]
        assert ordered[1] == pytest.approx(40.5)
        assert ordered[2] == pytest.approx(37)
        assert ordered[3] == 0

    def test_missing_e_string_scores_zero(self):
        pos = {"0": {}, "1": {}}
        assert ordering_positions(pos) == OrderedDict([(1, 0)])

    def test_invalid_tones_are_ignored(self):
        pos = {"0": {}, "1": {"eString": [{"tones": ["", "x", "zz9"]}]}}
        assert ordering_positions(pos) == OrderedDict([(1, 0)])

    def test_only_base_position_returns_empty(self):
        assert ordering_positions({"0": {}}) == OrderedDict()


class TestReOrderingPositions:
    def test_renumbers_positions_by_score_and_keeps_zero(self):
        pos = {
            "0": "open",
            "1": {"eString": [{"tones": ["g3"]}]},
            "2": {"eString": [{"tones": ["c3"]}]},
        }
        out = re_ordering_positions(pos)
        assert out["0"] == "open"
        assert out["1"] is pos["2"]
        assert out["2"] is pos["1"]
        assert set(out) == {"0", "1", "2"}


class TestGetTransposablePositions:
    def test_position_whose_tones_exist_an_octave_lower_is_transposable(self):
        # e string offers f2/f3 and g2/g3, so f3,g3 can be lowered; c3 cannot (only c3)
        pos = {
            "0": {},
            "1": {"eString": [{"tones": ["f3", "g3"]}]},
            "2": {"eString": [{"tones": ["c3"]}]},
        }
        assert get_transposable_positions(3, pos) == [1]

    def test_missing_keys_are_skipped(self):
        assert get_transposable_positions(4, {"0": {}}) == []

    def test_strings_without_tones_are_ignored(self):
        pos = {"1": {"eString": [{"tones": []}], "bString": [{}]}}
        assert get_transposable_positions(2, pos) == [1]

    def test_unknown_base_note_is_treated_as_missing(self):
        pos = {"1": {"eString": [{"tones": ["zz3"]}]}}
        assert get_transposable_positions(2, pos) == [1]


class _Obj:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __getattr__(self, name):
        return None


def test_get_tones_from_notes_skips_none_and_keeps_order():
    obj = _Obj(first_note=0, second_note=4, third_note=7, fifth_note=11)
    assert get_tones_from_notes(obj) == [0, 4, 7, 11]


# --------------------------------------------------------------------------- misc small helpers

@pytest.mark.parametrize("raw,expected", [(0, 0), (11, 11), (12, 0), (13, 1), (35, 11), (24, 0)])
def test_normalize_pitch_index(raw, expected):
    assert normalize_pitch_index(raw) == expected


def test_root_pitch_list_append_one_pitch_per_octave():
    assert root_pitch_list_append(3) == [o * 12 + 3 for o in tn.OCTAVES]


def test_find_tone():
    assert find_tone("3", ["R", "b3", "5"]) is True
    assert find_tone("9", ["R", "b3", "5"]) is False
    assert find_tone("x", []) is False


# --------------------------------------------------------------------------- template_notes invariants

class TestTemplateNotes:
    def test_twelve_semitone_tables_have_12_entries(self):
        for table in (tn.NOTES, tn.NOTES_SHARP, tn.TENSIONS, tn.TENSIONS_OPTIONAL,
                      tn.NOTE_NAMES, tn.NOTE_NAMES_OPTION, tn.NOTE_NAMES_SHARP,
                      tn.NOTE_NAMES_SHARP_OPTION):
            assert len(table) == 12

    def test_flat_and_sharp_names_agree_on_naturals(self):
        for i, (flat, sharp) in enumerate(zip(tn.NOTES, tn.NOTES_SHARP)):
            if len(flat) == 1:
                assert flat == sharp, i

    def test_octaves_are_consecutive(self):
        assert tn.OCTAVES == list(range(tn.OCTAVES[0], tn.OCTAVES[-1] + 1))

    def test_inversions_start_with_basic_position(self):
        assert tn.INVERSIONS[0] == "Basic Position"
        assert len(set(tn.INVERSIONS)) == len(tn.INVERSIONS)

    def test_every_string_has_option_table(self):
        for s in ("eString", "bString", "gString", "dString", "AString", "ELowString"):
            assert s in tn.STRING_NOTE_OPTIONS

    @pytest.mark.parametrize("string", sorted(__import__("positionfinder.template_notes", fromlist=["x"]).STRING_NOTE_OPTIONS))
    def test_tones_and_frets_are_parallel_and_playable(self, string):
        table = tn.STRING_NOTE_OPTIONS[string][0]
        for note, entry in table.items():
            info = entry[0]
            assert len(info["tone"]) == len(info["fret"]), (string, note)
            for fret in info["fret"]:
                assert 0 <= fret <= 17, (string, note, fret)
            for tone in info["tone"]:
                assert tone.startswith(note), (string, note, tone)

    @pytest.mark.parametrize("string", sorted(__import__("positionfinder.template_notes", fromlist=["x"]).STRING_NOTE_OPTIONS))
    def test_enharmonic_spellings_share_frets(self, string):
        table = tn.STRING_NOTE_OPTIONS[string][0]
        for flat, sharp in zip(tn.NOTES, tn.NOTES_SHARP):
            if flat in table and sharp in table:
                assert table[flat][0]["fret"] == table[sharp][0]["fret"]


# --------------------------------------------------------------------------- choices fields

class TestChoicesFields:
    def test_notes_choices_cover_twelve_pitches(self):
        assert sorted(NOTES_CHOICES) == list(range(12))
        field = NotesChoicesField()
        assert [k for k, _v in field.choices] == list(range(12))

    def test_chord_choices_field(self):
        field = ChordChoicesField()
        assert field.max_length == 20
        assert {k for k, _v in field.choices} == set(CHORD_CHOICES)
        assert list(k for k, _v in field.choices) == sorted(CHORD_CHOICES)

    def test_string_choices_field(self):
        field = StringChoicesField()
        assert field.max_length == 20
        assert dict(field.choices).keys() == STRING_CHOICES.keys()
        assert len(TUNING_NOTES["6-string"]) == 6
        assert len(TUNING_NOTES["7-string"]) == 7
        assert len(TUNING_NOTES["8-string"]) == 8

    def test_range_choices_field_allows_every_range_within_max_length(self):
        field = StringRangeChoicesField()
        assert {k for k, _v in field.choices} == set(STRING_RANGE_CHOICES)
        assert all(len(k) <= field.max_length for k in STRING_RANGE_CHOICES)

    def test_inversion_choices_field(self):
        field = ChordInversionChoicesField()
        assert field.max_length == 20
        assert {k for k, _v in field.choices} == set(INVERSION_CHOICES)
        assert set(INVERSION_CHOICES) == set(tn.INVERSIONS)

    def test_fields_are_deconstructible_for_migrations(self):
        for field in (NotesChoicesField(), ChordChoicesField(), StringChoicesField(),
                      StringRangeChoicesField(), ChordInversionChoicesField()):
            name, path, args, kwargs = field.deconstruct()
            assert path.startswith("positionfinder.")
