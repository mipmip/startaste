# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

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
