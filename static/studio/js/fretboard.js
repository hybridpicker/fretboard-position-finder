// SVG fretboard renderer (horizontal for desktop, vertical for phones, optional left-handed).

const INLAYS = [3, 5, 7, 9, 15, 17, 19, 21];
const DOUBLE_INLAYS = [12, 24];

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function fretScale(frets, length) {
  const real = (k) => 1 - Math.pow(2, -k / 12);
  const total = real(frets);
  // Blend real scale-length spacing with even spacing so high frets stay readable
  return (k) => length * (0.55 * (real(k) / total) + 0.45 * (k / frets));
}

export function geometry({ strings, frets, orientation }) {
  if (orientation === 'vertical') {
    const spacing = 44;
    const neck = Math.max(560, frets * 54);
    return {
      orientation, strings, frets, spacing,
      start: 62, // nut position along the neck
      neck,
      across0: 50, // room for fret numbers on the left
      width: 50 + 30 + spacing * (strings - 1),
      height: 62 + neck + 16,
    };
  }
  const spacing = 34;
  const neck = 1290;
  return {
    orientation, strings, frets, spacing,
    start: 58,
    neck,
    across0: 26,
    width: 58 + neck + 14,
    height: 26 + spacing * (strings - 1) + 40,
  };
}

/** Build a point mapper from (along, stringIndex) to SVG coordinates. */
function mapper(g, lefty) {
  const pos = fretScale(g.frets, g.neck);
  const along = (fret) => g.start + pos(fret);
  const noteAlong = (fret) => (fret === 0 ? g.start - (g.orientation === 'vertical' ? 30 : 30) : along(fret - 1) + (along(fret) - along(fret - 1)) * 0.55);
  const across = (s) => {
    if (g.orientation === 'vertical') {
      const idx = lefty ? g.strings - 1 - s : s; // low string on the left (right for lefties)
      return g.across0 + idx * g.spacing;
    }
    return g.across0 + (g.strings - 1 - s) * g.spacing; // high string on top, like tab
  };
  const pt = (a, c) => {
    if (g.orientation === 'vertical') return [c, a];
    return [lefty ? g.width - a : a, c];
  };
  return { along, noteAlong, across, pt };
}

/**
 * Render the fretboard into `host`.
 * notes: [{ string, fret, label, role, state ('active'|'ghost'|'hint'), finger, key }]
 */
export function renderFretboard(host, opts) {
  const { tuning, frets, orientation = 'horizontal', lefty = false, notes = [], barres = [], mutes = [], interactive = false, openLabels = [] } = opts;
  const n = tuning.midi.length;
  const g = geometry({ strings: n, frets, orientation });
  const { along, noteAlong, across, pt } = mapper(g, lefty);
  const vertical = orientation === 'vertical';
  const parts = [];

  parts.push(`<svg class="fb fb-${orientation}" viewBox="0 0 ${g.width} ${g.height}" role="img" aria-label="Guitar fretboard" xmlns="http://www.w3.org/2000/svg">`);
  // Fingerboard
  const a0 = g.start;
  const a1 = along(g.frets) + 2;
  const c0 = across(0);
  const c1 = across(n - 1);
  const cMin = Math.min(c0, c1) - g.spacing * 0.5;
  const cMax = Math.max(c0, c1) + g.spacing * 0.5;
  const rect = (aStart, aEnd, cStart, cEnd, attrs) => {
    const [x1, y1] = pt(aStart, cStart);
    const [x2, y2] = pt(aEnd, cEnd);
    return `<rect x="${Math.min(x1, x2)}" y="${Math.min(y1, y2)}" width="${Math.abs(x2 - x1)}" height="${Math.abs(y2 - y1)}" ${attrs}/>`;
  };
  parts.push(rect(a0, a1, cMin, cMax, 'class="fb-wood"'));

  // Inlays
  const inlayC = (cMin + cMax) / 2;
  for (let f = 1; f <= g.frets; f++) {
    const mid = (along(f - 1) + along(f)) / 2;
    if (INLAYS.includes(f)) {
      const [x, y] = pt(mid, inlayC);
      parts.push(`<circle class="fb-inlay" cx="${x}" cy="${y}" r="4.5"/>`);
    } else if (DOUBLE_INLAYS.includes(f)) {
      const off = g.spacing * Math.min(1.5, (n - 1) / 3);
      for (const c of [inlayC - off, inlayC + off]) {
        const [x, y] = pt(mid, c);
        parts.push(`<circle class="fb-inlay" cx="${x}" cy="${y}" r="4.5"/>`);
      }
    }
  }

  // Frets and nut
  for (let f = 1; f <= g.frets; f++) {
    parts.push(rect(along(f) - 0.75, along(f) + 0.75, cMin, cMax, 'class="fb-fret"'));
  }
  parts.push(rect(a0 - 3, a0 + 1, cMin, cMax, 'class="fb-nut"'));

  // Strings (thicker for lower strings)
  for (let s = 0; s < n; s++) {
    const width = 0.7 + (n - 1 - s) * (0.9 / Math.max(1, n - 1));
    const [x1, y1] = pt(a0 - 40, across(s));
    const [x2, y2] = pt(a1, across(s));
    parts.push(`<line class="fb-string" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke-width="${width.toFixed(2)}"/>`);
  }

  // Fret numbers
  for (let f = 1; f <= g.frets; f++) {
    const mid = (along(f - 1) + along(f)) / 2;
    const [x, y] = vertical ? pt(mid, cMin - 14) : pt(mid, cMax + 22);
    const strong = INLAYS.includes(f) || DOUBLE_INLAYS.includes(f);
    parts.push(`<text class="fb-fretnum ${strong ? 'strong' : ''}" x="${x}" y="${y}" ${vertical ? 'text-anchor="end" dominant-baseline="middle"' : 'text-anchor="middle"'}>${f}</text>`);
  }

  // Open-string labels
  openLabels.forEach((label, s) => {
    const [x, y] = pt(g.start - (vertical ? 52 : 50), across(s));
    parts.push(`<text class="fb-openlabel" x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central">${esc(label)}</text>`);
  });

  // Muted strings
  mutes.forEach((s) => {
    const [x, y] = pt(g.start - 30, across(s));
    parts.push(`<text class="fb-mute" x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central">×</text>`);
  });

  // Barres
  barres.forEach((b) => {
    const a = noteAlong(b.fret);
    const ca = across(b.from);
    const cb = across(b.to);
    const lo = Math.min(ca, cb) - 13;
    const hi = Math.max(ca, cb) + 13;
    parts.push(rect(a - 13, a + 13, lo, hi, 'class="fb-barre" rx="13"'));
  });

  // Click targets for building shapes
  if (interactive) {
    for (let s = 0; s < n; s++) {
      for (let f = 0; f <= g.frets; f++) {
        const aStart = f === 0 ? g.start - 46 : along(f - 1);
        const aEnd = f === 0 ? g.start : along(f);
        parts.push(rect(aStart, aEnd, across(s) - g.spacing / 2, across(s) + g.spacing / 2, `class="fb-cell" data-string="${s}" data-fret="${f}"`));
      }
    }
  }

  // Notes
  notes.forEach((note, i) => {
    const [x, y] = pt(noteAlong(note.fret), across(note.string));
    const r = note.state === 'ghost' ? 5 : 12;
    const cls = ['fb-note', `role-${note.role || 'tension'}`, `state-${note.state || 'active'}`];
    if (note.fret === 0) cls.push('open');
    parts.push(`<g class="${cls.join(' ')}" data-i="${i}" transform="translate(${x.toFixed(1)} ${y.toFixed(1)})" ${interactive ? '' : 'tabindex="-1"'}>`);
    parts.push(`<circle r="${r}"/>`);
    if (note.label !== undefined && note.label !== '' && note.state !== 'ghost') {
      const small = String(note.label).length > 2;
      parts.push(`<text class="${small ? 'small' : ''}" text-anchor="middle" dominant-baseline="central">${esc(note.label)}</text>`);
    }
    parts.push('</g>');
  });

  parts.push('</svg>');
  host.innerHTML = parts.join('');
  return g;
}

/** Highlight one rendered note (used while playing a sequence). */
export function pulseNote(host, index) {
  host.querySelectorAll('.fb-note.playing').forEach((el) => el.classList.remove('playing'));
  if (index === null || index === undefined) return;
  const el = host.querySelector(`.fb-note[data-i="${index}"]`);
  if (el) el.classList.add('playing');
}
