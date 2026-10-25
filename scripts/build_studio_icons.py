#!/usr/bin/env python3
"""
Build the Guitar Positions Studio icons (web, PWA and native app masters).

Motif: a minimal fretboard (nut, frets, six strings) with a three-note chord shape;
the root note uses the Studio accent colour. Requires `rsvg-convert` (librsvg).

    python3 scripts/build_studio_icons.py
"""

import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "static" / "studio" / "icons"

BG = "#141414"
INK = "#ececea"
ACCENT = "#ff5b36"


def motif(stroke=6, nut=18, dot=46, strings=6, scale=1.0, offset=(40, 0)):
    """Fretboard motif on a 1024 grid, optionally scaled around the centre."""
    # Strings stop one fret after the last chord tone; the offset re-centres the nut-heavy shape
    top, bottom, left, right = 312, 712, 192, 752
    parts = []
    gap = (bottom - top) / (strings - 1)
    for i in range(strings):
        y = top + i * gap
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{INK}" stroke-opacity=".32" stroke-width="{stroke}" stroke-linecap="round"/>'
        )
    for x in (352, 512, 672):
        parts.append(
            f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" stroke="{INK}" stroke-opacity=".2" stroke-width="{stroke}"/>'
        )
    parts.append(
        f'<rect x="{left - nut / 2}" y="{top - 6}" width="{nut}" height="{bottom - top + 12}" rx="{nut / 2}" fill="{INK}"/>'
    )

    # Chord shape: root on the lowest string pair, two chord tones above it
    def string_y(n):  # n = 1 (high) .. strings (low)
        return top + (strings - n) * gap

    parts.append(
        f'<circle cx="272" cy="{string_y(2 if strings < 6 else 3):.1f}" r="{dot}" fill="{ACCENT}"/>'
    )
    parts.append(
        f'<circle cx="432" cy="{string_y(3 if strings < 6 else 4):.1f}" r="{dot}" fill="{INK}"/>'
    )
    parts.append(
        f'<circle cx="592" cy="{string_y(4 if strings < 6 else 5):.1f}" r="{dot}" fill="{INK}"/>'
    )
    group = "".join(parts)
    cx, cy = 512, 512
    transform = (
        f"translate({cx + offset[0]} {cy + offset[1]}) scale({scale}) translate({-cx} {-cy})"
    )
    return f'<g transform="{transform}">{group}</g>'


def svg(body, background=None, radius=0):
    bg = ""
    if background:
        bg = f'<rect width="1024" height="1024" rx="{radius}" fill="{background}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">{bg}{body}</svg>\n'


VARIANTS = {
    # Rounded tile for browsers and the PWA "any" purpose
    "icon.svg": svg(motif(), BG, radius=224),
    # Full bleed: maskable PWA icon, iOS/iPadOS app icon (the OS rounds the corners)
    "icon-full.svg": svg(motif(), BG),
    # Bolder variant for 16-48 px favicons
    "icon-small.svg": svg(motif(stroke=28, nut=44, dot=78, strings=4, scale=1.05), BG, radius=200),
    # macOS (Big Sur+) app icon: rounded tile inside the 1024 canvas with transparent margin
    "icon-macos.svg": svg(
        f'<rect x="100" y="100" width="824" height="824" rx="185" fill="{BG}"/>' + motif(scale=0.8),
    ),
    # Android adaptive icon foreground (transparent; background colour is BG)
    "icon-android-foreground.svg": svg(motif(scale=0.82)),
}

PNGS = [
    ("icon.svg", "icon-192.png", 192),
    ("icon.svg", "icon-512.png", 512),
    ("icon-full.svg", "icon-maskable-192.png", 192),
    ("icon-full.svg", "icon-maskable-512.png", 512),
    ("icon-full.svg", "apple-touch-icon.png", 180),
    ("icon-small.svg", "favicon-32.png", 32),
    ("icon-small.svg", "favicon-48.png", 48),
    # Masters for the native app icon sets (Capacitor / Xcode / Android Studio)
    ("icon-full.svg", "app-icon-1024.png", 1024),
    ("icon-macos.svg", "app-icon-macos-1024.png", 1024),
    ("icon-android-foreground.svg", "app-icon-android-foreground-1024.png", 1024),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in VARIANTS.items():
        (OUT / name).write_text(content)
    for source, target, size in PNGS:
        subprocess.run(
            [
                "rsvg-convert",
                "-w",
                str(size),
                "-h",
                str(size),
                "-o",
                str(OUT / target),
                str(OUT / source),
            ],
            check=True,
        )
    print(f"Wrote {len(VARIANTS)} SVGs and {len(PNGS)} PNGs to {OUT}")


if __name__ == "__main__":
    main()
