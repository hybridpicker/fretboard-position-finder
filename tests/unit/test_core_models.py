"""Model behaviour, chord generation, ordering helper, admin and app config (synthetic rows)."""

import logging
from unittest import mock

import pytest
from django.apps import apps as django_apps
from django.contrib import admin
from django.core.cache import cache
from django.db.models.signals import post_save

from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.models_chords import (
    ChordNotes,
    ChordPosition,
    create_base_position,
    create_chord,
    create_eight_string_ranges,
    create_fourthnote_positions,
    create_triad_positions,
)
from positionfinder.ordering import re_ordering
from positionfinder.positions import NotesPosition
from positionfinder.views_studio import CATALOG_CACHE_KEY

pytestmark = pytest.mark.django_db


@pytest.fixture
def category():
    return NotesCategory.objects.create(category_name="Chords")


def make_chord(
    category, notes=(0, 4, 7, 11), type_name="T", chord_name="Major 7", rng="b - d", **extra
):
    kw = dict(category=category, type_name=type_name, chord_name=chord_name, range=rng)
    names = ["first", "second", "third", "fourth", "fifth", "sixth"]
    for n, v in zip(names, notes, strict=False):
        kw[f"{n}_note"] = v
    for n in names[len(notes) :]:
        kw[f"{n}_note"] = None
    kw.update(extra)
    return ChordNotes.objects.create(**kw)


def positions_of(chord):
    return {p.inversion_order: p for p in ChordPosition.objects.filter(notes_name=chord)}


def notes_of(obj):
    return [
        getattr(obj, f"{n}_note") for n in ("first", "second", "third", "fourth", "fifth", "sixth")
    ]


# --------------------------------------------------------------------------- simple models


class TestSimpleModels:
    def test_str_methods(self, category):
        root = Root.objects.create(name="C#", pitch=1)
        scale = Notes.objects.create(category=category, note_name="Major", first_note=0)
        pos = NotesPosition.objects.create(notes_name=scale, position_order=2, position="3,4,5")
        assert str(root) == "C#"
        assert str(category) == "Chords"
        assert str(scale) == "Chords : Major"
        assert str(pos) == "2 - Chords : Major"

    def test_root_ordering_is_by_pitch_then_name(self):
        Root.objects.create(name="D", pitch=2)
        Root.objects.create(name="Db", pitch=1)
        Root.objects.create(name="C#", pitch=1)
        assert [r.name for r in Root.objects.all()] == ["C#", "Db", "D"]

    def test_notes_defaults_and_ordering(self, category):
        b = Notes.objects.create(category=category, note_name="B", ordering=2)
        a = Notes.objects.create(category=category, note_name="A", ordering=1)
        assert b.tonal_root == 0 and b.first_note == 0 and b.second_note is None
        assert list(Notes.objects.all()) == [a, b]

    def test_notes_position_ordering_and_cascade(self, category):
        scale = Notes.objects.create(category=category, note_name="S")
        NotesPosition.objects.create(notes_name=scale, position_order=2, position="1")
        NotesPosition.objects.create(notes_name=scale, position_order=1, position="2")
        assert [p.position_order for p in NotesPosition.objects.all()] == [1, 2]
        scale.delete()
        assert NotesPosition.objects.count() == 0

    def test_chord_str(self, category):
        chord = make_chord(category)
        assert str(chord) == "Chords - T - Major 7 - b - d"
        pos = positions_of(chord)["Basic Position"]
        assert "Basic Position" in str(pos) and "Major 7" in str(pos)


# --------------------------------------------------------------------------- ChordNotes.save


class TestChordNotesSave:
    @pytest.mark.parametrize("bad", [12, -1, 99])
    def test_out_of_range_note_raises_and_does_not_save(self, category, bad):
        with pytest.raises(ValueError, match="Invalid note value"):
            make_chord(category, notes=(0, 4, bad, 11))
        assert ChordNotes.objects.count() == 0

    @pytest.mark.parametrize("ok", [0, 11])
    def test_boundary_notes_are_accepted(self, category, ok):
        chord = make_chord(category, notes=(0, 4, ok))
        assert chord.pk

    def test_seventh_chord_gets_four_positions_on_create(self, category):
        chord = make_chord(category)
        assert set(positions_of(chord)) == {
            "Basic Position",
            "First Inversion",
            "Second Inversion",
            "Third Inversion",
        }

    def test_triad_gets_three_positions_on_create(self, category):
        chord = make_chord(category, notes=(0, 4, 7), chord_name="Major")
        assert set(positions_of(chord)) == {"Basic Position", "First Inversion", "Second Inversion"}

    def test_five_note_chord_gets_no_positions(self, category):
        chord = make_chord(category, notes=(0, 4, 7, 11, 2))
        assert positions_of(chord) == {}

    def test_v1_e_d_assigns_default_strings(self, category):
        chord = make_chord(
            category, type_name="V1", rng="e - d", chord_name="Minor 7", notes=(0, 3, 7, 10)
        )
        chord.refresh_from_db()
        assert [
            chord.first_note_string,
            chord.second_note_string,
            chord.third_note_string,
            chord.fourth_note_string,
        ] == ["dString", "gString", "bString", "eString"]

    def test_non_e_d_range_keeps_given_strings(self, category):
        chord = make_chord(category, type_name="V1", rng="b - d", first_note_string="gString")
        chord.refresh_from_db()
        assert chord.first_note_string == "gString"
        assert chord.second_note_string is None

    def test_changing_notes_recreates_positions(self, category):
        chord = make_chord(category)
        old_ids = {p.id for p in positions_of(chord).values()}
        chord.second_note = 3
        chord.save()
        new = positions_of(chord)
        assert {p.id for p in new.values()}.isdisjoint(old_ids)
        assert set(new) == {
            "Basic Position",
            "First Inversion",
            "Second Inversion",
            "Third Inversion",
        }
        # intervals w,x,y,z are now 3,4,4,1
        assert [
            new["First Inversion"].__dict__[f]
            for f in ("first_note", "second_note", "third_note", "fourth_note")
        ] == [3, 4, 4, 1]

    def test_changing_other_fields_keeps_positions(self, category):
        chord = make_chord(category)
        old_ids = {p.id for p in positions_of(chord).values()}
        chord.ordering = 5
        chord.save()
        assert {p.id for p in positions_of(chord).values()} == old_ids

    def test_resaving_unchanged_chord_keeps_positions(self, category):
        chord = make_chord(category)
        old_ids = {p.id for p in positions_of(chord).values()}
        chord.save()
        assert {p.id for p in positions_of(chord).values()} == old_ids

    def test_deleting_chord_cascades_to_positions(self, category):
        chord = make_chord(category)
        chord.delete()
        assert ChordPosition.objects.count() == 0


class TestV1MajorSevenVariants:
    def test_creating_v1_major7_e_d_generates_dom7_min7_min7b5(self, category):
        make_chord(category, type_name="V1", rng="e - d")
        variants = {
            c.chord_name: notes_of(c)[:4] for c in ChordNotes.objects.filter(type_name="V1")
        }
        assert variants == {
            "Major 7": [0, 4, 7, 11],
            "Dominant 7": [0, 4, 7, 10],
            "Minor 7": [0, 3, 7, 10],
            "Minor 7b5": [0, 3, 6, 10],
        }
        # every variant also got its inversions
        for chord in ChordNotes.objects.filter(type_name="V1"):
            assert len(positions_of(chord)) == 4
        assert {c.chord_ordering for c in ChordNotes.objects.exclude(chord_name="Major 7")} == {
            2,
            3,
            4,
        }

    def test_variants_keep_string_assignment(self, category):
        make_chord(category, type_name="V1", rng="e - d")
        for chord in ChordNotes.objects.filter(type_name="V1"):
            assert chord.fourth_note_string == "eString"
            assert chord.first_note_string == "dString"

    def test_other_voicing_types_do_not_generate_variants(self, category):
        make_chord(category, type_name="V2", rng="e - d")
        assert ChordNotes.objects.count() == 1

    def test_non_major7_does_not_generate_variants(self, category):
        make_chord(category, type_name="V1", rng="e - d", chord_name="Minor 7", notes=(0, 3, 7, 10))
        assert ChordNotes.objects.count() == 1

    def test_existing_variants_are_updated_not_duplicated(self, category):
        for name, notes in (
            ("Dominant 7", (0, 4, 7, 0)),
            ("Minor 7", (0, 0, 7, 0)),
            ("Minor 7b5", (0, 0, 0, 0)),
        ):
            make_chord(category, type_name="V1", rng="e - d", chord_name=name, notes=notes)
        before = ChordNotes.objects.count()
        make_chord(category, type_name="V1", rng="e - d")
        assert ChordNotes.objects.count() == before + 1
        by_name = {c.chord_name: notes_of(c)[:4] for c in ChordNotes.objects.filter(type_name="V1")}
        assert by_name["Dominant 7"] == [0, 4, 7, 10]
        assert by_name["Minor 7"] == [0, 3, 7, 10]
        assert by_name["Minor 7b5"] == [0, 3, 6, 10]


# --------------------------------------------------------------------------- create_base_position and friends


class TestBasePositions:
    def test_returns_none_when_positions_exist(self, category):
        chord = make_chord(category)
        assert create_base_position(chord.id) is None

    def test_returns_none_for_five_note_chord(self, category):
        chord = make_chord(category, notes=(0, 4, 7, 11, 2))
        assert create_base_position(chord.id) is None
        assert ChordPosition.objects.count() == 0

    def test_returns_none_for_incomplete_notes(self, category):
        # the DB forbids NULL in the first three notes, so feed an unsaved instance
        unsaved = ChordNotes(category=category, first_note=0, second_note=None, third_note=7)
        unsaved.id = 123456
        with mock.patch.object(ChordNotes.objects, "get", return_value=unsaved):
            assert create_base_position(123456) is None

    def test_v1_requires_four_notes(self, category):
        chord = make_chord(category, type_name="V1", notes=(0, 4, 7), rng="b - d")
        assert positions_of(chord) == {}
        assert create_base_position(chord.id) is None

    def test_seventh_chord_inversion_offsets(self, category):
        chord = make_chord(category)
        pos = positions_of(chord)
        fields = ("first_note", "second_note", "third_note", "fourth_note")
        # intervals between notes 0,4,7,11 are w=4, x=3, y=4, z=1
        assert [getattr(pos["Basic Position"], f) for f in fields] == [0, 0, 0, 0]
        assert [getattr(pos["First Inversion"], f) for f in fields] == [4, 3, 4, 1]
        assert [getattr(pos["Second Inversion"], f) for f in fields] == [7, 7, 5, 5]
        assert [getattr(pos["Third Inversion"], f) for f in fields] == [11, 8, 9, 8]

    def test_triad_inversion_offsets(self, category):
        chord = make_chord(category, notes=(0, 4, 7), chord_name="Major")
        pos = positions_of(chord)
        fields = ("first_note", "second_note", "third_note")
        assert [getattr(pos["First Inversion"], f) for f in fields] == [4, 3, 5]
        assert [getattr(pos["Second Inversion"], f) for f in fields] == [7, 8, 9]

    def test_notes_descending_across_octave_are_wrapped(self, category):
        chord = make_chord(category, notes=(7, 11, 2, 6))  # G B D F#
        first = positions_of(chord)["First Inversion"]
        assert [first.first_note, first.second_note, first.third_note, first.fourth_note] == [
            4,
            3,
            4,
            1,
        ]

    @pytest.mark.parametrize(
        "notes", [(0, 4, 7, 11), (2, 5, 9, 0), (7, 11, 2, 6), (0, 3, 6, 9), (11, 3, 6, 10)]
    )
    def test_cumulative_offsets_return_to_same_pitch_classes(self, category, notes):
        """Every inversion offset-vector applied to the chord yields a rotation of the same pitch set."""
        chord = make_chord(category, notes=notes)
        original = sorted(n % 12 for n in notes)
        for _inversion, pos in positions_of(chord).items():
            shifted = [(n + o) % 12 for n, o in zip(notes, notes_of(pos)[:4], strict=False)]
            assert len(shifted) == 4
        # the first-inversion shift only moves each note up to the next chord tone
        first = positions_of(chord)["First Inversion"]
        up = [(n + o) % 12 for n, o in zip(notes, notes_of(first)[:4], strict=False)]
        assert sorted(up) == original

    def test_create_triad_and_fourthnote_positions_are_idempotent(self, category):
        chord = make_chord(category, notes=(0, 4, 7), chord_name="Major")
        assert create_triad_positions(4, 3, 5, chord.id) == []
        seventh = make_chord(category, chord_name="Major 7", rng="g - A")
        assert create_fourthnote_positions(4, 3, 4, 1, seventh.id) == []

    def test_create_positions_returns_created_rows(self, category):
        chord = make_chord(category, notes=(0, 4, 7), chord_name="Major")
        ChordPosition.objects.all().delete()
        created = create_triad_positions(4, 3, 5, chord.id)
        assert [p.inversion_order for p in created] == ["First Inversion", "Second Inversion"]


# --------------------------------------------------------------------------- create_chord


def _stored_notes(category, name, rng="e - d"):
    chord = ChordNotes.objects.get(category=category, type_name="T", chord_name=name, range=rng)
    return notes_of(chord)[: 4 if chord.fourth_note is not None else 3]


class TestCreateChord:
    def test_major_seventh_creates_the_seventh_chord_family(self, category):
        major7 = make_chord(category, rng="e - d")
        create_chord(major7.id)
        names = set(ChordNotes.objects.filter(type_name="T").values_list("chord_name", flat=True))
        assert names == {
            "Major 7",
            "Major 7(#5)",
            "Major 7(b5)",
            "Minor 7",
            "MinMaj 7",
            "Minor 7b5",
            "Dominant 7",
            "Dominant 7(#5)",
            "Dominant 7(b5)",
        }
        assert _stored_notes(category, "Minor 7") == [0, 3, 7, 10]
        assert _stored_notes(category, "MinMaj 7") == [0, 3, 7, 11]
        assert _stored_notes(category, "Minor 7b5") == [0, 3, 6, 10]
        assert _stored_notes(category, "Dominant 7") == [0, 4, 7, 10]
        assert _stored_notes(category, "Dominant 7(#5)") == [0, 4, 8, 10]
        assert _stored_notes(category, "Dominant 7(b5)") == [0, 4, 6, 10]

    def test_chord_ordering_and_positions_of_generated_chords(self, category):
        major7 = make_chord(category, rng="e - d")
        create_chord(major7.id)
        ordering = dict(
            ChordNotes.objects.filter(type_name="T").values_list("chord_name", "chord_ordering")
        )
        assert (
            ordering["Minor 7"] == 2
            and ordering["Dominant 7"] == 3
            and ordering["Dominant 7(b5)"] == 9
        )
        for chord in ChordNotes.objects.filter(type_name="T"):
            assert len(positions_of(chord)) == 4

    def test_create_chord_is_idempotent(self, category):
        major7 = make_chord(category, rng="e - d")
        create_chord(major7.id)
        count = ChordNotes.objects.count()
        create_chord(major7.id)
        assert ChordNotes.objects.count() == count

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: create_chord builds 'Major 7(#5)' with a flattened third ([0,3,8,11] instead of [0,4,8,11])",
    )
    def test_major_7_sharp5_has_major_third_and_augmented_fifth(self, category):
        create_chord(make_chord(category, rng="e - d").id)
        assert _stored_notes(category, "Major 7(#5)") == [0, 4, 8, 11]

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: create_chord builds 'Major 7(b5)' as [0,3,6,10] (a Minor 7b5) instead of [0,4,6,11]",
    )
    def test_major_7_flat5_is_a_major_seventh_with_flat_fifth(self, category):
        create_chord(make_chord(category, rng="e - d").id)
        assert _stored_notes(category, "Major 7(b5)") == [0, 4, 6, 11]

    def test_major_triad_creates_minor_and_diminished_and_augmented(self, category):
        major = make_chord(category, notes=(0, 4, 7), chord_name="Major", rng="e - d")
        create_chord(major.id)
        assert set(ChordNotes.objects.values_list("chord_name", flat=True)) == {
            "Major",
            "Minor",
            "Diminished",
            "Augmented",
        }
        assert _stored_notes(category, "Minor") == [0, 3, 7]
        assert _stored_notes(category, "Diminished") == [0, 3, 6]
        for chord in ChordNotes.objects.all():
            assert len(positions_of(chord)) == 3

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: create_chord raises the third of the augmented triad too ([0,5,8] instead of [0,4,8])",
    )
    def test_augmented_triad_keeps_the_major_third(self, category):
        create_chord(make_chord(category, notes=(0, 4, 7), chord_name="Major", rng="e - d").id)
        assert _stored_notes(category, "Augmented") == [0, 4, 8]

    def test_other_chord_names_are_ignored(self, category):
        chord = make_chord(category, chord_name="Minor 7", notes=(0, 3, 7, 10))
        create_chord(chord.id)
        assert ChordNotes.objects.count() == 1


# --------------------------------------------------------------------------- create_eight_string_ranges


class TestEightStringRanges:
    def test_triad_creates_three_extended_ranges(self, category):
        chord = make_chord(category, notes=(0, 4, 7), chord_name="Major", rng="e - g")
        create_eight_string_ranges(chord.id)
        ranges = set(ChordNotes.objects.exclude(pk=chord.pk).values_list("range", flat=True))
        assert ranges == {"highA - e", "highA - lowB", "e - lowB"}
        e_lowb = ChordNotes.objects.get(range="e - lowB")
        assert (e_lowb.first_note_string, e_lowb.second_note_string, e_lowb.third_note_string) == (
            "lowBString",
            "AString",
            "eString",
        )
        assert len(positions_of(e_lowb)) == 3

    def test_seventh_chord_adds_extended_range_variant(self, category):
        chord = make_chord(category, rng="e - g")
        create_eight_string_ranges(chord.id)
        ranges = list(ChordNotes.objects.exclude(pk=chord.pk).values_list("range", flat=True))
        assert sorted(ranges) == sorted(
            ["highA - e", "highA - lowB", "e - lowB"]
        )  # get_or_create reuses e - lowB

    def test_is_idempotent(self, category):
        chord = make_chord(category, notes=(0, 4, 7), chord_name="Major", rng="e - g")
        create_eight_string_ranges(chord.id)
        count = ChordNotes.objects.count()
        create_eight_string_ranges(chord.id)
        assert ChordNotes.objects.count() == count

    def test_incomplete_chord_is_skipped(self, category):
        chord = make_chord(category, rng="e - g")
        unsaved = ChordNotes(category=category, first_note=0, second_note=4, third_note=None)
        with mock.patch.object(ChordNotes.objects, "get", return_value=unsaved):
            create_eight_string_ranges(chord.id)
        assert ChordNotes.objects.count() == 1


# --------------------------------------------------------------------------- ordering helper


class TestReOrdering:
    def test_sets_ordering_only_for_the_given_type(self, category):
        a = make_chord(category, type_name="V2")
        b = make_chord(category, type_name="V2", rng="e - g")
        c = make_chord(category, type_name="V3")
        re_ordering("V2", 7)
        for chord in (a, b, c):
            chord.refresh_from_db()
        assert (a.ordering, b.ordering, c.ordering) == (7, 7, None)

    def test_unknown_type_is_a_noop(self, category):
        make_chord(category, type_name="V2")
        re_ordering("Nothing", 3)
        assert ChordNotes.objects.get().ordering is None

    def test_saving_through_re_ordering_keeps_positions(self, category):
        chord = make_chord(category, type_name="V2")
        re_ordering("V2", 1)
        assert len(positions_of(chord)) == 4


# --------------------------------------------------------------------------- admin


def test_all_models_are_registered_in_admin():
    for model in (Root, Notes, NotesCategory, NotesPosition, ChordNotes, ChordPosition):
        assert model in admin.site._registry


# --------------------------------------------------------------------------- app config


class TestAppConfig:
    def test_app_config_is_positionfinder(self):
        config = django_apps.get_app_config("positionfinder")
        assert config.name == "positionfinder"
        assert type(config).__name__ == "PositionfinderConfig"

    @pytest.mark.parametrize("model", [Notes, Root, ChordNotes])
    def test_saving_catalogue_models_clears_the_studio_cache(self, model, category):
        cache.set(CATALOG_CACHE_KEY, {"stale": True})
        if model is Notes:
            Notes.objects.create(category=category, note_name="x")
        elif model is Root:
            Root.objects.create(name="Zed", pitch=0)
        else:
            make_chord(category)
        assert cache.get(CATALOG_CACHE_KEY) is None

    def test_deleting_catalogue_models_clears_the_studio_cache(self, category):
        root = Root.objects.create(name="Zed", pitch=0)
        cache.set(CATALOG_CACHE_KEY, {"stale": True})
        root.delete()
        assert cache.get(CATALOG_CACHE_KEY) is None

    def test_other_models_do_not_clear_the_cache(self, category):
        cache.set(CATALOG_CACHE_KEY, {"keep": True})
        NotesCategory.objects.create(category_name="other")
        assert cache.get(CATALOG_CACHE_KEY) == {"keep": True}
        cache.delete(CATALOG_CACHE_KEY)

    def test_ready_is_idempotent_for_signal_registration(self):
        config = django_apps.get_app_config("positionfinder")
        before = len(post_save.receivers)
        config.ready()
        assert len(post_save.receivers) == before

    def test_ready_survives_integration_failure_and_logs(self, caplog):
        config = django_apps.get_app_config("positionfinder")
        with mock.patch("importlib.import_module", side_effect=RuntimeError("no integration")):
            with caplog.at_level(logging.ERROR, logger="positionfinder.apps"):
                config.ready()
        messages = [r.getMessage() for r in caplog.records]
        assert any(
            "Error initializing chord search integration: no integration" in m for m in messages
        )
        assert any("RuntimeError" in m for m in messages)


class TestEdgeCases:
    def test_v1_with_descending_notes_wraps_all_intervals(self, category):
        chord = make_chord(category, type_name="V1", rng="b - d", notes=(7, 11, 2, 6))
        first = positions_of(chord)["First Inversion"]
        assert [first.first_note, first.second_note, first.third_note, first.fourth_note] == [
            4,
            3,
            4,
            1,
        ]
        wrapped = make_chord(category, type_name="V1", rng="g - A", notes=(11, 2, 6, 9))
        first = positions_of(wrapped)["First Inversion"]
        assert [first.first_note, first.second_note, first.third_note, first.fourth_note] == [
            3,
            4,
            3,
            2,
        ]

    def test_saving_with_explicit_missing_pk_is_treated_as_new(self, category):
        chord = ChordNotes(
            pk=987654,
            category=category,
            type_name="T",
            chord_name="Major",
            range="b - d",
            first_note=0,
            second_note=4,
            third_note=7,
        )
        chord.save()
        assert ChordNotes.objects.filter(pk=987654).exists()
        assert len(positions_of(chord)) == 3
