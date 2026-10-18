// Guitar Positions Studio — UI state, rendering and interaction.
import {
  ROOT_NAMES, NOTE_SHARP, NOTE_FLAT, TUNINGS, getTuning, mod12, pretty, buildLibrary, spellCollection,
  intervalRole, neckNotes, scalePositions, findChordShapes, voicingTemplateShapes, assignFingers,
  identifyChords, identifyScales, midiName,
} from './theory.js';
import { renderFretboard, pulseNote } from './fretboard.js';
import { chordDiagram } from './diagram.js';
import { playNote, strum, playSequence, stopSequence, isSequencePlaying } from './audio.js';

const $ = (sel) => document.querySelector(sel);
const readJSON = (id) => { try { return JSON.parse(document.getElementById(id)?.textContent || 'null'); } catch { return null; } };
const store = {
  get(key, fallback) { try { const v = localStorage.getItem(`gp-${key}`); return v === null ? fallback : JSON.parse(v); } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(`gp-${key}`, JSON.stringify(value)); } catch { /* storage unavailable */ } },
};

const library = buildLibrary(readJSON('catalog-data'));
const MODE_NAMES = { scale: 'Scale', arpeggio: 'Arpeggio', chord: 'Chord', identify: 'Chord Namer' };
const ROLE_NAMES = { root: 'Root', third: '3rd', fifth: '5th', seventh: '7th', tension: 'Other' };

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const defaults = {
  mode: 'scale', root: 0,
  scaleKey: (library.scales.find((s) => s.intervals.join() === '0,2,4,5,7,9,11') || library.scales[0])?.key,
  arpKey: (library.arpeggios.find((a) => a.intervals.join() === '0,4,7,11') || library.arpeggios[0])?.key,
  chordKey: 'major', position: 1, system: 'box', labels: 'fingers', source: 'finder', bass: 'any',
  neck: 'all', vsystem: 'all', selected: 0,
};
const state = {
  ...defaults,
  tuning: store.get('tuning', 'standard'),
  frets: store.get('frets', 15),
  orientation: store.get('orientation', 'auto'),
  lefty: store.get('lefty', false),
  spelling: store.get('spelling', 'auto'),
  sound: store.get('sound', true),
  bpm: store.get('bpm', 110),
  identify: [],
};

function readUrl() {
  const p = new URLSearchParams(location.search);
  const legacy = readJSON('legacy-state') || {};
  if (legacy.mode) state.mode = legacy.mode;
  if (Number.isInteger(legacy.root)) state.root = legacy.root;
  if (legacy.typeId) {
    const list = legacy.mode === 'arpeggio' ? library.arpeggios : library.scales;
    const hit = list.find((x) => x.id === legacy.typeId);
    if (hit) state[legacy.mode === 'arpeggio' ? 'arpKey' : 'scaleKey'] = hit.key;
  }
  if (legacy.chordName) {
    const hit = library.chords.find((c) => c.dbName === legacy.chordName || c.name === legacy.chordName);
    if (hit) { state.chordKey = hit.key; state.source = 'vsystem'; }
    if (legacy.system) state.vsystem = legacy.system;
  }
  if (legacy.position) state.position = legacy.position;

  if (MODE_NAMES[p.get('mode')]) state.mode = p.get('mode');
  const r = p.get('root');
  if (r !== null && /^[A-Ga-g](#|b)?$/.test(r)) state.root = pcOfName(r);
  const type = p.get('type');
  if (type) {
    if (state.mode === 'scale' && library.scales.some((s) => s.key === type)) state.scaleKey = type;
    if (state.mode === 'arpeggio' && library.arpeggios.some((s) => s.key === type)) state.arpKey = type;
    if (state.mode === 'chord' && library.chords.some((s) => s.key === type)) state.chordKey = type;
  }
  if (p.get('pos') !== null) state.position = Math.max(0, parseInt(p.get('pos'), 10) || 0);
  if (p.get('sys') === 'nps' || p.get('sys') === 'box') state.system = p.get('sys');
  if (p.get('shape')) {
    state.identify = p.get('shape').split(',').map((v) => (v === 'x' ? -1 : parseInt(v, 10)));
  }
}

function pcOfName(name) {
  const base = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 }[name[0].toUpperCase()];
  return mod12(base + (name.includes('#') ? 1 : 0) - (/^.b/.test(name) ? 1 : 0));
}

function writeUrl() {
  const p = new URLSearchParams();
  p.set('mode', state.mode);
  if (state.mode !== 'identify') {
    p.set('root', ROOT_NAMES[state.root]);
    p.set('type', currentType().key);
  }
  if (state.mode === 'scale' || state.mode === 'arpeggio') {
    p.set('pos', String(state.position));
    if (state.mode === 'scale') p.set('sys', state.system);
  }
  if (state.mode === 'identify' && state.identify.some((f) => f >= 0)) {
    p.set('shape', state.identify.map((f) => (f < 0 ? 'x' : f)).join(','));
  }
  history.replaceState(null, '', `${location.pathname}?${p.toString()}`);
}

const tuning = () => getTuning(state.tuning);
function currentType() {
  if (state.mode === 'arpeggio') return library.arpeggios.find((a) => a.key === state.arpKey) || library.arpeggios[0];
  if (state.mode === 'chord') return library.chords.find((c) => c.key === state.chordKey) || library.chords[0];
  return library.scales.find((s) => s.key === state.scaleKey) || library.scales[0];
}
function setType(key) {
  if (state.mode === 'arpeggio') state.arpKey = key;
  else if (state.mode === 'chord') state.chordKey = key;
  else state.scaleKey = key;
}

function rootName(pc = state.root) {
  if (state.spelling === 'sharp') return NOTE_SHARP[pc];
  if (state.spelling === 'flat') return NOTE_FLAT[pc];
  return ROOT_NAMES[pc];
}

function spelling(intervals, kind) {
  const spelled = spellCollection(rootName(), intervals, kind);
  if (state.spelling !== 'auto') {
    const table = state.spelling === 'sharp' ? NOTE_SHARP : NOTE_FLAT;
    intervals.forEach((iv) => { spelled.names[iv] = table[mod12(state.root + iv)]; });
  }
  return spelled;
}

function orientation() {
  if (state.orientation !== 'auto') return state.orientation;
  return window.matchMedia('(max-width: 640px) and (orientation: portrait)').matches ? 'vertical' : 'horizontal';
}

// ---------------------------------------------------------------------------
// Derived data
// ---------------------------------------------------------------------------
let view = { notes: [], sequence: [] };

function computeScaleView() {
  const type = currentType();
  const kind = state.mode === 'arpeggio' ? 'chord' : 'scale';
  const { labels, names } = spelling(type.intervals, kind);
  const t = tuning();
  const system = state.mode === 'scale' && type.intervals.length >= 6 ? state.system : 'box';
  const positions = scalePositions(state.root, type.intervals, t, { system });
  if (state.position > positions.length) state.position = positions.length ? 1 : 0;
  const active = state.position > 0 ? positions[state.position - 1] : null;
  const maxFret = Math.max(state.frets, active ? active.maxFret + 1 : 0);
  const activeKeys = new Set(active ? active.notes.map((n) => `${n.string}:${n.fret}`) : []);
  const fingerOf = {};
  active?.notes.forEach((n) => { fingerOf[`${n.string}:${n.fret}`] = n.finger; });

  const label = (n) => {
    if (state.labels === 'notes') return pretty(names[n.interval]);
    if (state.labels === 'intervals') return pretty(labels[n.interval]);
    const f = fingerOf[`${n.string}:${n.fret}`];
    return f === undefined ? pretty(labels[n.interval]) : f === 0 ? 'O' : String(f);
  };
  const notes = neckNotes(state.root, type.intervals, t, maxFret).map((n) => ({
    ...n,
    role: intervalRole(n.interval, labels),
    state: !active || activeKeys.has(`${n.string}:${n.fret}`) ? 'active' : 'ghost',
    label: !active && state.labels === 'fingers' ? pretty(labels[n.interval]) : label(n),
  }));
  // Play order: the active position ascending (and back down), or two octaves from the lowest root
  let seqNotes;
  if (active) {
    const up = [...active.notes].sort((a, b) => a.midi - b.midi || a.string - b.string);
    seqNotes = [...up, ...up.slice(0, -1).reverse()];
  } else {
    const lowRoot = notes.filter((n) => n.interval === 0).sort((a, b) => a.midi - b.midi)[0];
    const pitches = [];
    for (let m = lowRoot.midi; m <= lowRoot.midi + 12; m++) if (type.intervals.includes(mod12(m - state.root))) pitches.push(m);
    seqNotes = pitches.map((m) => notes.find((n) => n.midi === m));
  }
  const sequence = seqNotes.map((sn) => ({ midi: sn.midi, index: notes.findIndex((n) => n.string === sn.string && n.fret === sn.fret) }));
  return { type, labels, names, positions, active, notes, sequence, maxFret, system, barres: [], mutes: [] };
}

function filterNeck(shapes) {
  if (state.neck === 'open') return shapes.filter((s) => s.minFret <= 3 && s.frets.some((f) => f === 0) || s.minFret <= 2);
  if (state.neck === 'mid') return shapes.filter((s) => s.minFret >= 4 && s.minFret <= 9);
  if (state.neck === 'high') return shapes.filter((s) => s.minFret >= 10);
  return shapes;
}

function computeChordView() {
  const type = currentType();
  const { labels, names } = spelling(type.intervals, 'chord');
  const t = tuning();
  const bass = state.bass === 'any' ? null : parseInt(state.bass, 10);
  let shapes;
  if (state.source === 'vsystem') {
    const templates = type.voicings.filter((v) => state.vsystem === 'all' || v.system === state.vsystem);
    shapes = templates.flatMap((tpl) => voicingTemplateShapes(state.root, type.intervals, tpl, t, { maxFret: 17 }));
    if (bass !== null) shapes = shapes.filter((s) => s.bassInterval === bass);
    shapes.sort((a, b) => a.minFret - b.minFret);
  } else {
    shapes = findChordShapes(state.root, type.intervals, t, { maxFret: Math.max(15, state.frets), bass, limit: 400 });
  }
  shapes = filterNeck(shapes).slice(0, state.source === 'vsystem' ? 96 : 36);
  if (state.selected >= shapes.length) state.selected = 0;
  const shape = shapes[state.selected] || null;
  const maxFret = Math.max(state.frets, shape ? Math.max(...shape.frets) + 1 : 0);

  const shapeKeys = new Map();
  shape?.frets.forEach((f, s) => { if (f >= 0) shapeKeys.set(`${s}:${f}`, shape.fingers[s]); });
  const notes = neckNotes(state.root, type.intervals, t, maxFret).map((n) => {
    const key = `${n.string}:${n.fret}`;
    const inShape = shapeKeys.has(key);
    let lbl = pretty(labels[n.interval]);
    if (state.labels === 'notes') lbl = pretty(names[n.interval]);
    if (state.labels === 'fingers' && inShape) lbl = shapeKeys.get(key) ? String(shapeKeys.get(key)) : 'O';
    return { ...n, role: intervalRole(n.interval, labels), state: !shape || inShape ? 'active' : 'ghost', label: lbl };
  });
  const sequence = shape ? shape.frets.map((f, s) => (f < 0 ? null : notes.findIndex((n) => n.string === s && n.fret === f))).filter((i) => i !== null && i >= 0).map((i) => ({ midi: notes[i].midi, index: i })) : [];
  const mutes = shape ? shape.frets.map((f, s) => (f < 0 ? s : null)).filter((s) => s !== null) : [];
  const barres = shape ? shape.barres.map((b) => ({ ...b })) : [];
  return { type, labels, names, shapes, shape, notes, sequence, maxFret, barres, mutes };
}

function computeIdentifyView() {
  const t = tuning();
  if (state.identify.length !== t.midi.length) state.identify = new Array(t.midi.length).fill(-1);
  const frets = state.identify;
  const sounding = frets.map((f, s) => (f >= 0 ? { string: s, fret: f, midi: t.midi[s] + f } : null)).filter(Boolean);
  const pcs = sounding.map((n) => mod12(n.midi));
  const bassPc = sounding.length ? mod12(sounding[0].midi) : null;
  const names = state.spelling === 'flat' ? NOTE_FLAT : state.spelling === 'sharp' ? NOTE_SHARP : ROOT_NAMES;
  const chords = identifyChords(pcs, bassPc, library.chords, names);
  const best = chords[0] || null;
  const refRoot = best ? best.root : bassPc;
  const fingering = sounding.length ? assignFingers(frets) : null;
  const notes = sounding.map((n) => {
    const interval = refRoot === null ? 0 : mod12(n.midi - refRoot);
    let label = pretty(midiName(n.midi, names === NOTE_FLAT || names === ROOT_NAMES && [1, 3, 8, 10].includes(mod12(n.midi))));
    if (state.labels === 'fingers' && fingering) label = fingering.fingers[n.string] ? String(fingering.fingers[n.string]) : 'O';
    if (state.labels === 'intervals' && best) label = pretty(spellCollection(names[best.root], best.chord.intervals, 'chord').labels[interval] || '?');
    return { ...n, interval, role: best ? intervalRole(interval, spellCollection(names[best.root], best.chord.intervals, 'chord').labels) : 'tension', state: 'active', label };
  });
  const scales = identifyScales(pcs, library.scales, best ? best.root : bassPc);
  const mutes = frets.map((f, s) => (f < 0 ? s : null)).filter((s) => s !== null);
  return {
    notes, chords, best, scales, frets, fingering, mutes, sequence: notes.map((n, i) => ({ midi: n.midi, index: i })),
    maxFret: state.frets, barres: fingering?.barres || [],
  };
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------
function render() {
  stopPlayback();
  document.body.dataset.mode = state.mode;
  document.querySelectorAll('.modes button').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.mode === state.mode)));
  const isIdentify = state.mode === 'identify';
  const isChord = state.mode === 'chord';
  const isScaleLike = state.mode === 'scale' || state.mode === 'arpeggio';
  $('.selector').hidden = isIdentify;
  $('#controls').hidden = !isScaleLike && !isChord;
  $('#positionsBar').hidden = !isScaleLike;
  $('#systemSeg').hidden = state.mode !== 'scale';
  $('#finder').hidden = !isChord;
  $('#namer').hidden = !isIdentify;
  $('#tempoBox').hidden = isChord || isIdentify;

  if (isIdentify) view = computeIdentifyView();
  else if (isChord) view = computeChordView();
  else view = computeScaleView();

  renderKeys();
  renderHeadline();
  renderBoard();
  renderLegend();
  if (isScaleLike) renderPositions();
  if (isChord) renderFinder();
  if (isIdentify) renderNamer();
  syncSegs();
  writeUrl();
}

function renderKeys() {
  const host = $('#keyPicker');
  host.innerHTML = ROOT_NAMES.map((_, pc) => `<button role="radio" data-root="${pc}" aria-checked="${pc === state.root}">${pretty(rootName(pc))}</button>`).join('');
}

function renderHeadline() {
  if (state.mode === 'identify') {
    $('#eyebrow').textContent = 'Chord Namer';
    $('#title').textContent = view.best ? pretty(view.best.name) : 'Build a chord';
    document.title = `${view.best ? pretty(view.best.name) + ' — ' : ''}Chord Namer — Guitar Positions`;
    $('#chips').innerHTML = view.notes.map((n) => `<span class="chip role-${n.role}" data-midi="${n.midi}"><b>${pretty(midiName(n.midi, ROOT_NAMES[mod12(n.midi)].includes('b')))}</b><i>${view.best ? pretty(spellCollection(ROOT_NAMES[view.best.root], view.best.chord.intervals, 'chord').labels[n.interval] || '') : ''}</i></span>`).join('');
    $('#typeLabel').textContent = '';
    return;
  }
  const type = view.type;
  $('#eyebrow').textContent = MODE_NAMES[state.mode] + (state.mode === 'chord' ? ` · ${type.name}` : '');
  const title = state.mode === 'scale' ? `${rootName()} ${type.name}` : `${rootName()}${type.symbol || ' ' + type.name}`;
  $('#title').textContent = pretty(title);
  document.title = `${pretty(title)} — Guitar Positions`;
  $('#typeLabel').textContent = state.mode === 'scale' ? type.name : `${type.name}${type.symbol ? ` (${pretty(rootName() + type.symbol)})` : ''}`;
  $('#chips').innerHTML = type.intervals.map((iv) => `<button class="chip role-${intervalRole(iv, view.labels)}" data-midi="${tuning().midi[0] + mod12(state.root - tuning().midi[0]) + iv + 12}" title="Listen"><b>${pretty(view.names[iv])}</b><i>${pretty(view.labels[iv])}</i></button>`).join('');
}

function renderBoard() {
  const t = tuning();
  const o = orientation();
  const host = $('#fretboard');
  $('#boardScroll').classList.toggle('vertical', o === 'vertical');
  host.classList.toggle('interactive', state.mode === 'identify');
  const openNames = t.midi.map((m) => pretty(midiName(m, state.spelling === 'flat')));
  renderFretboard(host, {
    tuning: t, frets: view.maxFret, orientation: o, lefty: state.lefty, notes: view.notes,
    barres: view.barres || [], mutes: view.mutes || [], interactive: state.mode === 'identify', openLabels: openNames,
  });
  // Keep the active position in view on narrow screens
  const first = host.querySelector('.fb-note.state-active');
  if (first && (state.mode !== 'identify')) {
    const scroller = $('#boardScroll');
    const box = first.getBoundingClientRect();
    const sbox = scroller.getBoundingClientRect();
    if (o === 'horizontal' && scroller.scrollWidth > scroller.clientWidth && (box.left < sbox.left || box.right > sbox.right)) {
      scroller.scrollLeft += box.left - sbox.left - 60;
    }
  }
}

function renderLegend() {
  let roles;
  if (state.mode === 'identify') roles = view.best ? view.best.chord.intervals.map((iv) => intervalRole(iv)) : [];
  else roles = view.type.intervals.map((iv) => intervalRole(iv, view.labels));
  const uniq = ['root', 'third', 'fifth', 'seventh', 'tension'].filter((r) => roles.includes(r));
  let html = uniq.map((r) => `<span class="role-${r}">${ROLE_NAMES[r]}</span>`).join('');
  if (state.mode !== 'identify' && (view.active || view.shape)) html += '<span class="hint">Faded: same notes elsewhere on the neck</span>';
  if (state.labels === 'fingers' && state.mode !== 'identify') html += '<span class="muted">Numbers = fingers (1 index … 4 pinky, O open)</span>';
  $('#legend').innerHTML = html;
}

function renderPositions() {
  const host = $('#positionsBar');
  const items = [`<button class="pos-btn" data-pos="0" aria-pressed="${state.position === 0}">All<small>whole neck</small></button>`];
  view.positions.forEach((p) => {
    items.push(`<button class="pos-btn" data-pos="${p.index}" aria-pressed="${state.position === p.index}">${p.index}<small>fr ${p.minFret}–${p.maxFret}</small></button>`);
  });
  host.innerHTML = items.join('');
  const sys = $('#systemSeg');
  sys.querySelectorAll('button').forEach((b) => { b.disabled = view.type.intervals.length < 6 && b.dataset.system === 'nps'; });
}

function easiness(score, best, worst) {
  const span = Math.max(0.0001, worst - best);
  return Math.max(1, 5 - Math.round(((score - best) / span) * 4));
}

function renderFinder() {
  const type = view.type;
  const bassSeg = $('#bassSeg');
  const bassOptions = [['any', 'Any bass']].concat(type.intervals.map((iv) => [String(iv), pretty(view.labels[iv]) + ' in bass']));
  bassSeg.innerHTML = bassOptions.map(([v, l]) => `<button data-bass="${v}" aria-pressed="${state.bass === v}">${l}</button>`).join('');
  const hasDb = type.voicings.length > 0;
  $('#sourceSeg [data-source="vsystem"]').disabled = !hasDb;
  if (!hasDb && state.source === 'vsystem') state.source = 'finder';
  const vs = $('#vsystemSelect');
  vs.hidden = state.source !== 'vsystem';
  if (state.source === 'vsystem') {
    const systems = [...new Set(type.voicings.map((v) => v.system))];
    vs.innerHTML = ['<option value="all">All voicing systems</option>'].concat(systems.map((s) => `<option value="${s}" ${state.vsystem === s ? 'selected' : ''}>${s}</option>`)).join('');
  }
  const shapes = view.shapes;
  const scores = shapes.map((s) => s.score).filter((x) => x !== undefined);
  const best = Math.min(...scores);
  const worst = Math.max(...scores);
  $('#finderSummary').textContent = shapes.length
    ? (state.source === 'vsystem' ? `${shapes.length} voicings from the V-System library, every inversion.` : `${shapes.length} playable shapes, easiest first. Click one to see it on the neck and hear it.`)
    : 'No shapes match these filters.';
  const chordName = pretty(rootName() + (type.symbol || ''));
  $('#cards').innerHTML = shapes.length ? shapes.map((s, i) => {
    const rootStrings = s.frets.map((f, st) => (f >= 0 && mod12(tuning().midi[st] + f - state.root) === 0 ? st : null)).filter((x) => x !== null);
    const ease = s.score !== undefined ? easiness(s.score, best, worst) : null;
    const bassName = s.bassInterval ? `/${pretty(view.names[s.bassInterval])}` : '';
    const meta = [s.voicing, s.inversion, s.system && s.range ? `${s.system} · ${s.range}` : ''].filter(Boolean).join(' · ');
    return `<button class="card" data-shape="${i}" aria-pressed="${i === state.selected}">
      <span class="rank">${i + 1}</span>
      ${ease ? `<span class="easy" title="Ease ${ease}/5">${[1, 2, 3, 4, 5].map((k) => `<i class="${k <= ease ? 'on' : ''}"></i>`).join('')}</span>` : ''}
      ${chordDiagram({ ...s, rootStrings }, tuning().midi.length)}
      <b>${chordName}${bassName}</b>
      <span>${meta || '&nbsp;'}</span>
      <span class="frets">${s.frets.map((f) => (f < 0 ? 'x' : f)).join(' ')}</span>
    </button>`;
  }).join('') : '<div class="empty">Try another bass note or neck region.</div>';
}

function renderNamer() {
  const res = $('#namerResult');
  if (!view.notes.length) {
    res.innerHTML = '<div class="big">—</div><div class="sub">Tap the fretboard to place notes</div>';
  } else if (!view.best) {
    res.innerHTML = `<div class="big">?</div><div class="sub">${view.notes.length} note${view.notes.length > 1 ? 's' : ''} — no common chord name yet</div>`;
  } else {
    const fingerText = view.fingering ? view.frets.map((f, s) => (f < 0 ? 'x' : f === 0 ? 'o' : view.fingering.fingers[s])).join(' ') : 'needs more than four fingers';
    res.innerHTML = `<div class="big">${pretty(view.best.name)}</div>
      <div class="sub">${view.best.chord.name}${view.best.exact ? '' : ' (no 5th)'}</div>
      <div class="sub">Fingering: <b>${fingerText}</b></div>
      <button class="ghost-btn" data-open-chord="${view.best.chord.key}" data-open-root="${view.best.root}" style="margin-top:10px">Show all shapes</button>`;
  }
  $('#namerChords').innerHTML = view.chords.slice(1).map((c) => `<li><button class="${c.exact ? '' : 'partial'}" data-open-chord="${c.chord.key}" data-open-root="${c.root}">${pretty(c.name)}</button></li>`).join('') || '<li class="muted">—</li>';
  const names = ROOT_NAMES;
  $('#namerScales').innerHTML = view.scales.map((s) => `<li><button data-open-scale="${s.scale.key}" data-open-root="${s.root}">${pretty(names[s.root])} ${s.scale.name}</button></li>`).join('') || '<li class="muted">—</li>';
}

function syncSegs() {
  document.querySelectorAll('#systemSeg button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.system === state.system)));
  document.querySelectorAll('#labelSeg button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.labels === state.labels)));
  document.querySelectorAll('#sourceSeg button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.source === state.source)));
  document.querySelectorAll('#neckSeg button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.neck === state.neck)));
  $('#soundBtn').setAttribute('aria-pressed', String(state.sound));
}

// ---------------------------------------------------------------------------
// Type picker
// ---------------------------------------------------------------------------
function typeList() {
  if (state.mode === 'arpeggio') return library.arpeggios;
  if (state.mode === 'chord') return library.chords;
  return library.scales;
}

function renderTypeList(filter = '') {
  const list = typeList();
  const q = filter.trim().toLowerCase();
  const current = currentType().key;
  const groups = {};
  list.forEach((item) => {
    const hay = `${item.name} ${item.symbol || ''}`.toLowerCase();
    if (q && !hay.includes(q)) return;
    (groups[item.group] = groups[item.group] || []).push(item);
  });
  const html = Object.entries(groups).map(([group, items]) => `<div class="combo-group">${group}</div>` + items.map((item) => `
    <button class="combo-item" role="option" data-key="${item.key}" aria-selected="${item.key === current}">
      <span>${item.name}${item.symbol ? ` <small>${pretty(item.symbol)}</small>` : ''}</span>
      <small>${item.intervals.length} notes</small>
    </button>`).join('')).join('');
  $('#typeList').innerHTML = html || '<div class="combo-group">No match</div>';
}

function openTypePanel(open) {
  const panel = $('#typePanel');
  panel.hidden = !open;
  $('#typeBtn').setAttribute('aria-expanded', String(open));
  if (open) {
    $('#typeSearch').value = '';
    renderTypeList();
    $('#typeSearch').focus();
    panel.querySelector('[aria-selected="true"]')?.scrollIntoView({ block: 'center' });
  }
}

// ---------------------------------------------------------------------------
// Playback
// ---------------------------------------------------------------------------
function stopPlayback() {
  stopSequence();
  $('#playBtn')?.classList.remove('playing');
  pulseNote($('#fretboard'), null);
}

function play() {
  if (!state.sound) { toast('Sound is off — press M or the speaker icon'); return; }
  if (isSequencePlaying()) { stopPlayback(); return; }
  if (state.mode === 'chord' || state.mode === 'identify') {
    strum(view.sequence.map((s) => s.midi));
    view.sequence.forEach((s, i) => setTimeout(() => pulseNote($('#fretboard'), s.index), i * 35));
    return;
  }
  $('#playBtn').classList.add('playing');
  playSequence(view.sequence.map((s) => s.midi), state.bpm, (i) => pulseNote($('#fretboard'), view.sequence[i].index), () => stopPlayback());
}

let toastTimer;
function toast(msg) {
  const el = $('#toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 2200);
}

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------
function bind() {
  document.querySelector('.modes').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-mode]');
    if (!b) return;
    state.mode = b.dataset.mode;
    state.selected = 0;
    render();
  });
  $('#keyPicker').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-root]');
    if (!b) return;
    state.root = parseInt(b.dataset.root, 10);
    state.selected = 0;
    render();
  });
  $('#typeBtn').addEventListener('click', () => openTypePanel($('#typePanel').hidden));
  $('#typeSearch').addEventListener('input', (e) => renderTypeList(e.target.value));
  $('#typeSearch').addEventListener('keydown', (e) => {
    const items = [...document.querySelectorAll('#typeList .combo-item')];
    if (!items.length) return;
    let idx = items.findIndex((i) => i.classList.contains('active'));
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      idx = e.key === 'ArrowDown' ? Math.min(items.length - 1, idx + 1) : Math.max(0, idx - 1);
      items.forEach((i) => i.classList.remove('active'));
      items[idx].classList.add('active');
      items[idx].scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter') {
      (items[idx] || items[0]).click();
    } else if (e.key === 'Escape') {
      openTypePanel(false);
    }
  });
  $('#typeList').addEventListener('click', (e) => {
    const b = e.target.closest('.combo-item');
    if (!b) return;
    setType(b.dataset.key);
    state.selected = 0;
    state.position = Math.min(state.position, 1) || state.position;
    openTypePanel(false);
    render();
  });
  document.addEventListener('click', (e) => {
    if (!$('#typePanel').hidden && !e.target.closest('#typeCombo')) openTypePanel(false);
  });

  $('#positionsBar').addEventListener('click', (e) => {
    const b = e.target.closest('[data-pos]');
    if (!b) return;
    state.position = parseInt(b.dataset.pos, 10);
    render();
  });
  $('#systemSeg').addEventListener('click', (e) => {
    const b = e.target.closest('[data-system]');
    if (!b || b.disabled) return;
    state.system = b.dataset.system;
    render();
  });
  $('#labelSeg').addEventListener('click', (e) => {
    const b = e.target.closest('[data-labels]');
    if (!b) return;
    state.labels = b.dataset.labels;
    store.set('labels', state.labels);
    render();
  });
  $('#sourceSeg').addEventListener('click', (e) => {
    const b = e.target.closest('[data-source]');
    if (!b || b.disabled) return;
    state.source = b.dataset.source;
    state.selected = 0;
    render();
  });
  $('#bassSeg').addEventListener('click', (e) => {
    const b = e.target.closest('[data-bass]');
    if (!b) return;
    state.bass = b.dataset.bass;
    state.selected = 0;
    render();
  });
  $('#neckSeg').addEventListener('click', (e) => {
    const b = e.target.closest('[data-neck]');
    if (!b) return;
    state.neck = b.dataset.neck;
    state.selected = 0;
    render();
  });
  $('#vsystemSelect').addEventListener('change', (e) => { state.vsystem = e.target.value; state.selected = 0; render(); });
  $('#cards').addEventListener('click', (e) => {
    const b = e.target.closest('[data-shape]');
    if (!b) return;
    state.selected = parseInt(b.dataset.shape, 10);
    render();
    if (state.sound) play();
  });

  $('#fretboard').addEventListener('click', (e) => {
    const cell = e.target.closest('.fb-cell');
    if (cell && state.mode === 'identify') {
      const s = parseInt(cell.dataset.string, 10);
      const f = parseInt(cell.dataset.fret, 10);
      const cur = state.identify[s];
      state.identify[s] = cur === f ? -1 : f;
      if (state.sound && state.identify[s] >= 0) playNote(tuning().midi[s] + f);
      render();
      return;
    }
    const note = e.target.closest('.fb-note');
    if (note && state.sound) {
      const n = view.notes[parseInt(note.dataset.i, 10)];
      if (n) { playNote(n.midi); pulseNote($('#fretboard'), parseInt(note.dataset.i, 10)); }
    }
  });
  $('#chips').addEventListener('click', (e) => {
    const chip = e.target.closest('[data-midi]');
    if (chip && state.sound) playNote(parseInt(chip.dataset.midi, 10));
  });

  $('#namer').addEventListener('click', (e) => {
    const chordBtn = e.target.closest('[data-open-chord]');
    const scaleBtn = e.target.closest('[data-open-scale]');
    if (chordBtn) {
      state.mode = 'chord';
      state.chordKey = chordBtn.dataset.openChord;
      state.root = parseInt(chordBtn.dataset.openRoot, 10);
      state.selected = 0; state.bass = 'any'; state.source = 'finder';
      render();
    } else if (scaleBtn) {
      state.mode = 'scale';
      state.scaleKey = scaleBtn.dataset.openScale;
      state.root = parseInt(scaleBtn.dataset.openRoot, 10);
      state.position = 1;
      render();
    }
  });
  $('#namerClear').addEventListener('click', () => { state.identify = []; render(); });
  $('#namerPlay').addEventListener('click', () => play());

  $('#playBtn').addEventListener('click', play);
  $('#tempo').value = state.bpm;
  $('#tempoOut').textContent = state.bpm;
  $('#tempo').addEventListener('input', (e) => { state.bpm = parseInt(e.target.value, 10); $('#tempoOut').textContent = state.bpm; store.set('bpm', state.bpm); });
  $('#soundBtn').addEventListener('click', () => { state.sound = !state.sound; store.set('sound', state.sound); syncSegs(); if (!state.sound) stopPlayback(); });

  // Settings
  const settingsBtn = $('#settingsBtn');
  settingsBtn.addEventListener('click', () => {
    const open = $('#settings').hidden;
    $('#settings').hidden = !open;
    settingsBtn.setAttribute('aria-expanded', String(open));
  });
  $('#tuningSelect').innerHTML = TUNINGS.map((t) => `<option value="${t.id}">${t.name}</option>`).join('');
  $('#tuningSelect').value = state.tuning;
  $('#fretsSelect').value = String(state.frets);
  $('#orientationSelect').value = state.orientation;
  $('#leftyToggle').checked = state.lefty;
  $('#spellingSelect').value = state.spelling;
  $('#themeSelect').value = document.documentElement.dataset.theme || '';
  $('#tuningSelect').addEventListener('change', (e) => { state.tuning = e.target.value; state.identify = []; store.set('tuning', state.tuning); render(); });
  $('#fretsSelect').addEventListener('change', (e) => { state.frets = parseInt(e.target.value, 10); store.set('frets', state.frets); render(); });
  $('#orientationSelect').addEventListener('change', (e) => { state.orientation = e.target.value; store.set('orientation', state.orientation); render(); });
  $('#leftyToggle').addEventListener('change', (e) => { state.lefty = e.target.checked; store.set('lefty', state.lefty); render(); });
  $('#spellingSelect').addEventListener('change', (e) => { state.spelling = e.target.value; store.set('spelling', state.spelling); render(); });
  $('#themeSelect').addEventListener('change', (e) => {
    const v = e.target.value;
    if (v) document.documentElement.dataset.theme = v; else delete document.documentElement.dataset.theme;
    try { if (v) localStorage.setItem('gp-theme', v); else localStorage.removeItem('gp-theme'); } catch { /* ignore */ }
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.target.closest('input, select, textarea') || e.metaKey || e.ctrlKey || e.altKey) return;
    const modes = ['scale', 'arpeggio', 'chord', 'identify'];
    if (['1', '2', '3', '4'].includes(e.key)) { state.mode = modes[parseInt(e.key, 10) - 1]; state.selected = 0; render(); return; }
    if (e.key === ' ' && !e.target.closest('button')) { e.preventDefault(); play(); return; }
    if (e.key === 'm' || e.key === 'M') { $('#soundBtn').click(); return; }
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      if (state.mode === 'identify') return;
      e.preventDefault();
      state.root = mod12(state.root + (e.key === 'ArrowUp' ? 1 : -1));
      state.selected = 0;
      render();
      return;
    }
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      const dir = e.key === 'ArrowRight' ? 1 : -1;
      if (state.mode === 'scale' || state.mode === 'arpeggio') {
        const count = view.positions.length;
        state.position = (state.position + dir + count + 1) % (count + 1);
      } else if (state.mode === 'chord' && view.shapes.length) {
        state.selected = (state.selected + dir + view.shapes.length) % view.shapes.length;
        if (state.sound) setTimeout(play, 0);
      } else return;
      e.preventDefault();
      render();
    }
  });

  let resizeTimer;
  let lastOrientation = orientation();
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => { if (orientation() !== lastOrientation) { lastOrientation = orientation(); renderBoard(); } }, 150);
  });
}

state.labels = store.get('labels', 'fingers');
readUrl();
bind();
render();
