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

Right now, startaste syncs your Hacker News upvotes to a local SQLite database and exports them as JSON. The roadmap:

- **Now:** HN upvotes → SQLite → JSON export
- **Next:** GitHub stars, unified data model
- **Later:** Self-hosted REST API, AT Protocol integration (publish your taste as a feed)

## How to use

Set your Hacker News credentials:

```sh
# in .env file or as environment variables
HN_COMMENTS_ACCT=your_username
HN_COMMENTS_PW=your_password
```

### Sync

Fetch your upvoted stories and comments from Hacker News into the local database:

```sh
startaste sync
```

First run does a full sync (all pages). Subsequent runs are incremental — they stop when hitting items already in the database.

### Export

Export from the local database (no network calls):

```sh
startaste export                          # JSON to stdout
startaste export -f out.json              # JSON to file
startaste export -s story                 # stories only
startaste export -s comment -f comments.json  # comments to file
```

Options:

- `--format` — output format (default: `json`)
- `-s` / `--select` — `story`, `comment`, or both (default: both)
- `-f` / `--file` — output file path (default: stdout)

## Testing

Run the test suite:

```sh
pytest tests/ -v
```

Run with coverage report:

```sh
pytest tests/ --cov=startaste --cov-report=term-missing
```

Tests use mocked HTTP fixtures — no HN credentials or network access needed.

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
