## MODIFIED Requirements

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
