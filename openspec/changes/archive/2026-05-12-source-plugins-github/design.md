# Design: source-plugins-github

## Goals

- Make adding a new source (e.g. Lobste.rs, Reddit) a matter of adding a module — no changes to core
- Add GitHub stars as first proof of the plugin system
- Migrate existing HN databases transparently

## Non-goals

- External/installable plugins (sources live in the startaste package)
- A plugin config file (sources are discovered by convention)
- Changing the SQLite database file or schema beyond table renames
- AT Protocol or REST API (future work)

## Architecture

```
startaste/
├── sources/
│   ├── __init__.py          ← registry: discover_sources()
│   ├── base.py              ← Source protocol
│   ├── hn/
│   │   ├── __init__.py      ← HnSource(Source)
│   │   ├── models.py        ← HnStory(Doc), HnComment(Doc)
│   │   └── scraper.py       ← moved from startaste/scraper.py
│   └── github/
│       ├── __init__.py      ← GithubSource(Source)
│       ├── models.py        ← GithubStar(Doc)
│       └── api.py           ← GitHub API client
├── db.py                    ← base Doc, database, migration
├── cli.py                   ← source-aware CLI
├── export.py                ← source-aware export
└── sync.py                  ← thin dispatcher to source.sync()
```

## Source protocol

```python
class Source:
    name: str                           # "hn", "github"
    item_types: list[str]               # ["story", "comment"] or ["star"]
    models: list[type[Doc]]             # [HnStory, HnComment] or [GithubStar]
    env_help: dict[str, str]            # {"GITHUB_TOKEN": "GitHub personal access token"}

    def is_configured(self) -> bool:    # check env vars
        ...

    def sync(self):                     # fetch + store
        ...
```

## Source discovery

`startaste/sources/__init__.py` imports all source modules and returns configured ones:

```python
from startaste.sources.hn import HnSource
from startaste.sources.github import GithubSource

ALL_SOURCES = [HnSource(), GithubSource()]

def get_sources() -> list[Source]:
    return ALL_SOURCES

def get_configured_sources() -> list[Source]:
    return [s for s in ALL_SOURCES if s.is_configured()]

def get_source(name: str) -> Source:
    ...
```

No dynamic discovery needed — just import the known sources.

## Database tables (namespaced)

```
Before:              After:
  story        →       hn_story
  comment      →       hn_comment
                        github_star     (new)
```

Each source's models define their own table names via peewee `Meta.table_name`.

## Migration

On startup, check if old table names exist and rename:

```python
def migrate_tables():
    tables = database.get_tables()
    renames = {"story": "hn_story", "comment": "hn_comment"}
    for old, new in renames.items():
        if old in tables and new not in tables:
            database.execute_sql(f'ALTER TABLE "{old}" RENAME TO "{new}"')
```

Run this in `create_tables()` before creating any new tables.

## GitHub source

### Authentication

```sh
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

Personal access token with no special scopes needed (starring info is public for your own stars). Document creation at `github.com/settings/tokens`.

### API

GitHub REST API: `GET /user/starred` with `Accept: application/vnd.github.v3.star+json` header to get star timestamps.

Response is paginated (30 per page by default, up to 100 with `per_page`). Use `Link` header for pagination.

Each star returns:
```json
{
  "starred_at": "2024-01-15T10:30:00Z",
  "repo": {
    "id": 12345,
    "full_name": "owner/repo",
    "description": "...",
    "html_url": "https://github.com/owner/repo",
    "language": "Python",
    "stargazers_count": 1234
  }
}
```

### Sync logic

- Full sync: paginate until empty page
- Incremental: stop when all repos on a page are already known (same pattern as HN)
- Store the full repo JSON as `body`, use `starred_at` as timestamp
- `_id` is `repo.id` (numeric, stored as string like HN)

### Rate limiting

GitHub allows 5000 requests/hour authenticated. With 100 stars per page, that's 500,000 stars before hitting limits. Add a small delay (0.2s) between pages to be polite.

## CLI changes

```
startaste sync                     # sync all configured sources
startaste sync hn                  # sync HN only
startaste sync github              # sync GitHub only

startaste export                   # export all sources
startaste export --source hn       # export only HN
startaste export --type story      # export stories from any source
startaste export --source github --type star
startaste export -f out.json       # file output (unchanged)
startaste export --format json     # format flag (unchanged)
```

The old `-s story`/`-s comment` flag becomes `--source` and `--type` as separate flags.

## Export JSON structure

```json
{
  "hn": {
    "stories": [...],
    "comments": [...]
  },
  "github": {
    "stars": [...]
  }
}
```

Nested by source, then by type. This replaces the old flat `saved_stories`/`saved_comments` structure. **BREAKING** for anyone parsing the old format.
