#!/usr/bin/env python3
"""
Generate the native app icons and launch screens from the icon masters in static/studio/icons/
(which scripts/build_studio_icons.py renders from the SVG sources). Requires Pillow.

    python apps/scripts/generate_native_icons.py      (or: cd apps && npm run icons)

iOS / iPadOS   AppIcon.appiconset: single-size 1024 icon from app-icon-1024.png (opaque, full
               bleed; the OS applies the corner mask)
Mac Catalyst   the same AppIcon set gets "mac" idiom entries (16-512 pt @1x/@2x) from
               app-icon-macos-1024.png (Big Sur tile with transparent margin); Catalyst builds use
               those instead of the iOS icon
Android        legacy square and round launcher icons from app-icon-1024.png, an adaptive icon
               with the foreground app-icon-android-foreground-1024.png on BACKGROUND and a
               monochrome layer (themed icons, Android 13+) derived from the foreground alpha
Splash         iOS Splash.imageset and Android drawable*/splash.png: BACKGROUND with the
               1024 master centred
"""
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw

APPS = Path(__file__).resolve().parent.parent
MASTERS = APPS.parent / 'static' / 'studio' / 'icons'
BACKGROUND = '#f7f7f5'

IOS_ASSETS = APPS / 'ios' / 'App' / 'App' / 'Assets.xcassets'
ANDROID_RES = APPS / 'android' / 'app' / 'src' / 'main' / 'res'

ANDROID_DENSITIES = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
# Capacitor template splash sizes (width, height) per drawable folder
ANDROID_SPLASH = {
    'drawable': (480, 320),
    'drawable-land-mdpi': (480, 320), 'drawable-land-hdpi': (800, 480), 'drawable-land-xhdpi': (1280, 720),
    'drawable-land-xxhdpi': (1600, 960), 'drawable-land-xxxhdpi': (1920, 1280),
    'drawable-port-mdpi': (320, 480), 'drawable-port-hdpi': (480, 800), 'drawable-port-xhdpi': (720, 1280),
    'drawable-port-xxhdpi': (960, 1600), 'drawable-port-xxxhdpi': (1280, 1920),
}
MAC_SIZES = (16, 32, 128, 256, 512)
IOS_SPLASH_SIZE = 2732


def load(name, mode):
    image = Image.open(MASTERS / name)
    if image.size != (1024, 1024):
        raise SystemExit(f'{name}: expected 1024x1024, got {image.size}')
    return image.convert(mode)


def resized(image, size):
    return image.resize((size, size), Image.Resampling.LANCZOS)


def save_png(image, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def circle_mask(size, supersample=4):
    big = Image.new('L', (size * supersample, size * supersample), 0)
    ImageDraw.Draw(big).ellipse((0, 0, size * supersample - 1, size * supersample - 1), fill=255)
    return big.resize((size, size), Image.Resampling.LANCZOS)


def splash(width, height, icon, icon_size):
    canvas = Image.new('RGB', (width, height), BACKGROUND)
    canvas.paste(resized(icon, icon_size), ((width - icon_size) // 2, (height - icon_size) // 2))
    return canvas


def ios(full, macos):
    iconset = IOS_ASSETS / 'AppIcon.appiconset'
    for old in iconset.glob('*.png'):
        old.unlink()
    images = [{'filename': 'AppIcon-1024.png', 'idiom': 'universal', 'platform': 'ios', 'size': '1024x1024'}]
    save_png(full, iconset / 'AppIcon-1024.png')
    for points in MAC_SIZES:
        for scale in (1, 2):
            name = f'AppIcon-mac-{points}@{scale}x.png'
            save_png(resized(macos, points * scale), iconset / name)
            images.append({'filename': name, 'idiom': 'mac', 'scale': f'{scale}x', 'size': f'{points}x{points}'})
    write_json(iconset / 'Contents.json', {'images': images, 'info': {'author': 'xcode', 'version': 1}})

    imageset = IOS_ASSETS / 'Splash.imageset'
    for old in imageset.glob('*.png'):
        old.unlink()
    # The launch screen scales this square aspect-fill, so the centre 1024 stays visible on every device
    image = splash(IOS_SPLASH_SIZE, IOS_SPLASH_SIZE, full, 1024)
    images = []
    for scale in (1, 2, 3):
        name = f'splash-{IOS_SPLASH_SIZE}@{scale}x.png'
        save_png(image, imageset / name)
        images.append({'filename': name, 'idiom': 'universal', 'scale': f'{scale}x'})
    write_json(imageset / 'Contents.json', {'images': images, 'info': {'author': 'xcode', 'version': 1}})

    # Launch screen background behind the image (instead of the system white/black)
    storyboard = APPS / 'ios' / 'App' / 'App' / 'Base.lproj' / 'LaunchScreen.storyboard'
    text = storyboard.read_text(encoding='utf-8')
    rgb = [int(BACKGROUND[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    color = (f'<color key="backgroundColor" red="{rgb[0]:.4f}" green="{rgb[1]:.4f}" blue="{rgb[2]:.4f}" '
             'alpha="1" colorSpace="custom" customColorSpace="sRGB"/>')
    text, count = re.subn(r'<color key="backgroundColor"[^>]*/>', color, text)
    if count != 1:
        raise SystemExit(f'{storyboard.name}: expected one backgroundColor, found {count}')
    storyboard.write_text(text, encoding='utf-8')


def android(full, foreground):
    round_masks = {}
    # Themed icon: the foreground's shapes in one colour, keeping their alpha
    monochrome = Image.new('RGBA', foreground.size, (255, 255, 255, 0))
    monochrome.putalpha(foreground.getchannel('A'))
    for density, factor in ANDROID_DENSITIES.items():
        folder = ANDROID_RES / f'mipmap-{density}'
        legacy = round(48 * factor)
        adaptive = round(108 * factor)
        square = resized(full, legacy)
        save_png(square, folder / 'ic_launcher.png')
        mask = round_masks.setdefault(legacy, circle_mask(legacy))
        rounded = square.convert('RGBA')
        rounded.putalpha(mask)
        save_png(rounded, folder / 'ic_launcher_round.png')
        save_png(resized(foreground, adaptive), folder / 'ic_launcher_foreground.png')
        save_png(resized(monochrome, adaptive), folder / 'ic_launcher_monochrome.png')

    adaptive_xml = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
    <monochrome android:drawable="@mipmap/ic_launcher_monochrome"/>
</adaptive-icon>
"""
    for name in ('ic_launcher.xml', 'ic_launcher_round.xml'):
        (ANDROID_RES / 'mipmap-anydpi-v26' / name).write_text(adaptive_xml, encoding='utf-8')
    (ANDROID_RES / 'values' / 'ic_launcher_background.xml').write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        f'    <color name="ic_launcher_background">{BACKGROUND}</color>\n</resources>\n', encoding='utf-8')
    # Android Studio's default vector placeholders are no longer referenced
    for unused in ('drawable-v24/ic_launcher_foreground.xml', 'drawable/ic_launcher_background.xml'):
        (ANDROID_RES / unused).unlink(missing_ok=True)

    for folder, (width, height) in ANDROID_SPLASH.items():
        save_png(splash(width, height, full, round(min(width, height) * 0.5)), ANDROID_RES / folder / 'splash.png')


def main():
    full = load('app-icon-1024.png', 'RGB')
    macos = load('app-icon-macos-1024.png', 'RGBA')
    foreground = load('app-icon-android-foreground-1024.png', 'RGBA')
    ios(full, macos)
    android(full, foreground)
    print(f'Icons and launch screens written to {IOS_ASSETS.relative_to(APPS)} and {ANDROID_RES.relative_to(APPS)}')


if __name__ == '__main__':
    main()
