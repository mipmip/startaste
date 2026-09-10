# release Specification

## Purpose
How a release is cut: where the version lives, how the changelog is promoted,
and which version-control and publishing steps run.

## Requirements

### Requirement: The VERSION file is the single source of truth
The version SHALL be held in a `VERSION` file at the repository root, read at runtime and at build time, so no version string is duplicated in code.

#### Scenario: Version at runtime
- **WHEN** the version is reported by the CLI
- **THEN** it matches the contents of the VERSION file

#### Scenario: File format
- **WHEN** the VERSION file is read
- **THEN** it holds a single semantic version and nothing else

### Requirement: The changelog follows Keep a Changelog
The changelog SHALL keep an `## [Unreleased]` section that accumulates entries under Added, Changed and Fixed headings, and released versions SHALL be dated sections below it.

#### Scenario: Unreleased section
- **WHEN** work is merged
- **THEN** its user-facing effect is described under Unreleased

#### Scenario: Released section
- **WHEN** a release is cut
- **THEN** the Unreleased entries become a section headed by the new version and its date

### Requirement: A release is cut by a script taking a bump level
Releasing SHALL be driven by a script that takes the bump level, and SHALL support a dry run that reports what it would do without doing it. A dry run MUST NOT write to any file, including files the script updates as a side effect of its own checks.

#### Scenario: Running a release
- **WHEN** the script is run with a bump level
- **THEN** it computes the new version, updates the VERSION file and the changelog, and performs the version-control and publishing steps

#### Scenario: Dry run
- **WHEN** the script is run in dry-run mode
- **THEN** it prints each step it would take and changes nothing

#### Scenario: Dry run leaves the working tree clean
- **WHEN** a dry run finishes on a clean working tree
- **THEN** the working tree is still clean, so its "No changes made" is literally true

#### Scenario: Invalid argument
- **WHEN** the bump level is missing or not recognised
- **THEN** it exits with usage without changing anything

### Requirement: Pre-flight checks run before anything changes
The release script SHALL verify its preconditions before modifying any file, and SHALL stop on the first failure. Verifying a tool is on PATH is not sufficient where the tool also needs a usable repository: the version-control steps run after the VERSION file and the changelog have already been rewritten, so an unusable repository must be caught up front rather than mid-release.

#### Scenario: Missing VERSION or changelog
- **WHEN** either file is absent
- **THEN** the script stops before making changes

#### Scenario: Nothing to release
- **WHEN** the Unreleased section is empty
- **THEN** the script stops rather than cutting an empty release

#### Scenario: Missing tools
- **WHEN** a required tool is not on PATH
- **THEN** the script stops and names the tool

#### Scenario: Version control is not usable
- **WHEN** a required version-control tool is on PATH but cannot operate in this checkout
- **THEN** the script stops before modifying any file and says what to do about it

#### Scenario: No file is modified by a failed pre-flight
- **WHEN** any pre-flight check fails
- **THEN** the VERSION file, the changelog and the README are unchanged

### Requirement: The version is bumped by semantic level
The script SHALL bump major, minor or patch as asked, resetting the lower components.

#### Scenario: Each level
- **WHEN** a level is given
- **THEN** the corresponding component is incremented and the components below it are reset to zero

### Requirement: Commits go through jj and tags through git
The release script SHALL commit with jj and tag with git, matching the colocated repository setup it was written for.

#### Scenario: Commit and tag
- **WHEN** a release is performed
- **THEN** it describes the change and starts a new one with jj, then creates the version tag with git

#### Scenario: Push
- **WHEN** the release is pushed
- **THEN** commits and tags both reach the remote

### Requirement: A GitHub release is created for the tag
The script SHALL create a GitHub release for the new tag, with the changelog entries for that version as its notes.

#### Scenario: Publishing
- **WHEN** the tag has been pushed
- **THEN** a GitHub release is created for it carrying that version's changelog section
