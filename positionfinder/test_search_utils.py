import pytest
from .search_utils import parse_query
import requests
import os
import json
import django

def test_typo_and_default_handling():
    # Typo in note and scale name
    note, type_, quality, position, inversion = parse_query("EMinor Penatotnic")
    assert note in ("E", "C"), f"Expected E or C, got {note}"
    assert type_ == "chord"  # default fallback
    assert quality == "minor pentatonic"
    assert inversion == "basic position"

    # No note, just V2 Major Chord
    note, type_, quality, position, inversion = parse_query("V2 Major Chord")
    assert note == "C", f"Expected default C, got {note}"
    assert quality == "major"
    assert position == "V2"
    assert type_ == "chord"

    # No type, just G Major7
    note, type_, quality, position, inversion = parse_query("G Major7")
    assert note == "G"
    assert quality in ("maj7", "major")
    assert type_ == "chord"

    # Lowercase, missing everything
    note, type_, quality, position, inversion = parse_query("")
    assert note == "C"
    assert type_ == "chord"
    assert quality == "major"
    assert inversion == "basic position"

    # Harmonic major scale
    note, type_, quality, position, inversion = parse_query("e Harmonic Major")
    assert note == "E"
    assert quality == "harmonic major"

    # Ambiguous input defaults
    note, type_, quality, position, inversion = parse_query("random gibberish")
    assert note == "C"
    assert type_ == "chord"
    assert quality == "major"
    assert inversion == "basic position"

    # All positions
    note, type_, quality, position, inversion = parse_query("A minor all positions")
    assert note == "A"
    assert quality == "minor"
    assert position == "all positions"

    # Inversion
    note, type_, quality, position, inversion = parse_query("D major 1st inversion")
    assert note == "D"
    assert quality == "major"
    assert inversion == "1st inversion"

def test_search_chords_major7_v2():
    """
    Integration test: The /search_json/ endpoint should return a chord result for 'Major7 V2' if such a chord exists in the DB.
    This test requires Django test server to be running and the DB to contain at least one Major7 V2 chord.
    """
    # You may want to set this dynamically or use Django's test client in a real test suite
    url = os.environ.get('DJANGO_TEST_SERVER', 'http://localhost:8000/search_json/')
    params = {'q': 'Major7 V2'}
    response = requests.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    # If your DB is seeded with a matching chord, assert it's present
    chords = data.get('chord_results', [])
    # Accept either an empty result (if not seeded) or at least one with correct fields
    if chords:
        chord = chords[0]
        assert 'url' in chord, f"Chord result missing URL: {chord}"
        assert 'Major' in chord['name'] or 'Maj7' in chord['name']
        assert 'V2' in chord['type'] or 'V-2' in chord['type']
    else:
        # If no chords, print a warning (not a failure)
        print("WARNING: No 'Major7 V2' chord found in the database. Seed test data for full test.")

def test_search_chords_triads():
    """
    Integration test: /search_json/ endpoint should return a chord result for 'Triad' if such a chord exists in the DB.
    """
    url = os.environ.get('DJANGO_TEST_SERVER', 'http://localhost:8000/search_json/')
    params = {'q': 'Triad'}
    response = requests.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    chords = data.get('chord_results', [])
    if chords:
        chord = chords[0]
        assert 'url' in chord, f"Chord result missing URL: {chord}"
        assert 'Triad' in chord['name'] or 'Triad' in chord['type']
    else:
        print("WARNING: No 'Triad' chord found in the database. Seed test data for full test.")

def test_search_chords_spread_triads():
    """
    Integration test: /search_json/ endpoint should return a chord result for 'Spread Triad' if such a chord exists in the DB.
    """
    url = os.environ.get('DJANGO_TEST_SERVER', 'http://localhost:8000/search_json/')
    params = {'q': 'Spread Triad'}
    response = requests.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    chords = data.get('chord_results', [])
    if chords:
        chord = chords[0]
        assert 'url' in chord, f"Chord result missing URL: {chord}"
        assert 'Spread' in chord['name'] or 'Spread' in chord['type']
        assert 'Triad' in chord['name'] or 'Triad' in chord['type']
    else:
        print("WARNING: No 'Spread Triad' chord found in the database. Seed test data for full test.")

def test_search_chords_v_system():
    """
    Integration test: /search_json/ endpoint should return chord results for V1, V2, V3, V4, etc. if such chords exist in the DB.
    """
    url = os.environ.get('DJANGO_TEST_SERVER', 'http://localhost:8000/search_json/')
    for v in range(1, 8):
        params = {'q': f'V{v}'}
        response = requests.get(url, params=params)
        assert response.status_code == 200
        data = response.json()
        chords = data.get('chord_results', [])
        if chords:
            chord = chords[0]
            assert 'url' in chord, f"Chord result missing URL: {chord}"
            assert f'V{v}' in chord['type'] or f'V-{v}' in chord['type']
        else:
            print(f"WARNING: No 'V{v}' chord found in the database. Seed test data for full test.")
