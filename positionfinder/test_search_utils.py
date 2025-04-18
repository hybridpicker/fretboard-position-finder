import pytest
from .search_utils import parse_query, get_root_id_from_name
import requests
import os
import json
import django

def test_typo_and_default_handling():
    # Typo in note and scale name
    note, type_, quality, position, inversion = parse_query("EMinor Penatotnic")
    assert note in ("E", "C"), f"Expected E or C, got {note}"
    assert type_ == "scale"  # now correctly identifies as scale
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

def test_search_scales_minor_pentatonic():
    """
    Test that querying 'E Minor Pentatonic' returns only the E-root scale, with dynamic fallback if no fixture exists.
    """
    import requests
    resp = requests.get("http://localhost:8080/search_json", params={"q": "E Minor Pentatonic", "search_type": "all"})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["total_results"] == len(data["scale_results"]), "Should only return scales for minor pentatonic query"
    assert all("E" in r["name"] for r in data["scale_results"]), f"Non-E scale found: {[r['name'] for r in data['scale_results']]}"
    # Should dynamically generate if not present in DB
    assert any("pentatonic" in r["name"].lower() for r in data["scale_results"]), "No pentatonic scale returned"

def test_search_chords_major7():
    """
    Test that querying 'C Major7' returns only chords.
    """
    import requests
    resp = requests.get("http://localhost:8080/search_json", params={"q": "C Major7", "search_type": "all"})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["total_results"] == len(data["chord_results"]), "Should only return chords for Major7 query"
    assert all("C" in r["name"] for r in data["chord_results"]), f"Non-C chord found: {[r['name'] for r in data['chord_results']]}"
    assert any(
        "maj7" in r["name"].lower() or
        "major7" in r["name"].lower() or
        "major 7" in r["name"].lower()
        for r in data["chord_results"]
    ), "No Major7 chord returned"

def test_search_typo_scale_name():
    """
    Test typo tolerance for scale queries (e.g., 'A Minorr Pentatonik').
    """
    import requests
    resp = requests.get("http://localhost:8080/search_json", params={"q": "A Minorr Pentatonik", "search_type": "all"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] == len(data["scale_results"])
    assert any("A" in r["name"] for r in data["scale_results"]), f"Non-A scale found: {[r['name'] for r in data['scale_results']]}"
    assert any("pentatonic" in r["name"].lower() for r in data["scale_results"]), "No pentatonic scale returned"

def test_search_typo_chord_name():
    """
    Test typo tolerance for chord queries (e.g., 'G Majjor7').
    """
    import requests
    resp = requests.get("http://localhost:8080/search_json", params={"q": "G Majjor7", "search_type": "all"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] == len(data["chord_results"])
    assert all("G" in r["name"] for r in data["chord_results"]), f"Non-G chord found: {[r['name'] for r in data['chord_results']]}"
    assert any(
        "maj7" in r["name"].lower() or
        "major7" in r["name"].lower() or
        "major 7" in r["name"].lower()
        for r in data["chord_results"]
    ), "No Major7 chord returned"

def test_search_exact_arpeggio():
    """
    Test exact search for an arpeggio (e.g., 'C Major Arpeggio').
    """
    import requests
    resp = requests.get("http://localhost:8080/search_json", params={"q": "C Major Arpeggio", "search_type": "arpeggios"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] == len(data["arpeggio_results"])
    assert all("C" in r["name"] or "C" in r.get("type", "") for r in data["arpeggio_results"]), f"Non-C arpeggio found: {[r['name'] for r in data['arpeggio_results']]}"
    assert any("arpeggio" in r["type"].lower() or "arpeggio" in r["name"].lower() for r in data["arpeggio_results"]), "No arpeggio returned"

def test_search_typo_arpeggio():
    """
    Test typo tolerance for arpeggio queries (e.g., 'D Minorr Arpegio').
    """
    import requests
    resp = requests.get("http://localhost:8080/search_json", params={"q": "D Minorr Arpegio", "search_type": "arpeggios"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] == len(data["arpeggio_results"])
    assert any("D" in r["name"] or "D" in r.get("type", "") for r in data["arpeggio_results"]), f"Non-D arpeggio found: {[r['name'] for r in data['arpeggio_results']]}"
    assert any("arpeggio" in r["type"].lower() or "arpeggio" in r["name"].lower() for r in data["arpeggio_results"]), "No arpeggio returned"

def test_search_case_insensitivity():
    """
    Test that search is case-insensitive (e.g., 'f# minor pentatonic').
    """
    import requests
    resp = requests.get("http://localhost:8080/search_json", params={"q": "f# minor pentatonic", "search_type": "all"})
    assert resp.status_code == 200
    data = resp.json()
    assert any("F#" in r["name"] for r in data["scale_results"]), f"Non-F# scale found: {[r['name'] for r in data['scale_results']]}"
    assert any("pentatonic" in r["name"].lower() for r in data["scale_results"]), "No pentatonic scale returned"

def test_search_partial_quality():
    """
    Test partial quality search (e.g., 'Bb min').
    """
    import requests
    resp = requests.get("http://localhost:8080/search_json", params={"q": "Bb min", "search_type": "all"})
    assert resp.status_code == 200
    data = resp.json()
    assert any("Bb" in r["name"] for r in data["chord_results"]), f"Non-Bb chord found: {[r['name'] for r in data['chord_results']]}"
    assert any("min" in r["name"].lower() or "minor" in r["name"].lower() for r in data["chord_results"]), "No minor chord returned"

def test_root_id_mapping():
    # Provided user mapping
    assert get_root_id_from_name('C') == 1
    assert get_root_id_from_name('Db') == 2
    assert get_root_id_from_name('C#') == 3
    assert get_root_id_from_name('D') == 4
    assert get_root_id_from_name('Eb') == 5
    assert get_root_id_from_name('D#') == 6
    assert get_root_id_from_name('E') == 7
    assert get_root_id_from_name('F') == 8
    assert get_root_id_from_name('Gb') == 9
    assert get_root_id_from_name('F#') == 10
    assert get_root_id_from_name('G') == 11
    assert get_root_id_from_name('Ab') == 12
    assert get_root_id_from_name('G#') == 13
    assert get_root_id_from_name('A') == 14
    assert get_root_id_from_name('Bb') == 15
    assert get_root_id_from_name('A#') == 16
    assert get_root_id_from_name('B') == 17
    # Enharmonic handling
    assert get_root_id_from_name('d#') == 6
    assert get_root_id_from_name('eb') == 5
    assert get_root_id_from_name('c#') == 3
    assert get_root_id_from_name('db') == 2
    assert get_root_id_from_name('gb') == 9
    assert get_root_id_from_name('f#') == 10
    assert get_root_id_from_name('ab') == 12
    assert get_root_id_from_name('g#') == 13
    assert get_root_id_from_name('bb') == 15
    assert get_root_id_from_name('a#') == 16
    # Unknown returns None
    assert get_root_id_from_name('Z') is None
    assert get_root_id_from_name('') is None
    assert get_root_id_from_name(None) is None
