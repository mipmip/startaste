# Configurable Data Locations

**Bean:** startaste-pg9g

## Summary

Move database, logs, and future config out of the current working directory and into XDG-compliant paths. All paths are overridable via env vars to support future daemon/service deployment. Rename `hn.db` → `startaste.db` to reflect multi-source usage.

## Why

- Database and log files currently land in cwd, which scatters files when running as an installed binary
- `hn.db` is a misleading name now that the DB stores GitHub stars too
- Future daemon/service mode will need `/var/lib/startaste` and `/var/log/startaste` — the same env var override mechanism serves both use cases

## What Changes

- Add `startaste/paths.py` module with XDG-compliant path resolution
- Update `db.py` to use resolved database path
- Update `cli.py` to use resolved log path
- Auto-create directories on first use
- Rename `hn.db` → `startaste.db` with automatic file migration
- Add `STARTASTE_DATA`, `STARTASTE_STATE`, `STARTASTE_DB`, `STARTASTE_LOG` env vars
- `.env` loading stays cwd-only (unchanged)

## Capabilities

### New Capabilities

- `paths`: XDG path resolution with env var overrides
- `db-rename`: `hn.db` → `startaste.db` file migration

### Modified Capabilities

_None._

## Impact

- `startaste/paths.py` — new module
- `startaste/db.py` — uses resolved DB path
- `startaste/cli.py` — uses resolved log path
- Existing `hn.db` files automatically renamed on first run
- `.gitignore` — update patterns
