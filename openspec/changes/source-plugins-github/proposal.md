# Source Plugins and GitHub Stars

**Bean:** startaste-32di

## Summary

Restructure startaste into a pluggable source architecture and add GitHub stars as the second source. Each source is a lightweight Python module under `startaste/sources/` with its own models, sync logic, and credentials. The CLI and export system discover sources automatically.

## Why

- startaste's vision is multi-source ("HN upvotes, GitHub stars, ...more") but the code is hardwired to HN
- Adding GitHub stars without a plugin structure would mean duplicating patterns and tangling code
- A concrete second source (GitHub) keeps the plugin design grounded rather than speculative

## What Changes

- Introduce `startaste/sources/` package with a `Source` protocol
- Move HN code into `startaste/sources/hn/` (models, scraper, sync)
- Add `startaste/sources/github/` (models, API client, sync)
- Namespace database tables per source: `story` → `hn_story`, `comment` → `hn_comment`, new `github_star`
- **BREAKING**: DB table rename requires migration on first run
- Update CLI: `startaste sync [source]`, `startaste export --source/--type`
- Update export to iterate all sources
- Add `GITHUB_TOKEN` env var for GitHub authentication

## Capabilities

### New Capabilities

- `source-plugin`: the Source protocol and discovery mechanism
- `github-source`: GitHub stars sync and storage
- `cli-sources`: CLI changes for multi-source support
- `export-sources`: export changes for multi-source output
- `db-migration`: table rename migration for existing databases

### Modified Capabilities

_None._

## Impact

- `startaste/sources/` — new package with hn/ and github/ subpackages
- `startaste/db.py` — base Doc model stays, source models move out
- `startaste/sync.py` — becomes a thin dispatcher
- `startaste/export.py` — iterates sources instead of hardcoded models
- `startaste/cli.py` — source argument on sync, --source/--type on export
- `startaste/scraper.py` — moves to `startaste/sources/hn/scraper.py`
- Database: table migration for existing users
- `.env` / docs: new `GITHUB_TOKEN` variable
