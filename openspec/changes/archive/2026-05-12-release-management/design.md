# Design: release-management

## Architecture

```
  VERSION              ← single source of truth (plain text: "2.0.0")
       │
       ├── hn2json.py reads at runtime
       │     __version__ = Path("VERSION").read_text().strip()
       │
       └── release.sh reads/writes
             │
             ├── Bump version (major/minor/patch)
             ├── Update CHANGELOG.md
             ├── Write VERSION
             ├── jj describe + jj new    (commit)
             ├── git tag                 (tag in colocated repo)
             ├── jj git push --all       (push)
             └── gh release create       (GitHub release)
```

## VERSION file

Plain text file containing only the semver string, no trailing newline considerations — the script trims whitespace on read.

```
2.0.0
```

## CHANGELOG format

[Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [2.0.0] - 2026-05-12

### Changed
- Rewritten as startaste (previously Python-Pinboard)
```

Developers manually add entries under `## [Unreleased]` as they work. The release script promotes them to a versioned section.

## release.sh flow

```bash
release.sh <major|minor|patch> [--dry-run]
```

### Version bumping

Parse current version, split on `.`, increment the appropriate part, reset lower parts to 0:

```
major: 2.1.3 → 3.0.0
minor: 2.1.3 → 2.2.0
patch: 2.1.3 → 2.1.4
```

### Changelog update

Use `sed` to:
1. Replace `## [Unreleased]` with `## [Unreleased]\n\n## [X.Y.Z] - YYYY-MM-DD`
2. This preserves everything under `[Unreleased]` — it just inserts a version header between the unreleased marker and the content

### Validation

Before running, the script checks:
- `VERSION` file exists
- `CHANGELOG.md` exists and contains `## [Unreleased]`
- There is content under `[Unreleased]` (refuse to release with empty changelog)
- `jj`, `git`, and `gh` are available on PATH
- Working copy is clean (no uncommitted changes beyond what the script creates)

### --dry-run

Prints what would happen without making changes. Shows the new version, the changelog diff, and the commands that would run.

## jj + git interplay

The colocated setup means jj and git share the same `.git` directory:

```
jj describe -m "..."   ← creates the commit
jj new                  ← moves working copy to new empty change
git tag v2.1.0          ← tags the commit (jj has no native tagging)
jj git push --all       ← pushes commits + tags to remote
```

## GitHub release

```bash
gh release create "v${new_version}" \
  --title "v${new_version}" \
  --notes "${changelog_section}"
```

The release notes are extracted from the changelog: everything between `## [X.Y.Z]` and the next `## [` heading.
