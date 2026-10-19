#!/usr/bin/env python3
"""Regenerate the Studio app icons (light, minimal) in static/studio/icons.

Needs `rsvg-convert` (brew install librsvg) for the PNG exports.
Usage: python scripts/build_icons.py
"""
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'static' / 'studio' / 'icons'

BG = '#f7f7f5'      # light surface, matches the Studio's --subtle/--board tones
BORDER = '#e0e0dc'
INK = '#141414'
ACCENT = '#d6401f'  # root note, same as the light theme accent


def glyph(scale=1.0, thick=False):
    """Fretboard motif: six strings (four in the bold favicon), three frets, nut and three notes."""
    sw, nut_w, r = (28, 44, 78) if thick else (6, 18, 46)
    strings = 4 if thick else 6
    ys = [312 + i * 400 / (strings - 1) for i in range(strings)]
    parts = []
    for y in ys:
        parts.append(f'<line x1="192" y1="{y:.1f}" x2="752" y2="{y:.1f}" stroke="{INK}" stroke-opacity=".32" stroke-width="{sw}" stroke-linecap="round"/>')
    for x in (352, 512, 672):
        parts.append(f'<line x1="{x}" y1="312" x2="{x}" y2="712" stroke="{INK}" stroke-opacity=".2" stroke-width="{sw}"/>')
    parts.append(f'<rect x="{192 - nut_w / 2 - 0.0:.1f}" y="306" width="{nut_w}" height="412" rx="{nut_w / 2}" fill="{INK}"/>')
    low, mid, high = (ys[2], ys[1], ys[0]) if thick else (ys[3], ys[2], ys[1])
    parts.append(f'<circle cx="272" cy="{low:.1f}" r="{r}" fill="{ACCENT}"/>')
    parts.append(f'<circle cx="432" cy="{mid:.1f}" r="{r}" fill="{INK}"/>')
    parts.append(f'<circle cx="592" cy="{high:.1f}" r="{r}" fill="{INK}"/>')
    return f'<g transform="translate(552 512) scale({scale}) translate(-512 -512)">{"".join(parts)}</g>'


def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">{body}</svg>\n'


def rounded(x, y, size, rx):
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{rx}" fill="{BG}" stroke="{BORDER}" stroke-width="6"/>'


ICONS = {
    'icon.svg': svg(rounded(3, 3, 1018, 224) + glyph(1.0)),
    'icon-small.svg': svg(rounded(3, 3, 1018, 200) + glyph(1.05, thick=True)),
    'icon-macos.svg': svg(rounded(103, 103, 818, 185) + glyph(0.8)),
    'icon-full.svg': svg(f'<rect width="1024" height="1024" fill="{BG}"/>' + glyph(1.0)),
    'icon-android-foreground.svg': svg(glyph(0.82)),
}

# (svg source, png name, size)
PNGS = [
    ('icon-full.svg', 'app-icon-1024.png', 1024),
    ('icon-macos.svg', 'app-icon-macos-1024.png', 1024),
    ('icon-android-foreground.svg', 'app-icon-android-foreground-1024.png', 1024),
    ('icon-full.svg', 'apple-touch-icon.png', 180),
    ('icon-small.svg', 'favicon-32.png', 32),
    ('icon-small.svg', 'favicon-48.png', 48),
    ('icon.svg', 'icon-192.png', 192),
    ('icon.svg', 'icon-512.png', 512),
    ('icon-full.svg', 'icon-maskable-192.png', 192),
    ('icon-full.svg', 'icon-maskable-512.png', 512),
]


def main():
    for name, content in ICONS.items():
        (OUT / name).write_text(content)
    for src, png, size in PNGS:
        subprocess.run(['rsvg-convert', '-w', str(size), '-h', str(size), str(OUT / src), '-o', str(OUT / png)], check=True)
    print(f'wrote {len(ICONS)} SVGs and {len(PNGS)} PNGs to {OUT}')


if __name__ == '__main__':
    main()
