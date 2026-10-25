"""generate_vsystem and test_unused_files management commands."""

from io import StringIO
from unittest import mock

import pytest
from django.core.management import call_command

from positionfinder.models import NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition

MODULE = "positionfinder.management.commands.generate_vsystem.VoicingSystem"


def run(*args, **kwargs):
    out = StringIO()
    call_command(*args, stdout=out, **kwargs)
    return out.getvalue()


# --------------------------------------------------------------------------- generate_vsystem (real generator)


@pytest.fixture
def category_one(db):
    # the command uses VoicingSystem() whose default category id is 1
    return NotesCategory.objects.create(pk=1, category_name="V-System")


@pytest.mark.django_db
class TestGenerateVSystemReal:
    def test_specific_v1_chord(self, category_one):
        out = run("generate_vsystem", root=0, chord_type="Major 7")
        chord = ChordNotes.objects.get()
        assert (chord.type_name, chord.chord_name, chord.range, chord.tonal_root) == (
            "V1",
            "Major 7",
            "e-b",
            0,
        )
        assert "Generating V1 voicing for root=0, chord_type=Major 7, string_set=e-b" in out
        assert f"Created chord: {chord}" in out
        assert out.rstrip().endswith("Done!")
        assert ChordPosition.objects.filter(notes_name=chord).count() == 4

    def test_specific_v2_chord_via_option_string(self, category_one):
        out = run(
            "generate_vsystem",
            "--v-system",
            "V2",
            "--root",
            "7",
            "--chord-type",
            "Minor 7",
            "--string-set",
            "g-A",
        )
        chord = ChordNotes.objects.get()
        assert (chord.type_name, chord.range, chord.tonal_root) == ("V2", "g-A", 7)
        assert "Generating V2 voicing for root=7" in out

    def test_all_chord_types_for_a_root(self, category_one):
        out = run("generate_vsystem", root=2)
        assert ChordNotes.objects.count() == 13
        assert set(ChordNotes.objects.values_list("tonal_root", flat=True)) == {2}
        assert "Created 13 V1 chords" in out

    def test_all_roots_for_a_chord_type(self, category_one):
        out = run("generate_vsystem", chord_type="Dominant 7")
        assert sorted(ChordNotes.objects.values_list("tonal_root", flat=True)) == list(range(12))
        assert "Created 12 V1 chords" in out

    def test_v2_all_chord_types_for_a_root(self, category_one):
        out = run("generate_vsystem", v_system="v2", root=0)
        assert ChordNotes.objects.filter(type_name="V2").count() == 13
        assert "Created 13 V2 chords" in out

    def test_clean_removes_existing_v_system_chords_only(self, category_one):
        other = ChordNotes.objects.create(
            category=category_one,
            type_name="Triads",
            chord_name="Major",
            range="e - g",
            first_note=0,
            second_note=4,
            third_note=7,
        )
        old = ChordNotes.objects.create(
            category=category_one,
            type_name="V2",
            chord_name="Major",
            range="b - d",
            first_note=0,
            second_note=4,
            third_note=7,
        )
        out = run("generate_vsystem", clean=True, root=0, chord_type="Major 7")
        assert not ChordNotes.objects.filter(pk=old.pk).exists()
        assert ChordNotes.objects.filter(pk=other.pk).exists()
        assert "Cleaning existing V-System chords..." in out
        assert "Deleted" in out
        assert ChordNotes.objects.filter(type_name="V1", chord_name="Major 7").count() == 1

    def test_eight_string_set_reports_warning(self, category_one):
        out = run("generate_vsystem", root=0, chord_type="Major 7", string_set="highA-E")
        assert "Failed to create chord for highA-E" in out
        assert ChordNotes.objects.count() == 0

    def test_invalid_chord_type_reports_error_instead_of_raising(self, category_one):
        out = run("generate_vsystem", root=0, chord_type="Nope")
        assert "Error creating chord: Unsupported chord type: Nope" in out
        assert out.rstrip().endswith("Done!")

    def test_invalid_chord_type_for_v2(self, category_one):
        out = run("generate_vsystem", v_system="v2", root=0, chord_type="Nope")
        assert "Error creating chord: Unsupported chord type: Nope" in out

    def test_unknown_system_only_says_done(self, category_one):
        out = run("generate_vsystem", v_system="v9")
        assert out.strip() == "Done!"
        assert ChordNotes.objects.count() == 0


# --------------------------------------------------------------------------- generate_vsystem (mocked generator)


def fake_system():
    vs = mock.MagicMock()
    vs.chord_types = {"Major 7": [0, 4, 7, 11], "Minor 7": [0, 3, 7, 10]}
    vs.generate_all_roots_v1.return_value = [object(), None, object()]
    vs.generate_all_roots_v2.return_value = [object(), None, object()]
    vs.generate_all_types_v1.return_value = [object(), None]
    vs.generate_all_types_v2.return_value = [None, None]
    vs.generate_v1_voicing.return_value = None
    vs.generate_v2_voicing.return_value = None
    return vs


@pytest.mark.django_db
class TestGenerateVSystemMocked:
    def test_full_v1_run_iterates_chord_types_and_filters_none(self):
        vs = fake_system()
        with mock.patch(MODULE, return_value=vs):
            out = run("generate_vsystem")
        assert [c.args for c in vs.generate_all_roots_v1.call_args_list] == [
            ("Major 7", "e-b"),
            ("Minor 7", "e-b"),
        ]
        assert "Created 4 V1 chords" in out  # 2 per type, None entries filtered
        vs.generate_all_roots_v2.assert_not_called()

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: the V1 branch of 'all' rebinds the loop variable chord_type, so the V2 branch then only generates the last chord type",
    )
    def test_all_without_filters_generates_every_chord_type_for_both_systems(self):
        vs = fake_system()
        with mock.patch(MODULE, return_value=vs):
            out = run("generate_vsystem", v_system="all")
        assert "Created 4 V1 chords" in out
        assert "Created 4 V2 chords" in out
        assert vs.generate_all_roots_v2.call_count == 2

    def test_all_without_filters_currently_runs_v2_only_for_the_last_chord_type(self):
        vs = fake_system()
        with mock.patch(MODULE, return_value=vs):
            out = run("generate_vsystem", v_system="all")
        assert "Created 4 V1 chords" in out
        assert [c.args for c in vs.generate_all_roots_v2.call_args_list] == [("Minor 7", "e-b")]

    def test_root_only_passes_root_and_string_set(self):
        vs = fake_system()
        with mock.patch(MODULE, return_value=vs):
            out = run("generate_vsystem", v_system="all", root=5, string_set="d-E")
        vs.generate_all_types_v1.assert_called_once_with(5, "d-E")
        vs.generate_all_types_v2.assert_called_once_with(5, "d-E")
        assert "Created 1 V1 chords" in out
        assert "Created 0 V2 chords" in out

    def test_chord_type_only_for_v2(self):
        vs = fake_system()
        with mock.patch(MODULE, return_value=vs):
            out = run("generate_vsystem", v_system="v2", chord_type="Major 7")
        vs.generate_all_roots_v2.assert_called_once_with("Major 7", "e-b")
        assert "Created 2 V2 chords" in out

    @pytest.mark.parametrize(
        "kwargs,method,label",
        [
            (
                {"v_system": "v1", "root": 1},
                "generate_all_types_v1",
                "Error generating V1 voicings: kaput",
            ),
            (
                {"v_system": "v1", "chord_type": "Major 7"},
                "generate_all_roots_v1",
                "Error generating V1 voicings: kaput",
            ),
            (
                {"v_system": "v2", "root": 1},
                "generate_all_types_v2",
                "Error generating V2 voicings: kaput",
            ),
            (
                {"v_system": "v2", "chord_type": "Major 7"},
                "generate_all_roots_v2",
                "Error generating V2 voicings: kaput",
            ),
        ],
    )
    def test_bulk_errors_are_reported_not_raised(self, kwargs, method, label):
        vs = fake_system()
        getattr(vs, method).side_effect = RuntimeError("kaput")
        with mock.patch(MODULE, return_value=vs):
            out = run("generate_vsystem", **kwargs)
        assert label in out
        assert out.rstrip().endswith("Done!")

    @pytest.mark.parametrize(
        "v_system,method", [("v1", "generate_all_roots_v1"), ("v2", "generate_all_roots_v2")]
    )
    def test_full_run_error_is_reported(self, v_system, method):
        vs = fake_system()
        getattr(vs, method).side_effect = RuntimeError("kaput")
        with mock.patch(MODULE, return_value=vs):
            out = run("generate_vsystem", v_system=v_system)
        assert f"Error generating {v_system.upper()} voicings: kaput" in out

    def test_specific_chord_success_message_uses_returned_chord(self):
        vs = fake_system()
        vs.generate_v2_voicing.return_value = "CHORD-OBJ"
        with mock.patch(MODULE, return_value=vs):
            out = run("generate_vsystem", v_system="v2", root=0, chord_type="Major 7")
        assert "Created chord: CHORD-OBJ" in out

    def test_v_system_option_is_case_insensitive(self):
        vs = fake_system()
        with mock.patch(MODULE, return_value=vs):
            run("generate_vsystem", v_system="V1", root=0, chord_type="Major 7")
        vs.generate_v1_voicing.assert_called_once_with(0, "Major 7", "e-b")


# --------------------------------------------------------------------------- test_unused_files

JS_NAMES = ["base_fixed.js", "c_major_fix.js", "debug-helpers.js", "root_note_fix.js"]


@pytest.fixture
def static_dir(tmp_path, settings):
    settings.BASE_DIR = str(tmp_path)
    js = tmp_path / "static" / "js"
    css = tmp_path / "static" / "css"
    js.mkdir(parents=True)
    css.mkdir(parents=True)
    for name in JS_NAMES + ["keep_me.js"]:
        (js / name).write_text(f"// {name}")
    (css / "site.css").write_text("body{}")
    return tmp_path / "static"


class TestUnusedFilesCommand:
    def test_default_hides_known_unused_js_only(self, static_dir):
        out = run("test_unused_files")
        remaining = sorted(p.name for p in (static_dir / "js").iterdir())
        assert remaining == ["keep_me.js"]
        assert sorted(p.name for p in (static_dir / "backup_js").iterdir()) == sorted(JS_NAMES)
        assert (static_dir / "css" / "site.css").exists()
        assert "Hidden 4 js files" in out
        assert "Hidden 0 css files" in out
        assert "Temporarily hidden: base_fixed.js" in out
        assert "--restore" in out

    def test_hide_only_css_leaves_js_alone(self, static_dir):
        out = run("test_unused_files", hide="css")
        assert len(list((static_dir / "js").iterdir())) == 5
        assert "Hidden 0 css files" in out
        assert "js files" not in out

    def test_hide_nothing(self, static_dir):
        out = run("test_unused_files", hide="")
        assert len(list((static_dir / "js").iterdir())) == 5
        assert "Hidden" not in out

    def test_restore_moves_files_back(self, static_dir):
        run("test_unused_files")
        out = run("test_unused_files", restore=True)
        assert sorted(p.name for p in (static_dir / "js").iterdir()) == sorted(
            JS_NAMES + ["keep_me.js"]
        )
        assert list((static_dir / "backup_js").iterdir()) == []
        assert "Restored 4 JS files and 0 CSS files" in out

    def test_restore_handles_css_backup_files(self, static_dir):
        (static_dir / "backup_css").mkdir()
        (static_dir / "backup_css" / "old.css").write_text("x")
        out = run("test_unused_files", restore=True)
        assert (static_dir / "css" / "old.css").exists()
        assert "Restored 0 JS files and 1 CSS files" in out

    def test_restore_ignores_subdirectories_in_backup(self, static_dir):
        (static_dir / "backup_js").mkdir()
        (static_dir / "backup_js" / "nested").mkdir()
        out = run("test_unused_files", restore=True)
        assert "Restored 0 JS files" in out
        assert (static_dir / "backup_js" / "nested").is_dir()

    def test_backup_dirs_are_created_when_missing(self, static_dir):
        assert not (static_dir / "backup_js").exists()
        run("test_unused_files", hide="css")
        assert (static_dir / "backup_js").is_dir()
        assert (static_dir / "backup_css").is_dir()

    def test_hide_then_hide_again_is_a_noop(self, static_dir):
        run("test_unused_files")
        out = run("test_unused_files")
        assert "Hidden 0 js files" in out


@pytest.mark.django_db
def test_specific_v2_chord_on_eight_string_set_warns(category_one):
    out = run("generate_vsystem", v_system="v2", root=0, chord_type="Major 7", string_set="highA-E")
    assert "Failed to create chord for highA-E" in out
    assert ChordNotes.objects.count() == 0


@pytest.mark.django_db
def test_full_v2_run_counts_all_chords_and_filters_none():
    vs = fake_system()
    with mock.patch(MODULE, return_value=vs):
        out = run("generate_vsystem", v_system="v2")
    assert [c.args for c in vs.generate_all_roots_v2.call_args_list] == [
        ("Major 7", "e-b"),
        ("Minor 7", "e-b"),
    ]
    assert "Created 4 V2 chords" in out
    vs.generate_all_roots_v1.assert_not_called()
