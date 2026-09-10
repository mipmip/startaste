---
# startaste-hq9c
title: enable sqlite WAL mode before a second process reads the database
status: completed
type: bug
priority: high
created_at: 2026-09-10T15:07:17Z
updated_at: 2026-09-10T15:21:30Z
---

The database is in rollback-journal mode with no pragmas configured. Checked on
the live database:

```
journal_mode = delete
busy_timeout = 5000
```

`startaste/db.py` creates `SqliteDatabase(None)` with no `pragmas=` argument, so
nothing sets WAL. Today that is harmless because only one process ever touches
the file. It stops being harmless as soon as a second unit reads while the sync
timer writes: readers block on the writer's lock and get
`sqlite3.OperationalError: database is locked`.

That is exactly the topology being built — a oneshot sync unit
([[startaste-8khv]]) writing while the MCP server ([[startaste-qbtu]]) and the
mesh-only dashboard read.

Wanted:

- WAL journal mode plus an explicit busy timeout, set as peewee `pragmas` on the
  database so every connection gets them
- confirm the mode survives across processes (WAL is persistent in the file, so
  it needs setting once, but the pragma should still be declared)
- a check that a read during a long write transaction succeeds rather than
  raising

Context: the `save_ids` change in `untrack python bytecode, and two small sync
fixes` moved the writer from thousands of tiny autocommits to one transaction
(5.69s to 0.21s for 3000 ids). That shortens the contention window and makes it
predictable, but a reader arriving during that 0.21s still blocks without WAL.

## Summary of Changes

Shipped as openspec change `sqlite-wal-mode`, archived at
`openspec/changes/archive/2026-09-10-sqlite-wal-mode`, commit `b04eb95`.

`startaste/db.py` now constructs `SqliteDatabase(None, pragmas=...)` with
`journal_mode: wal` and `busy_timeout: 10000`. Verified against peewee that a
bare `init(path)` does not reset constructor pragmas, so no call site changed.

New live capability `database` (2 requirements, 6 scenarios) records the
behaviour. `tests/test_db_pragmas.py` covers a fresh database, conversion of an
existing rollback-journal file, a non-zero busy timeout, and a read succeeding
while another connection holds an open write transaction. The tests use a
file-based database because the shared fixture opens `:memory:`, which cannot be
in WAL mode; reverting the journal mode makes two of them fail.

Unblocks the second unit in `mipnix` change `deploy-startaste-dapperehaan`
(dashboard and MCP reading while the sync timer writes).
