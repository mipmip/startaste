## ADDED Requirements

### Requirement: XDG-compliant default paths
The system SHALL use XDG Base Directory paths by default for data and state.

#### Scenario: Default data directory
- **WHEN** `STARTASTE_DATA` is not set
- **THEN** data directory is `$XDG_DATA_HOME/startaste` (default: `~/.local/share/startaste`)

#### Scenario: Default state directory
- **WHEN** `STARTASTE_STATE` is not set
- **THEN** state directory is `$XDG_STATE_HOME/startaste` (default: `~/.local/state/startaste`)

#### Scenario: Default database path
- **WHEN** `STARTASTE_DB` is not set
- **THEN** database path is `$STARTASTE_DATA/startaste.db`

#### Scenario: Default log path
- **WHEN** `STARTASTE_LOG` is not set
- **THEN** log path is `$STARTASTE_STATE/startaste.log`

### Requirement: Env var overrides
All paths SHALL be overridable via environment variables.

#### Scenario: Override data directory
- **WHEN** `STARTASTE_DATA=/var/lib/startaste` is set
- **THEN** data directory is `/var/lib/startaste`

#### Scenario: Override database path directly
- **WHEN** `STARTASTE_DB=/custom/path/my.db` is set
- **THEN** database path is `/custom/path/my.db` regardless of `STARTASTE_DATA`

#### Scenario: Override log path directly
- **WHEN** `STARTASTE_LOG=/var/log/startaste/app.log` is set
- **THEN** log path is `/var/log/startaste/app.log` regardless of `STARTASTE_STATE`

### Requirement: Automatic directory creation
The system SHALL create data and state directories on first use if they don't exist.

#### Scenario: First run with no existing directories
- **WHEN** startaste runs for the first time
- **THEN** data and state directories are created with `mkdir -p` semantics

#### Scenario: Directories already exist
- **WHEN** directories already exist
- **THEN** no error occurs

### Requirement: .env loading is cwd-only
The `.env` file SHALL only be loaded from the current working directory.

#### Scenario: .env in cwd
- **WHEN** a `.env` file exists in the current working directory
- **THEN** it is loaded for credentials

#### Scenario: No .env in XDG dirs
- **WHEN** a `.env` file exists in the XDG data or config directory
- **THEN** it is NOT loaded
