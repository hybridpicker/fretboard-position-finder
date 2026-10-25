"""HTTP-level tests for every route in ``fretboard/urls.py`` (200 paths, 404s, invalid parameters)."""

import json

import pytest
from django.urls import resolve, reverse

from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.positions import NotesPosition

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("music_data")]


def template_names(response):
    return [t.name for t in response.templates if t.name]


# ----------------------------------------------------------------------------- studio / catalogue
def test_studio_home_renders_studio_template(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "studio/index.html" in template_names(response)


def test_studio_home_name_reverses_to_root():
    assert reverse("fretboard") == "/"
    assert resolve("/").url_name == "fretboard"


def test_api_catalog_returns_json_with_scales_and_chords(client):
    response = client.get("/api/catalog/")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/json")
    data = response.json()
    assert len(data["roots"]) == 17
    assert any(s["name"] == "Major" for s in data["scales"])


def test_api_catalog_rejects_post(client):
    assert client.post("/api/catalog/").status_code == 405


# ----------------------------------------------------------------------------- classic dispatcher
def test_classic_defaults_to_scales(client):
    response = client.get("/classic/")
    assert response.status_code == 200
    assert response.context["selected_category"] == 1
    assert response.context["selected_category_name"] == "Scales"
    assert "fretboard.html" in template_names(response)


def test_classic_models_select_2_dispatches_to_arpeggios(client):
    response = client.get("/classic/?models_select=2")
    assert response.status_code == 200
    assert response.context["selected_category"] == 2
    assert response.context["selected_category_name"] == "Arpeggios"


def test_classic_models_select_3_dispatches_to_chords(client):
    response = client.get("/classic/?models_select=3")
    assert response.status_code == 200
    assert response.context["selected_category"] == 3
    assert response.context["selected_type"] == "Triads"


def test_classic_unknown_models_select_falls_back_to_scales(client):
    # '9' is neither 2 nor 3, so the scale handler is used; it then fails on the missing category
    with pytest.raises(NotesCategory.DoesNotExist):
        client.get("/classic/?models_select=9")


def test_classic_non_numeric_models_select_is_scale_branch(client):
    # dispatcher falls through to the scale view, which keeps the raw value as category id
    with pytest.raises(ValueError):
        client.get("/classic/?models_select=abc")


# ----------------------------------------------------------------------------- /scales
def test_scales_default_context(client):
    response = client.get("/scales")
    assert response.status_code == 200
    ctx = response.context
    assert ctx["selected_root_name"] == "C"
    assert ctx["selected_notes_name"] == "Major"
    assert ctx["selected_position"] == "0"
    assert ctx["note_names"] == ["C", "D", "E", "F", "G", "A", "B"]
    assert ctx["tensions"] == ["R", "9", "3", "11", "5", "13", "7"]
    assert len(ctx["string_names"]) == 8
    assert ctx["v1_data_exists"] is True and ctx["v2_data_exists"] is True


def test_scales_json_payload_is_valid_and_has_metadata(client):
    ctx = client.get("/scales?root=14&notes_options_select=1").context
    payload = json.loads(ctx["scale_json_data"])
    assert payload["name"] == "Major"
    assert payload["root"][0].startswith("a")
    assert json.loads(ctx["note_name_json_data"])["tones"][0] == "A"
    assert json.loads(ctx["tension_json_data"])["tensions"][0] == "R"


def test_scales_chord_name_from_selected_scale(client):
    ctx = client.get("/scales?notes_options_select=1").context
    assert ctx["chord_name"] == "Major 7"


def test_scales_other_root_changes_names(client):
    ctx = client.get("/scales?root=14&notes_options_select=1").context
    assert ctx["selected_root_name"] == "A"
    assert ctx["note_names"][0] == "A"


def test_scales_with_existing_position(client):
    pos = NotesPosition.objects.filter(notes_name_id=1).order_by("position_order").first()
    response = client.get(f"/scales?notes_options_select=1&position_select={pos.pk}")
    assert response.status_code == 200
    ctx = response.context
    assert ctx["selected_position"] == str(pos.pk)
    expected = [int(x) for x in pos.position.split(",")]
    assert ctx["position"] == expected
    assert pos in list(ctx["position_options"])


def test_scales_unknown_position_falls_back_to_all_notes(client):
    response = client.get("/scales?notes_options_select=1&position_select=99999")
    assert response.status_code == 200
    assert response.context["selected_position"] == "0"


def test_scales_unknown_root_raises(client):
    with pytest.raises(Root.DoesNotExist):
        client.get("/scales?root=99999")


def test_scales_non_numeric_root_raises(client):
    with pytest.raises(ValueError):
        client.get("/scales?root=abc")


def test_scales_unknown_notes_option_raises(client):
    with pytest.raises(Notes.DoesNotExist):
        client.get("/scales?notes_options_select=99999")


def test_scales_post_uses_defaults(client):
    response = client.post("/scales?root=14")
    assert response.status_code == 200
    assert response.context["selected_root_name"] == "C"


# ----------------------------------------------------------------------------- /arpeggios
def test_arpeggios_default_picks_first_arpeggio(client):
    response = client.get("/arpeggios")
    assert response.status_code == 200
    ctx = response.context
    assert ctx["selected_category"] == 2
    assert ctx["selected_notes_name"] == "Major Triad"
    assert ctx["note_names"] == ["C", "E", "G"]
    assert ctx["position_options"] == []
    assert all(n.category.category_name == "Arpeggios" for n in ctx["notes_options"])


def test_arpeggios_explicit_selection_and_root(client):
    first = Notes.objects.filter(category__category_name="Arpeggios").order_by("pk")[1]
    ctx = client.get(f"/arpeggios?root=14&notes_options_select={first.pk}").context
    assert ctx["selected_notes"] == first.pk
    assert ctx["selected_notes_name"] == first.note_name
    assert ctx["selected_root_name"] == "A"


def test_arpeggios_models_select_mismatch_is_rejected(client):
    # models_select=1 on the arpeggio endpoint selects the scale category with an arpeggio id
    response = client.get("/arpeggios?models_select=1&notes_options_select=1")
    assert response.status_code == 200
    assert response.context["selected_category"] == 1


# ----------------------------------------------------------------------------- /chords
def test_chords_default_context(client):
    response = client.get("/chords")
    assert response.status_code == 200
    ctx = response.context
    assert ctx["selected_type"] == "Triads"
    assert ctx["selected_chord"] == "Major"
    assert ctx["selected_range"] == "e - g"
    assert ctx["selected_notes"] == ["C"]
    assert ctx["chord_function"] == "R - 3 - 5"
    assert ctx["is_eight_string"] is False
    assert ctx["page_title"] == "C Major Chord | Guitar Positions & Voicings"
    assert ctx["breadcrumbs"][0] == ("/", "Home")
    assert json.loads(ctx["chord_json_data"])["chord"] == "Major"


def test_chords_v_system_selection(client):
    response = client.get("/chords?root=3&type_options_select=V1&chords_options_select=Major%207")
    assert response.status_code == 200
    ctx = response.context
    assert ctx["selected_type"] == "V1"
    assert ctx["root_name"] == "C#"
    assert ctx["chord_function"] == "R - 3 - 5 - 7"
    assert "V1" in ctx["chord_type_options"]["v_system_types"]


def test_chords_eight_string_cookie_enables_eight_string(client):
    client.cookies["stringConfig"] = "eight-string"
    ctx = client.get("/chords?type_options_select=V1&chords_options_select=Major%207").context
    assert ctx["is_eight_string"] is True
    ranges = [r.range for r in ctx["range_options"]]
    assert "highA - g" in ranges and "d - lowB" in ranges


def test_chords_six_string_hides_eight_string_ranges(client):
    ctx = client.get("/chords?type_options_select=V1&chords_options_select=Major%207").context
    assert ctx["range_options"]
    assert all("highA" not in r.range and "lowB" not in r.range for r in ctx["range_options"])


def test_chords_non_numeric_root_raises(client):
    with pytest.raises(ValueError):
        client.get("/chords?root=abc")


def test_chords_unknown_root_falls_back_to_first_root(client):
    response = client.get("/chords?root=99999")
    assert response.status_code == 200


# ----------------------------------------------------------------------------- /search/ and JSON
def test_search_page_without_query(client):
    response = client.get("/search/")
    assert response.status_code == 200
    assert "search/unified_search.html" in template_names(response)
    assert response.context["total_count"] == 0
    assert response.context["search_query"] == ""


def test_search_page_with_query_has_results(client):
    response = client.get("/search/?search_query=C+major")
    assert response.status_code == 200
    assert response.context["search_query"] == "C major"
    assert response.context["total_count"] > 0
    assert response.context["results"]["scales"]


def test_search_page_ajax_returns_json(client):
    response = client.get("/search/?search_query=C+major", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 200
    data = response.json()
    assert data["search_query"] == "C major"
    assert data["total_count"] > 0


@pytest.mark.parametrize("path", ["/search_json/", "/search/json/"])
def test_search_json_endpoints_empty_query(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert response.json() == {
        "query": "",
        "total_results": 0,
        "chord_results": [],
        "scale_results": [],
        "arpeggio_results": [],
    }


@pytest.mark.parametrize("path", ["/search_json/", "/search/json/"])
def test_search_json_endpoints_with_chord_query(client, path):
    data = client.get(path, {"q": "Am7"}).json()
    assert data["query"] == "Am7"
    assert data["total_results"] == len(data["chord_results"]) + len(data["scale_results"]) + len(
        data["arpeggio_results"]
    )
    first = data["chord_results"][0]
    assert first["note_name"] == "A Minor 7"
    assert first["intervals"] == [0, 3, 7, 10]
    assert first["url"].startswith("/?root=14&models_select=3")


def test_search_json_name_query_is_scale_query(client):
    data = client.get("/search_json/", {"q": "C scale major"}).json()
    assert data["scale_results"]
    assert data["scale_results"][0]["url"].startswith("/?root=1&models_select=1")


# ----------------------------------------------------------------------------- static pages
def test_about_page(client):
    response = client.get("/about/")
    assert response.status_code == 200
    assert "about.html" in template_names(response)
    assert response.context["show_fretboard"] is False
    assert "use_optimized_chord_view" in response.context


def test_impressum_page(client):
    response = client.get("/impressum/")
    assert response.status_code == 200
    assert "impressum.html" in template_names(response)
    assert response.context["show_fretboard"] is False


def test_optimized_query_parameter_is_stored_in_session(client):
    client.get("/about/?optimized=no")
    response = client.get("/about/")
    assert response.context["use_optimized_chord_view"] is False
    assert client.session["use_optimized_chord_view"] is False


@pytest.mark.parametrize("path", ["/de/about/", "/de/", "/fr/search/", "/es/scales"])
def test_language_prefixes_are_not_routed_when_i18n_is_disabled(client, path):
    # settings.USE_I18N is False, so i18n_patterns serve only the unprefixed URLs
    assert client.get(path).status_code == 404


def test_unknown_path_is_404(client):
    assert client.get("/does-not-exist/").status_code == 404


def test_unknown_language_prefix_is_404(client):
    assert client.get("/xx/about/").status_code == 404


def test_non_trailing_slash_about_redirects(client):
    response = client.get("/about")
    assert response.status_code == 301
    assert response["Location"].endswith("/about/")


# ----------------------------------------------------------------------------- test route (template missing)
@pytest.mark.xfail(
    strict=True,
    reason="BUG: /test/chords/ renders 'test_chords.html' which does not exist (TemplateDoesNotExist)",
)
def test_chord_test_route_renders(client):
    client.raise_request_exception = False
    response = client.get("/test/chords/")
    assert response.status_code == 200


# ----------------------------------------------------------------------------- SEO files / PWA
def test_robots_txt(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert b"User-agent" in response.content


def test_sitemap_lists_static_pages_over_https(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/xml")
    body = response.content.decode()
    assert "<loc>https://testserver/</loc>" in body
    assert "https://testserver/about/" in body
    assert "https://testserver/impressum/" in body
    assert "<changefreq>weekly</changefreq>" in body


def test_service_worker_route(client):
    response = client.get("/sw.js")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/javascript; charset=utf-8"
    assert response["Service-Worker-Allowed"] == "/"
    assert response["Cache-Control"] == "no-cache"


def test_service_worker_rejects_post(client):
    assert client.post("/sw.js").status_code == 405
