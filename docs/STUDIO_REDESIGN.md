# Guitar Positions Studio: Redesign Proposal and Native-App Plan

Status: proposal, October 2026. Covers the Studio UI served at `/` (the previous UI stays at `/classic/`).
Facts about third-party platforms were checked on 2026-10-18; items that could not be verified are marked **(to verify)**.

---

## 1. Summary

Guitar Positions Studio is a single-page fretboard tool for finding scales, arpeggios and chords on the
guitar neck, with fingerings, sound and a reverse chord lookup. It replaces the multi-form classic UI
with one screen: pick a key, pick a type, see the neck.

Audience, from first lesson to jazz gigs:

- **Beginners:** open-position chords ranked by ease, finger numbers on every note, "play" to hear it.
- **Intermediate players:** five box positions or 3-notes-per-string (3NPS) patterns per scale, arpeggio positions.
- **Jazz/advanced players:** extended chords, drop-2/drop-3/drop-2+4 voicing labels, every inversion of the
  V-System voicing library, chord namer with slash-chord and "scales that fit" results.

The client is about 1,800 lines of dependency-free ES modules plus one stylesheet; Django supplies the
musical catalogue (scales, arpeggios, V-System voicings) as JSON.

## 2. Problems with the previous UI (evidence from the repo)

| Area | Evidence |
|---|---|
| Asset sprawl | `static/css/` holds 42 stylesheets (~7,000 lines); `static/js/` holds 56 scripts (~24,000 lines). `fretboardbase.html` plus its header/footer includes reference ~34 stylesheet and ~50 script tags. |
| Debug code in production | 17 top-level scripts named `*debug*`, `*fix*`, `*test*` (e.g. `debug-logger.js`, `cursor-debug.js`, `playtone-autofix.js`, `string_toggle_fix.js`, `cookie_test.js`); `fretboard-inlay-debug.css` and `debug-logger.js` are loaded by the base template; ~380 `console.log` calls in `static/js/`. |
| Layered patches | Fix-on-fix files (`note-visibility-fix.css`, `recursive-function-fix.js`, `validation_panel_fix.js`), commented-out `<script>` tags, ad-hoc cache busters such as `?v=20230416_final5`. |
| Interaction model | Separate forms per mode (`forms/fretboard_form.html`, `forms/fretboard_form_chords.html`), overlay menu, sidebar and search overlay competing for the same job; full page reloads on every selection. |
| Data quirks surfaced to users | Scale names stored as "Aeloian" and "Minor Penatonic"; chord name stored as both "Minor 7b5" and "Minor7b5"; model fields `eigth_note` / `twelth_note`; incomplete records with fewer than three notes. The Studio now normalises these (`cleanScaleName()` in `theory.js`, `_normalise_chord_name()` and the `< 3 intervals` filter in `views_studio.py`) instead of showing them. |
| No testable core | Theory, rendering and DOM state are interleaved, so fingering logic could not be unit-tested. |
| i18n leftovers | `i18n_patterns` is still used in `fretboard/urls.py` while `LocaleMiddleware` is commented out in settings. |

## 3. Product principles and information architecture

**Principles**

1. One screen, no reloads: every control changes state instantly and is reflected in the URL (shareable).
2. Show the music, not the controls: the neck is the hero; secondary settings live behind one gear button.
3. Correct theory by default: enharmonic spelling follows the key (`spellNote()`), interval labels follow the formula (b3 vs #9, #11 vs b5).
4. Playable over exhaustive: chord shapes are filtered for four-finger playability and ranked by ease.
5. Works everywhere: phone (vertical neck), desktop (horizontal), left-handed, keyboard-only, offline (PWA).
6. Private by construction: no accounts, no tracking, no third-party requests.

**Structure**

```
Top bar      brand · modes [1 Scales | 2 Arpeggios | 3 Chords | 4 Chord Namer] · sound · settings
Selector     12 key buttons (radiogroup) · type combobox with search, grouped (Modes of Major, Pentatonic & Blues, ...)
Headline     "C Dorian" · note chips coloured by role (tap = listen) · Play + tempo
Fretboard    SVG neck · legend (role colours, "faded = same notes elsewhere")
Mode panel   Scales/Arpeggios: positions bar (All, 1..n with fret range) · Box | 3NPS · Fingers | Intervals | Notes
             Chords: fingering finder (Best shapes | V-System) · bass filter · neck region · shape cards
             Chord Namer: tap frets → best name, alternatives, fitting scales, "Show all shapes"
Settings     tuning (8) · frets (12–24) · orientation · left-handed · theme · note spelling
```

Cross-links close the loop: Chord Namer results open the Chords or Scales mode with the same root.

## 4. Features

### 4.1 Implemented now

**Engine (`static/studio/js/theory.js`, pure functions, no DOM)**

- Built-in formula library: 28 chord types (triads to 13ths) and 13 scales, merged with the database catalogue (duplicates by pitch-class set are collapsed).
- Scale/arpeggio positions: CAGED-style box positions (one finger per fret, stretch-aware anchor selection) and 3NPS patterns (2NPS for pentatonics), each with finger numbers; open/drop tunings fall back to 5-fret windows.
- Chord-shape finder: enumerates shapes per fret window, requires all essential tones (fifth optional on 7th chords; 9/11 optional on 13ths), rejects more than one interior mute, assigns fingers with barre detection (index barre plus a shared-finger partial barre as in the A shape), and ranks by an ease score (span, barres, mutes, root in bass, open strings).
- V-System templates from the database turned into concrete shapes for any root, with every inversion (each voice rotates to the next chord tone, mirroring the Django `ChordPosition` offsets).
- Voicing classification: Close, Drop 2, Drop 3, Drop 2+4, Spread; inversion naming.
- Reverse lookup: chord identification (incl. slash chords, rootless/no-5th tolerance) and fitting scales.
- 8 tunings: Standard, Eb, Drop D, DADGAD, Open G, Open D, 7-string, 8-string.
- Unit tests: `node --test static/studio/js/` (`theory.test.mjs`).

**UI (`app.js`, `fretboard.js`, `diagram.js`, `audio.js`)**

- Four modes with keyboard shortcuts: `1`–`4` mode, `←/→` position or shape, `↑/↓` key, `Space` play, `M` mute.
- URL state (`?mode=&root=&type=&pos=&sys=&shape=`) with `history.replaceState`; legacy `models_select=…` links are mapped server-side.
- SVG neck: horizontal, vertical (auto on portrait phones), left-handed, 12–24 frets, inlays, barre and mute markers; ghosted notes show the same pitches outside the active position.
- Labels: fingers, intervals or note names; theory-correct, sharp or flat spelling.
- Chord cards with mini chord boxes, ease rating (1–5), voicing/inversion meta, fret string.
- Karplus-Strong plucked-string synth (cached `AudioBuffer`s), strum, sequenced playback with note highlighting, tempo 50–220.
- Settings persisted in `localStorage` (`gp-*` keys); dark/light/system theme without flash.
- PWA groundwork in progress in the working tree: `static/studio/manifest.webmanifest` and a root-scoped service worker (`positionfinder/views_pwa.py`, fingerprinted shell precache).

### 4.2 Next (not implemented)

| Idea | Notes |
|---|---|
| CAGED shape labels | Tag box positions as C/A/G/E/D shapes for standard tuning. |
| Practice mode | Metronome, loop a position, ascending/descending/sequence patterns (3rds, 4ths), count-in. |
| Progressions and voice-leading | Enter ii–V–I etc.; pick voicings that minimise total finger movement between chords. |
| Capo | Transpose shapes and labels; open-position finder relative to capo. |
| Custom tunings | Editor for arbitrary MIDI per string; persisted locally; share via URL. |
| Export | PNG/SVG of the neck, PDF sheet of all positions, ASCII/Guitar Pro-style tab. |
| Favourites | Saved shapes/scales in `localStorage` only (no account). |
| Ear training | Interval/chord-quality quizzes using the same synth. |
| MIDI input | Web MIDI: play a chord on a MIDI guitar/keyboard and name it. |
| i18n DE/EN | Externalise strings; German note names (H/B) as a spelling option. |
| Accessibility pass | Text description of the active position for screen readers (see 5.4). |

## 5. Design system

### 5.1 Colour roles

Colour encodes the function of a note; labels always carry the same information, so colour is never the only cue.

| Role | Token | Dark | Light |
|---|---|---|---|
| Root | `--c-root` | `#f5a524` amber | `#e8900c` |
| 3rd | `--c-third` | `#2ec4b6` teal | `#0f9d8f` |
| 5th | `--c-fifth` | `#5b9cf6` blue | `#2f74e0` |
| 7th | `--c-seventh` | `#b18cff` violet | `#8655e8` |
| Tension/other | `--c-tension` | `#cfd3da` grey | `#5d636e` |

Each role has a matching `--ink-*` token for text on the dot. The accent colour equals the root colour, so "home" reads the same everywhere.

### 5.2 Themes

Tokens live on `:root`; light values apply via `@media (prefers-color-scheme: light)` unless the user forces `data-theme`. A wood-toned neck (`--wood-*`, `--string-wound`) is used in both themes.

### 5.3 Typography and third parties

- System font stack (`ui-sans-serif, system-ui, -apple-system, …`) for all UI text; monospace for fret strings.
- Self-hosted Dosis SemiBold (`static/fonts/dosis/`) for the wordmark only.
- No Google Fonts, CDNs, analytics or embeds: the page makes only same-origin requests. This avoids transferring visitor IP addresses to third parties (relevant under GDPR since the 2022 Munich Regional Court ruling on remotely loaded Google Fonts).

### 5.4 Accessibility

In place: skip link, `role="tablist"`/`radiogroup`/`aria-pressed`/`aria-expanded` on controls, `:focus-visible` outline, keyboard shortcuts, `prefers-reduced-motion`, `aria-live` toast.
To do: test role colours for colour-vision deficiencies (teal vs. blue for 3rd/5th), verify text contrast of `--ink-*` on each role colour (WCAG AA), ensure ≥44 px touch targets on the vertical neck, and add a textual summary of the active position/shape for screen readers (the SVG notes are currently not individually announced).

## 6. Architecture

```
Django (content)                         Browser (zero-build SPA)
───────────────────────────────          ───────────────────────────────────────
models Notes / ChordNotes / Root  ─┐     templates/studio/index.html
views_studio.build_catalog()       ├──►  <script type="application/json" id="catalog-data">
  cache 'studio_catalog_v1' (1 h)  │     app.js  ── state, URL, events
GET /api/catalog/ (max-age 3600) ──┘       ├─ theory.js     pure engine (node --test)
_legacy_state() → id="legacy-state"        ├─ fretboard.js  SVG neck
                                           ├─ diagram.js    chord boxes
                                           └─ audio.js      Web Audio synth
```

- **Django as catalogue backend.** Musical content stays editable in the admin. `build_catalog()` emits pitch-class formulas and V-System templates (`string` + `interval` per tone), not rendered positions; all geometry is computed client-side, so any tuning works with the same data.
- **Zero build step.** Native ES modules, no bundler, no npm dependencies at runtime. Cache busting through `?v={{ APP_VERSION }}` on the entry files; the service worker fingerprints the shell.
- **Testability.** `theory.js` has no DOM access and runs under `node --test`; Django view/catalogue tests live in `positionfinder/tests/test_studio.py`.
- **Data flow.** The catalogue is embedded in the HTML (one request for first paint) and also exposed at `/api/catalog/` for the PWA and native builds. Client state is derived purely from `state` + catalogue in `render()`.
- **Caching.** Catalogue cached in Django's cache for one hour. Gap: the key is not invalidated when admin data changes; add a `post_save`/`post_delete` signal on the three models or include a content hash in the key.
- **Legacy URLs.** `/?models_select=1&root=…&notes_options_id=…&position_select=…` and the chord parameters are translated by `_legacy_state()`; `/classic/` keeps the old UI reachable during transition.
- **Engine notes.** `findChordShapes()` contains a no-op `if (w === 0) continue;` and a comment about dropping subset shapes that is not implemented yet; worth cleaning when the progression feature lands.

### 6.1 SEO for an SPA

Current state: one indexable URL. `index.html` sets `<link rel="canonical">` to `/` for every state, and `positionfinder/sitemaps.py` lists only `fretboard`, `about`, `impressum`. Query-string states are effectively invisible to search engines.

Proposal:

1. Server-rendered landing pages per entity, e.g. `/scales/c-dorian/`, `/arpeggios/g-maj7/`, `/chords/a-m7b5/`: real `<h1>`, intervals, note names, a static SVG of position 1 / the easiest shape, short explanatory text, and a "Open in Studio" link (`/?mode=…`). The same `theory.js` logic can be ported or run once at build time to emit the SVG.
2. Self-canonical URLs on those pages; keep `/` canonical for the app shell.
3. Extend the sitemap with all root × type combinations (12 roots × catalogue size) and prioritise common keys.
4. Reuse the existing `templates/seo/*_structured_data.html` partials on the landing pages.
5. Add `hreflang` only once DE/EN content actually exists.

## 7. Native apps plan (iOS, macOS, Android)

### 7.1 Options

| Option | Reuse of web code | Store presence | Offline | Effort | Main risk |
|---|---|---|---|---|---|
| (a) PWA (manifest + service worker) | 100 % | none (Android can install; iOS via "Add to Home Screen") | yes | low, already in progress | discoverability; iOS install UX |
| (b) Capacitor wrapping the same bundle | ~100 % | App Store + Play | yes (assets bundled) | medium | guideline 4.2 if it feels like a website |
| (c1) macOS via "Designed for iPad" on Apple silicon | iOS build as-is | Mac App Store (iPhone & iPad apps section) | yes | ~zero | iPad-style UI on Mac; Apple silicon only |
| (c2) macOS via Mac Catalyst from the Capacitor iOS project | iOS project | Mac App Store | yes | low–medium | not an officially supported Capacitor target **(to verify)** |
| (c3) Tauri 2 (macOS, also iOS) | 100 % web | Mac App Store supported, plus DMG | yes | medium | second native toolchain (Rust) to maintain |
| (d) Native rewrite (SwiftUI + Kotlin/Compose) | 0 % (engine must be ported twice) | both | yes | very high | three codebases for one maintainer |

### 7.2 Recommendation

**PWA first, then Capacitor for iOS and Android from the same bundle, macOS via "Designed for iPad" on Apple silicon; revisit Catalyst or Tauri only if Mac users ask for a real Mac UI.**

Reasons: the engine is the product and it is already pure JS with tests; a rewrite would duplicate ~750 lines of fingering logic in two languages with no user-visible gain. Capacitor 8 is current and targets the Play API level that is now mandatory. "Designed for iPad" gives a Mac presence for free, and the Studio already handles keyboard shortcuts and wide layouts.

### 7.3 Facts that shape the plan (verified 2026-10-18)

- **Capacitor:** latest stable is 8.5.3 (npm `@capacitor/core`, published 2026-10-07); v8 released 2025-12-08 and requires iOS 15+, Android 7 (API 24)+, Node 22, Xcode 26. v9 is in alpha (iOS 16+, Xcode 27, Node 24). v7 extended support ends 2026-12-08. Capacitor 8 sets `compileSdkVersion`/`targetSdkVersion` 36 and creates Swift Package Manager iOS projects by default.
  Sources: <https://registry.npmjs.org/@capacitor/core>, <https://capacitorjs.com/docs/next/main/reference/support-policy>, <https://capacitorjs.com/docs/updating/8-0>
- **Google Play target API:** from 2026-08-31 new apps and updates must target Android 16 (API 36); extension possible to 2026-11-01.
  Source: <https://developer.android.com/google/play/requirements/target-sdk>
- **Google Play new personal accounts:** closed test with at least 12 testers opted in for 14 consecutive days before production access.
  Source: <https://support.google.com/googleplay/android-developer/answer/14151465>
- **Apple SDK minimum:** uploads must be built with Xcode 26 / iOS 26 SDK since 2026-04-28.
  Source: <https://developer.apple.com/news/upcoming-requirements/>
- **Apple guideline 4.2 (Minimum Functionality):** "Your app should include features, content, and UI that elevate it beyond a repackaged website." 4.2.2 adds that apps should not be primarily web clippings or collections of links.
  Source: <https://developer.apple.com/app-store/review/guidelines/>
- **Apple donations:** 3.1.1 allows in-app purchase currencies to "tip" the developer; 3.2.1(vi) lets *approved nonprofits* fundraise in-app (with Apple Pay); 3.2.2(iv) forbids collecting funds for charities in-app unless approved, such apps must be free and collect outside the app (Safari/SMS). A donation to the developer is therefore a tip and falls under in-app purchase.
  Source: <https://developer.apple.com/app-store/review/guidelines/>
- **Apple App Privacy:** data processed only on device is not "collected"; a privacy policy URL is required for every app.
  Source: <https://developer.apple.com/app-store/app-privacy-details/>
- **Google Play payments:** Play Billing must not be used for tax-exempt donations; tips to a developer are not addressed in the excerpt checked **(to verify)**.
  Source: <https://support.google.com/googleplay/android-developer/answer/9858738>
- **Tauri 2:** documents Mac App Store and iOS App Store distribution (sandbox entitlements, Mac Installer Distribution certificate).
  Source: <https://v2.tauri.app/distribute/app-store/>

### 7.4 How the app clears guideline 4.2

- Assets and catalogue are bundled; the app works fully offline and never loads the website in a web view (no `server.url` in production config).
- Native integrations: haptic tick on fret tap / position change (`@capacitor/haptics`), native share sheet for a shape or scale link (`@capacitor/share`), status bar and safe-area handling, splash screen, iPad split-view and hardware-keyboard shortcuts.
- App-only value: favourites and practice mode (section 4.2) shipped with or before the first store release.
- No donation links, external "visit website" banners or link collections in the iOS build.

### 7.5 Offline catalogue bundling

> Implemented in phase 1 as `scripts/build_app_bundle.py` (see `apps/README.md`): the catalogue is inlined into `www/index.html` as the same `catalog-data` JSON script the web page uses, so `app.js` needs no loader change. The bullets below were the original sketch.

- Build step: `python manage.py export_catalog > www/catalog.json` (new management command wrapping `build_catalog()`), or `curl https://fretboard.schoensgibl.com/api/catalog/`. Contains formulas only, no personal data.
- A small `www/index.html` (static copy of `templates/studio/index.html` without Django tags) loads `catalog.json` instead of the inline `json_script`; `app.js` gets a tiny loader that prefers inline data and falls back to `fetch('catalog.json')`.
- Optional: check `/api/catalog/` for a newer `version` when online and cache it; the bundled copy remains the baseline.

### 7.6 Audio

- Web Audio works in WKWebView and Android WebView; the synth renders buffers once and plays them, so CPU load is small.
- iOS: an `AudioContext` must be started from a user gesture (already the case: play/tap); the hardware silent switch can mute web audio. Safari's `navigator.audioSession.type = 'playback'` may address this **(to verify on device)**; fallback is a minimal native plugin setting `AVAudioSession` category `.playback`.
- Latency: acceptable for "tap to hear" and sequenced playback (scheduled ahead). For a future practice metronome, schedule on the `AudioContext` clock instead of `setTimeout` (current `playSequence()` uses `setTimeout`). Measure Android WebView output latency on low-end devices before considering a native audio plugin **(to measure)**.

### 7.7 Store, privacy and donations

- **App Privacy (Apple):** "Data Not Collected": no network traffic in the app except the optional catalogue update, which carries no identifiers and is not retained beyond server access logs. **Play Data safety:** declare no data collected or shared.
- **Privacy policy / Impressum:** link the existing `impressum` page in the store listings and inside the app (settings sheet). The text must describe the app as well as the website.
- **Donations:** hide `STRIPE_DONATE_URL` in native builds (build flag). Optional later: an Apple in-app purchase "tip" and the Play Billing equivalent. Only an approved nonprofit could fundraise directly, which does not apply here.
- **Age rating:** 4+ / Everyone; no user-generated content, no ads.

### 7.8 Accounts, signing, CI and versioning

- **Accounts:** Apple Developer Program (annual fee; individual or organisation, organisation needs a D-U-N-S number), Google Play Console (one-time registration fee; identity verification; personal accounts face the 12-tester/14-day rule). Exact fees **(to verify)**.
- **Signing:** iOS distribution certificate and profiles via fastlane `match` (encrypted private repo or storage) or Xcode automatic signing; Android upload key with Play App Signing. Keys and the App Store Connect API key live only in GitHub Actions secrets, never in the repository or prompts.
- **CI (GitHub Actions):** job 1 (ubuntu) runs `node --test` and Django tests, exports `catalog.json`, `npx cap sync`; job 2 (macos runner, Xcode 26) `fastlane ios beta` → TestFlight; job 3 (ubuntu) `./gradlew bundleRelease` + `fastlane supply` → Play internal track. Release on tag `v*`.
- **Versioning:** one source of truth (`settings.VERSION`, shown as `APP_VERSION`) propagated to `package.json`, `CFBundleShortVersionString` and `versionName`; build numbers (`CFBundleVersion`, `versionCode`) from the CI run number, always increasing. Web, PWA and apps share the semantic version.

### 7.9 Phased timeline (one developer, part-time; rough)

| Phase | Scope | Effort |
|---|---|---|
| 0. Web launch | Deploy Studio to fretboard.schoensgibl.com, finish PWA (icons, offline test, update flow), privacy text update | 3–5 days |
| 1. SEO pages | Landing pages per scale/chord, sitemap, canonical fixes | 4–6 days |
| 2. App-only features | Favourites, practice loop + AudioContext-clock metronome, share | 5–8 days |
| 3. Capacitor shell | `www/` bundle, catalogue export, haptics/share/status bar plugins, iOS audio session check, icons/splash | 4–6 days |
| 4. Store setup | Accounts, listings, screenshots (iPhone, iPad, Android phone/tablet), privacy forms, Play closed test (≥14 days elapsed) | 3–4 days + waiting |
| 5. CI and release | GitHub Actions + fastlane, TestFlight and Play internal → production | 3–5 days |
| 6. macOS | Enable "Designed for iPad" availability, test on Apple silicon; evaluate Catalyst/Tauri only on demand | 1 day (+ 5–10 days if Catalyst/Tauri) |

Total to both stores: roughly 4–6 calendar weeks of focused work, dominated by store review and the Play testing window.

## 8. Compliance notes

- **GDPR scope is minimal:** no accounts, no forms, no analytics, no third-party requests. Personal data processed is limited to what the web server necessarily sees (IP address, user agent in access logs); retention of those logs should be short and stated in the privacy text.
- **Cookies:** the Studio template uses no CSRF token or session; confirm in production that Django sets no cookie on `/` **(to verify)**.
- **Local storage:** `gp-*` keys hold only user-chosen preferences (tuning, theme, labels, tempo). This is storage the user requests for the service; the privacy text should mention it (ePrivacy/Austrian TKG 2021 consent exemption for strictly necessary storage; legal confirmation is the owner's call).
- **Apps:** no SDKs that collect data (no Firebase/Crashlytics/analytics). If crash reporting is ever wanted, use the platform's opt-in reports (App Store Connect, Play Console vitals) rather than a third-party SDK.
- **Impressum and privacy page** must be reachable from the website footer (already linked), from inside both apps, and from both store listings.
- **EU AI Act:** not applicable. The Studio contains no AI system; chord finding, fingering and identification are deterministic, rule-based algorithms.

## 9. Deployment target

- Production URL: **https://fretboard.schoensgibl.com** on the AlmaLinux 9 server (fresh instance, Django behind Nginx, HTTPS required for the service worker).
- **Decision (2026-10-18):** fretboard.schoensgibl.com is the only domain. guitar-positions.org is not used any more (the old deployment was removed in January 2026, the domain no longer resolves and no redirect is planned). Legacy query parameters (`?models_select=…`) are still mapped for old bookmarks on the new host.
- Server checklist: `collectstatic`; long-lived cache headers for fingerprinted static files, short for `index.html` and `/sw.js`; gzip/brotli; `/api/catalog/` cached 1 h; clear the `studio_catalog_v1` cache key on deploy when catalogue data changed; set `CSRF_TRUSTED_ORIGINS`/`ALLOWED_HOSTS` for the new host; update `robots.txt` and sitemap host.
- Server work (deploy, Nginx, certificates) is done in a Claude Code session on the AlmaLinux 9 host, not from the workstation.

## 10. Open decisions for the owner

1. **Native path:** approve "PWA → Capacitor (iOS + Android) → Designed for iPad on Mac" or prefer a different macOS route (Catalyst/Tauri)?
2. **Developer accounts:** publish as individual or organisation (affects Apple D-U-N-S requirement and Google's 12-tester rule)?
3. **App price/monetisation:** free with no donation link in apps, or add an in-app "tip" purchase?
4. **App name and bundle ID:** e.g. "Guitar Positions Studio", `com.schoensgibl.guitarpositions`?
5. **Classic UI:** set a removal date for `/classic/` and the 56 legacy scripts / 42 stylesheets?
6. **SEO pages:** approve the landing-page URL scheme (`/scales/<root>-<type>/` etc.) before content is generated.
7. **i18n:** is German a launch requirement for the apps, or a later release? If later, remove the unused `i18n_patterns` prefixing or re-enable `LocaleMiddleware` consistently.
8. **Database clean-up:** fix the "Aeloian"/"Penatonic"/"Minor7b5" records at the source (data migration) and keep the client-side fixes only as a safety net?
9. **Privacy text:** who updates the privacy policy for the new domain, the PWA and the apps, and what log retention period is stated?
