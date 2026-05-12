# Design: remove-legacy

## Goals

- Clean up the repo root by removing files that are superseded by the `startaste` package
- Remove documentation that points users to the old interface

## Non-goals

- Preserving backward compatibility with `hn2json.py` (the CLI restructure already replaced it)
- Migrating data from `hn2json.json` (the SQLite DB is the source of truth)

## What to remove

```
Root directory:
  hn2json.py       ← replaced by startaste/ package
  hn2json.json     ← sample output, not needed
  hn2json.py.log   ← log file from old script

README.md:
  ### Legacy section  ← references hn2json.py

.gitignore:
  hn2json.json     ← no longer relevant
```

## What to keep

- `hn.db` — the SQLite database is still used by the new `startaste` package
- `hn.db` in `.gitignore` — the `*.db` pattern covers it
