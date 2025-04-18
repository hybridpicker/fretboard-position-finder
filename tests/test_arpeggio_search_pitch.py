# tests/test_arpeggio_search_pitch.py
"""
Tests specifically for the updated arpeggio search logic that uses pitch values instead of ID values.
This focuses on verifying the fix in fix_search_arpeggios.py works correctly.
"""
import pytest
from django.test import TestCase
from positionfinder.models import Root, NotesCategory, Notes
from positionfinder.views_search import search_arpeggios
import logging

# Configure logging for test output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestArpeggioSearchPitch(TestCase):
    """Test that arpeggio search correctly uses pitch values for matching root notes"""

    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create root notes with specific pitch values and IDs
        # The key for this test is that the ID and pitch values are different
        # This helps ensure we're using pitch for filtering, not ID
        cls.root_c = Root.objects.create(name="C", display_name="C", pitch=0, id=1)
        cls.root_cs = Root.objects.create(name="C#", display_name="C#", pitch=1, id=3)
        cls.root_db = Root.objects.create(name="Db", display_name="Db", pitch=1, id=2)  # Same pitch as C#
        cls.root_d = Root.objects.create(name="D", display_name="D", pitch=2, id=4)
        cls.root_eb = Root.objects.create(name="Eb", display_name="Eb", pitch=3, id=5)
        cls.root_ds = Root.objects.create(name="D#", display_name="D#", pitch=3, id=6)  # Same pitch as Eb
        cls.root_e = Root.objects.create(name="E", display_name="E", pitch=4, id=7)
        cls.root_f = Root.objects.create(name="F", display_name="F", pitch=5, id=8)
        cls.root_fs = Root.objects.create(name="F#", display_name="F#", pitch=6, id=10)
        cls.root_gb = Root.objects.create(name="Gb", display_name="Gb", pitch=6, id=9)  # Same pitch as F#
        cls.root_g = Root.objects.create(name="G", display_name="G", pitch=7, id=11)
        cls.root_gs = Root.objects.create(name="G#", display_name="G#", pitch=8, id=13)
        cls.root_ab = Root.objects.create(name="Ab", display_name="Ab", pitch=8, id=12)  # Same pitch as G#
        cls.root_a = Root.objects.create(name="A", display_name="A", pitch=9, id=14)
        cls.root_bb = Root.objects.create(name="Bb", display_name="Bb", pitch=10, id=15)
        cls.root_as = Root.objects.create(name="A#", display_name="A#", pitch=10, id=16)  # Same pitch as Bb
        cls.root_b = Root.objects.create(name="B", display_name="B", pitch=11, id=17)
        
        # Create arpeggio category
        cls.arpeggio_category = NotesCategory.objects.create(category_name="arpeggio")
        
        # Create a set of arpeggios with different root pitches
        # Using tonal_root as pitch, not ID
        cls.c_major = Notes.objects.create(
            category=cls.arpeggio_category,
            note_name="Major",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7
        )
        
        cls.cs_major = Notes.objects.create(
            category=cls.arpeggio_category,
            note_name="Major",
            tonal_root=1,  # C#
            first_note=1, third_note=5, fifth_note=8
        )
        
        cls.d_major = Notes.objects.create(
            category=cls.arpeggio_category,
            note_name="Major",
            tonal_root=2,  # D
            first_note=2, third_note=6, fifth_note=9
        )
        
        cls.a_minor = Notes.objects.create(
            category=cls.arpeggio_category,
            note_name="Minor",
            tonal_root=9,  # A
            first_note=9, third_note=0, fifth_note=4
        )
        
        cls.e_minor = Notes.objects.create(
            category=cls.arpeggio_category,
            note_name="Minor",
            tonal_root=4,  # E
            first_note=4, third_note=7, fifth_note=11
        )

    def test_search_by_pitch_value(self):
        """Test that search correctly matches by pitch, not ID"""
        # Search for C# arpeggios
        results = search_arpeggios(note="C#", quality="major")
        
        # Should find one arpeggio with tonal_root=1
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.cs_major.id)
        
        # Search for Db (enharmonic with C#)
        db_results = search_arpeggios(note="Db", quality="major")
        
        # Should find the same results as C# (since they're the same pitch)
        self.assertEqual(len(db_results), 1)
        self.assertEqual(db_results[0]["id"], self.cs_major.id)
        
        # Search by name where ID != pitch
        # For D, ID=4 but pitch=2
        d_results = search_arpeggios(note="D", quality="major")
        
        # Should use pitch (2), not ID (4)
        self.assertEqual(len(d_results), 1)
        self.assertEqual(d_results[0]["id"], self.d_major.id)

    def test_search_enharmonic_equivalence(self):
        """Test that search works with enharmonic note names"""
        # Create enharmonic test data
        enharmonic_pairs = [
            ("C#", "Db"),
            ("D#", "Eb"),
            ("F#", "Gb"),
            ("G#", "Ab"),
            ("A#", "Bb")
        ]
        
        # Test standard quality
        quality = "major"
        for note1, note2 in enharmonic_pairs:
            # Both members of each pair should return the same results
            results1 = search_arpeggios(note=note1, quality=quality)
            results2 = search_arpeggios(note=note2, quality=quality)
            
            # Check that the IDs match (regardless of order)
            results1_ids = sorted([r["id"] for r in results1])
            results2_ids = sorted([r["id"] for r in results2])
            
            self.assertEqual(
                results1_ids,
                results2_ids,
                f"Searches for '{note1} {quality}' and '{note2} {quality}' returned different arpeggios"
            )
            
        # Test minor quality too
        quality = "minor"
        for note1, note2 in enharmonic_pairs:
            results1 = search_arpeggios(note=note1, quality=quality)
            results2 = search_arpeggios(note=note2, quality=quality)
            
            # Check that the IDs match (regardless of order)
            results1_ids = [r["id"] for r in results1]
            results2_ids = [r["id"] for r in results2]
            
            self.assertEqual(
                set(results1_ids),
                set(results2_ids),
                f"Searches for '{note1} {quality}' and '{note2} {quality}' returned different arpeggios"
            )

    def test_manual_pitch_search(self):
        """
        Manually test pitch-based filtering to verify behavior
        matches the search_arpeggios function
        """
        # Test A minor
        # First method: Direct pitch filter
        query1 = Notes.objects.filter(
            category__category_name__icontains='arpeggio',
            note_name__icontains='minor',
            tonal_root=9  # A pitch
        )
        
        # Second method: via Root model (like in the updated code)
        root_obj = Root.objects.filter(name__iexact='A').first()
        query2 = Notes.objects.filter(
            category__category_name__icontains='arpeggio',
            note_name__icontains='minor',
            tonal_root=root_obj.pitch
        )
        
        # Both should return the same results
        self.assertEqual(query1.count(), query2.count())
        self.assertEqual(
            set(query1.values_list('id', flat=True)),
            set(query2.values_list('id', flat=True))
        )
        
        # Compare with view function
        view_results = search_arpeggios(note='A', quality='minor')
        self.assertEqual(query1.count(), len(view_results))
        self.assertEqual(
            set(query1.values_list('id', flat=True)),
            set(item['id'] for item in view_results)
        )

    def test_unicode_symbols_compatibility(self):
        """Test that Unicode sharp and flat symbols work correctly"""
        # Create test data
        Notes.objects.create(
            category=self.arpeggio_category,
            note_name="Diminished",
            tonal_root=1,  # C#/Db pitch
            first_note=1, third_note=4, fifth_note=7, seventh_note=10
        )
        
        # Test with standard notation
        results_std = search_arpeggios(note="C#", quality="diminished")
        self.assertEqual(len(results_std), 1)
        
        # Test with Unicode sharp (♯)
        results_unicode = search_arpeggios(note="C♯", quality="diminished")
        self.assertEqual(len(results_unicode), 1)
        
        # Test with Unicode flat (♭)
        results_unicode_flat = search_arpeggios(note="D♭", quality="diminished")
        self.assertEqual(len(results_unicode_flat), 1)
        
        # All should return the same arpeggio
        self.assertEqual(results_std[0]["id"], results_unicode[0]["id"])
        self.assertEqual(results_std[0]["id"], results_unicode_flat[0]["id"])

    def test_root_id_url_consistency(self):
        """Test that the URL generated uses the correct root ID (not pitch)"""
        # Search for A minor
        results = search_arpeggios(note="A", quality="minor")
        self.assertEqual(len(results), 1)
        
        # Extract URL from results
        url = results[0]["url"]
        
        # URL should include the root ID (14 for 'A'), not the pitch value (9)
        self.assertIn("root=14", url)  # Should contain root ID, not pitch
        self.assertNotIn("root=9", url)  # Should not contain pitch
        
        # Test another note too
        results_e = search_arpeggios(note="E", quality="minor")
        self.assertEqual(len(results_e), 1)
        
        # Extract URL from results
        url_e = results_e[0]["url"]
        
        # URL should include the root ID (7 for 'E'), not the pitch value (4)
        self.assertIn("root=7", url_e)  # Should contain root ID, not pitch
        self.assertNotIn("root=4", url_e)  # Should not contain pitch

    def test_mixed_case_search(self):
        """Test that searches work with mixed case input"""
        # Create mix case test data
        Notes.objects.create(
            category=self.arpeggio_category,
            note_name="Mixed Case Quality",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7
        )
        
        # Test lowercase
        lower_results = search_arpeggios(note="c", quality="mixed case quality")
        self.assertEqual(len(lower_results), 1)
        
        # Test uppercase
        upper_results = search_arpeggios(note="C", quality="MIXED CASE QUALITY")
        self.assertEqual(len(upper_results), 1)
        
        # Test mixed case
        mixed_results = search_arpeggios(note="C", quality="MiXeD CaSe QuAlItY")
        self.assertEqual(len(mixed_results), 1)
        
        # Test camel case (Quality is CamelCase in the query but regular in the DB)
        base_results = search_arpeggios(note="C", quality="Mixed Case Quality")
        self.assertEqual(len(base_results), 1)
        
        # All should match the same ID
        test_id = lower_results[0]["id"]
        self.assertEqual(upper_results[0]["id"], test_id)
        self.assertEqual(mixed_results[0]["id"], test_id)
        self.assertEqual(base_results[0]["id"], test_id)

    def test_arpeggio_name_composition(self):
        """Test that arpeggio names are correctly composed with root notes"""
        # Create test arpeggio with standard quality name
        Notes.objects.create(
            category=self.arpeggio_category,
            note_name="Dominant 7",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7, seventh_note=10
        )
        
        # Test search with root note 
        results = search_arpeggios(note="C", quality="dominant 7")
        self.assertEqual(len(results), 1)
        
        # The result name should properly combine root and quality
        self.assertEqual(results[0]["name"], "C Dominant 7")
        
        # Test search where the note is already part of the quality/name
        # This tests that we don't end up with something like "G G Dominant 7"
        Notes.objects.create(
            category=self.arpeggio_category,
            note_name="G Dominant 7",  # Note already in the name
            tonal_root=7,  # G
            first_note=7, third_note=11, fifth_note=2, seventh_note=5
        )
        
        g_results = search_arpeggios(note="G", quality="G Dominant 7")
        self.assertEqual(len(g_results), 1)
        
        # Name should not duplicate the "G"
        self.assertEqual(g_results[0]["name"], "G Dominant 7")
        
        # Check simple search by quality
        dom7_results = search_arpeggios(quality="dominant 7")
        self.assertGreaterEqual(len(dom7_results), 2)  # Should find at least both dominant 7s

    def test_edge_cases(self):
        """Test edge cases and error handling in search_arpeggios"""
        # Test with non-existent note
        results_nonexistent = search_arpeggios(note="Z", quality="major")
        self.assertEqual(len(results_nonexistent), 0)  # Should handle gracefully with no results
        
        # Test with note name that has special characters
        results_special = search_arpeggios(note="C#!@#", quality="major")
        self.assertEqual(len(results_special), 0)  # Should handle gracefully
        
        # Test with extremely long strings
        long_note = "A" * 100
        results_long = search_arpeggios(note=long_note, quality="major")
        self.assertEqual(len(results_long), 0)  # Should handle gracefully
        
        # Test with non-English characters in search
        Notes.objects.create(
            category=self.arpeggio_category,
            note_name="Special",
            tonal_root=0,  # C
            first_note=0, third_note=4, fifth_note=7
        )
        
        # Search with special unicode characters
        results = search_arpeggios(note="C", quality="Spécial")
        self.assertGreater(len(results), 0)  # Should find the arpeggio

if __name__ == "__main__":
    pytest.main(["-xvs", "test_arpeggio_search_pitch.py"])
