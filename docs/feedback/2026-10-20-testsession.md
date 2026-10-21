# Guitar Positions Studio – Test Session 2026-10-20

- Baseline: master `36fadbf` (web), native apps on branch `claude/festive-payne-53db8c` (`caa7e26`)
- Platforms under test: not specified per entry (shared Studio code: Web, Mac app, iPad/iOS, Android)
- Scope: observations only during the session; implemented afterwards on master (`14ad08d`…`8e1fdac`).

## Entries

<!-- New entries are appended below. Format: #ID · Title / Status / Area / Type · Priority / Platform / Observation / Expected / Steps / Suspected location / Open -->

### #1 · "Chords in this scale" lists too many chords – follow Graf/Nettles chord-scale theory
- Status: done (83dee77)
- Area: Scales (scale → chords panel, from #7 of 2026-10-19)
- Type: Wunsch (refinement) · Priority: mittel
- Platform: not specified (assumed all – shared Studio code)
- Observation: The chord list in the Scale view is partly overloaded; too many chords are shown.
- Expected: Recommendations follow the chord-scale theory of Richard Graf (Nettles/Graf, "The Chord Scale Theory & Jazz Harmony"): per scale only the chords it is the chord scale for (e.g. Dorian → m7/m6, Lydian → maj7(#11), Mixolydian → 7, Altered → 7alt), with available tensions instead of every chord that happens to be a pitch subset; diatonic triads/sevenths of the parent scale stay where they make sense.
- Steps: Scale mode → pick any heptatonic scale (e.g. C Major or Dorian) → "Chords in this scale" → expand "All fitting chords".
- Suspected location: `static/studio/js/theory.js:946` `chordsForScale()` – `others` is every library chord with ≥3 notes on every scale degree whose pitch set is a subset of the scale (no avoid-note / chord-function filter); rendered in `static/studio/js/app.js:430` `renderScaleChords()` as "Diatonic sevenths", "Diatonic triads" and the collapsible "All fitting chords (n)". A scale → primary chord(s) + available tensions / avoid notes mapping would need to live in `theory.js` next to `SCALE_LIBRARY` (`theory.js:88`) / `MESSIAEN_MODES` (`theory.js:114`); `scalesForChord()` (`theory.js:932`) could use the same mapping for the reverse direction.
- Open: Drop "All fitting chords" entirely or keep it collapsed but reduced? Should avoid notes (b9 rule, e.g. 4 over Ionian, b13 over Phrygian) exclude chords containing them (e.g. maj7 add11 on Ionian)? How to handle scales outside Graf's catalogue (bebop, Messiaen, exotic)? Should the reverse direction (chord → scales, search/Chord Namer) also be limited to Graf's recommendations?
- Decision (2026-10-20): Replace "All fitting chords" with the Graf/Nettles recommendations (diatonic rows stay, plus the chord(s) the scale is the chord scale for, with available tensions). Apply the same mapping in both directions (scale → chords and chord → scales in search/Chord Namer).

### #2 · Position 1 should always be the lowest position on the neck (around fret 1)
- Status: done (14ad08d)
- Area: Scales/Arpeggios (positions bar, numbering)
- Type: Bug (numbering inconsistent after transposition) · Priority: hoch
- Platform: not specified (assumed all – shared Studio code)
- Observation: Position numbering follows the root, so after transposing, position 1 can start at the 7th fret while position 5 sits at the 1st fret.
- Expected: Position 1 is always the first playable position near the nut (around fret 1), positions 2, 3, … follow ascending up the neck, independent of the root.
- Steps: Scale (or Arpeggio) mode → root e.g. B or A (root on low E at fret 7/5) → positions bar: "1" shows fr 7–…, a later number shows fr 0/1–….
- Suspected location: `static/studio/js/theory.js:476` `scalePositions()` – start frets are `rootFret + interval` per scale degree, wrapped down by 12 only when ≥ `maxStart` (12); positions are pushed in degree order and numbered at `theory.js:523-524` ("Conventional numbering: position 1 starts on the root …"), never sorted by fret. Fix: sort by `minFret` (start fret) before assigning `index`. Labels in `static/studio/js/app.js:335` `renderPositions()` ("fr min–max") need no change.
- Side effects to check: `state.position` is persisted in the URL (`pos`, `app.js:73/98`) and in legacy state (`app.js:59`), number-key shortcuts (`app.js:831`) and arrow stepping (`app.js:847`) – existing links/bookmarks would point to a different position after the change. 3-notes-per-string positions may be moved up an octave (`theory.js:492`), which affects sorting. Tests for `scalePositions` in `static/studio/js/theory.test.mjs` probably assert the root-based order.
- Open: What does "Bei Position All Past" refer to – the positions bar in general, or the "All (whole neck)" button? Should a position starting on open strings (fret 0) count as position 1? Keep the root-based numbering as an option (e.g. CAGED-style teaching) or replace it entirely? Same rule for box and 3-notes-per-string?
- Decision (2026-10-20): Position 1 = lowest position on the neck, open strings (fret 0) included, then ascending; same rule for box and 3-notes-per-string. No toggle for root-based numbering.

### #3 · Share fingerings/positions with students via link
- Status: done (2537cc1)
- Area: Sharing (all modes)
- Type: Wunsch · Priority: mittel
- Platform: Web (explicitly "in der Web-Applikation"); native apps could open the same links later
- Observation: There is no clear way to share a specific fingering, position etc. with students.
- Expected: A visible "Share"/"Copy link" action that produces a link reproducing exactly what the teacher sees (mode, root, type, position, system, selected voicing …) under https://fretboard.schoensgibl.com/.
- Steps: Pick e.g. Scale → A Dorian → Position 3 → want to send this to a student.
- Suspected location: `static/studio/js/app.js:85` `writeUrl()` already mirrors part of the state into the query string via `history.replaceState` (`mode`, `root`, `type`, `src`, `vs`, `strings`, `pos`, `sys`, `shape`), parsed in `readUrl` (`app.js:61-77`). Not in the URL: selected chord voicing (`state.selected`, `app.js:200`), tuning (`state.tuning`), labels (intervals/notes), neck filter (`state.neck`), bass filter. No share/copy button exists (no `navigator.share`/clipboard code in `app.js` or `templates/studio/index.html`). A selected-voicing parameter would need a stable id (index into a filtered list breaks when filters/library change).
- Open: Is copying the current URL enough, or should the link be a short/clean link? Should a shared link open in a reduced "student view" (no editing UI)? Should it pin the exact voicing frets (e.g. `shape=`-style) so it survives later library changes? Relates to #2 (position numbering change would alter what old `pos=` links show).
- Decision (2026-10-20): Full-state link – "Copy link" button (native share sheet on mobile); the link restores the exact view incl. selected voicing (stored as frets), tuning and labels; students see the normal app.

### #4 · Print/PDF export: A4, minimalist black and white
- Status: done (7805277)
- Area: Export/Print (scales, arpeggios, chords)
- Type: Wunsch · Priority: mittel
- Platform: Web (Mac/iPad would get it via the shared bundle; native print path to check)
- Observation: Fingerings covered in lessons cannot be produced as a printable sheet.
- Expected: A PDF/print output that fits exactly one A4 page, minimalist black and white (no colour fills, no UI chrome, good contrast for photocopies), containing the current diagram(s) plus title (root, type, position/voicing).
- Steps: Pick a scale position or chord voicing(s) → "Print / PDF" → A4 page.
- Suspected location: no print support yet – `static/studio/studio.css` has only `prefers-color-scheme`, width and reduced-motion media queries (lines 49, 325, 333, 349), no `@media print` / `@page { size: A4 }`. Simplest route: print stylesheet + `window.print()` (browser "Save as PDF") rendering the SVG fretboard (`static/studio/js/fretboard.js`) and chord boxes (`static/studio/js/diagram.js`) in a monochrome theme; a generated PDF (client-side library or server side) is heavier. Dark-mode tokens must not leak into print.
- Open: One diagram per sheet, or a sheet collecting several items (e.g. all positions of a scale, a lesson set)? Should it include fingers/interval labels, a header (date, title) or a free-text note? Is "Save as PDF" from the print dialog acceptable, or a direct PDF download button? Does the Mac/iPad app need its own print path (WKWebView print)?
- Decision (2026-10-20): Content = current view (scale/arpeggio: all positions + whole neck; chord: visible voicings as a grid), fitted to one A4 page, black and white, with title and fingers/intervals. Direct PDF download, generated by an own small vector PDF writer (lines, dots, built-in Helvetica) – no external library.

### #5 · Songs/exercises: own chord progressions with Ted Greene-style chord grids
- Status: done (8e1fdac)
- Area: New feature (chord progressions / song sheets)
- Type: Wunsch ("vielleicht auch gut") · Priority: niedrig
- Platform: Web (primary); native via shared bundle
- Observation: Teachers want to assemble chord progressions for songs and exercises to go through with students (e.g. "Song XY" → sequence of chords).
- Expected: Create a named song/exercise, add chords (root + type + chosen voicing) in order, optionally share (#3) and print (#4). Chord grids in the classic Ted Greene style: horizontal (strings running horizontally), at most 7 frets per grid.
- Steps: (new) Songs → "New song" → name → add chords → view/print.
- Suspected location: no progression/song concept in the code yet. Chord voicings come from `findChordShapes`/`voicingTemplateShapes` (`static/studio/js/theory.js`, imported in `static/studio/js/app.js:4`). Current chord boxes in `static/studio/js/diagram.js:3` `chordDiagram()` are vertical (strings vertical, frets as rows, min 4 rows, no upper limit) – a horizontal, max-7-fret variant would be a new renderer option. Persistence options: URL-encoded (fits #3, no server storage), `localStorage` via the existing `store` helper (`app.js:14`), or a Django model (would need accounts → personal data, data-protection review).
- Open: "Tate Green System" read as Ted Greene's chord-grid style – confirm. Horizontal with low E at the bottom or at the top? Should voicings wider than 7 frets be excluded or split? Should songs carry lyrics/sections/bars/rhythm or just a chord list? Where to store songs (link-only/local vs. server with accounts – the latter needs a GDPR assessment since students would be involved)? Should the Ted Greene grid also be offered in the normal Chord view?
- Decision (2026-10-20): Stored locally in the browser (existing `store` helper) and shareable/printable as a link (song encoded in the URL); no accounts, no server storage. Content: title, optional note, ordered chords (root, type, chosen voicing), optional section dividers (Verse/Chorus). Ted Greene grid: horizontal, high E on top, low E at the bottom, nut on the left, 7 frets by default; wider voicings allowed, grid widens. Grid used in songs and PDF only; the Chord view keeps its vertical boxes.

### #6 · Songs: where do the fingerings go? (adding chords was not discoverable)
- Status: done (0c2e868)
- Area: Songs
- Type: Bug (usability) · Priority: hoch
- Platform: all (shared Studio code)
- Observation: In a song only sections could be entered; it was unclear how to add chords/fingerings (only via Chords view → "Add to song").
- Expected: Add chords directly in the song; diagrams show the fingering.
- Fix: "Add chord" field in the song editor (type a symbol, click one of the eight easiest fingerings, Enter takes the first); dots show finger numbers by default (switchable to intervals / note names, also on the PDF).

### #7 · Chord diagrams always vertical
- Status: done (de69142), corrected in d7bf830: only song chords are vertical
- Area: Songs, PDF
- Type: Wunsch · Priority: hoch
- Platform: all
- Observation: The horizontal (Ted Greene-style) grids from #5 are not wanted.
- Expected: Fingering diagrams are always vertical.
- Fix: chord boxes in songs and PDF sheets and the scale positions on PDF sheets are vertical (low string left, nut on top, start fret beside the box); only the whole-neck overview stays horizontal. Supersedes the orientation decision in #5.
- Correction (user, same day): only song chords (song view, chord picker, song PDF) are vertical; scale positions and chord sheets stay horizontal (d7bf830).

### #8 · Explain the song workflow
- Status: done (0c2e868)
- Area: Songs
- Type: Wunsch · Priority: mittel
- Platform: all
- Expected: Short, user-friendly explanation of how songs work.
- Fix: "How songs work" box (four steps: new song, add chords, arrange, share/PDF), open while there are no songs or the song is empty.

### #9 · Neighbouring positions almost identical (C Ionian 5 vs 6 differ by one note)
- Status: done (09b03e1)
- Area: Scales (box positions)
- Type: Bug · Priority: hoch
- Platform: all
- Observation: In C Ionian, positions 5 and 6 differ by a single note; positions 1 and 2 are also nearly the same.
- Cause: `scalePositions()` in `static/studio/js/theory.js` built one box per scale degree; degrees a semitone apart (B/C, E/F) yield near-identical boxes.
- Fix: boxes sharing ≥ 85 % of their notes are merged (keep the more compact one, then the one on the root). 7-note scales now have five CAGED-like boxes (C major: fr 0–3, 2–6, 4–8, 7–10, 9–13); 3 notes per string keeps seven patterns. A test checks every scale, key and system for near-duplicates.

### #10 · Fretboard upright on desktop
- Status: done (03d5c06)
- Area: Fretboard (orientation)
- Type: Bug · Priority: hoch
- Platform: Web (desktop, live site)
- Observation: https://fretboard.schoensgibl.com/?mode=scale&root=C&type=major-ionian&pos=1&sys=box showed the main fretboard vertically on a wide screen.
- Cause: not reproducible with default settings; most likely a saved "Neck: Vertical" choice in that browser, which `orientation()` in `static/studio/js/app.js` applied on every screen size.
- Fix: wide screens always show the neck horizontally; the setting (now "Neck on phones") only applies to narrow portrait screens.
