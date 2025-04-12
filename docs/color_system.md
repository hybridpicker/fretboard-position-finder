# Fretboard Position Finder Color System

This document outlines the color system implemented throughout the application.

## Color Palette

We've implemented a harmonious color scheme based on the following hex values:

| Color Name   | Hex Code | RGB Values       | Purpose                         |
|--------------|----------|------------------|----------------------------------|
| Cream        | #EFEDE8  | 239, 237, 232    | Light backgrounds, text on dark  |
| Dark Slate   | #2D3C3F  | 45, 60, 63       | Dark backgrounds, text on light  |
| Teal         | #3D7876  | 61, 120, 118     | Primary accent color             |
| Khaki        | #D8CD77  | 216, 205, 119    | Secondary accent, root notes     |
| Terra Cotta  | #C5574B  | 197, 87, 75      | Tertiary accent, special notes   |
| Blue Teal    | #407781  | 64, 119, 129     | Quaternary accent, hover states  |

## Implementation

The color system has been implemented through several key files:

1. `static/css/colors.css` - Core color variables
2. Component-specific color implementations:
   - `static/css/chord_selector_colors.css`
   - `static/css/direct-inversion-cycling-colors.css`
   - `static/css/3d-strings-colors.css`

## Usage Guidelines

### Interface Elements

- **Background Colors**:
  - Primary background: Cream (`--bg-primary`)
  - Secondary/Dark background: Dark Slate (`--bg-secondary`)
  - Accent elements: Teal (`--bg-accent`)

- **Text Colors**:
  - Primary text (on light bg): Dark Slate (`--text-primary`)
  - Secondary text (on dark bg): Cream (`--text-secondary`)
  - Accent text: Terra Cotta (`--text-accent`)

- **Interactive Elements**:
  - Buttons: Teal with Cream text
  - Links: Terra Cotta
  - Hover states: Blue Teal or Khaki

### Fretboard Elements

- **Notes**:
  - Regular notes: Teal (`--color-teal`)
  - Root notes: Khaki (`--color-khaki`)
  - Accent/special notes: Terra Cotta (`--color-terra-cotta`)
  - Higher octave notes: Blue Teal (`--color-blue-teal`)

- **Strings**: Dark background with light borders
- **Fretboard**: Alternating light/dark patterns using the color scheme

## SVG Assets

Note indicators use SVG files with the color scheme:
- `static/media/circle_01.svg` - Teal
- `static/media/circle_02.svg` - Blue Teal
- `static/media/circle_03.svg` - Khaki
- `static/media/circle_04.svg` - Terra Cotta

## Benefits

This consistent color system provides:
1. Visual harmony across the application
2. Semantic meaning through color
3. Improved accessibility through thoughtful contrast
4. Easier updates through centralized variables
