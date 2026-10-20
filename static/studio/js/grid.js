// Horizontal fret grids in the classic Ted Greene style: strings run left to right with the high string
// on top, the nut (or a start-fret number) on the left. One geometry feeds two backends: inline SVG for
// the song view and the vector PDF writer for printable sheets. Pure functions, no DOM.

/**
 * Lay out a grid.
 * strings: string count. from/to: first and last fret column (from >= 1).
 * notes: [{ string, fret, text, filled }] (fret 0 = open string, drawn left of the nut).
 * mutes: string indices drawn as ×. barres: [{ fret, from, to }] (string indices).
 * fretNumbers: 'start' (number under the first column when it is not fret 1) or 'neck' (3, 5, 7, 9, 12 …).
 * sy: string spacing; sx: fret width (defaults to 1.75 × sy).
 * Returns { width, height, items } with items of type line / circle / text in grid units (y down).
 */
export function fretGrid({ strings, from = 1, to = 5, notes = [], mutes = [], barres = [], fretNumbers = 'start', sy = 12, sx = sy * 1.75 }) {
  const items = [];
  const r = sy * 0.42;
  const left = sy * 1.25; // room for open-string circles and mute marks
  const top = r + 1;
  const columns = to - from + 1;
  const right = left + columns * sx;
  const bottom = top + (strings - 1) * sy;
  const y = (s) => top + (strings - 1 - s) * sy;
  const cx = (fret) => (fret === 0 ? left - sy * 0.62 : left + (fret - from + 0.5) * sx);

  for (let k = 0; k <= columns; k++) {
    const x = left + k * sx;
    items.push({ type: 'line', x1: x, y1: top, x2: x, y2: bottom, width: k === 0 && from === 1 ? sy * 0.28 : 0.6, color: from === 1 && k === 0 ? 'ink' : 'fret' });
  }
  for (let s = 0; s < strings; s++) items.push({ type: 'line', x1: left, y1: y(s), x2: right, y2: y(s), width: 0.6, color: 'ink' });

  const labelY = bottom + sy * 1.3;
  if (fretNumbers === 'start' && from > 1) {
    items.push({ type: 'text', x: cx(from), y: labelY, text: String(from), size: sy * 0.72, align: 'center', color: 'muted' });
  } else if (fretNumbers === 'neck') {
    for (let f = from; f <= to; f++) {
      if ([3, 5, 7, 9, 12, 15, 17, 19, 21, 24].includes(f)) items.push({ type: 'text', x: cx(f), y: labelY, text: String(f), size: sy * 0.72, align: 'center', color: 'muted' });
    }
  }

  mutes.forEach((s) => items.push({ type: 'text', x: cx(0), y: y(s) + sy * 0.26, text: '×', size: sy * 0.8, align: 'center', color: 'ink' }));
  barres.forEach((b) => {
    if (b.fret < from || b.fret > to) return;
    items.push({ type: 'line', x1: cx(b.fret), y1: y(b.from), x2: cx(b.fret), y2: y(b.to), width: r * 1.1, color: 'ink', cap: 'round' });
  });
  notes.forEach((n) => {
    if (n.fret !== 0 && (n.fret < from || n.fret > to)) return;
    const radius = n.fret === 0 ? r * 0.85 : r;
    items.push({ type: 'circle', cx: cx(n.fret), cy: y(n.string), r: radius, fill: n.filled ? 'ink' : 'paper', stroke: 'ink', width: 0.8 });
    if (n.text) {
      const size = sy * (String(n.text).length > 2 ? 0.44 : 0.54);
      items.push({ type: 'text', x: cx(n.fret), y: y(n.string) + size * 0.36, text: String(n.text), size, bold: true, align: 'center', color: n.filled ? 'paper' : 'ink' });
    }
  });
  return { width: right + 2, height: labelY + sy * 0.3, items };
}

/**
 * Pick the fret window for a chord voicing: from the nut when it fits, otherwise from the lowest fretted note.
 * `columns` is the grid width (Ted Greene grids: up to 7 frets); wider voicings widen the grid.
 */
export function chordWindow(frets, columns = 5) {
  const fretted = frets.filter((f) => f > 0);
  const lo = fretted.length ? Math.min(...fretted) : 1;
  const hi = fretted.length ? Math.max(...fretted) : 1;
  const width = Math.max(columns, hi - lo + 1);
  if (hi <= width) return { from: 1, to: width };
  return { from: lo, to: lo + width - 1 };
}

/** Grid items for one chord voicing (labels: per-string text, roots: string indices that hold the root). */
export function chordGrid(shape, strings, { labels = [], roots = [], columns = 5, sy = 12 } = {}) {
  const { from, to } = chordWindow(shape.frets, columns);
  const notes = [];
  const mutes = [];
  shape.frets.forEach((f, s) => {
    if (f < 0) mutes.push(s);
    else notes.push({ string: s, fret: f, text: labels[s] || '', filled: roots.includes(s) });
  });
  return fretGrid({ strings, from, to, notes, mutes, barres: shape.barres || [], sy });
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
