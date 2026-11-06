"""Share metadata and favicons served by the Studio and the info pages."""

from pathlib import Path

import pytest
from django.conf import settings

OG_IMAGE_URL = "http://testserver/static/thumbnail/og-image.png"
STATIC_DIR = Path(settings.BASE_DIR) / "static"

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("path", ["/", "/about/", "/impressum/"])
def test_pages_share_an_absolute_current_image(client, path):
    html = client.get(path).content.decode()
    assert f'<meta property="og:image" content="{OG_IMAGE_URL}">' in html
    assert f'<meta name="twitter:image" content="{OG_IMAGE_URL}">' in html
    assert 'property="og:site_name" content="Guitar Positions"' in html
    assert "thumb_25" not in html


@pytest.mark.parametrize("path", ["/", "/about/", "/impressum/"])
def test_pages_link_versioned_current_favicons(client, path):
    html = client.get(path).content.decode()
    version = settings.VERSION
    assert f'href="/static/studio/icons/icon-small.svg?v={version}"' in html
    assert f'href="/static/studio/icons/favicon-32.png?v={version}"' in html
    assert f'href="/static/studio/icons/apple-touch-icon.png?v={version}"' in html
    assert "favicon/v2/" not in html


@pytest.mark.parametrize(
    ("path", "title"),
    [
        ("/", "Guitar Positions | Fretboard Studio"),
        ("/about/", "About | Guitar Positions"),
        ("/impressum/", "Impressum &amp; Privacy | Guitar Positions"),
    ],
)
def test_page_titles(client, path, title):
    html = client.get(path).content.decode()
    assert f"<title>{title}</title>" in html
    assert "Ultimate" not in html
    assert "Position Generator" not in html


def test_share_image_exists():
    assert (STATIC_DIR / "thumbnail" / "og-image.png").is_file()


def test_root_favicon_redirects_to_existing_icon(client):
    response = client.get("/favicon.ico")
    assert response.status_code == 302
    assert response["Location"] == f"/static/favicon/v2/favicon.ico?v={settings.VERSION}"
    assert (STATIC_DIR / "favicon" / "v2" / "favicon.ico").is_file()


def test_service_worker_precaches_favicons_under_their_linked_urls(client):
    body = client.get("/sw.js").content.decode()
    version = settings.VERSION
    assert f"/static/studio/icons/icon-small.svg?v={version}" in body
    assert f"/static/studio/icons/favicon-32.png?v={version}" in body
