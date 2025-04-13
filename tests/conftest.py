# tests/conftest.py
import pytest
from positionfinder.models import Notes, Root, NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition
from django.test import Client, RequestFactory
from django.utils import translation
from tests.test_utils import create_sample_data_fixture
from tests.locale_setup import SUPPORTED_LANGUAGES


@pytest.fixture(scope="session")
def django_db_setup():
    """DB setup for tests - only used if you need to modify database settings"""
    pass


@pytest.fixture
def client():
    """Django test client"""
    return Client()


@pytest.fixture
def factory():
    """Django request factory"""
    return RequestFactory()


@pytest.fixture
def set_language(request):
    """Fixture to set language in tests"""
    original_language = translation.get_language()
    
    def _set_language(language_code):
        if language_code in SUPPORTED_LANGUAGES:
            translation.activate(language_code)
            return True
        return False
    
    yield _set_language
    
    # Reset language after test
    translation.activate(original_language)


@pytest.fixture
def multi_language_client(client):
    """Test client with language setting capabilities"""
    original_language = translation.get_language()
    
    def set_language(language_code):
        if language_code in SUPPORTED_LANGUAGES:
            translation.activate(language_code)
            return True
        return False
    
    client.set_language = set_language
    
    yield client
    
    # Reset language after test
    translation.activate(original_language)


@pytest.fixture
def sample_roots(db):
    """Create sample root notes"""
    roots = []
    root_data = [
        {"name": "C", "pitch": 0},
        {"name": "C#", "pitch": 1},
        {"name": "D", "pitch": 2},
        {"name": "D#", "pitch": 3},
        {"name": "E", "pitch": 4},
        {"name": "F", "pitch": 5},
        {"name": "F#", "pitch": 6},
        {"name": "G", "pitch": 7},
        {"name": "G#", "pitch": 8},
        {"name": "A", "pitch": 9},
        {"name": "A#", "pitch": 10},
        {"name": "B", "pitch": 11},
    ]
    for data in root_data:
        root = Root.objects.create(**data)
        roots.append(root)
    return roots


@pytest.fixture
def sample_categories(db):
    """Create sample note categories"""
    scale_category = NotesCategory.objects.create(category_name="scale")
    arpeggio_category = NotesCategory.objects.create(category_name="arpeggio")
    chord_category = NotesCategory.objects.create(category_name="chord")
    return {
        "scale": scale_category,
        "arpeggio": arpeggio_category,
        "chord": chord_category
    }


@pytest.fixture
def sample_scales(db, sample_categories, sample_roots):
    """Create sample scales"""
    scales = []
    scale_data = [
        {
            "category": sample_categories["scale"],
            "note_name": "C Major Scale",
            "ordering": 1,
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 2,
            "third_note": 4,
            "fourth_note": 5,
            "fifth_note": 7,
            "sixth_note": 9,
            "seventh_note": 11,
        },
        {
            "category": sample_categories["scale"],
            "note_name": "C Minor Scale",
            "ordering": 2,
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 2,
            "third_note": 3,
            "fourth_note": 5,
            "fifth_note": 7,
            "sixth_note": 8,
            "seventh_note": 10,
        },
        {
            "category": sample_categories["scale"],
            "note_name": "C Minor Pentatonic Scale",
            "ordering": 3,
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 3,
            "third_note": 5,
            "fourth_note": 7,
            "fifth_note": 10,
        },
        {
            "category": sample_categories["scale"],
            "note_name": "C Dorian Scale",
            "ordering": 4,
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 2,
            "third_note": 3,
            "fourth_note": 5,
            "fifth_note": 7,
            "sixth_note": 9,
            "seventh_note": 10,
        },
        {
            "category": sample_categories["scale"],
            "note_name": "C Phrygian Scale",
            "ordering": 5,
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 1,
            "third_note": 3,
            "fourth_note": 5,
            "fifth_note": 7,
            "sixth_note": 8,
            "seventh_note": 10,
        },
    ]
    for data in scale_data:
        scale = Notes.objects.create(**data)
        scales.append(scale)
    return scales


@pytest.fixture
def sample_arpeggios(db, sample_categories, sample_roots):
    """Create sample arpeggios"""
    arpeggios = []
    arpeggio_data = [
        {
            "category": sample_categories["arpeggio"],
            "note_name": "C Major Arpeggio",
            "ordering": 1,
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 4,
            "third_note": 7,
        },
        {
            "category": sample_categories["arpeggio"],
            "note_name": "C Minor Arpeggio",
            "ordering": 2,
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 3,
            "third_note": 7,
        },
        {
            "category": sample_categories["arpeggio"],
            "note_name": "C Major 7 Arpeggio",
            "ordering": 3,
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 4,
            "third_note": 7,
            "fourth_note": 11,
        },
        {
            "category": sample_categories["arpeggio"],
            "note_name": "C Dominant 7 Arpeggio",
            "ordering": 4,
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 4,
            "third_note": 7,
            "fourth_note": 10,
        },
    ]
    for data in arpeggio_data:
        arpeggio = Notes.objects.create(**data)
        arpeggios.append(arpeggio)
    return arpeggios


@pytest.fixture
def sample_chords(db, sample_categories, sample_roots):
    """Create sample chords"""
    chords = []
    chord_data = [
        {
            "category": sample_categories["chord"],
            "type_name": "V1",
            "chord_name": "Major",
            "range": "e - d",
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 4,
            "third_note": 7,
        },
        {
            "category": sample_categories["chord"],
            "type_name": "V1",
            "chord_name": "Minor",
            "range": "e - d",
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 3,
            "third_note": 7,
        },
        {
            "category": sample_categories["chord"],
            "type_name": "V1",
            "chord_name": "Major 7",
            "range": "e - d",
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 4,
            "third_note": 7,
            "fourth_note": 11,
        },
        {
            "category": sample_categories["chord"],
            "type_name": "V1",
            "chord_name": "Dominant 7",
            "range": "e - d",
            "tonal_root": 0,
            "first_note": 0,
            "second_note": 4,
            "third_note": 7,
            "fourth_note": 10,
        },
    ]
    for data in chord_data:
        chord = ChordNotes.objects.create(**data)
        # Create positions for chords (required for search)
        ChordPosition.objects.create(
            notes_name=chord,
            inversion_order="Basic Position",
            first_note=0,
            second_note=0,
            third_note=0,
            fourth_note=0 if chord.fourth_note is not None else None
        )
        chords.append(chord)
    return chords


@pytest.fixture
def all_sample_data(sample_roots, sample_categories, sample_scales, sample_arpeggios, sample_chords):
    """Combine all sample data fixtures"""
    return {
        "roots": sample_roots,
        "categories": sample_categories,
        "scales": sample_scales,
        "arpeggios": sample_arpeggios,
        "chords": sample_chords
    }


@pytest.fixture
def mock_fixture_data():
    """Return fixture data for mocking"""
    return create_sample_data_fixture()