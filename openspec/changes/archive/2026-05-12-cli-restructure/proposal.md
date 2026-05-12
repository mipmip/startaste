# CLI Restructure: sync and export subcommands

**Bean:** startaste-ef1p

## Summary

Restructure startaste from a monolithic script (`hn2json.py`) into a proper CLI with two subcommands: `startaste sync` and `startaste export`. Install as a binary via `flake.nix`.

## Why

- The current `-n` (number of pages) flag is a leaky abstraction — users shouldn't need to know about HN pagination
- Syncing and exporting are separate concerns tangled into one command
- There's no way to do an incremental update without guessing a page count
- The script isn't installable as a proper CLI tool

## What changes

- Replace `hn2json.py` with a `startaste` CLI using argparse subcommands
- `startaste sync`: auto-detects full vs incremental based on DB state
- `startaste export`: reads from SQLite, outputs JSON (extensible to other formats)
- Package as an installable bin via `flake.nix`

## Scope

```
  startaste sync
  ├── DB empty?  → full sync (scrape all pages until empty)
  ├── DB has items? → incremental (stop when hitting known ID)
  └── Always syncs both stories and comments

  startaste export [--format=json] [-s story/comment] [-f file]
  ├── Reads from SQLite only, no network calls
  ├── --format=json (default), extensible
  ├── -s to filter story/comment/both (default: both)
  └── -f for file output, otherwise stdout
```

## Capabilities

- **cli** — subcommand-based entrypoint, installable binary, credential handling
- **sync** — auto-detecting full/incremental sync from HN to SQLite
- **export** — format-extensible export from SQLite to file/stdout

## Non-goals

- Adding new data sources (GitHub stars, etc.)
- Changing the SQLite schema
- Building the REST API or AT Protocol feed
