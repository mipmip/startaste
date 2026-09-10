---
# startaste-4t8b
title: backfill live openspec specs from archived deltas
status: completed
type: task
priority: high
created_at: 2026-09-10T11:14:05Z
updated_at: 2026-09-10T18:48:25Z
---

Only 2 of 16 capabilities exist in `openspec/specs/`: `paths` and `hn-sync`.
The other 14 live solely inside archived change deltas
(`cli cli-sources dashboard-views db-migration db-rename export
export-sources github-source release serve-command service-layer
source-plugin sync testing`), so `openspec list --specs` under-reports the
project and there is no single place that states current behaviour.

Concrete consequence: a `MODIFIED` delta against a capability with no live spec
is rejected — `openspec archive` failed with "target spec does not exist; only
ADDED requirements are allowed for new specs" while archiving
`fix-env-file-loading`, and `openspec/specs/paths/spec.md` had to be seeded by
hand from the `2026-05-12-configurable-data-locations` archive.

This is not a copy job. Some archived text has been superseded without a formal
delta — the `sync` capability from `2026-05-12-cli-restructure` still says
"`startaste sync` SHALL always fetch both upvoted stories and comments ...
without requiring any flags", which `cli-sources` (optional source argument)
contradicts. Backfilling means reconciling those before they become the live
spec.

Scope to decide in the proposal:

- which capabilities to backfill, and whether some should merge (the HN parts of
  `sync` arguably belong with `hn-sync`)
- how superseded requirements are resolved and recorded
- whether `openspec/specs/` becomes the norm going forward, or the project
  deliberately stays archive-only (in which case future deltas must be
  `ADDED`-only, and that should be written down)

## Summary of Changes

Shipped as openspec change `backfill-live-specs`, archived at
`openspec/changes/archive/2026-09-10-backfill-live-specs`, commit `9266355`.

`openspec/specs/` went from 5 capabilities to 14, all validating: cli,
dashboard, database, export, github-source, hn-sync, mcp-server, nixos-service,
paths, queries, release, source-plugin, sync, testing. 48 requirements added.

Fourteen archived capabilities became nine new live ones plus requirements on
`database`. Merges: `cli` absorbed `cli-sources`; `export` absorbed
`export-sources`; `serve-command` + `dashboard-views` became `dashboard`;
`db-migration` + `db-rename` became part of `database`; `service-layer` became
`queries`, since `mcp-server` had moved those functions out of the dashboard
package. `cli`'s "installable binary via flake" was dropped as superseded by
`nixos-service`. The archived `paths` delta was already superseded by the live
`paths`.

Stale text was corrected, not carried over — the subcommand list, `hn.db` and
the pre-namespace table names, the `-s` export flag, the
`saved_stories`/`saved_comments` shape, "always fetches both without flags", and
page-counting HN pagination. Requirements are now phrased against observable
behaviour rather than function names, which is what allowed a refactor to
falsify a spec.

Every requirement was verified against the code. Two verifications found the
code wrong rather than the text, and are tracked as beans with the requirements
left stating the intended contract: [[startaste-2j0n]] (`release.sh` needs jj in
a plain git checkout, so a release fails after modifying VERSION and the
changelog) and [[startaste-48g1]] (the suite creates
`<HOME>/state/startaste/startaste.log` and `<HOME>/data/startaste/`, verified
with a clean HOME).

No application code changed: 128 tests pass, `nix build` succeeds, and the suite
also passes inside a network namespace with no connectivity — which verified the
`testing` capability's offline requirement.
