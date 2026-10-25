"""Unit tests for views_base.MusicalTheoryView and its ScaleView / ArpeggioView subclasses."""
import json

import pytest
from django.test import RequestFactory
from django.urls import NoReverseMatch

from positionfinder.models import Notes, NotesCategory
from positionfinder.models_chords import ChordNotes
from positionfinder.positions import NotesPosition
from positionfinder.template_notes import ALL_NOTES_POSITION
from positionfinder.views_arpeggio import ArpeggioView, arpeggio_list, fretboard_arpeggio_view
from positionfinder.views_base import MusicalTheoryView
from positionfinder.views_scale import ScaleView, fretboard_scale_view
from positionfinder import views as plain_views

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("music_data")]
RF = RequestFactory()


def get_request(query=None, path="/scales"):
    request = RF.get(path, query or {})
    request.session = {}
    return request


# ----------------------------------------------------------------------------- MusicalTheoryView.process_request
def test_process_request_defaults():
    view = MusicalTheoryView(category_id=1)
    assert view.process_request(get_request()) == {
        "root_id": 1, "category_id": 1, "position_id": "0", "notes_options_id": None,
    }


def test_process_request_reads_all_parameters_as_strings():
    view = MusicalTheoryView(category_id=1)
    params = view.process_request(get_request(
        {"root": "5", "models_select": "2", "position_select": "7", "notes_options_select": "9"}))
    assert params == {"root_id": "5", "category_id": "2", "position_id": "7", "notes_options_id": "9"}


def test_non_get_requests_use_defaults():
    request = RF.post("/scales", {"root": "5"})
    params = MusicalTheoryView(category_id=3).process_request(request)
    assert params["root_id"] == 1 and params["category_id"] == 3


def test_base_apply_defaults_is_identity():
    params = {"a": 1}
    assert MusicalTheoryView(1).apply_defaults(params) is params


def test_base_add_view_specific_context_is_identity():
    ctx = {"a": 1}
    assert MusicalTheoryView(1).add_view_specific_context(ctx, {}) is ctx


def test_default_template_name():
    assert MusicalTheoryView(1).template_name == "fretboard.html"
    assert MusicalTheoryView(1, "x.html").template_name == "x.html"


# ----------------------------------------------------------------------------- get_position_data
def test_position_data_all_notes():
    assert MusicalTheoryView(1).get_position_data("1", 0, "0") == ALL_NOTES_POSITION


def test_position_data_existing_position_shifted_by_root():
    position = NotesPosition.objects.filter(notes_name_id=1).first()
    base = [int(x) for x in position.position.split(",")]
    result = MusicalTheoryView(1).get_position_data("1", 2, str(position.pk))
    assert result == [x + 2 for x in base] or result == [x + 2 - 12 for x in base]


def test_position_data_missing_position_falls_back_to_all_notes():
    assert MusicalTheoryView(1).get_position_data("1", 0, "424242") == ALL_NOTES_POSITION


# ----------------------------------------------------------------------------- build_position_json
def test_build_position_json_scale_adds_name_and_root():
    payload = json.loads(ScaleView().build_position_json("Major", 14, 9, 0, "A", "1"))
    assert payload["name"] == "Major"
    assert payload["root"][0].startswith("a")
    assert "1" in payload  # position 1 present


def test_build_position_json_arpeggio_skips_position_transposition():
    arp = Notes.objects.filter(category__category_name="Arpeggios").first()
    payload = json.loads(ArpeggioView().build_position_json(arp.note_name, 1, 0, 0, "C", str(arp.pk)))
    assert payload["name"] == arp.note_name


def test_build_position_json_unknown_notes_option_is_tolerated():
    # Notes id lookup fails after the position dict was built: positions stay untransposed
    payload = json.loads(ScaleView().build_position_json("Major", 1, 0, 0, "C", "424242"))
    assert payload["name"] == "Major"


# ----------------------------------------------------------------------------- ScaleView
def test_scale_apply_defaults_sets_first_scale():
    assert ScaleView().apply_defaults({"notes_options_id": None})["notes_options_id"] == "1"
    assert ScaleView().apply_defaults({"notes_options_id": "4"})["notes_options_id"] == "4"


def test_scale_view_category_is_one():
    assert ScaleView().category_id == 1


def test_scale_specific_context_flags_v_systems():
    view = ScaleView()
    ctx = view.add_view_specific_context({"notes_options": Notes.objects.filter(category_id=1)},
                                         {"notes_options_id": "1"})
    assert ctx["chord_name"] == "Major 7"
    assert ctx["v1_data_exists"] is True and ctx["v2_data_exists"] is True


def test_scale_specific_context_without_v2_data_and_bad_scale():
    ChordNotes.objects.filter(type_name="V2").delete()
    ctx = ScaleView().add_view_specific_context({"notes_options": Notes.objects.filter(category_id=1)},
                                                {"notes_options_id": "424242"})
    assert ctx["chord_name"] == ""
    assert ctx["v2_data_exists"] is False
    assert ctx["v1_data_exists"] is True


def test_scale_specific_context_with_missing_options_key():
    ctx = ScaleView().add_view_specific_context({}, {"notes_options_id": "1"})
    assert ctx["chord_name"] == ""


def test_fretboard_scale_view_renders():
    response = fretboard_scale_view(get_request({"root": "4", "notes_options_select": "1"}))
    assert response.status_code == 200
    assert b"fretboard" in response.content.lower()


# ----------------------------------------------------------------------------- ArpeggioView
def test_arpeggio_view_category_is_two():
    assert ArpeggioView().category_id == 2


def test_arpeggio_defaults_to_first_arpeggio():
    first = Notes.objects.filter(category__category_name="Arpeggios").first()
    assert ArpeggioView().apply_defaults({"notes_options_id": None})["notes_options_id"] == str(first.id)


def test_arpeggio_keeps_explicit_selection():
    assert ArpeggioView().apply_defaults({"notes_options_id": "5"})["notes_options_id"] == "5"


def test_arpeggio_default_without_category_is_13():
    NotesCategory.objects.filter(category_name__icontains="arpeggio").update(category_name="Other")
    assert ArpeggioView().apply_defaults({"notes_options_id": None})["notes_options_id"] == "13"


def test_arpeggio_default_without_arpeggio_notes_is_13():
    Notes.objects.filter(category__category_name__icontains="arpeggio").delete()
    assert ArpeggioView().apply_defaults({"notes_options_id": None})["notes_options_id"] == "13"


def test_fretboard_arpeggio_view_renders_arpeggio_context():
    response = fretboard_arpeggio_view(get_request(path="/arpeggios"))
    assert response.status_code == 200


def test_get_context_for_arpeggio_without_category_has_no_options():
    NotesCategory.objects.filter(category_name__icontains="arpeggio").update(category_name="Other")
    arp_id = Notes.objects.filter(category_id=2).first().pk
    view = ArpeggioView()
    params = {"root_id": 1, "category_id": 2, "position_id": "0", "notes_options_id": str(arp_id)}
    ctx = view.get_context(get_request(), params)
    assert list(ctx["notes_options"]) == []
    assert ctx["position_options"] == []
    assert ctx["selected_notes"] == arp_id


def test_get_context_formats_selected_position_name():
    position = NotesPosition.objects.filter(notes_name_id=1).first()
    params = {"root_id": 1, "category_id": 1, "position_id": str(position.pk), "notes_options_id": "1"}
    ctx = ScaleView().get_context(get_request(), params)
    assert ctx["selected_position"] == str(position.pk)
    assert ctx["position"] != ALL_NOTES_POSITION


def test_get_context_resets_position_not_belonging_to_scale():
    other = NotesPosition.objects.exclude(notes_name_id=1).first()
    params = {"root_id": 1, "category_id": 1, "position_id": str(other.pk), "notes_options_id": "1"}
    ctx = ScaleView().get_context(get_request(), params)
    assert ctx["selected_position"] == "0"


def test_get_context_includes_common_context():
    ctx = ScaleView().get_context(get_request(), ScaleView().process_request(get_request()) | {"notes_options_id": "1"})
    assert "use_optimized_chord_view" in ctx


# ----------------------------------------------------------------------------- unrouted legacy views
@pytest.mark.xfail(strict=True, reason="BUG: arpeggio_list renders 'arpeggio_list.html' which does not exist "
                                       "(view is also not routed in fretboard/urls.py)")
def test_arpeggio_list_renders_arpeggios():
    response = arpeggio_list(get_request())
    assert response.status_code == 200


@pytest.mark.xfail(strict=True, reason="BUG: arpeggio_list renders 'arpeggio_list.html' which does not exist")
def test_arpeggio_list_without_category():
    NotesCategory.objects.filter(category_name__icontains="arpeggio").update(category_name="Other")
    assert arpeggio_list(get_request()).status_code == 200


@pytest.mark.xfail(strict=True, reason="BUG: landing_page_view reverses the non-existent URL name 'search' "
                                       "(the route is called 'unified_search'); view is also not routed")
def test_landing_page_view_renders():
    response = plain_views.landing_page_view(get_request(path="/"))
    assert response.status_code == 200


def test_landing_page_view_fails_with_no_reverse_match():
    with pytest.raises(NoReverseMatch):
        plain_views.landing_page_view(get_request(path="/"))


def test_about_and_impressum_views_direct():
    for view, template in ((plain_views.about_view, b"<html"), (plain_views.impressum_view, b"<html")):
        response = view(get_request(path="/about/"))
        assert response.status_code == 200
        assert template in response.content.lower()


def test_unified_view_dispatches_by_category():
    assert plain_views.fretboard_unified_view(get_request({"models_select": "2"})).status_code == 200
    assert plain_views.fretboard_unified_view(get_request({"models_select": "3"})).status_code == 200
    assert plain_views.fretboard_unified_view(get_request({"models_select": "1"})).status_code == 200
