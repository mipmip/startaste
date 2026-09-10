## Context

See proposal.md — Why for the motivation and the two measurements that bound it.

Constraints that shape the approach:

- `export.py` builds its output by zipping `src.models` with `src.item_types`
  (`startaste/export.py:30`), and `db.py::_get_all_models()` collects tables to
  create from the same `source.models` lists. Anything added to a source's
  `models` therefore appears in exports and the dashboard. The state model must
  live outside those lists and be registered separately.
- `Source` (`startaste/sources/base.py`) has no notion of a listing. HN walks
  two (`stories`, `comments`) inside `sync()`; GitHub walks one (`stars`).
  `item_types` is close but is about item shape for export, not about walks, and
  HN's `item_types` are `["story", "comment"]` — singular item names, not
  listing names. Overloading it would couple export naming to walk naming.
- `Doc.save_ids` is idempotent (`IntegrityError` per row is swallowed), so
  re-storing a listing's IDs during a resumed full walk is safe.
- `migrate_tables()` already runs on every `init_database()` and is where the
  `story` → `hn_story` renames live, so it is the natural home for seeding.

## Goals / Non-Goals

**Goals:**

- One shared mechanism for both sources; no per-source state handling.
- Upgrading an existing database is invisible: no unexpected full walk, no
  manual step.
- The state is inspectable with plain SQL, since it changes how sync behaves and
  a wrong record is worth being able to see and correct.

**Non-Goals:**

- Cursor persistence and mid-listing resume. Chosen against: the cursor carries
  a `time=` token whose validity between runs is unverified, and under re-walk
  resume the ~40s is re-spent either way. `sync-state` is the prerequisite if
  this is ever wanted.
- Per-page ID persistence. It buys nothing under re-walk resume and would put
  rows in the database for a walk that never finished.
- Any change to the metadata phase, which already resumes via `list_empty`.

## Decisions

**A table in the sync database, not a file in the state directory.** The record
describes the contents of one database, so it should travel with it — copying or
pointing `STARTASTE_DB` at another file must not carry a stale record along.
Alternative considered: `~/.local/state/startaste/sync_state.json`, which avoids
a schema change but drifts the moment the database moves, and `STARTASTE_DB` is
an advertised override.

**Keyed by `(source, listing)`, with `complete` and `updated_at`.** Two string
columns rather than one composite key, so the record is greppable and a listing
can be reset by hand (`update sync_state set complete = 0 where source = 'hn'`)
to force a re-walk — the escape hatch that replaces "delete the database".

**Registered outside `source.models`.** The model is added to the table-creation
list directly in `db.py`, not to any source's `models`. This is what keeps it out
of exports and the dashboard, and it means the requirement about not exposing
completion records is satisfied by construction rather than by filtering.

**`listings` on the `Source` protocol, distinct from `item_types`.** Each source
declares its listing names (`hn` → `["stories", "comments"]`, `github` →
`["stars"]`) alongside the model each listing fills. Alternative considered:
reuse `item_types`. Rejected because those are singular item names consumed by
export's pluralizer, and a source could one day walk two listings that produce
the same item type, or one listing producing two types.

**The mode is resolved once per listing, before its walk.** `_sync_type` already
receives `is_full`; it changes from a caller-computed row count to a lookup. The
completion write happens after the store, in the same place, so "walk finished
and stored" is a single point in the code rather than a property to maintain
across two paths.

**A full walk drops the all-known stop condition entirely** rather than
counting how many pages were already known. The stop condition exists to keep
incremental runs short; during a full walk it is exactly the bug being fixed.

**Seeding runs inside the existing table migration.** After `create_tables`, if
the state table is empty, insert `complete = 1` for every listing whose model
already has rows. Empty state plus populated tables is unambiguous — it can only
mean a database from before this change — and doing it there means the seed
happens before any source consults the state. It runs once: after seeding, the
table is no longer empty.

## Risks / Trade-offs

- **A listing recorded complete when it is not** (e.g. a future code path
  writes the record too early) silently truncates future syncs, which is the
  original bug wearing a different hat → the record is written at exactly one
  place, immediately after the store, and a test asserts no record is written
  when the walk raises. The SQL escape hatch above is the manual recovery.
- **Seeding is a heuristic**: a database interrupted mid-walk *under the old
  code* has no partial listing (storage was already atomic), so seeding is
  correct for it; but a database left by some other tool with partial rows would
  be seeded complete and stay truncated → accepted, and called out in the
  changelog so the one-line SQL reset is discoverable.
- **A full walk now costs a full walk.** A listing recorded incomplete is
  re-walked from page 1 every run until one run finishes it. For an account
  whose walk is long (a 50k-item listing is ~1600 pages, ~13 min), repeated
  interruptions make no progress → the page bound already warns when a walk
  stops early, and cursor resume remains available as a follow-up; the
  `sync-state` record is what makes it safe to add.
- **Two more columns to keep honest across sources.** GitHub's listing is walked
  by API page rather than by cursor, so "reached the last page" means a
  different thing in each source → the requirement is phrased as reaching the
  end of the listing, and each source decides what that means for its own
  pagination.

## Migration Plan

1. Ship the state table and register it for creation; `init_database()` creates
   it on first run for every existing database.
2. Seed as described, inside `migrate_tables()`, before any source reads state.
3. No rollback step is needed: reverting the code leaves an unused table, and
   the old row-count inference still works on the data as it stands. Dropping
   the table is optional and safe.
