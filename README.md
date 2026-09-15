<p align="center">
  <img src="assets/logo.png" alt="StarTaste" width="200">
</p>

Coverage: 95%

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

### Dashboard

Browse your synced data in a local web UI:

```sh
startaste serve                   # http://localhost:8421
startaste serve --port 9000       # custom port
```

### MCP server

Expose your collection to MCP clients (Claude and friends) over streamable
HTTP. The server opens the database **read-only** — no tool it offers can change
your data — so it is safe to put behind an HTTPS reverse proxy. Run
`startaste sync` first; the MCP server refuses to create a database.

**1. Mint a token.** Tokens are never stored in recoverable form, only as
SHA-256 hashes, so the raw value is shown exactly once:

```sh
startaste mcp-token --name laptop
```

It prints the token plus the record to add to your tokens file. That file is
JSON — either a bare list of records, or `{"tokens": [...]}`:

```json
[{"name": "laptop", "hash": "b92e06f3…e669", "scopes": ["read"]}]
```

**2. Serve it.**

```sh
startaste mcp --tokens-file /var/lib/startaste/tokens.json
startaste mcp --tokens-file tokens.json --port 9100
startaste mcp --tokens-file tokens.json --allowed-host taste.example.com
```

Options:

- `--tokens-file` — **required**, path to the JSON token records above. With no
  readable file the server exits rather than serving unauthenticated.
- `--host` — address to bind (default: `127.0.0.1`). TLS terminates upstream.
- `--port` — port to serve on (default: `8766`).
- `--allowed-host` — public hostname this server is reached by. Repeatable.
  Needed when an HTTPS reverse proxy fronts it: the transport checks the `Host`
  header against an allow-list to block DNS rebinding, and a forwarded public
  hostname is otherwise refused with `421`. Loopback and the bound address are
  always allowed, so a local or mesh-only deployment needs nothing here.

Two paths are served:

| Path       | Auth                    | Purpose                             |
|------------|-------------------------|-------------------------------------|
| `/mcp`     | `Authorization: Bearer` | The MCP endpoint                    |
| `/healthz` | none                    | Liveness, for a proxy or monitoring |

Anything else answers `404`. Point your client at `https://<host>/mcp` with the
token as a bearer credential.

**3. What a client gets.**

| Tool             | Returns                                                     |
|------------------|-------------------------------------------------------------|
| `overview`       | Per-source counts and when each last had new data           |
| `search_stars`   | Starred repos by text, language and/or topic                |
| `search_upvotes` | Upvoted HN items by text, optionally story- or comment-only |
| `get_item`       | One stored item in full, by source and id                   |
| `top_topics`     | Most common GitHub topics, by count                         |
| `top_languages`  | Most common languages across starred repos                  |
| `top_domains`    | Most upvoted HN domains, by count                           |

Results are bounded by a `limit` (default 20) and say whether they were
truncated.

The two servers listen on different ports and are enabled independently:

| Server    | Command           | Default port | Auth         |
|-----------|-------------------|--------------|--------------|
| Dashboard | `startaste serve` | `8421`       | none (local) |
| MCP       | `startaste mcp`   | `8766`       | bearer token |

### Sources

| Source   | Item Types         | Env Vars                             |
|----------|--------------------|--------------------------------------|
| `hn`     | `story`, `comment` | `HN_COMMENTS_ACCT`, `HN_COMMENTS_PW` |
| `github` | `star`             | `GITHUB_TOKEN`                       |

Adding a new source: create a module under `startaste/sources/<name>/` implementing the `Source` protocol (see `startaste/sources/base.py`), then register it in `startaste/sources/__init__.py`.

### Data locations

By default, startaste follows the [XDG Base Directory](https://specifications.freedesktop.org/basedir-spec/latest/) convention:

| File      | Default path                             | Env var override  |
|-----------|------------------------------------------|-------------------|
| Database  | `~/.local/share/startaste/startaste.db`  | `STARTASTE_DB`    |
| Log       | `~/.local/state/startaste/startaste.log` | `STARTASTE_LOG`   |
| Data dir  | `~/.local/share/startaste/`              | `STARTASTE_DATA`  |
| State dir | `~/.local/state/startaste/`              | `STARTASTE_STATE` |

Directories are created automatically on first run. For service/daemon deployment, override via env vars (e.g. `STARTASTE_DATA=/var/lib/startaste`).

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
