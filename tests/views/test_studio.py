"""
Tests for the Guitar Positions Studio (single-page UI) and its catalogue API.

All rows are created synthetically; no fixtures or real data are used.
"""
import json
import re

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from positionfinder.models import Notes, NotesCategory, Root
from positionfinder.models_chords import ChordNotes
from positionfinder.views_studio import CATALOG_CACHE_KEY, build_catalog, get_catalog


def _json_script(html, element_id):
    """Extract and decode the payload of a `json_script` tag from rendered HTML."""
    match = re.search(
        r'<script id="%s" type="application/json">(.*?)</script>' % re.escape(element_id),
        html,
        re.S,
    )
    assert match, f'json_script tag "{element_id}" not found'
    return json.loads(match.group(1))


class StudioTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.scale_cat = NotesCategory.objects.create(id=1, category_name='Scales')
        cls.arpeggio_cat = NotesCategory.objects.create(id=2, category_name='Arpeggios')
        cls.chord_cat = NotesCategory.objects.create(id=3, category_name='Chords')

        cls.root_c = Root.objects.create(name='C', pitch=0)
        cls.root_d = Root.objects.create(name='D', pitch=2)

        # D major scale stored in D's tonal space, intentionally out of order.
        cls.scale = Notes.objects.create(
            category=cls.scale_cat, note_name=' Major ', ordering=1, tonal_root=2,
            first_note=2, second_note=4, third_note=6, fourth_note=7,
            fifth_note=9, sixth_note=11, seventh_note=1,
        )
        # Incomplete record: only two distinct notes -> must be skipped.
        cls.incomplete = Notes.objects.create(
            category=cls.scale_cat, note_name='Broken', ordering=2, tonal_root=0,
            first_note=0, second_note=7, third_note=7,
        )
        # Minor 7 arpeggio in C's tonal space, unsorted with a duplicate.
        cls.arpeggio = Notes.objects.create(
            category=cls.arpeggio_cat, note_name='Minor 7', ordering=1, tonal_root=0,
            first_note=10, second_note=0, third_note=3, fourth_note=7, fifth_note=0,
        )

        # bulk_create bypasses ChordNotes.save() side effects (ChordPosition generation).
        ChordNotes.objects.bulk_create([
            ChordNotes(
                category=cls.chord_cat, type_name='V2', chord_name='Major 7',
                range='e - g', tonal_root=0, ordering=1, chord_ordering=1, range_ordering=1,
                first_note=0, first_note_string='gString',
                second_note=4, second_note_string='bString',
                third_note=7, third_note_string='eString',
                fourth_note=11, fourth_note_string='highAString',
            ),
            ChordNotes(
                category=cls.chord_cat, type_name='V2', chord_name='Major 7',
                range='b - d', tonal_root=0, ordering=1, chord_ordering=1, range_ordering=2,
                first_note=0, first_note_string='dString',
                second_note=4, second_note_string='gString',
                third_note=7, third_note_string='bString',
                fourth_note=11, fourth_note_string='eString',
            ),
            ChordNotes(
                category=cls.chord_cat, type_name='V2', chord_name='Minor7b5',
                range='e - g', tonal_root=0, ordering=2, chord_ordering=4, range_ordering=1,
                first_note=0, first_note_string='gString',
                second_note=3, second_note_string='bString',
                third_note=6, third_note_string='eString',
                fourth_note=10, fourth_note_string='highAString',
            ),
            ChordNotes(
                category=cls.chord_cat, type_name='V1', chord_name='Minor 7b5',
                range='e - d', tonal_root=0, ordering=2, chord_ordering=4, range_ordering=2,
                first_note=0, first_note_string='dString',
                second_note=3, second_note_string='gString',
                third_note=6, third_note_string='bString',
                fourth_note=10, fourth_note_string='eString',
            ),
            # Only two strings assigned -> fewer than 3 tones -> skipped.
            ChordNotes(
                category=cls.chord_cat, type_name='V2', chord_name='Diminished',
                range='e - g', tonal_root=0, ordering=3, chord_ordering=1, range_ordering=1,
                first_note=0, first_note_string='gString',
                second_note=3, second_note_string='bString',
                third_note=6, third_note_string=None,
            ),
        ])

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()


class CatalogShapeTests(StudioTestBase):
    def test_top_level_keys(self):
        catalog = build_catalog()
        self.assertEqual(catalog['version'], 1)
        self.assertEqual(set(catalog), {'version', 'scales', 'arpeggios', 'chords', 'roots'})

    def test_scale_intervals_sorted_relative_to_tonal_root(self):
        catalog = build_catalog()
        self.assertEqual(catalog['scales'], [
            {'id': self.scale.id, 'name': 'Major', 'intervals': [0, 2, 4, 5, 7, 9, 11]},
        ])

    def test_incomplete_records_are_skipped(self):
        catalog = build_catalog()
        ids = [s['id'] for s in catalog['scales'] + catalog['arpeggios']]
        self.assertNotIn(self.incomplete.id, ids)
        chord_names = [c['name'] for c in catalog['chords']]
        self.assertNotIn('Diminished', chord_names)

    def test_arpeggio_intervals_deduplicated_and_sorted(self):
        catalog = build_catalog()
        self.assertEqual(catalog['arpeggios'], [
            {'id': self.arpeggio.id, 'name': 'Minor 7', 'intervals': [0, 3, 7, 10]},
        ])

    def test_chords_grouped_by_name_with_voicings(self):
        catalog = build_catalog()
        chords = {c['name']: c for c in catalog['chords']}
        self.assertEqual(set(chords), {'Major 7', 'Minor 7b5'})

        major7 = chords['Major 7']
        self.assertEqual(major7['intervals'], [0, 4, 7, 11])
        self.assertEqual(len(major7['voicings']), 2)
        voicing = major7['voicings'][0]
        self.assertEqual(set(voicing), {'id', 'system', 'range', 'tones'})
        self.assertEqual(voicing['system'], 'V2')
        self.assertEqual(voicing['range'], 'e - g')
        self.assertEqual(voicing['tones'], [
            {'string': 'gString', 'interval': 0},
            {'string': 'bString', 'interval': 4},
            {'string': 'eString', 'interval': 7},
            {'string': 'highAString', 'interval': 11},
        ])

    def test_minor7b5_spellings_are_merged(self):
        catalog = build_catalog()
        chords = {c['name']: c for c in catalog['chords']}
        self.assertNotIn('Minor7b5', chords)
        half_dim = chords['Minor 7b5']
        self.assertEqual(half_dim['intervals'], [0, 3, 6, 10])
        self.assertEqual({v['system'] for v in half_dim['voicings']}, {'V1', 'V2'})

    def test_roots(self):
        catalog = build_catalog()
        self.assertEqual(catalog['roots'], [
            {'id': self.root_c.id, 'name': 'C', 'pitch': 0},
            {'id': self.root_d.id, 'name': 'D', 'pitch': 2},
        ])


class CatalogCacheTests(StudioTestBase):
    def test_get_catalog_populates_cache(self):
        self.assertIsNone(cache.get(CATALOG_CACHE_KEY))
        catalog = get_catalog()
        self.assertEqual(cache.get(CATALOG_CACHE_KEY), catalog)

    def test_cached_catalog_is_reused(self):
        get_catalog()
        with self.assertNumQueries(0):
            get_catalog()

    def test_content_change_refreshes_catalog(self):
        get_catalog()
        Notes.objects.create(
            category=self.scale_cat, note_name='New Scale', ordering=9, tonal_root=0,
            first_note=0, second_note=3, third_note=7,
        )
        self.assertIn('New Scale', [s['name'] for s in get_catalog()['scales']])


class StudioViewTests(StudioTestBase):
    def test_index_renders_with_json_script_tags(self):
        response = self.client.get(reverse('fretboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studio/index.html')
        html = response.content.decode()
        catalog = _json_script(html, 'catalog-data')
        self.assertEqual(catalog['version'], 1)
        self.assertEqual(len(catalog['scales']), 1)
        self.assertEqual(_json_script(html, 'legacy-state'), {})

    def test_legacy_arpeggio_params(self):
        response = self.client.get(reverse('fretboard'), {
            'models_select': '2',
            'root': str(self.root_d.pk),
            'notes_options_id': str(self.arpeggio.id),
            'position_select': '3',
        })
        self.assertEqual(response.status_code, 200)
        state = _json_script(response.content.decode(), 'legacy-state')
        self.assertEqual(state, {
            'mode': 'arpeggio', 'root': 2, 'typeId': self.arpeggio.id, 'position': 3,
        })

    def test_legacy_scale_params(self):
        response = self.client.get(reverse('fretboard'), {
            'models_select': '1', 'root': str(self.root_c.pk), 'notes_options_id': str(self.scale.id),
        })
        state = _json_script(response.content.decode(), 'legacy-state')
        self.assertEqual(state, {'mode': 'scale', 'root': 0, 'typeId': self.scale.id})

    def test_legacy_chord_params(self):
        response = self.client.get(reverse('fretboard'), {
            'models_select': '3',
            'root': str(self.root_d.pk),
            'chords_options_select': 'Major 7',
            'type_options_select': 'V2',
            'note_range': 'e - g',
            'notes_options_id': '99',  # ignored for chords
        })
        state = _json_script(response.content.decode(), 'legacy-state')
        self.assertEqual(state, {
            'mode': 'chord', 'root': 2, 'chordName': 'Major 7', 'system': 'V2', 'range': 'e - g',
        })

    def test_legacy_invalid_params_are_ignored(self):
        response = self.client.get(reverse('fretboard'), {
            'models_select': '9', 'root': '99999', 'notes_options_id': 'abc', 'position_select': 'x',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_json_script(response.content.decode(), 'legacy-state'), {})


class CatalogApiTests(StudioTestBase):
    def test_catalog_endpoint(self):
        response = self.client.get(reverse('studio_catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response['Cache-Control'], 'public, max-age=3600')
        data = response.json()
        self.assertEqual(data['version'], 1)
        self.assertEqual({c['name'] for c in data['chords']}, {'Major 7', 'Minor 7b5'})

    def test_catalog_endpoint_rejects_post(self):
        response = self.client.post(reverse('studio_catalog'))
        self.assertEqual(response.status_code, 405)


class ClassicViewTests(StudioTestBase):
    def test_classic_url_reverses(self):
        self.assertEqual(reverse('fretboard_classic'), '/classic/')

    def test_classic_view_does_not_error(self):
        # The classic view defaults to Root pk=1 / Notes pk=1, which synthetic rows
        # cannot guarantee, so pass explicit (classic-style) parameters.
        response = self.client.get(reverse('fretboard_classic'), {
            'models_select': '1',
            'root': str(self.root_c.pk),
            'notes_options_select': str(self.scale.id),
        })
        self.assertLess(response.status_code, 500)


class SeoDomainTests(TestCase):
    def test_robots_points_to_new_domain(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('Sitemap: https://fretboard.schoensgibl.com/sitemap.xml', body)
        self.assertNotIn('guitar-positions.org', body)

    @override_settings(ALLOWED_HOSTS=['fretboard.schoensgibl.com'])
    def test_sitemap_uses_request_host_over_https(self):
        response = self.client.get('/sitemap.xml', HTTP_HOST='fretboard.schoensgibl.com')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('<loc>https://fretboard.schoensgibl.com/</loc>', body)
        self.assertNotIn('guitar-positions.org', body)


class PwaTests(TestCase):
    def test_service_worker_served_from_root(self):
        response = self.client.get(reverse('service_worker'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('javascript', response['Content-Type'])
        self.assertEqual(response['Service-Worker-Allowed'], '/')
        self.assertEqual(response['Cache-Control'], 'no-cache')
        body = response.content.decode()
        self.assertIn('/static/studio/js/theory.js', body)

    def test_service_worker_rejects_post(self):
        self.assertEqual(self.client.post(reverse('service_worker')).status_code, 405)

    def test_manifest_is_valid_and_icons_exist(self):
        from pathlib import Path
        from django.conf import settings
        static_dir = Path(settings.BASE_DIR) / 'static' / 'studio'
        manifest = json.loads((static_dir / 'manifest.webmanifest').read_text())
        self.assertEqual(manifest['start_url'], '/?source=pwa')
        for icon in manifest['icons']:
            self.assertTrue((static_dir / icon['src']).exists(), icon['src'])

    def test_studio_page_links_manifest(self):
        response = self.client.get('/')
        self.assertContains(response, 'manifest.webmanifest')
        self.assertContains(response, reverse('service_worker'))


class CatalogInvalidationTests(StudioTestBase):
    def test_saving_content_clears_catalog_cache(self):
        get_catalog()
        self.assertIsNotNone(cache.get(CATALOG_CACHE_KEY))
        Root.objects.create(name='Fb', pitch=4)
        self.assertIsNone(cache.get(CATALOG_CACHE_KEY))
