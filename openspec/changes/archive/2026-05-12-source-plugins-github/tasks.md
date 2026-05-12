## 1. Source plugin infrastructure

- [x] 1.1 Create `startaste/sources/__init__.py` with registry (get_sources, get_configured_sources, get_source)
- [x] 1.2 Create `startaste/sources/base.py` with Source protocol/base class
- [x] 1.3 Create `startaste/sources/hn/__init__.py` with HnSource class
- [x] 1.4 Move `startaste/scraper.py` to `startaste/sources/hn/scraper.py`, update imports
- [x] 1.5 Create `startaste/sources/hn/models.py` with HnStory(Doc), HnComment(Doc) using table names `hn_story`, `hn_comment`
- [x] 1.6 Move HN sync logic into HnSource.sync(), remove old `startaste/sync.py` HN-specific code

## 2. Database migration

- [x] 2.1 Add `migrate_tables()` to `startaste/db.py` that renames `story` → `hn_story`, `comment` → `hn_comment`
- [x] 2.2 Update `create_tables()` to run migration first, then create all source tables

## 3. GitHub source

- [x] 3.1 Create `startaste/sources/github/__init__.py` with GithubSource class
- [x] 3.2 Create `startaste/sources/github/models.py` with GithubStar(Doc) using table name `github_star`
- [x] 3.3 Create `startaste/sources/github/api.py` with GitHub API client (token auth, pagination, star timestamps)
- [x] 3.4 Implement GithubSource.sync() with full/incremental support

## 4. CLI updates

- [x] 4.1 Update `startaste sync` to accept optional `[source]` argument, dispatch to source.sync()
- [x] 4.2 Update `startaste export` to use `--source` and `--type` flags instead of `-s`
- [x] 4.3 Show helpful errors for unconfigured or unknown sources

## 5. Export updates

- [x] 5.1 Update export to nested JSON structure: `{source: {type: [items]}}`
- [x] 5.2 Support `--source` and `--type` filtering

## 6. Sync dispatcher

- [x] 6.1 Rewrite `startaste/sync.py` as thin dispatcher that calls source.sync() for each configured source

## 7. Documentation

- [x] 7.1 Update README with GitHub token setup instructions
- [x] 7.2 Update README with new CLI usage (sync [source], export --source/--type)
- [x] 7.3 Document source architecture for future contributors

## 8. Tests

- [x] 8.1 Add GitHub API fixtures (starred repos pages, empty page)
- [x] 8.2 Add tests for GithubSource.sync() (full, incremental, stop condition)
- [x] 8.3 Add tests for source registry (get_sources, get_configured_sources, get_source)
- [x] 8.4 Update existing HN tests for new module paths
- [x] 8.5 Add tests for DB migration (old tables renamed, already migrated, fresh DB)
- [x] 8.6 Update export tests for new nested JSON structure
- [x] 8.7 Run full test suite and verify all pass (33 tests, all passing)
