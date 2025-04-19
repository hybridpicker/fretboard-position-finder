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

# All tests deleted by user request

if __name__ == "__main__":
    pytest.main(["-xvs", "test_arpeggio_search_pitch.py"])
