"""SEO helpers: context processor, template tags, structured-data helpers and the sitemap."""

import json

import pytest
from django.contrib.sites.requests import RequestSite
from django.template import Context, Template
from django.test import RequestFactory

from positionfinder.seo_context_processor import get_seo_metadata
from positionfinder.sitemaps import StaticViewSitemap
from positionfinder.templatetags import seo_tags
from positionfinder.views_helpers import generate_breadcrumbs, generate_seo_data

RF = RequestFactory()

DEFAULT_TITLE = "Guitar Positions | Complete Fretboard Visualization Tool"
ALL_KEYS = {
    "page_title",
    "meta_description",
    "meta_keywords",
    "og_title",
    "og_description",
    "twitter_title",
    "twitter_description",
}


def meta(path):
    return get_seo_metadata(RF.get(path))


# ----------------------------------------------------------------------------- get_seo_metadata
@pytest.mark.parametrize("path", ["/", "/scale/c/major/", "/unknown/page/", "/about/", "/mode/"])
def test_metadata_always_has_all_keys(path):
    assert set(meta(path)) == ALL_KEYS


def test_default_metadata_for_unknown_path():
    data = meta("/something/else/")
    assert data["page_title"] == DEFAULT_TITLE
    assert data["og_title"] == "Guitar Positions | Ultimate Fretboard Tool"
    assert data["twitter_title"] == "Guitar Positions | Fretboard Tool"


def test_home_page_metadata():
    data = meta("/")
    assert data["page_title"] == "Guitar Positions | Ultimate Fretboard Visualization Tool"
    assert "ad-free" in data["meta_description"]
    # other keys keep the defaults
    assert data["og_title"] == "Guitar Positions | Ultimate Fretboard Tool"


def test_scale_page_with_root_and_type():
    data = meta("/scale/a/harmonic-minor/")
    assert data["page_title"] == "A Harmonic Minor Scale | Complete Guitar Positions"
    assert data["twitter_title"] == "A Harmonic Minor Scale"
    assert "A Harmonic Minor scale, A Harmonic Minor guitar" in data["meta_keywords"]


def test_arpeggio_page_with_root_and_type():
    data = meta("/arpeggio/e/minor-7/")
    assert data["page_title"] == "E Minor 7 Arpeggio | Guitar Positions"
    assert (
        data["og_description"]
        == "Complete E Minor 7 arpeggio positions for guitar. Interactive fretboard visualization."
    )


@pytest.mark.parametrize(
    "slug,description",
    [
        ("major", "Major"),
        ("minor", "Minor"),
        ("7", "Dominant 7th"),
        ("dominant-7", "Dominant 7th"),
        ("dom7", "Dominant 7th"),
        ("maj7", "Major 7th"),
        ("major-7", "Major 7th"),
        ("min7", "Minor 7th"),
        ("m7", "Minor 7th"),
        ("minor-7", "Minor 7th"),
        ("sus4", "sus4"),
    ],
)
def test_chord_page_descriptions(slug, description):
    data = meta(f"/chord/c/{slug}/")
    assert data["page_title"] == f"C {description} Chord | Guitar Positions & Voicings"
    assert data["twitter_description"] == f"All C {description} chord voicings and positions."


def test_mode_page_with_root_and_name():
    data = meta("/mode/d/dorian/")
    assert data["page_title"] == "D Dorian Mode | Guitar Positions"
    assert data["meta_keywords"].startswith("D Dorian mode, Dorian mode guitar")


def test_about_page_metadata():
    data = meta("/about/")
    assert data["page_title"] == "About Guitar Positions | The Complete Fretboard Tool"


GENERIC = [
    ("scale", "Guitar Scales | Complete Scale Library"),
    ("arpeggio", "Guitar Arpeggios | Complete Arpeggio Library"),
    ("chord", "Guitar Chords | Complete Chord Library & Voicings"),
    ("mode", "Guitar Modes | Complete Modal Playing Guide"),
]


@pytest.mark.parametrize("segment,title", GENERIC)
def test_generic_page_with_only_a_root_segment(segment, title):
    assert meta(f"/{segment}/c/")["page_title"] == title


@pytest.mark.parametrize("segment,title", GENERIC)
@pytest.mark.xfail(
    strict=True,
    reason="BUG: the generic scale/arpeggio/chord/mode branches are only reachable "
    "with an extra path segment: '/scale/' is stripped to 'scale', which "
    "does not start with 'scale/'",
)
def test_generic_page_without_further_segments(segment, title):
    assert meta(f"/{segment}/")["page_title"] == title


def test_single_segment_scale_path_is_not_a_scale_page():
    # 'scale' without trailing segments does not start with 'scale/' after stripping slashes
    assert meta("/scale")["page_title"] == DEFAULT_TITLE


# ----------------------------------------------------------------------------- seo_tags
def test_chord_structured_data_with_positions_and_print_action():
    data = json.loads(seo_tags.chord_structured_data("C", "Major", [1, 2, 3]))
    assert data["@type"] == "MusicComposition"
    assert data["name"] == "C Major Chord"
    assert data["musicalKey"] == "C"
    assert data["numberOfPositions"] == 3
    assert data["potentialAction"]["name"] == "Print Chord Chart"
    assert data["potentialAction"]["target"]["urlTemplate"] == "?print=true"


def test_chord_structured_data_without_positions_or_print():
    data = json.loads(seo_tags.chord_structured_data("D", "Minor", [], is_printable=False))
    assert "numberOfPositions" not in data
    assert "potentialAction" not in data


def test_chord_structured_data_with_none_positions():
    data = json.loads(seo_tags.chord_structured_data("D", "Minor", None))
    assert "numberOfPositions" not in data


def test_scale_structured_data_full():
    data = json.loads(
        seo_tags.scale_structured_data("A", "Minor Pentatonic", "1,b3,4,5,b7", ["p1", "p2"])
    )
    assert data["name"] == "A Minor Pentatonic Scale"
    assert data["learningResourceType"] == "Guitar Scale"
    assert data["additionalProperty"] == {
        "@type": "PropertyValue",
        "name": "Scale Formula",
        "value": "1,b3,4,5,b7",
    }
    assert data["numberOfPatterns"] == 2
    assert data["keywords"] == (
        "A Minor Pentatonic scale, guitar scale, Minor Pentatonic positions, A guitar scale"
    )


def test_scale_structured_data_minimal():
    data = json.loads(seo_tags.scale_structured_data("A", "Major"))
    assert "additionalProperty" not in data
    assert "numberOfPatterns" not in data


def test_fretboard_breadcrumbs_tag():
    data = json.loads(seo_tags.fretboard_breadcrumbs([("/", "Home"), ("/chords/", "Chords")]))
    assert data["@type"] == "BreadcrumbList"
    assert data["itemListElement"] == [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
        {"@type": "ListItem", "position": 2, "name": "Chords", "item": "/chords/"},
    ]


def test_fretboard_breadcrumbs_empty():
    assert json.loads(seo_tags.fretboard_breadcrumbs([]))["itemListElement"] == []


def test_seo_tags_usable_from_template():
    template = Template(
        "{% load seo_tags %}{% chord_structured_data root kind positions False as sd %}{{ sd }}"
    )
    rendered = template.render(Context({"root": "G", "kind": "Major", "positions": [1]}))
    assert "G Major Chord" in rendered.replace("&quot;", '"')


# ----------------------------------------------------------------------------- views_helpers SEO helpers
def test_generate_seo_data_chord():
    result = generate_seo_data(
        "chord",
        root="C",
        chord_type="Major",
        chord_notes=["C", "E", "G"],
        positions=[{"position": "Basic"}],
    )
    assert result["chord_root"] == "C"
    assert result["chord_type"] == "Major"
    assert result["chord_notes_description"] == "C, E, G"
    assert result["chord_position_fret"] == "Basic"
    structured = json.loads(result["chord_structured_data"])
    assert structured["name"] == "C Major Chord"
    assert structured["description"] == "C Major chord positions for guitar"


def test_generate_seo_data_chord_defaults():
    result = generate_seo_data("chord")
    assert result["chord_notes_description"] == ""
    assert result["chord_position_fret"] is None
    assert result["chord_root"] == ""


def test_generate_seo_data_scale():
    result = generate_seo_data("scale", root="A", scale_type="Minor", scale_formula="1 2 b3")
    assert (
        result["scale_root"] == "A"
        and result["scale_type"] == "Minor"
        and result["scale_formula"] == "1 2 b3"
    )
    structured = json.loads(result["scale_structured_data"])
    assert structured["name"] == "A Minor Scale"
    assert structured["learningResourceType"] == "Guitar Scale"


def test_generate_seo_data_arpeggio():
    result = generate_seo_data("arpeggio", root="E", arpeggio_type="Dim", notes=["E", "G", "Bb"])
    assert result["arpeggio_notes"] == "E, G, Bb"
    assert json.loads(result["arpeggio_structured_data"])["name"] == "E Dim Arpeggio"
    assert generate_seo_data("arpeggio")["arpeggio_notes"] == ""


@pytest.mark.parametrize("kind", ["mode", "unknown", ""])
def test_generate_seo_data_unsupported_types_return_empty_dict(kind):
    assert generate_seo_data(kind, root="C") == {}


def test_generate_breadcrumbs():
    data = json.loads(generate_breadcrumbs([("/", "Home"), ("/scales/", "Scales")]))
    assert [i["position"] for i in data["itemListElement"]] == [1, 2]
    assert data["itemListElement"][1] == {
        "@type": "ListItem",
        "position": 2,
        "name": "Scales",
        "item": "/scales/",
    }


def test_generate_breadcrumbs_empty():
    assert json.loads(generate_breadcrumbs([]))["itemListElement"] == []


# ----------------------------------------------------------------------------- sitemap
@pytest.mark.django_db
def test_static_sitemap_items_and_locations():
    sitemap = StaticViewSitemap()
    assert list(sitemap.items()) == ["fretboard", "about", "impressum"]
    assert [sitemap.location(i) for i in sitemap.items()] == ["/", "/about/", "/impressum/"]
    assert (sitemap.priority, sitemap.changefreq, sitemap.protocol) == (0.8, "weekly", "https")


@pytest.mark.django_db
def test_static_sitemap_urls_use_request_host_with_https():
    request = RF.get("/sitemap.xml")
    urls = StaticViewSitemap().get_urls(site=RequestSite(request))
    assert [u["location"] for u in urls] == [
        "https://testserver/",
        "https://testserver/about/",
        "https://testserver/impressum/",
    ]
