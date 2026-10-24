# Guitar Positions Studio – Test Session 2026-10-24

- Baseline: master `8d59ba6` (web), native apps on branch `claude/festive-payne-53db8c` (`fbc90b3`)
- Platforms under test: not specified per entry (shared Studio code: Web, Mac app, iPad/iOS, Android)
- Scope: observations only during the session; implementation follows after "go".

## Confirmed design decisions (check every entry against these)

- Main fretboard always horizontal on wide screens; vertical only on narrow portrait screens ("Neck on phones").
- Only song chord diagrams (song view, chord picker, song PDF) are vertical; scale positions, chord PDF and neck overview are horizontal.
- Positions are numbered by neck position (position 1 = lowest); near-identical boxes (≥ 85 % same notes) are merged.
- Chord ↔ scale mapping follows the Nettles/Graf table (`CHORD_SCALES` in `theory.js`).
- Songs are stored locally in the browser and shared by link; no accounts, no server storage.
- PDF uses an own writer (`pdf.js`), no third-party library, A4 black and white.

## Entries

<!-- New entries are appended below. Format: #ID · Title / Status / Area / Type · Priority / Platform / Observation / Expected / Steps / Suspected location / Open -->

### #1 · Scale fingerings partly wrong ("Fingersätze passen teilweise nicht mehr")
- Status: withdrawn (user: pentatonic fingerings are correct, false alarm; tested on iPad, build state unknown)
- Area: Scales (positions, finger numbers)
- Type: Bug · Priority: hoch
- Platform: not specified (assumed all – shared Studio code)
- Observation: In the Scale view some positions show finger numbers that do not fit any more (presumably since the recent position changes); no concrete example given yet.
- Expected: Every scale position has a playable fingering (one finger per fret, index finger on the lowest fret, no avoidable stretches), as before the changes of 2026-10-20; fix by checking git history.
- Steps: Scale mode → any scale/key → step through positions and compare finger numbers (box and 3-notes-per-string).
- Suspected location: Finger logic itself is unchanged since `368e0a8` (`git log` shows only 14ad08d, 83dee77, 2537cc1, 09b03e1 touching `theory.js` afterwards, none touching `fingerBox`/`fingerStringGroup`, `static/studio/js/theory.js:354/384`). Candidates for the regression: (a) 14ad08d re-sorted/renumbered positions and 09b03e1 merges positions in `scalePositions()` (`theory.js:483-540`), keeping the *more compact* box by `maxFret-minFret`, not the one with the best fingering – the kept box may be one needing a stretch while the dropped neighbour was cleanly playable; (b) the UI shows `n.finger` only for fret > 0 (`app.js:204`), so open-string positions and `stretch` flags are not signalled. Read-only measurement with the default tuning, all 100 scales × 12 keys × box/nps: stretched boxes (`stretch` flag or nps span > 5 frets) 1285/3000 positions before (`368e0a8`), 1050/2676 now – i.e. no worse in rate, but e.g. C Ionian box now has stretches in positions 2, 3 (1 each) and 5 (2, fr 9–13).
- Conflicts with decisions: none (merge threshold ≥ 85 % and numbering by neck position stay).
- Open: Which scale/key/position/system did you see wrong (example link)? "Wrong" = finger numbers inconsistent with the frets, or positions that are unplayable/stretchy? Compare with which earlier version? Possible fix: choose the kept box in the merge by best fingering (fewest stretches), and re-check `fingerBox` for 5-fret boxes.

### #2 · Chord voicing not playable (Bb Major, frets 13-13-12-11-10-10 with two barres)
- Status: done (50dee54)
- Area: Chords (voicing generator, `assignFingers`)
- Type: Bug · Priority: hoch
- Platform: not specified (screenshot looks like web/desktop layout; shared Studio code)
- Observation: Screenshot (Chord · Bb Major, dots labelled with intervals 1/3/5) shows a 6-string voicing E13 A13 D12 G10 B11 e10, drawn with two barres (one over e–G at fret 10, one over A–low E at fret 13). User: "der ist nicht spielbar".
- Expected: Only voicings that can be fretted by four fingers in a realistic way are offered; shapes needing a barre with ring/pinky finger (or two barres) are excluded or ranked far down.
- Steps: Chord mode → Bb → Major → look at the voicing list/neck highlighting for the position around frets 10–13.
- Suspected location: `static/studio/js/theory.js:550` `assignFingers()` – with > 4 fretted notes it builds an index barre at the lowest fret (here fret 10 on G–e) and then, for the remaining notes, lets *any* same-fret group on adjacent strings share one finger ("A-shape" rule, `theory.js:~575-585`); here the group A13+E13 becomes a barre of finger 4 (pinky) over two strings, and B11 gets finger 2, D12 finger 3. A pinky barre is not realistic (and the 10→13 reach with an index barre makes it worse); the function should only accept shared fingers for the A-shape case (middle/ring finger on 3 adjacent strings at the same fret, higher strings) and reject barres for finger 4 and barres with fewer than all strings above/below. Callers: `findChordShapes` (`theory.js:732`), `voicingTemplateShapes` (`theory.js:~809`), Chord Namer (`app.js:432`); when `assignFingers` returns null the code falls back to a dummy fingering (`theory.js:670/809`) instead of dropping the shape – check that shapes with null fingering are filtered/penalised in `scoreShape` (`theory.js:~640`).
- Conflicts with decisions: none (song diagrams vertical / chord view horizontal unaffected).
- Open: Are such shapes shown in the main list or only as faded alternatives? Should the rule also cap the fret span (here 10–13 = 4 frets, borderline) and forbid two barres in one shape? Does the same issue occur in the song "Add chord" picker (`app.js:794`, uses the same generator)?
- Decision (2026-10-24, user said "go" without the question round; defaults taken): shapes whose fingering needs a little-finger barre are no longer generated (`assignFingers` returns null); span limit and two-barre rule unchanged. Test added.

### #3 · Chord search "G7#11" returns nothing
- Status: done (f4da6e5)
- Area: Chord search / chord library (`parseChordQuery`)
- Type: Bug (missing chord qualities) · Priority: mittel
- Platform: not specified (assumed all – shared Studio code)
- Observation: Typing a symbol like `G7#11` into the search gives no result.
- Expected: Common altered/extended dominant (and other jazz) symbols resolve to a chord with voicings.
- Steps: Search field → `G7#11` (same for e.g. `G9#11`, `G7b13`, `G7alt` – to be confirmed).
- Suspected location: `static/studio/js/theory.js:56` `CHORD_LIBRARY` has no dominant-7#11 – only `maj7#11` (`theory.js:83`); `parseChordQuery` (`theory.js:932`) → `findChordQuality` (`theory.js:910`) matches the quality only by identical library symbol/name/alias (`QUALITY_ALIASES`, `theory.js:877`), so unknown qualities return no hits. Missing in the library (no entry at all): `7#11` [0,4,7,6→ i.e. 1 3 5 b7 #11, optional 9], `9#11`, `13#11`, `7b13`/`7b9b13`, `7alt`, `m7(11)`, `m(maj9)`, `7b9#11`, `9sus4`, `13sus4`, `maj13`, `m13`, `m7#5`, `sus2/sus4` with 7th/9th. Note the Nettles/Graf table (`CHORD_SCALES`, `theory.js:~965-990`) already lists `7`, `9`, `13`, `7b5` for Lydian Dominant and tension `#11`, so adding `7#11` would also let it appear in the scale ↔ chord suggestions (needs a table entry for it). The database dump (never opened) may add more qualities via the merge in the app.
- Conflicts with decisions: none; new qualities must be added to `CHORD_SCALES` consistently with the Nettles/Graf mapping.
- Open: Which qualities besides `7#11` should be added (list above is a proposal)? Voicing `7#11` as 1-3-#11-b7 (no 5th) allowed or only with the 5th? Should unparsable input show a "no chord found – did you mean …" hint instead of an empty list? Parsing of inputs like `G7(#11)`, `G7+11`, `G7/#11` and `G13#11` – accept as aliases?
- Decision (2026-10-24, defaults): added `7#11`, `9#11`, `13#11`, `7b13`, `9sus4`, `maj13`, `m13`, `m(maj9)` with aliases (`7+11`, `7(#11)` …) and entered them in the Nettles/Graf table (Lydian Dominant, Mixolydian b6, Mixolydian, Dorian, Ionian, Melodic Minor). `7#11` keeps the 5th. `7alt`, `m7#5` not added.

### #4 · Scale list: order modes by degree within their parent scale
- Status: done (221f7d1, 49025ab)
- Area: Scales (type picker / list order)
- Type: Wunsch · Priority: mittel
- Platform: not specified (assumed all – shared Studio code)
- Observation: Modes are listed in arbitrary order, e.g. "Altered, Melodic Minor, …" in the melodic-minor family.
- Expected: Modes grouped by parent scale and ordered by degree, e.g. Melodic Minor (I), Dorian b2 (II), Lydian Augmented (III), Lydian Dominant (IV), Mixolydian b6 (V), Locrian #2 / Half-diminished (VI), Altered (VII); same for Major (Ionian … Locrian) and the Harmonic Minor family.
- Steps: Scale mode → open the type picker → group "Melodic minor family" / "Harmonic family".
- Suspected location: `static/studio/js/theory.js:163` `buildLibrary()` pushes scales in database order first (`catalog.scales`, `theory.js:173`), then the built-in `SCALE_LIBRARY` (`theory.js:88`); `scaleGroup()` (`theory.js:~148`) only assigns the group via `SCALE_GROUPS` (`theory.js:~137`), whose keyword lists have a degree order but are never used to sort. The picker (`app.js:980-997`) and the keyboard stepping order (`app.js:1282`) keep insertion order within a group. Fix: sort each group by the index of the matching keyword in `SCALE_GROUPS` (or add an explicit `degree` per scale). Note: names are matched with `includes()`, so "Lydian Augmented #2" also matches "lydian augmented" – the sort needs the longest/most specific match. Parent scales not yet in the library: Harmonic family modes depend on database entries (not opened).
- Conflicts with decisions: none. Check: stored/shared links use the scale `key`, not the list index, so reordering does not break old links; `app.js:1282` order only affects next/previous-type shortcuts.
- Open: Show the degree in the label (e.g. "II · Dorian b2") or order only? Order of the groups themselves (Major modes, Melodic minor, Harmonic minor, Harmonic major?) and where Pentatonic/Blues/Bebop/Symmetric go? Should "Major (Ionian)" etc. stay named as now?
- Decision (2026-10-24, defaults): order only, no degree in the label. Finding: the database holds scales with wrong names or without a root interval (e.g. a "Lydian Dominant" without 0), so several modes were missing or wrong. The melodic minor, harmonic minor and harmonic major families are now generated in code (`MODE_NAMES`), database scales without interval 0 are skipped, database ids are kept. Groups follow the menu order; `Major Pentatonic` moved from "Modes of Major" to "Pentatonic & Blues". Old links by key still resolve (same keys), except the wrongly built database variants, which now show the correct scale.

### #5 · Use an F major pentatonic fingering as the icon/favicon everywhere
- Status: done (5a4f218)
- Area: Branding (web favicon, PWA, Mac/iOS/iPad/Android app icons)
- Type: Wunsch · Priority: niedrig
- Platform: all (web + native apps; "überall")
- Observation: The current icon shows a generic fretboard with a three-note chord shape (root in accent colour); it is not tied to a real fingering.
- Expected: The motif on every icon is one fingering of the F major pentatonic scale (F G A C D), root F highlighted in the accent colour.
- Steps: Compare tab icon, PWA/home-screen icon and the Mac/iOS/Android app icons.
- Suspected location: Masters are generated by `scripts/build_studio_icons.py` (dark, `motif()` draws 6 strings, 3 frets and three hard-coded dots at `build_studio_icons.py:~28-50`; variants `icon.svg`, `icon-full.svg`, `icon-small.svg` with only 4 strings, `icon-macos.svg`, `icon-android-foreground.svg`) and by `scripts/build_icons.py` (light variant, same output folder `static/studio/icons`) – both write the same files, so decide which one is authoritative. Used by `templates/studio/index.html:15-19` (svg, favicon-32/48, apple-touch-icon) and the manifest. Native: `apps/scripts/generate_native_icons.py` (`npm run icons`) derives all iOS/macOS/Android icon sizes from `app-icon-1024.png`, `app-icon-macos-1024.png`, `app-icon-android-foreground-1024.png`. The legacy site header (`templates/favicon.html`, `static/favicon/v1|v2`) is a separate older icon set (also note a typo there: `apple-icon114x114.png` instead of `apple-icon-114x114.png`, line 8); "überall" might include it.
- Candidate fingering (computed with `scalePositions()`, F = pc 5, box system, standard tuning; low E → high E, fret(finger)): Position 1 (open position, frets 0–5): E 1(1,R) 3(3); A 0 3(3); D 0 3(3,R); G 0 2(2); B 1(1) 3(3); e 1(1,R) 3(3) 5(4). Position 5 (frets 10–13) is the other classic shape, F root on E string at fret 13/ A string fret 8 etc. Small sizes (16–48 px, 4-string `icon-small`) cannot show 13 dots – needs a reduced rendition (e.g. only the root + 5–6 dots, bolder strokes).
- Conflicts with decisions: none (icon is a horizontal neck motif; no rule on icon orientation).
- Open: Which position/shape (position 1 near the nut, or the common box 8–10 with F on the 8th fret)? Show all ten pentatonic notes or a reduced set for small icons? Keep the dark tile or switch to the light variant (`build_icons.py`)? Include the legacy header favicon (`static/favicon/v2`) in the change? Needs a new native build (Xcode/Android Studio) and App Store/Play listing icons are separate uploads.
- Decision (2026-10-24, defaults): F major pentatonic box on frets 7–10 (F on A string fret 8 and G string fret 10, both in the accent colour), light tile (`scripts/build_icons.py` is the authoritative script; `build_studio_icons.py` is the older dark variant and no longer matches). The 4-string favicon variant keeps D, G, B, e. Legacy header icons `static/favicon/v2` regenerated from the same masters (typo `apple-icon114x114` fixed). Native icons follow via `npm run icons`.
