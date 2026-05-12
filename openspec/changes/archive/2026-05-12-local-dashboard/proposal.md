# Local Dashboard in Browser

**Bean:** startaste-he8y

## Summary

Add a `startaste serve` command that starts a local Flask web server showing a read-only dashboard of your synced data. Clean, minimal design inspired by tangled.org. Architecture separates data access (service layer) from presentation (templates) to prepare for a future REST API.

## Why

- JSON export is useful for scripts but not for browsing your data
- A visual dashboard makes the synced data immediately useful
- Separating the service layer now avoids a refactor when adding the API later

## What Changes

- Add `startaste/dashboard/` package with Flask app, views, services, templates, static CSS
- Add `startaste serve` CLI command (port 8421, configurable via `--port`)
- Add Flask to dependencies
- Service layer returns dicts — views render HTML, future API returns JSON

## Capabilities

### New Capabilities

- `serve-command`: CLI command to start the dashboard server
- `dashboard-views`: HTML pages for overview, per-source dashboards
- `service-layer`: data query functions shared between views and future API

### Modified Capabilities

_None._

## Impact

- `startaste/dashboard/` — new package
- `startaste/cli.py` — new `serve` subcommand
- `requirements.txt` / `flake.nix` — add Flask
- `README.md` — document the serve command
