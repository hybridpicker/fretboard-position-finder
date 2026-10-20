// Fret grids for chord voicings and scale positions. Chord and position diagrams are vertical (strings
// top to bottom with the low string on the left, nut on top); the whole-neck overview is horizontal (high
// string on top, nut on the left). One geometry feeds two backends: inline SVG for the song view and the
// vector PDF writer for printable sheets. Pure functions, no DOM.

/**
 * Lay out a grid.
 * strings: string count. from/to: first and last fret (from >= 1).
 * notes: [{ string, fret, text, filled }] (fret 0 = open string, drawn before the nut).
 * mutes: string indices drawn as ×. barres: [{ fret, from, to }] (string indices).
 * fretNumbers: 'start' (number beside the first fret when it is not fret 1) or 'neck' (3, 5, 7, 9, 12 …).
 * sy: string spacing; sx: fret length; vertical: frets run downwards.
 * Returns { width, height, items } with items of type line / circle / text in grid units (y down).
 */
export function fretGrid({ strings, from = 1, to = 5, notes = [], mutes = [], barres = [], fretNumbers = 'start', vertical = false, sy = 12, sx = sy * (vertical ? 1.45 : 1.75) }) {
  const items = [];
  const r = sy * 0.42;
  const head = sy * 1.25; // room before the nut for open-string circles and mute marks
  const side = r + 1;
  const offset = vertical ? sy * 1.2 : 0; // vertical: start-fret numbers sit left of the grid
  const frets = to - from + 1;
  const end = head + frets * sx;
  const span = (strings - 1) * sy;
  const across = (s) => offset + side + (vertical ? s : strings - 1 - s) * sy;
  const along = (fret) => (fret === 0 ? head - sy * 0.62 : head + (fret - from + 0.5) * sx);
  const P = (a, c) => (vertical ? { x: c, y: a } : { x: a, y: c });
  const line = (a1, c1, a2, c2, width, color, cap) => {
    const p1 = P(a1, c1);
    const p2 = P(a2, c2);
    items.push({ type: 'line', x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y, width, color, ...(cap ? { cap } : {}) });
  };
  const text = (a, c, value, size, extra = {}) => {
    const p = P(a, c);
    items.push({ type: 'text', x: p.x, y: p.y + size * 0.36, text: value, size, align: 'center', ...extra });
  };

  for (let k = 0; k <= frets; k++) {
    const nut = k === 0 && from === 1;
    line(head + k * sx, across(0), head + k * sx, across(strings - 1), nut ? sy * 0.28 : 0.6, nut ? 'ink' : 'fret');
  }
  for (let s = 0; s < strings; s++) line(head, across(s), end, across(s), 0.6, 'ink');

  const numberSize = sy * 0.72;
  const label = (fret) => {
    if (vertical) items.push({ type: 'text', x: offset - sy * 0.3, y: along(fret) + numberSize * 0.36, text: String(fret), size: numberSize, align: 'right', color: 'muted' });
    else text(along(fret), across(0) + sy * 1.05, String(fret), numberSize, { color: 'muted' });
  };
  if (fretNumbers === 'start' && from > 1) label(from);
  else if (fretNumbers === 'neck') {
    for (let f = from; f <= to; f++) if ([3, 5, 7, 9, 12, 15, 17, 19, 21, 24].includes(f)) label(f);
  }

  mutes.forEach((s) => text(along(0), across(s), '×', sy * 0.8, { color: 'ink' }));
  barres.forEach((b) => {
    if (b.fret < from || b.fret > to) return;
    line(along(b.fret), across(b.from), along(b.fret), across(b.to), r * 1.1, 'ink', 'round');
  });
  notes.forEach((n) => {
    if (n.fret !== 0 && (n.fret < from || n.fret > to)) return;
    const p = P(along(n.fret), across(n.string));
    items.push({ type: 'circle', cx: p.x, cy: p.y, r: n.fret === 0 ? r * 0.85 : r, fill: n.filled ? 'ink' : 'paper', stroke: 'ink', width: 0.8 });
    if (n.text) {
      const size = sy * (String(n.text).length > 2 ? 0.44 : 0.54);
      text(along(n.fret), across(n.string), String(n.text), size, { bold: true, color: n.filled ? 'paper' : 'ink' });
    }
  });
  const acrossEnd = offset + side * 2 + span;
  if (vertical) return { width: acrossEnd + 1, height: end + 2, items };
  const labels = fretNumbers === 'neck' || (fretNumbers === 'start' && from > 1) ? sy * 1.35 : sy * 0.3;
  return { width: end + 2, height: acrossEnd + labels, items };
}

/**
 * Pick the fret window for a chord voicing: from the nut when it fits, otherwise from the lowest fretted note.
 * `columns` is the number of frets shown (5 by default); wider voicings widen the grid.
 */
export function chordWindow(frets, columns = 5) {
  const fretted = frets.filter((f) => f > 0);
  const lo = fretted.length ? Math.min(...fretted) : 1;
  const hi = fretted.length ? Math.max(...fretted) : 1;
  const width = Math.max(columns, hi - lo + 1);
  if (hi <= width) return { from: 1, to: width };
  return { from: lo, to: lo + width - 1 };
}

/** Vertical chord box for one voicing (labels: per-string text, roots: string indices that hold the root). */
export function chordGrid(shape, strings, { labels = [], roots = [], columns = 5, sy = 12 } = {}) {
  const { from, to } = chordWindow(shape.frets, columns);
  const notes = [];
  const mutes = [];
  shape.frets.forEach((f, s) => {
    if (f < 0) mutes.push(s);
    else notes.push({ string: s, fret: f, text: labels[s] || '', filled: roots.includes(s) });
  });
  return fretGrid({ strings, from, to, notes, mutes, barres: shape.barres || [], sy, vertical: true });
}

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const SVG_COLORS = { ink: 'var(--ink)', paper: 'var(--surface)', fret: 'var(--fret)', muted: 'var(--muted)' };

/** Render grid items as an inline SVG (theme-aware colours). */
export function gridSvg(grid, { className = 'tg' } = {}) {
  const out = [`<svg class="${className}" viewBox="0 0 ${grid.width.toFixed(1)} ${grid.height.toFixed(1)}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">`];
  for (const it of grid.items) {
    if (it.type === 'line') {
      out.push(`<line x1="${it.x1.toFixed(1)}" y1="${it.y1.toFixed(1)}" x2="${it.x2.toFixed(1)}" y2="${it.y2.toFixed(1)}" stroke="${SVG_COLORS[it.color]}" stroke-width="${it.width.toFixed(2)}"${it.cap ? ` stroke-linecap="${it.cap}"` : ''}/>`);
    } else if (it.type === 'circle') {
      out.push(`<circle cx="${it.cx.toFixed(1)}" cy="${it.cy.toFixed(1)}" r="${it.r.toFixed(1)}" fill="${SVG_COLORS[it.fill]}" stroke="${SVG_COLORS[it.stroke]}" stroke-width="${it.width}"/>`);
    } else if (it.type === 'text') {
      const anchor = it.align === 'center' ? 'middle' : it.align === 'right' ? 'end' : 'start';
      out.push(`<text x="${it.x.toFixed(1)}" y="${it.y.toFixed(1)}" font-size="${it.size.toFixed(1)}" text-anchor="${anchor}" fill="${SVG_COLORS[it.color]}"${it.bold ? ' font-weight="600"' : ''}>${esc(it.text)}</text>`);
    }
  }
  out.push('</svg>');
  return out.join('');
}
