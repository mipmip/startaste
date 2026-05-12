## 1. Paths module

- [x] 1.1 Create `startaste/paths.py` with `get_data_dir()`, `get_state_dir()`, `get_db_path()`, `get_log_path()`, `ensure_dirs()`
- [x] 1.2 Respect `STARTASTE_DATA`, `STARTASTE_STATE`, `STARTASTE_DB`, `STARTASTE_LOG` env vars
- [x] 1.3 Fall back to XDG Base Directory defaults

## 2. Database file migration

- [x] 2.1 Add `migrate_db_file()` to `paths.py` — rename `hn.db` → `startaste.db` at data dir
- [x] 2.2 Also check cwd for legacy `hn.db` and move to XDG path if no DB exists there yet

## 3. Integration

- [x] 3.1 Update `startaste/db.py` to use `get_db_path()` from paths module
- [x] 3.2 Update `startaste/cli.py` to use `get_log_path()` from paths module
- [x] 3.3 Call `ensure_dirs()` and `migrate_db_file()` early in CLI startup via `init_database()`

## 4. Cleanup

- [x] 4.1 Update `.gitignore` — `*.db` and `*.log` patterns already cover it, no changes needed
- [x] 4.2 Update README with data location info and env var overrides

## 5. Tests

- [x] 5.1 Add tests for `paths.py` (defaults, env var overrides, XDG overrides)
- [x] 5.2 Add tests for `migrate_db_file()` (old file renamed, cwd legacy moved, already exists)
- [x] 5.3 Update existing tests to work with new path resolution (conftest handles :memory: init)
- [x] 5.4 Run full test suite and verify all pass (48 tests passing)
