## 1. Version infrastructure

- [x] 1.1 Create `VERSION` file at repo root with `2.0.0`
- [x] 1.2 Update `hn2json.py` to read `__version__` from `VERSION` file at runtime
- [x] 1.3 Add `VERSION` to `.gitignore` exclusion (ensure it's tracked)

## 2. Changelog

- [x] 2.1 Create `CHANGELOG.md` with Keep a Changelog format and initial `[2.0.0]` entry
- [x] 2.2 Add `[Unreleased]` section above `[2.0.0]`

## 3. Release script

- [x] 3.1 Create `release.sh` with argument parsing (`major`/`minor`/`patch`, `--dry-run`)
- [x] 3.2 Implement pre-flight checks (files exist, tools on PATH, unreleased content present)
- [x] 3.3 Implement semver bump logic
- [x] 3.4 Implement changelog update via sed
- [x] 3.5 Implement VCS operations (jj describe, jj new, git tag)
- [x] 3.6 Implement push and GitHub release creation
- [x] 3.7 Implement `--dry-run` mode

## 4. Documentation

- [x] 4.1 Update README with release process instructions
