#!/usr/bin/env python3
"""Regenerate the Studio app icons (light, minimal) in static/studio/icons and the
social share image in static/thumbnail.
Motif: an F major pentatonic box on the neck, root F in the accent colour.

Needs `rsvg-convert` (brew install librsvg) for the PNG exports. The share image text
uses a system font (Helvetica Neue on macOS, falling back to Arial or Helvetica).
Usage: python scripts/build_icons.py
"""

import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "static" / "studio" / "icons"

BG = "#f7f7f5"  # light surface, matches the Studio's --subtle/--board tones
BORDER = "#e0e0dc"
INK = "#141414"
ACCENT = "#d6401f"  # root note, same as the light theme accent


# F major pentatonic (F G A C D), box position on frets 7-10: (string 0 = low E .. 5 = high E, fret, is_root)
F_PENTATONIC = [
    (0, 8, False),
    (0, 10, False),
    (1, 8, True),
    (1, 10, False),
    (2, 7, False),
    (2, 10, False),
    (3, 7, False),
    (3, 10, True),
    (4, 8, False),
    (4, 10, False),
    (5, 8, False),
    (5, 10, False),
]


def glyph(scale=1.0, thick=False):
    """Fretboard fragment (frets 7-10) with the F major pentatonic box; always six strings."""
    sw, nut_w, r = (16, 36, 37) if thick else (6, 14, 33)
    top, bottom, left, step = 312, 712, 192, 140
    ys = {s: top + (5 - s) * (bottom - top) / 5 for s in range(6)}
    parts = []
    for y in ys.values():
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + 4 * step}" y2="{y:.1f}" stroke="{INK}" stroke-opacity=".4" stroke-width="{sw}" stroke-linecap="round"/>'
        )
    for k in range(1, 5):
        parts.append(
            f'<line x1="{left + k * step}" y1="{top}" x2="{left + k * step}" y2="{bottom}" stroke="{INK}" stroke-opacity=".22" stroke-width="{sw}"/>'
        )
    parts.append(
        f'<rect x="{left - nut_w / 2:.1f}" y="{top - 6}" width="{nut_w}" height="{bottom - top + 12}" rx="{nut_w / 2}" fill="{INK}"/>'
    )
    for string, fret, root in F_PENTATONIC:
        x = left + (fret - 7) * step + step / 2
        parts.append(
            f'<circle cx="{x:.1f}" cy="{ys[string]:.1f}" r="{r}" fill="{ACCENT if root else INK}"/>'
        )
    return f'<g transform="translate(552 512) scale({scale}) translate(-512 -512)">{"".join(parts)}</g>'


def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">{body}</svg>\n'


def rounded(x, y, size, rx):
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{rx}" fill="{BG}" stroke="{BORDER}" stroke-width="6"/>'


ICONS = {
    "icon.svg": svg(rounded(3, 3, 1018, 224) + glyph(1.0)),
    "icon-small.svg": svg(rounded(3, 3, 1018, 200) + glyph(1.35, thick=True)),
    "icon-macos.svg": svg(rounded(103, 103, 818, 185) + glyph(0.8)),
    "icon-full.svg": svg(f'<rect width="1024" height="1024" fill="{BG}"/>' + glyph(1.0)),
    "icon-android-foreground.svg": svg(glyph(0.82)),
}

# (svg source, png name, size)
PNGS = [
    ("icon-full.svg", "app-icon-1024.png", 1024),
    ("icon-macos.svg", "app-icon-macos-1024.png", 1024),
    ("icon-android-foreground.svg", "app-icon-android-foreground-1024.png", 1024),
    ("icon-full.svg", "apple-touch-icon.png", 180),
    ("icon-small.svg", "favicon-32.png", 32),
    ("icon-small.svg", "favicon-48.png", 48),
    ("icon.svg", "icon-192.png", 192),
    ("icon.svg", "icon-512.png", 512),
    ("icon-full.svg", "icon-maskable-192.png", 192),
    ("icon-full.svg", "icon-maskable-512.png", 512),
]


# The site header (templates/favicon.html) uses the same motif in static/favicon/v2
LEGACY = Path(__file__).resolve().parent.parent / "static" / "favicon" / "v2"
LEGACY_PNGS = (
    [("icon-small.svg", f"favicon-{n}x{n}.png", n) for n in (16, 32, 96)]
    + [("icon.svg", f"android-icon-{n}x{n}.png", n) for n in (36, 48, 72, 96, 144, 192)]
    + [
        ("icon-full.svg", f"apple-icon-{n}x{n}.png", n)
        for n in (57, 60, 72, 76, 114, 120, 144, 152, 180)
    ]
    + [("icon.svg", f"ms-icon-{n}x{n}.png", n) for n in (70, 144, 150, 310)]
    + [
        ("icon-full.svg", "apple-icon.png", 192),
        ("icon-full.svg", "apple-icon-precomposed.png", 192),
    ]
)


def render(src, target, size):
    subprocess.run(
        ["rsvg-convert", "-w", str(size), "-h", str(size), str(OUT / src), "-o", str(target)],
        check=True,
    )


OG_IMAGE = OUT.parent.parent / "thumbnail" / "og-image.png"
OG_FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif"


def build_og_image():
    """Social share image (1200x630): wordmark and tagline beside the app icon."""
    lines = ("Scales, arpeggios and chords", "with fingerings on an", "interactive fretboard.")
    tagline = "".join(
        f'<text x="84" y="{412 + i * 46}" font-size="33" fill="#5c5c58">{line}</text>'
        for i, line in enumerate(lines)
    )
    source = OUT.parent / "og-image.svg"
    source.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">'
        '<rect width="1200" height="630" fill="#ffffff"/>'
        f'<g font-family="{OG_FONT}">'
        f'<text x="80" y="228" font-size="112" font-weight="700" letter-spacing="-3" fill="{INK}">Guitar</text>'
        f'<text x="80" y="344" font-size="112" font-weight="700" letter-spacing="-3" fill="{INK}">Positions</text>'
        f"{tagline}</g>"
        f'<g transform="translate(650 90) scale(0.4395)">{rounded(3, 3, 1018, 224)}{glyph(1.0)}</g>'
        "</svg>\n"
    )
    try:
        subprocess.run(
            ["rsvg-convert", "-w", "1200", "-h", "630", str(source), "-o", str(OG_IMAGE)],
            check=True,
        )
    finally:
        source.unlink()


def main():
    build_og_image()
    for name, content in ICONS.items():
        (OUT / name).write_text(content)
    for src, png, size in PNGS:
        render(src, OUT / png, size)
    for src, png, size in LEGACY_PNGS:
        render(src, LEGACY / png, size)
    from PIL import Image  # favicon.ico: 16, 32 and 48 px

    Image.open(OUT / "favicon-48.png").save(
        LEGACY / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )
    print(f"wrote {len(ICONS)} SVGs and {len(PNGS) + len(LEGACY_PNGS)} PNGs to {OUT} and {LEGACY}")


if __name__ == "__main__":
    main()
