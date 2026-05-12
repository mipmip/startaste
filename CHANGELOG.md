# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

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
