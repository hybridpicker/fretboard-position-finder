from django.urls import path
from . import views
from . import views_search

app_name = 'api'

urlpatterns = [
    path('chord-voicings/', views.ChordVoicingView.as_view(), name='chord_voicings'),
    path('tuning-options/', views.TuningOptionsView.as_view(), name='tuning_options'),
    path('voicing-groups/', views.VoicingGroupsView.as_view(), name='voicing_groups'),
    path('chord-types/', views.ChordTypesView.as_view(), name='chord_types'),

    # New endpoints for dynamic menu options
    path('chord-names/', views.ChordNamesView.as_view(), name='ajax_chord_names'),
    path('chord-ranges/', views.ChordRangesView.as_view(), name='ajax_chord_ranges'),
    path('chord-positions/', views.ChordPositionsView.as_view(), name='ajax_chord_positions'),
    path('scale-positions/', views.ScalePositionsView.as_view(), name='ajax_scale_positions'),
    path('arpeggio-positions/', views.ArpeggioPositionsView.as_view(), name='ajax_arpeggio_positions'),
    path('fallback-positions/', views.FallbackPositionsView.as_view(), name='fallback_positions'),
    path('emergency-positions/', views.emergency_positions, name='emergency_positions'),
    path('emergency-chord-names/', views.emergency_positions, name='emergency_chord_names'),

    # Search API endpoints
    path('search/autocomplete/', views_search.search_autocomplete, name='search_autocomplete'),
    path('search/direct-match/', views_search.direct_match, name='search_direct_match'),

    # No tester endpoint
]
