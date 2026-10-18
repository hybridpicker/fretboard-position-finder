// Run with: node --test static/studio/js/
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  TUNINGS, getTuning, scalePositions, assignFingers, findChordShapes, classifyVoicing,
  identifyChords, identifyScales, spellNote, intervalLabels, buildLibrary, voicingTemplateShapes,
  CHORD_LIBRARY, SCALE_LIBRARY, fingerStringGroup,
} from './theory.js';

const std = getTuning('standard');
const byString = (notes, s) => notes.filter((n) => n.string === s).map((n) => n.fret);

test('A minor pentatonic box 1 is the classic shape with fingering', () => {
  const positions = scalePositions(9, [0, 3, 5, 7, 10], std, { system: 'box' });
  assert.equal(positions.length, 5);
  const box1 = positions[0];
  assert.equal(box1.startInterval, 0, 'position 1 starts on the root');
  assert.deepEqual([0, 1, 2, 3, 4, 5].map((s) => byString(box1.notes, s)), [[5, 8], [5, 7], [5, 7], [5, 7], [5, 8], [5, 8]]);
  assert.deepEqual(box1.notes.filter((n) => n.string === 0).map((n) => n.finger), [1, 4]);
});

test('A minor pentatonic box 2 uses the A string stretch, not the pinky on low E', () => {
  const positions = scalePositions(9, [0, 3, 5, 7, 10], std, { system: 'box' });
  const box2 = positions.find((p) => p.startInterval === 3);
  assert.deepEqual([0, 1, 2, 3, 4, 5].map((s) => byString(box2.notes, s)), [[8, 10], [7, 10], [7, 10], [7, 9], [8, 10], [8, 10]]);
});

test('G major second position box', () => {
  const positions = scalePositions(7, [0, 2, 4, 5, 7, 9, 11], std, { system: 'box' });
  const pos = positions.find((p) => p.minFret === 2 && p.notes[0].fret === 2);
  assert.ok(pos, 'position starting on F# at fret 2 exists');
  assert.deepEqual(byString(pos.notes, 0), [2, 3, 5]);
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
