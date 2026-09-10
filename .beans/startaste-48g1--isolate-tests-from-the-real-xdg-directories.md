---
# startaste-48g1
title: isolate tests from the real XDG directories
status: completed
type: bug
priority: normal
created_at: 2026-09-10T18:47:24Z
updated_at: 2026-09-10T19:03:10Z
---

The test suite writes into the real XDG directories. Verified by running it with
a clean HOME:

```
env HOME=$T XDG_DATA_HOME=$T/data XDG_STATE_HOME=$T/state pytest tests/
-> created  <HOME>/state/startaste/startaste.log
-> created  <HOME>/data/startaste/
```

`tests/conftest.py` isolates the database (an autouse fixture opens `:memory:`)
but nothing isolates the paths, so any test that reaches `setup_logging()` or
`ensure_dirs()` — the ones that call `cli.main()` — resolves the real
`STARTASTE_DATA` / `STARTASTE_STATE` and opens the real log file. It appends
nothing today, so no data is corrupted, but on a fresh machine running the suite
creates those directories, and a test that logged at INFO would write into the
developer's real log.

This violates the "Tests are isolated from each other and from the machine"
requirement in `openspec/specs/testing/spec.md` — the requirement is right and
the suite is wrong.

Fix: one autouse fixture in `conftest.py` pointing `STARTASTE_DATA`,
`STARTASTE_STATE`, `STARTASTE_DB` and `STARTASTE_LOG` at `tmp_path` for every
test, so no test can reach a real path by forgetting to override it. The
per-test overrides in `test_cli_serve.py`, `test_db_pragmas.py`,
`test_db_readonly.py` and `test_paths.py` then become redundant.

## Summary of Changes

Shipped as openspec change `isolate-tests-from-real-paths`, archived at
`openspec/changes/archive/2026-09-10-isolate-tests-from-real-paths`.

One autouse fixture in `tests/conftest.py` points `STARTASTE_DATA`,
`STARTASTE_STATE`, `STARTASTE_DB` and `STARTASTE_LOG` at each test's `tmp_path`,
so isolation is enforced centrally rather than arranged per test. It uses the
documented env overrides, so no production code changed.

The per-test overrides in `test_cli_serve.py`, `test_db_pragmas.py` and
`test_db_readonly.py` are gone. One deliberate override stayed, with a comment
saying why: the missing-database test points `STARTASTE_DB` at a path with no
file, which is the behaviour it asserts rather than isolation.

Verified with a clean HOME: the suite now creates nothing startaste-related
under it, where before it created `<HOME>/state/startaste/startaste.log` and
`<HOME>/data/startaste/`. 128 tests pass, coverage 94%, and `test_paths.py`'s
default-location tests still pass because they clear the overrides themselves.
Fixture ordering was checked by swapping the two autouse fixtures and re-running
— it does not matter.

The `testing` capability's isolation requirement now also states that isolation
is enforced by default, so a test that configures nothing still cannot reach a
real path.
