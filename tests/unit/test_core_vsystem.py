"""VoicingSystem (Ted Greene V-System generator) behaviour."""
from unittest import mock

import pytest

from positionfinder import v_system_generator
from positionfinder.models import NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.v_system_generator import VoicingSystem

pytestmark = pytest.mark.django_db


@pytest.fixture
def vs():
    category = NotesCategory.objects.create(category_name="V-System")
    return VoicingSystem(notes_category_id=category.id)


def notes_of(chord):
    return [n for n in (chord.first_note, chord.second_note, chord.third_note, chord.fourth_note) if n is not None]


def strings_of(chord):
    return [s for s in (chord.first_note_string, chord.second_note_string, chord.third_note_string,
                        chord.fourth_note_string) if s]


class TestTables:
    def test_chord_types_have_valid_intervals(self, vs):
        for name, intervals in vs.chord_types.items():
            assert intervals[0] == 0, name
            assert intervals == sorted(set(intervals)), name
            assert len(intervals) in (3, 4)
            assert all(0 <= i < 12 for i in intervals)

    def test_string_sets_go_from_bass_to_treble_pitch_names(self, vs):
        assert vs.string_sets["e-b"] == ("bString", "gString", "dString", "eString")
        for key, strings in vs.string_sets.items():
            assert len(strings) == len(set(strings)), key

    def test_default_category(self):
        assert VoicingSystem().category_id == 1


class TestV1:
    def test_cmaj7_close_position(self, vs):
        chord = vs.generate_v1_voicing(0, "Major 7", "e-b")
        assert (chord.type_name, chord.chord_name, chord.range, chord.tonal_root) == ("V1", "Major 7", "e-b", 0)
        assert notes_of(chord) == [0, 4, 7, 11]
        assert strings_of(chord) == ["bString", "gString", "dString", "eString"]
        assert ChordPosition.objects.filter(notes_name=chord).count() == 4

    def test_triad_uses_three_strings(self, vs):
        chord = vs.generate_v1_voicing(0, "Major", "d-E")
        assert notes_of(chord) == [0, 4, 7]
        assert strings_of(chord) == ["ELowString", "AString", "dString"]
        assert chord.fourth_note is None

    @pytest.mark.xfail(strict=True, reason="BUG: a V1 triad from VoicingSystem gets no ChordPosition rows because create_base_position requires 4 notes for type V1 (V2 triads do get 3)")
    def test_triad_gets_inversion_positions(self, vs):
        chord = vs.generate_v1_voicing(0, "Major", "d-E")
        assert ChordPosition.objects.filter(notes_name=chord).count() == 3

    def test_v2_triad_does_get_positions(self, vs):
        chord = vs.generate_v2_voicing(0, "Major", "d-E")
        assert ChordPosition.objects.filter(notes_name=chord).count() == 3

    @pytest.mark.parametrize("root", range(12))
    def test_every_root_has_the_same_pitch_class_set_as_chord_type(self, vs, root):
        chord = vs.generate_v1_voicing(root, "Dominant 7", "g-A")
        assert sorted(notes_of(chord)) == sorted((root + i) % 12 for i in vs.chord_types["Dominant 7"])

    def test_v1_notes_are_ascending(self, vs):
        for root in range(12):
            chord = vs.generate_v1_voicing(root, "Minor 7", "e-b")
            assert notes_of(chord) == sorted(notes_of(chord))

    def test_unknown_chord_type_raises(self, vs):
        with pytest.raises(ValueError, match="Unsupported chord type"):
            vs.generate_v1_voicing(0, "Wonky", "e-b")

    def test_unknown_string_set_raises(self, vs):
        with pytest.raises(ValueError, match="Unsupported string set"):
            vs.generate_v1_voicing(0, "Major 7", "nope")

    @pytest.mark.parametrize("key", ["highA-E", "e-lowB", "highA-lowB"])
    def test_eight_string_sets_are_skipped(self, vs, key):
        assert vs.generate_v1_voicing(0, "Major 7", key) is None
        assert ChordNotes.objects.count() == 0

    def test_position_creation_failure_still_returns_chord(self, vs):
        with mock.patch.object(v_system_generator, "create_base_position", side_effect=RuntimeError("x")):
            chord = vs.generate_v1_voicing(0, "Major 7", "e-b")
        assert chord.pk is not None

    def test_database_failure_is_reraised(self, vs):
        with mock.patch.object(ChordNotes.objects, "create", side_effect=RuntimeError("db down")):
            with pytest.raises(RuntimeError, match="db down"):
                vs.generate_v1_voicing(0, "Major 7", "e-b")

    def test_not_enough_strings_raises(self, vs):
        vs.chord_types["Big"] = [0, 2, 4, 5, 7]
        vs.string_sets["tiny"] = ("eString", "bString", "gString", "dString")
        with pytest.raises(ValueError, match="Not enough strings"):
            vs.generate_v1_voicing(0, "Big", "tiny")
        with pytest.raises(ValueError, match="Not enough strings"):
            vs.generate_v2_voicing(0, "Big", "tiny")

    def test_unsupported_note_count_raises_and_creates_nothing(self, vs):
        vs.chord_types["Dyad"] = [0, 7]
        with pytest.raises(ValueError, match="Unsupported number of notes"):
            vs.generate_v1_voicing(0, "Dyad", "e-b")
        with pytest.raises(ValueError, match="Unsupported number of notes"):
            vs.generate_v2_voicing(0, "Dyad", "e-b")
        assert ChordNotes.objects.count() == 0


class TestV2:
    def test_seventh_drop2_moves_second_highest_note_to_the_bass(self, vs):
        chord = vs.generate_v2_voicing(0, "Major 7", "e-b")
        assert chord.type_name == "V2"
        # close position C E G B -> drop the G: G C E B
        assert notes_of(chord) == [7, 0, 4, 11]

    def test_triad_drop2(self, vs):
        chord = vs.generate_v2_voicing(0, "Major", "e-b")
        assert notes_of(chord) == [4, 0, 7]

    @pytest.mark.parametrize("chord_type", ["Major 7", "Minor 7", "Minor 7b5", "Major", "Diminished"])
    def test_drop2_keeps_the_pitch_class_set(self, vs, chord_type):
        for root in (0, 5, 9):
            chord = vs.generate_v2_voicing(root, chord_type, "d-E")
            assert sorted(notes_of(chord)) == sorted((root + i) % 12 for i in vs.chord_types[chord_type])

    def test_errors_and_skips(self, vs):
        with pytest.raises(ValueError):
            vs.generate_v2_voicing(0, "Wonky", "e-b")
        with pytest.raises(ValueError):
            vs.generate_v2_voicing(0, "Major 7", "nope")
        assert vs.generate_v2_voicing(0, "Major 7", "highA-E") is None

    def test_position_creation_failure_still_returns_chord(self, vs):
        with mock.patch.object(v_system_generator, "create_base_position", side_effect=RuntimeError("x")):
            assert vs.generate_v2_voicing(0, "Major 7", "e-b").pk is not None

    def test_database_failure_is_reraised(self, vs):
        with mock.patch.object(ChordNotes.objects, "create", side_effect=RuntimeError("db down")):
            with pytest.raises(RuntimeError):
                vs.generate_v2_voicing(0, "Major 7", "e-b")


class TestBulkGenerators:
    def test_all_roots_v1_creates_twelve_distinct_chords(self, vs):
        chords = vs.generate_all_roots_v1("Minor 7", "e-b")
        assert len(chords) == 12
        assert sorted(c.tonal_root for c in chords) == list(range(12))

    def test_all_types_v1_creates_one_per_type(self, vs):
        chords = vs.generate_all_types_v1(0, "e-b")
        assert [c.chord_name for c in chords] == list(vs.chord_types)

    def test_all_types_v2_creates_one_per_type(self, vs):
        chords = vs.generate_all_types_v2(2, "g-A")
        assert [c.chord_name for c in chords] == list(vs.chord_types)
        assert {c.type_name for c in chords} == {"V2"}

    def test_all_roots_v2_covers_every_midi_note_from_c0_to_d4(self, vs):
        chords = vs.generate_all_roots_v2("Major 7", "e-b")
        assert len(chords) == 51
        assert [c.tonal_root for c in chords][:12] == list(range(12))
        assert set(c.tonal_root for c in chords) == set(range(12))

    def test_bulk_skips_return_none_entries_for_eight_string_sets(self, vs):
        assert vs.generate_all_roots_v1("Major 7", "highA-E") == [None] * 12
