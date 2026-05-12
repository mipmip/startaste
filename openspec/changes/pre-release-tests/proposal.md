# Pre-release Tests and Coverage

**Bean:** startaste-xubm

## Why

The release script currently bumps, tags, and pushes without verifying that tests pass. A broken release could be published. Running tests as a pre-flight check catches this before any irreversible actions (tagging, pushing, GitHub release).

## What Changes

- Add a test + coverage step to `release.sh` as a pre-flight check (before any modifications)
- Tests must pass or the release is aborted
- Coverage report is displayed for visibility
- Dry-run also runs tests (so you can verify before committing to a release)
- Update README release section to mention the test gate

## Capabilities

### New Capabilities

_None — extending existing release capability._

### Modified Capabilities

_None — no spec-level behavior changes, just adding a pre-flight step._

## Impact

- `release.sh` — adds pytest run before version bump
- `README.md` — documents the test gate
