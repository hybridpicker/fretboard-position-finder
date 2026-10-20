// Minimal vector PDF writer for printable A4 sheets: lines, circles, text in the built-in Helvetica
// fonts (no embedding, no compression, no dependencies). ♯ and ♭ are not in Helvetica, so they are
// drawn as small vector glyphs. Coordinates are in points from the top-left corner (y down).

export const A4 = { width: 595.28, height: 841.89 };

// Helvetica / Helvetica-Bold advance widths (AFM, 1/1000 em) for ASCII 32–126
const WIDTHS = {
  regular: [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584],
  bold: [278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 333, 333, 584, 584, 584, 611, 975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556, 333, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611, 611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500, 389, 280, 389, 584],
};
// WinAnsi code points and widths for the few non-ASCII characters the sheets use
const EXTRA = { '·': [0xb7, 278], '×': [0xd7, 584], '°': [0xb0, 400], '–': [0x96, 556], '—': [0x97, 1000], '’': [0x92, 222], 'ø': [0xf8, 611], 'é': [0xe9, 556], 'ä': [0xe4, 556], 'ö': [0xf6, 556], 'ü': [0xfc, 556], 'ß': [0xdf, 611], 'Ä': [0xc4, 667], 'Ö': [0xd6, 778], 'Ü': [0xdc, 722] };
const ACCIDENTALS = { '♯': 'sharp', '♭': 'flat', '𝄫': 'doubleflat', '𝄪': 'doublesharp' };
const GLYPH_WIDTH = { sharp: 0.5, flat: 0.42, doubleflat: 0.74, doublesharp: 0.5 };

const num = (n) => (Math.round(n * 100) / 100).toString();

function charWidth(ch, bold) {
  const code = ch.charCodeAt(0);
  if (code >= 32 && code <= 126) return WIDTHS[bold ? 'bold' : 'regular'][code - 32] / 1000;
  if (EXTRA[ch]) return EXTRA[ch][1] / 1000;
  return 0.556;
}

/** Split text into Helvetica runs and accidental glyphs. */
function runs(text) {
  const out = [];
  for (const ch of String(text)) {
    if (ACCIDENTALS[ch]) out.push({ glyph: ACCIDENTALS[ch] });
    else if (out.length && out[out.length - 1].text !== undefined) out[out.length - 1].text += ch;
    else out.push({ text: ch });
  }
  return out;
}

function encode(text) {
  let s = '';
  for (const ch of text) {
    const code = ch.charCodeAt(0);
    let byte;
    if (code >= 32 && code <= 126) byte = code;
    else if (EXTRA[ch]) byte = EXTRA[ch][0];
    else byte = 63; // '?'
    const c = String.fromCharCode(byte);
    s += c === '(' || c === ')' || c === '\\' ? `\\${c}` : c;
  }
  return s;
}

export class PdfWriter {
  constructor({ title = 'Guitar Positions', width = A4.width, height = A4.height } = {}) {
    this.title = title;
    this.width = width;
    this.height = height;
    this.pages = [];
    this.addPage();
  }

  addPage() {
    this.ops = [];
    this.pages.push(this.ops);
  }

  Y(y) { return this.height - y; }

  gray(level, stroke) { return `${num(level)} ${stroke ? 'G' : 'g'}`; }

  line(x1, y1, x2, y2, { width = 0.75, gray = 0, cap = 0 } = {}) {
    this.ops.push(`q ${this.gray(gray, true)} ${num(width)} w ${cap} J ${num(x1)} ${num(this.Y(y1))} m ${num(x2)} ${num(this.Y(y2))} l S Q`);
  }

  rect(x, y, w, h, { fill = null, stroke = null, width = 0.75 } = {}) {
    const paint = fill !== null && stroke !== null ? 'B' : fill !== null ? 'f' : 'S';
    this.ops.push(`q ${fill !== null ? this.gray(fill) : ''} ${stroke !== null ? this.gray(stroke, true) : ''} ${num(width)} w ${num(x)} ${num(this.Y(y + h))} ${num(w)} ${num(h)} re ${paint} Q`);
  }

  circle(cx, cy, r, { fill = null, stroke = null, width = 0.75 } = {}) {
    const k = 0.5523 * r;
    const X = cx;
    const Yc = this.Y(cy);
    const path = [
      `${num(X + r)} ${num(Yc)} m`,
      `${num(X + r)} ${num(Yc + k)} ${num(X + k)} ${num(Yc + r)} ${num(X)} ${num(Yc + r)} c`,
      `${num(X - k)} ${num(Yc + r)} ${num(X - r)} ${num(Yc + k)} ${num(X - r)} ${num(Yc)} c`,
      `${num(X - r)} ${num(Yc - k)} ${num(X - k)} ${num(Yc - r)} ${num(X)} ${num(Yc - r)} c`,
      `${num(X + k)} ${num(Yc - r)} ${num(X + r)} ${num(Yc - k)} ${num(X + r)} ${num(Yc)} c`,
    ].join(' ');
    const paint = fill !== null && stroke !== null ? 'b' : fill !== null ? 'f' : 's';
    this.ops.push(`q ${fill !== null ? this.gray(fill) : ''} ${stroke !== null ? this.gray(stroke, true) : ''} ${num(width)} w ${path} ${paint} Q`);
  }

  textWidth(text, size, bold = false) {
    let w = 0;
    for (const run of runs(text)) {
      if (run.glyph) w += GLYPH_WIDTH[run.glyph];
      else for (const ch of run.text) w += charWidth(ch, bold);
    }
    return w * size;
  }

  /** Text with its baseline at y. align: left | center | right. */
  text(x, y, text, { size = 10, bold = false, gray = 0, align = 'left' } = {}) {
    let cursor = x;
    if (align !== 'left') cursor -= this.textWidth(text, size, bold) * (align === 'center' ? 0.5 : 1);
    for (const run of runs(text)) {
      if (run.glyph) {
        this.glyph(run.glyph, cursor, y, size, gray);
        cursor += GLYPH_WIDTH[run.glyph] * size;
      } else {
        this.ops.push(`BT ${this.gray(gray)} /${bold ? 'F2' : 'F1'} ${num(size)} Tf ${num(cursor)} ${num(this.Y(y))} Td (${encode(run.text)}) Tj ET`);
        for (const ch of run.text) cursor += charWidth(ch, bold) * size;
      }
    }
    return cursor;
  }

  /** Vector accidentals (em units, baseline at y). */
  glyph(kind, x, y, size, gray) {
    const P = (px, py) => `${num(x + px * size)} ${num(this.Y(y - py * size))}`;
    const g = this.gray(gray, true);
    if (kind === 'flat' || kind === 'doubleflat') {
      const one = (dx) => {
        this.ops.push(`q ${g} ${num(size * 0.07)} w 1 J 1 j ${P(dx + 0.1, 0.74)} m ${P(dx + 0.1, -0.01)} l S Q`);
        this.ops.push(`q ${g} ${num(size * 0.07)} w 1 J 1 j ${P(dx + 0.1, 0.3)} m ${P(dx + 0.28, 0.44)} ${P(dx + 0.44, 0.28)} ${P(dx + 0.3, 0.14)} c ${P(dx + 0.22, 0.06)} ${P(dx + 0.14, 0.02)} ${P(dx + 0.1, -0.01)} c S Q`);
      };
      one(0);
      if (kind === 'doubleflat') one(0.32);
    } else if (kind === 'sharp') {
      this.ops.push(`q ${g} ${num(size * 0.055)} w ${P(0.17, -0.06)} m ${P(0.17, 0.74)} l ${P(0.33, -0.02)} m ${P(0.33, 0.78)} l S Q`);
      this.ops.push(`q ${g} ${num(size * 0.09)} w ${P(0.05, 0.2)} m ${P(0.45, 0.3)} l ${P(0.05, 0.44)} m ${P(0.45, 0.54)} l S Q`);
    } else {
      this.ops.push(`q ${g} ${num(size * 0.09)} w 1 J ${P(0.08, 0.1)} m ${P(0.42, 0.44)} l ${P(0.08, 0.44)} m ${P(0.42, 0.1)} l S Q`);
    }
  }

  /** Draw items from grid.js at (ox, oy), scaled by `scale`. */
  drawGrid(grid, ox, oy, scale = 1) {
    const GRAY = { ink: 0, paper: 1, fret: 0.55, muted: 0.4 };
    const X = (v) => ox + v * scale;
    const Yv = (v) => oy + v * scale;
    for (const it of grid.items) {
      if (it.type === 'line') this.line(X(it.x1), Yv(it.y1), X(it.x2), Yv(it.y2), { width: it.width * scale, gray: GRAY[it.color], cap: it.cap === 'round' ? 1 : 0 });
      else if (it.type === 'circle') this.circle(X(it.cx), Yv(it.cy), it.r * scale, { fill: GRAY[it.fill], stroke: GRAY[it.stroke], width: it.width * scale });
      else if (it.type === 'text') this.text(X(it.x), Yv(it.y), it.text, { size: it.size * scale, bold: it.bold, gray: GRAY[it.color], align: it.align });
    }
  }

  /** Serialise to PDF bytes. */
  output() {
    const objects = [];
    const add = (body) => { objects.push(body); return objects.length; };
    const catalog = add(null);
    const pagesObj = add(null);
    const f1 = add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>');
    const f2 = add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>');
    const kids = [];
    for (const ops of this.pages) {
      const stream = ops.join('\n');
      const content = add(`<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`);
      kids.push(add(`<< /Type /Page /Parent ${pagesObj} 0 R /MediaBox [0 0 ${num(this.width)} ${num(this.height)}] /Resources << /Font << /F1 ${f1} 0 R /F2 ${f2} 0 R >> >> /Contents ${content} 0 R >>`));
    }
    objects[catalog - 1] = `<< /Type /Catalog /Pages ${pagesObj} 0 R >>`;
    objects[pagesObj - 1] = `<< /Type /Pages /Kids [${kids.map((k) => `${k} 0 R`).join(' ')}] /Count ${kids.length} >>`;
    const info = add(`<< /Title (${encode(this.title)}) /Producer (Guitar Positions) >>`);

    let out = '%PDF-1.4\n%\xe2\xe3\xcf\xd3\n';
    const offsets = [];
    objects.forEach((body, i) => {
      offsets.push(out.length);
      out += `${i + 1} 0 obj\n${body}\nendobj\n`;
    });
    const xref = out.length;
    out += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
    out += offsets.map((o) => `${String(o).padStart(10, '0')} 00000 n \n`).join('');
    out += `trailer\n<< /Size ${objects.length + 1} /Root ${catalog} 0 R /Info ${info} 0 R >>\nstartxref\n${xref}\n%%EOF\n`;
    const bytes = new Uint8Array(out.length);
    for (let i = 0; i < out.length; i++) bytes[i] = out.charCodeAt(i) & 0xff;
    return bytes;
  }
}
