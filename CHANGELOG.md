# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Fixed
- MCP clients that follow the authorization flow (e.g. the Claude connector)
  could not connect: authentication guarded the whole server, so paths it does
  not serve — including the `/.well-known/` OAuth discovery paths — answered
  `401` instead of `404`. A client could then neither discover OAuth metadata nor
  rule it out, and gave up before using its configured bearer token. Auth is now
  scoped to `/mcp`, and rejections no longer carry an uninformative bare
  `WWW-Authenticate: Bearer` challenge

## [3.1.0] - 2026-09-10

### Added
- MCP server (`startaste mcp`): serves the collection to Claude clients over
  streamable HTTP with seven read-only tools — search stars, search upvotes,
  fetch one item, overview, and top topics / languages / upvoted domains.
  Bearer-token authenticated (`startaste mcp-token` mints one), `/healthz` open,
  and the database is opened read-only so no tool can write
- `services.startaste.mcp.*` NixOS options for the MCP server
- NixOS module (`nixosModules.startaste`) and overlay (`overlays.default`):
  scheduled sync on a systemd timer and the dashboard as hardened units, with
  state under `/var/lib/startaste` and credentials from an `environmentFile`
- Flake now provides `packages` and `devShells` for `x86_64-linux` and
  `aarch64-linux` instead of a single hardcoded system

### Changed
- `startaste serve` takes `--host` (default `127.0.0.1`, unchanged behaviour).
  The dashboard has no authentication, so only widen it on a trusted network

### Fixed
- A rejected credential is now reported like a missing one — one line naming the
  variable and how to renew it, with no traceback. Rate limiting and an
  unreachable service are reported as themselves rather than blamed on the token
- One source failing no longer aborts the others: `startaste sync` reports the
  failure, syncs the remaining sources, then exits non-zero naming what failed
- `release.sh` now checks that jj can actually operate in the checkout, not just
  that it is installed — previously a plain git checkout failed part-way through
  a release, after VERSION and the changelog had been rewritten
- `release.sh --dry-run` no longer rewrites the README coverage badge, so its
  "No changes made" is true
- The database is opened in WAL mode with a busy timeout, so reading (dashboard,
  export) while a sync is writing no longer fails with "database is locked" —
  required before startaste can run as a service alongside other readers
- HN sync now follows the `More` cursor on `/upvoted` instead of a `p=` page
  parameter Hacker News ignores there — a full sync no longer loops over page
  one and discards everything it scraped
- HN page traversal is bounded (200 pages) and warns when the bound is reached
- `.env` is now loaded from the working directory by every subcommand, so
  installed builds (nix package, `nix run`, virtualenv) pick up credentials
  again instead of only working from a source checkout

## [3.0.0] - 2026-05-12

### Added
- StarTaste logo in README, dashboard nav, and favicon
- Pluggable source architecture (`startaste/sources/`)
- GitHub stars source (`startaste sync github`)
- Source registry with auto-discovery of configured sources
- `--source` and `--type` flags on export command
- Database table migration (automatic rename on first run)
- GitHub token setup instructions in README
- `startaste serve` command — local web dashboard on port 8421
- Dashboard service layer (reusable by future REST API)
- Overview page with source cards, HN upvotes/comments listings, GitHub stars listing
- Pagination on all dashboard listings
- Light/dark mode via `prefers-color-scheme`

### Changed
- **BREAKING**: Export JSON format changed to nested `{source: {type: [items]}}`
- **BREAKING**: Database tables renamed (`story` → `hn_story`, `comment` → `hn_comment`)
- HN code moved to `startaste/sources/hn/`
- `startaste sync` now accepts optional source argument
- `startaste export` uses `--source`/`--type` instead of `-s`

### Removed
- `hn2json.py` legacy script (replaced by `startaste sync` + `startaste export`)
- `hn2json.json` sample output file
- Legacy section from README

## [2.3.0] - 2026-05-12

### Added
- CLI with `startaste sync` and `startaste export` subcommands
- Auto-detecting full/incremental sync (no more `-n` page count)
- Incremental sync stops when all IDs on a page are already known
- `--format` flag on export (json default, extensible)
- Installable binary via `nix build` / `nix run`
- `pyproject.toml` for Python packaging
- pytest test suite with HTML/JSON fixtures for offline HN testing
- Coverage reporting via `pytest-cov`
- Release script runs tests with coverage before making any changes

### Fixed
- JSON export no longer overwrites stories with comments (bean startaste-1r78)

### Changed
- Restructured from monolithic `hn2json.py` into `startaste` package
- Updated all Python dependencies (beautifulsoup4, certifi, requests, urllib3, etc.)
- Upgraded peewee 3.17.0 → 4.0.5 (pinned; nix provides 3.19.0)
- Pinned dev dependencies (pytest, responses, pytest-cov)
- Fixed pyproject.toml build backend and package discovery for `nix build`
- Version detection uses `importlib.metadata` when installed as package

## [2.2.0] - 2026-05-12

### Fixed
- release.sh now pushes git tags explicitly before creating GitHub release

## [2.1.0] - 2026-05-12

### Added
- VERSION file as single source of truth for semver
- CHANGELOG.md in Keep a Changelog format
- release.sh script for major/minor/patch bumps with --dry-run support
- Release process documentation in README

### Changed
- hn2json.py reads version from VERSION file at runtime

## [2.0.0] - 2026-05-12

### Changed
- Rewritten as startaste (previously Python-Pinboard)

### Added
- Nix flake for development environment
- SQLite caching of fetched items
- JSON export with story/comment selection
- Configurable logging with rotating file handler
