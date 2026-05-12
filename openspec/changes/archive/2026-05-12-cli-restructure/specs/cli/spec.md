## ADDED Requirements

### Requirement: Subcommand-based CLI entrypoint
The `startaste` binary SHALL be the single entrypoint for all functionality. All operations MUST be accessed via subcommands.

#### Scenario: Running without subcommand
- **WHEN** user runs `startaste` with no subcommand
- **THEN** system displays usage help listing available subcommands

#### Scenario: Available subcommands
- **WHEN** user runs `startaste --help`
- **THEN** system lists `sync` and `export` as available subcommands

### Requirement: Installable binary via flake
The `startaste` CLI SHALL be installable as a binary via `flake.nix`.

#### Scenario: Installation via nix
- **WHEN** user runs `nix develop` or installs the flake
- **THEN** `startaste` is available as a command in PATH

### Requirement: Automatic database initialization
The system SHALL create the SQLite database (`hn.db`) automatically on first use.

#### Scenario: First run with no existing database
- **WHEN** user runs any `startaste` subcommand for the first time
- **THEN** system creates `hn.db` with Story and Comment tables without error

### Requirement: Credentials from environment
The system SHALL read HN credentials from environment variables or a `.env` file.

#### Scenario: Credentials in environment
- **WHEN** `HN_COMMENTS_ACCT` and `HN_COMMENTS_PW` are set as environment variables
- **THEN** system uses them for authentication

#### Scenario: Credentials in .env file
- **WHEN** credentials are defined in a `.env` file in the working directory
- **THEN** system loads and uses them for authentication

#### Scenario: Missing credentials
- **WHEN** credentials are not set in environment or `.env`
- **THEN** system exits with a clear error message
