# Update Python Dependencies

**Bean:** startaste-mzsl

## Why

All pinned dependencies are from late 2023 and are 2+ years behind. This includes security-relevant packages (certifi, urllib3, requests) and a major version bump for peewee (3→4). Keeping deps current reduces vulnerability surface and ensures compatibility with modern Python.

## What Changes

- Update all pinned versions in `requirements.txt` to latest
- Pin the currently unpinned dev dependencies (pytest, responses, pytest-cov)
- **BREAKING**: Upgrade peewee 3.17.0 → 4.0.5 (major version, may require code changes)
- Update `flake.lock` to pick up new nixpkgs versions
- Verify all tests pass after upgrade

## Capabilities

### New Capabilities

_None — this is a maintenance change._

### Modified Capabilities

_None — no spec-level behavior changes._

## Impact

- `requirements.txt` — all versions updated
- `flake.lock` — refreshed
- `startaste/db.py` — may need changes for peewee 4.x API
- `startaste/sync.py` — may need changes if peewee 4.x affects queries
- Test suite must pass after upgrade
