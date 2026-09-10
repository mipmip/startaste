# cli Specification

## Purpose
The command surface: which subcommands `startaste` offers, what arguments they
take, and how credentials and the database reach them.

## Requirements

### Requirement: Subcommand-based entrypoint
The `startaste` binary SHALL be the single entrypoint for all functionality, with every operation reached through a subcommand.

#### Scenario: Running with no subcommand
- **WHEN** `startaste` is run with no subcommand
- **THEN** usage help is displayed listing the available subcommands, and the exit status is non-zero

#### Scenario: Available subcommands
- **WHEN** `startaste --help` is run
- **THEN** it lists `sync`, `export`, `serve`, `mcp` and `mcp-token`

#### Scenario: Version
- **WHEN** `startaste --version` is run
- **THEN** it prints the version from the VERSION file

### Requirement: Sync accepts an optional source
The `sync` subcommand SHALL accept an optional source name, syncing only that source, and SHALL sync every configured source when given none.

#### Scenario: All configured sources
- **WHEN** `startaste sync` is run with no argument
- **THEN** every configured source is synced

#### Scenario: One source
- **WHEN** `startaste sync github` is run
- **THEN** only the GitHub source is synced

#### Scenario: Unconfigured source
- **WHEN** a named source's credentials are not set
- **THEN** it exits with an error listing the environment variables that source needs

#### Scenario: Unknown source
- **WHEN** a source name that does not exist is given
- **THEN** it exits with an error listing the available sources

#### Scenario: No source configured at all
- **WHEN** `startaste sync` is run with no credentials for any source
- **THEN** it exits with an error saying no sources are configured

### Requirement: Export accepts source and type filters
The `export` subcommand SHALL accept `--source` and `--type` to filter what is exported, `--format` to choose the output format, and `-f`/`--file` to choose the destination.

#### Scenario: Filter by source
- **WHEN** `startaste export --source hn` is run
- **THEN** only HN items are exported

#### Scenario: Filter by type
- **WHEN** `startaste export --type star` is run
- **THEN** only items of that type are exported, from any source

#### Scenario: Both filters
- **WHEN** both flags are given
- **THEN** only items matching both are exported

### Requirement: The dashboard and MCP subcommands take a bind
The `serve` and `mcp` subcommands SHALL each accept a host and a port, both defaulting to loopback, and `mcp` SHALL require a path to its token file.

#### Scenario: Dashboard defaults
- **WHEN** `startaste serve` is run with no arguments
- **THEN** it binds `127.0.0.1` on the dashboard's default port

#### Scenario: MCP defaults
- **WHEN** `startaste mcp` is run with only a token file
- **THEN** it binds `127.0.0.1` on the MCP default port

#### Scenario: MCP without a token file
- **WHEN** `startaste mcp` is run with no token file
- **THEN** it exits with a usage error rather than serving unauthenticated

### Requirement: Credentials come from the environment or a .env file
The system SHALL read each source's credentials from environment variables, falling back to a `.env` file discovered from the working directory, and SHALL exit with a clear message naming what is missing. A credential that is present but rejected by the source SHALL be reported in the same shape as one that is absent — naming the variable, saying it was rejected, and showing no traceback.

#### Scenario: Credentials in the environment
- **WHEN** a source's variables are set in the environment
- **THEN** they are used

#### Scenario: Credentials in a .env file
- **WHEN** a `.env` file in the working directory defines them
- **THEN** they are loaded and used, with the environment taking precedence

#### Scenario: Missing credentials
- **WHEN** a source's credentials are absent
- **THEN** the error names the variables that source needs, and no traceback is shown

#### Scenario: Rejected credentials
- **WHEN** a source rejects the credentials it was given
- **THEN** the error names the variable whose value was rejected and says how to renew it, and no traceback is shown

#### Scenario: A failure that is not about credentials
- **WHEN** a source cannot be reached, or refuses because of rate limiting
- **THEN** the error says so, and does not blame the credentials

### Requirement: The database is created on first use
Subcommands that read or write stored items SHALL create the database and its tables on first use, except the MCP server, which opens it read-only and refuses to create one.

#### Scenario: First run
- **WHEN** `sync`, `export` or `serve` runs against a machine with no database
- **THEN** the database and every source's tables are created without error, at the location the `paths` capability specifies

#### Scenario: Minting a token creates nothing
- **WHEN** `startaste mcp-token` is run
- **THEN** no database is created, because it touches no stored data
