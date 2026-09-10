## 1. Verify the reconciled requirements against the code

Each item confirms the live spec being created matches what the code does. A
mismatch means either the spec text or the code is wrong — decide which, and say
so, rather than adjusting the text to fit.

- [x] 1.1 `cli`: confirm the subcommand list (`sync`, `export`, `serve`, `mcp`,
      `mcp-token`), the flags on each, `--version` reading VERSION, and that
      `mcp-token` creates no database; check against `startaste/cli.py`
- [x] 1.2 `cli`: confirm credentials resolve from the environment first and a
      cwd-discovered `.env` second, and that a missing credential names the
      variables for that source; check `cli.py`, `sources/*/__init__.py`
- [x] 1.3 `sync`: confirm only configured sources run, that no-sources exits
      with an error, and that a named unconfigured source lists its variables;
      check `startaste/sync.py`
- [x] 1.4 `sync`: confirm metadata is fetched only for items with no stored
      body, so an interrupted run resumes; check both sources' sync methods
- [x] 1.5 `export`: confirm the nested `{source: {type: [items]}}` shape, plural
      type keys, the `--source`/`--type`/`--format`/`-f` flags, and that no
      network call happens; check `startaste/export.py`
- [x] 1.6 `queries`: confirm the functions live outside the dashboard package,
      that both the dashboard and the MCP server call them, that listings clamp
      an out-of-range page, and that searches report `total` and `truncated`;
      check `startaste/queries.py` and both consumers
- [x] 1.7 `queries`: confirm aggregations skip items missing the field rather
      than counting a null value
- [x] 1.8 `dashboard`: confirm the routes exist, the bind defaults to loopback,
      there is no authentication, and no page writes; check
      `startaste/dashboard/`
- [x] 1.9 `source-plugin`: confirm the interface, the registry functions, the
      namespaced table names, and that registering a source is enough for
      export and the dashboard to include it; check `startaste/sources/`
- [x] 1.10 `github-source`: confirm token authentication, page-based walking to
      an empty page, the stored record shape, and the delay between requests;
      check `startaste/sources/github/`
- [x] 1.11 `database`: confirm both migrations happen on startup and preserve
      data; check `migrate_tables` and `migrate_db_file`
- [x] 1.12 `release`: confirm the script's pre-flight checks, bump logic,
      changelog promotion, and that it uses jj for commits and git for tags;
      check `release.sh`
- [x] 1.13 `testing`: confirm the suite runs offline, uses a real database,
      neutralises pacing delays, does not touch real data directories, and
      supports coverage; check `tests/conftest.py` and run the suite with no
      network

## 2. Record what verification turned up

- [x] 2.1 File a bean (`startaste-2j0n`) for `release.sh` requiring jj in a
      checkout that has no jj repo — it checks for the tool and then runs `jj describe`, so a release
      would fail part-way after modifying VERSION and the changelog
- [x] 2.2 Note any other mismatch found in section 1 as a bean rather than
      quietly reshaping the requirement — found one: the suite writes into the
      real XDG directories (`startaste-48g1`)

## 3. Land it

- [x] 3.1 `openspec validate --strict` passes for the change, and archiving
      creates nine new capability specs and extends `database`
- [x] 3.2 `openspec list --specs` afterwards shows every capability that has a
      live spec, and no archived capability remains unaccounted for — each is
      either live, merged into a live one, or explicitly dropped in the proposal
- [x] 3.3 `pytest tests/ -v` and `nix build .#default` still pass, confirming
      this change touched no code
