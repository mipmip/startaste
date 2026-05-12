## ADDED Requirements

### Requirement: VERSION file as single source of truth
The project version SHALL be stored in a plain text `VERSION` file at the repo root containing only a semver string. All components that need the version MUST read from this file.

#### Scenario: Reading version at runtime
- **WHEN** `hn2json.py` is executed
- **THEN** it reads `__version__` from the `VERSION` file at runtime

#### Scenario: VERSION file format
- **WHEN** the `VERSION` file is read
- **THEN** it contains only a semver string (e.g. `2.0.0`) with no other content

### Requirement: Keep a Changelog format
The project SHALL maintain a `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com/) format.

#### Scenario: Unreleased section exists
- **WHEN** a developer opens `CHANGELOG.md`
- **THEN** there is a `## [Unreleased]` section at the top for adding changes as they work

#### Scenario: Released version format
- **WHEN** a version has been released
- **THEN** its section has the format `## [X.Y.Z] - YYYY-MM-DD`

### Requirement: Release script interface
The `release.sh` script SHALL accept a bump type and an optional dry-run flag.

#### Scenario: Running a release
- **WHEN** user runs `release.sh minor`
- **THEN** system bumps the minor version, updates changelog, commits, tags, pushes, and creates a GitHub release

#### Scenario: Dry run
- **WHEN** user runs `release.sh minor --dry-run`
- **THEN** system prints what would happen without making any changes

#### Scenario: Invalid argument
- **WHEN** user runs `release.sh` with no argument or an invalid argument
- **THEN** system exits with non-zero status and shows usage

### Requirement: Pre-flight validation
The release script SHALL validate preconditions before making any changes.

#### Scenario: Missing VERSION file
- **WHEN** `VERSION` file does not exist
- **THEN** system exits with an error

#### Scenario: Missing changelog
- **WHEN** `CHANGELOG.md` does not exist or has no `## [Unreleased]` section
- **THEN** system exits with an error

#### Scenario: Empty unreleased section
- **WHEN** there are no entries under `## [Unreleased]`
- **THEN** system refuses to release and exits with an error

#### Scenario: Missing tools
- **WHEN** `jj`, `git`, or `gh` are not on PATH
- **THEN** system exits with an error naming the missing tool

### Requirement: Semver bump logic
The release script SHALL bump versions according to semantic versioning rules.

#### Scenario: Major bump
- **WHEN** user runs `release.sh major` with current version `2.1.3`
- **THEN** new version is `3.0.0`

#### Scenario: Minor bump
- **WHEN** user runs `release.sh minor` with current version `2.1.3`
- **THEN** new version is `2.2.0`

#### Scenario: Patch bump
- **WHEN** user runs `release.sh patch` with current version `2.1.3`
- **THEN** new version is `2.1.4`

### Requirement: Changelog update on release
The release script SHALL promote unreleased entries to a versioned section.

#### Scenario: Changelog after release
- **WHEN** `release.sh minor` completes successfully
- **THEN** `CHANGELOG.md` has a fresh empty `## [Unreleased]` section above a new `## [2.2.0] - YYYY-MM-DD` section containing the previously unreleased entries

### Requirement: VCS operations use jj for commits and git for tags
The release script SHALL use jj for committing and git for tagging, compatible with the colocated setup.

#### Scenario: Commit and tag
- **WHEN** release script runs VCS operations
- **THEN** it runs `jj describe -m "release vX.Y.Z"`, then `jj new`, then `git tag vX.Y.Z`

#### Scenario: Push
- **WHEN** release script pushes
- **THEN** it runs `jj git push --all` to push both commits and tags

### Requirement: GitHub release creation
The release script SHALL create a GitHub release with notes extracted from the changelog.

#### Scenario: GitHub release
- **WHEN** release script creates a GitHub release
- **THEN** it uses `gh release create vX.Y.Z` with the changelog section for that version as the body
