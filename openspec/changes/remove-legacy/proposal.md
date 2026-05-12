# Remove Legacy Code and Docs

**Bean:** startaste-zoeg

## Why

The CLI restructure (startaste-ef1p) replaced `hn2json.py` with the `startaste` package. The old script and its output file are no longer needed and create confusion — two ways to do the same thing.

## What Changes

- Remove `hn2json.py` (replaced by `startaste sync` + `startaste export`)
- Remove `hn2json.json` (sample output from the old script)
- Remove `hn2json.py.log` (log file from old script)
- Remove the "Legacy" section from README
- Update `.gitignore` to remove `hn2json.json` entry
- Update docstrings/metadata referencing the old script

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

_None._

## Impact

- Root directory cleanup: 3 files removed
- README: Legacy section removed
- `.gitignore`: `hn2json.json` line removed
