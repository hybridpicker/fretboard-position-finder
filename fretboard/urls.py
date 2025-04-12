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
from django.conf.urls.i18n import i18n_patterns
import positionfinder.views_scale
import positionfinder.views_arpeggio
import positionfinder.views_chords
import positionfinder.views
import positionfinder.search_views
from positionfinder.views import fretboard_unified_view, chord_search_test_view

# Non-translatable URLs
urlpatterns = [
    # API endpoints
    path('api/', include('api.urls', namespace='api')),
    path('i18n/', include('django.conf.urls.i18n')),  # Add this for language switcher
]

# Translatable URLs
urlpatterns += i18n_patterns(
    # Main unified view that handles scales, arpeggios, and chords
    path('', fretboard_unified_view, name='fretboard'),
    
    # Search views
    path('search/', positionfinder.search_views.search_view, name='search'),
    path('search/json/', positionfinder.search_views.search_json, name='search_json'),
    
    # Testing route
    path('test/chords/', chord_search_test_view, name='test_chords'),
    
    # Keep original views for API compatibility, but they will redirect to unified view
    path('arpeggios', positionfinder.views_arpeggio.fretboard_arpeggio_view,
         name='show_arpeggio_fretboard'),
    path('chords', positionfinder.views_chords.fretboard_chords_view,
         name='show_chords_fretboard'),
    path('scales', positionfinder.views_scale.fretboard_scale_view, 
         name='show_scale_fretboard'),
         
    path('about/', positionfinder.views.about_view, name='about'),
    path('impressum/', positionfinder.views.impressum_view, name='impressum'),
    path('admin/', admin.site.urls),
    
    prefix_default_language=True,
)