// Printable A4 sheets (black and white) for scales/arpeggios, chord shapes and songs.
// Input is plain data prepared by app.js; output is a PdfWriter ready for `.output()`.
import { PdfWriter, A4 } from './pdf.js';
import { fretGrid, chordGrid, chordWindow } from './grid.js';

const MARGIN = 42;
const WIDTH = A4.width - 2 * MARGIN;
const FOOTER = 40; // space kept free at the bottom of every page

function header(pdf, title, lines) {
  let y = MARGIN + 18;
  pdf.text(MARGIN, y, title, { size: 20, bold: true });
  y += 8;
  for (const line of lines.filter(Boolean)) {
    y += 14;
    pdf.text(MARGIN, y, line, { size: 9.5, gray: 0.3 });
  }
  pdf.line(MARGIN, y + 10, MARGIN + WIDTH, y + 10, { width: 0.5, gray: 0.7 });
  return y + 28;
}

function footer(pdf, link) {
  pdf.pages.forEach((ops, i) => {
    pdf.ops = ops;
    const y = A4.height - 26;
    pdf.text(MARGIN, y, 'Guitar Positions · fretboard.schoensgibl.com', { size: 7.5, gray: 0.45 });
    if (pdf.pages.length > 1) pdf.text(MARGIN + WIDTH, y, `${i + 1} / ${pdf.pages.length}`, { size: 7.5, gray: 0.45, align: 'right' });
    if (link && pdf.textWidth(link, 6.5) <= WIDTH) pdf.text(MARGIN, y + 10, link, { size: 6.5, gray: 0.45 });
  });
}

/** Break text into lines no wider than `width` at `size`. */
function wrap(pdf, text, size, width) {
  const out = [];
  for (const para of String(text || '').split(/\n/)) {
    let line = '';
    for (const word of para.split(/\s+/).filter(Boolean)) {
      const next = line ? `${line} ${word}` : word;
      if (line && pdf.textWidth(next, size) > width) { out.push(line); line = word; } else line = next;
    }
    out.push(line);
  }
  return out;
}

/**
 * Scale or arpeggio sheet: whole neck plus every position.
 * data: { title, lines, strings, link, neck: { frets, notes }, positions: [{ label, from, to, notes }] }
 */
export function scaleSheet(data) {
  const pdf = new PdfWriter({ title: data.title });
  let y = header(pdf, data.title, data.lines);
  const bottom = A4.height - MARGIN - FOOTER;

  // Whole neck across the full width
  pdf.text(MARGIN, y, 'Whole neck', { size: 10, bold: true });
  y += 8;
  const neckSy = data.strings > 6 ? 11 : 13;
  const neckCols = data.neck.frets;
  const neckSx = (WIDTH - neckSy * 1.25 - 2) / neckCols;
  const neck = fretGrid({ strings: data.strings, from: 1, to: neckCols, notes: data.neck.notes, fretNumbers: 'neck', sy: neckSy, sx: neckSx });
  pdf.drawGrid(neck, MARGIN, y);
  y += neck.height + 22;

  // Positions in a grid of two (or three) columns, scaled down when they would not fit
  const positions = data.positions;
  if (positions.length) {
    const cols = positions.length > 8 ? 3 : 2;
    const gap = 24;
    const colW = (WIDTH - gap * (cols - 1)) / cols;
    const frets = Math.max(...positions.map((p) => p.to - p.from + 1));
    const sy = data.strings > 6 ? 10.5 : 12;
    const sx = Math.min(sy * 2.4, (colW - sy * 1.25 - 2) / frets);
    const grids = positions.map((p) => fretGrid({ strings: data.strings, from: p.from, to: p.from + frets - 1, notes: p.notes, sy, sx }));
    const blockH = 16 + Math.max(...grids.map((g) => g.height)) + 14;
    const rows = Math.ceil(positions.length / cols);
    // Grow the diagrams into free space (up to 1.3×), shrink them when they would not fit
    let scale = Math.min(1.3, (bottom - y) / (rows * blockH), colW / Math.max(...grids.map((g) => g.width)));
    if (scale < 0.65) { pdf.addPage(); y = MARGIN + 10; scale = Math.min(1.3, (bottom - y) / (rows * blockH), colW / Math.max(...grids.map((g) => g.width))); }
    positions.forEach((p, i) => {
      const x = MARGIN + (i % cols) * (colW + gap);
      const top = y + Math.floor(i / cols) * blockH * scale;
      pdf.text(x, top, p.label, { size: 9.5 * Math.max(scale, 0.85), bold: true });
      pdf.drawGrid(grids[i], x, top + 6 * scale, scale);
    });
  }
  footer(pdf, data.link);
  return pdf;
}

/** String spacing that makes a vertical diagram with `strings` strings fill `width`. */
const gridUnit = (width, strings) => (width - 3) / (strings + 1.04);

/**
 * Shared cell layout for chord diagrams (labels inside the dots): horizontal grids on chord sheets,
 * vertical boxes on song sheets.
 */
function cellLayout(chords, strings, columns, { vertical = false } = {}) {
  const gap = 16;
  const colW = (WIDTH - gap * (columns - 1)) / columns;
  const frets = Math.max(5, ...chords.map((c) => { const w = chordWindow(c.frets, 5); return w.to - w.from + 1; }));
  const sy = vertical ? Math.min(14, gridUnit(colW, strings)) : Math.min(13, (colW - 2) / (1.25 + 1.75 * frets));
  const grids = chords.map((c) => chordGrid(c, strings, { labels: c.labels, roots: c.roots, columns: frets, sy, vertical }));
  const cellH = Math.max(...grids.map((g) => g.height)) + 30;
  return { gap, colW, grids, cellH, columns };
}

function chordCells(pdf, chords, layout, startY, scale = 1) {
  const { gap, colW, grids, cellH, columns } = layout;
  const bottom = A4.height - MARGIN - FOOTER;
  const rowH = (cellH + 8) * scale;
  let y = startY;
  chords.forEach((c, i) => {
    const col = i % columns;
    if (col === 0 && i > 0) y += rowH;
    if (col === 0 && y + cellH * scale > bottom) { pdf.addPage(); y = MARGIN + 10; }
    const x = MARGIN + col * (colW + gap);
    pdf.drawGrid(grids[i], x, y, scale);
    const fs = Math.max(scale, 0.8);
    let ty = y + grids[i].height * scale + 9 * fs;
    pdf.text(x, ty, c.name, { size: 10 * fs, bold: true });
    if (c.meta) { ty += 9 * fs; pdf.text(x, ty, c.meta, { size: 7 * fs, gray: 0.4 }); }
    ty += 9 * fs;
    pdf.text(x, ty, c.frets.map((f) => (f < 0 ? 'x' : f)).join(' '), { size: 7 * fs, gray: 0.4 });
  });
  return chords.length ? y + rowH : y;
}

/**
 * Chord shapes sheet, fitted to one A4 page where possible (more columns and smaller grids for long lists).
 * data: { title, lines, strings, link, chords: [{ name, meta, frets, barres, labels, roots }] }
 */
export function chordSheet(data) {
  const pdf = new PdfWriter({ title: data.title });
  const y = header(pdf, data.title, data.lines);
  const avail = A4.height - MARGIN - FOOTER - y;
  let best = null;
  for (const columns of [4, 5, 6]) {
    const layout = cellLayout(data.chords, data.strings, columns);
    const rows = Math.ceil(data.chords.length / columns);
    const scale = Math.min(1, avail / (rows * (layout.cellH + 8)));
    if (!best || scale > best.scale + 0.15) best = { layout, scale };
    if (scale >= 0.85) break;
  }
  chordCells(pdf, data.chords, best.layout, y, Math.max(best.scale, 0.6));
  footer(pdf, data.link);
  return pdf;
}

/**
 * Song / exercise sheet: title, optional note, sections and chords in order.
 * data: { title, note, lines, strings, link, items: [{ section } | { name, meta, frets, barres, labels, roots }] }
 */
export function songSheet(data) {
  const pdf = new PdfWriter({ title: data.title });
  let y = header(pdf, data.title, data.lines);
  if (data.note) {
    for (const line of wrap(pdf, data.note, 10, WIDTH)) { pdf.text(MARGIN, y, line, { size: 10 }); y += 14; }
    y += 8;
  }
  // Group consecutive chords between section dividers
  const blocks = [];
  for (const item of data.items) {
    if (item.section !== undefined) blocks.push({ section: item.section, chords: [] });
    else {
      if (!blocks.length) blocks.push({ section: null, chords: [] });
      blocks[blocks.length - 1].chords.push(item);
    }
  }
  const bottom = A4.height - MARGIN - FOOTER;
  for (const block of blocks) {
    if (block.section) {
      if (y + 90 > bottom) { pdf.addPage(); y = MARGIN + 10; }
      pdf.text(MARGIN, y, block.section, { size: 12, bold: true });
      y += 12;
    }
    if (block.chords.length) y = chordCells(pdf, block.chords, cellLayout(block.chords, data.strings, 5, { vertical: true }), y);
    y += 6;
  }
  footer(pdf, data.link);
  return pdf;
}

/** File name for a sheet title: "A Dorian" -> "a-dorian.pdf". */
export function pdfFileName(title) {
  const base = String(title).replace(/♯/g, 'sharp').replace(/♭/g, 'flat').replace(/#/g, 'sharp')
    .normalize('NFKD').replace(/[^\w\s-]/g, '').trim().toLowerCase().replace(/[\s_]+/g, '-');
  return `${base || 'guitar-positions'}.pdf`;
}
