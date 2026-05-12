# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- CLI with `startaste sync` and `startaste export` subcommands
- Auto-detecting full/incremental sync (no more `-n` page count)
- Incremental sync stops when all IDs on a page are already known
- `--format` flag on export (json default, extensible)
- Installable binary via `nix build` / `nix run`
- `pyproject.toml` for Python packaging
- pytest test suite with HTML/JSON fixtures for offline HN testing
- Coverage reporting via `pytest-cov`

### Fixed
- JSON export no longer overwrites stories with comments (bean startaste-1r78)

### Changed
- Restructured from monolithic `hn2json.py` into `startaste` package

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
