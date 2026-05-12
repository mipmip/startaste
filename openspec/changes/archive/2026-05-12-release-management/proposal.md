# Release Management

**Bean:** startaste-wwn3

## Summary

Add release management to startaste: a `VERSION` file as single source of truth, a Keep a Changelog format `CHANGELOG.md`, and a bash `release.sh` script that bumps versions, updates the changelog, commits with jj, tags with git, and creates GitHub releases.

## Why

- No versioning scheme — `__version__ = "2"` is not semver
- No changelog — contributors and users can't see what changed between versions
- No release process — creating a release is manual and undocumented
- Need to work within the colocated jj+git setup

## What changes

- Add `VERSION` file at repo root (single source of truth)
- Add `CHANGELOG.md` in Keep a Changelog format with `[Unreleased]` section
- Add `release.sh` bash script for major/minor/patch bumps
- Update `hn2json.py` to read version from `VERSION` file at runtime
- Starting version: `2.0.0`

## Scope

```
  release.sh <major|minor|patch> [--dry-run]

  1. Read VERSION file              → 2.0.0
  2. Bump per argument              → 2.1.0
  3. Update CHANGELOG.md
     ├── [Unreleased] → [2.1.0] - 2026-05-12
     └── Insert fresh [Unreleased] section
  4. Write new VERSION
  5. jj describe -m "release v2.1.0"
  6. jj new
  7. git tag v2.1.0
  8. jj git push --all
  9. gh release create v2.1.0
     └── Body extracted from changelog section
```

## Capabilities

- **release** — version bumping, changelog management, tagging, GitHub release creation

## Non-goals

- Automated changelog generation from commit messages (entries are manual)
- CI/CD integration (this is a local script)
- npm/PyPI publishing
