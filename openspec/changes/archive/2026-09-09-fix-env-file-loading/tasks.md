## 1. Implementation

- [x] 1.1 In `startaste/cli.py`, load the `.env` at CLI startup before any
      subcommand or source reads configuration, resolving it from the current
      working directory: `load_dotenv(find_dotenv(usecwd=True))`
- [x] 1.2 Remove the module-level `load_dotenv()` from
      `startaste/sources/hn/scraper.py` so `.env` loading no longer depends on
      the HN module being imported

## 2. Verification

- [x] 2.1 `nix build .#default` then, from a directory containing a `.env` with
      `GITHUB_TOKEN`, run `./result/bin/startaste sync github` with the var
      unset in the shell (`env -u GITHUB_TOKEN`) and confirm it syncs instead of
      printing `Error: no sources configured` — use `STARTASTE_DB` to write to a
      throwaway database
- [x] 2.2 With no `.env` present and no credentials in the environment, confirm
      `startaste sync` still exits with the "no sources configured" message and
      no traceback
- [x] 2.3 `pytest tests/ -v` passes

## Notes

- The `tinychange` schema used by this change comes from
  https://github.com/speclib/openspec-tinychange-schema — collaborators without
  it can install it by following that repo's `AGENT_INSTALL.md`.
- Context: `load_dotenv()` was called with no argument at import of
  `startaste/sources/hn/scraper.py`. python-dotenv resolves that relative to the
  *calling file*, so for an installed build it searched upward from the store /
  site-packages path and never saw the working directory's `.env`. The existing
  `paths` spec already required cwd-only `.env` loading, so this restores
  specified behavior rather than adding new behavior.
