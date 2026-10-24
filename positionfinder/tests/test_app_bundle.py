"""The native app bundle must stay ad-free, offline and free of payment links."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

REPO = Path(__file__).resolve().parents[2]


class AppBundleTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls._tmp.name) / 'www'
        subprocess.run(
            [sys.executable, str(REPO / 'scripts' / 'build_app_bundle.py'), '--out', str(cls.out)],
            check=True, cwd=REPO, capture_output=True,
        )
        cls.files = [p for p in cls.out.rglob('*') if p.is_file() and p.suffix in {'.html', '.js', '.css', '.json'}]

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()
        super().tearDownClass()

    def test_no_payment_or_donation_links(self):
        for path in self.files:
            text = path.read_text(encoding='utf-8')
            for needle in ('STRIPE_DONATE_URL', 'stripe.com', 'paypal', 'Support the project'):
                self.assertNotIn(needle, text, f'{needle} found in {path.name}')

    def test_no_service_worker_or_manifest(self):
        self.assertFalse((self.out / 'studio' / 'manifest.webmanifest').exists())
        for path in self.files:
            text = path.read_text(encoding='utf-8')
            self.assertNotIn('serviceWorker', text, path.name)
            self.assertNotIn('manifest.webmanifest', text, path.name)

    def test_only_expected_external_urls(self):
        allowed_prefixes = ('https://fretboard.schoensgibl.com', 'http://www.w3.org/2000/svg',
                            'https://github.com/hybridpicker/fretboard-position-finder',
                            'https://github.com/ionic-team/capacitor',
                            'https://developer.android.com/jetpack/androidx')
        for path in self.files:
            for url in re.findall(r'https?://[A-Za-z0-9./_#?=&%-]+', path.read_text(encoding='utf-8')):
                self.assertTrue(url.startswith(allowed_prefixes), f'unexpected URL {url} in {path.name}')

    def test_csp_allows_only_the_bundle(self):
        html = (self.out / 'index.html').read_text(encoding='utf-8')
        self.assertIn("default-src 'self'", html)
        self.assertIn("connect-src 'self'", html)
        self.assertNotRegex(html, r"(script|connect|img|font)-src[^;\"]*https?:")

    def test_native_additions_are_loaded(self):
        html = (self.out / 'index.html').read_text(encoding='utf-8')
        self.assertIn('native.js', html)
        self.assertTrue((self.out / 'native.js').is_file())
