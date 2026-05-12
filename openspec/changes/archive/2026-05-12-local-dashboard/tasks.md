## 1. Dependencies

- [x] 1.1 Add Flask to `requirements.txt`
- [x] 1.2 Update `flake.nix`, `pyproject.toml` to include Flask in dependencies

## 2. Service layer

- [x] 2.1 Create `startaste/dashboard/services.py` with `get_overview()`
- [x] 2.2 Add `get_hn_stories(page, per_page)` and `get_hn_comments(page, per_page)`
- [x] 2.3 Add `get_github_stars(page, per_page)`

## 3. Flask app

- [x] 3.1 Create `startaste/dashboard/__init__.py` with `create_app()` factory
- [x] 3.2 Create `startaste/dashboard/views.py` with blueprint and routes: `/`, `/hn`, `/hn/comments`, `/github`

## 4. Templates

- [x] 4.1 Create `startaste/dashboard/templates/base.html` — layout with nav, content block, light/dark mode
- [x] 4.2 Create `startaste/dashboard/templates/index.html` — source overview cards
- [x] 4.3 Create `startaste/dashboard/templates/hn.html` — stories/comments listing with pagination
- [x] 4.4 Create `startaste/dashboard/templates/github.html` — stars listing with pagination

## 5. Static assets

- [x] 5.1 Create `startaste/dashboard/static/style.css` — tangled-inspired minimal CSS with light/dark

## 6. CLI integration

- [x] 6.1 Add `serve` subcommand to `startaste/cli.py` with `--port` flag (default 8421)

## 7. Documentation

- [x] 7.1 Update README with `startaste serve` usage

## 8. Tests

- [x] 8.1 Add tests for service layer functions (overview, paginated listings, empty DB)
- [x] 8.2 Add tests for Flask routes (status codes, content checks)
- [x] 8.3 Run full test suite and verify all pass (65 tests passing)
