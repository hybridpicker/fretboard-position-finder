# tests/test_utils.py
import pytest
from unittest.mock import patch, MagicMock
from positionfinder.models import Notes, Root, NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition
import json
from django.test import Client, RequestFactory
import re


class MockQuerySet:
    """Mock Django QuerySet for testing"""
    
    def __init__(self, data_list=None):
        self.data = data_list or []
        self.query = "MOCKED QUERY"
    
    def filter(self, *args, **kwargs):
        """Mock filter method - returns self for chaining"""
        return self
    
    def get(self, *args, **kwargs):
        """Mock get method"""
        if not self.data:
            raise Notes.DoesNotExist("No matching object found")
        return self.data[0]
    
    def first(self):
        """Mock first method"""
        if not self.data:
            return None
        return self.data[0]
    
    def all(self):
        """Mock all method"""
        return self
    
    def __iter__(self):
        """Make iterable"""
        return iter(self.data)
    
    def count(self):
        """Return count of data"""
        return len(self.data)
        
    def values(self, *fields):
        """Mock values method"""
        if not fields:
            return [obj.__dict__ for obj in self.data]
        
        result = []
        for obj in self.data:
            item = {}
            for field in fields:
                item[field] = getattr(obj, field, None)
            result.append(item)
        return MockQuerySet(result)
    
    def values_list(self, *fields, flat=False):
        """Mock values_list method"""
        if not self.data:
            return []
        
        if flat and len(fields) == 1:
            return [getattr(obj, fields[0], None) for obj in self.data]
        
        result = []
        for obj in self.data:
            if fields:
                item = tuple(getattr(obj, field, None) for field in fields)
            else:
                item = tuple(obj.__dict__.values())
            result.append(item)
        return result
    
    def distinct(self):
        """Mock distinct method"""
        return self
    
    def order_by(self, *fields):
        """Mock order_by method"""
        return self


def create_mock_scale(note_name, scale_type="Major", root="C", note_id=1, root_id=1):
    """Helper to create a mock scale object"""
    scale = MagicMock(spec=Notes)
    scale.note_name = note_name
    scale.note_id = note_id
    scale.scale_type = scale_type
    scale.root = root
    scale.id = note_id
    scale.root_id = root_id
    scale.category = MagicMock(category_name="scale")
    # Add intervals property
    if scale_type == "Major":
        scale.intervals = "1-2-3-4-5-6-7"
    elif scale_type == "Minor":
        scale.intervals = "1-2-b3-4-5-b6-b7"
    elif scale_type == "Minor Pentatonic":
        scale.intervals = "1-b3-4-5-b7"
    return scale


def create_mock_chord(chord_name, type_name="V1", range="e - d", chord_id=1):
    """Helper to create a mock chord object"""
    chord = MagicMock(spec=ChordNotes)
    chord.chord_name = chord_name
    chord.id = chord_id
    chord.type_name = type_name
    chord.range = range
    chord.tonal_root = 0
    chord.category = MagicMock(category_name="chord")
    
    # Add chord formula
    if chord_name == "Major":
        chord.chord_formula = "1-3-5"
    elif chord_name == "Minor":
        chord.chord_formula = "1-b3-5"
    elif chord_name == "Major 7":
        chord.chord_formula = "1-3-5-7"
    elif chord_name == "Dominant 7":
        chord.chord_formula = "1-3-5-b7"
    return chord


def extract_form_with_inputs(html_content):
    """Extract form elements and inputs from HTML content for testing"""
    result = {}
    
    # Extract form
    form_match = re.search(r'<form[^>]*action="([^"]*)"[^>]*>', html_content)
    if form_match:
        result['form_action'] = form_match.group(1)
    
    # Extract inputs
    input_matches = re.finditer(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', html_content)
    result['inputs'] = {match.group(1): match.group(2) for match in input_matches}
    
    # Extract selects and options
    select_matches = re.finditer(r'<select[^>]*name="([^"]*)"[^>]*>(.*?)</select>', html_content, re.DOTALL)
    result['selects'] = {}
    
    for match in select_matches:
        select_name = match.group(1)
        select_content = match.group(2)
        
        # Find selected option
        selected_match = re.search(r'<option[^>]*value="([^"]*)"[^>]*selected[^>]*>', select_content)
        if selected_match:
            result['selects'][select_name] = selected_match.group(1)
        else:
            # Default to first option
            first_match = re.search(r'<option[^>]*value="([^"]*)"[^>]*>', select_content)
            if first_match:
                result['selects'][select_name] = first_match.group(1)
            else:
                result['selects'][select_name] = ""
    
    return result


class SearchTestHelpers:
    """Helper methods for testing search functionality"""
    
    @staticmethod
    def extract_results_from_html(html_content):
        """Extract search results from HTML content"""
        results = {
            'scales': [],
            'arpeggios': [],
            'chords': []
        }
        
        # Extract scale results
        scale_section = re.search(r'<h2>Scales</h2>.*?<ul class="result-list">(.*?)</ul>', html_content, re.DOTALL)
        if scale_section:
            scale_items = re.finditer(r'<li>.*?<div class="result-title">(.*?)</div>.*?</li>', scale_section.group(1), re.DOTALL)
            results['scales'] = [item.group(1).strip() for item in scale_items]
        
        # Extract arpeggio results
        arpeggio_section = re.search(r'<h2>Arpeggios</h2>.*?<ul class="result-list">(.*?)</ul>', html_content, re.DOTALL)
        if arpeggio_section:
            arpeggio_items = re.finditer(r'<li>.*?<div class="result-title">(.*?)</div>.*?</li>', arpeggio_section.group(1), re.DOTALL)
            results['arpeggios'] = [item.group(1).strip() for item in arpeggio_items]
        
        # Extract chord results
        chord_section = re.search(r'<h2>Chords</h2>.*?<ul class="result-list">(.*?)</ul>', html_content, re.DOTALL)
        if chord_section:
            chord_items = re.finditer(r'<li>.*?<div class="result-title">(.*?)</div>.*?</li>', chord_section.group(1), re.DOTALL)
            results['chords'] = [item.group(1).strip() for item in chord_items]
        
        return results
    
    @staticmethod
    def extract_urls_from_html(html_content):
        """Extract URLs from HTML content"""
        urls = []
        url_matches = re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>', html_content)
        for match in url_matches:
            urls.append(match.group(1))
        return urls
    
    @staticmethod
    def parse_json_response(response):
        """Parse JSON response and validate structure"""
        data = json.loads(response.content)
        
        # Basic validation of JSON structure
        assert 'query' in data, "JSON response missing 'query' field"
        
        if 'total_results' in data:
            # Search JSON response
            assert 'scale_results' in data, "JSON response missing 'scale_results' field"
            assert 'arpeggio_results' in data, "JSON response missing 'arpeggio_results' field"
            assert 'chord_results' in data, "JSON response missing 'chord_results' field"
        elif 'results' in data:
            # Autocomplete JSON response
            for result in data['results']:
                assert 'name' in result, "Result missing 'name' field"
                assert 'type' in result, "Result missing 'type' field"
                assert 'url' in result, "Result missing 'url' field"
        
        return data


def create_sample_data_fixture():
    """Create a fixture with sample test data"""
    # Create root notes
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
    
    # Create note categories
    scale_category = {"id": 1, "category_name": "scale"}
    arpeggio_category = {"id": 2, "category_name": "arpeggio"}
    chord_category = {"id": 3, "category_name": "chord"}
    
    # Create scales
    scales = [
        {
            "id": 1,
            "category": 1,
            "note_name": "C Major Scale",
            "ordering": 1,
            "tonal_root": 0,
            "notes_set": "0 2 4 5 7 9 11"
        },
        {
            "id": 2,
            "category": 1,
            "note_name": "C Minor Scale",
            "ordering": 2,
            "tonal_root": 0,
            "notes_set": "0 2 3 5 7 8 10"
        },
        {
            "id": 3,
            "category": 1,
            "note_name": "C Minor Pentatonic Scale",
            "ordering": 3,
            "tonal_root": 0,
            "notes_set": "0 3 5 7 10"
        }
    ]
    
    # Create arpeggios
    arpeggios = [
        {
            "id": 4,
            "category": 2,
            "note_name": "C Major Arpeggio",
            "ordering": 1,
            "tonal_root": 0,
            "notes_set": "0 4 7"
        },
        {
            "id": 5,
            "category": 2,
            "note_name": "C Minor Arpeggio",
            "ordering": 2,
            "tonal_root": 0,
            "notes_set": "0 3 7"
        },
        {
            "id": 6,
            "category": 2,
            "note_name": "C Major 7 Arpeggio",
            "ordering": 3,
            "tonal_root": 0,
            "notes_set": "0 4 7 11"
        }
    ]
    
    # Create chords
    chords = [
        {
            "id": 7,
            "category": 3,
            "type_name": "V1",
            "chord_name": "Major",
            "range": "e - d",
            "tonal_root": 0,
            "chord_formula": "1-3-5",
            "notes_set": "0 4 7"
        },
        {
            "id": 8,
            "category": 3,
            "type_name": "V1",
            "chord_name": "Minor",
            "range": "e - d",
            "tonal_root": 0,
            "chord_formula": "1-b3-5",
            "notes_set": "0 3 7"
        },
        {
            "id": 9,
            "category": 3,
            "type_name": "V1",
            "chord_name": "Major 7",
            "range": "e - d",
            "tonal_root": 0,
            "chord_formula": "1-3-5-7",
            "notes_set": "0 4 7 11"
        }
    ]
    
    fixture = {
        "roots": root_data,
        "categories": [scale_category, arpeggio_category, chord_category],
        "scales": scales,
        "arpeggios": arpeggios,
        "chords": chords
    }
    
    return fixture