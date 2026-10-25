"""Tests for positionfinder.views_search.

The application monkey-patches ``views_search.search_json`` and ``views_search.search_chords`` at start-up
(see search_integration.py).  These tests load a pristine copy of the module so the original code paths are
exercised; the patched URL behaviour is covered in test_views_urls_pages.py and test_search_integration.py.
"""

import importlib.util
import json
import logging

import pytest
from django.test import RequestFactory

from positionfinder import views_search
from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.models_chords import ChordNotes, ChordPosition

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("music_data")]
RF = RequestFactory()


@pytest.fixture(scope="module")
def vs():
    spec = importlib.util.spec_from_file_location(
        "positionfinder.views_search_unpatched", views_search.__file__
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get(query=None, **headers):
    request = RF.get("/search", query or {}, **headers)
    request.session = {}
    return request


def make_chord_copies(type_name, chord_name, tonal_root, count=1):
    """Duplicate real voicings with a different tonal_root (the fixture only has tonal_root=0 templates)."""
    created = []
    for template in ChordNotes.objects.filter(type_name=type_name, chord_name=chord_name).order_by(
        "id"
    )[:count]:
        template.pk = None
        template.tonal_root = tonal_root
        template.save()
        created.append(template)
    return created


# ----------------------------------------------------------------------------- log_debug_info
def test_log_debug_info_with_and_without_data(vs, caplog):
    with caplog.at_level(logging.DEBUG, logger=vs.logger.name):
        vs.log_debug_info("hello")
        vs.log_debug_info("with dict", {"a": 1})
        vs.log_debug_info("with text", "plain")
    text = caplog.text
    assert "DEBUG: hello" in text
    assert 'DATA: {"a": 1}' in text
    assert "DATA: plain" in text


# ----------------------------------------------------------------------------- search_json
def search_json_data(vs, **params):
    response = vs.search_json(get(params))
    return response.status_code, json.loads(response.content)


def test_search_json_blank_query_returns_empty_structure(vs):
    status, data = search_json_data(vs, q="   ")
    assert status == 200
    assert data == {
        "query": "",
        "total_results": 0,
        "chord_results": [],
        "scale_results": [],
        "arpeggio_results": [],
    }


def test_search_json_scales_only(vs):
    status, data = search_json_data(vs, q="C major", search_type="scales")
    assert status == 200
    assert data["query"] == "C major"
    assert data["chord_results"] == [] and data["arpeggio_results"] == []
    first = data["scale_results"][0]
    assert first["name"] == "C Major"
    assert first["url"] == "/?root=1&models_select=1&notes_options_select=1&position_select=0"
    assert data["total_results"] == len(data["scale_results"]) == 3


def test_search_json_arpeggios_only(vs):
    status, data = search_json_data(vs, q="C major", search_type="arpeggios")
    assert data["scale_results"] == [] and data["chord_results"] == []
    assert data["arpeggio_results"][0]["name"] == "C Major Triad"
    assert data["total_results"] == len(data["arpeggio_results"])


def test_search_json_all_with_scale_query_uses_only_scale_search(vs):
    _, data = search_json_data(vs, q="G pentatonic")
    assert sorted(s["name"] for s in data["scale_results"]) == [
        "G Minor Pentatonic",
        "G Pentatonic",
    ]
    assert data["arpeggio_results"] == []


def test_search_json_all_with_arpeggio_query(vs):
    _, data = search_json_data(vs, q="C minor arpeggio")
    assert data["scale_results"] == [] and data["chord_results"] == []
    assert data["arpeggio_results"][0]["name"] == "C Minor Triad"


def test_search_json_chord_search_type_uses_search_chords(vs, monkeypatch):
    monkeypatch.setattr(vs, "search_chords", lambda q: [{"id": 1, "name": f"stub {q}"}])
    _, data = search_json_data(vs, q="Am7", search_type="chords")
    assert data["chord_results"] == [{"id": 1, "name": "stub Am7"}]
    assert data["total_results"] == 1


def test_search_json_all_with_chord_query_calls_chord_search(vs, monkeypatch):
    calls = []
    monkeypatch.setattr(vs, "search_chords", lambda q: calls.append(q) or [])
    _, data = search_json_data(vs, q="Am7")
    assert calls == ["Am7"]
    assert data["total_results"] == 0


def test_search_json_unknown_search_type_returns_nothing(vs):
    _, data = search_json_data(vs, q="C major", search_type="bogus")
    assert data["total_results"] == 0


def test_search_json_error_returns_500_with_message(vs, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("kaput")

    monkeypatch.setattr(vs, "search_scales", boom)
    status, data = search_json_data(vs, q="C major", search_type="scales")
    assert status == 500
    assert data["error"] == "kaput"
    assert "RuntimeError" in data["traceback"]


# ----------------------------------------------------------------------------- unified_search_view
def test_unified_view_empty_query_renders_template_without_results(vs):
    response = vs.unified_search_view(get())
    assert response.status_code == 200
    assert b"<html" in response.content.lower()


def test_unified_view_blank_query_ajax_json(vs):
    response = vs.unified_search_view(
        get({"search_query": "  "}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    )
    assert json.loads(response.content) == {
        "results": {"chords": [], "scales": [], "arpeggios": []},
        "total_count": 0,
        "search_query": "",
        "search_type": "all",
    }


def test_unified_view_ajax_all_types(vs, monkeypatch):
    monkeypatch.setattr(vs, "search_chords", lambda q: [{"id": 7, "name": "stub"}])
    response = vs.unified_search_view(
        get({"search_query": "C major"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    )
    data = json.loads(response.content)
    assert data["results"]["chords"] == [{"id": 7, "name": "stub"}]
    assert data["results"]["scales"][0]["name"] == "C Major"
    assert data["results"]["arpeggios"][0]["name"] == "C Major Triad"
    assert data["total_count"] == 1 + len(data["results"]["scales"]) + len(
        data["results"]["arpeggios"]
    )


@pytest.mark.parametrize(
    "search_type,filled", [("chords", "chords"), ("scales", "scales"), ("arpeggios", "arpeggios")]
)
def test_unified_view_search_type_limits_result_groups(vs, monkeypatch, search_type, filled):
    monkeypatch.setattr(vs, "search_chords", lambda q: [{"id": 7}])
    response = vs.unified_search_view(
        get(
            {"search_query": "C major", "search_type": search_type},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
    )
    results = json.loads(response.content)["results"]
    for group, items in results.items():
        assert bool(items) == (group == filled)


def test_unified_view_html_context(vs, monkeypatch):
    monkeypatch.setattr(vs, "search_chords", lambda q: [])
    response = vs.unified_search_view(get({"search_query": "C major", "search_type": "scales"}))
    assert response.status_code == 200
    assert b"C Major" in response.content


# ----------------------------------------------------------------------------- search_chords
def test_search_chords_returns_empty_list_for_templates_with_zero_tonal_root(vs):
    assert vs.search_chords("C major") == []


@pytest.mark.xfail(
    strict=True,
    reason="BUG: search_chords filters tonal_root against ROOT_NAME_TO_ID (a Root row id, "
    "C=1) although tonal_root is a pitch (C=0), so a plain 'C major' query finds "
    "no chord voicings at all (only the monkey patched replacement works)",
)
def test_search_chords_finds_c_major_voicings(vs):
    assert vs.search_chords("C major")


def test_search_chords_chord_and_type_branch(vs):
    make_chord_copies("V1", "Major 7", tonal_root=1, count=2)
    results = vs.search_chords("C major7 V1")
    assert results
    assert {r["type"] for r in results} == {"V1"}
    assert all(r["name"].startswith("C ") for r in results)
    assert all(
        "models_select=3" in r["url"] and "type_options_select=V1" in r["url"] for r in results
    )


def test_search_chords_chord_and_type_branch_without_rows_is_empty(vs):
    assert vs.search_chords("C minor7 V1") == []


def test_search_chords_chord_only_branch(vs):
    make_chord_copies("Triads", "Major", tonal_root=1)
    results = vs.search_chords("C major")
    assert results
    assert all(r["type"] == "Triads" for r in results)
    assert results[0]["name"] == "C Major"


def test_search_chords_type_only_branch(vs):
    make_chord_copies("V1", "Major 7", tonal_root=1)
    results = vs.search_chords("C pentatonic V1")
    assert results and all(r["type"] == "V1" for r in results)


def test_search_chords_no_matching_chord_or_type(vs):
    assert vs.search_chords("C pentatonic") == []


def test_search_chords_errors_are_swallowed(vs, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("db down")

    monkeypatch.setattr(vs.ChordNotes.objects, "values_list", boom)
    assert vs.search_chords("C major") == []


# ----------------------------------------------------------------------------- process_chord_results
def test_process_chord_results_without_root_note(vs):
    chord = ChordNotes.objects.filter(type_name="Triads", chord_name="Major", range="e - g").first()
    results = vs.process_chord_results(ChordNotes.objects.filter(pk=chord.pk))
    assert len(results) == 1
    item = results[0]
    assert item["id"] == chord.id
    assert item["name"] == "Major"
    assert item["type"] == "Triads"
    assert item["category"] == "Chords"
    assert item["positions"] == list(
        ChordPosition.objects.filter(notes_name=chord).values_list("inversion_order", flat=True)
    )
    assert item["notes"] == [chord.first_note, chord.second_note, chord.third_note]
    assert item["intervals"] == [(n - chord.first_note) % 12 for n in item["notes"]]
    assert item["url"].endswith("&position_select=Root+Position")


def test_process_chord_results_root_filter_by_tonal_root_and_name_prefix(vs):
    copies = make_chord_copies(
        "Triads", "Major", tonal_root=14, count=1
    )  # 14 == ROOT_NAME_TO_ID['A']
    qs = ChordNotes.objects.filter(type_name="Triads", chord_name="Major")
    results = vs.process_chord_results(qs, root_note="A")
    assert [r["id"] for r in results] == [copies[0].id]
    assert results[0]["name"] == "A Major"
    assert "root=14&" in results[0]["url"]


def test_process_chord_results_root_without_match_keeps_everything(vs):
    qs = ChordNotes.objects.filter(type_name="Triads", chord_name="Major")
    results = vs.process_chord_results(qs, root_note="Bb")
    expected = [c for c in qs if "e" in c.range and "E" not in c.range]
    assert len(results) == len(expected) > 0
    assert all(r["name"] == "Bb Major" for r in results)


def test_process_chord_results_name_prefix_fallback(vs):
    chord = ChordNotes.objects.filter(type_name="Triads", chord_name="Major").first()
    chord.pk = None
    chord.chord_name = "C Major special"
    chord.range = "e - g"
    chord.save()
    results = vs.process_chord_results(ChordNotes.objects.filter(pk=chord.pk), root_note="C")
    assert [r["name"] for r in results] == ["C Major special"]


def test_process_chord_results_prioritises_lowercase_e_ranges(vs):
    qs = ChordNotes.objects.filter(type_name="V1", chord_name="Major 7")
    results = vs.process_chord_results(qs)
    ids = {r["id"] for r in results}
    expected = {c.id for c in qs if "e" in c.range and "E" not in c.range}
    assert ids == expected


# ----------------------------------------------------------------------------- search_scales
def test_search_scales_template_fallback_for_other_roots(vs):
    results = vs.search_scales("G pentatonic")
    assert {r["name"] for r in results} == {"G Minor Pentatonic", "G Pentatonic"}
    assert all(
        r["url"].startswith("/?root=11&models_select=1&notes_options_select=") for r in results
    )
    assert all(r["type"] == "Scales" for r in results)


def test_search_scales_prefers_root_specific_rows(vs):
    template = Notes.objects.filter(
        category_id=1, note_name__icontains="pentatonic", tonal_root=0
    ).first()
    template.pk = None
    template.tonal_root = Root.objects.get(name="G").pitch
    template.save()
    results = vs.search_scales("G pentatonic")
    assert [r["id"] for r in results] == [template.pk]


def test_search_scales_numeric_query_filters_by_pk(vs):
    results = vs.search_scales("1")
    assert [r["id"] for r in results] == [1]
    assert results[0]["name"] == "C Major"


def test_search_scales_unresolvable_root(vs, monkeypatch):
    monkeypatch.setattr(vs, "resolve_root", lambda note: None)
    assert vs.search_scales("C major") == []


def test_search_scales_no_match(vs):
    assert vs.search_scales("C locrian") == []


def test_search_scales_no_scale_rows(vs):
    Notes.objects.filter(category_id=1).delete()
    assert vs.search_scales("C major") == []


def test_search_scales_swallows_errors(vs, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("bad")

    monkeypatch.setattr(vs, "process_scale_results", boom)
    assert vs.search_scales("C major") == []


# ----------------------------------------------------------------------------- process_scale_results
def test_process_scale_results_fields(vs):
    scale = Notes.objects.get(pk=1)
    [item] = vs.process_scale_results(
        Notes.objects.filter(pk=1), user_note="D", user_quality="major"
    )
    assert item == {
        "id": 1,
        "name": "D Major",
        "type": "Scales",
        "notes": item["notes"],
        "intervals": [(n - item["notes"][0]) % 12 for n in item["notes"]],
        "url": "/?root=4&models_select=1&notes_options_select=1&position_select=0",
    }
    assert item["notes"][:3] == [scale.first_note, scale.second_note, scale.third_note]


def test_process_scale_results_keeps_name_if_already_prefixed(vs):
    scale = Notes.objects.get(pk=1)
    scale.note_name = "C Major"
    scale.save()
    [item] = vs.process_scale_results(Notes.objects.filter(pk=1), user_note="C")
    assert item["name"] == "C Major"


def test_process_scale_results_without_user_note(vs):
    [item] = vs.process_scale_results(Notes.objects.filter(pk=1))
    assert item["name"] == "Major"
    assert "root=1&" in item["url"]


# ----------------------------------------------------------------------------- search_arpeggios
def test_search_arpeggios_minor_group(vs):
    results = vs.search_arpeggios(note="C", quality="minor", type_="arpeggio")
    assert results
    assert results[0]["name"] == "C Minor Triad"
    assert results[0]["type"] == "Arpeggio"
    assert results[0]["notes"] == [0, 3, 7]
    assert results[0]["intervals"] == [0, 3, 7]
    assert results[0]["url"] == "/?root=1&models_select=2&notes_options_select=16&position_select=0"


def test_search_arpeggios_exact_quality_sorted_first(vs):
    results = vs.search_arpeggios(note="C", quality="major", type_="arpeggio")
    names = [r["name"] for r in results]
    first_non_major = next((i for i, n in enumerate(names) if "major" not in n.lower()), len(names))
    assert all("major" in n.lower() for n in names[:first_non_major])
    assert all("major" not in n.lower() for n in names[first_non_major:])


def test_search_arpeggios_abbreviated_quality_uses_group(vs):
    assert vs.search_arpeggios(note="C", quality="dim")
    assert vs.search_arpeggios(note="C", quality="aug")
    assert vs.search_arpeggios(note="C", quality="dom")


def test_search_arpeggios_unknown_quality_uses_direct_filter(vs):
    results = vs.search_arpeggios(note="C", quality="triad")
    assert results and all("triad" in r["name"].lower() for r in results)


def test_search_arpeggios_unmatched_quality_returns_empty(vs):
    assert vs.search_arpeggios(note="C", quality="zzzz") == []


def test_search_arpeggios_without_quality_returns_all(vs):
    total = Notes.objects.filter(category__category_name__icontains="arpeggio").count()
    assert len(vs.search_arpeggios(note="C")) == total


def test_search_arpeggios_pentatonic_filter_on_list(vs):
    results = vs.search_arpeggios(note="C", quality="minor", type_="pentatonic")
    assert all("pentatonic" in r["name"].lower() for r in results)


def test_search_arpeggios_pentatonic_filter_on_queryset(vs):
    results = vs.search_arpeggios(note="C", type_="Pentatonic")
    assert all("pentatonic" in r["name"].lower() for r in results)


def test_search_arpeggios_other_root_in_names_and_urls(vs):
    results = vs.search_arpeggios(note="A", quality="minor")
    assert results[0]["name"].startswith("A ")
    assert "root=14&" in results[0]["url"]


def test_search_arpeggios_root_found_through_id_mapping(vs):
    Root.objects.filter(name="Db").update(name="Dflat")
    results = vs.search_arpeggios(note="Db", quality="minor")
    assert results and "root=2&" in results[0]["url"]


def test_search_arpeggios_unknown_root_uses_default_root_id(vs):
    results = vs.search_arpeggios(note="Zz", quality="minor")
    assert results and "root=14&" in results[0]["url"]


def test_search_arpeggios_without_note_uses_default_root(vs):
    results = vs.search_arpeggios(quality="minor")
    assert results[0]["name"].endswith("Minor Triad")
    assert "root=14&" in results[0]["url"]


def test_search_arpeggios_without_category(vs):
    NotesCategory.objects.filter(category_name__icontains="arpeggio").update(category_name="Other")
    assert vs.search_arpeggios(note="C", quality="minor") == []


def test_search_arpeggios_swallows_errors(vs, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("x")

    monkeypatch.setattr(vs, "process_arpeggio_results", boom)
    assert vs.search_arpeggios(note="C", quality="minor") == []


# ----------------------------------------------------------------------------- process_arpeggio_results
def test_process_arpeggio_results_resolves_root_by_name(vs):
    qs = Notes.objects.filter(pk=16)
    [item] = vs.process_arpeggio_results(qs, root_note="E")
    assert item["name"] == "E Minor Triad"
    assert "root=7&" in item["url"]


def test_process_arpeggio_results_resolves_root_via_mapping(vs):
    Root.objects.filter(name="Gb").update(name="Gflat")
    [item] = vs.process_arpeggio_results([Notes.objects.get(pk=16)], root_note="Gb")
    assert "root=9&" in item["url"]


def test_process_arpeggio_results_uses_given_root_object(vs):
    root = Root.objects.get(name="D")
    [item] = vs.process_arpeggio_results(Notes.objects.filter(pk=16), root_note="D", root_obj=root)
    assert "root=%d&" % root.id in item["url"]


def test_process_arpeggio_results_name_already_prefixed(vs):
    arp = Notes.objects.get(pk=16)
    arp.note_name = "C Minor Triad"
    arp.save()
    [item] = vs.process_arpeggio_results(Notes.objects.filter(pk=16), root_note="C")
    assert item["name"] == "C Minor Triad"


def test_process_arpeggio_results_skips_broken_rows(vs):
    class Broken:
        id = 99

        @property
        def note_name(self):
            raise RuntimeError("nope")

    assert vs.process_arpeggio_results([Broken()], root_note="C") == []
