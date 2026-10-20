// Songs and exercises: an ordered list of chord voicings with optional section dividers.
// Stored only in this browser (localStorage) and shared as a readable link; no server storage.
// Pure helpers (no DOM) so they run under `node --test`.

const ROOTS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];
const ROOT_PC = { C: 0, 'C#': 1, Db: 1, D: 2, 'D#': 3, Eb: 3, E: 4, F: 5, 'F#': 6, Gb: 6, G: 7, 'G#': 8, Ab: 8, A: 9, 'A#': 10, Bb: 10, B: 11 };

export const newSongId = () => `s${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;

export function emptySong(title = 'Untitled song') {
  return { id: newSongId(), title, note: '', items: [] };
}

/**
 * Link encoding: t=title, n=note, c=items joined by ";" where a section is "#Name" and a chord is
 * "<root>.<chord key>.<frets>" with frets separated by "-" and "x" for muted strings,
 * e.g. c=#Verse;C.major-7.x-3-2-0-0-0;G.dominant-7.3-2-0-0-0-1
 */
export function encodeSong(song) {
  const items = song.items.map((it) => (it.section !== undefined
    ? `#${it.section.replace(/[;#]/g, ' ').trim()}`
    : `${ROOTS[it.root]}.${it.key}.${it.frets.map((f) => (f < 0 ? 'x' : f)).join('-')}`));
  const params = { t: song.title || 'Untitled song' };
  if (song.note) params.n = song.note;
  params.c = items.join(';');
  return params;
}

/** Parse link parameters back into a song (null when there is no song in the link). */
export function decodeSong(get) {
  const title = get('t');
  const list = get('c');
  if (title === null && list === null) return null;
  const items = [];
  for (const part of (list || '').split(';')) {
    if (!part) continue;
    if (part.startsWith('#')) { items.push({ section: part.slice(1).trim().slice(0, 60) }); continue; }
    const m = /^([A-G][#b]?)\.([a-z0-9-]+)\.([x0-9-]+)$/.exec(part);
    if (!m || !(m[1] in ROOT_PC)) continue;
    const frets = m[3].split('-').map((v) => (v === 'x' ? -1 : Math.min(30, parseInt(v, 10) || 0)));
    if (frets.length < 4 || frets.length > 8) continue;
    items.push({ root: ROOT_PC[m[1]], key: m[2], frets });
  }
  return { id: newSongId(), title: (title || 'Untitled song').slice(0, 120), note: (get('n') || '').slice(0, 2000), items };
}

/** Same content (ignoring ids), used to recognise a shared song that is already saved. */
export function sameSong(a, b) {
  const ea = encodeSong(a);
  const eb = encodeSong(b);
  return ea.t === eb.t && (ea.n || '') === (eb.n || '') && ea.c === eb.c;
}

/** Move the item at `index` by `dir` (-1 / +1); returns a new list. */
export function moveItem(items, index, dir) {
  const target = index + dir;
  if (target < 0 || target >= items.length) return items;
  const next = [...items];
  [next[index], next[target]] = [next[target], next[index]];
  return next;
}
