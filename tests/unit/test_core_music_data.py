"""Property and value tests for the core positionfinder helpers using the real music fixture."""

import pytest

from positionfinder.functionality_tones_setup import (
    get_all_notes_functionality,
    get_all_notes_functionality_optional,
    get_functionality_note_names,
    get_functionality_pitches,
    get_functionality_tones,
    get_notes_object,
    get_tension_final_list,
)
from positionfinder.get_position import get_notes_position
from positionfinder.get_position_dict_chords import get_position_dict
from positionfinder.get_position_dict_scales import get_scale_position_dict
from positionfinder.improved_chord_search import (
    CHORD_QUALITY_MAP,
    improved_search_chords,
    process_improved_chord_results,
)
from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.note_setup import build_notes, get_notes_tones
from positionfinder.positions import NotesPosition
from positionfinder.root_chord_note_setup import get_root_note as get_chord_root_note
from positionfinder.root_note_setup import get_root_note
from positionfinder.template_notes import (
    INVERSIONS,
    NOTE_NAMES,
    NOTE_NAMES_SHARP,
    NOTES,
    NOTES_SHARP,
    OCTAVES,
    STRING_NOTE_OPTIONS,
    TENSIONS,
)

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("music_data")]

C_ROOT_ID, G_ROOT_ID, CSHARP_ROOT_ID, DB_ROOT_ID = 1, 11, 3, 2
NOTE_FIELDS = ["first_note", "second_note", "third_note", "fourth_note", "fifth_note", "sixth_note"]


def pitch_class(tone):
    """Pitch class of a tone name such as 'ds3' or 'bb2' (octave digits are ignored)."""
    name = tone.rstrip("-0123456789")
    return NOTES.index(name) if name in NOTES else NOTES_SHARP.index(name)


def fret_of(string, tone):
    entry = STRING_NOTE_OPTIONS[string][0][tone[:-1]][0]
    return entry["fret"][entry["tone"].index(tone)]


def chord_strings(chord):
    return {
        getattr(chord, f"{n}_string")
        for n in (
            "first_note",
            "second_note",
            "third_note",
            "fourth_note",
            "fifth_note",
            "sixth_note",
        )
        if getattr(chord, n) is not None
    }


# --------------------------------------------------------------------------- fixture sanity


def test_fixture_counts():
    assert Root.objects.count() == 17
    assert NotesCategory.objects.count() == 3
    assert Notes.objects.count() == 46
    assert ChordNotes.objects.count() == 236
    assert ChordPosition.objects.count() == 904


def test_every_chord_has_a_basic_position_and_matching_note_count():
    for chord in ChordNotes.objects.all():
        positions = list(ChordPosition.objects.filter(notes_name=chord))
        order = [p.inversion_order for p in positions]
        assert "Basic Position" in order, chord
        assert len(order) == len(set(order)), chord
        n_notes = sum(getattr(chord, f) is not None for f in NOTE_FIELDS)
        for p in positions:
            filled = sum(getattr(p, f) is not None for f in NOTE_FIELDS)
            assert filled == n_notes, (chord, p.inversion_order)
            assert all(
                0 <= getattr(chord, f) <= 11 for f in NOTE_FIELDS if getattr(chord, f) is not None
            )


def test_basic_position_is_all_zero_offsets():
    for p in ChordPosition.objects.filter(inversion_order="Basic Position"):
        assert all(getattr(p, f) in (0, None) for f in NOTE_FIELDS)


# --------------------------------------------------------------------------- get_position_dict (chords)

ROOT_CASES = [(0, "C"), (1, "Db"), (6, "F#"), (7, "G"), (9, "A"), (11, "B")]


def _all_chord_position_pairs():
    return [
        (c, p) for c in ChordNotes.objects.all() for p in ChordPosition.objects.filter(notes_name=c)
    ]


def test_every_chord_position_is_resolvable_and_uses_the_chord_strings():
    pairs = _all_chord_position_pairs()
    assert len(pairs) == 904
    for chord, pos in pairs:
        d = get_position_dict(
            pos.inversion_order, chord.chord_name, chord.range, chord.type_name, 0, 0, "C"
        )
        assert d, (chord.id, pos.inversion_order)
        assigned = d["assigned_strings"]
        assert set(assigned) <= chord_strings(chord)
        assert set(d) == set(assigned) | {"assigned_strings"}
        for string in assigned:
            tone, tension, is_assigned, is_root = d[string]
            assert is_assigned is True
            assert tension in TENSIONS
            assert is_root == (tension == "R")


def test_every_position_is_playable_within_the_fretboard():
    for chord, pos in _all_chord_position_pairs():
        d = get_position_dict(
            pos.inversion_order, chord.chord_name, chord.range, chord.type_name, 0, 0, "C"
        )
        for string in d["assigned_strings"]:
            tone = d[string][0]
            assert tone[-1].isdigit(), (chord.id, string, tone)
            assert 0 <= fret_of(string, tone) <= 17


@pytest.mark.parametrize("root_pitch,root_name", ROOT_CASES)
def test_transposing_the_root_shifts_every_pitch_class_by_the_same_amount(root_pitch, root_name):
    """Transposition is consistent: pitch classes at root r == pitch classes at root 0 shifted by r."""
    for chord, pos in _all_chord_position_pairs()[::7]:
        base = get_position_dict(
            pos.inversion_order, chord.chord_name, chord.range, chord.type_name, 0, 0, "C"
        )
        moved = get_position_dict(
            pos.inversion_order,
            chord.chord_name,
            chord.range,
            chord.type_name,
            root_pitch,
            0,
            root_name,
        )
        assert base["assigned_strings"] == moved["assigned_strings"]
        for string in base["assigned_strings"]:
            assert pitch_class(moved[string][0]) == (pitch_class(base[string][0]) + root_pitch) % 12
            # the function of the note (R, 3, 5, ...) does not depend on the root
            assert moved[string][1] == base[string][1]
            assert moved[string][3] == base[string][3]


def test_transposing_by_zero_is_identity_and_deterministic():
    chord = ChordNotes.objects.filter(type_name="V1", chord_name="Major 7", range="e - d").get()
    a = get_position_dict("Basic Position", "Major 7", "e - d", "V1", 0, 0, "C")
    b = get_position_dict("Basic Position", "Major 7", "e - d", "V1", 0, 0, "C")
    assert a == b
    assert chord.first_note == 0


def test_cmaj7_v1_basic_position_exact_values():
    d = get_position_dict("Basic Position", "Major 7", "e - d", "V1", 0, 0, "C")
    assert d == {
        "dString": ["c2", "R", True, True],
        "gString": ["e2", "3", True, False],
        "bString": ["g2", "5", True, False],
        "eString": ["b2", "7", True, False],
        "assigned_strings": ["dString", "gString", "bString", "eString"],
    }


def test_sharp_root_name_selects_sharp_spellings_and_flat_name_flats():
    sharp = get_position_dict("Basic Position", "Major 7", "e - d", "V1", 1, 0, "C#")
    assert [sharp[s][0] for s in sharp["assigned_strings"]] == ["cs2", "f2", "gs2", "c3"]
    flat = get_position_dict("Basic Position", "Major 7", "e - d", "V1", 1, 0, "Db")
    assert [flat[s][0] for s in flat["assigned_strings"]] == ["db2", "f2", "ab2", "c3"]


def test_unknown_chord_returns_empty_dict():
    assert get_position_dict("Basic Position", "Nonexistent", "e - d", "V1", 0, 0, "C") == {}


def test_unknown_inversion_name_raises_value_error():
    with pytest.raises(ValueError):
        get_position_dict("Bogus Inversion", "Major 7", "e - d", "V1", 0, 0, "C")


def test_inversion_beyond_available_positions_returns_empty_dict():
    # triads only have 3 stored positions
    assert get_position_dict("Fourth Inversion", "Major", "e - g", "Triads", 0, 0, "C") == {}
    assert INVERSIONS.index("Fourth Inversion") == 4


def test_triad_dict_has_three_notes():
    d = get_position_dict("Basic Position", "Major", "e - g", "Triads", 0, 0, "C")
    assert sorted(d[s][1] for s in d["assigned_strings"]) == ["3", "5", "R"]
    assert d == {
        "gString": ["e2", "3", True, False],
        "bString": ["g2", "5", True, False],
        "eString": ["c3", "R", True, True],
        "assigned_strings": ["gString", "bString", "eString"],
    }


# --------------------------------------------------------------------------- get_notes_position


def test_get_notes_position_adds_root_pitch():
    pos = NotesPosition.objects.get(notes_name_id=10, position_order=1)
    assert pos.position == "3,4,5,6"
    assert get_notes_position(pos.id, 0) == [3, 4, 5, 6]
    assert get_notes_position(pos.id, 2) == [5, 6, 7, 8]


def test_get_notes_position_drops_an_octave_when_beyond_fret_17():
    pos = NotesPosition.objects.get(notes_name_id=10, position_order=3)
    assert pos.position == "8,9,10,11"
    assert get_notes_position(pos.id, 5) == [13, 14, 15, 16]
    assert get_notes_position(pos.id, 7) == [3, 4, 5, 6]  # 15..18 does not fit, so one octave down
    assert get_notes_position(pos.id, 11) == [7, 8, 9, 10]


def test_get_notes_position_always_stays_on_the_fretboard():
    for pos in NotesPosition.objects.all():
        for root in range(12):
            frets = get_notes_position(pos.id, root)
            assert len(frets) == len(pos.position.split(","))
            assert max(frets) <= 17
            assert min(frets) >= 0, (pos.id, root, frets)


def test_get_notes_position_is_congruent_to_root_shift_mod_octave():
    for pos in NotesPosition.objects.all()[::5]:
        base = [int(x) for x in pos.position.split(",")]
        for root in range(12):
            frets = get_notes_position(pos.id, root)
            assert [(f - b - root) % 12 for f, b in zip(frets, base, strict=False)] == [0] * len(
                base
            )


def test_get_notes_position_unknown_id_raises():
    with pytest.raises(NotesPosition.DoesNotExist):
        get_notes_position(10**9, 0)


# --------------------------------------------------------------------------- get_scale_position_dict


def _fret_for(string, tone):
    return fret_of(string, tone)


def test_scale_dict_by_name_has_open_position_and_all_fretted_positions():
    d = get_scale_position_dict("Major", C_ROOT_ID, 0, 0, "C")
    scale = Notes.objects.get(note_name="Major")
    positions = NotesPosition.objects.filter(notes_name=scale)
    assert set(d) == {"0"} | {str(p.position_order) for p in positions}
    for entry in d.values():
        assert set(entry) == set(STRING_NOTE_OPTIONS)
        assert all(len(v) == 1 and "tones" in v[0] for v in entry.values())


def test_scale_dict_resolves_numeric_string_id_like_name():
    by_id = get_scale_position_dict(
        str(Notes.objects.get(note_name="Major").id), C_ROOT_ID, 0, 0, "C"
    )
    by_name = get_scale_position_dict("Major", C_ROOT_ID, 0, 0, "C")
    assert by_id == by_name


@pytest.mark.parametrize(
    "scale_name,root_id,root_pitch,root_name",
    [
        ("Major", 1, 0, "C"),
        ("Major", 11, 7, "G"),
        ("Minor Pentatonic", 14, 9, "A"),
        ("Harmonic Minor", 3, 1, "C#"),
        ("Whole Tone", 15, 10, "Bb"),
    ],
)
def test_scale_dict_tones_belong_to_the_scale_and_to_the_position(
    scale_name, root_id, root_pitch, root_name
):
    scale = Notes.objects.get(note_name=scale_name)
    intervals = {
        getattr(scale, f)
        for f in (
            "first_note",
            "second_note",
            "third_note",
            "fourth_note",
            "fifth_note",
            "sixth_note",
            "seventh_note",
            "eigth_note",
            "ninth_note",
            "tenth_note",
            "eleventh_note",
            "twelth_note",
        )
        if getattr(scale, f) is not None
    }
    allowed = {(i + root_pitch) % 12 for i in intervals}
    d = get_scale_position_dict(scale_name, root_id, root_pitch, 0, root_name)
    for key, strings in d.items():
        for string, cell in strings.items():
            for tone in cell[0]["tones"]:
                assert pitch_class(tone) in allowed
                if key != "0":
                    pos = NotesPosition.objects.get(notes_name=scale, position_order=int(key))
                    assert _fret_for(string, tone) in get_notes_position(pos.id, root_pitch)
    # the open (position 0) dict contains every available tone of the scale
    covered = {pitch_class(t) for cell in d["0"].values() for t in cell[0]["tones"]}
    assert covered == allowed


def test_scale_dict_sharp_root_uses_sharp_names():
    sharp = get_scale_position_dict("Major", CSHARP_ROOT_ID, 1, 0, "C#")
    flat = get_scale_position_dict("Major", DB_ROOT_ID, 1, 0, "Db")
    sharp_tones = {t for c in sharp["0"].values() for t in c[0]["tones"]}
    flat_tones = {t for c in flat["0"].values() for t in c[0]["tones"]}
    assert any(t.startswith("cs") for t in sharp_tones)
    assert any(t.startswith("db") for t in flat_tones)
    assert {pitch_class(t) for t in sharp_tones} == {pitch_class(t) for t in flat_tones}


def test_scale_dict_partial_name_fallback_uses_icontains():
    d = get_scale_position_dict("harmonic min", 1, 0, 0, "C")
    assert d == get_scale_position_dict("Harmonic Minor", 1, 0, 0, "C")


def test_scale_dict_tail_of_name_fallback():
    # "A Minor Pentatonic" is not a name, the tail "Minor Pentatonic" is
    d = get_scale_position_dict("A Minor Pentatonic", 14, 9, 0, "A")
    assert d == get_scale_position_dict("Minor Pentatonic", 14, 9, 0, "A")


def test_scale_dict_unknown_scale_raises():
    with pytest.raises(Notes.DoesNotExist):
        get_scale_position_dict("Zzz Qqq", 1, 0, 0, "C")
    with pytest.raises(Notes.DoesNotExist):
        get_scale_position_dict("Nothing", 1, 0, 0, "C")


def test_scale_dict_arpeggio_has_no_fretted_positions_but_open_tones():
    arp = Notes.objects.get(note_name="Major Triad")
    d = get_scale_position_dict(str(arp.id), 1, 0, 0, "C")
    assert set(d) == {"0"} | {
        str(p.position_order) for p in NotesPosition.objects.filter(notes_name=arp)
    }
    covered = {pitch_class(t) for cell in d["0"].values() for t in cell[0]["tones"]}
    assert covered == {0, 4, 7}


# --------------------------------------------------------------------------- note_setup


def test_build_notes_for_scale_chord_and_other():
    major = Notes.objects.get(note_name="Major")
    assert build_notes(major) == [0, 2, 4, 5, 7, 9, 11]
    assert build_notes(object()) == []


@pytest.mark.xfail(
    strict=True,
    reason="BUG: build_notes(ChordNotes) does not exclude the *_string fields, so string names leak into the note list",
)
def test_build_notes_for_chordnotes_returns_only_pitches():
    chord = ChordNotes.objects.filter(type_name="V1", chord_name="Major 7", range="e - d").get()
    assert build_notes(chord) == [0, 4, 7, 11]


def test_get_notes_tones_c_major_has_seven_names_per_octave():
    tones = get_notes_tones(Notes.objects.get(note_name="Major").id, 0, 0, C_ROOT_ID)
    assert len(tones) == len(OCTAVES) * 7
    assert {t.rstrip("-0123456789") for t in tones} == {"c", "d", "e", "f", "g", "a", "b"}
    # one full octave of each pitch for all six octave labels
    assert {t for t in tones if t.startswith("c")} == {f"c{o}" for o in OCTAVES}


def test_get_notes_tones_transposed_to_g_uses_sharp_f():
    tones = get_notes_tones(Notes.objects.get(note_name="Major").id, 7, 0, G_ROOT_ID)
    assert {t.rstrip("-0123456789") for t in tones} == {"g", "a", "b", "c", "d", "e", "fs"}


def test_get_notes_tones_flat_vs_sharp_root_spelling():
    major = Notes.objects.get(note_name="Major").id
    flat = {t.rstrip("-0123456789") for t in get_notes_tones(major, 1, 0, DB_ROOT_ID)}
    sharp = {t.rstrip("-0123456789") for t in get_notes_tones(major, 1, 0, CSHARP_ROOT_ID)}
    assert "db" in flat and "cs" in sharp
    assert "db" not in sharp and "cs" not in flat


@pytest.mark.xfail(
    strict=True,
    reason="BUG: ChordNotes fallback in get_notes_tones crashes because build_notes leaks *_string fields",
)
def test_get_notes_tones_accepts_chord_notes_primary_key():
    chord = ChordNotes.objects.filter(type_name="V1", chord_name="Major 7", range="e - d").get()
    tones = get_notes_tones(chord.id, 0, 0, C_ROOT_ID)
    assert {t.rstrip("-0123456789") for t in tones} == {"c", "e", "g", "b"}


def test_get_notes_tones_unknown_id_returns_empty_list():
    assert get_notes_tones(10**8, 0, 0, C_ROOT_ID) == []


def test_get_notes_tones_unknown_root_raises():
    with pytest.raises(Root.DoesNotExist):
        get_notes_tones(1, 0, 0, 10**8)


def test_get_notes_tones_large_tonal_root_branch():
    # tonal_root + root > 12 shifts the root down an octave and must still work
    tones = get_notes_tones(Notes.objects.get(note_name="Major").id, 11, 5, 17)
    assert len(tones) > 0


# --------------------------------------------------------------------------- root note lookups


@pytest.mark.parametrize(
    "root_pitch,root_id,name", [(0, 1, "c"), (7, 11, "g"), (9, 14, "a"), (4, 7, "e")]
)
def test_get_root_note_one_name_per_octave(root_pitch, root_id, name):
    result = get_root_note(root_pitch, 0, root_id)
    assert len(result) == len(OCTAVES)
    assert {r.rstrip("-0123456789") for r in result} == {name}
    assert {int(r.lstrip("abcdefgs")) if False else r[len(name) :] for r in result} == {
        str(o) for o in OCTAVES
    }


def test_get_root_note_sharp_and_flat_spelling():
    assert {r.rstrip("-0123456789") for r in get_root_note(1, 0, CSHARP_ROOT_ID)} == {"cs"}
    assert {r.rstrip("-0123456789") for r in get_root_note(1, 0, DB_ROOT_ID)} == {"db"}


def test_chord_root_note_variant_matches_after_dropping_wrapped_octave():
    """root_chord_note_setup skips the negative (wrapped) index that root_note_setup keeps."""
    for pitch in range(12):
        root = Root.objects.filter(pitch=pitch).order_by("id").first()
        old = get_root_note(pitch, 0, root.id)
        new = get_chord_root_note(pitch, 0, root.id)
        assert new == old[1:], (pitch, old, new)
        assert len(new) == len(OCTAVES) - 1
        assert len(old) == len(OCTAVES)


def test_chord_root_note_tonal_root_wraps_and_picks_sharps():
    # combined tonal root 14 -> 2 which is in SHARP_NOTES
    assert {r.rstrip("-0123456789") for r in get_chord_root_note(2, 12, 4)} == {"d"}
    assert {r.rstrip("-0123456789") for r in get_chord_root_note(1, 0, CSHARP_ROOT_ID)} == {"cs"}
    assert {r.rstrip("-0123456789") for r in get_chord_root_note(1, 0, DB_ROOT_ID)} == {"db"}
    # tonal_root + root == 12 is normalised to 0 by the >= branch
    assert {r.rstrip("-0123456789") for r in get_chord_root_note(11, 1, 17)} == {"b"}


def test_chord_root_note_unknown_root_raises():
    with pytest.raises(Root.DoesNotExist):
        get_chord_root_note(0, 0, 10**8)


# --------------------------------------------------------------------------- functionality tones


def test_get_notes_object_prefers_notes_then_chordnotes_then_none():
    assert get_notes_object(Notes.objects.get(note_name="Major").id).note_name == "Major"
    chord = ChordNotes.objects.first()
    assert get_notes_object(chord.id).pk == chord.pk
    assert get_notes_object(10**8) is None


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Major", ["R", "9", "3", "11", "5", "13", "7"]),
        ("Harmonic Minor", ["R", "9", "b3", "11", "5", "b13", "7"]),
        ("Minor Pentatonic", ["R", "b3", "11", "5", "b7"]),
        ("Dominant 7", ["R", "3", "5", "b7"]),
        ("Major Triad", ["R", "3", "5"]),
        ("Diminished 7", ["R", "b3", "#11", "13"]),
        ("Whole Tone", ["R", "9", "3", "#11", "b13", "b7"]),
        # 13 after b13 would clash, so the optional spelling bb7 is used
        ("Diminished", ["R", "9", "b3", "11", "#11", "b13", "bb7", "7"]),
    ],
)
def test_functionality_tones(name, expected):
    notes = Notes.objects.get(note_name=name)
    assert get_functionality_tones(notes.id, 0) == expected


def test_functionality_tones_never_repeats_a_label_and_is_root_independent():
    for notes in Notes.objects.all():
        tones = get_functionality_tones(notes.id, 0)
        assert len(tones) == len(build_notes(notes))
        assert len(set(tones)) == len(tones), notes.note_name
        assert tones[0] == "R"
        assert get_functionality_tones(notes.id, 5) == tones


def test_functionality_pitches_equal_functionality_tones():
    for notes in Notes.objects.all():
        assert get_functionality_pitches(notes.id, 0) == get_functionality_tones(notes.id, 0)


def test_functionality_for_unknown_id_is_empty():
    assert get_functionality_tones(10**8, 0) == []
    assert get_functionality_pitches(10**8, 0) == []
    assert get_functionality_note_names(10**8, 0, 0, C_ROOT_ID) == []


@pytest.mark.xfail(
    strict=True,
    reason="BUG: ChordNotes fallback in get_functionality_tones crashes because build_notes leaks *_string fields",
)
def test_functionality_for_chordnotes():
    chord = ChordNotes.objects.filter(type_name="V1", chord_name="Major 7", range="e - d").get()
    assert get_functionality_tones(chord.id, 0) == ["R", "3", "5", "7"]


def test_all_notes_functionality_sharp_vs_flat():
    assert get_all_notes_functionality(0, C_ROOT_ID) == NOTE_NAMES
    assert get_all_notes_functionality(1, CSHARP_ROOT_ID) == NOTE_NAMES_SHARP
    assert get_all_notes_functionality(1, DB_ROOT_ID) == NOTE_NAMES
    # G (pitch 7) is a "sharp" key even though its name carries no #
    assert get_all_notes_functionality(7, G_ROOT_ID) == NOTE_NAMES_SHARP
    assert get_all_notes_functionality_optional(0, C_ROOT_ID)[1] == "Db"
    assert get_all_notes_functionality_optional(1, CSHARP_ROOT_ID)[1] == "C#"
    assert get_all_notes_functionality_optional(7, G_ROOT_ID)[1] == "C#"


@pytest.mark.parametrize(
    "root_pitch,root_id,tonal,expected",
    [
        (0, 1, 0, ["C", "D", "E", "F", "G", "A", "B"]),
        (7, 11, 0, ["G", "A", "B", "C", "D", "E", "F#"]),
        (10, 15, 0, ["Bb", "C", "D", "Eb", "F", "G", "A"]),
        (2, 4, 0, ["D", "E", "F#", "G", "A", "B", "C#"]),
    ],
)
def test_functionality_note_names_major_scale(root_pitch, root_id, tonal, expected):
    major = Notes.objects.get(note_name="Major")
    assert get_functionality_note_names(major.id, root_pitch, tonal, root_id) == expected


def spelled_pitch_class(name):
    base = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[name[0]]
    return (base + name[1:].count("#") - name[1:].count("b")) % 12


@pytest.mark.parametrize("root_pitch,root_id", [(0, 1), (2, 4), (5, 8), (7, 11), (10, 15)])
def test_functionality_note_names_are_enharmonically_correct_for_every_scale(root_pitch, root_id):
    for notes in Notes.objects.filter(category__category_name="Scales"):
        offsets = build_notes(notes)
        result = get_functionality_note_names(notes.id, root_pitch, 0, root_id)
        assert [spelled_pitch_class(n) for n in result] == [
            (o + root_pitch) % 12 for o in offsets
        ], notes.note_name


def test_get_tension_final_list_substitutes_optional_name_on_duplicates():
    # two notes that fall on the same name -> second one uses the optional spelling
    flat = NOTE_NAMES
    optional = ["B#", "C#", "C##", "D#", "D##", "E#", "F#", "F##", "G#", "G##", "A#", "A##"]
    assert get_tension_final_list(0, [0, 0], flat, None, optional) == ["C", "B#"]
    # values >= 12 wrap around
    assert get_tension_final_list(5, [7, 2], flat, None, optional) == ["C", "G"]


# --------------------------------------------------------------------------- improved chord search


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("maj7", "Major 7"),
        ("min7", "Minor 7"),
        ("m7b5", "Minor 7b5"),
        ("7", "Dominant 7"),
        ("dim7", "Diminished 7"),
        ("+", "Augmented"),
    ],
)
def test_chord_quality_map_values(raw, expected):
    assert CHORD_QUALITY_MAP[raw] == expected


def test_search_with_position_filters_on_voicing_type():
    results = improved_search_chords("Gmaj7 V2")
    assert results
    assert {r["type"] for r in results} == {"V2"}
    assert all(r["name"] == "G Major 7" for r in results)
    assert all("root=11" in r["url"] for r in results)
    assert all(r["url"].endswith("&position_select=Basic+Position") for r in results)


def test_search_result_structure_and_url_contents():
    result = improved_search_chords("Gmaj7 V2")[0]
    chord = ChordNotes.objects.get(pk=result["id"])
    assert set(result) == {
        "id",
        "name",
        "type",
        "category",
        "positions",
        "notes",
        "intervals",
        "url",
        "range",
        "tonal_root",
    }
    assert result["category"] == "Chords"
    assert result["notes"] == [0, 4, 7, 11] or len(result["notes"]) == 4
    assert result["intervals"][0] == 0
    assert f"type_options_select={chord.type_name}" in result["url"]
    assert f"note_range={chord.range}" in result["url"]
    assert "Basic Position" in result["positions"]


def test_search_orders_voicing_types_numerically():
    results = improved_search_chords("C#min7")
    v_numbers = [
        int(r["type"][1:]) for r in results if r["type"].startswith("V") and r["type"][1:].isdigit()
    ]
    assert v_numbers == sorted(v_numbers)
    assert len(v_numbers) > 10


def test_spread_triad_query_only_returns_spread_triads_and_sorts_first():
    results = improved_search_chords("A Major Spread Triad")
    assert results
    assert {r["type"] for r in results} == {"Spread Triads"}
    assert all(r["name"].startswith("A ") for r in results)


def test_unknown_quality_falls_back_to_root_only_loose_search_without_error():
    # No "Diminished 7" chords in the fixture -> empty result, not an exception
    assert improved_search_chords("F dim7") == []


def test_blank_query_defaults_to_c_major():
    results = improved_search_chords("")
    assert results
    assert all(r["name"].startswith("C ") for r in results)


def test_error_in_search_is_swallowed(monkeypatch):
    import positionfinder.search_utils as su

    monkeypatch.setattr(su, "parse_query", lambda q: (_ for _ in ()).throw(RuntimeError("boom")))
    assert improved_search_chords("C major") == []


def test_process_results_uses_given_root_for_display():
    qs = ChordNotes.objects.filter(type_name="V1", chord_name="Major 7", range="e - d")
    [res] = process_improved_chord_results(qs, root_note="Eb")
    assert res["name"] == "Eb Major 7"
    assert "root=5" in res["url"]


def test_process_results_default_root_is_c_when_chord_root_unknown():
    qs = ChordNotes.objects.filter(type_name="V1", chord_name="Major 7", range="e - d")
    [res] = process_improved_chord_results(qs)
    assert res["name"] == "C Major 7"
    assert "root=1&" in res["url"]


def test_process_results_does_not_double_prefix_root():
    chord = ChordNotes.objects.filter(type_name="V1", chord_name="Major 7", range="e - d").get()
    ChordNotes.objects.filter(pk=chord.pk).update(chord_name="C Major 7")
    [res] = process_improved_chord_results(ChordNotes.objects.filter(pk=chord.pk), root_note="C")
    assert res["name"] == "C Major 7"


def test_process_results_priority_sorting():
    spread = ChordNotes.objects.filter(type_name="Spread Triads")[:1]
    v2 = ChordNotes.objects.filter(type_name="V2")[:1]
    v1 = ChordNotes.objects.filter(type_name="V1")[:1]
    triads_eg = ChordNotes.objects.filter(type_name="Triads", range="e - g")[:1]
    triads_bd = ChordNotes.objects.filter(type_name="Triads", range="b - d")[:1]
    other = ChordNotes.objects.filter(type_name="Triads", range="A - B")[:1]
    ids = [c.pk for qs in (other, triads_bd, triads_eg, v2, v1, spread) for c in qs]
    qs = ChordNotes.objects.filter(pk__in=ids)
    types = [(r["type"], r["range"]) for r in process_improved_chord_results(qs)]
    assert [t[0] for t in types] == ["Spread Triads", "V1", "V2", "Triads", "Triads", "Triads"]
    assert [t[1] for t in types][3:] == ["e - g", "b - d", "A - B"]


def test_process_results_skips_rows_that_fail_to_process():
    class Broken:
        id = 1

        def __getattr__(self, name):
            raise RuntimeError("broken row")

    class Rows:
        def __iter__(self):
            return iter([Broken()])

        def __len__(self):
            return 1

    assert process_improved_chord_results(Rows()) == []


# --------------------------------------------------------------------------- degenerate chord / scale data


@pytest.fixture
def scratch_category():
    return NotesCategory.objects.get(category_name="Chords")


def _scratch_chord(category, **kw):
    base = dict(
        category=category,
        type_name="Scratch",
        chord_name="Major",
        range="b - d",
        tonal_root=0,
        first_note=0,
        second_note=0,
        third_note=0,
    )
    base.update(kw)
    return ChordNotes.objects.create(**base)


def test_position_dict_uses_alternate_octave_when_frets_are_far_apart():
    # C on the e string is fret 8, C on the b string fret 1: more than 5 frets apart -> alternate octave
    cat = NotesCategory.objects.get(category_name="Chords")
    _scratch_chord(
        cat, first_note_string="eString", second_note_string="bString", third_note_string="gString"
    )
    d = get_position_dict("Basic Position", "Major", "b - d", "Scratch", 0, 0, "C")
    assert d["assigned_strings"] == ["eString", "bString", "gString"]
    # eString has a single "c" option so the alternate octave falls back to it
    assert d["eString"][0] == "c3"
    assert d["bString"][0] == "c3"  # second option (fret 13) instead of c2 (fret 1)
    assert d["gString"][0] == "c3" or d["gString"][0].startswith("c")


def test_position_dict_without_far_apart_frets_uses_first_octave():
    cat = NotesCategory.objects.get(category_name="Chords")
    _scratch_chord(
        cat, first_note_string="bString", second_note_string="gString", third_note_string="dString"
    )
    d = get_position_dict("Basic Position", "Major", "b - d", "Scratch", 0, 0, "C")
    assert d["bString"][0] == "c2"


def test_position_dict_ignores_notes_on_unknown_or_missing_strings():
    cat = NotesCategory.objects.get(category_name="Chords")
    _scratch_chord(
        cat, first_note_string=None, second_note_string="bogusString", third_note_string="bString"
    )
    d = get_position_dict("Basic Position", "Major", "b - d", "Scratch", 0, 0, "C")
    assert d == {"bString": ["c2", "R", True, True], "assigned_strings": ["bString"]}


def test_position_dict_chord_without_positions_is_empty():
    cat = NotesCategory.objects.get(category_name="Chords")
    chord = _scratch_chord(cat)
    ChordPosition.objects.filter(notes_name=chord).delete()
    assert get_position_dict("Basic Position", "Major", "b - d", "Scratch", 0, 0, "C") == {}


def test_scale_dict_with_repeated_interval_has_no_duplicate_tones():
    cat = NotesCategory.objects.get(category_name="Scales")
    scale = Notes.objects.create(
        category=cat, note_name="Octave Doubled", first_note=0, second_note=12, third_note=7
    )
    pos = NotesPosition.objects.create(notes_name=scale, position_order=1, position="3,4,5,6,7,8")
    d = get_scale_position_dict("Octave Doubled", C_ROOT_ID, 0, 0, "C")
    assert set(d) == {"0", "1"}
    for entry in d.values():
        for cell in entry.values():
            assert len(cell[0]["tones"]) == len(set(cell[0]["tones"]))
    assert {pitch_class(t) for c in d["0"].values() for t in c[0]["tones"]} == {0, 7}
    assert pos.id


# --------------------------------------------------------------------------- improved search: root filtering


def test_root_filter_prefers_chords_stored_with_the_matching_pitch():
    cat = NotesCategory.objects.get(category_name="Chords")
    g_chord = _scratch_chord(
        cat, type_name="V2", chord_name="Major 7", range="e - d", tonal_root=7, fourth_note=11
    )
    results = improved_search_chords("Gmaj7 V2")
    assert [r["id"] for r in results] == [g_chord.id]


def test_non_v_position_is_matched_against_type_name_text():
    cat = NotesCategory.objects.get(category_name="Chords")
    chord = _scratch_chord(
        cat, type_name="All Positions Voicing", chord_name="Major 7", fourth_note=11
    )
    results = improved_search_chords("C major 7 all positions")
    assert chord.id in [r["id"] for r in results]


def test_unmatched_position_falls_back_to_loose_search_on_chord_name():
    # no chord has type "V14 Spread", so the strict filter finds nothing and the loose search kicks in
    results = improved_search_chords("Dm7b5 all positions")
    assert results
    assert all(r["name"].startswith("D ") for r in results)
    assert {r["type"] for r in results} != {"all positions"}


def test_spread_triad_without_matching_chord_name_returns_empty():
    assert improved_search_chords("F dim7 spread triad") == []


def test_spread_triad_query_without_spread_chords_falls_back_to_plain_chord_name_search():
    ChordNotes.objects.filter(type_name="Spread Triads").update(chord_name="Weird")
    results = improved_search_chords("A Major Spread Triad")
    assert results
    assert "Spread Triads" not in {r["type"] for r in results}
    assert all(r["name"].startswith("A ") for r in results)


# --------------------------------------------------------------------------- improved search: remaining branches


class Rows:
    """Minimal queryset stand-in without .count() so process_improved_chord_results uses len()."""

    def __init__(self, *items):
        self.items = list(items)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


def _cmaj7_v1():
    return ChordNotes.objects.filter(type_name="V1", chord_name="Major 7", range="e - d").get()


def test_note_without_root_id_skips_root_filtering_and_defaults_to_c_url():
    results = improved_search_chords("Fbmaj7")
    assert results
    assert all(r["name"] == "Fb Major 7" for r in results)
    assert all("root=1&" in r["url"] for r in results)


def test_loose_search_narrows_by_root_pitch():
    cat = NotesCategory.objects.get(category_name="Chords")
    marker = _scratch_chord(
        cat, type_name="V2", chord_name="Major 7", range="e - d", tonal_root=7, fourth_note=11
    )
    # the strict pass finds nothing (no type contains "all positions"); the loose pass narrows by root pitch
    results = improved_search_chords("Gmaj7 all positions")
    assert [r["id"] for r in results] == [marker.id]


def test_loose_search_keeps_all_chord_name_matches_when_root_filter_is_empty():
    results = improved_search_chords("Gmaj7 all positions")
    assert len(results) == ChordNotes.objects.filter(chord_name__icontains="Major 7").count()


def test_precomputed_intervals_attribute_is_used():
    chord = _cmaj7_v1()
    chord.intervals = [0, 4, 7, 11, 14]
    [res] = process_improved_chord_results(Rows(chord), root_note="C")
    assert res["intervals"] == [0, 4, 7, 11, 14]


def test_single_note_chord_has_no_intervals():
    chord = _cmaj7_v1()
    chord.second_note = chord.third_note = chord.fourth_note = None
    [res] = process_improved_chord_results(Rows(chord), root_note="C")
    assert res["notes"] == [0]
    assert res["intervals"] == []


def test_intervals_are_relative_to_first_note_and_wrapped():
    chord = _cmaj7_v1()
    chord.first_note, chord.second_note, chord.third_note, chord.fourth_note = 7, 11, 2, 6
    [res] = process_improved_chord_results(Rows(chord), root_note="G")
    assert res["intervals"] == [0, 4, 7, 11]


def test_unknown_display_root_is_kept_but_url_uses_c_id():
    [res] = process_improved_chord_results(Rows(_cmaj7_v1()), root_note="Fb")
    assert res["name"] == "Fb Major 7"
    assert "root=1&" in res["url"]


def test_chord_without_tonal_root_and_without_user_root_defaults_to_c():
    chord = _cmaj7_v1()
    chord.tonal_root = None
    [res] = process_improved_chord_results(Rows(chord))
    assert res["name"] == "C Major 7"
    assert res["tonal_root"] is None


def test_display_root_is_derived_from_the_pitch_of_tonal_root():
    chord = _cmaj7_v1()
    chord.tonal_root = 5  # F
    [res] = process_improved_chord_results(Rows(chord))
    assert res["name"].startswith("F ")


def test_url_without_positions_has_no_position_param_and_root_position_fallback():
    chord = _cmaj7_v1()
    [with_basic] = process_improved_chord_results(Rows(chord), root_note="C")
    assert with_basic["url"].endswith("&position_select=Basic+Position")
    ChordPosition.objects.filter(notes_name=chord, inversion_order="Basic Position").delete()
    [no_basic] = process_improved_chord_results(Rows(chord), root_note="C")
    assert no_basic["url"].endswith("&position_select=Root+Position")
    ChordPosition.objects.filter(notes_name=chord).delete()
    [none] = process_improved_chord_results(Rows(chord), root_note="C")
    assert "position_select" not in none["url"]
    assert none["positions"] == []


def test_root_note_setup_tonal_root_above_octave_is_normalised():
    # root 1 (Db) + tonal_root 13 = 14 -> 2, a "sharp" key, so sharp spelling is used
    assert {r.rstrip("-0123456789") for r in get_root_note(1, 13, DB_ROOT_ID)} == {"cs"}
