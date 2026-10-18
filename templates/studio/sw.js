{% load static %}/*
 * Guitar Positions Studio service worker.
 * Rendered by positionfinder.views_pwa.service_worker and served from /sw.js.
 *
 * Strategy
 *   - install:   precache the studio shell (page, CSS, ES modules, font, icons)
 *   - "/" nav:   network-first, falling back to the cached page when offline
 *   - catalogue: stale-while-revalidate
 *   - static:    cache-first (same-origin GETs under the static prefix)
 *   - activate:  delete caches from previous versions
 *
 * Privacy: only anonymous, same-origin GET responses for public content are
 * cached. Non-GET, cross-origin and range requests pass straight through.
 * Nothing is sent anywhere; there is no analytics or third-party traffic.
 */
'use strict';

// Changes whenever APP_VERSION or any precached shell file changes, which makes
// the browser install this worker again and rebuild the caches.
const VERSION = '{{ cache_version|escapejs }}';
const CACHE_PREFIX = 'gp-studio-';
const SHELL_CACHE = `${CACHE_PREFIX}shell-${VERSION}`;
const RUNTIME_CACHE = `${CACHE_PREFIX}runtime-${VERSION}`;
const OFFLINE_PAGE = '/';
const STATIC_PREFIX = '{% get_static_prefix %}';
const CATALOG_PATH = '{% url "studio_catalog" %}';
const PRECACHE_URLS = {{ precache_json }};

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      // `cache: 'reload'` bypasses the HTTP cache so the precache gets fresh copies.
      .then((cache) => cache.addAll(PRECACHE_URLS.map((url) => new Request(url, { cache: 'reload' }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys
        .filter((key) => key.startsWith(CACHE_PREFIX) && key !== SHELL_CACHE && key !== RUNTIME_CACHE)
        .map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET' || request.headers.has('range')) return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    // Only the studio page is handled; other pages (classic UI, about, ...) use the network as usual.
    if (url.pathname === OFFLINE_PAGE) event.respondWith(networkFirstPage(event, url));
    return;
  }
  if (url.pathname === CATALOG_PATH) {
    event.respondWith(staleWhileRevalidate(event));
    return;
  }
  if (url.pathname.startsWith(STATIC_PREFIX)) {
    event.respondWith(cacheFirst(event));
  }
});

// Cache only complete, same-origin, successful responses that allow storage.
function isCacheable(response) {
  return response && response.status === 200 && response.type === 'basic'
    && !/no-store/i.test(response.headers.get('Cache-Control') || '');
}

// Look up a request in this version's caches only.
async function matchOwn(request) {
  return (await caches.match(request, { cacheName: SHELL_CACHE }))
    || caches.match(request, { cacheName: RUNTIME_CACHE });
}

async function networkFirstPage(event, url) {
  try {
    const response = await fetch(event.request);
    // Refresh the offline copy only from the plain page: legacy query parameters
    // (`?models_select=...`) embed a per-link initial state that must not become the default.
    const plain = [...url.searchParams.keys()].every((key) => key === 'source');
    if (plain && isCacheable(response) && !response.redirected) {
      const copy = response.clone();
      event.waitUntil(caches.open(SHELL_CACHE).then((cache) => cache.put(OFFLINE_PAGE, copy)));
    }
    return response;
  } catch (error) {
    return (await caches.match(OFFLINE_PAGE, { cacheName: SHELL_CACHE })) || Response.error();
  }
}

async function staleWhileRevalidate(event) {
  const cache = await caches.open(RUNTIME_CACHE);
  const cached = await cache.match(event.request);
  const refresh = fetch(event.request).then((response) => {
    if (isCacheable(response)) event.waitUntil(cache.put(event.request, response.clone()));
    return response;
  });
  if (cached) {
    event.waitUntil(refresh.catch(() => undefined));
    return cached;
  }
  return refresh;
}

async function cacheFirst(event) {
  const cached = await matchOwn(event.request);
  if (cached) return cached;
  const response = await fetch(event.request);
  if (isCacheable(response)) {
    const copy = response.clone();
    event.waitUntil(caches.open(RUNTIME_CACHE).then((cache) => cache.put(event.request, copy)));
  }
  return response;
}
