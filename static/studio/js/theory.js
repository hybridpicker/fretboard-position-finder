// Music theory + fingering engine for Guitar Positions Studio.
// Pure functions only (no DOM), so it runs in the browser and under `node --test`.

export const NOTE_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
export const NOTE_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
// Default key names offered in the root picker
export const ROOT_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];

const LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B'];
const LETTER_PC = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
const MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11];

export const mod12 = (n) => ((n % 12) + 12) % 12;

export function pretty(name) {
  return String(name).replace(/bb/g, '𝄫').replace(/##/g, '𝄪').replace(/#/g, '♯').replace(/(?<=[A-G1-9])b/g, '♭').replace(/^b(?=\d)/, '♭');
}

// ---------------------------------------------------------------------------
// Tunings (MIDI numbers, lowest string first). `numbers` are classic string
// numbers (1 = high e) used to map database voicings onto any instrument.
// ---------------------------------------------------------------------------
export const TUNINGS = [
  { id: 'standard', name: 'Standard (E A D G B E)', midi: [40, 45, 50, 55, 59, 64], numbers: [6, 5, 4, 3, 2, 1] },
  { id: 'eb', name: 'Half step down (E♭)', midi: [39, 44, 49, 54, 58, 63], numbers: [6, 5, 4, 3, 2, 1] },
  { id: 'dropd', name: 'Drop D (D A D G B E)', midi: [38, 45, 50, 55, 59, 64], numbers: [6, 5, 4, 3, 2, 1] },
  { id: 'dadgad', name: 'DADGAD', midi: [38, 45, 50, 55, 57, 62], numbers: [6, 5, 4, 3, 2, 1] },
  { id: 'openg', name: 'Open G (D G D G B D)', midi: [38, 43, 50, 55, 59, 62], numbers: [6, 5, 4, 3, 2, 1] },
  { id: 'opend', name: 'Open D (D A D F♯ A D)', midi: [38, 45, 50, 54, 57, 62], numbers: [6, 5, 4, 3, 2, 1] },
  { id: 'seven', name: '7-string (B E A D G B E)', midi: [35, 40, 45, 50, 55, 59, 64], numbers: [7, 6, 5, 4, 3, 2, 1] },
  { id: 'eight', name: '8-string (B E A D G B E A)', midi: [35, 40, 45, 50, 55, 59, 64, 69], numbers: [7, 6, 5, 4, 3, 2, 1, 0] },
];

// Database string names -> classic string numbers
export const DB_STRING_NUMBERS = {
  highAString: 0, eString: 1, bString: 2, gString: 3, dString: 4, AString: 5, ELowString: 6, lowBString: 7,
};

export function getTuning(id) {
  return TUNINGS.find((t) => t.id === id) || TUNINGS[0];
}

export function midiName(midi, preferFlat = false) {
  return (preferFlat ? NOTE_FLAT : NOTE_SHARP)[mod12(midi)];
}

export function midiToFreq(midi) {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

// ---------------------------------------------------------------------------
// Built-in formula library. Database entries are merged on top of it, so the
// app keeps working (and gains extended chords) even with a sparse database.
// ---------------------------------------------------------------------------
export const CHORD_LIBRARY = [
  { name: 'Major', symbol: '', intervals: [0, 4, 7], group: 'Triads' },
  { name: 'Minor', symbol: 'm', intervals: [0, 3, 7], group: 'Triads' },
  { name: 'Diminished', symbol: 'dim', intervals: [0, 3, 6], group: 'Triads' },
  { name: 'Augmented', symbol: 'aug', intervals: [0, 4, 8], group: 'Triads' },
  { name: 'Sus 2', symbol: 'sus2', intervals: [0, 2, 7], group: 'Triads' },
  { name: 'Sus 4', symbol: 'sus4', intervals: [0, 5, 7], group: 'Triads' },
  { name: 'Power chord', symbol: '5', intervals: [0, 7], group: 'Triads' },
  { name: 'Major 7', symbol: 'maj7', intervals: [0, 4, 7, 11], group: 'Sevenths' },
  { name: 'Dominant 7', symbol: '7', intervals: [0, 4, 7, 10], group: 'Sevenths' },
  { name: 'Minor 7', symbol: 'm7', intervals: [0, 3, 7, 10], group: 'Sevenths' },
  { name: 'Minor 7b5', symbol: 'm7b5', intervals: [0, 3, 6, 10], group: 'Sevenths' },
  { name: 'Diminished 7', symbol: 'dim7', intervals: [0, 3, 6, 9], group: 'Sevenths' },
  { name: 'Minor Major 7', symbol: 'm(maj7)', intervals: [0, 3, 7, 11], group: 'Sevenths' },
  { name: 'Dominant 7 sus4', symbol: '7sus4', intervals: [0, 5, 7, 10], group: 'Sevenths' },
  { name: 'Augmented 7', symbol: '7#5', intervals: [0, 4, 8, 10], group: 'Sevenths' },
  { name: 'Dominant 7b5', symbol: '7b5', intervals: [0, 4, 6, 10], group: 'Sevenths' },
  { name: 'Major 7#5', symbol: 'maj7#5', intervals: [0, 4, 8, 11], group: 'Sevenths' },
  { name: 'Major 6', symbol: '6', intervals: [0, 4, 7, 9], group: 'Sixths & adds' },
  { name: 'Minor 6', symbol: 'm6', intervals: [0, 3, 7, 9], group: 'Sixths & adds' },
  { name: 'Add 9', symbol: 'add9', intervals: [0, 2, 4, 7], group: 'Sixths & adds' },
  { name: 'Minor add 9', symbol: 'm(add9)', intervals: [0, 2, 3, 7], group: 'Sixths & adds' },
  { name: '6/9', symbol: '6/9', intervals: [0, 2, 4, 7, 9], group: 'Sixths & adds' },
  { name: 'Dominant 9', symbol: '9', intervals: [0, 2, 4, 7, 10], group: 'Extended' },
  { name: 'Major 9', symbol: 'maj9', intervals: [0, 2, 4, 7, 11], group: 'Extended' },
  { name: 'Minor 9', symbol: 'm9', intervals: [0, 2, 3, 7, 10], group: 'Extended' },
  { name: 'Dominant 7b9', symbol: '7b9', intervals: [0, 1, 4, 7, 10], group: 'Extended' },
  { name: 'Dominant 7#9', symbol: '7#9', intervals: [0, 3, 4, 7, 10], group: 'Extended' },
  { name: 'Major 7#11', symbol: 'maj7#11', intervals: [0, 4, 6, 7, 11], group: 'Extended' },
  { name: 'Minor 11', symbol: 'm11', intervals: [0, 2, 3, 5, 7, 10], group: 'Extended' },
  { name: 'Dominant 13', symbol: '13', intervals: [0, 2, 4, 7, 9, 10], group: 'Extended' },
];

export const SCALE_LIBRARY = [
  { name: 'Major (Ionian)', intervals: [0, 2, 4, 5, 7, 9, 11] },
  { name: 'Dorian', intervals: [0, 2, 3, 5, 7, 9, 10] },
  { name: 'Phrygian', intervals: [0, 1, 3, 5, 7, 8, 10] },
  { name: 'Lydian', intervals: [0, 2, 4, 6, 7, 9, 11] },
  { name: 'Mixolydian', intervals: [0, 2, 4, 5, 7, 9, 10] },
  { name: 'Aeolian (Natural Minor)', intervals: [0, 2, 3, 5, 7, 8, 10] },
  { name: 'Locrian', intervals: [0, 1, 3, 5, 6, 8, 10] },
  { name: 'Major Pentatonic', intervals: [0, 2, 4, 7, 9] },
  { name: 'Minor Pentatonic', intervals: [0, 3, 5, 7, 10] },
  { name: 'Blues Scale', intervals: [0, 3, 5, 6, 7, 10] },
  { name: 'Melodic Minor', intervals: [0, 2, 3, 5, 7, 9, 11] },
  { name: 'Harmonic Minor', intervals: [0, 2, 3, 5, 7, 8, 11] },
  { name: 'Whole Tone', intervals: [0, 2, 4, 6, 8, 10] },
  // Bebop scales: a heptatonic scale plus one chromatic passing tone (8 notes)
  { name: 'Bebop Dominant', intervals: [0, 2, 4, 5, 7, 9, 10, 11] },
  { name: 'Bebop Major', intervals: [0, 2, 4, 5, 7, 8, 9, 11] },
  { name: 'Bebop Dorian (Minor)', intervals: [0, 2, 3, 4, 5, 7, 9, 10] },
  { name: 'Bebop Harmonic Minor', intervals: [0, 2, 3, 5, 7, 8, 10, 11] },
  { name: 'Bebop Melodic Minor', intervals: [0, 2, 3, 5, 7, 8, 9, 11] },
];

/**
 * Messiaen's modes of limited transposition. Mode 1 is the whole-tone scale and Mode 2 the half-whole
 * diminished scale; both are matched by interval set so a database entry is never duplicated.
 */
export const MESSIAEN_MODES = [
  { mode: 1, name: 'Whole Tone', intervals: [0, 2, 4, 6, 8, 10] },
  { mode: 2, name: 'Messiaen Mode 2 (Diminished half-whole)', intervals: [0, 1, 3, 4, 6, 7, 9, 10] },
  { mode: 3, name: 'Messiaen Mode 3', intervals: [0, 2, 3, 4, 6, 7, 8, 10, 11] },
  { mode: 4, name: 'Messiaen Mode 4', intervals: [0, 1, 2, 5, 6, 7, 8, 11] },
  { mode: 5, name: 'Messiaen Mode 5', intervals: [0, 1, 5, 6, 7, 11] },
  { mode: 6, name: 'Messiaen Mode 6', intervals: [0, 2, 4, 5, 6, 8, 10, 11] },
  { mode: 7, name: 'Messiaen Mode 7', intervals: [0, 1, 2, 3, 5, 6, 7, 8, 9, 11] },
];

const SCALE_GROUPS = [
  ['Modes of Major', ['major', 'ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']],
  ['Pentatonic & Blues', ['pentatonic', 'blues']],
  ['Melodic minor family', ['melodic minor', 'dorian b2', 'lydian augmented', 'lydian dominant', 'aeolian dominant', 'half diminished', 'altered', 'mixolydian b6']],
  ['Harmonic family', ['harmonic', 'locrian #6', 'major augmented', 'dorian #4', 'phrygian dominant', 'lydian #2', 'altered dominant bb7', 'dorian b5', 'phrygian b4', 'lydian b3', 'mixolydian b2', 'lydian augmented #2', 'locrian bb7']],
  ['Symmetric', ['whole tone', 'diminished', 'augmented', 'messiaen']],
  ['Bebop', ['bebop']],
];

// Fix spelling glitches carried in the database
const NAME_FIXES = {
  aeloian: 'Aeolian (Natural Minor)',
  'minor penatonic': 'Minor Pentatonic',
  pentatonic: 'Major Pentatonic',
  major: 'Major (Ionian)',
};

export function cleanScaleName(name) {
  return NAME_FIXES[name.trim().toLowerCase()] || name.trim();
}

export function scaleGroup(name) {
  const lower = name.toLowerCase();
  // Exact family matches first so e.g. "Dorian b2" is not filed under the modes of major
  for (const [group, keys] of SCALE_GROUPS.slice(2)) {
    if (keys.some((k) => lower === k || lower.startsWith(k + ' ') || lower.startsWith(k + ' ('))) return group;
  }
  for (const [group, keys] of SCALE_GROUPS) {
    if (keys.some((k) => lower.includes(k))) return group;
  }
  return 'More scales';
}

const sameSet = (a, b) => a.length === b.length && a.every((x) => b.includes(x));

/**
 * Merge the server catalogue with the built-in library.
 * Returns { scales, arpeggios, chords } where every entry has a stable `key`.
 */
export function buildLibrary(catalog) {
  const slug = (s) => s.toLowerCase().replace(/[^a-z0-9#]+/g, '-').replace(/#/g, 's').replace(/^-|-$/g, '');

  const scales = [];
  const addScale = (entry, source) => {
    const intervals = [...new Set(entry.intervals.map(mod12))].sort((a, b) => a - b);
    if (intervals.length < 5 || scales.some((s) => sameSet(s.intervals, intervals))) return;
    const name = cleanScaleName(entry.name);
    scales.push({ key: slug(name), id: entry.id ?? null, name, intervals, group: scaleGroup(name), source });
  };
  (catalog?.scales || []).forEach((s) => addScale(s, 'db'));
  SCALE_LIBRARY.forEach((s) => addScale(s, 'builtin'));
  for (const m of MESSIAEN_MODES) {
    const existing = scales.find((x) => sameSet(x.intervals, m.intervals));
    if (existing) existing.alias = `${existing.alias || ''} messiaen mode ${m.mode}`.trim();
    else addScale(m, 'builtin');
  }

  const chords = CHORD_LIBRARY.map((c) => ({ ...c, key: slug(c.name), voicings: [], source: 'builtin' }));
  for (const dbChord of catalog?.chords || []) {
    const match = chords.find((c) => sameSet(c.intervals, dbChord.intervals));
    if (match) {
      match.voicings = dbChord.voicings || [];
      match.source = 'db';
      match.dbName = dbChord.name;
    } else {
      chords.push({
        key: slug(dbChord.name), name: dbChord.name, symbol: ` ${dbChord.name}`, intervals: dbChord.intervals,
        group: 'Database', voicings: dbChord.voicings || [], source: 'db',
      });
    }
  }

  deriveVSystem(chords);

  const arpeggios = [];
  const addArp = (entry, source) => {
    const intervals = [...new Set(entry.intervals.map(mod12))].sort((a, b) => a - b);
    if (intervals.length < 3 || arpeggios.some((a) => sameSet(a.intervals, intervals))) return;
    const chord = chords.find((c) => sameSet(c.intervals, intervals));
    arpeggios.push({
      key: slug(entry.name), id: entry.id ?? null, name: entry.name.trim(), intervals,
      symbol: chord ? chord.symbol : '', group: chord ? chord.group : 'More', source,
    });
  };
  (catalog?.arpeggios || []).forEach((a) => addArp(a, 'db'));
  CHORD_LIBRARY.filter((c) => c.intervals.length >= 3).forEach((c) => addArp(c, 'builtin'));

  return { scales, arpeggios, chords };
}

/**
 * Reduce a chord to the notes a V-System voicing can hold: drop the 5th first, then the 9th, then the 11th.
 * Returns { intervals, omitted } or null when fewer than three notes remain.
 */
export function vSystemReduction(intervals, size) {
  let kept = [...intervals].sort((a, b) => a - b);
  const omitted = [];
  for (const drop of [7, 2, 5]) {
    if (kept.length <= size) break;
    if (kept.includes(drop)) { kept = kept.filter((iv) => iv !== drop); omitted.push(drop); }
  }
  return kept.length === size ? { intervals: kept, omitted } : null;
}

/**
 * The V-System only says which voice of the close-position chord sits on which string, so the database
 * templates of one 4-note chord (and one triad) apply to every other 4-note chord (and triad).
 * Chord types without voicings of their own get templates derived from Major 7 / Major.
 */
export function deriveVSystem(chords) {
  const sourceFor = (size) => chords
    .filter((c) => c.voicings.length && !c.vsDerived && c.intervals.length === size)
    .sort((a, b) => b.voicings.length - a.voicings.length)[0];
  for (const chord of chords) {
    if (chord.voicings.length) continue;
    for (const size of [4, 3]) {
      const reduction = vSystemReduction(chord.intervals, size);
      const source = sourceFor(size);
      if (!reduction || !source) continue;
      const from = [...source.intervals].sort((a, b) => a - b);
      chord.voicings = source.voicings.map((v) => ({
        ...v,
        id: `${chord.key}-${v.id}`,
        tones: v.tones.map((t) => ({ string: t.string, interval: reduction.intervals[from.indexOf(t.interval)] })),
      }));
      chord.vsDerived = true;
      chord.vsOmitted = reduction.omitted;
      break;
    }
  }
}

// ---------------------------------------------------------------------------
// Interval labels and spelling
// ---------------------------------------------------------------------------
const DEFAULT_LABELS = ['1', 'b2', '2', 'b3', '3', '4', 'b5', '5', 'b6', '6', 'b7', '7'];

/** Map semitone -> interval label, aware of the surrounding formula. */
export function intervalLabels(intervals, kind = 'scale') {
  const has = (n) => intervals.includes(n);
  const labels = {};
  if (kind === 'scale' && intervals.length === 7) {
    // Heptatonic: one letter per degree, accidental relative to major
    intervals.forEach((semi, degree) => {
      const diff = semi - MAJOR_STEPS[degree];
      const acc = diff === 0 ? '' : diff > 0 ? '#'.repeat(diff) : 'b'.repeat(-diff);
      labels[semi] = acc + (degree + 1);
    });
    return labels;
  }
  const seventh = has(10) || has(11) || (kind === 'chord' && has(9) && has(3) && has(6));
  for (const semi of intervals) {
    let label = DEFAULT_LABELS[semi];
    if (kind === 'chord') {
      if (semi === 2 && seventh) label = '9';
      if (semi === 1 && seventh) label = 'b9';
      if (semi === 3 && has(4)) label = '#9';
      if (semi === 5 && seventh && (has(3) || has(4))) label = '11';
      if (semi === 6 && has(7)) label = '#11';
      if (semi === 8) label = has(7) ? 'b13' : '#5';
      if (semi === 9) label = has(10) || has(11) ? '13' : (has(3) && has(6) && !has(7) ? 'bb7' : '6');
    } else {
      if (semi === 3 && has(4)) label = '#2';
      if (semi === 6 && !has(7) && has(8)) label = '#4';
      if (semi === 6 && has(7) && !has(5)) label = '#4';
      if (semi === 8 && !has(7)) label = '#5';
    }
    labels[semi] = label;
  }
  return labels;
}

/** Spell a note from a root name and an interval label such as "b3" or "#11". */
export function spellNote(rootName, semitone, label) {
  const rootLetter = rootName[0];
  const rootPc = mod12(LETTER_PC[rootLetter] + (rootName.includes('#') ? 1 : 0) - (rootName.slice(1).includes('b') ? 1 : 0));
  const match = /(\d+)$/.exec(label || '');
  const pc = mod12(rootPc + semitone);
  if (!match) return NOTE_SHARP[pc];
  const degree = (parseInt(match[1], 10) - 1) % 7;
  const letter = LETTERS[(LETTERS.indexOf(rootLetter) + degree) % 7];
  let diff = mod12(pc - LETTER_PC[letter]);
  if (diff > 6) diff -= 12;
  if (Math.abs(diff) > 1) {
    // Avoid double accidentals: fall back to the simplest name in this key's direction
    return (rootName.includes('b') || rootName === 'F' ? NOTE_FLAT : NOTE_SHARP)[pc];
  }
  return letter + (diff === 1 ? '#' : diff === -1 ? 'b' : '');
}

export function spellCollection(rootName, intervals, kind) {
  const labels = intervalLabels(intervals, kind);
  const out = {};
  for (const semi of intervals) out[semi] = spellNote(rootName, semi, labels[semi]);
  return { labels, names: out };
}

/** Coarse role of an interval for colouring. */
export function intervalRole(semi, labels) {
  if (semi === 0) return 'root';
  const label = labels?.[semi] || DEFAULT_LABELS[semi];
  const num = parseInt(label.replace(/[^0-9]/g, ''), 10);
  if (num === 3) return 'third';
  if (num === 5) return 'fifth';
  if (num === 7) return 'seventh';
  return 'tension';
}

// ---------------------------------------------------------------------------
// Scale & arpeggio positions with fingerings
// ---------------------------------------------------------------------------

/** All notes of a pitch-class set across the neck. */
export function neckNotes(rootPc, intervals, tuning, maxFret) {
  const notes = [];
  tuning.midi.forEach((open, string) => {
    for (let fret = 0; fret <= maxFret; fret++) {
      const interval = mod12(open + fret - rootPc);
      if (intervals.includes(interval)) notes.push({ string, fret, midi: open + fret, interval });
    }
  });
  return notes;
}

function nextPitch(midi, rootPc, intervals) {
  for (let m = midi + 1; m < midi + 13; m++) if (intervals.includes(mod12(m - rootPc))) return m;
  return null;
}

/** Fingers for a box shape: choose the index-finger anchor with the fewest stretches. */
export function fingerBox(notes) {
  const fretted = notes.filter((n) => n.fret > 0);
  if (!fretted.length) return { anchor: 0, notes: notes.map((n) => ({ ...n, finger: 0 })) };
  const lo = Math.min(...fretted.map((n) => n.fret));
  let best = null;
  for (let anchor = lo - 1; anchor <= lo + 1; anchor++) {
    if (anchor < 1) continue;
    let cost = 0;
    for (const n of fretted) {
      const d = n.fret - anchor;
      if (d >= 0 && d <= 3) continue;
      cost += d === -1 || d === 4 ? 1 : 6;
    }
    // Prefer anchoring the index finger on the lowest note when costs tie
    cost += Math.abs(anchor - lo) * 0.01;
    if (!best || cost < best.cost) best = { anchor, cost };
  }
  const { anchor } = best;
  return {
    anchor,
    notes: notes.map((n) => {
      if (n.fret === 0) return { ...n, finger: 0 };
      const d = n.fret - anchor;
      const finger = d < 0 ? 1 : d > 3 ? 4 : d + 1;
      return { ...n, finger, stretch: d < 0 || d > 3 };
    }),
  };
}

/** Fingers for one string of a three-notes-per-string pattern. */
export function fingerStringGroup(frets) {
  if (frets.length === 1) return [1];
  const base = frets[0];
  const offsets = frets.map((f) => f - base);
  const last = offsets[offsets.length - 1];
  if (frets.length === 2) return [1, last >= 3 ? 4 : last + 1];
  if (last <= 2) return offsets.map((d) => d + 1);
  // span of 3+ frets: index on first, pinky on last, middle note on 2 or 3
  return offsets.map((d, i) => {
    if (i === 0) return 1;
    if (i === offsets.length - 1) return 4;
    return d === 1 ? 2 : last - d === 1 ? 3 : 2;
  });
}

function buildBox(anchor, rootPc, intervals, tuning) {
  const open = tuning.midi;
  const n = open.length;
  const lo = Math.max(0, anchor - 1);
  const hi = anchor + 4;
  const inCore = (f) => f >= Math.max(0, anchor) && f <= anchor + 3;

  // Lowest scale pitch on the lowest string inside the core window
  let pitch = null;
  for (let f = Math.max(0, anchor); f <= anchor + 3; f++) {
    if (intervals.includes(mod12(open[0] + f - rootPc))) { pitch = open[0] + f; break; }
  }
  if (pitch === null) return [];
  const notes = [{ string: 0, fret: pitch - open[0], midi: pitch, interval: mod12(pitch - rootPc) }];
  let string = 0;
  const perString = { 0: 1 };
  for (;;) {
    pitch = nextPitch(pitch, rootPc, intervals);
    if (pitch === null) break;
    const options = [];
    const frets = notes.map((x) => x.fret).filter((f) => f > 0);
    const curMin = frets.length ? Math.min(...frets) : anchor;
    const curMax = frets.length ? Math.max(...frets) : anchor;
    for (let s = string; s < n; s++) {
      const fret = pitch - open[s];
      // Keep the whole position within one hand span (four frets plus one stretch)
      const fitsHand = fret === 0 || (fret - curMin <= 4 && curMax - fret <= 4);
      if (fret >= lo && fret <= hi && fitsHand && (perString[s] || 0) < 4) options.push({ s, fret });
    }
    const pick = options.find((o) => inCore(o.fret))
      || options.find((o) => o.fret === anchor - 1)
      || options.find((o) => o.fret === anchor + 4);
    if (!pick) break;
    string = pick.s;
    perString[string] = (perString[string] || 0) + 1;
    notes.push({ string, fret: pick.fret, midi: pitch, interval: mod12(pitch - rootPc) });
  }
  return notes;
}

function buildPerString(startFret, rootPc, intervals, tuning, perStringCount) {
  const open = tuning.midi;
  let pitch = open[0] + startFret;
  const notes = [];
  for (let s = 0; s < open.length; s++) {
    for (let k = 0; k < perStringCount; k++) {
      if (!(s === 0 && k === 0)) pitch = nextPitch(pitch, rootPc, intervals);
      const fret = pitch - open[s];
      if (fret < 0) return [];
      notes.push({ string: s, fret, midi: pitch, interval: mod12(pitch - rootPc) });
    }
  }
  return notes;
}

// Fourths/major-third tunings support the classic box logic; open and drop tunings use fret windows
export function isRegularTuning(tuning) {
  return tuning.midi.every((m, i) => i === 0 || [4, 5].includes(m - tuning.midi[i - 1]));
}

function buildWindow(start, rootPc, intervals, tuning) {
  const lo = Math.max(0, start);
  const hi = lo + 4;
  const notes = [];
  tuning.midi.forEach((open, string) => {
    for (let fret = lo === 0 ? 0 : lo; fret <= hi; fret++) {
      const interval = mod12(open + fret - rootPc);
      if (intervals.includes(interval)) notes.push({ string, fret, midi: open + fret, interval });
    }
  });
  return notes;
}

/**
 * Positions for a scale or arpeggio.
 * system: 'box' (one finger per fret, CAGED-style) or 'nps' (three notes per string).
 */
export function scalePositions(rootPc, intervals, tuning, { system = 'box', maxStart = 12 } = {}) {
  const open0 = tuning.midi[0];
  const rootFret = mod12(rootPc - open0);
  // Start frets: every scale degree on the lowest string, folded below the 12th fret
  const starts = intervals.map((iv) => {
    let f = rootFret + iv;
    if (f >= maxStart) f -= 12;
    return f;
  });
  const positions = [];
  const seen = new Set();
  const perStringCount = intervals.length <= 5 ? 2 : 3;
  starts.forEach((start, degree) => {
    let notes;
    if (system === 'nps') {
      notes = buildPerString(start, rootPc, intervals, tuning, perStringCount);
      // Scales with chromatic passing tones can run out of frets below the nut: play that position an octave up
      if (!notes.length && start < 12) notes = buildPerString(start + 12, rootPc, intervals, tuning, perStringCount);
    }
    else if (isRegularTuning(tuning)) notes = buildBox(start, rootPc, intervals, tuning);
    else notes = buildWindow(start, rootPc, intervals, tuning);
    if (notes.length < intervals.length) return;
    const sig = notes.map((n) => `${n.string}:${n.fret}`).join('|');
    if (seen.has(sig)) return;
    seen.add(sig);
    let fingered;
    if (system === 'nps') {
      fingered = [];
      for (let s = 0; s < tuning.midi.length; s++) {
        const group = notes.filter((n) => n.string === s);
        const fretted = group.filter((n) => n.fret > 0);
        const fingers = fingerStringGroup(fretted.map((n) => n.fret));
        let k = 0;
        group.forEach((n) => fingered.push({ ...n, finger: n.fret === 0 ? 0 : fingers[k++] }));
      }
    } else {
      fingered = fingerBox(notes).notes;
    }
    const frets = notes.map((n) => n.fret);
    positions.push({
      startDegree: degree,
      startInterval: intervals[degree],
      notes: fingered,
      minFret: Math.min(...frets),
      maxFret: Math.max(...frets),
    });
  });
  // Numbered by place on the neck: position 1 is the lowest one (open strings included), whatever the key
  positions.sort((a, b) => a.minFret - b.minFret || a.notes[0].fret - b.notes[0].fret);
  return positions.map((p, i) => ({ ...p, index: i + 1 }));
}

// ---------------------------------------------------------------------------
// Chord fingering
// ---------------------------------------------------------------------------

/**
 * Assign fingers to a fret array (lowest string first; -1 muted, 0 open).
 * Returns { fingers, barres } or null when the shape needs more than four fingers.
 */
export function assignFingers(frets) {
  const fretted = frets.map((f, s) => ({ s, f })).filter((n) => n.f > 0);
  const fingers = frets.map((f) => (f < 0 ? null : 0));
  if (!fretted.length) return { fingers, barres: [] };
  const byFret = (a, b) => a.f - b.f || a.s - b.s;

  if (fretted.length <= 4) {
    [...fretted].sort(byFret).forEach((n, i) => { fingers[n.s] = i + 1; });
    return { fingers, barres: [] };
  }

  const minF = Math.min(...fretted.map((n) => n.f));
  const atMin = fretted.filter((n) => n.f === minF).map((n) => n.s);
  const from = Math.min(...atMin);
  let to = Math.max(...atMin);
  // A full barre extends to the highest string when that keeps it a single straight bar
  for (let s = from; s <= to; s++) {
    if (frets[s] === 0 || (frets[s] > 0 && frets[s] < minF)) return null;
  }
  const rest = fretted.filter((n) => n.f > minF || n.s < from || n.s > to);
  atMin.forEach((s) => { if (s >= from && s <= to) fingers[s] = 1; });
  const barres = [{ finger: 1, fret: minF, from, to }];

  // Group remaining notes; a same-fret group on adjacent strings may share one finger (A-shape)
  let units = rest.map((n) => ({ fret: n.f, strings: [n.s] }));
  if (units.length > 3) {
    const groups = {};
    rest.forEach((n) => { (groups[n.f] = groups[n.f] || []).push(n.s); });
    const candidates = Object.entries(groups)
      .map(([f, ss]) => ({ fret: +f, strings: ss.sort((a, b) => a - b) }))
      .filter((g) => g.strings.length >= 2 && g.strings.every((s, i, arr) => i === 0 || frets.slice(arr[i - 1] + 1, s).every((x) => x < 0 || x >= g.fret)))
      .sort((a, b) => b.strings.length - a.strings.length);
    if (!candidates.length) return null;
    const g = candidates[0];
    units = [g, ...rest.filter((n) => !g.strings.includes(n.s)).map((n) => ({ fret: n.f, strings: [n.s] }))];
    if (units.length > 3) return null;
  }
  units.sort((a, b) => a.fret - b.fret || a.strings[0] - b.strings[0]).forEach((u, i) => {
    const finger = i + 2;
    u.strings.forEach((s) => { fingers[s] = finger; });
    if (u.strings.length > 1) barres.push({ finger, fret: u.fret, from: u.strings[0], to: u.strings[u.strings.length - 1] });
  });
  return { fingers, barres };
}

/** Classify a voicing (close / drop 2 / drop 3 / drop 2+4 / spread). */
export function classifyVoicing(midis) {
  const v = [...midis].sort((a, b) => a - b);
  const pcs = new Set(v.map(mod12));
  if (pcs.size !== v.length) return v.length >= 5 ? 'Full' : '';
  const close = (arr) => { const s = [...arr].sort((a, b) => a - b); return s[s.length - 1] - s[0] < 12; };
  if (close(v)) return 'Close';
  if (v.length === 3) return 'Spread';
  if (v.length === 4) {
    const up0 = [v[0] + 12, v[1], v[2], v[3]];
    if (close(up0)) return v[0] + 12 > v[3] ? '' : v[0] + 12 > v[2] ? 'Drop 2' : 'Drop 3';
    if (close([v[0] + 12, v[1] + 12, v[2], v[3]])) return 'Drop 2+4';
  }
  return '';
}

const INVERSION_NAMES = { 0: 'Root position', 1: '1st inversion', 2: '2nd inversion', 3: '3rd inversion' };

export function inversionName(bassInterval, intervals) {
  const sorted = [...intervals].sort((a, b) => a - b);
  // Inversion number follows the chord-tone stack 1-3-5-7 (tensions count as their own label)
  const stack = sorted.filter((iv) => [0, 3, 4, 2, 5, 6, 7, 8, 9, 10, 11].includes(iv));
  const core = [0, stack.find((i) => i === 3 || i === 4 || i === 2 || i === 5), stack.find((i) => i >= 6 && i <= 8), stack.find((i) => i >= 9)];
  const idx = core.indexOf(bassInterval);
  return idx >= 0 ? INVERSION_NAMES[idx] : 'Slash chord';
}

function describeVoicing(frets, tuning, rootPc, intervals) {
  const midis = [];
  let bass = null;
  frets.forEach((f, s) => {
    if (f < 0) return;
    const m = tuning.midi[s] + f;
    midis.push(m);
    if (bass === null) bass = mod12(m - rootPc);
  });
  return {
    bassInterval: bass,
    inversion: inversionName(bass, intervals),
    voicing: classifyVoicing(midis),
    midis,
  };
}

function scoreShape(frets, fingering, rootPc, intervals, tuning) {
  const sounding = frets.map((f, s) => ({ f, s })).filter((n) => n.f >= 0);
  const fretted = sounding.filter((n) => n.f > 0);
  const lowS = sounding[0].s;
  const highS = sounding[sounding.length - 1].s;
  const interiorMutes = frets.slice(lowS, highS + 1).filter((f) => f < 0).length;
  const topMutes = frets.length - 1 - highS;
  const span = fretted.length ? Math.max(...fretted.map((n) => n.f)) - Math.min(...fretted.map((n) => n.f)) : 0;
  const minF = fretted.length ? Math.min(...fretted.map((n) => n.f)) : 0;
  const opens = sounding.length - fretted.length;
  const bass = mod12(tuning.midi[lowS] + frets[lowS] - rootPc);
  const pcs = new Set(sounding.map((n) => mod12(tuning.midi[n.s] + n.f - rootPc)));
  const missingFifth = intervals.includes(7) && !pcs.has(7);
  const fingersUsed = new Set(fingering.fingers.filter((f) => f > 0)).size;
  let score = span * 1.1 + (span >= 4 ? 1.5 : 0);
  score += fingering.barres.length ? 1.3 + (fingering.barres.length - 1) * 0.8 : 0;
  score += interiorMutes * 2.6 + topMutes * 0.7;
  score += missingFifth ? 0.4 : 0;
  score += bass === 0 ? 0 : 2.2;
  score += minF * 0.08 + fingersUsed * 0.15;
  // Fuller shapes are what most players look for first; open strings only help near the nut
  score -= sounding.length * 0.9;
  const maxF = fretted.length ? Math.max(...fretted.map((n) => n.f)) : 0;
  score += opens * (maxF <= 4 ? -0.3 : minF >= 5 ? 1.6 : 1.0);
  return score;
}

/** A complete shape record (fingers, barres, inversion, voicing) for an explicit fret array, e.g. from a link. */
export function shapeFromFrets(frets, tuning, rootPc, intervals) {
  if (frets.length !== tuning.midi.length || !frets.some((f) => f >= 0)) return null;
  const fretted = frets.filter((f) => f > 0);
  const fingering = assignFingers(frets) || { fingers: frets.map((f) => (f < 0 ? null : f === 0 ? 0 : 1)), barres: [] };
  return {
    frets: [...frets], ...fingering,
    ...describeVoicing(frets, tuning, rootPc, intervals),
    minFret: fretted.length ? Math.min(...fretted) : 0,
    span: fretted.length ? Math.max(...fretted) - Math.min(...fretted) : 0,
  };
}

/**
 * Find playable chord shapes anywhere on the neck.
 * options: { maxFret, maxSpan (frets between lowest and highest fretted note), minStrings, bass }
 * bass: null (any) or an interval that must be in the bass.
 */
export function findChordShapes(rootPc, intervals, tuning, options = {}) {
  const { maxFret = 15, maxSpan = 3, minStrings = Math.min(3, intervals.length), bass = null, limit = 48 } = options;
  const n = tuning.midi.length;
  const chordSet = new Set(intervals);
  const optional = new Set();
  if (intervals.length >= 4 && intervals.includes(7)) optional.add(7);
  if (intervals.length >= 6) { optional.add(2); optional.add(5); }
  const required = intervals.filter((iv) => !optional.has(iv));
  const results = new Map();

  for (let w = 0; w <= maxFret; w++) {
    const choices = tuning.midi.map((open) => {
      const opts = [-1];
      if (chordSet.has(mod12(open - rootPc))) opts.push(0);
      if (w > 0) {
        for (let f = w; f <= Math.min(w + maxSpan, maxFret); f++) {
          if (chordSet.has(mod12(open + f - rootPc))) opts.push(f);
        }
      }
      return opts;
    });
    const frets = new Array(n).fill(-1);
    const walk = (s) => {
      if (s === n) {
        evaluate(frets.slice());
        return;
      }
      for (const f of choices[s]) {
        frets[s] = f;
        walk(s + 1);
      }
    };
    const evaluate = (shape) => {
      const fretted = shape.filter((f) => f > 0);
      // Anchor each window on its lowest fretted note so shapes are generated once
      if (w > 0 && (!fretted.length || Math.min(...fretted) !== w)) return;
      if (w === 0 && fretted.length) return;
      const sounding = shape.filter((f) => f >= 0).length;
      if (sounding < minStrings) return;
      const pcs = new Set();
      shape.forEach((f, s) => { if (f >= 0) pcs.add(mod12(tuning.midi[s] + f - rootPc)); });
      if (!required.every((iv) => pcs.has(iv))) return;
      const lowS = shape.findIndex((f) => f >= 0);
      const highS = n - 1 - [...shape].reverse().findIndex((f) => f >= 0);
      const interior = shape.slice(lowS, highS + 1).filter((f) => f < 0).length;
      if (interior > 1) return;
      const bassIv = mod12(tuning.midi[lowS] + shape[lowS] - rootPc);
      if (bass !== null && bassIv !== bass) return;
      const fingering = assignFingers(shape);
      if (!fingering) return;
      const key = shape.join(',');
      if (results.has(key)) return;
      results.set(key, {
        frets: shape,
        ...fingering,
        score: scoreShape(shape, fingering, rootPc, intervals, tuning),
        ...describeVoicing(shape, tuning, rootPc, intervals),
        minFret: fretted.length ? Math.min(...fretted) : 0,
      });
    };
    walk(0);
  }

  // Variety first: a better shape plus/minus one string (e.g. x32010 vs 332010) goes after the distinct shapes
  const sorted = [...results.values()].sort((a, b) => a.score - b.score);
  const similar = (a, b) => {
    const diff = a.frets.map((f, s) => s).filter((s) => a.frets[s] !== b.frets[s]);
    return diff.length === 1 && (a.frets[diff[0]] < 0 || b.frets[diff[0]] < 0);
  };
  const primary = [];
  const variants = [];
  for (const shape of sorted) (primary.some((p) => similar(p, shape)) ? variants : primary).push(shape);
  return primary.concat(variants).slice(0, limit);
}

/**
 * Turn database voicing templates (V-System etc.) into concrete shapes for a root.
 * Each template yields all inversions (rotating every voice to the next chord tone,
 * exactly like ChordPosition offsets in the Django models).
 */
export function voicingTemplateShapes(rootPc, chordIntervals, template, tuning, { maxFret = 22, maxSpan = 11 } = {}) {
  const n = tuning.midi.length;
  const indexByNumber = {};
  tuning.numbers.forEach((num, idx) => { indexByNumber[num] = idx; });
  const tones = template.tones.map((t) => ({ idx: indexByNumber[DB_STRING_NUMBERS[t.string]], interval: t.interval }));
  if (tones.some((t) => t.idx === undefined)) return [];
  // Chord-tone cycle (1-3-5-7): every voice moves up to the next chord tone per inversion,
  // exactly like the ChordPosition offsets in the Django models.
  const cycle = [...new Set(tones.map((t) => t.interval))].sort((a, b) => a - b);
  const order = [...tones].sort((a, b) => a.idx - b.idx);

  // Root position: octave per voice so pitches rise from string to string with the smallest span
  const base = order.map((t) => mod12(rootPc + t.interval - tuning.midi[t.idx]));
  let rootPos = null;
  for (let mask = 0; mask < 1 << order.length; mask++) {
    const frets = base.map((b, k) => b + (mask & (1 << k) ? 12 : 0));
    const pitches = frets.map((f, k) => tuning.midi[order[k].idx] + f);
    if (pitches.some((p, k) => k > 0 && p <= pitches[k - 1])) continue;
    const fretted = frets.filter((f) => f > 0);
    const span = fretted.length ? Math.max(...fretted) - Math.min(...fretted) : 0;
    const low = Math.min(...frets);
    if (!rootPos || span < rootPos.span || (span === rootPos.span && low < rootPos.low)) rootPos = { pitches, span, low };
  }
  if (!rootPos) return [];

  const shapes = [];
  for (let inv = 0; inv < cycle.length; inv++) {
    const pitches = rootPos.pitches.map((p, k) => {
      let pitch = p;
      let iv = order[k].interval;
      for (let step = 0; step < inv; step++) {
        const next = cycle[(cycle.indexOf(iv) + 1) % cycle.length];
        pitch += mod12(next - iv) || 12;
        iv = next;
      }
      return pitch;
    });
    let voiceFrets = pitches.map((p, k) => p - tuning.midi[order[k].idx]);
    // Show each inversion at its lowest octave on the neck
    voiceFrets = voiceFrets.map((f) => f - 12 * Math.floor(Math.min(...voiceFrets) / 12));
    const fretted = voiceFrets.filter((f) => f > 0);
    const span = fretted.length ? Math.max(...fretted) - Math.min(...fretted) : 0;
    if (Math.max(...voiceFrets) > maxFret || span > maxSpan) continue;
    const frets = new Array(n).fill(-1);
    order.forEach((t, k) => { frets[t.idx] = voiceFrets[k]; });
    const fingering = assignFingers(frets) || { fingers: frets.map((f) => (f < 0 ? null : f === 0 ? 0 : 1)), barres: [] };
    shapes.push({
      frets, ...fingering, inversionIndex: inv, system: template.system, range: template.range,
      ...describeVoicing(frets, tuning, rootPc, chordIntervals),
      minFret: fretted.length ? Math.min(...fretted) : 0,
      span,
    });
  }
  return shapes;
}

// ---------------------------------------------------------------------------
// Reverse lookup: what chord / scale is this?
// ---------------------------------------------------------------------------
export function identifyChords(pcs, bassPc, chordLibrary, rootNames = ROOT_NAMES) {
  const set = [...new Set(pcs.map(mod12))];
  if (set.length < 2) return [];
  const out = [];
  for (let root = 0; root < 12; root++) {
    for (const chord of chordLibrary) {
      const chordPcs = chord.intervals.map((iv) => mod12(iv + root));
      const allIn = set.every((pc) => chordPcs.includes(pc));
      if (!allIn) continue;
      const missing = chordPcs.filter((pc) => !set.includes(pc));
      const missingIntervals = missing.map((pc) => mod12(pc - root));
      // Only the fifth may be left out (plus 9/11 on big chords)
      const tolerable = missingIntervals.every((iv) => iv === 7 || (chord.intervals.length >= 6 && (iv === 2 || iv === 5)));
      if (!tolerable || !set.includes(root) && chord.intervals.length < 5) continue;
      const exact = missing.length === 0;
      const score = (exact ? 0 : 2 + missing.length) + (root === bassPc ? 0 : 1.5) + chord.intervals.length * 0.15
        + (set.includes(root) ? 0 : 3);
      const name = rootNames[root] + chord.symbol + (bassPc !== null && bassPc !== root ? '/' + rootNames[bassPc] : '');
      out.push({ root, chord, name, exact, missing: missingIntervals, score });
    }
  }
  out.sort((a, b) => a.score - b.score);
  const seen = new Set();
  return out.filter((r) => (seen.has(r.name) ? false : seen.add(r.name))).slice(0, 12);
}

function scalePopularity(name) {
  if (/^major \(|aeolian|minor pentatonic|major pentatonic|dorian$|mixolydian$|lydian$|blues/i.test(name)) return 0;
  if (/phrygian$|locrian$|harmonic minor|melodic minor/i.test(name)) return 1;
  return 2.5;
}

/** Scales containing all given pitch classes; `preferRoot` (e.g. the chord root) ranks first. */
export function identifyScales(pcs, scaleLibrary, preferRoot = null) {
  const set = [...new Set(pcs.map(mod12))];
  if (set.length < 2) return [];
  const out = [];
  for (let root = 0; root < 12; root++) {
    for (const scale of scaleLibrary) {
      const scalePcs = scale.intervals.map((iv) => mod12(iv + root));
      if (!set.every((pc) => scalePcs.includes(pc))) continue;
      const extra = scalePcs.length - set.length;
      const score = extra * 0.5 + scalePopularity(scale.name) + (set.includes(root) ? 0 : 2)
        + (preferRoot === null || root === preferRoot ? 0 : 0.75);
      out.push({ root, scale, extra, score });
    }
  }
  out.sort((a, b) => a.score - b.score);
  return out.slice(0, 12);
}

// ---------------------------------------------------------------------------
// Chord symbol search ("Em7", "Maj7#11", "F#m7b5")
// ---------------------------------------------------------------------------
// Extra spellings people type for the library's chord qualities (keys: normalised library symbol).
const QUALITY_ALIASES = {
  '': ['maj', 'major', 'ma'],
  m: ['min', 'minor', 'mi', '-'],
  dim: ['o', '°', 'diminished'],
  aug: ['+', 'augmented'],
  sus4: ['sus'],
  maj7: ['ma7', 'major7', 'Δ', 'Δ7'],
  7: ['dom7', 'dominant7', 'dominant'],
  m7: ['min7', 'mi7', 'minor7', '-7'],
  m7b5: ['ø', 'ø7', 'min7b5', 'm7-5', 'halfdim', 'halfdiminished'],
  dim7: ['o7', '°7'],
  'mmaj7': ['minmaj7', 'mmaj7', 'm#7', '-maj7'],
  '7#5': ['aug7', '+7', '7+5'],
  'maj7#5': ['maj7+5', '+maj7'],
  m6: ['min6', 'minor6', '-6'],
  add9: ['add2'],
  madd9: ['minadd9', 'm(add9)'],
  maj9: ['ma9', 'major9', 'Δ9'],
  m9: ['min9', 'minor9', '-9'],
  '7b9': ['7-9'],
  '7#9': ['7+9'],
  '7b5': ['7-5'],
  m11: ['min11', 'minor11', '-11'],
};

/** Lowercase, drop spaces and parentheses, unify accidental glyphs. */
function normaliseQuality(text) {
  return text.replace(/[♯]/g, '#').replace(/[♭]/g, 'b').replace(/[\s()]/g, '').toLowerCase();
}

/** Resolve the quality part of a chord symbol to library entries (by interval-set identity). */
export function findChordQuality(text, chordLibrary) {
  const raw = text.replace(/[\s()]/g, '').replace(/♯/g, '#').replace(/♭/g, 'b');
  // A capital M followed by nothing or a digit means major ("M7" is not "m7")
  const capitalM = /^M(?!in|a|i)(\d.*)?$/.exec(raw);
  const norm = capitalM ? (capitalM[1] ? `maj${capitalM[1]}` : 'maj') : normaliseQuality(raw);
  if (!norm && raw !== '') return [];
  const hits = [];
  for (const chord of chordLibrary) {
    const sym = normaliseQuality(chord.symbol || '').trim();
    const aliasList = (QUALITY_ALIASES[sym] || []).map(normaliseQuality);
    const candidates = new Set([sym, normaliseQuality(chord.name), normaliseQuality(chord.dbName || ''), ...aliasList]);
    if (chord.symbol !== undefined && candidates.has(norm) && (norm !== '' || sym === '')) hits.push(chord);
  }
  return hits;
}

/**
 * Parse a search string such as "Em7", "F#m7b5" or "maj7#11".
 * Returns { root (pitch class or null), rootName, quality, chords: [library entries] } or null.
 * A bare root ("E") is not treated as a chord symbol so plain-text search keeps working.
 */
export function parseChordQuery(text, chordLibrary) {
  const q = text.trim();
  if (!q) return null;
  const m = /^([A-Ga-g])([#b♯♭]?)\s*(.*)$/.exec(q);
  const attempts = [];
  if (m) {
    if (m[2]) attempts.push({ rootName: m[1].toUpperCase() + m[2].replace('♯', '#').replace('♭', 'b'), rest: m[3] });
    attempts.push({ rootName: m[1].toUpperCase(), rest: m[2] + m[3] });
  }
  attempts.push({ rootName: null, rest: q });
  for (const { rootName, rest } of attempts) {
    if (rootName && !rest.trim()) continue;
    const chords = findChordQuality(rest, chordLibrary);
    if (!chords.length) continue;
    let root = null;
    if (rootName) {
      root = mod12(LETTER_PC[rootName[0]] + (rootName.includes('#') ? 1 : 0) - (rootName.slice(1).includes('b') ? 1 : 0));
    }
    return { root, rootName, quality: rest.trim(), chords };
  }
  return null;
}

// ---------------------------------------------------------------------------
// Chord <-> scale fit (shared by search suggestions and the scale view)
// ---------------------------------------------------------------------------
const pcSet = (root, intervals) => intervals.map((iv) => mod12(iv + root));
const isSubset = (small, big) => small.every((pc) => big.includes(pc));

/**
 * Chord-scale relationships after Nettles/Graf, "The Chord Scale Theory & Jazz Harmony".
 * Each entry names the chords (library symbols, built on the scale root) the scale is the chord scale for,
 * most characteristic first, with its available tensions and avoid notes. Scales are matched by interval
 * set, so database entries with other names (e.g. "Super Locrian") resolve too. Pentatonic, blues and
 * bebop entries follow the same idea for the scales the book does not list as chord scales.
 */
export const CHORD_SCALES = [
  { name: 'Ionian', intervals: [0, 2, 4, 5, 7, 9, 11], chords: ['maj7', '6', 'maj9', '6/9', 'add9', ''], tensions: ['9', '13'], avoid: ['11'] },
  { name: 'Dorian', intervals: [0, 2, 3, 5, 7, 9, 10], chords: ['m7', 'm6', 'm9', 'm11', 'm(add9)', 'm'], tensions: ['9', '11', '13'], avoid: [] },
  { name: 'Phrygian', intervals: [0, 1, 3, 5, 7, 8, 10], chords: ['m7', 'm'], tensions: ['11'], avoid: ['b9', 'b13'] },
  { name: 'Lydian', intervals: [0, 2, 4, 6, 7, 9, 11], chords: ['maj7#11', 'maj7', 'maj9', '6', '6/9', 'add9', ''], tensions: ['9', '#11', '13'], avoid: [] },
  { name: 'Mixolydian', intervals: [0, 2, 4, 5, 7, 9, 10], chords: ['7', '9', '13', '7sus4', ''], tensions: ['9', '13'], avoid: ['11'] },
  { name: 'Aeolian', intervals: [0, 2, 3, 5, 7, 8, 10], chords: ['m7', 'm9', 'm11', 'm(add9)', 'm'], tensions: ['9', '11'], avoid: ['b13'] },
  { name: 'Locrian', intervals: [0, 1, 3, 5, 6, 8, 10], chords: ['m7b5', 'dim'], tensions: ['11', 'b13'], avoid: ['b9'] },
  { name: 'Melodic Minor', intervals: [0, 2, 3, 5, 7, 9, 11], chords: ['m(maj7)', 'm6', 'm(add9)', 'm'], tensions: ['9', '11', '13'], avoid: [] },
  { name: 'Harmonic Minor', intervals: [0, 2, 3, 5, 7, 8, 11], chords: ['m(maj7)', 'm'], tensions: ['9', '11'], avoid: ['b13'] },
  { name: 'Dorian b2', intervals: [0, 1, 3, 5, 7, 9, 10], chords: ['7sus4', 'm7'], tensions: ['b9', '13'], avoid: [] },
  { name: 'Lydian Augmented', intervals: [0, 2, 4, 6, 8, 9, 11], chords: ['maj7#5', 'aug'], tensions: ['9', '#11', '13'], avoid: [] },
  { name: 'Lydian Dominant', intervals: [0, 2, 4, 6, 7, 9, 10], chords: ['7', '9', '13', '7b5', ''], tensions: ['9', '#11', '13'], avoid: [] },
  { name: 'Mixolydian b6', intervals: [0, 2, 4, 5, 7, 8, 10], chords: ['7', '9', ''], tensions: ['9', 'b13'], avoid: ['11'] },
  { name: 'Locrian #2', intervals: [0, 2, 3, 5, 6, 8, 10], chords: ['m7b5', 'dim'], tensions: ['9', '11', 'b13'], avoid: [] },
  { name: 'Altered', intervals: [0, 1, 3, 4, 6, 8, 10], chords: ['7#5', '7b5'], tensions: ['b9', '#9', '#11', 'b13'], avoid: [] },
  { name: 'Phrygian Dominant', intervals: [0, 1, 4, 5, 7, 8, 10], chords: ['7b9', '7', ''], tensions: ['b9', 'b13'], avoid: ['11'] },
  { name: 'Diminished (half-whole)', intervals: [0, 1, 3, 4, 6, 7, 9, 10], chords: ['7b9', '7#9', '7', '7b5'], tensions: ['b9', '#9', '#11', '13'], avoid: [] },
  { name: 'Diminished (whole-half)', intervals: [0, 2, 3, 5, 6, 8, 9, 11], chords: ['dim7', 'dim'], tensions: ['9', '11', 'b13', 'maj7'], avoid: [] },
  { name: 'Whole Tone', intervals: [0, 2, 4, 6, 8, 10], chords: ['7#5', '7b5', 'aug'], tensions: ['9', '#11', 'b13'], avoid: [] },
  { name: 'Major Pentatonic', intervals: [0, 2, 4, 7, 9], chords: ['6/9', '6', 'add9', ''], tensions: ['9', '13'], avoid: [] },
  { name: 'Minor Pentatonic', intervals: [0, 3, 5, 7, 10], chords: ['m7', '7sus4', 'm'], tensions: ['11'], avoid: [] },
  { name: 'Blues', intervals: [0, 3, 5, 6, 7, 10], chords: ['m7', 'm'], tensions: ['11'], avoid: [] },
  { name: 'Bebop Dominant', intervals: [0, 2, 4, 5, 7, 9, 10, 11], chords: ['7', '9', '13'], tensions: ['9', '13'], avoid: ['11'] },
  { name: 'Bebop Major', intervals: [0, 2, 4, 5, 7, 8, 9, 11], chords: ['6', 'maj7', '6/9', 'maj9', ''], tensions: ['9', '13'], avoid: ['11'] },
  { name: 'Bebop Dorian', intervals: [0, 2, 3, 4, 5, 7, 9, 10], chords: ['m7', 'm9', 'm11', 'm6'], tensions: ['9', '11', '13'], avoid: [] },
  { name: 'Bebop Harmonic Minor', intervals: [0, 2, 3, 5, 7, 8, 10, 11], chords: ['m(maj7)', 'm7', 'm'], tensions: ['9', '11'], avoid: ['b13'] },
  { name: 'Bebop Melodic Minor', intervals: [0, 2, 3, 5, 7, 8, 9, 11], chords: ['m6', 'm(maj7)', 'm'], tensions: ['9', '11'], avoid: [] },
];

const chordBySymbol = (symbol, chordLibrary) => {
  const builtin = CHORD_LIBRARY.find((c) => c.symbol === symbol);
  return builtin ? chordLibrary.find((c) => sameSet(c.intervals, builtin.intervals)) || null : null;
};

/** The chord-scale entry for a scale (by interval set), with its chords resolved against the library. */
export function chordScaleFor(scaleIntervals, chordLibrary) {
  const entry = CHORD_SCALES.find((e) => sameSet(e.intervals, scaleIntervals));
  if (!entry) return null;
  return { ...entry, chords: entry.chords.map((sym) => chordBySymbol(sym, chordLibrary)).filter(Boolean) };
}

/**
 * Scales on `rootPc` for a chord: the chord scales that list it (Nettles/Graf), most characteristic first.
 * Chords outside the table (e.g. database-only types) fall back to every scale holding all chord tones.
 */
export function scalesForChord(rootPc, chordIntervals, scaleLibrary, limit = 8) {
  const ranked = [];
  CHORD_SCALES.forEach((entry, order) => {
    const at = entry.chords.findIndex((sym) => {
      const c = CHORD_LIBRARY.find((x) => x.symbol === sym);
      return c && sameSet(c.intervals, chordIntervals);
    });
    if (at < 0) return;
    const scale = scaleLibrary.find((sc) => sameSet(sc.intervals, entry.intervals));
    if (scale) ranked.push({ scale, root: rootPc, chordScale: entry, score: at * 10 + order });
  });
  if (ranked.length) return ranked.sort((a, b) => a.score - b.score).slice(0, limit);
  const chordPcs = pcSet(rootPc, chordIntervals);
  return scaleLibrary
    .filter((scale) => isSubset(chordPcs, pcSet(rootPc, scale.intervals)))
    .map((scale) => ({ scale, root: rootPc, score: (scale.intervals.length - chordIntervals.length) * 0.5 + scalePopularity(scale.name) }))
    .sort((a, b) => a.score - b.score)
    .slice(0, limit);
}

/**
 * Chords that live inside a scale.
 * diatonic: for heptatonic scales the stacked-thirds triads and sevenths per degree.
 * chordScale: the chords on the scale root this scale is the chord scale for (Nettles/Graf), with
 *   tensions and avoid notes; null for scales outside the table.
 * others: only for scales without a chord-scale entry, the library chords (3+ notes) on the scale root
 *   built entirely from scale notes.
 */
export function chordsForScale(rootPc, scaleIntervals, chordLibrary) {
  const sorted = [...scaleIntervals].sort((a, b) => a - b);
  const scalePcs = pcSet(rootPc, sorted);
  const find = (intervals) => chordLibrary.find((c) => sameSet(c.intervals, intervals));
  const diatonic = [];
  if (sorted.length === 7) {
    sorted.forEach((iv, degree) => {
      const stack = (steps) => steps.map((k) => mod12(sorted[(degree + k) % 7] - iv)).sort((a, b) => a - b);
      diatonic.push({
        degree, interval: iv, root: mod12(rootPc + iv),
        triad: find(stack([0, 2, 4])), seventh: find(stack([0, 2, 4, 6])),
      });
    });
  }
  const chordScale = chordScaleFor(sorted, chordLibrary);
  const others = chordScale ? [] : chordLibrary
    .filter((chord) => chord.intervals.length >= 3 && isSubset(pcSet(rootPc, chord.intervals), scalePcs))
    .map((chord) => ({ root: rootPc, interval: 0, chord }));
  return { diatonic, chordScale, others };
}
