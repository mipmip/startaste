# Design: pre-release-tests

## Goals

- Catch test failures before any release artifacts are created
- Provide coverage visibility at release time
- Work in both real and dry-run modes

## Non-goals

- Enforcing a minimum coverage threshold (visibility only)
- Adding CI/CD — this is a local script gate
- Running linters or type checkers (just pytest)

## Where in the flow

Tests run after pre-flight checks but before any modifications:

```
  release.sh minor

  1. Argument parsing
  2. Pre-flight checks (files, tools, changelog)
  3. ► Run pytest with coverage ◄  ← NEW
  4. Version bump calculation
  5. Dry-run exit (if --dry-run)
  6. Changelog update
  7. Write VERSION
  8. VCS operations
  9. Push + GitHub release
```

If tests fail, the script exits before any files are modified. This is the safest insertion point.

## Test command

```bash
pytest tests/ --cov=startaste --cov-report=term-missing
```

This gives both pass/fail and coverage visibility in one command. The `set -e` in the script ensures a non-zero exit from pytest aborts the release.

## Dry-run behavior

Dry-run also runs tests — this lets you verify the test suite before committing to a release. The dry-run output will show test results followed by the "what would happen" summary.

## pytest discovery

The script needs `pytest` on PATH. Add it to the existing tool check loop alongside `jj`, `git`, `gh`.
