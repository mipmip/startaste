---
# startaste-4t8b
title: backfill live openspec specs from archived deltas
status: todo
type: task
priority: high
created_at: 2026-09-10T11:14:05Z
updated_at: 2026-09-10T11:14:05Z
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
