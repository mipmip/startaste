# Design: add-logo

## Goals

- Logo visible in README and dashboard
- Single source asset in `assets/`, copies/references from there

## Non-goals

- Redesigning the logo or creating variants (SVG, dark mode version)
- Corporate identity guidelines (colors, typography rules)
- CI (continuous integration) — separate concern

## Asset storage

```
assets/
└── logo.png    ← full-size logo (from ~/Downloads/startaste-logo.png)
```

## README placement

Centered image at the top, replacing the text `# Startaste`:

```markdown
<p align="center">
  <img src="assets/logo.png" alt="StarTaste" width="200">
</p>
```

Keep the coverage line below the logo.

## Dashboard placement

In `base.html`, replace the text "startaste" in the nav with a small logo image:

```html
<a href="/" class="logo">
  <img src="{{ url_for('dashboard.static', filename='logo.png') }}" alt="StarTaste" height="28">
</a>
```

Copy `logo.png` to `startaste/dashboard/static/logo.png` for Flask to serve it.

## Favicon

Scale down or use the logo as-is for a favicon. Reference in `base.html`:

```html
<link rel="icon" href="{{ url_for('dashboard.static', filename='favicon.png') }}">
```

Use the same logo file scaled to a small size — browsers handle the resize. No need for .ico format.
