# Guitar Positions Studio – Test Session 2026-10-19

- Baseline: master `31a9062` (web), native apps on branch `claude/festive-payne-53db8c` (`d9f783c`)
- Platforms under test: Web (local, http://localhost:8080), Mac app, iPad app (dev build)
- Scope: observations only; no code changes during the session.

## Entries

<!-- New entries are appended below. Format: #ID · Title / Area / Type · Priority / Platform / Observation / Expected / Steps / Suspected code location -->

### #1 · Search does not understand chord symbols (Maj7#11, Em7); no chord/scale suggestions
- Status: done
- Area: Chords (type picker search); touches Scales/Arpeggios/Chord Namer
- Type: Wunsch (possibly Bug, depending on mode) · Priority: mittel
- Platform: not specified (open: Web/Mac/iPad, which mode was active)
- Observation: Typing `Maj7#11` into the search field yields no result.
- Observation (2): Same for `Em7` – a full chord symbol with root. Searching it should show Em7 shapes/voicings and scales that fit it.
- Expected: Matching chords and fitting scales are suggested (e.g. Maj7#11 chord, Lydian-type scales; for Em7: Em7 shapes + Dorian/Phrygian/Aeolian on E etc.). Search parses root + quality and sets root and type, ideally across modes.
- Steps: Open type picker → type `Maj7#11` in the search field.
- Suspected location: `static/studio/js/app.js` `renderTypeList()` – plain case-insensitive substring match on `"<name> <symbol>"` (no root parsing, so `Em7` cannot match anything) of the *current mode's* list only; shows "No match" otherwise. `theory.js:83` defines chord `Major 7#11` / symbol `maj7#11` (so it should match in Chord mode; in Scale/Arpeggio mode the list contains no such entry, and there is no cross-mode suggestion).
- Open: which mode was active when searching? If Chord mode, it is a bug; if Scale/Arpeggio, it is the missing cross-mode suggestion.

### #2 · Bebop scales missing
- Status: done
- Area: Scales
- Type: Wunsch · Priority: mittel
- Platform: not specified (assumed all)
- Observation: There are no bebop scales in the scale list.
- Expected: Bebop scales available, e.g. Bebop Dominant, Bebop Major, Bebop Dorian (Minor), Bebop Melodic Minor / Harmonic (8-note scales).
- Steps: Scale mode → open type picker → look for "Bebop".
- Suspected location: `static/studio/js/theory.js` – no "bebop" string anywhere; scale list is built from the server catalogue plus the built-in library, grouped by `scaleGroup()`; a new group (e.g. "Bebop") and 8-note intervals would be needed (check that diagram/fretboard code handles 8-note scales).
- Open: should bebop scales also be offered as Chord Namer scale matches (#1-related)?

### #3 · V-System dropdown not sorted numerically
- Status: done
- Area: V-System
- Type: Bug · Priority: niedrig (quick fix)
- Platform: Mac (screenshot, native select menu); likely all
- Observation: Dropdown order is All systems, V3, V2, V4, V5 … V14, V1 – follows data order.
- Expected: Sorted numerically: All systems, V1, V2, V3 … V14.
- Steps: Chord type with V-System voicings → Source "V-System" → open the system select.
- Suspected location: `static/studio/js/app.js` (~line 358), `systems = [...new Set(type.voicings.map((v) => v.system))]` – no sort; sort by numeric part of "V<n>".

### #4 · Add Messiaen modes of limited transposition
- Status: done
- Area: Scales
- Type: Wunsch · Priority: niedrig
- Platform: all
- Observation: Messiaen modes may be added to the scale library ("kann man auch ruhig nehmen").
- Expected: Modes 1–7 (Mode 1 = whole tone, Mode 2 = octatonic/diminished, Mode 3 … Mode 7), ideally in the existing "Symmetric" group.
- Suspected location: `static/studio/js/theory.js` ~line 101 (built-in scale list; Whole Tone exists, no Messiaen entries) and `SCALE_GROUPS` (~line 109, "Symmetric"). Related: #2 (bebop, also 8+-note scales – handle both together).
- Open: Modes 4–7 have 8 notes; check diagram/fretboard handling together with #2.

### #5 · App icon with black background does not match overall design
- Status: done (web only; native app icons on branch claude/festive-payne-53db8c still need the refresh)
- Area: Design/Layout (icons)
- Type: Wunsch · Priority: mittel
- Platform: not specified (open: Mac app / iPad app / browser tab / PWA?)
- Observation: The icon with the black background does not fit the minimal light overall design.
- Expected: Icon consistent with the Studio's look (light/minimal background).
- Suspected location: `static/studio/icons/` – full set incl. `icon.svg`, `icon-small.svg` (favicon in `templates/studio/index.html:15`), `icon-macos.svg`, `app-icon-*.png`, maskable PNGs, `apple-touch-icon.png`; referenced in `static/studio/manifest.webmanifest`. Native apps use their own copies on branch `claude/festive-payne-53db8c`.
- Open: which icon exactly (see Platform)? All variants should be regenerated consistently.

### #6 · Ensure public site is https://fretboard.schoensgibl.com/ (only domain)
- Status: done in repo (ALLOWED_HOSTS/CSRF/canonical); server-side check still open for the go-live session
- Area: Deployment
- Type: Wunsch · Priority: hoch (blocks go-live)
- Platform: Web/PWA, server almalinux9
- Observation: Make sure the website to view is https://fretboard.schoensgibl.com/.
- Expected: App reachable only under that domain via HTTPS (other hostnames / http redirect or rejected; manifest, canonical/meta URLs and native app server URLs, if any, point to it).
- Server status: not verified in this session (no server access by rule). Go-live is covered by `~/deploy-prep/fretboard-schoensgibl/GO_LIVE_PROMPT.md` on almalinux9; commit `0052d25` documents the domain as the only one.
- Open: verify after go-live in a server session (nginx server_name, ALLOWED_HOSTS, HTTP→HTTPS redirect, old domain behaviour).

### #7 · Scales view should suggest matching chords
- Status: done
- Area: Scales (cross-mode suggestions)
- Type: Wunsch · Priority: mittel
- Platform: all
- Observation: In Scale mode, chords that fit the selected scale should be suggested.
- Expected: For the selected scale + root, a list of fitting chords (e.g. diatonic 7th chords / chords whose notes are a subset of the scale), each opening the Chords view with root and type set.
- Suspected location: `static/studio/js/app.js` `renderNamer()` (~line 410) already does the reverse (notes → matching chords/scales, with `data-open-chord` / `data-open-scale` buttons); a scale → chords panel could reuse that matching logic in `theory.js`. Related: #1 (search suggestions), #2/#4 (new scales).

