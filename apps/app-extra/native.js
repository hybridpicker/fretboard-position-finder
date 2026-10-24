// App-only additions for the native shells (copied into the bundle by scripts/build_app_bundle.py).
// The web Studio does not load this file. No network access: everything stays on the device.
(function () {
  'use strict';
  var cap = window.Capacitor;
  var plugins = (cap && cap.Plugins) || {};
  var $ = function (sel) { return document.querySelector(sel); };

  var SITE = 'https://fretboard.schoensgibl.com';
  var REPO = 'https://github.com/hybridpicker/fretboard-position-finder';
  var MAX_FAVORITES = 100;

  var store = {
    get: function (key, fallback) { try { var v = localStorage.getItem('gp-' + key); return v === null ? fallback : JSON.parse(v); } catch (e) { return fallback; } },
    set: function (key, value) { try { localStorage.setItem('gp-' + key, JSON.stringify(value)); } catch (e) { /* storage unavailable */ } },
  };

  function toast(msg) {
    var el = $('#toast');
    if (!el) return;
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toast.t);
    toast.t = setTimeout(function () { el.classList.remove('show'); }, 1800);
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') node.textContent = attrs[k]; else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { node.appendChild(c); });
    return node;
  }

  // --- Haptics: a short tick when a note, fret or shape is tapped ------------------------------
  var hapticsOn = store.get('haptics', true);
  function tick() {
    if (!hapticsOn || !plugins.Haptics) return;
    try { plugins.Haptics.impact({ style: 'LIGHT' }); } catch (e) { /* no haptics on this device */ }
  }
  document.addEventListener('click', function (e) {
    if (e.target.closest('.fb-note, .fb-cell, #cards [data-shape], #chips [data-midi]')) tick();
  }, true);

  // --- Status bar follows the theme ------------------------------------------------------------
  function syncStatusBar() {
    if (!plugins.StatusBar) return;
    var theme = document.documentElement.dataset.theme;
    var dark = theme ? theme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    try { plugins.StatusBar.setStyle({ style: dark ? 'DARK' : 'LIGHT' }); } catch (e) { /* ignore */ }
  }

  // --- Dialog shell (reuses the Studio help dialog styles) -------------------------------------
  function dialog(id, title) {
    var close = el('button', { class: 'icon-btn', 'aria-label': 'Close' });
    close.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.4 5 12 10.6 17.6 5 19 6.4 13.4 12l5.6 5.6-1.4 1.4-5.6-5.6L6.4 19 5 17.6l5.6-5.6L5 6.4z"/></svg>';
    var body = el('div', { class: 'app-dialog-body' });
    var panel = el('div', { class: 'help-panel app-dialog' }, [
      el('div', { class: 'help-head' }, [el('h2', { id: id + 'Title', text: title }), close]),
      body,
    ]);
    var root = el('div', { class: 'help', id: id, role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': id + 'Title', hidden: '' }, [panel]);
    var hide = function () { root.hidden = true; };
    close.addEventListener('click', hide);
    root.addEventListener('click', function (e) { if (e.target === root) hide(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !root.hidden) hide(); });
    document.body.appendChild(root);
    return { root: root, body: body, show: function () { root.hidden = false; }, hide: hide };
  }

  function link(href, text) {
    return el('a', { href: href, target: '_blank', rel: 'noopener', text: text });
  }

  // --- Favourites: the current view is its URL query, stored on the device ---------------------
  var favorites = store.get('favorites', []);
  if (!Array.isArray(favorites)) favorites = [];
  var favBtn, favDialog;

  function currentQuery() { return location.search || ''; }
  function isFavorite() { return favorites.some(function (f) { return f.q === currentQuery(); }); }

  function syncFavBtn() {
    if (!favBtn) return;
    var on = isFavorite();
    favBtn.setAttribute('aria-pressed', String(on));
    favBtn.classList.toggle('is-on', on);
    favBtn.title = on ? 'Remove from favourites' : 'Add this view to favourites';
  }

  function saveFavorites() { store.set('favorites', favorites); syncFavBtn(); }

  function toggleFavorite() {
    var q = currentQuery();
    if (/(^|[?&])mode=song(&|$)/.test(q)) { toast('Songs are saved in the Songs view already'); return; }
    var at = favorites.findIndex(function (f) { return f.q === q; });
    if (at >= 0) {
      favorites.splice(at, 1);
      toast('Removed from favourites');
    } else {
      if (favorites.length >= MAX_FAVORITES) { toast('Favourites are full (' + MAX_FAVORITES + ')'); return; }
      var title = ($('#title') && $('#title').textContent.trim()) || document.title;
      var kind = ($('#eyebrow') && $('#eyebrow').textContent.trim()) || '';
      favorites.unshift({ q: q, title: title, kind: kind });
      toast('Added to favourites');
    }
    saveFavorites();
  }

  function openFavorites() {
    if (!favDialog) favDialog = dialog('favDialog', 'Favourites');
    var body = favDialog.body;
    body.textContent = '';
    if (!favorites.length) {
      body.appendChild(el('p', { class: 'muted', text: 'Nothing here yet. Tap the star in the top bar to keep the current scale, arpeggio or chord shape.' }));
    } else {
      var list = el('ul', { class: 'app-fav-list' });
      favorites.forEach(function (f, i) {
        var open = el('button', { class: 'app-fav-open' }, [el('b', { text: f.title }), el('span', { class: 'muted', text: f.kind })]);
        open.addEventListener('click', function () { location.search = f.q; });
        var del = el('button', { class: 'ghost-btn', 'aria-label': 'Remove ' + f.title, text: 'Remove' });
        del.addEventListener('click', function () { favorites.splice(i, 1); saveFavorites(); openFavorites(); });
        list.appendChild(el('li', {}, [open, del]));
      });
      body.appendChild(list);
    }
    favDialog.show();
  }

  function addTopButtons() {
    var bar = $('.top-actions');
    if (!bar) return;
    favBtn = el('button', { class: 'icon-btn', id: 'favBtn', 'aria-pressed': 'false', 'aria-label': 'Favourite this view' });
    favBtn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3.5 2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 16.9 6.8 19.7l1-5.9L3.5 9.7l5.9-.8z"/></svg>';
    favBtn.addEventListener('click', toggleFavorite);
    var list = el('button', { class: 'icon-btn', id: 'favListBtn', title: 'Favourites', 'aria-label': 'Open favourites', 'aria-haspopup': 'dialog' });
    list.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h14v16l-7-4-7 4z"/></svg>';
    list.addEventListener('click', openFavorites);
    bar.insertBefore(list, bar.firstChild);
    bar.insertBefore(favBtn, bar.firstChild);
    syncFavBtn();
    // The Studio rewrites the URL after every change; follow it
    var replace = history.replaceState;
    history.replaceState = function () { var r = replace.apply(this, arguments); syncFavBtn(); return r; };
  }

  // --- Settings toggle for haptics --------------------------------------------------------------
  function addHapticsSetting() {
    var grid = $('.settings-grid');
    if (!grid || !plugins.Haptics) return;
    var input = el('input', { type: 'checkbox', id: 'hapticsToggle' });
    input.checked = hapticsOn;
    input.addEventListener('change', function () { hapticsOn = input.checked; store.set('haptics', hapticsOn); if (hapticsOn) tick(); });
    var label = el('label', { class: 'check' }, [input, document.createTextNode(' Haptic feedback')]);
    grid.appendChild(label);
  }

  // --- Info window: what the app is, privacy and licences --------------------------------------
  function openInfo() {
    if (!openInfo.d) {
      var d = openInfo.d = dialog('infoDialog', 'About Guitar Positions');
      var version = ($('.footer .muted') && $('.footer .muted').textContent.trim()) || '';
      d.body.appendChild(el('p', { text: 'Scales, arpeggios, chords and fingerings on an interactive fretboard. ' + version }));
      d.body.appendChild(el('p', { text: 'No ads, no tracking, no account. The app works offline and makes no network requests. Songs and favourites are stored only on this device.' }));
      d.body.appendChild(el('h3', { text: 'Privacy' }));
      d.body.appendChild(el('p', {}, [link(SITE + '/impressum/', 'Privacy policy and imprint'), document.createTextNode(' (opens in your browser)')]));
      d.body.appendChild(el('h3', { text: 'Licences' }));
      var ul = el('ul', { class: 'app-licences' });
      [
        ['Guitar Positions', 'MIT License, © Lukas Schönsgibl. Source code: ', REPO],
        ['Capacitor and its Haptics and Status Bar plugins', 'MIT License, © Ionic', 'https://github.com/ionic-team/capacitor'],
        ['Android libraries (AndroidX)', 'Apache License 2.0', 'https://developer.android.com/jetpack/androidx'],
      ].forEach(function (row) {
        var li = el('li', {}, [el('b', { text: row[0] }), el('br'), document.createTextNode(row[1])]);
        if (row[2] === REPO) li.appendChild(link(row[2], 'GitHub'));
        else li.appendChild(link(row[2], row[2].replace('https://', '')));
        ul.appendChild(li);
      });
      d.body.appendChild(ul);
      d.body.appendChild(el('p', { class: 'muted', text: 'The plucked-string sound is generated on the device (Karplus-Strong synthesis); no audio files are used.' }));
    }
    openInfo.d.show();
  }

  function addInfoLink() {
    var nav = $('.footer nav');
    if (!nav) return;
    var a = el('a', { href: '#', id: 'appInfoLink', text: 'Info & licences' });
    a.addEventListener('click', function (e) { e.preventDefault(); openInfo(); });
    nav.insertBefore(a, nav.firstChild);
  }

  function init() {
    addTopButtons();
    addHapticsSetting();
    addInfoLink();
    syncStatusBar();
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', syncStatusBar);
    new MutationObserver(syncStatusBar).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
