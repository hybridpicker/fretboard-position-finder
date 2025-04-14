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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns # Re-added i18n_patterns import
import positionfinder.views_scale
import positionfinder.views_arpeggio
import positionfinder.views_chords
import positionfinder.views
import positionfinder.views_search
from positionfinder.views import fretboard_unified_view, chord_search_test_view
from positionfinder.views_search import unified_search_view, search_json

# URLs that should not be prefixed with language code
urlpatterns_non_i18n = [
    # API endpoints
    path('api/', include('api.urls', namespace='api')),
    # Admin site
    path('admin/', admin.site.urls),
    # JSON search endpoint (likely doesn't need i18n)
    path('search/json/', search_json, name='search_json'),
    # Testing route
    path('test/chords/', chord_search_test_view, name='test_chords'),
]

# URLs that should be prefixed with language code
urlpatterns_i18n = i18n_patterns(
    # API endpoints
    # Main unified view that handles scales, arpeggios, and chords
    path('', fretboard_unified_view, name='fretboard'),
    
    # Search view page
    path('search/', unified_search_view, name='unified_search'),

    # Keep original views for API compatibility, but they will redirect to unified view
    # These might also need i18n if accessed directly via browser
    path('arpeggios', positionfinder.views_arpeggio.fretboard_arpeggio_view,
         name='show_arpeggio_fretboard'),
    path('chords', positionfinder.views_chords.fretboard_chords_view,
         name='show_chords_fretboard'),
    path('scales', positionfinder.views_scale.fretboard_scale_view,
         name='show_scale_fretboard'),

    path('about/', positionfinder.views.about_view, name='about'),
    path('impressum/', positionfinder.views.impressum_view, name='impressum'),
    prefix_default_language=False # Important: Avoids prefixing the default language (e.g., /en/)
)

# Combine the two lists
urlpatterns = urlpatterns_non_i18n + urlpatterns_i18n
    
# Note: The original lines 39-53 are now either moved into urlpatterns_i18n,
# urlpatterns_non_i18n, or implicitly handled by the structure above.
# Ensure all necessary imports remain at the top.