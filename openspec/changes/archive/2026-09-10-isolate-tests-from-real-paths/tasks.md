## 1. Implementation

- [x] 1.1 Add an autouse fixture in `tests/conftest.py` that points
      `STARTASTE_DATA`, `STARTASTE_STATE`, `STARTASTE_DB` and `STARTASTE_LOG` at
      the test's `tmp_path` for every test, so isolation cannot be forgotten
- [x] 1.2 Remove the now-redundant per-test overrides in
      `tests/test_cli_serve.py`, `tests/test_db_pragmas.py` and
      `tests/test_db_readonly.py`, keeping any that assert something specific
      about a path rather than merely isolating

## 2. Verification

- [x] 2.1 Run the suite with a clean `HOME`, `XDG_DATA_HOME` and
      `XDG_STATE_HOME` and confirm nothing startaste-related is created under
      them — this currently creates `<HOME>/state/startaste/startaste.log` and
      `<HOME>/data/startaste/`
- [x] 2.2 `pytest tests/ -v` passes, including `tests/test_paths.py`, whose
      default-location tests clear the overrides themselves and must keep
      working
- [x] 2.3 Confirm the ordering of the two autouse fixtures does not matter:
      the database fixture opens `:memory:` and the path fixture only sets
      environment variables

## Notes

- Schema source: https://github.com/speclib/openspec-tinychange-schema
- Bean [[startaste-48g1]]. Measured: with a clean HOME the suite creates
  `<HOME>/state/startaste/startaste.log` and `<HOME>/data/startaste/`.
  `conftest.py` isolates the database with an autouse fixture but nothing
  isolates the paths, so any test reaching `setup_logging()` or `ensure_dirs()`
  resolves the real locations — the tests that call `cli.main()`.
- Nothing is corrupted today: the log file is opened for append and nothing is
  written to it, so the leak shows up as directories appearing on a fresh
  machine rather than as damaged data. It would become real damage the moment a
  test logged at INFO.
- No delta for `paths`: the fixture uses the `Env var overrides` requirement
  exactly as specified, which is why this needs no production code change.
- `tests/test_paths.py` already `delenv`s the variables whose defaults it
  asserts, so a global fixture setting them does not break it.
