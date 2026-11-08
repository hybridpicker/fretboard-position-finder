// Run with: node --test static/studio/js/
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  TUNINGS, getTuning, scalePositions, assignFingers, findChordShapes, classifyVoicing,
  identifyChords, identifyScales, spellNote, intervalLabels, buildLibrary, voicingTemplateShapes,
  CHORD_LIBRARY, SCALE_LIBRARY, fingerStringGroup,
  parseChordQuery, scalesForChord, chordsForScale, MESSIAEN_MODES, neckNotes, CHORD_SCALES, chordScaleFor, positionOverlap,
  shapeFromFrets,
} from './theory.js';

const std = getTuning('standard');
const byString = (notes, s) => notes.filter((n) => n.string === s).map((n) => n.fret);

test('A minor pentatonic box 1 is the classic shape with fingering', () => {
  const positions = scalePositions(9, [0, 3, 5, 7, 10], std, { system: 'box' });
  assert.equal(positions.length, 5);
  const box1 = positions.find((p) => p.startInterval === 0);
  assert.ok(box1, 'a position starts on the root');
  assert.deepEqual([0, 1, 2, 3, 4, 5].map((s) => byString(box1.notes, s)), [[5, 8], [5, 7], [5, 7], [5, 7], [5, 8], [5, 8]]);
  assert.deepEqual(box1.notes.filter((n) => n.string === 0).map((n) => n.finger), [1, 4]);
});

test('A minor pentatonic box 2 uses the A string stretch, not the pinky on low E', () => {
  const positions = scalePositions(9, [0, 3, 5, 7, 10], std, { system: 'box' });
  const box2 = positions.find((p) => p.startInterval === 3);
  assert.deepEqual([0, 1, 2, 3, 4, 5].map((s) => byString(box2.notes, s)), [[8, 10], [7, 10], [7, 10], [7, 9], [8, 10], [8, 10]]);
});

test('G major second position box starts on the root', () => {
  const positions = scalePositions(7, [0, 2, 4, 5, 7, 9, 11], std, { system: 'box' });
  const pos = positions.find((p) => p.minFret === 2 && p.notes[0].fret === 3);
  assert.ok(pos, 'box at frets 2-5 starting on G (the near-identical F# box is merged into it)');
  assert.equal(pos.startInterval, 0);
  assert.deepEqual(byString(pos.notes, 0), [3, 5]);
  assert.deepEqual(byString(pos.notes, 5), [2, 3, 5]);
  assert.ok(pos.notes.every((n) => n.finger >= 1 && n.finger <= 4));
});

test('three notes per string pattern has exactly three notes on each string', () => {
  const positions = scalePositions(0, [0, 2, 4, 5, 7, 9, 11], std, { system: 'nps' });
  assert.equal(positions.length, 7);
  for (const p of positions) {
    for (let s = 0; s < 6; s++) assert.equal(p.notes.filter((n) => n.string === s).length, 3);
  }
});

test('per-string fingering rules', () => {
  assert.deepEqual(fingerStringGroup([5, 7, 9]), [1, 2, 4]);
  assert.deepEqual(fingerStringGroup([5, 7, 8]), [1, 3, 4]);
  assert.deepEqual(fingerStringGroup([5, 6, 8]), [1, 2, 4]);
  assert.deepEqual(fingerStringGroup([5, 6, 7]), [1, 2, 3]);
});

test('finger assignment: open C, F barre, A-shape', () => {
  assert.deepEqual(assignFingers([-1, 3, 2, 0, 1, 0]).fingers, [null, 3, 2, 0, 1, 0]);
  const f = assignFingers([1, 3, 3, 2, 1, 1]);
  assert.deepEqual(f.fingers, [1, 3, 4, 2, 1, 1]);
  assert.deepEqual(f.barres[0], { finger: 1, fret: 1, from: 0, to: 5 });
  const bb = assignFingers([-1, 1, 3, 3, 3, 1]);
  assert.ok(bb, 'A-shape barre is playable');
  assert.equal(assignFingers([-1, 3, 0, 2, 1, 4]) !== null, true);
});

test('no shape needs a little-finger barre', () => {
  assert.equal(assignFingers([13, 13, 12, 10, 11, 10]), null, 'Bb 13-13-12-10-11-10 is not playable');
  for (const q of [[0, 4, 7], [0, 4, 7, 10], [0, 3, 7, 10], [0, 4, 7, 11]]) {
    for (let root = 0; root < 12; root++) {
      for (const sh of findChordShapes(root, q, std, { maxFret: 15, limit: 500 })) {
        const pinkyBarre = sh.barres.some((b) => b.finger === 4);
        assert.equal(pinkyBarre, false, `${root} ${q} ${sh.frets}`);
      }
    }
  }
});

test('chord shape finder returns the shapes guitarists expect', () => {
  const shapes = findChordShapes(0, [0, 4, 7], std, { maxFret: 12, limit: 200 });
  const keys = shapes.map((s) => s.frets.join(','));
  assert.ok(keys.includes('-1,3,2,0,1,0'), 'open C');
  assert.ok(keys.includes('-1,3,5,5,5,3'), 'A-shape barre C');
  assert.ok(keys.includes('8,10,10,9,8,8'), 'E-shape barre C');
  assert.ok(keys.indexOf('-1,3,2,0,1,0') < 10, 'open C ranks near the top');
  const g = findChordShapes(7, [0, 4, 7], std, { maxFret: 12 });
  assert.ok(g.slice(0, 5).some((s) => s.frets.join(',') === '3,2,0,0,0,3' || s.frets.join(',') === '3,2,0,0,3,3'), 'open G ranks in top 5');
});

test('bass filter only returns the requested inversion', () => {
  const shapes = findChordShapes(0, [0, 4, 7], std, { bass: 4 });
  assert.ok(shapes.length > 0);
  for (const s of shapes) assert.equal(s.bassInterval, 4);
});

test('voicing classification', () => {
  assert.equal(classifyVoicing([60, 67, 71, 76]), 'Drop 2');
  assert.equal(classifyVoicing([60, 64, 67, 71]), 'Close');
  assert.equal(classifyVoicing([48, 59, 64, 67]), 'Drop 3');
});

test('reverse lookup names slash chords and scales', () => {
  const chords = identifyChords([4, 7, 0], 4, CHORD_LIBRARY);
  assert.equal(chords[0].name, 'C/E');
  const am7 = identifyChords([9, 0, 4, 7], 9, CHORD_LIBRARY);
  assert.equal(am7[0].name, 'Am7');
  const scales = identifyScales([0, 2, 4, 5, 7, 9, 11], SCALE_LIBRARY);
  assert.ok(scales.some((s) => s.root === 0 && s.scale.name.startsWith('Major')));
});

test('spelling and interval labels', () => {
  assert.equal(spellNote('Eb', 3, 'b3'), 'Gb');
  assert.equal(spellNote('F#', 4, '3'), 'A#');
  assert.equal(spellNote('F', 10, 'b7'), 'Eb');
  assert.deepEqual(Object.values(intervalLabels([0, 2, 3, 5, 7, 9, 10])), ['1', '2', 'b3', '4', '5', '6', 'b7']);
  assert.equal(intervalLabels([0, 3, 6, 9], 'chord')[9], 'bb7');
  assert.equal(intervalLabels([0, 4, 7, 10, 2], 'chord')[2], '9');
});

test('database catalogue merges into the library', () => {
  const lib = buildLibrary({
    scales: [{ id: 25, name: 'Aeloian', intervals: [0, 2, 3, 5, 7, 8, 10] }],
    arpeggios: [{ id: 2, name: 'Major 7', intervals: [0, 4, 7, 11] }],
    chords: [{ name: 'Major 7', intervals: [0, 4, 7, 11], voicings: [{ id: 1, system: 'V2', range: 'e - A', tones: [] }] }],
  });
  const aeolian = lib.scales.find((s) => s.key.startsWith('aeolian'));
  assert.equal(aeolian.source, 'db');
  assert.equal(aeolian.id, 25);
  assert.equal(lib.chords.find((c) => c.symbol === 'maj7').voicings.length, 1);
  assert.equal(lib.arpeggios[0].symbol, 'maj7');
});

test('V-System template yields every inversion at a playable place', () => {
  // Cmaj7 drop 2 on D-G-B-e: C (D) G (G) B (B) E (e)
  const template = {
    system: 'V2', range: 'e - d',
    tones: [
      { string: 'dString', interval: 0 }, { string: 'gString', interval: 7 },
      { string: 'bString', interval: 11 }, { string: 'eString', interval: 4 },
    ],
  };
  const shapes = voicingTemplateShapes(0, [0, 4, 7, 11], template, std);
  assert.equal(shapes.length, 4);
  for (const s of shapes) {
    const used = s.frets.filter((f) => f >= 0);
    assert.ok(Math.max(...used) - Math.min(...used) <= 5);
    assert.equal(s.voicing, 'Drop 2');
  }
});

test('all tunings produce positions', () => {
  for (const t of TUNINGS) {
    assert.ok(scalePositions(4, [0, 2, 4, 5, 7, 9, 11], t).length >= 5, t.id);
    assert.ok(findChordShapes(4, [0, 3, 7], t).length > 3, t.id);
  }
});

test('V-System inversions keep the voicing structure (close stays close)', () => {
  // Cmaj7 V1 (close) on D-G-B-e, stored root-first like the database
  const template = {
    system: 'V1', range: 'e - d',
    tones: [
      { string: 'dString', interval: 0 }, { string: 'gString', interval: 4 },
      { string: 'bString', interval: 7 }, { string: 'eString', interval: 11 },
    ],
  };
  const shapes = voicingTemplateShapes(0, [0, 4, 7, 11], template, std);
  assert.deepEqual(shapes.map((s) => s.frets.join(',')), ['-1,-1,10,9,8,7', '-1,-1,14,12,12,8', '-1,-1,5,4,1,0', '-1,-1,9,5,5,3']);
  assert.ok(shapes.every((s) => s.voicing === 'Close'));
});

test('chord types without database voicings get V-System voicings derived from Major 7', () => {
  const lib = buildLibrary({
    chords: [{
      name: 'Major 7', intervals: [0, 4, 7, 11],
      voicings: [{ id: 1, system: 'V2', range: 'e - A', tones: [
        { string: 'AString', interval: 0 }, { string: 'dString', interval: 7 },
        { string: 'gString', interval: 11 }, { string: 'bString', interval: 4 }] }],
    }],
  });
  const maj7s11 = lib.chords.find((c) => c.symbol === 'maj7#11');
  assert.equal(maj7s11.vsDerived, true);
  assert.deepEqual(maj7s11.vsOmitted, [7]);
  // 1-3-#11-7 replaces 1-3-5-7 voice for voice
  assert.deepEqual(maj7s11.voicings[0].tones.map((t) => t.interval), [0, 6, 11, 4]);
  const shapes = voicingTemplateShapes(0, maj7s11.intervals, maj7s11.voicings[0], std);
  assert.equal(shapes.length, 4);
  assert.ok(lib.chords.find((c) => c.symbol === 'm6').vsDerived);
  assert.equal(lib.chords.find((c) => c.symbol === '5').voicings.length, 0, 'power chords have no V-System');
});

// ---- Chord symbol search (#1) ------------------------------------------------
test('parseChordQuery reads root and quality', () => {
  const lib = buildLibrary(null);
  const parse = (q) => parseChordQuery(q, lib.chords);
  const em7 = parse('Em7');
  assert.equal(em7.root, 4);
  assert.deepEqual(em7.chords.map((c) => c.name), ['Minor 7']);
  assert.equal(parse('em7').root, 4, 'case-insensitive root');
  assert.equal(parse('EM7').chords[0].name, 'Major 7', 'capital M means major');
  const f = parse('F#m7b5');
  assert.equal(f.root, 6);
  assert.equal(f.chords[0].name, 'Minor 7b5');
  assert.equal(parse('Bbmaj7').root, 10);
  assert.equal(parse('Eb7').chords[0].name, 'Dominant 7');
  assert.equal(parse('Ab5').chords[0].name, 'Power chord');
  assert.equal(parse('C-7').chords[0].name, 'Minor 7');
});

test('"maj7#11" and "Major 7#11" are the same chord, with or without root', () => {
  const lib = buildLibrary(null);
  const a = parseChordQuery('Maj7#11', lib.chords);
  const b = parseChordQuery('major 7#11', lib.chords);
  assert.equal(a.root, null);
  assert.equal(a.chords[0].key, b.chords[0].key);
  assert.equal(parseChordQuery('Dmaj7#11', lib.chords).root, 2);
  assert.equal(parseChordQuery('Add9', lib.chords).chords[0].name, 'Add 9', 'A + "dd9" falls back to the whole word');
  assert.equal(parseChordQuery('dim', lib.chords).root, null);
});

test('modes are listed by degree inside their parent scale', () => {
  // A database with unusable entries (no root, wrong names) must not change the result
  const lib = buildLibrary({ scales: [
    { id: 1, name: 'Altered', intervals: [0, 1, 3, 4, 6, 8, 10] },
    { id: 2, name: 'Lydian Dominant', intervals: [1, 2, 4, 5, 7, 9, 11] },
  ] });
  const names = (group) => lib.scales.filter((s) => s.group === group).map((s) => s.name);
  assert.deepEqual(names('Melodic minor family'), ['Melodic Minor', 'Dorian b2', 'Lydian Augmented', 'Lydian Dominant', 'Mixolydian b6', 'Locrian #2', 'Altered']);
  assert.deepEqual(names('Modes of Major'), ['Major (Ionian)', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian (Natural Minor)', 'Locrian']);
  assert.deepEqual(names('Harmonic minor family'), ['Harmonic Minor', 'Locrian #6', 'Major Augmented', 'Dorian #4', 'Phrygian Dominant', 'Lydian #2', 'Altered Dominant bb7']);
  assert.deepEqual(names('Harmonic major family'), ['Harmonic Major', 'Dorian b5', 'Phrygian b4', 'Lydian b3', 'Mixolydian b2', 'Lydian Augmented #2', 'Locrian bb7']);
  assert.deepEqual(names('Bebop').filter((n) => /harmonic/i.test(n)), ['Bebop Harmonic Minor']);
  assert.equal(lib.scales.find((s) => s.name === 'Altered').id, 1, 'database ids are kept');
  assert.ok(lib.scales.every((s) => s.intervals.includes(0)), 'every scale contains its root');
  assert.equal(lib.scales.find((s) => s.name === 'Major Pentatonic').group, 'Pentatonic & Blues');
  const dorianB2 = lib.scales.find((s) => s.name === 'Dorian b2');
  assert.deepEqual(dorianB2.intervals, [0, 1, 3, 5, 7, 9, 10]);
});

test('V-System exists only for chords that can be played with four voices', () => {
  const voicing = (id, tones) => ({ id, system: 'V1', range: 'e - d', tones: tones.map((interval, i) => ({ string: i + 1, interval })) });
  const lib = buildLibrary({ chords: [
    { name: 'Major 7', intervals: [0, 4, 7, 11], voicings: [voicing(1, [0, 7, 11, 4])] },
    { name: 'Major', intervals: [0, 4, 7], voicings: [voicing(2, [0, 4, 7])] },
  ] });
  const by = (symbol) => lib.chords.find((c) => c.symbol === symbol);
  assert.ok(by('maj7').voicings.length, 'four-note chord keeps its voicings');
  assert.ok(by('7').voicings.length && by('7').vsDerived, 'other four-note chords are derived');
  assert.equal(by('').voicings.length, 0, 'triads have no V-System');
  assert.equal(by('5').voicings.length, 0, 'power chords have no V-System');
  assert.ok(by('9').vsDerived && by('9').vsOmitted.length > 0, 'five-note chords get a four-voice version');
  assert.ok(lib.chords.every((c) => c.intervals.length >= 4 || c.voicings.length === 0));
});

test('altered and extended dominants are found by symbol', () => {
  const lib = buildLibrary(null);
  const find = (q) => parseChordQuery(q, lib.chords);
  const g = find('G7#11');
  assert.equal(g.root, 7);
  assert.deepEqual(g.chords.map((c) => c.intervals), [[0, 4, 6, 7, 10]]);
  assert.equal(find('G7(#11)').chords.length, 1);
  assert.equal(find('G7+11').chords.length, 1);
  for (const q of ['G9#11', 'G13#11', 'G7b13', 'G9sus4', 'Gmaj13', 'Gm13', 'Gm(maj9)']) assert.equal(find(q)?.chords.length, 1, q);
  assert.ok(findChordShapes(7, [0, 4, 6, 7, 10], std, { maxFret: 12 }).length > 0, 'G7#11 has shapes');
  const lydDom = chordScaleFor([0, 2, 4, 6, 7, 9, 10], lib.chords);
  assert.equal(lydDom.chords[0].symbol, '7#11', 'Lydian Dominant lists 7#11 first');
});

test('parseChordQuery ignores bare roots and plain words', () => {
  const lib = buildLibrary(null);
  assert.equal(parseChordQuery('E', lib.chords), null);
  assert.equal(parseChordQuery('Bb', lib.chords), null);
  assert.equal(parseChordQuery('dorian', lib.chords), null);
});

test('Em7 suggests Dorian, Phrygian and Aeolian on E', () => {
  const lib = buildLibrary(null);
  const names = scalesForChord(4, [0, 3, 7, 10], lib.scales).map((x) => x.scale.name);
  for (const n of ['Dorian', 'Phrygian', 'Aeolian (Natural Minor)']) assert.ok(names.includes(n), n);
  assert.ok(!names.includes('Lydian'));
});

// ---- Bebop / Messiaen (#2, #4) -----------------------------------------------
test('bebop scales are grouped and have eight notes', () => {
  const lib = buildLibrary(null);
  const bebop = lib.scales.filter((s) => s.group === 'Bebop');
  assert.equal(bebop.length, 5);
  assert.ok(bebop.every((s) => s.intervals.length === 8));
  assert.ok(bebop.some((s) => s.name === 'Bebop Dominant'));
});

test('8-note scales produce complete positions in box and NPS systems', () => {
  const lib = buildLibrary(null);
  const dom = lib.scales.find((s) => s.name === 'Bebop Dominant');
  for (const system of ['box', 'nps']) {
    const positions = scalePositions(7, dom.intervals, std, { system });
    assert.equal(positions.length, system === 'nps' ? 8 : 5, system);
    for (const p of positions) {
      assert.ok(p.notes.length >= 8, `${system} position ${p.index} has all degrees`);
      assert.ok(p.notes.every((n) => n.finger >= 0 && n.finger <= 4));
    }
  }
  assert.ok(neckNotes(7, dom.intervals, std, 15).length > 40);
});

test('Messiaen modes 1-7 exist exactly once, in the Symmetric group', () => {
  const lib = buildLibrary(null);
  for (const m of MESSIAEN_MODES) {
    const hits = lib.scales.filter((s) => s.intervals.join() === m.intervals.join());
    assert.equal(hits.length, 1, `mode ${m.mode} appears once`);
    assert.equal(hits[0].group, 'Symmetric');
  }
  assert.match(lib.scales.find((s) => s.name === 'Whole Tone').alias, /messiaen mode 1/);
  const catalog = { scales: [{ name: 'Diminished', intervals: [0, 1, 3, 4, 6, 7, 9, 10] }] };
  const withDb = buildLibrary(catalog);
  assert.equal(withDb.scales.filter((s) => s.intervals.length === 8 && s.intervals.join() === '0,1,3,4,6,7,9,10').length, 1, 'no duplicate of a database Diminished');
  const sparse = buildLibrary(null).scales.filter((s) => s.group === 'Symmetric');
  assert.equal(sparse.length, 7);
});

test('Messiaen modes are limited-transposition (symmetric)', () => {
  for (const m of MESSIAEN_MODES) {
    const set = new Set(m.intervals);
    const transpositions = new Set();
    for (let t = 0; t < 12; t++) transpositions.add([...set].map((iv) => (iv + t) % 12).sort((a, b) => a - b).join());
    assert.ok(transpositions.size < 12, `mode ${m.mode}`);
  }
});

// ---- Scale -> chords (#7) ----------------------------------------------------
test('C major yields the diatonic seventh chords', () => {
  const lib = buildLibrary(null);
  const { diatonic } = chordsForScale(0, [0, 2, 4, 5, 7, 9, 11], lib.chords);
  assert.deepEqual(diatonic.map((d) => d.seventh.symbol), ['maj7', 'm7', 'm7', 'maj7', '7', 'm7', 'm7b5']);
  assert.deepEqual(diatonic.map((d) => d.root), [0, 2, 4, 5, 7, 9, 11]);
  assert.equal(diatonic[6].triad.symbol, 'dim');
});

test('scales outside the chord-scale table fall back to chords on the root built from scale notes', () => {
  const lib = buildLibrary(null);
  const mode5 = MESSIAEN_MODES.find((m) => m.mode === 5).intervals;
  const { diatonic, chordScale, others } = chordsForScale(9, mode5, lib.chords);
  assert.equal(diatonic.length, 0);
  assert.equal(chordScale, null);
  const scalePcs = mode5.map((i) => (i + 9) % 12);
  for (const o of others) {
    assert.equal(o.root, 9, 'only chords on the scale root');
    assert.ok(o.chord.intervals.every((iv) => scalePcs.includes((iv + o.root) % 12)));
  }
});

// ---- Chord-scale theory after Nettles/Graf (2026-10-20 #1) --------------------
test('every chord-scale chord exists in the library and is built from scale notes', () => {
  const lib = buildLibrary(null);
  for (const entry of CHORD_SCALES) {
    const resolved = chordScaleFor(entry.intervals, lib.chords);
    assert.equal(resolved.chords.length, entry.chords.length, `${entry.name}: all symbols resolve`);
    for (const chord of resolved.chords) {
      assert.ok(chord.intervals.every((iv) => entry.intervals.includes(iv)), `${entry.name}: ${chord.symbol || 'major'} fits`);
    }
  }
});

test('chord-scale recommendations replace the full subset list', () => {
  const lib = buildLibrary(null);
  const ionian = chordsForScale(0, [0, 2, 4, 5, 7, 9, 11], lib.chords);
  assert.equal(ionian.others.length, 0, 'no "all fitting chords" list');
  assert.deepEqual(ionian.chordScale.chords.map((c) => c.symbol), ['maj7', '6', 'maj9', 'maj13', '6/9', 'add9', '']);
  assert.deepEqual(ionian.chordScale.avoid, ['11']);
  const dorian = chordsForScale(2, [0, 2, 3, 5, 7, 9, 10], lib.chords).chordScale;
  assert.equal(dorian.chords[0].symbol, 'm7');
  assert.ok(!dorian.chords.some((c) => c.symbol === 'maj7'));
  const lydian = chordsForScale(5, [0, 2, 4, 6, 7, 9, 11], lib.chords).chordScale;
  assert.equal(lydian.chords[0].symbol, 'maj7#11');
});

test('chord -> scales follows the same table', () => {
  const lib = buildLibrary(null);
  const names = (intervals) => scalesForChord(0, intervals, lib.scales).map((x) => x.scale.name);
  assert.deepEqual(names([0, 4, 7, 11]).slice(0, 2), ['Major (Ionian)', 'Lydian']);
  assert.equal(names([0, 3, 7, 10])[0], 'Dorian');
  assert.equal(names([0, 4, 7, 10])[0], 'Mixolydian');
  assert.equal(names([0, 3, 6, 10])[0], 'Locrian');
  assert.ok(!names([0, 4, 7, 11]).includes('Mixolydian'), 'maj7 never suggests Mixolydian');
  assert.ok(!names([0, 4, 7, 11]).includes('Bebop Dominant'));
  const lydianDominant = { name: 'Lydian Dominant', intervals: [0, 2, 4, 6, 7, 9, 10] };
  const withDb = buildLibrary({ scales: [lydianDominant] });
  assert.ok(scalesForChord(0, [0, 4, 7, 10], withDb.scales).some((x) => x.scale.name === 'Lydian Dominant'));
});

test('chords outside the table still get scales by pitch content', () => {
  const lib = buildLibrary(null);
  assert.ok(scalesForChord(0, [0, 4, 7], lib.scales).length > 0);
  const odd = scalesForChord(0, [0, 1, 6], lib.scales);
  for (const x of odd) assert.ok([0, 1, 6].every((iv) => x.scale.intervals.includes(iv)));
});

// ---- Position numbering by neck place (2026-10-20 #2) ------------------------
test('position 1 is always the lowest position on the neck, in every key', () => {
  for (let root = 0; root < 12; root++) {
    for (const intervals of [[0, 3, 5, 7, 10], [0, 2, 4, 5, 7, 9, 11]]) {
      for (const system of intervals.length >= 6 ? ['box', 'nps'] : ['box']) {
        const positions = scalePositions(root, intervals, std, { system });
        positions.forEach((p, i) => assert.equal(p.index, i + 1));
        for (let i = 1; i < positions.length; i++) {
          assert.ok(positions[i].minFret >= positions[i - 1].minFret, `root ${root} ${system}: ascending`);
        }
        assert.ok(positions[0].minFret <= 3, `root ${root} ${system}: position 1 sits near the nut (fr ${positions[0].minFret})`);
      }
    }
  }
});

test('B major: position 1 no longer starts at the 7th fret', () => {
  const positions = scalePositions(11, [0, 2, 4, 5, 7, 9, 11], std, { system: 'box' });
  assert.ok(positions[0].minFret <= 2);
  assert.ok(positions[positions.length - 1].minFret >= 7);
});

// ---- Shared links (2026-10-20 #3) -----------------------------------------------
test('shapeFromFrets rebuilds a voicing from a link', () => {
  const shape = shapeFromFrets([-1, 3, 5, 5, 5, 3], std, 0, [0, 4, 7]);
  assert.equal(shape.minFret, 3);
  assert.equal(shape.inversion, 'Root position');
  assert.ok(shape.barres.length >= 1, 'A-shape barre');
  assert.equal(shapeFromFrets([-1, -1, -1, -1, -1, -1], std, 0, [0, 4, 7]), null);
  assert.equal(shapeFromFrets([0, 2, 2], std, 0, [0, 4, 7]), null, 'wrong string count');
});

// ---- PDF sheets (2026-10-20 #4) ---------------------------------------------------
test('PDF writer produces a valid A4 file with a correct xref table', async () => {
  const { PdfWriter } = await import('./pdf.js');
  const pdf = new PdfWriter({ title: 'C♯ Test (1)' });
  pdf.text(42, 60, 'F♯m7♭5 · ×', { size: 12, bold: true });
  pdf.circle(100, 100, 5, { fill: 0, stroke: 0 });
  pdf.line(10, 10, 100, 10);
  pdf.addPage();
  pdf.text(42, 60, 'Page 2');
  const bytes = pdf.output();
  const text = Array.from(bytes, (b) => String.fromCharCode(b)).join('');
  assert.ok(text.startsWith('%PDF-1.4'));
  assert.ok(text.trimEnd().endsWith('%%EOF'));
  assert.match(text, /\/MediaBox \[0 0 595\.28 841\.89\]/);
  assert.match(text, /\/Count 2/);
  assert.match(text, /\(F\) Tj/, 'accidentals are drawn, not sent as text');
  const xref = parseInt(/startxref\n(\d+)/.exec(text)[1], 10);
  assert.equal(text.slice(xref, xref + 4), 'xref');
  const offsets = [...text.slice(xref).matchAll(/^(\d{10}) 00000 n $/gm)].map((m) => parseInt(m[1], 10));
  offsets.forEach((o, i) => assert.equal(text.slice(o, o + `${i + 1} 0 obj`.length), `${i + 1} 0 obj`));
  for (const m of text.matchAll(/<< \/Length (\d+) >>\nstream\n/g)) {
    const start = m.index + m[0].length;
    assert.equal(text.slice(start + parseInt(m[1], 10), start + parseInt(m[1], 10) + 10), '\nendstream');
  }
});

test('chord grids: horizontal by default, vertical boxes for songs', async () => {
  const { chordGrid, chordWindow, fretGrid } = await import('./grid.js');
  assert.deepEqual(chordWindow([-1, 3, 2, 0, 1, 0]), { from: 1, to: 5 }, 'open C from the nut');
  assert.deepEqual(chordWindow([8, 10, 10, 9, 8, 8]), { from: 8, to: 12 });
  assert.deepEqual(chordWindow([1, 8, -1, -1, -1, -1], 7), { from: 1, to: 8 }, 'wide voicing widens the grid');
  const shape = { frets: [3, -1, -1, -1, -1, 5], barres: [] };
  const opts = { labels: ['1', '', '', '', '', '5'], roots: [0] };
  const dotsOf = (grid) => {
    const dots = grid.items.filter((i) => i.type === 'circle');
    return { low: dots.find((d) => d.fill === 'ink'), high: dots.find((d) => d.fill === 'paper') };
  };
  const flat = chordGrid(shape, 6, opts);
  assert.ok(dotsOf(flat).low.cy > dotsOf(flat).high.cy, 'horizontal: low string at the bottom');
  assert.ok(flat.width > flat.height);
  const box = chordGrid(shape, 6, { ...opts, vertical: true });
  assert.ok(dotsOf(box).low.cx < dotsOf(box).high.cx, 'vertical: low string on the left');
  assert.ok(dotsOf(box).low.cy < dotsOf(box).high.cy, 'vertical: higher frets further down');
  assert.ok(box.height > box.width, 'portrait box');
  assert.ok(box.items.some((i) => i.type === 'line' && i.width > 1 && i.y1 === i.y2), 'horizontal nut on top');
  const moved = chordGrid({ frets: [8, 10, 10, 9, 8, 8], barres: [{ fret: 8, from: 0, to: 5 }] }, 6, { vertical: true });
  assert.ok(moved.items.some((i) => i.type === 'text' && i.text === '8' && i.align === 'right'), 'start fret beside the box');
  const neck = fretGrid({ strings: 6, from: 1, to: 15, fretNumbers: 'neck' });
  assert.ok(neck.width > neck.height, 'whole neck is horizontal');
});

test('sheets build for scales, chords and songs', async () => {
  const { scaleSheet, chordSheet, songSheet, pdfFileName } = await import('./sheet.js');
  const positions = scalePositions(9, [0, 2, 3, 5, 7, 9, 10], std, { system: 'box' });
  const scale = scaleSheet({
    title: 'A Dorian', lines: ['Notes A B C D E F♯ G'], strings: 6, link: 'https://fretboard.schoensgibl.com/?mode=scale',
    neck: { frets: 15, notes: neckNotes(9, [0, 2, 3, 5, 7, 9, 10], std, 15).map((n) => ({ ...n, text: '1', filled: n.interval === 0 })) },
    positions: positions.map((p) => ({ label: `Position ${p.index}`, from: Math.max(1, p.minFret), to: Math.max(1, p.minFret) + 5, notes: p.notes.map((n) => ({ ...n, text: String(n.finger) })) })),
  });
  assert.equal(scale.pages.length, 1, 'scale sheet fits one A4 page');
  const chords = findChordShapes(0, [0, 4, 7], std, { limit: 36 }).map((sh) => ({ name: 'C', meta: sh.inversion, frets: sh.frets, barres: sh.barres, labels: [], roots: [] }));
  assert.equal(chordSheet({ title: 'C', lines: [], strings: 6, chords }).pages.length, 1, '36 shapes fit one page');
  assert.ok(chordSheet({ title: 'C', lines: [], strings: 6, chords: [...chords, ...chords, ...chords] }).pages.length >= 2, 'very long lists continue on the next page');
  const song = songSheet({ title: 'Song XY', note: 'Swing feel', lines: [], strings: 6, items: [{ section: 'Verse' }, ...chords.slice(0, 5), { section: 'Chorus' }, ...chords.slice(5, 9)] });
  assert.equal(song.pages.length, 1);
  assert.equal(pdfFileName('F♯ Dorian'), 'fsharp-dorian.pdf');
});

// ---- Songs & exercises (2026-10-20 #5) --------------------------------------------
test('songs round-trip through the share link', async () => {
  const { encodeSong, decodeSong, sameSong, moveItem, emptySong } = await import('./songs.js');
  const song = { ...emptySong('Autumn Leaves'), note: 'Swing; two bars each', items: [
    { section: 'A' }, { root: 9, key: 'minor-7', frets: [5, -1, 5, 5, 5, -1] }, { root: 2, key: 'dominant-7', frets: [-1, 5, 4, 5, 3, -1] },
    { section: 'B #2' }, { root: 7, key: 'major-7', frets: [3, -1, 4, 4, 3, -1] }, { root: 10, key: 'major-7', frets: [6, -1, 7, 7, 6, -1] },
  ] };
  const params = encodeSong(song);
  assert.equal(params.c, '#A;A.minor-7.5-x-5-5-5-x;D.dominant-7.x-5-4-5-3-x;#B  2;G.major-7.3-x-4-4-3-x;Bb.major-7.6-x-7-7-6-x');
  const url = new URLSearchParams(params);
  const back = decodeSong((k) => url.get(k));
  assert.equal(back.title, 'Autumn Leaves');
  assert.equal(back.note, 'Swing; two bars each');
  assert.deepEqual(back.items.filter((it) => it.frets).map((it) => it.root), [9, 2, 7, 10]);
  assert.ok(sameSong(back, decodeSong((k) => url.get(k))), 'a saved copy is recognised');
  assert.ok(!sameSong(back, { ...back, title: 'Other' }));
  assert.equal(decodeSong(() => null), null, 'no song in the link');
  const junk = decodeSong((k) => ({ t: 'X', c: 'H.major.1-2-3;C.major.1;C.major.x-3-2-0-1-0' }[k] ?? null));
  assert.equal(junk.items.length, 1, 'invalid items are dropped');
  assert.deepEqual(moveItem([1, 2, 3], 0, 1), [2, 1, 3]);
  assert.deepEqual(moveItem([1, 2, 3], 0, -1), [1, 2, 3]);
});

// ---- Distinct positions (2026-10-20 #9) ---------------------------------------------
test('C Ionian box positions are five distinct CAGED-like boxes (no near-duplicates)', () => {
  const positions = scalePositions(0, [0, 2, 4, 5, 7, 9, 11], std, { system: 'box' });
  assert.equal(positions.length, 5);
  assert.deepEqual(positions.map((p) => [p.minFret, p.maxFret]), [[0, 3], [2, 6], [4, 8], [7, 10], [9, 13]]);
  assert.ok(positions.some((p) => p.minFret === 7 && p.startInterval === 0), 'of the B/C pair the box on the root stays');
});

test('no two positions are near-duplicates, in any key, scale or system', () => {
  const lib = buildLibrary(null);
  for (const scale of lib.scales) {
    for (const system of scale.intervals.length >= 6 ? ['box', 'nps'] : ['box']) {
      for (let root = 0; root < 12; root++) {
        const positions = scalePositions(root, scale.intervals, std, { system });
        assert.ok(positions.length >= 3, `${scale.name} ${system} root ${root}: ${positions.length} positions`);
        for (let i = 0; i < positions.length; i++) {
          for (let j = i + 1; j < positions.length; j++) {
            assert.ok(positionOverlap(positions[i], positions[j]) < 0.85, `${scale.name} ${system} root ${root}: ${i + 1}~${j + 1}`);
          }
        }
      }
    }
  }
});

test('three notes per string keeps one pattern per scale degree', () => {
  assert.equal(scalePositions(0, [0, 2, 4, 5, 7, 9, 11], std, { system: 'nps' }).length, 7);
  assert.equal(scalePositions(9, [0, 2, 3, 5, 7, 9, 10], std, { system: 'nps' }).length, 7);
});

test('other instruments: ukulele (re-entrant), banjo and Loog Guitar tunings exist', () => {
  assert.deepEqual(getTuning('ukulele').midi, [67, 60, 64, 69]);
  assert.deepEqual(getTuning('loog').midi, [55, 59, 64]);
  assert.equal(getTuning('banjo').midi.length, 4);
});

test('ukulele chords take the bass from the lowest pitch, not the lowest string', () => {
  const uke = getTuning('ukulele');
  // G C E A with frets 0 0 0 3 = G C E C: lowest note is C, so C major is in root position
  const shape = shapeFromFrets([0, 0, 0, 3], uke, 0, [0, 4, 7]);
  assert.equal(shape.bassInterval, 0);
  const rootBass = findChordShapes(0, [0, 4, 7], uke, { bass: 0 });
  assert.ok(rootBass.length > 0);
  assert.ok(rootBass.every((s) => s.bassInterval === 0));
});

test('Loog Guitar: three strings, triads are playable (open G B E is E minor, first inversion)', () => {
  const loog = getTuning('loog');
  const shapes = findChordShapes(4, [0, 3, 7], loog);
  assert.ok(shapes.some((s) => s.frets.join(',') === '0,0,0'));
});
