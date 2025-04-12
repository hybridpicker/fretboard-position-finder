# V2 Chords Implementation

This update adds full support for V2 chords across all string sets. These chords follow Ted Greene's V-System voicing classification, with V2 representing drop-2 voicings.

## Added Chord Types

The following chord types have been implemented for V2 chords:

- **Dominant 7** - R-3-5-b7 (Dur mit kleiner Septime)
- **Major 7** - R-3-5-7 (Dur mit großer Septime)
- **Minor 7** - R-b3-5-b7 (Moll mit kleiner Septime)
- **Minor 7b5** - R-b3-b5-b7 (Halbvermindert)

## Supported String Sets

V2 chords are available on all string sets:

- High register: e-d, highA-g
- Middle register: b-A, g-A
- Low register: g-E, d-E
- Extended range: e-E, d-lowB, e-lowB

## All Key Centers

All chord types are implemented across all 12 key centers (C, C#/Db, D, D#/Eb, E, F, F#/Gb, G, G#/Ab, A, A#/Bb, B).

## Translations

All chord types are properly translated for locale support:
- English: "Dominant 7", "Major 7", "Minor 7", "Minor 7b5"
- German: "Dominant 7", "Dur 7", "Moll 7", "Moll 7b5"

## How V2 Chords Differ from V1

V2 chords are "drop-2" voicings, where the second highest note in a close-position chord is dropped by one octave.
This creates a more spread voicing with wider intervals, giving a different tonal character compared to V1 chords.

## How To Generate More V2 Chords

If you need to generate additional V2 chords, you can use the Django management command:

```
python manage.py generate_vsystem --v-system=v2 --root=0 --chord-type="Dominant 7" --string-set="e-b"
```

Or you can use the `update_v2_chord_fixture.py` script to ensure all V2 chords are properly included in the fixture.
