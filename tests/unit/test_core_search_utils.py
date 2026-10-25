"""Edge cases of search_utils not covered by the query-level tests."""

import pytest

from positionfinder.models import Root
from positionfinder.search_utils import (
    INVERSIONS,
    POSITIONS,
    QUALITIES,
    ROOT_NAME_TO_ID,
    best_fuzzy_match,
    fuzzy_find,
    get_root_id_from_name,
    parse_query,
    resolve_root,
)

# --------------------------------------------------------------------------- get_root_id_from_name


class TestGetRootIdFromName:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("C", 1),
            ("c", 1),
            ("Db", 2),
            ("C#", 3),
            ("D", 4),
            ("Eb", 5),
            ("D#", 6),
            ("E", 7),
            ("F", 8),
            ("Gb", 9),
            ("F#", 10),
            ("G", 11),
            ("Ab", 12),
            ("G#", 13),
            ("A", 14),
            ("Bb", 15),
            ("A#", 16),
            ("B", 17),
        ],
    )
    def test_every_root_name(self, name, expected):
        assert get_root_id_from_name(name) == expected

    def test_whitespace_and_case_are_normalised(self):
        assert get_root_id_from_name("  eB ") == 5
        assert get_root_id_from_name("f#") == 10

    def test_unicode_accidentals(self):
        assert get_root_id_from_name("C♯") == 3
        assert get_root_id_from_name("B♭") == 15

    @pytest.mark.parametrize("bad", [None, "", "H", "xyz"])
    def test_unknown_or_empty_returns_none(self, bad):
        assert get_root_id_from_name(bad) is None

    @pytest.mark.parametrize("name,same_as", [("E#", "F"), ("Fb", "E"), ("Cb", "B"), ("B#", "C")])
    def test_rare_spellings_map_to_the_natural_note(self, name, same_as):
        assert get_root_id_from_name(name) == ROOT_NAME_TO_ID[same_as]

    def test_ids_are_unique_and_dense(self):
        assert sorted(ROOT_NAME_TO_ID.values()) == list(range(1, 18))


# --------------------------------------------------------------------------- fuzzy helpers


class TestFuzzyFind:
    def test_exact_and_close_matches(self):
        assert fuzzy_find("chord", ["chord", "scale"]) == "chord"
        assert fuzzy_find("scal", ["chord", "scale"]) == "scale"

    def test_below_cutoff_returns_none(self):
        assert fuzzy_find("zzz", ["chord", "scale"]) is None

    def test_cutoff_is_respected(self):
        assert fuzzy_find("scal", ["scale"], cutoff=0.99) is None


class TestBestFuzzyMatch:
    def test_prefers_longest_adjacent_window(self):
        assert (
            best_fuzzy_match("a minor pentatonic scale", QUALITIES, case_sensitive=False)
            == "minor pentatonic"
        )

    def test_returns_original_casing_of_choice(self):
        assert best_fuzzy_match("DORIAN", QUALITIES, case_sensitive=False) == "dorian"

    def test_case_sensitive_mode_does_not_lowercase_query(self):
        assert best_fuzzy_match("dorian", ["dorian"], case_sensitive=True) == "dorian"
        assert best_fuzzy_match("DORIAN", ["dorian"], case_sensitive=True) is None

    def test_non_adjacent_pair_is_found(self):
        choices = ["minor pentatonic"]
        assert (
            best_fuzzy_match(
                "minor qqqqqqqqqqqq pentatonic", choices, cutoff=0.95, case_sensitive=False
            )
            == "minor pentatonic"
        )

    def test_non_adjacent_triplet_is_found(self):
        choices = ["aaaa bbbb cccc"]
        query = "aaaa xxxxxxxxxxxx bbbb yyyyyyyyyyyy cccc"
        assert (
            best_fuzzy_match(query, choices, cutoff=0.95, case_sensitive=False) == "aaaa bbbb cccc"
        )

    def test_no_match_returns_none(self):
        assert best_fuzzy_match("qqq zzz", ["dorian"], case_sensitive=False) is None

    def test_empty_query_returns_none(self):
        assert best_fuzzy_match("", QUALITIES) is None


# --------------------------------------------------------------------------- parse_query


class TestParseQueryTable:
    @pytest.mark.parametrize(
        "query,expected",
        [
            ("Gmaj7", ("G", "chord", "maj7", "", "basic position")),
            ("Abmin7", ("Ab", "chord", "min7", "", "basic position")),
            ("F#dim7", ("F#", "chord", "dim7", "", "basic position")),
            ("Em7b5", ("E", "chord", "m7b5", "", "basic position")),
            ("Cm", ("C", "chord", "minor", "", "basic position")),
            ("D dorian", ("D", "scale", "dorian", "", "basic position")),
            ("A minor pentatonic", ("A", "scale", "minor pentatonic", "", "basic position")),
            ("G major arpeggio", ("G", "arpeggio", "major", "", "basic position")),
            ("C dorian arpeggio", ("C", "arpeggio", "dorian", "", "basic position")),
            ("e harmonic minor", ("E", "scale", "harmonic minor", "", "basic position")),
            ("C major V3", ("C", "chord", "major", "V3", "basic position")),
            ("C major 1st inversion", ("C", "chord", "major", "", "1st inversion")),
        ],
    )
    def test_expected_tuple(self, query, expected):
        assert parse_query(query) == expected

    @pytest.mark.xfail(
        strict=True,
        reason="BUG: compact chord symbols 'Bbaug'/'Cdim' get type 'scale' because 'augmented'/'diminished' are in scale_terms",
    )
    @pytest.mark.parametrize("query", ["Bbaug", "Cdim"])
    def test_compact_aug_and_dim_symbols_are_chords(self, query):
        assert parse_query(query)[1] == "chord"

    @pytest.mark.parametrize("query,quality", [("Bbaug", "augmented"), ("Cdim", "diminished")])
    def test_compact_aug_and_dim_symbols_quality(self, query, quality):
        assert parse_query(query)[2] == quality

    def test_hyphens_are_treated_as_spaces(self):
        assert parse_query("A-minor-pentatonic")[2] == "minor pentatonic"

    def test_result_values_are_from_the_canonical_lists(self):
        for query in ["foo", "C maj", "Dsus4", "x y z", "all positions major"]:
            note, type_, quality, position, inversion = parse_query(query)
            assert type_ in ("chord", "scale", "arpeggio")
            assert (
                position == ""
                or position in POSITIONS
                or position.upper() in POSITIONS
                or position.lower() in [p.lower() for p in POSITIONS]
            )
            assert inversion.lower() in INVERSIONS

    def test_default_when_nothing_recognised(self):
        assert parse_query("???") == ("C", "chord", "major", "", "basic position")


# --------------------------------------------------------------------------- resolve_root


@pytest.fixture
def clean_cache():
    cache = resolve_root.__defaults__[0]
    cache.clear()
    yield cache
    cache.clear()


@pytest.mark.django_db
class TestResolveRoot:
    def test_exact_case_insensitive_match(self, clean_cache):
        c = Root.objects.create(name="C", pitch=0)
        assert resolve_root("c") == c

    def test_enharmonic_equivalent_is_found(self, clean_cache):
        db = Root.objects.create(name="Db", pitch=1)
        assert resolve_root("C#") == db

    def test_unicode_accidentals(self, clean_cache):
        eb = Root.objects.create(name="Eb", pitch=3)
        assert resolve_root("e♭") == eb

    def test_partial_match_fallback(self, clean_cache):
        sharp = Root.objects.create(name="C#", pitch=1)
        assert resolve_root("C") == sharp

    def test_unknown_returns_none(self, clean_cache):
        Root.objects.create(name="C", pitch=0)
        assert resolve_root("Q") is None

    def test_result_is_cached_including_negative_result(self, clean_cache):
        c = Root.objects.create(name="C", pitch=0)
        assert resolve_root("C") == c
        Root.objects.all().delete()
        assert resolve_root("C") == c  # served from cache
        assert resolve_root("Zz") is None
        Root.objects.create(name="Zz", pitch=0)
        assert resolve_root("Zz") is None  # None is cached too
        assert set(clean_cache) == {"C", "Zz"}

    def test_cache_hit_prints_diagnostic(self, clean_cache, capsys):
        Root.objects.create(name="C", pitch=0)
        resolve_root("C")
        capsys.readouterr()
        resolve_root("C")
        assert "CACHE HIT" in capsys.readouterr().out
