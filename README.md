# Startaste

Coverage: 83%

**Your stars are your taste.**

Startaste is a self-hostable tool for owning your stars, upvotes, and favorites across the web. Platforms like Hacker News and GitHub don't let you easily access or export your own curation data. Startaste works around that — it logs in, dumps your data, and gives it back to you.

## Vision

```
  Sources             Store            Outputs

  HN upvotes ──┐
                ├──▶  SQLite  ──▶  REST API
  GitHub stars ─┘     (yours)      AT Proto feed
  ...more                          JSON export
```

Startaste syncs your Hacker News upvotes and GitHub stars to a local SQLite database and exports them as JSON. The architecture is pluggable — new sources can be added as modules under `startaste/sources/`.

- **Now:** HN upvotes + GitHub stars → SQLite → JSON export
- **Later:** Self-hosted REST API, AT Protocol integration (publish your taste as a feed)

## How to use

### Credentials

Set credentials for the sources you want to use in `.env` or as environment variables:

```sh
# Hacker News
HN_COMMENTS_ACCT=your_username
HN_COMMENTS_PW=your_password

# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

**GitHub token setup:**

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Name it (e.g. `startaste`) — **no scopes needed**, a scopeless token can read your own stars
4. Copy the token into your `.env` as `GITHUB_TOKEN`

Alternatively, use a **fine-grained token** at [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new) with Account permissions → **Starring → Read-only**.

Only configured sources are synced. If you only set HN credentials, only HN is synced.

### Sync

Fetch your data from configured sources into the local database:

```sh
startaste sync                    # sync all configured sources
startaste sync hn                 # sync HN only
startaste sync github             # sync GitHub only
```

First run does a full sync. Subsequent runs are incremental — they stop when hitting items already in the database.

### Export

Export from the local database (no network calls):

```sh
startaste export                              # all sources, JSON to stdout
startaste export --source hn                  # HN only
startaste export --source github --type star  # GitHub stars only
startaste export -f out.json                  # to file
```

Options:

- `--format` — output format (default: `json`)
- `--source` — filter by source (`hn`, `github`)
- `--type` — filter by item type (`story`, `comment`, `star`)
- `-f` / `--file` — output file path (default: stdout)

### Sources

| Source | Item Types | Env Vars |
|--------|-----------|----------|
| `hn` | `story`, `comment` | `HN_COMMENTS_ACCT`, `HN_COMMENTS_PW` |
| `github` | `star` | `GITHUB_TOKEN` |

Adding a new source: create a module under `startaste/sources/<name>/` implementing the `Source` protocol (see `startaste/sources/base.py`), then register it in `startaste/sources/__init__.py`.

## Testing

Run the test suite:

```sh
pytest tests/ -v
```

Run with coverage report:

```sh
pytest tests/ --cov=startaste --cov-report=term-missing
```

Tests use mocked HTTP fixtures — no credentials or network access needed.

## Releasing

Bump version, update changelog, tag, and create a GitHub release:

```sh
./release.sh <major|minor|patch>
```

Preview what would happen without making changes:

```sh
./release.sh minor --dry-run
```

The script runs the full test suite with coverage before making any changes. If tests fail, the release is aborted. It then reads the current version from `VERSION`, updates `CHANGELOG.md` (promoting `[Unreleased]` entries to the new version), commits with jj, tags with git, pushes, and creates a GitHub release.

Add changelog entries under `## [Unreleased]` in `CHANGELOG.md` as you work.

## History

Originally developed on iPad by Luciano Fiandesio with Pythonista, modified for JSON output by John David Pressman, rewritten by Kraktus, and continued by Pim Snel as startaste.

## License

BSD 3-Clause — see [LICENSE](LICENSE).
