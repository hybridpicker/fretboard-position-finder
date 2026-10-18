// Compact chord-box diagrams for voicing cards.

export function chordDiagram(shape, stringCount, { showFingers = true } = {}) {
  const frets = shape.frets;
  const fretted = frets.filter((f) => f > 0);
  const maxF = fretted.length ? Math.max(...fretted) : 0;
  const minF = fretted.length ? Math.min(...fretted) : 0;
  const rows = Math.max(4, maxF - minF + 1);
  const startFret = maxF <= rows ? 1 : minF;
  const sx = 16;
  const sy = 19;
  const left = 22;
  const top = 26;
  const width = left + sx * (stringCount - 1) + 16;
  const height = top + sy * rows + 12;
  const x = (s) => left + s * sx;
  const y = (row) => top + row * sy;
  const out = [`<svg class="cd" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">`];

  if (startFret === 1) {
    out.push(`<rect class="cd-nut" x="${x(0) - 1}" y="${top - 4}" width="${sx * (stringCount - 1) + 2}" height="4" rx="1"/>`);
  } else {
    out.push(`<text class="cd-start" x="${left - 7}" y="${y(0.5)}" text-anchor="end" dominant-baseline="central">${startFret}</text>`);
  }
  for (let r = 0; r <= rows; r++) out.push(`<line class="cd-fret" x1="${x(0)}" y1="${y(r)}" x2="${x(stringCount - 1)}" y2="${y(r)}"/>`);
  for (let s = 0; s < stringCount; s++) out.push(`<line class="cd-string" x1="${x(s)}" y1="${top}" x2="${x(s)}" y2="${y(rows)}"/>`);

  frets.forEach((f, s) => {
    if (f < 0) out.push(`<text class="cd-mark" x="${x(s)}" y="${top - 11}" text-anchor="middle" dominant-baseline="central">×</text>`);
    else if (f === 0) out.push(`<circle class="cd-open" cx="${x(s)}" cy="${top - 11}" r="4"/>`);
  });

  (shape.barres || []).forEach((b) => {
    const row = b.fret - startFret + 0.5;
    out.push(`<rect class="cd-barre" x="${x(b.from) - 7}" y="${y(row) - 7}" width="${x(b.to) - x(b.from) + 14}" height="14" rx="7"/>`);
  });

  frets.forEach((f, s) => {
    if (f <= 0) return;
    const row = f - startFret + 0.5;
    const isRoot = shape.rootStrings?.includes(s);
    out.push(`<circle class="cd-dot ${isRoot ? 'root' : ''}" cx="${x(s)}" cy="${y(row)}" r="7"/>`);
    const finger = shape.fingers?.[s];
    if (showFingers && finger) out.push(`<text class="cd-finger" x="${x(s)}" y="${y(row) + 0.5}" text-anchor="middle" dominant-baseline="central">${finger}</text>`);
  });
  out.push('</svg>');
  return out.join('');
}
