## 1. Implementation

- [x] 1.1 Pass `pragmas` to the `SqliteDatabase` in `startaste/db.py`
      (`journal_mode: wal`, a non-zero `busy_timeout`), so every connection gets
      them without changing any call site

## 2. Verification

- [x] 2.1 Test that `init_database()` leaves `pragma journal_mode` reporting
      `wal` on a fresh database
- [x] 2.2 Test that a database file created in rollback-journal mode is
      converted to WAL when opened
- [x] 2.3 Test that a read succeeds while another connection holds an open write
      transaction — the failure this change exists to prevent
- [x] 2.4 Test that `pragma busy_timeout` is non-zero
- [x] 2.5 `pytest tests/ -v` passes and `nix build .#default` succeeds
- [x] 2.6 Update CHANGELOG.md under Unreleased

## Notes

- Schema source: https://github.com/speclib/openspec-tinychange-schema
- Measured before writing this: the live database reports
  `journal_mode = delete` and `startaste/db.py` constructs
  `SqliteDatabase(None)` with no `pragmas=` argument, so nothing sets WAL.
- `database.init(db_path)` is called with no pragmas, which raised the question
  of whether `init()` resets pragmas given in the constructor. Verified against
  peewee that it does not: constructor pragmas plus a bare `init(path)` yields
  `('wal',)` and `(10000,)`. So the fix is confined to the constructor.
- Why now: the deployment on dapperehaan runs a sync timer alongside an MCP
  server and a dashboard reading the same file
  (`mipnix` change `deploy-startaste-dapperehaan`). Its spec defers enabling any
  second unit until this lands.
