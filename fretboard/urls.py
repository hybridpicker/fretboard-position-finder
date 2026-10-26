"""fretboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns  # Re-added i18n_patterns import
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic.base import TemplateView

import positionfinder.views
import positionfinder.views_arpeggio
import positionfinder.views_chords
import positionfinder.views_scale
import positionfinder.views_search

# Import sitemap classes
from positionfinder.sitemaps import StaticViewSitemap
from positionfinder.views import fretboard_unified_view
from positionfinder.views_pwa import service_worker
from positionfinder.views_search import search_json, unified_search_view
from positionfinder.views_studio import catalog_json, studio_view

# Define sitemaps dictionary
sitemaps = {
    "static": StaticViewSitemap,
}

# URLs that should not be prefixed with language code
urlpatterns_non_i18n = [
    # API endpoints
    path("api/catalog/", catalog_json, name="studio_catalog"),
    # PWA service worker (served from the root so its scope covers the studio at /)
    path("sw.js", service_worker, name="service_worker"),
    path("api/", include("api.urls", namespace="api")),
    # JSON search endpoint (likely doesn't need i18n)
    path("search/json/", search_json, name="search_json"),
    path("search_json/", search_json, name="search_json_alt"),
    # Testing route
    # SEO-related URLs
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path(
        "sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"
    ),
]

# Only add the admin URL in DEBUG mode
if settings.DEBUG:
    urlpatterns_non_i18n.append(path("admin/", admin.site.urls))

# URLs that should be prefixed with language code
urlpatterns_i18n = i18n_patterns(
    # API endpoints
    # Studio: the redesigned single-page app (also understands legacy query parameters)
    path("", studio_view, name="fretboard"),
    # Previous UI that handles scales, arpeggios, and chords
    path("classic/", fretboard_unified_view, name="fretboard_classic"),
    # Search view page
    path("search/", unified_search_view, name="unified_search"),
    # Keep original views for API compatibility, but they will redirect to unified view
    # These might also need i18n if accessed directly via browser
    path(
        "arpeggios",
        positionfinder.views_arpeggio.fretboard_arpeggio_view,
        name="show_arpeggio_fretboard",
    ),
    path("chords", positionfinder.views_chords.fretboard_chords_view, name="show_chords_fretboard"),
    path("scales", positionfinder.views_scale.fretboard_scale_view, name="show_scale_fretboard"),
    path("about/", positionfinder.views.about_view, name="about"),
    path("impressum/", positionfinder.views.impressum_view, name="impressum"),
    prefix_default_language=False,  # Important: Avoids prefixing the default language (e.g., /en/)
)

# Combine the two lists
urlpatterns = urlpatterns_non_i18n + urlpatterns_i18n
