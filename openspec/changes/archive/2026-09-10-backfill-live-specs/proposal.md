<!-- Epic: .beans/startaste-4t8b--backfill-live-openspec-specs-from-archived-deltas.md -->

## Why

Five capabilities are live in `openspec/specs/` — `database`, `hn-sync`,
`mcp-server`, `nixos-service`, `paths`. Fourteen more exist only as deltas
inside archived changes, so `openspec list --specs` under-reports the project
and there is no single place that states what startaste currently does.

The practical cost has been paid twice already: a `MODIFIED` delta against a
capability with no live spec is rejected, so `fix-env-file-loading` failed to
archive until `openspec/specs/paths/spec.md` was seeded by hand.

The archived text is also not simply behind — parts of it are wrong, because
later changes superseded requirements without a formal delta. That is what makes
this a reconciliation rather than a copy.

## What Changes

Create live specs for the capabilities that only exist in the archive,
reconciled against the code rather than transcribed. Fourteen archived
capabilities become nine new live ones plus additions to an existing one:

- `cli` — absorbs `cli-sources`. One capability describes the command surface.
- `export` — absorbs `export-sources`, whose nested JSON structure replaced the
  original flat one.
- `sync` — narrowed to source-agnostic orchestration; the HN specifics it used
  to carry now live in `hn-sync`.
- `queries` — supersedes `service-layer`, which described the query functions as
  a dashboard-internal layer. They moved to `startaste/queries.py` in
  `mcp-server` and are now shared by the dashboard and the MCP server.
- `dashboard` — merges `serve-command` and `dashboard-views`.
- `source-plugin`, `github-source`, `release`, `testing` — carried over with
  corrections where the code has moved.
- `database` (already live) — gains the startup-migration requirements from
  `db-migration` and `db-rename`, which belong with how the database is opened.

Stale text being corrected rather than enshrined:

- `cli` listed `sync` and `export` as the subcommands; there are now also
  `serve`, `mcp` and `mcp-token`. Its "creates `hn.db` with Story and Comment
  tables" predates `paths` and the namespaced tables. Its HN-only credentials
  requirement predates the GitHub source and `environmentFile`.
- `cli`'s "Installable binary via flake" is dropped: `nixos-service` now
  specifies the flake surface in detail, and two capabilities claiming it is the
  problem this change exists to fix.
- `export` documented a `-s` flag replaced by `--source`/`--type`, and a
  `saved_stories`/`saved_comments` JSON shape replaced by the nested format.
- `sync` claimed it "SHALL always fetch both upvoted stories and comments …
  without requiring any flags", which the optional source argument contradicts,
  and described HN pagination as "scraping all pages until HN returns an empty
  page", which `fix-hn-upvoted-pagination` replaced with cursor traversal.
- `serve-command` fixed the dashboard to localhost; `nixos-service` added
  `--host`.
- `service-layer` located the query functions inside the dashboard.

No code changes. Where a requirement no longer matches the code, the code is
right and the text is corrected — except in two places where verification found
the *code* to be wrong, noted under Impact.

## Capabilities

### New Capabilities
- `cli`: the command surface — subcommands, arguments, and what each one is for.
- `sync`: source-agnostic sync orchestration — which sources run, and what sync
  may and may not do.
- `export`: reading the collection out as JSON, and the shape of that output.
- `queries`: the shared query layer over stored items, used by the dashboard and
  the MCP server.
- `dashboard`: the local web dashboard — serving it, and what its pages show.
- `source-plugin`: the contract a source implements and how sources are
  discovered.
- `github-source`: how GitHub stars are authenticated, fetched and stored.
- `release`: how a release is cut — versioning, changelog, tagging, publishing.
- `testing`: how the suite is built — real database, mocked HTTP, isolation.

### Modified Capabilities
- `database`: gains the automatic table-rename and database-file-rename
  requirements, which were their own archived capabilities but describe part of
  opening the database.

## Impact

- `openspec/specs/` — nine new capability directories, one extended. After this,
  every capability with a live spec is the current contract, and future deltas
  can be `MODIFIED` rather than blocked.
- No application code. Verification found two discrepancies that are code
  problems rather than spec problems. Both are recorded as beans and the
  requirements are written as the contract they should meet, so each is a known
  violation rather than a softened rule:
  - `startaste-2j0n`: `release.sh` requires `jj` (it checks for the tool and
    then runs `jj describe` / `jj new` / `jj git push`) but this checkout is a
    plain git repository, so a release fails part-way — after VERSION and the
    changelog have been modified. The `release` capability states what the
    script does; the repository not satisfying it is the bug.
  - `startaste-48g1`: the test suite writes into the real XDG directories. Run
    with a clean HOME it creates `<HOME>/state/startaste/startaste.log` and
    `<HOME>/data/startaste/`, because `conftest.py` isolates the database but
    not the paths. The `testing` capability's isolation requirement is right and
    the suite is wrong.
- `startaste-4t8b` is the epic; nothing else is blocked on this, but it removes
  the friction every future change has been paying.
