"""views_helpers, context processors, PWA service worker, template tags and the chord-search integration."""

import json

import pytest
from django.http import JsonResponse
from django.template import Context, Template
from django.test import RequestFactory, override_settings

from fretboard.templatetags import custom_tags, filters
from positionfinder import search_integration, views_pwa, views_search
from positionfinder.context_processors import app_version_context, unified_menu_context
from positionfinder.context_stripe import stripe_url_context
from positionfinder.models_chords import ChordNotes
from positionfinder.templatetags import position_tags
from positionfinder.views_helpers import get_common_context

RF = RequestFactory()


def session_request(path="/", query=None, session=None):
    request = RF.get(path, query or {})
    request.session = dict(session or {})
    return request


# ----------------------------------------------------------------------------- get_common_context
@override_settings(USE_OPTIMIZED_CHORD_VIEW=False)
def test_common_context_falls_back_to_settings():
    assert get_common_context(session_request()) == {"use_optimized_chord_view": False}


@override_settings(USE_OPTIMIZED_CHORD_VIEW=True)
def test_common_context_setting_true():
    assert get_common_context(session_request())["use_optimized_chord_view"] is True


@override_settings()
def test_common_context_without_setting_defaults_to_false():
    from django.conf import settings

    del settings.USE_OPTIMIZED_CHORD_VIEW
    assert get_common_context(session_request())["use_optimized_chord_view"] is False


@pytest.mark.parametrize(
    "raw,expected",
    [("true", True), ("YES", True), ("1", True), ("no", False), ("0", False), ("garbage", False)],
)
def test_common_context_query_parameter_is_parsed_and_stored(raw, expected):
    request = session_request(query={"optimized": raw})
    assert get_common_context(request)["use_optimized_chord_view"] is expected
    assert request.session["use_optimized_chord_view"] is expected


@override_settings(USE_OPTIMIZED_CHORD_VIEW=False)
def test_common_context_session_wins_over_query_and_settings():
    request = session_request(
        query={"optimized": "false"}, session={"use_optimized_chord_view": True}
    )
    assert get_common_context(request)["use_optimized_chord_view"] is True
    assert request.session["use_optimized_chord_view"] is True


# ----------------------------------------------------------------------------- simple context processors
def test_app_version_context_reads_settings():
    with override_settings(VERSION="9.9"):
        assert app_version_context(RF.get("/")) == {"APP_VERSION": "9.9"}


def test_app_version_context_default_when_setting_missing():
    from django.conf import settings

    with override_settings():
        del settings.VERSION
        assert app_version_context(RF.get("/")) == {"APP_VERSION": "2.1"}


def test_stripe_context_with_and_without_url():
    with override_settings(STRIPE_DONATE_URL="https://example.test/donate"):
        assert stripe_url_context(RF.get("/")) == {
            "STRIPE_DONATE_URL": "https://example.test/donate"
        }
    with override_settings(STRIPE_DONATE_URL=None):
        assert stripe_url_context(RF.get("/")) == {"STRIPE_DONATE_URL": None}


# ----------------------------------------------------------------------------- unified_menu_context
@pytest.mark.django_db
@pytest.mark.usefixtures("music_data")
class TestUnifiedMenuContext:
    def test_roots_are_ordered_by_pitch_then_name(self):
        ctx = unified_menu_context(RF.get("/"))
        roots = list(ctx["unified_menu_root_options"])
        assert len(roots) == 17
        assert [(r.pitch, r.name) for r in roots] == sorted((r.pitch, r.name) for r in roots)

    def test_scale_and_arpeggio_options_by_category(self):
        ctx = unified_menu_context(RF.get("/"))
        scales = list(ctx["unified_menu_scale_options"])
        arps = list(ctx["unified_menu_arpeggio_options"])
        assert scales and arps
        assert {n.category_id for n in scales} == {1}
        assert {n.category_id for n in arps} == {2}
        assert [n.ordering for n in scales] == sorted(n.ordering for n in scales)

    def test_chord_type_options_standard_and_natural_v_sorting(self):
        options = unified_menu_context(RF.get("/"))["unified_menu_chord_type_options"]
        assert options["standard_types"] == ["Triads", "Spread Triads"]
        v = options["v_system_types"]
        assert v[0] == "V1"
        assert v == sorted(v, key=lambda s: int(s[1:]))

    def test_unknown_type_names_are_ignored(self):
        template = ChordNotes.objects.first()
        for name in ("Foo", "", "Vx"):
            template.pk = None
            template.type_name = name
            template.save()
        options = unified_menu_context(RF.get("/"))["unified_menu_chord_type_options"]
        assert "Foo" not in options["standard_types"] + options["v_system_types"]
        assert "" not in options["v_system_types"] and "Vx" not in options["v_system_types"]

    def test_without_chords_triads_is_still_offered(self):
        ChordNotes.objects.all().delete()
        options = unified_menu_context(RF.get("/"))["unified_menu_chord_type_options"]
        assert options == {"standard_types": ["Triads"], "v_system_types": []}

    def test_only_spread_triads_gets_triads_prepended(self):
        ChordNotes.objects.exclude(type_name="Spread Triads").delete()
        options = unified_menu_context(RF.get("/"))["unified_menu_chord_type_options"]
        assert options["standard_types"] == ["Triads", "Spread Triads"]
        assert options["v_system_types"] == []


# ----------------------------------------------------------------------------- PWA service worker internals
def test_shell_assets_list_has_versioned_css_and_js():
    versioned = [a for a, flag in views_pwa.SHELL_ASSETS if flag]
    assert versioned == ["studio/studio.css", "studio/js/app.js"]


def test_file_digest_is_content_hash_and_memoised(tmp_path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"hello")
    stat = f.stat()
    views_pwa._file_digest.cache_clear()
    first = views_pwa._file_digest(str(f), stat.st_mtime_ns, stat.st_size)
    assert first == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    f.write_bytes(b"HELLO")  # same size, but the memoised stat key is unchanged
    assert views_pwa._file_digest(str(f), stat.st_mtime_ns, stat.st_size) == first
    assert views_pwa._file_digest.cache_info().hits >= 1


def test_shell_fingerprint_is_stable_and_twelve_hex_chars():
    first = views_pwa._shell_fingerprint()
    assert first == views_pwa._shell_fingerprint()
    assert len(first) == 12 and int(first, 16) >= 0


def test_shell_fingerprint_changes_when_asset_content_changes(tmp_path, monkeypatch):
    asset = tmp_path / "x.js"
    asset.write_text("one")
    monkeypatch.setattr(views_pwa, "SHELL_ASSETS", (("x.js", False),))
    monkeypatch.setattr(views_pwa.finders, "find", lambda name: str(asset))
    before = views_pwa._shell_fingerprint()
    asset.write_text("two!")
    assert views_pwa._shell_fingerprint() != before


def test_shell_fingerprint_marks_missing_assets(monkeypatch):
    monkeypatch.setattr(views_pwa, "SHELL_ASSETS", (("gone.js", False),))
    monkeypatch.setattr(views_pwa.finders, "find", lambda name: None)
    missing = views_pwa._shell_fingerprint()
    monkeypatch.setattr(views_pwa, "SHELL_ASSETS", (("other.js", False),))
    assert views_pwa._shell_fingerprint() != missing


@pytest.mark.django_db
class TestServiceWorkerView:
    def test_body_contains_version_precache_and_catalog_path(self, client):
        response = client.get("/sw.js")
        body = response.content.decode()
        assert "const VERSION = '2.1\\u002D" in body
        assert "const CATALOG_PATH = '/api/catalog/';" in body
        assert '"/"' in body.split("PRECACHE_URLS = ")[1]
        assert "/static/studio/studio.css?v=2.1" in body
        assert "/static/studio/js/theory.js" in body and "theory.js?v=" not in body

    def test_version_follows_setting(self, client):
        with override_settings(VERSION="7.7"):
            body = client.get("/sw.js").content.decode()
        assert "const VERSION = '7.7\\u002D" in body
        assert "studio.css?v=7.7" in body

    def test_precache_json_escapes_angle_brackets(self, rf, monkeypatch):
        monkeypatch.setattr(views_pwa, "static", lambda path: f"/s/<{path}")
        monkeypatch.setattr(views_pwa, "SHELL_ASSETS", (("a.js", False),))
        body = views_pwa.service_worker(rf.get("/sw.js")).content.decode()
        assert "\\u003ca.js" in body and "<a.js" not in body

    def test_head_is_allowed_and_options_is_not(self, client):
        assert client.head("/sw.js").status_code == 200
        assert client.options("/sw.js").status_code == 405


# ----------------------------------------------------------------------------- position_tags
@pytest.mark.parametrize(
    "name,expected",
    [
        ("eString", "High E (1st)"),
        ("bString", "B (2nd)"),
        ("gString", "G (3rd)"),
        ("dString", "D (4th)"),
        ("AString", "A (5th)"),
        ("ELowString", "Low E (6th)"),
        ("highAString", "High A (0)"),
        ("lowBString", "Low B (7th)"),
        ("mystery", "mystery"),
    ],
)
def test_friendly_string_name(name, expected):
    assert position_tags.friendly_string_name(name) == expected


@pytest.mark.parametrize(
    "order,expected",
    [
        (1, "Open Position (0-4 Frets)"),
        (7, "12th Position/Octave (12-16 Frets)"),
        (9, "High Extended Position (For 8-string)"),
        (10, "Position 10"),
        (0, "Position 0"),
    ],
)
def test_position_description(order, expected):
    assert position_tags.position_description(order) == expected


@pytest.mark.parametrize(
    "order,expected",
    [
        (1, "Beginner"),
        (2, "Beginner-Intermediate"),
        (3, "Intermediate"),
        (5, "Intermediate-Advanced"),
        (6, "Advanced"),
        (8, "Advanced (8-string)"),
        (42, "Intermediate"),
    ],
)
def test_position_difficulty(order, expected):
    assert position_tags.position_difficulty(order) == expected


@pytest.mark.parametrize(
    "order,expected",
    [
        (0, "position-beginner"),
        (1, "position-beginner"),
        (2, "position-beginner"),
        (3, "position-intermediate"),
        (5, "position-intermediate"),
        (6, "position-advanced"),
        (9, "position-advanced"),
    ],
)
def test_position_color_class(order, expected):
    assert position_tags.position_color_class(order) == expected


def test_position_tags_in_template():
    out = Template(
        "{% load position_tags %}{{ s|friendly_string_name }}|{{ p|position_difficulty }}"
    ).render(Context({"s": "eString", "p": 6}))
    assert out == "High E (1st)|Advanced"


# ----------------------------------------------------------------------------- fretboard template tags
def test_custom_tags_times_is_zero_based():
    assert list(custom_tags.times(3)) == [0, 1, 2]


def test_filters_times_is_one_based_inclusive():
    assert list(filters.times(3)) == [1, 2, 3]
    assert list(filters.times(0)) == []


@pytest.mark.parametrize(
    "num,expected", [(0, "zero"), (5, "five"), (17, "seventeen"), (18, "18"), (-1, "-1")]
)
def test_to_english(num, expected):
    assert filters.to_english(num) == expected


@pytest.mark.parametrize(
    "num,expected",
    [
        (0, ""),
        (1, "I"),
        (4, "IV"),
        (9, "IX"),
        (14, "XIV"),
        (40, "XL"),
        (90, "XC"),
        (400, "CD"),
        (1994, "MCMXCIV"),
        (3999, "MMMCMXCIX"),
    ],
)
def test_to_roman(num, expected):
    assert filters.to_roman(num) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("bb2", "Bb2"),
        ("db3", "Db3"),
        ("eb4", "Eb4"),
        ("ab1", "Ab1"),
        ("cs3", "C#3"),
        ("as2", "A#2"),
        ("fs0", "F#0"),
        ("c3", "C3"),
        ("g2", "G2"),
        ("b1", "B1"),
    ],
)
def test_format_note_name(raw, expected):
    assert filters.format_note_name(raw) == expected


def test_get_notes_returns_enharmonic_names_for_fret():
    assert filters.get_notes("eString", 1) == ["f2"]
    assert filters.get_notes("eString", 2) == ["gb2", "fs2"]
    assert filters.get_notes("lowBString", 17) == ["e1"]


def test_get_notes_out_of_range_or_unknown_string():
    assert filters.get_notes("eString", 18) == []
    assert filters.get_notes("nopeString", 3) == []


def test_filters_in_template():
    out = Template("{% load filters %}{% for i in 3|times %}{{ i|to_roman }}{% endfor %}").render(
        Context()
    )
    assert out == "IIIIII"


# ----------------------------------------------------------------------------- search_integration
def stub_original(payload):
    return lambda request: JsonResponse(payload)


@pytest.mark.django_db
@pytest.mark.usefixtures("music_data")
class TestSearchIntegration:
    def test_integration_is_active_after_startup(self):
        assert views_search.search_chords is search_integration.integrated_search_chords

    def test_empty_query_uses_original_response(self):
        original = stub_original({"marker": 1})
        response = search_integration.integrated_search_json(RF.get("/s"), original)
        assert json.loads(response.content) == {"marker": 1}

    def test_non_chord_query_uses_original_response(self):
        original = stub_original({"marker": 2})
        response = search_integration.integrated_search_json(
            RF.get("/s", {"q": "G pentatonic"}), original
        )
        assert json.loads(response.content) == {"marker": 2}

    def test_chord_query_replaces_chord_results_in_json_response(self):
        original = stub_original(
            {
                "query": "Am7",
                "total_results": 1,
                "chord_results": [{"old": True}],
                "scale_results": [{"s": 1}, {"s": 2}],
                "arpeggio_results": [{"a": 1}],
            }
        )
        response = search_integration.integrated_search_json(RF.get("/s", {"q": "Am7"}), original)
        data = json.loads(response.content)
        assert data["chord_results"], "improved search must return A minor 7 voicings"
        first = data["chord_results"][0]
        assert first["note_name"] == "A Minor 7"
        assert first["intervals"] == [0, 3, 7, 10]
        assert first["url"].startswith("/?root=14&models_select=3")
        assert set(first) == {"note_name", "description", "intervals", "url"}
        assert data["total_results"] == 2 + 1 + len(data["chord_results"])
        assert data["scale_results"] == [{"s": 1}, {"s": 2}]

    def test_word_chord_in_query_triggers_chord_enhancement(self):
        original = stub_original({"scale_results": [], "arpeggio_results": []})
        response = search_integration.integrated_search_json(
            RF.get("/s", {"q": "C scale chord"}), original
        )
        data = json.loads(response.content)
        assert "chord_results" in data
        assert data["total_results"] == len(data["chord_results"])

    def test_chord_query_with_drf_style_response_object(self):
        class FakeResponse:
            def __init__(self):
                self.data = {"scale_results": [1], "arpeggio_results": [2, 3], "chord_results": []}

        original = lambda request: FakeResponse()  # noqa: E731
        response = search_integration.integrated_search_json(RF.get("/s", {"q": "Am7"}), original)
        assert response.data["chord_results"]
        assert response.data["total_results"] == 3 + len(response.data["chord_results"])

    def test_integrated_search_chords_delegates_to_improved_search(self):
        results = search_integration.integrated_search_chords("Am7")
        assert results and results[0]["name"] == "A Minor 7"

    def test_apply_integration_replaces_functions(self, monkeypatch):
        sentinel_json, sentinel_chords = views_search.search_json, views_search.search_chords
        monkeypatch.setattr(views_search, "search_json", sentinel_json)
        monkeypatch.setattr(views_search, "search_chords", sentinel_chords)
        monkeypatch.setattr(
            search_integration,
            "integrated_search_chords",
            search_integration.integrated_search_chords,
        )
        assert search_integration.apply_chord_search_integration() is True
        assert views_search.search_chords is search_integration.integrated_search_chords
        assert views_search.search_json is not sentinel_json
        response = views_search.search_json(RF.get("/s", {"q": "  "}))
        assert json.loads(response.content)["total_results"] == 0

    def test_apply_integration_reports_failure(self, monkeypatch, caplog):
        monkeypatch.delattr(views_search, "search_chords")
        assert search_integration.apply_chord_search_integration() is False
        assert "Failed to integrate improved chord search" in caplog.text
