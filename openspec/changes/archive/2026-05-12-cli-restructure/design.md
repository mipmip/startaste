# Design: cli-restructure

## Architecture

```
  startaste (entrypoint)
       │
       ├── sync command
       │   ├── Login to HN
       │   ├── Detect mode:
       │   │   ├── DB empty → full: scrape all pages until empty page
       │   │   └── DB has items → incremental: scrape until known ID hit
       │   ├── Save new IDs to SQLite (Story + Comment tables)
       │   └── Fetch API metadata for items with body=NULL
       │
       └── export command
           ├── Read from SQLite (no network)
           ├── Filter by -s story/comment/both
           ├── Format as --format (json default)
           └── Write to -f file or stdout
```

## Sync: auto-detection logic

The sync command has no flags — it inspects the database:

```python
if Story.select().count() == 0 and Comment.select().count() == 0:
    # Full sync: scrape pages until HN returns empty
    max_page = very_high_number  # let the break-on-empty handle it
else:
    # Incremental: scrape page by page, stop when all IDs on a page are known
    # This works because HN shows upvotes in reverse chronological order
```

For incremental sync, the stop condition per type is: if every ID on a scraped page already exists in the DB, stop scraping that type. This handles the case where a user upvotes many items between syncs (spanning multiple pages).

## Export: format extensibility

Use a simple dispatch pattern:

```python
exporters = {
    "json": export_json,
}
```

New formats can be added later (csv, etc.) by adding to the dict.

## CLI structure

Use argparse with subparsers. The entrypoint is a `startaste` console script installed via the flake.

```
  startaste sync                          # just works
  startaste export                        # JSON to stdout
  startaste export -f out.json            # JSON to file
  startaste export -s story -f stories.json  # stories only
```

## Packaging

Update `flake.nix` to build a Python package with a `startaste` entrypoint. The current `hn2json.py` gets refactored into a package structure (or stays as a single module with a console_scripts entry point).
