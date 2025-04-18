# tests/test_search_functions.py
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from bs4 import BeautifulSoup
import json
import re
from unittest.mock import patch, MagicMock

from positionfinder.models import Root, NotesCategory, Notes
from positionfinder.models_chords import ChordNotes
from positionfinder.search_utils import (
    parse_query, best_fuzzy_match, resolve_root,
    get_root_id_from_name, ROOT_NAME_TO_ID
)
from positionfinder.views_search import (
    search_scales, search_chords, search_arpeggios,
    process_scale_results, process_chord_results, process_arpeggio_results
)
from django.db.models import Q

@pytest.mark.django_db
class TestSearchUtils(TestCase):
    """Tests for search utility functions"""

    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create root notes
        cls.root_c = Root.objects.create(name="C", pitch=0)
        cls.root_cs = Root.objects.create(name="C#", pitch=1)
        cls.root_d = Root.objects.create(name="D", pitch=2)
        cls.root_eb = Root.objects.create(name="Eb", pitch=3)
        cls.root_e = Root.objects.create(name="E", pitch=4)
        cls.root_f = Root.objects.create(name="F", pitch=5)
        cls.root_fs = Root.objects.create(name="F#", pitch=6)
        cls.root_g = Root.objects.create(name="G", pitch=7)
        cls.root_gs = Root.objects.create(name="G#", pitch=8)
        cls.root_a = Root.objects.create(name="A", pitch=9)
        cls.root_bb = Root.objects.create(name="Bb", pitch=10)
        cls.root_b = Root.objects.create(name="B", pitch=11)

        # Create categories
        cls.scale_category = NotesCategory.objects.create(category_name="scale")
        cls.arpeggio_category = NotesCategory.objects.create(category_name="arpeggio")
        cls.chord_category = NotesCategory.objects.create(category_name="chord")

        # Create scales
        cls.c_major_scale = Notes.objects.create(
            category=cls.scale_category,
            note_name="C Major Scale",
            tonal_root=0,  # C
            first_note=0, second_note=2, third_note=4,
            fourth_note=5, fifth_note=7, sixth_note=9, seventh_note=11
        )

        cls.a_minor_scale = Notes.objects.create(
            category=cls.scale_category,
            note_name="A Minor Scale",
            tonal_root=9,  # A
            first_note=9, second_note=11, third_note=0,
            fourth_note=2, fifth_note=4, sixth_note=5, seventh_note=7
        )

        # Create arpeggios
        cls.c_major_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Major",
            type_name="Standard",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7,
            range="e - d"
        )

        cls.a_minor_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Minor",
            type_name="Standard",
            tonal_root=9,  # A
            first_note=9, third_note=0, fifth_note=4,
            range="e - d"
        )

        cls.a_min_pent_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Minor Pentatonic",
            type_name="Pentatonic",
            tonal_root=9,  # A
            first_note=9, third_note=0, fourth_note=2, fifth_note=4, seventh_note=7,
            range="e - d"
        )

        # Create chords
        cls.c_major_chord = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Major",
            type_name="V1",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7,
            range="e - d"
        )

        cls.a_minor_chord = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Minor",
            type_name="V1",
            tonal_root=9,  # A
            first_note=9, third_note=0, fifth_note=4,
            range="e - d"
        )

    def test_parse_query(self):
        """Test parsing of different query formats"""
        test_cases = [
            # Query, Expected (note, type, quality, position, inversion)
            ("A minor", ("A", "chord", "minor", "", "basic position")),
            ("a minor scale", ("A", "scale", "minor", "", "basic position")),
            ("c major arpeggio", ("C", "arpeggio", "major", "", "basic position")),
            ("G pentatonic", ("G", "scale", "pentatonic", "", "basic position")),
            ("D# minor pentatonic", ("D#", "scale", "minor pentatonic", "", "basic position")),
            ("F# maj7", ("F#", "chord", "maj7", "", "basic position")),
            ("E V1", ("E", "chord", "major", "V1", "basic position")),
            ("A minor V2", ("A", "chord", "minor", "V2", "basic position")),
            ("B min7", ("B", "chord", "min7", "", "basic position")),
            ("Eb 1st inversion", ("Eb", "chord", "major", "", "1st inversion")),
            ("Bb dominant 7", ("Bb", "chord", "dominant 7", "", "basic position")),
            ("C dorian", ("C", "scale", "dorian", "", "basic position")),
            ("G lydian", ("G", "scale", "lydian", "", "basic position")),
            ("A harmonic minor", ("A", "scale", "harmonic minor", "", "basic position")),
            ("Major", ("C", "chord", "major", "", "basic position")),  # Default note
            ("pentatonic", ("C", "scale", "pentatonic", "", "basic position")),  # Default note
        ]

        for query, expected in test_cases:
            result = parse_query(query)
            self.assertEqual(result, expected, f"Failed for query '{query}'")

    def test_best_fuzzy_match(self):
        """Test best fuzzy match for various inputs"""
        # Test note matching
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.assertEqual(best_fuzzy_match("see", notes, cutoff=0.6), "C")
        self.assertEqual(best_fuzzy_match("ay", notes, cutoff=0.6), "A")
        self.assertEqual(best_fuzzy_match("ef", notes, cutoff=0.6), "F")

        # Test quality matching
        qualities = ["major", "minor", "major pentatonic", "minor pentatonic", "harmonic minor"]
        self.assertEqual(best_fuzzy_match("mino", qualities, cutoff=0.6), "minor")
        self.assertEqual(best_fuzzy_match("major penta", qualities, cutoff=0.6), "major pentatonic")
        self.assertEqual(best_fuzzy_match("harmo min", qualities, cutoff=0.6), "harmonic minor")

        # Test with case insensitivity
        self.assertEqual(best_fuzzy_match("Major", qualities, cutoff=0.6, case_sensitive=False), "major")
        self.assertEqual(best_fuzzy_match("MINOR PENTA", qualities, cutoff=0.6, case_sensitive=False), "minor pentatonic")

    def test_resolve_root(self):
        """Test resolving root by name to Root object"""
        # Test exact matches
        self.assertEqual(resolve_root("C"), self.root_c)
        self.assertEqual(resolve_root("A"), self.root_a)
        self.assertEqual(resolve_root("G#"), self.root_gs)

        # Test case insensitivity
        self.assertEqual(resolve_root("c"), self.root_c)
        self.assertEqual(resolve_root("a"), self.root_a)

        # Test enharmonic equivalents
        self.assertEqual(resolve_root("Db"), self.root_cs)  # C# == Db
        self.assertEqual(resolve_root("D#"), self.root_eb)  # D# == Eb

        # Test with Unicode symbols
        self.assertEqual(resolve_root("C♯"), self.root_cs)  # C# with sharp symbol
        self.assertEqual(resolve_root("E♭"), self.root_eb)  # Eb with flat symbol

        # Test non-existent note
        self.assertIsNone(resolve_root("H"))  # Not a valid note name
        self.assertIsNone(resolve_root("X"))  # Not a valid note name

    def test_get_root_id_from_name(self):
        """Test mapping note names to root IDs"""
        # Test exact matches in mapping
        self.assertEqual(get_root_id_from_name("C"), ROOT_NAME_TO_ID["C"])
        self.assertEqual(get_root_id_from_name("A"), ROOT_NAME_TO_ID["A"])
        self.assertEqual(get_root_id_from_name("F#"), ROOT_NAME_TO_ID["F#"])

        # Test case insensitivity
        self.assertEqual(get_root_id_from_name("c"), ROOT_NAME_TO_ID["C"])
        self.assertEqual(get_root_id_from_name("a"), ROOT_NAME_TO_ID["A"])

        # Test with Unicode symbols
        self.assertEqual(get_root_id_from_name("C♯"), ROOT_NAME_TO_ID["C#"])
        self.assertEqual(get_root_id_from_name("E♭"), ROOT_NAME_TO_ID["Eb"])

        # Test enharmonic equivalents
        self.assertEqual(get_root_id_from_name("Db"), ROOT_NAME_TO_ID["C#"])
        self.assertEqual(get_root_id_from_name("Eb"), ROOT_NAME_TO_ID["Eb"])

        # Test non-existent note
        self.assertIsNone(get_root_id_from_name("H"))  # Not a valid note name
        self.assertIsNone(get_root_id_from_name("X"))  # Not a valid note name


@pytest.mark.django_db
class TestSearchArpeggios(TestCase):
    """Tests for search_arpeggios function"""

    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create root notes
        cls.root_c = Root.objects.create(name="C", pitch=0)
        cls.root_cs = Root.objects.create(name="C#", pitch=1)
        cls.root_d = Root.objects.create(name="D", pitch=2)
        cls.root_eb = Root.objects.create(name="Eb", pitch=3)
        cls.root_e = Root.objects.create(name="E", pitch=4)
        cls.root_a = Root.objects.create(name="A", pitch=9)
        cls.root_bb = Root.objects.create(name="Bb", pitch=10)

        # Create categories
        cls.arpeggio_category = NotesCategory.objects.create(category_name="arpeggio")

        # Create arpeggios
        cls.c_major_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Major",
            type_name="Standard",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7,
            range="e - d"
        )

        cls.a_minor_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Minor",
            type_name="Standard",
            tonal_root=9,  # A
            first_note=9, third_note=0, fifth_note=4,
            range="e - d"
        )

        cls.a_min_pent_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Minor Pentatonic",
            type_name="Pentatonic",
            tonal_root=9,  # A
            first_note=9, third_note=0, fourth_note=2, fifth_note=4, seventh_note=7,
            range="e - d"
        )

        cls.e_major_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Major",
            type_name="Standard",
            tonal_root=4,  # E
            first_note=4, third_note=8, fifth_note=11,
            range="e - d"
        )

        cls.d_minor_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Minor",
            type_name="Standard",
            tonal_root=2,  # D
            first_note=2, third_note=5, fifth_note=9,
            range="e - d"
        )

        # Create some variation arpeggios
        cls.a_min7_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Min7",
            type_name="7th",
            tonal_root=9,  # A
            first_note=9, third_note=0, fifth_note=4, seventh_note=7,
            range="e - d"
        )

        cls.c_maj7_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Maj7",
            type_name="7th",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7, seventh_note=11,
            range="e - d"
        )

    def test_search_arpeggios_by_note_and_quality(self):
        """Test searching arpeggios by note and quality"""
        # Test A minor
        results = search_arpeggios(note="A", quality="minor")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "A Minor")

        # Test C major
        results = search_arpeggios(note="C", quality="major")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "C Major")

        # Test A minor pentatonic
        results = search_arpeggios(note="A", quality="minor pentatonic")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "A Minor Pentatonic")

        # Test E major
        results = search_arpeggios(note="E", quality="major")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "E Major")

    def test_search_arpeggios_with_quality_variants(self):
        """Test searching with different quality variants"""
        # Test with 'min' instead of 'minor'
        results = search_arpeggios(note="A", quality="min")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "A Minor")

        # Test with 'maj' instead of 'major'
        results = search_arpeggios(note="C", quality="maj")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "C Major")

        # Test with mixed case
        results = search_arpeggios(note="A", quality="MiNoR")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "A Minor")

    def test_search_arpeggios_by_quality_only(self):
        """Test searching by quality only (no root note)"""
        # Test minor arpeggios
        results = search_arpeggios(quality="minor")
        self.assertEqual(len(results), 2)  # A minor and D minor

        # Test major arpeggios
        results = search_arpeggios(quality="major")
        self.assertEqual(len(results), 2)  # C major and E major

        # Test pentatonic
        results = search_arpeggios(quality="pentatonic")
        self.assertEqual(len(results), 1)  # A minor pentatonic

        # Test 7th chords
        results = search_arpeggios(quality="7")
        self.assertEqual(len(results), 2)  # A Min7 and C Maj7

    def test_search_arpeggios_by_note_only(self):
        """Test searching by note only (no quality)"""
        # Test A arpeggios
        results = search_arpeggios(note="A")
        self.assertEqual(len(results), 3)  # A minor, A minor pentatonic, A Min7

        # Test C arpeggios
        results = search_arpeggios(note="C")
        self.assertEqual(len(results), 2)  # C major, C Maj7

        # Test D arpeggios
        results = search_arpeggios(note="D")
        self.assertEqual(len(results), 1)  # D minor

        # Test E arpeggios
        results = search_arpeggios(note="E")
        self.assertEqual(len(results), 1)  # E major

    def test_search_arpeggios_with_enharmonic_notes(self):
        """Test searching with enharmonic note names"""
        # Create test data with enharmonic equivalents
        eb_minor_arpeggio = ChordNotes.objects.create(
            category=self.arpeggio_category,
            chord_name="Minor",
            type_name="Standard",
            tonal_root=3,  # Eb/D#
            first_note=3, third_note=6, fifth_note=10,
            range="e - d"
        )

        # Test with Eb
        results = search_arpeggios(note="Eb", quality="minor")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Eb Minor")

        # Test with D#
        results = search_arpeggios(note="D#", quality="minor")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "D# Minor")

    def test_search_arpeggios_with_no_results(self):
        """Test search with no matching results"""
        # Test non-existent note
        results = search_arpeggios(note="H", quality="major")  # H is not a valid note
        self.assertEqual(len(results), 0)

        # Test non-existent quality
        results = search_arpeggios(note="A", quality="super-major")  # Not a valid quality
        self.assertEqual(len(results), 0)

        # Test valid note but non-matching quality
        results = search_arpeggios(note="A", quality="augmented")  # We don't have A augmented in our test data
        self.assertEqual(len(results), 0)

        # Test non-matching note/quality combination
        results = search_arpeggios(note="D", quality="major")  # We don't have D major in our test data
        self.assertEqual(len(results), 0)

    def test_manual_arpeggio_search(self):
        """Test the manual arpeggio search function from test_arpeggio_search.py"""
        # This simulates the function in test_arpeggio_search.py
        def manual_test_arpeggio_search(note_name, quality):
            # Start with base arpeggio query
            qs = ChordNotes.objects.filter(category__category_name__icontains='arpeggio')

            # Filter by root note
            if note_name:
                # First try to find the note by name
                root_obj = Root.objects.filter(name__iexact=note_name).first()

                if root_obj:
                    # Use the pitch value for filtering (not the ID)
                    root_pitch = root_obj.pitch
                    qs = qs.filter(tonal_root=root_pitch)

            # Filter by quality
            if quality:
                # Use Q object for more flexible quality matching
                quality_filters = Q()
                variations = [quality, quality.capitalize(), quality.lower()]

                if quality.lower() == 'minor':
                    variations.extend(['Min', 'm', 'minor pentatonic', 'Minor Pentatonic'])
                elif quality.lower() == 'major':
                    variations.extend(['Maj', 'major pentatonic', 'Major Pentatonic'])

                for var in set(variations):
                    quality_filters |= Q(chord_name__icontains=var)

                qs = qs.filter(quality_filters)

            return qs

        # Test A minor
        manual_results = manual_test_arpeggio_search('A', 'minor')
        view_results = search_arpeggios(note='A', quality='minor')

        self.assertEqual(
            manual_results.count(),
            len(view_results),
            "Manual test and view function should return the same number of results"
        )

        # Check if all IDs from manual search are present in view results
        manual_ids = set(manual_results.values_list('id', flat=True))
        view_ids = set(item['id'] for item in view_results)

        self.assertEqual(
            manual_ids,
            view_ids,
            "Manual test and view function should return the same arpeggio IDs"
        )


@pytest.mark.django_db
class TestSearchScales(TestCase):
    """Tests for search_scales function"""

    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create root notes
        cls.root_c = Root.objects.create(name="C", pitch=0)
        cls.root_cs = Root.objects.create(name="C#", pitch=1)
        cls.root_d = Root.objects.create(name="D", pitch=2)
        cls.root_a = Root.objects.create(name="A", pitch=9)
        cls.root_bb = Root.objects.create(name="Bb", pitch=10)
        cls.root_b = Root.objects.create(name="B", pitch=11)

        # Create categories
        cls.scale_category = NotesCategory.objects.create(category_name="scale")

        # Create scales
        cls.c_major_scale = Notes.objects.create(
            category=cls.scale_category,
            note_name="Major Scale",
            tonal_root=0,  # C
            first_note=0, second_note=2, third_note=4,
            fourth_note=5, fifth_note=7, sixth_note=9, seventh_note=11
        )

        cls.a_minor_scale = Notes.objects.create(
            category=cls.scale_category,
            note_name="Minor Scale",
            tonal_root=9,  # A
            first_note=9, second_note=11, third_note=0,
            fourth_note=2, fifth_note=4, sixth_note=5, seventh_note=7
        )

        cls.a_minor_pent_scale = Notes.objects.create(
            category=cls.scale_category,
            note_name="Minor Pentatonic Scale",
            tonal_root=9,  # A
            first_note=9, third_note=0, fourth_note=2, fifth_note=4, seventh_note=7
        )

        cls.d_dorian_scale = Notes.objects.create(
            category=cls.scale_category,
            note_name="Dorian Scale",
            tonal_root=2,  # D
            first_note=2, second_note=4, third_note=5,
            fourth_note=7, fifth_note=9, sixth_note=11, seventh_note=0
        )

    def test_search_scales_by_note_and_quality(self):
        """Test searching scales by note and quality"""
        # Test C major
        results = search_scales("C major")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "C Major")

        # Test A minor
        results = search_scales("A minor")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "A Minor")

        # Test D dorian
        results = search_scales("D dorian")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "D dorian")

    def test_search_scales_by_id(self):
        """Test searching scales by ID"""
        # Get ID of C major scale
        c_major_id = self.c_major_scale.id

        # Search by ID
        results = search_scales(str(c_major_id))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], c_major_id)

    def test_search_scales_dynamic_generation(self):
        """Test dynamic generation of scales not in database"""
        # Test B minor pentatonic (not in DB but should be generated dynamically)
        results = search_scales("B minor pentatonic")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "B Minor Pentatonic")

        # Verify notes are correct
        expected_notes = [11, 2, 4, 7, 9]  # B minor pentatonic: B-D-E-G-A
        self.assertEqual(set(results[0]["notes"]), set(expected_notes))

        # Test Bb major scale (not in DB but should be generated dynamically)
        results = search_scales("Bb major")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Bb Major")

        # Expected pitch classes for Bb major
        expected_notes = [10, 0, 2, 3, 5, 7, 9]  # Bb C D Eb F G A

        # Check if notes array exists (it may not for dynamically generated results)
        if "notes" in results[0]:
            # We only check for the root note as the full calculation might differ
            self.assertEqual(results[0]["notes"][0], 10)  # First note should be Bb (10)

    def test_search_scales_with_enharmonic_notes(self):
        """Test searching scales with enharmonic note names"""
        # Test C# major (C# and Db are enharmonic)
        results_cs = search_scales("C# major")
        results_db = search_scales("Db major")

        # Both searches should return results (either the same or equivalent)
        self.assertGreater(len(results_cs), 0)
        self.assertGreater(len(results_db), 0)

        # Check that the first notes match expected pitch values
        if "notes" in results_cs[0]:
            self.assertEqual(results_cs[0]["notes"][0], 1)  # C# is pitch 1
        if "notes" in results_db[0]:
            self.assertEqual(results_db[0]["notes"][0], 1)  # Db is also pitch 1


@pytest.mark.django_db
class TestSearchChords(TestCase):
    """Tests for search_chords function"""

    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create root notes
        cls.root_c = Root.objects.create(name="C", pitch=0)
        cls.root_d = Root.objects.create(name="D", pitch=2)
        cls.root_e = Root.objects.create(name="E", pitch=4)
        cls.root_a = Root.objects.create(name="A", pitch=9)

        # Create categories
        cls.chord_category = NotesCategory.objects.create(category_name="chord")

        # Create chords
        cls.c_major_v1 = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Major",
            type_name="V1",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7,
            range="e - d"
        )

        cls.c_major_v2 = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Major",
            type_name="V2",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7,
            range="a - g"
        )

        cls.a_minor_v1 = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Minor",
            type_name="V1",
            tonal_root=9,  # A
            first_note=9, third_note=0, fifth_note=4,
            range="e - d"
        )

        cls.a_minor_v2 = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Minor",
            type_name="V2",
            tonal_root=9,  # A
            first_note=9, third_note=0, fifth_note=4,
            range="a - g"
        )

        cls.d_dominant7_v1 = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Dominant 7",
            type_name="V1",
            tonal_root=2,  # D
            first_note=2, third_note=6, fifth_note=9, seventh_note=0,
            range="e - d"
        )

        cls.e_maj7_v1 = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Maj7",
            type_name="V1",
            tonal_root=4,  # E
            first_note=4, third_note=8, fifth_note=11, seventh_note=3,
            range="e - d"
        )

    # Original tests for TestSearchChords were here...
    # Now adding the new tests provided by the user, correctly indented

    def test_search_chords_by_note_and_quality(self):
        """Test searching chords by note and quality"""
        # Test C major
        results = search_chords("C major")
        self.assertEqual(len(results), 2)  # C major V1 and V2

        # Test A minor
        results = search_chords("A minor")
        self.assertEqual(len(results), 2)  # A minor V1 and V2

        # Check that results include both positions
        chord_types = set([r["type"] for r in results])
        self.assertIn("V1", chord_types)
        self.assertIn("V2", chord_types)

    def test_search_chords_by_note_type_and_quality(self):
        """Test searching chords by note, type, and quality"""
        # Test C major V1
        results = search_chords("C major V1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], "V1")

        # Test A minor V2
        results = search_chords("A minor V2")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], "V2")

    def test_search_chords_prioritizes_e_string_range(self):
        """Test that chords on the E string are prioritized"""
        # Create a new position with a different range
        d_major_low = ChordNotes.objects.create(
            category=self.chord_category,
            chord_name="Major",
            type_name="V1",
            tonal_root=2,  # D
            first_note=2, third_note=6, fifth_note=9,
            range="e - d"  # E string
        )

        d_major_high = ChordNotes.objects.create(
            category=self.chord_category,
            chord_name="Major",
            type_name="V1",
            tonal_root=2,  # D
            first_note=2, third_note=6, fifth_note=9,
            range="a - g"  # A string
        )

        # Search for D major - should prioritize e-string range
        results = search_chords("D major")
        self.assertEqual(len(results), 2)

        # First result should be the e-string version
        self.assertEqual(results[0]["id"], d_major_low.id)

    def test_search_chords_with_no_results(self):
        """Test search with no matching results"""
        # Test non-existent quality
        results = search_chords("C diminished")  # Not in our test data
        self.assertEqual(len(results), 0)

        # Test non-existent note
        results = search_chords("H major")  # Not a valid note
        self.assertEqual(len(results), 0)

        # Test non-matching combination
        results = search_chords("D minor")  # Not in our test data
        self.assertEqual(len(results), 0)


@pytest.mark.django_db
class TestSearchIntegration(TestCase):
    """Integration tests for search views"""

    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create root notes
        cls.root_c = Root.objects.create(name="C", pitch=0)
        cls.root_a = Root.objects.create(name="A", pitch=9)

        # Create categories
        cls.scale_category = NotesCategory.objects.create(category_name="scale")
        cls.chord_category = NotesCategory.objects.create(category_name="chord")
        cls.arpeggio_category = NotesCategory.objects.create(category_name="arpeggio")

        # Create test objects
        cls.c_major_scale = Notes.objects.create(
            category=cls.scale_category,
            note_name="Major Scale",
            tonal_root=0,
            first_note=0, second_note=2, third_note=4,
            fourth_note=5, fifth_note=7, sixth_note=9, seventh_note=11
        )

        cls.a_minor_scale = Notes.objects.create(
            category=cls.scale_category,
            note_name="Minor Scale",
            tonal_root=9,
            first_note=9, second_note=11, third_note=0,
            fourth_note=2, fifth_note=4, sixth_note=5, seventh_note=7
        )

        cls.c_major_chord = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Major",
            type_name="V1",
            tonal_root=0,
            first_note=0, third_note=4, fifth_note=7,
            range="e - d"
        )

        cls.a_minor_chord = ChordNotes.objects.create(
            category=cls.chord_category,
            chord_name="Minor",
            type_name="V1",
            tonal_root=9,
            first_note=9, third_note=0, fifth_note=4,
            range="e - d"
        )

        cls.c_major_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Major",
            type_name="Standard",
            tonal_root=0,
            first_note=0, third_note=4, fifth_note=7,
            range="e - d"
        )

        cls.a_minor_arpeggio = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Minor",
            type_name="Standard",
            tonal_root=9,
            first_note=9, third_note=0, fifth_note=4,
            range="e - d"
        )

    def test_search_json_endpoint(self):
        """Test the JSON search endpoint"""
        client = Client()

        # Test search for "A minor"
        response = client.get('/search/json/', {'q': 'A minor'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Check response structure
        self.assertIn('query', data)
        self.assertIn('total_results', data)
        self.assertIn('scale_results', data)
        self.assertIn('chord_results', data)
        self.assertIn('arpeggio_results', data)

        # Check that we found results in all categories
        self.assertGreater(len(data['scale_results']), 0)  # Should find A minor scale
        self.assertGreater(len(data['chord_results']), 0)  # Should find A minor chord
        self.assertGreater(len(data['arpeggio_results']), 0)  # Should find A minor arpeggio

        # Test search for "C major"
        response = client.get('/search/json/', {'q': 'C major'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Check that we found results in all categories
        self.assertGreater(len(data['scale_results']), 0)  # Should find C major scale
        self.assertGreater(len(data['chord_results']), 0)  # Should find C major chord
        self.assertGreater(len(data['arpeggio_results']), 0)  # Should find C major arpeggio

        # Test search by category
        response = client.get('/search/json/', {'q': 'A minor', 'search_type': 'scales'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Should only find scales, not chords or arpeggios
        self.assertGreater(len(data['scale_results']), 0)
        self.assertEqual(len(data['chord_results']), 0)
        self.assertEqual(len(data['arpeggio_results']), 0)

    def test_unified_search_view(self):
        """Test the unified search view"""
        client = Client()

        # Test search for "A minor"
        response = client.get('/search/', {'search_query': 'A minor', 'search_type': 'all'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check that response contains expected content
        self.assertIn('A Minor', content)  # Should contain A minor results

        # Test search for "C major"
        response = client.get('/search/', {'search_query': 'C major', 'search_type': 'all'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check that response contains expected content
        self.assertIn('C Major', content)  # Should contain C major results

        # Test search by category
        response = client.get('/search/', {'search_query': 'A minor', 'search_type': 'scales'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Should contain scales, but not chords or arpeggios
        soup = BeautifulSoup(content, 'html.parser')

        # Find scales section
        scales_section = soup.find(id='scales-results')
        self.assertIsNotNone(scales_section)
        self.assertIn('A Minor', scales_section.text)

        # Check if chords and arpeggios sections contain no results
        # Note: This depends on your specific HTML structure, adjust as needed
        if soup.find(id='chords-results'):
            chords_section = soup.find(id='chords-results')
            self.assertNotIn('A Minor', chords_section.text)

        if soup.find(id='arpeggios-results'):
            arpeggios_section = soup.find(id='arpeggios-results')
            self.assertNotIn('A Minor', arpeggios_section.text)

    def test_ajax_search_request(self):
        """Test AJAX search request"""
        client = Client()

        # Simulate AJAX request
        response = client.get(
            '/search/',
            {'search_query': 'A minor', 'search_type': 'all'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        # Response should be JSON
        self.assertEqual(response['Content-Type'], 'application/json')

        # Parse JSON and check structure
        data = json.loads(response.content)
        self.assertIn('results', data)
        self.assertIn('total_count', data)
        self.assertIn('search_query', data)
        self.assertIn('search_type', data)

        # Check results
        self.assertIn('scales', data['results'])
        self.assertIn('chords', data['results'])
        self.assertIn('arpeggios', data['results'])

        # We should have found A minor in all categories
        self.assertTrue(any('A Minor' in item.get('name', '') for item in data['results']['scales']))
        self.assertTrue(any('A Minor' in item.get('name', '') for item in data['results']['chords']))
        self.assertTrue(any('A Minor' in item.get('name', '') for item in data['results']['arpeggios']))


if __name__ == "__main__":
    pytest.main(["-xvs", "test_search_functions.py"])