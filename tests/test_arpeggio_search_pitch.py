# tests/test_arpeggio_search_pitch.py
"""
Tests specifically for the updated arpeggio search logic that uses pitch values instead of ID values.
This focuses on verifying the fix in fix_search_arpeggios.py works correctly.
"""
import pytest
from django.test import TestCase
from positionfinder.models import Root, NotesCategory
from positionfinder.models_chords import ChordNotes
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
        cls.c_major = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Major",
            type_name="Standard",
            tonal_root=0,  # C pitch
            first_note=0, third_note=4, fifth_note=7,
            range="e - d"
        )
        
        cls.cs_major = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Major",
            type_name="Standard",
            tonal_root=1,  # C#/Db pitch
            first_note=1, third_note=5, fifth_note=8,
            range="e - d"
        )
        
        cls.d_minor = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Minor",
            type_name="Standard",
            tonal_root=2,  # D pitch
            first_note=2, third_note=5, fifth_note=9,
            range="e - d"
        )
        
        cls.eb_major = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Major",
            type_name="Standard",
            tonal_root=3,  # Eb/D# pitch
            first_note=3, third_note=7, fifth_note=10,
            range="e - d"
        )
        
        cls.a_minor = ChordNotes.objects.create(
            category=cls.arpeggio_category,
            chord_name="Minor",
            type_name="Standard",
            tonal_root=9,  # A pitch
            first_note=9, third_note=0, fifth_note=4,
            range="e - d"
        )

    def test_search_by_pitch_value(self):
        """Test that search correctly matches by pitch, not ID"""
        # Search for C major
        results = search_arpeggios(note="C", quality="major")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "C Major")
        
        # Search for C# major using both C# and Db
        results_cs = search_arpeggios(note="C#", quality="major")
        results_db = search_arpeggios(note="Db", quality="major")
        
        # Both should find the same arpeggio
        self.assertEqual(len(results_cs), 1)
        self.assertEqual(len(results_db), 1)
        self.assertEqual(results_cs[0]["id"], results_db[0]["id"])
        
        # Search for Eb major using both Eb and D#
        results_eb = search_arpeggios(note="Eb", quality="major")
        results_ds = search_arpeggios(note="D#", quality="major")
        
        # Both should find the same arpeggio
        self.assertEqual(len(results_eb), 1)
        self.assertEqual(len(results_ds), 1)
        self.assertEqual(results_eb[0]["id"], results_ds[0]["id"])

    def test_search_enharmonic_equivalence(self):
        """Test that enharmonic note equivalents return the same results"""
        # List of enharmonic equivalent pairs
        enharmonics = [
            ("C#", "Db"),
            ("D#", "Eb"),
            ("F#", "Gb"),
            ("G#", "Ab"),
            ("A#", "Bb")
        ]
        
        qualities = ["major", "minor"]
        
        for note1, note2 in enharmonics:
            for quality in qualities:
                results1 = search_arpeggios(note=note1, quality=quality)
                results2 = search_arpeggios(note=note2, quality=quality)
                
                # Both searches should return the same number of results
                self.assertEqual(
                    len(results1), 
                    len(results2), 
                    f"Searches for '{note1} {quality}' and '{note2} {quality}' returned different result counts"
                )
                
                # If results were found, they should have the same IDs
                if len(results1) > 0:
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
        query1 = ChordNotes.objects.filter(
            category__category_name__icontains='arpeggio',
            chord_name__icontains='minor',
            tonal_root=9  # A pitch
        )
        
        # Second method: via Root model (like in the updated code)
        root_obj = Root.objects.filter(name__iexact='A').first()
        query2 = ChordNotes.objects.filter(
            category__category_name__icontains='arpeggio',
            chord_name__icontains='minor',
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
        ChordNotes.objects.create(
            category=self.arpeggio_category,
            chord_name="Diminished",
            type_name="Standard",
            tonal_root=1,  # C#/Db pitch
            first_note=1, third_note=4, fifth_note=7, seventh_note=10,
            range="e - d"
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
        
        # The URL should contain root=14 (ID of A), not root=9 (pitch of A)
        url = results[0]["url"]
        self.assertIn("root=14", url)
        self.assertNotIn("root=9", url)
        
        # Search for C# major
        results = search_arpeggios(note="C#", quality="major")
        self.assertEqual(len(results), 1)
        
        # The URL should contain root=3 (ID of C#), not root=1 (pitch of C#)
        url = results[0]["url"]
        self.assertIn("root=3", url)
        self.assertNotIn("root=1", url)
        
    def test_quality_variations(self):
        """Test that various quality name variations work correctly"""
        # Create test data with different quality name formats
        ChordNotes.objects.create(
            category=self.arpeggio_category,
            chord_name="Min",  # Abbreviated 'Minor'
            type_name="Standard",
            tonal_root=7,  # G pitch
            first_note=7, third_note=10, fifth_note=2,
            range="e - d"
        )
        
        ChordNotes.objects.create(
            category=self.arpeggio_category,
            chord_name="m",  # Very abbreviated 'Minor'
            type_name="Standard",
            tonal_root=11,  # B pitch
            first_note=11, third_note=2, fifth_note=6,
            range="e - d"
        )
        
        ChordNotes.objects.create(
            category=self.arpeggio_category,
            chord_name="Maj",  # Abbreviated 'Major'
            type_name="Standard",
            tonal_root=5,  # F pitch
            first_note=5, third_note=9, fifth_note=0,
            range="e - d"
        )
        
        # Test minor variations
        results1 = search_arpeggios(note="G", quality="minor")
        results2 = search_arpeggios(note="G", quality="min")
        results3 = search_arpeggios(note="G", quality="m")
        
        # All should return the G Min arpeggio
        self.assertEqual(len(results1), 1)
        self.assertEqual(len(results2), 1)
        self.assertEqual(len(results3), 1)
        self.assertEqual(results1[0]["id"], results2[0]["id"])
        self.assertEqual(results1[0]["id"], results3[0]["id"])
        
        # Test with B minor
        results1 = search_arpeggios(note="B", quality="minor")
        results2 = search_arpeggios(note="B", quality="min")
        results3 = search_arpeggios(note="B", quality="m")
        
        # All should return the B m arpeggio
        self.assertEqual(len(results1), 1)
        self.assertEqual(len(results2), 1)
        self.assertEqual(len(results3), 1)
        self.assertEqual(results1[0]["id"], results2[0]["id"])
        self.assertEqual(results1[0]["id"], results3[0]["id"])
        
        # Test major variations
        results1 = search_arpeggios(note="F", quality="major")
        results2 = search_arpeggios(note="F", quality="maj")
        
        # Both should return the F Maj arpeggio
        self.assertEqual(len(results1), 1)
        self.assertEqual(len(results2), 1)
        self.assertEqual(results1[0]["id"], results2[0]["id"])

    def test_mixed_case_search(self):
        """Test that searches work with mixed case input"""
        # Test with various case variations
        variations = [
            "a minor",
            "A minor",
            "a MINOR",
            "A MINOR",
            "A Minor"
        ]
        
        # All should return the same A minor arpeggio
        base_results = search_arpeggios(note="A", quality="minor")
        self.assertEqual(len(base_results), 1)
        
        for query in variations:
            # Extract note and quality from the query
            parts = query.split(" ", 1)
            note = parts[0]
            quality = parts[1] if len(parts) > 1 else ""
            
            results = search_arpeggios(note=note, quality=quality)
            
            # Should return the same result as the base query
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["id"], base_results[0]["id"])
            
    def test_arpeggio_name_composition(self):
        """Test that arpeggio names are correctly composed with root notes"""
        # Create test data with different naming patterns
        ChordNotes.objects.create(
            category=self.arpeggio_category,
            chord_name="Major 7",  # Space in quality name
            type_name="Standard",
            tonal_root=7,  # G pitch
            first_note=7, third_note=11, fifth_note=2, seventh_note=6,
            range="e - d"
        )
        
        ChordNotes.objects.create(
            category=self.arpeggio_category,
            chord_name="G Minor",  # Root already included in name
            type_name="Standard",
            tonal_root=7,  # G pitch
            first_note=7, third_note=10, fifth_note=2,
            range="e - d"
        )
        
        # Test name composition for "Major 7"
        results = search_arpeggios(note="G", quality="major 7")
        self.assertEqual(len(results), 1)
        # Name should be composed as "G Major 7"
        self.assertEqual(results[0]["name"], "G Major 7")
        
        # Test with name that already includes root
        results = search_arpeggios(note="G", quality="minor")
        self.assertGreaterEqual(len(results), 1)  # Could be multiple matches from other tests
        
        # Find the result with "G Minor" chord_name
        g_minor_result = None
        for result in results:
            if result["name"] == "G Minor":
                g_minor_result = result
                break
        
        self.assertIsNotNone(g_minor_result, "Couldn't find G Minor in results")
        # Name should not be duplicated as "G G Minor"
        self.assertEqual(g_minor_result["name"], "G Minor")
        
    def test_edge_cases(self):
        """Test edge cases and error handling in search_arpeggios"""
        # Test with empty note and quality
        results = search_arpeggios(note="", quality="")
        # Should return all arpeggios
        self.assertGreater(len(results), 0)
        
        # Test with non-existent note
        results = search_arpeggios(note="Z", quality="major")
        # Should return empty list
        self.assertEqual(len(results), 0)
        
        # Test with non-existent quality
        results = search_arpeggios(note="A", quality="ultra-minor")
        # Should return empty list
        self.assertEqual(len(results), 0)
        
        # Test with None values
        results = search_arpeggios(note=None, quality=None)
        # Should handle gracefully and return results (all arpeggios)
        self.assertGreater(len(results), 0)
        
        # Test with weird characters that might cause issues
        results = search_arpeggios(note="A'", quality="minor--")
        # Should handle gracefully, either returning A minor or empty list
        # We're mainly testing that it doesn't crash
        
        # Test with SQL injection attempt
        results = search_arpeggios(note="A'; DROP TABLE arpeggios; --", quality="minor")
        # Should sanitize input and either return A minor or empty list
        # Again, mainly testing that it doesn't crash


if __name__ == "__main__":
    pytest.main(["-xvs", "test_arpeggio_search_pitch.py"])
