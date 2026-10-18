"""
Progressive Web App support for Guitar Positions Studio.

`service_worker` serves the worker script from the site root (`/sw.js`) so its
scope can cover the studio at `/`. The script is rendered from the template
`studio/sw.js`; the list of shell assets to precache is defined once here and
also feeds a content fingerprint, so any change to a shell asset changes the
worker's bytes and makes browsers install a fresh cache automatically, even
when settings.VERSION (APP_VERSION) was not bumped.

The worker only handles public, anonymous, same-origin GET requests (the studio
page, its static assets and the public catalogue). It stores no personal data,
sends nothing anywhere and makes no third-party requests.
"""
import hashlib
import json
import os
from functools import lru_cache

from django.contrib.staticfiles import finders
from django.shortcuts import render
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_safe

from .context_processors import app_version_context

# Static files that make up the studio shell, precached on install.
# Entries flagged True are requested with `?v=<APP_VERSION>` by templates/studio/index.html,
# so they are precached under that exact URL. The ES modules imported by app.js resolve
# without a query string and are precached as plain paths.
SHELL_ASSETS = (
    ('studio/studio.css', True),
    ('studio/js/app.js', True),
    ('studio/js/theory.js', False),
    ('studio/js/fretboard.js', False),
    ('studio/js/diagram.js', False),
    ('studio/js/audio.js', False),
    ('fonts/dosis/Dosis-SemiBold.ttf', False),
    ('studio/manifest.webmanifest', False),
    ('studio/icons/icon-192.png', False),
    ('studio/icons/icon-512.png', False),
    ('studio/icons/icon-maskable-192.png', False),
    ('studio/icons/icon-maskable-512.png', False),
    ('studio/icons/apple-touch-icon.png', False),
)


@lru_cache(maxsize=64)
def _file_digest(path, mtime_ns, size):
    """Content hash of one file; memoised on its stat signature so unchanged files are not re-read."""
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(65536), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _shell_fingerprint():
    combined = hashlib.sha256()
    for asset, _versioned in SHELL_ASSETS:
        path = finders.find(asset)
        if path:
            stat = os.stat(path)
            combined.update(_file_digest(path, stat.st_mtime_ns, stat.st_size).encode())
        else:
            combined.update(f'missing:{asset}'.encode())
    return combined.hexdigest()[:12]


@require_safe
def service_worker(request):
    app_version = app_version_context(request)['APP_VERSION']
    precache = [
        f'{static(asset)}?v={app_version}' if versioned else static(asset)
        for asset, versioned in SHELL_ASSETS
    ]
    precache.insert(0, '/')  # the studio page itself, used as the offline fallback
    context = {
        # JSON with `<` escaped is safe to embed verbatim in a JS file.
        'precache_json': mark_safe(json.dumps(precache, indent=2).replace('<', '\\u003c')),
        'cache_version': f'{app_version}-{_shell_fingerprint()}',
    }
    response = render(request, 'studio/sw.js', context,
                      content_type='application/javascript; charset=utf-8')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response
