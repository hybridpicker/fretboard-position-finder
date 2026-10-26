"""backup, create_full_dump, export_chord_data and import_data management commands.

Everything that touches the filesystem runs in a tmp dir; nothing touches the real dev DB.
"""

import json
import os
from io import StringIO
from unittest import mock

import pytest
from django.core.management import call_command

from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.models_chords import ChordNotes, ChordPosition


def run(*args, **kwargs):
    out = StringIO()
    result = call_command(*args, stdout=out, **kwargs)
    return out.getvalue(), result


@pytest.fixture
def in_tmp(tmp_path, monkeypatch):
    """Run the command with a tmp cwd, because several commands write to relative paths."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def sample_rows(db):
    category = NotesCategory.objects.create(category_name="Chords")
    Root.objects.create(name="C", pitch=0)
    Notes.objects.create(category=category, note_name="Major", second_note=4, third_note=7)
    v1 = ChordNotes.objects.create(
        category=category,
        type_name="V1",
        chord_name="Minor 7",
        range="b - d",
        first_note=0,
        second_note=3,
        third_note=7,
        fourth_note=10,
    )
    v2 = ChordNotes.objects.create(
        category=category,
        type_name="V2",
        chord_name="Major",
        range="b - d",
        first_note=0,
        second_note=4,
        third_note=7,
    )
    return v1, v2


# --------------------------------------------------------------------------- backup


class TestBackup:
    def test_calls_dumpdata_with_natural_keys_into_fixture_path(self):
        with mock.patch("positionfinder.management.commands.backup.call_command") as dump:
            out, _ = run("backup")
        expected = os.path.join("positionfinder", "fixtures", "databasedump.json")
        dump.assert_called_once_with(
            "dumpdata",
            "--natural-foreign",
            "--natural-primary",
            "--indent",
            "2",
            "--output",
            expected,
        )
        assert f"Backing up database to {expected}" in out
        assert f"Database backup complete: {expected}" in out


# --------------------------------------------------------------------------- create_full_dump


class TestCreateFullDump:
    def test_creates_fixtures_dir_and_dumps_all_positionfinder_models(self, in_tmp, sample_rows):
        out, _ = run("create_full_dump")
        path = in_tmp / "fixtures" / "full_database_dump.json"
        assert path.exists()
        assert "Created directory: fixtures" in out
        assert "Successfully created database dump" in out
        data = json.loads(path.read_text())
        models = {row["model"] for row in data}
        assert {
            "positionfinder.root",
            "positionfinder.notes",
            "positionfinder.notescategory",
            "positionfinder.chordnotes",
            "positionfinder.chordposition",
        } <= models
        assert sum(r["model"] == "positionfinder.chordnotes" for r in data) == 2
        assert all(r["model"].startswith("positionfinder.") for r in data)

    def test_dump_can_be_reloaded(self, in_tmp, sample_rows):
        run("create_full_dump", output="again.json")
        ChordNotes.objects.all().delete()
        assert ChordPosition.objects.count() == 0
        call_command("loaddata", str(in_tmp / "fixtures" / "again.json"), verbosity=0)
        assert ChordNotes.objects.count() == 2
        assert ChordPosition.objects.count() == 3 + 4

    def test_exclude_models(self, in_tmp, sample_rows):
        out, _ = run("create_full_dump", exclude=["ChordNotes", "ChordPosition"])
        data = json.loads((in_tmp / "fixtures" / "full_database_dump.json").read_text())
        assert not any(
            r["model"] in ("positionfinder.chordnotes", "positionfinder.chordposition")
            for r in data
        )
        assert "positionfinder.ChordNotes" not in out
        assert "positionfinder.Root" in out

    def test_indent_option(self, in_tmp, sample_rows):
        run("create_full_dump", indent=0, output="compact.json")
        text = (in_tmp / "fixtures" / "compact.json").read_text()
        run("create_full_dump", indent=8, output="wide.json")
        wide = (in_tmp / "fixtures" / "wide.json").read_text()
        assert len(wide) > len(text)
        assert "\n        " in wide

    def test_existing_file_is_renamed_to_timestamped_backup(self, in_tmp, sample_rows):
        run("create_full_dump", output="x.json")
        out, _ = run("create_full_dump", output="x.json")
        files = sorted(p.name for p in (in_tmp / "fixtures").iterdir())
        assert len(files) == 2
        assert "x.json" in files
        backups = [f for f in files if f != "x.json"]
        assert backups[0].startswith("x_") and backups[0].endswith(".json")
        assert "Created backup:" in out

    def test_reports_failure_when_no_file_is_produced(self, in_tmp, db):
        with mock.patch("positionfinder.management.commands.create_full_dump.call_command"):
            out, _ = run("create_full_dump")
        assert "Failed to create database dump" in out

    def test_other_app_label(self, in_tmp, db):
        out, _ = run("create_full_dump", app="contenttypes", output="ct.json")
        assert "contenttypes.ContentType" in out
        assert (in_tmp / "fixtures" / "ct.json").exists()

    def test_unknown_app_raises(self, in_tmp, db):
        with pytest.raises(LookupError):
            run("create_full_dump", app="nonexistent_app")


# --------------------------------------------------------------------------- export_chord_data


class TestExportChordData:
    def test_exports_chords_with_positions(self, in_tmp, sample_rows):
        out, _ = run("export_chord_data")
        data = json.loads((in_tmp / "fixtures" / "chord_data_dump.json").read_text())
        assert [r["model"] for r in data].count("positionfinder.chordnotes") == 2
        assert [r["model"] for r in data].count("positionfinder.chordposition") == 7
        assert "Found 2 chord notes" in out
        assert "Found 7 chord positions" in out
        assert "- V1: 1 chords" in out and "- V2: 1 chords" in out
        assert "Successfully exported data" in out

    def test_type_filter_limits_both_chords_and_positions(self, in_tmp, sample_rows):
        out, _ = run("export_chord_data", type="V1", output="v1.json")
        data = json.loads((in_tmp / "fixtures" / "v1.json").read_text())
        chords = [r for r in data if r["model"] == "positionfinder.chordnotes"]
        positions = [r for r in data if r["model"] == "positionfinder.chordposition"]
        assert [c["fields"]["type_name"] for c in chords] == ["V1"]
        assert len(positions) == 4
        assert {p["fields"]["notes_name"] for p in positions} == {chords[0]["pk"]}
        assert "Filtering chords by type: V1" in out
        assert "Chord types included" not in out

    def test_unknown_type_exports_empty_list(self, in_tmp, sample_rows):
        run("export_chord_data", type="V99", output="none.json")
        assert json.loads((in_tmp / "fixtures" / "none.json").read_text()) == []

    def test_pretty_flag_indents(self, in_tmp, sample_rows):
        run("export_chord_data", output="a.json")
        run("export_chord_data", output="b.json", pretty=True)
        compact = (in_tmp / "fixtures" / "a.json").read_text()
        pretty = (in_tmp / "fixtures" / "b.json").read_text()
        assert "\n" not in compact
        assert "\n    " in pretty
        assert json.loads(compact) == json.loads(pretty)

    def test_backup_copies_existing_file(self, in_tmp, sample_rows):
        run("export_chord_data", output="c.json")
        original = (in_tmp / "fixtures" / "c.json").read_text()
        out, _ = run("export_chord_data", output="c.json", backup=True)
        copies = [p for p in (in_tmp / "fixtures").iterdir() if p.name != "c.json"]
        assert len(copies) == 1
        assert copies[0].read_text() == original
        assert "Created backup" in out

    def test_without_backup_flag_existing_file_is_overwritten(self, in_tmp, sample_rows):
        run("export_chord_data", output="d.json")
        run("export_chord_data", output="d.json")
        assert [p.name for p in (in_tmp / "fixtures").iterdir()] == ["d.json"]

    def test_empty_database(self, in_tmp, db):
        out, _ = run("export_chord_data", output="empty.json")
        assert json.loads((in_tmp / "fixtures" / "empty.json").read_text()) == []
        assert "Found 0 chord notes" in out

    def test_roundtrip_restores_rows(self, in_tmp, sample_rows):
        run("export_chord_data", output="rt.json")
        ChordNotes.objects.all().delete()
        call_command("loaddata", str(in_tmp / "fixtures" / "rt.json"), verbosity=0)
        assert ChordNotes.objects.count() == 2
        assert ChordPosition.objects.count() == 7


# --------------------------------------------------------------------------- import_data


class TestImportData:
    def test_flushes_then_loads_the_merged_fixture(self):
        with mock.patch("positionfinder.management.commands.import_data.call_command") as inner:
            out, result = run("import_data")
        assert [c.args for c in inner.call_args_list] == [
            ("flush", "--noinput"),
            ("loaddata", "positionfinder/fixtures/databasedump.json"),
        ]
        assert "Flushing the database..." in out
        assert "Database flushed." in out
        assert json.loads(result) == {"message": "Successfully Loading initial data"}

    def test_flush_failure_aborts_before_loading(self):
        def fake(name, *a, **k):
            if name == "flush":
                raise RuntimeError("flush failed")

        with mock.patch(
            "positionfinder.management.commands.import_data.call_command", side_effect=fake
        ) as inner:
            with pytest.raises(RuntimeError, match="flush failed"):
                run("import_data")
        assert [c.args[0] for c in inner.call_args_list] == ["flush"]
